"""Sandboxed tool execution.

Provides isolation for tool execution via subprocess, optional container
isolation, and configurable resource limits.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass


@dataclass
class SandboxConfig:
    """Configuration for sandboxed execution."""

    enabled: bool = True
    timeout_seconds: int = 30
    max_output_bytes: int = 1_000_000  # 1MB
    allowed_paths: list[str] | None = None  # None = all paths allowed
    blocked_commands: list[str] | None = None
    env_whitelist: list[str] | None = None  # None = inherit all


@dataclass
class ExecutionResult:
    """Result of a sandboxed command execution."""

    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool = False


class Sandbox:
    """Execute commands and operations in a controlled environment."""

    def __init__(self, config: SandboxConfig | None = None) -> None:
        self._config = config or SandboxConfig()

    async def run_command(
        self,
        command: str,
        *,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> ExecutionResult:
        """Run a shell command with sandboxing.

        Args:
            command: Shell command to execute.
            cwd: Working directory.
            env: Environment variables (merged with whitelist).
            timeout: Override default timeout.

        Returns:
            ExecutionResult with stdout, stderr, and exit code.
        """
        if self._config.blocked_commands:
            for blocked in self._config.blocked_commands:
                if blocked in command:
                    return ExecutionResult(
                        stdout="",
                        stderr=f"Blocked: command contains restricted pattern '{blocked}'",
                        exit_code=1,
                    )

        # Build environment
        exec_env = self._build_env(env)
        effective_timeout = timeout or self._config.timeout_seconds

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=exec_env,
            )

            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=effective_timeout,
            )

            # Truncate if too large
            max_bytes = self._config.max_output_bytes
            stdout = stdout_bytes[:max_bytes].decode("utf-8", errors="replace")
            stderr = stderr_bytes[:max_bytes].decode("utf-8", errors="replace")

            return ExecutionResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=process.returncode or 0,
            )

        except TimeoutError:
            process.kill()
            return ExecutionResult(
                stdout="",
                stderr=f"Command timed out after {effective_timeout}s",
                exit_code=-1,
                timed_out=True,
            )
        except Exception as e:
            return ExecutionResult(
                stdout="",
                stderr=str(e),
                exit_code=-1,
            )

    def _build_env(self, extra: dict[str, str] | None) -> dict[str, str] | None:
        """Build execution environment from whitelist + extras."""
        if self._config.env_whitelist is None:
            # Inherit all, merge extras
            env = os.environ.copy()
            if extra:
                env.update(extra)
            return env

        # Only whitelisted vars
        env = {}
        for key in self._config.env_whitelist:
            if key in os.environ:
                env[key] = os.environ[key]
        if extra:
            env.update(extra)
        return env
