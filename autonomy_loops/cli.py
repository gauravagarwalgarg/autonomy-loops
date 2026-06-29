"""CLI entry point for AutonomyLoops.

Provides commands to run agents, orchestrate pipelines, serve the
dashboard, and manage configuration.
"""

from __future__ import annotations

import asyncio
import sys

import click

from autonomy_loops import __version__


@click.group()
@click.version_option(version=__version__, prog_name="autonomy-loops")
def main():
    """AutonomyLoops Multi-agent orchestration framework."""
    pass


@main.command()
@click.option("--role", "-r", default="developer", help="Agent role/persona")
@click.option("--mode", "-m", default="code", help="Lifecycle mode")
@click.option("--provider", "-p", default=None, help="LLM provider override")
@click.option("--model", default=None, help="Model override")
@click.option("--config", "-c", default=None, help="Config file path")
@click.option("--task", "-t", default=None, help="Task description (or reads from stdin)")
def run(role: str, mode: str, provider: str | None, model: str | None, config: str | None, task: str | None):
    """Run a single agent with the given role and mode."""
    from autonomy_loops.config import Config

    cfg = Config.load(config)
    effective_provider = provider or cfg.default_provider

    if not task:
        if not sys.stdin.isatty():
            task = sys.stdin.read().strip()
        else:
            click.echo("Error: provide --task or pipe input via stdin", err=True)
            sys.exit(1)

    click.echo(f"Running agent: role={role}, mode={mode}, provider={effective_provider}")
    asyncio.run(_run_agent(cfg, role, mode, effective_provider, model, task))


async def _run_agent(cfg, role: str, mode: str, provider_name: str, model: str | None, task: str):
    """Internal: create provider and run agent."""
    from autonomy_loops.agent import Agent
    from autonomy_loops._factory import create_provider

    provider = create_provider(provider_name, cfg)
    agent = Agent(role=role, mode=mode, provider=provider, config=cfg)
    result = await agent.run(task)

    click.echo(f"\n{'='*60}")
    click.echo(f"Result: {'SUCCESS' if result.success else 'FAILED'}")
    click.echo(f"Iterations: {result.iterations}")
    click.echo(f"Tokens: {result.total_tokens}")
    click.echo(f"Time: {result.elapsed_seconds:.2f}s")
    click.echo(f"{'='*60}\n")
    click.echo(result.output)


@main.command()
@click.option("--pipeline", "-p", required=True, help="Pipeline YAML file")
@click.option("--config", "-c", default=None, help="Config file path")
def orchestrate(pipeline: str, config: str | None):
    """Run a multi-agent pipeline."""
    from autonomy_loops.config import Config
    from autonomy_loops.orchestrator import Orchestrator

    cfg = Config.load(config)
    click.echo(f"Running pipeline: {pipeline}")
    asyncio.run(_run_pipeline(cfg, pipeline))


async def _run_pipeline(cfg, pipeline_path: str):
    """Internal: run orchestrator pipeline."""
    from autonomy_loops.orchestrator import Orchestrator
    from autonomy_loops._factory import create_all_providers

    providers = create_all_providers(cfg)
    orch = Orchestrator.from_pipeline(pipeline_path, config=cfg, providers=providers)
    result = await orch.run()

    click.echo(f"\nPipeline {'SUCCEEDED' if result.success else 'FAILED'}")
    click.echo(f"Steps: {len(result.steps)}")
    click.echo(f"Total tokens: {result.total_tokens}")
    click.echo(f"Time: {result.elapsed_seconds:.2f}s")

    for name, step_result in result.steps.items():
        status = "✓" if step_result.success else "✗"
        click.echo(f"  {status} {name} ({step_result.iterations} iters, {step_result.total_tokens} tokens)")


@main.command()
@click.option("--port", default=8091, help="Server port")
@click.option("--host", default="0.0.0.0", help="Server host")
def serve(port: int, host: str):
    """Start the AutonomyLoops dashboard server."""
    import http.server
    import os

    directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    server = http.server.HTTPServer((host, port), Handler)
    click.echo(f"AutonomyLoops dashboard: http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        click.echo("\nShutdown.")
        server.server_close()


@main.command()
def init():
    """Initialize AutonomyLoops in the current project."""
    from pathlib import Path

    config_file = Path("autonomy-loops.yaml")
    if config_file.exists():
        click.echo("autonomy-loops.yaml already exists.")
        return

    template = """\
# AutonomyLoops Configuration
# See: https://github.com/GauravAgarwalGarg/AutonomyLoops/blob/main/docs/configuration.md

project:
  name: my-project
  languages: []  # auto-detected if empty

steering:
  mode: code
  role: developer
  plugins: []
  styles_dir: ./styles

providers:
  default: anthropic
  anthropic:
    api_key: ${ANTHROPIC_API_KEY}
    default_model: claude-sonnet-4-20250514
  openai:
    api_key: ${OPENAI_API_KEY}
    default_model: gpt-4o

policy:
  hitl_mode: none
  max_iterations: 50
  cost_limit_usd: 5.00
  allowed_tools: [file, shell, web, code]

telemetry:
  enabled: true
  exporter: console
  log_level: info
"""
    config_file.write_text(template, encoding="utf-8")
    click.echo("Created autonomy-loops.yaml")

    # Create styles directory
    styles_dir = Path("styles")
    styles_dir.mkdir(exist_ok=True)
    (styles_dir / "common.md").write_text(
        "# Team Conventions\n\nAdd your team's shared standards here.\n",
        encoding="utf-8",
    )
    click.echo("Created styles/ directory with common.md")


if __name__ == "__main__":
    main()


# =============================================================================
# ORBIT COMMANDS Lightweight second-brain agent skills
# Merged from orbit/ package into the main CLI for a single entry point.
# =============================================================================

@main.command("skill")
@click.argument("skill_name")
@click.option("--input", "-i", "input_text", default=None, help="Input text (default: stdin)")
@click.option("--model", "-m", default="", help="Override model")
def skill_run(skill_name: str, input_text: str | None, model: str):
    """Run an orbit skill (prompt template + LLM). Alias: orbit run <skill>"""
    from orbit.runner import run_skill
    text = input_text or (sys.stdin.read() if not sys.stdin.isatty() else "")
    output = run_skill(skill_name, text, model)
    click.echo(output)


@main.command("skills")
def skills_list():
    """List available orbit skills."""
    from orbit.runner import list_skills
    list_skills()


@main.command("plan")
@click.argument("goal", nargs=-1, required=True)
def plan_goal(goal: tuple):
    """Break a goal into actionable steps using AI."""
    from orbit.planner import plan_goal
    plan_goal(" ".join(goal))


@main.command("audit")
def audit_project():
    """Score current project's loop readiness (0-100)."""
    from orbit.audit import audit_project
    audit_project()


@main.command("context")
def show_context():
    """Show current git context (branch, status, changes)."""
    from orbit.context import show_context
    show_context()


@main.command("state")
def show_state():
    """Show orbit loop state (history, budget, plans)."""
    from orbit.state import show_state
    show_state()
