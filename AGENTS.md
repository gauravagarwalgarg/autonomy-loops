# AutonomyLoops Agent Instructions

AutonomyLoops is a production-ready, multi-agent orchestration framework.

## Project Structure

```
autonomy-loops/
├── autonomy_loops/          # Core Python package
│   ├── agent.py             # Agent execution loop
│   ├── orchestrator.py      # Multi-agent pipeline coordinator
│   ├── config.py            # Configuration loader
│   ├── state.py             # Agent state machine
│   ├── cli.py               # CLI entry point
│   ├── _factory.py          # Provider factory
│   ├── providers/           # LLM provider abstraction
│   ├── tools/               # Tool execution framework
│   ├── policy/              # Governance & HITL
│   ├── telemetry/           # Observability (OTel, logging)
│   └── steering/            # Steering file loader
├── roles/                   # Agent persona definitions (markdown)
├── modes/                   # Lifecycle mode definitions (markdown)
├── plugins/                 # Industry-specific knowledge packs
├── pipelines/               # Multi-agent workflow definitions (YAML)
├── styles/                  # Team customization overlays
├── tests/                   # Test suite (pytest)
├── docs/                    # Documentation
├── pyproject.toml           # Python packaging
├── Dockerfile               # Container deployment
└── docker-compose.yaml      # Full observability stack
```

## Technology

- Python 3.11+ with type annotations
- Async-first architecture (asyncio)
- Pydantic for configuration validation
- OpenTelemetry for distributed tracing
- structlog for structured logging
- click for CLI
- httpx for HTTP client operations

## When Editing This Repo

- Run `pytest tests/ -v` after changes
- Run `ruff check autonomy_loops/` for linting
- Run `mypy autonomy_loops/` for type checking
- Roles go in `roles/` one markdown file per role
- Modes go in `modes/` one markdown file per mode
- Plugins go in `plugins/{plugin-id}/` markdown skill files
- Tests go in `tests/` one test file per module

## Key Design Decisions

- Async-first: all agent execution is async for concurrency
- Provider-agnostic: LLM providers implement a common interface
- Steering layers: role + mode + plugins + team styles (in order)
- Policy engine: declarative rules evaluated at action boundaries
- State machine: explicit transitions with full audit history
- Plugin architecture: domain knowledge as loadable markdown packs
