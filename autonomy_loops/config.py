"""Configuration loader for AutonomyLoops.

Supports YAML config files with environment variable interpolation,
hierarchical merging, and validation via Pydantic.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

# --- Environment variable interpolation ---

_ENV_PATTERN = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")


def _interpolate_env(value: Any) -> Any:
    """Recursively interpolate ${ENV_VAR} references in config values."""
    if isinstance(value, str):

        def replacer(match: re.Match[str]) -> str:
            var_name = match.group(1)
            return os.environ.get(var_name, "")

        return _ENV_PATTERN.sub(replacer, value)
    if isinstance(value, dict):
        return {k: _interpolate_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_interpolate_env(item) for item in value]
    return value


# --- Pydantic models ---


class ProviderConfig(BaseModel):
    """LLM provider configuration."""

    api_key: str = ""
    base_url: str | None = None
    default_model: str = ""
    max_retries: int = 3
    timeout_seconds: int = 120
    region: str | None = None  # For Bedrock


class PolicyConfig(BaseModel):
    """Agent governance policy."""

    hitl_mode: str = "none"  # none | notify | approval_required
    max_iterations: int = 50
    cost_limit_usd: float = 10.0
    allowed_tools: list[str] = Field(default_factory=lambda: ["file", "shell", "web", "code"])
    blocked_patterns: list[str] = Field(default_factory=list)


class TelemetryConfig(BaseModel):
    """Observability configuration."""

    enabled: bool = True
    exporter: str = "otlp"  # otlp | console | none
    endpoint: str = "http://localhost:4317"
    log_level: str = "info"
    audit_trail: bool = True
    service_name: str = "autonomy-loops"


class SecurityConfig(BaseModel):
    """Security and access control."""

    rbac_enabled: bool = False
    token_vault: str = "env"  # env | aws-secrets | vault | azure-keyvault # noqa: S105
    sandbox_tools: bool = True


class SteeringConfig(BaseModel):
    """Steering layer configuration."""

    mode: str = "code"
    role: str = "developer"
    plugins: list[str] = Field(default_factory=list)
    styles_dir: str | None = "./styles"


class ProjectConfig(BaseModel):
    """Project metadata."""

    name: str = "unnamed"
    languages: list[str] = Field(default_factory=list)


class Config(BaseModel):
    """Root configuration for AutonomyLoops."""

    project: ProjectConfig = Field(default_factory=ProjectConfig)
    steering: SteeringConfig = Field(default_factory=SteeringConfig)
    providers: dict[str, ProviderConfig] = Field(default_factory=dict)
    default_provider: str = "anthropic"
    policy: PolicyConfig = Field(default_factory=PolicyConfig)
    telemetry: TelemetryConfig = Field(default_factory=TelemetryConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    @classmethod
    def load(cls, path: str | Path | None = None) -> Config:
        """Load configuration from YAML file with env interpolation.

        Search order:
        1. Explicit path argument
        2. AUTONOMY_LOOPS_CONFIG env var
        3. ./autonomy-loops.yaml
        4. ~/.config/autonomy-loops/config.yaml
        """
        search_paths: list[Path] = []

        if path:
            search_paths.append(Path(path))

        env_path = os.environ.get("AUTONOMY_LOOPS_CONFIG")
        if env_path:
            search_paths.append(Path(env_path))

        search_paths.extend(
            [
                Path("autonomy-loops.yaml"),
                Path("autonomy-loops.yml"),
                Path.home() / ".config" / "autonomy-loops" / "config.yaml",
            ]
        )

        for candidate in search_paths:
            if candidate.exists():
                return cls._from_file(candidate)

        # No config found return defaults
        return cls()

    @classmethod
    def _from_file(cls, path: Path) -> Config:
        """Parse a YAML config file."""
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        interpolated = _interpolate_env(raw)

        # Normalize provider configs
        providers_raw = interpolated.pop("providers", {})
        default_provider = providers_raw.pop("default", "anthropic")
        providers = {
            name: ProviderConfig(**cfg) if isinstance(cfg, dict) else ProviderConfig()
            for name, cfg in providers_raw.items()
        }

        return cls(
            project=ProjectConfig(**interpolated.get("project", {})),
            steering=SteeringConfig(**interpolated.get("steering", {})),
            providers=providers,
            default_provider=default_provider,
            policy=PolicyConfig(**interpolated.get("policy", {})),
            telemetry=TelemetryConfig(**interpolated.get("telemetry", {})),
            security=SecurityConfig(**interpolated.get("security", {})),
        )
