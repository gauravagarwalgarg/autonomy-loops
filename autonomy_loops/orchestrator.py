"""Multi-agent orchestrator.

Coordinates multiple agents in a pipeline, manages handoffs between agents,
and enforces global policies across the pipeline execution.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from autonomy_loops.agent import Agent, AgentResult
from autonomy_loops.config import Config
from autonomy_loops.providers.base import LLMProvider
from autonomy_loops.telemetry.logger import get_logger
from autonomy_loops.tools.registry import ToolRegistry

logger = get_logger(__name__)


@dataclass
class PipelineStep:
    """A single step in a multi-agent pipeline."""

    name: str
    role: str
    mode: str
    task_template: str
    depends_on: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    provider_override: str | None = None
    model_override: str | None = None
    max_iterations: int | None = None


@dataclass
class PipelineResult:
    """Aggregated result of a full pipeline execution."""

    success: bool
    steps: dict[str, AgentResult]
    elapsed_seconds: float
    total_tokens: int


class Orchestrator:
    """Multi-agent pipeline orchestrator.

    Runs agents in dependency order, passing outputs between steps,
    and collecting aggregate metrics.
    """

    def __init__(
        self,
        *,
        steps: list[PipelineStep],
        config: Config | None = None,
        providers: dict[str, LLMProvider] | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        self._steps = steps
        self._config = config or Config()
        self._providers = providers or {}
        self._tools = tools or ToolRegistry()

    @classmethod
    def from_pipeline(
        cls,
        path: str | Path,
        *,
        config: Config | None = None,
        providers: dict[str, LLMProvider] | None = None,
        tools: ToolRegistry | None = None,
    ) -> Orchestrator:
        """Load a pipeline definition from YAML.

        Pipeline YAML format:
        ```yaml
        name: ci-review
        steps:
          - name: analyze
            role: architect
            mode: review
            task: "Analyze the code changes and identify risks"
            depends_on: []
          - name: review
            role: reviewer
            mode: review
            task: "Review code for quality and correctness. Context: {analyze.output}"
            depends_on: [analyze]
          - name: test-suggest
            role: tester
            mode: test
            task: "Suggest test cases for the changes. Context: {analyze.output}"
            depends_on: [analyze]
        ```
        """
        pipeline_path = Path(path)
        if not pipeline_path.exists():
            raise FileNotFoundError(f"Pipeline file not found: {path}")

        raw = yaml.safe_load(pipeline_path.read_text(encoding="utf-8"))
        steps = []
        for step_def in raw.get("steps", []):
            steps.append(
                PipelineStep(
                    name=step_def["name"],
                    role=step_def.get("role", "developer"),
                    mode=step_def.get("mode", "code"),
                    task_template=step_def.get("task", ""),
                    depends_on=step_def.get("depends_on", []),
                    tools=step_def.get("tools", []),
                    provider_override=step_def.get("provider"),
                    model_override=step_def.get("model"),
                    max_iterations=step_def.get("max_iterations"),
                )
            )

        return cls(steps=steps, config=config, providers=providers, tools=tools)

    async def run(self, *, context: dict[str, Any] | None = None) -> PipelineResult:
        """Execute the pipeline.

        Steps run in dependency order. Steps with no dependencies run in parallel.
        """
        start_time = time.time()
        results: dict[str, AgentResult] = {}
        context = context or {}

        logger.info("pipeline_start", steps=len(self._steps))

        # Build dependency graph and execution order
        execution_layers = self._resolve_execution_order()

        for layer in execution_layers:
            # Run independent steps in parallel
            tasks = []
            for step in layer:
                task_text = self._interpolate_task(step.task_template, results, context)
                tasks.append(self._run_step(step, task_text, context))

            layer_results = await asyncio.gather(*tasks, return_exceptions=True)

            for step, result in zip(layer, layer_results, strict=False):
                if isinstance(result, BaseException):
                    logger.error("step_failed", step=step.name, error=str(result))
                    results[step.name] = AgentResult(
                        success=False,
                        output=f"Error: {result}",
                        iterations=0,
                    )
                else:
                    results[step.name] = result

        elapsed = time.time() - start_time
        total_tokens = sum(r.total_tokens for r in results.values())
        all_success = all(r.success for r in results.values())

        logger.info(
            "pipeline_complete",
            success=all_success,
            elapsed=f"{elapsed:.2f}s",
            tokens=total_tokens,
        )

        return PipelineResult(
            success=all_success,
            steps=results,
            elapsed_seconds=elapsed,
            total_tokens=total_tokens,
        )

    async def _run_step(
        self, step: PipelineStep, task: str, context: dict[str, Any]
    ) -> AgentResult:
        """Run a single pipeline step."""
        logger.info("step_start", step=step.name, role=step.role, mode=step.mode)

        # Resolve provider for this step
        provider_name = step.provider_override or self._config.default_provider
        provider = self._providers.get(provider_name)
        if not provider:
            raise RuntimeError(f"Provider '{provider_name}' not configured for step '{step.name}'")

        agent = Agent(
            role=step.role,
            mode=step.mode,
            provider=provider,
            config=self._config,
            tools=self._tools,
        )

        result = await agent.run(task, context=context)
        logger.info("step_complete", step=step.name, success=result.success)
        return result

    def _resolve_execution_order(self) -> list[list[PipelineStep]]:
        """Topological sort steps into execution layers."""
        step_map = {s.name: s for s in self._steps}
        in_degree = {s.name: len(s.depends_on) for s in self._steps}
        dependents: dict[str, list[str]] = {s.name: [] for s in self._steps}

        for step in self._steps:
            for dep in step.depends_on:
                if dep in dependents:
                    dependents[dep].append(step.name)

        layers: list[list[PipelineStep]] = []
        remaining = set(in_degree.keys())

        while remaining:
            # Find all steps with no unresolved dependencies
            ready = [name for name in remaining if in_degree[name] == 0]
            if not ready:
                raise RuntimeError(f"Circular dependency detected among: {remaining}")

            layers.append([step_map[name] for name in ready])

            for name in ready:
                remaining.remove(name)
                for dependent in dependents.get(name, []):
                    in_degree[dependent] -= 1

        return layers

    def _interpolate_task(
        self,
        template: str,
        results: dict[str, AgentResult],
        context: dict[str, Any],
    ) -> str:
        """Replace {step_name.output} and {context.key} placeholders."""
        interpolated = template

        # Replace step outputs
        for name, result in results.items():
            interpolated = interpolated.replace(f"{{{name}.output}}", result.output[:2000])

        # Replace context values
        for key, value in context.items():
            interpolated = interpolated.replace(f"{{context.{key}}}", str(value))

        return interpolated
