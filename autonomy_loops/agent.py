"""Core Agent implementation the autonomous execution loop.

An Agent runs a Plan → Act → Observe → Reflect loop until a task is
completed, fails, or exceeds iteration/cost limits. The agent is
governed by policies, steered by roles/modes/plugins, and observed
via OpenTelemetry.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any

from autonomy_loops.config import Config
from autonomy_loops.providers.base import LLMMessage, LLMProvider, LLMResponse
from autonomy_loops.state import AgentState, StateMachine
from autonomy_loops.steering.loader import SteeringLoader
from autonomy_loops.telemetry.logger import get_logger
from autonomy_loops.tools.registry import ToolRegistry

logger = get_logger(__name__)


@dataclass
class AgentResult:
    """Final result of an agent execution."""
    success: bool
    output: str
    iterations: int
    total_tokens: int = 0
    elapsed_seconds: float = 0.0
    tool_calls_made: int = 0
    state: AgentState = AgentState.COMPLETED
    history: list[LLMMessage] = field(default_factory=list)


class Agent:
    """Autonomous AI agent with Plan → Act → Observe → Reflect loop.

    Args:
        role: Agent persona (e.g., "developer", "reviewer").
        mode: Lifecycle phase (e.g., "code", "test", "deploy").
        provider: LLM provider instance.
        config: AutonomyLoops configuration.
        tools: Tool registry for the agent to use.
    """

    def __init__(
        self,
        *,
        role: str = "developer",
        mode: str = "code",
        provider: LLMProvider,
        config: Config | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        self._role = role
        self._mode = mode
        self._provider = provider
        self._config = config or Config()
        self._tools = tools or ToolRegistry()
        self._state_machine = StateMachine()
        self._messages: list[LLMMessage] = []
        self._total_tokens = 0
        self._tool_calls_made = 0

    @property
    def state(self) -> AgentState:
        return self._state_machine.state

    @property
    def iteration(self) -> int:
        return self._state_machine.iteration

    async def run(self, task: str, *, context: dict[str, Any] | None = None) -> AgentResult:
        """Execute the agent loop for a given task.

        Args:
            task: Natural language description of what to accomplish.
            context: Additional context (file contents, metadata, etc.).

        Returns:
            AgentResult with the outcome of the execution.
        """
        start_time = time.time()
        max_iterations = self._config.policy.max_iterations

        logger.info(
            "agent_start",
            role=self._role,
            mode=self._mode,
            task=task[:200],
            provider=self._provider.name,
        )

        # Build system prompt from steering
        system_prompt = self._build_system_prompt(context)
        self._messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=task),
        ]

        self._state_machine.transition(AgentState.PLANNING, reason="task_received")

        try:
            while not self._state_machine.is_terminal:
                if self._state_machine.iteration > max_iterations:
                    self._state_machine.transition(
                        AgentState.FAILED,
                        reason=f"max_iterations_exceeded ({max_iterations})",
                    )
                    break

                # Plan: ask LLM what to do next
                response = await self._think()

                if response.tool_calls:
                    # Act: execute tool calls
                    self._state_machine.transition(AgentState.ACTING, reason="tool_calls_pending")
                    results = await self._execute_tools(response.tool_calls)

                    # Observe: feed results back
                    self._state_machine.transition(AgentState.OBSERVING, reason="tool_results_ready")
                    self._append_tool_results(response, results)

                    # Reflect: decide next step
                    self._state_machine.transition(AgentState.REFLECTING, reason="reflecting")
                    self._state_machine.transition(AgentState.PLANNING, reason="next_iteration")
                else:
                    # No tool calls agent is done
                    self._state_machine.transition(AgentState.REFLECTING, reason="no_tool_calls")
                    self._state_machine.transition(AgentState.COMPLETED, reason="task_complete")

        except Exception as e:
            logger.error("agent_error", error=str(e), iteration=self.iteration)
            if not self._state_machine.is_terminal:
                self._state_machine.transition(AgentState.FAILED, reason=str(e))

        elapsed = time.time() - start_time
        final_output = self._messages[-1].content if self._messages else ""

        logger.info(
            "agent_complete",
            state=self.state.value,
            iterations=self.iteration,
            tokens=self._total_tokens,
            elapsed=f"{elapsed:.2f}s",
        )

        return AgentResult(
            success=self.state == AgentState.COMPLETED,
            output=final_output,
            iterations=self.iteration,
            total_tokens=self._total_tokens,
            elapsed_seconds=elapsed,
            tool_calls_made=self._tool_calls_made,
            state=self.state,
            history=self._messages.copy(),
        )

    def _build_system_prompt(self, context: dict[str, Any] | None) -> str:
        """Assemble the system prompt from steering layers."""
        loader = SteeringLoader(self._config)
        parts = loader.load(role=self._role, mode=self._mode)

        if context:
            parts.append(f"\n## Additional Context\n\n{_format_context(context)}")

        return "\n\n---\n\n".join(parts)

    async def _think(self) -> LLMResponse:
        """Send current conversation to LLM and get next action."""
        tool_defs = self._tools.get_tool_definitions()

        response = await self._provider.complete(
            messages=self._messages,
            tools=tool_defs if tool_defs else None,
            temperature=0.0,
        )

        self._total_tokens += response.usage.get("prompt_tokens", 0)
        self._total_tokens += response.usage.get("completion_tokens", 0)

        # Append assistant response to history
        self._messages.append(LLMMessage(
            role="assistant",
            content=response.content,
            tool_calls=response.tool_calls,
        ))

        return response

    async def _execute_tools(self, tool_calls: list) -> list[dict[str, Any]]:
        """Execute tool calls and return results."""
        results = []
        for tc in tool_calls:
            self._tool_calls_made += 1
            logger.info("tool_call", tool=tc.name, args=tc.arguments)

            try:
                result = await self._tools.execute(tc.name, tc.arguments)
                results.append({"tool_call_id": tc.id, "success": True, "output": str(result)})
            except Exception as e:
                logger.warning("tool_error", tool=tc.name, error=str(e))
                results.append({"tool_call_id": tc.id, "success": False, "output": f"Error: {e}"})

        return results

    def _append_tool_results(self, response: LLMResponse, results: list[dict[str, Any]]) -> None:
        """Append tool results to conversation history."""
        for result in results:
            self._messages.append(LLMMessage(
                role="tool",
                content=result["output"],
                tool_call_id=result["tool_call_id"],
            ))


def _format_context(context: dict[str, Any]) -> str:
    """Format context dict as readable text."""
    parts = []
    for key, value in context.items():
        parts.append(f"**{key}**: {value}")
    return "\n".join(parts)
