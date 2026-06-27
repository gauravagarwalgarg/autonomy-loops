# AutonomyLoops

[![GitHub CI](https://github.com/GauravAgarwalGarg/AutonomyLoops/actions/workflows/ci.yml/badge.svg)](https://github.com/GauravAgarwalGarg/AutonomyLoops/actions)
[![GitLab CI](https://gitlab.com/GauravAgarwalGarg/AutonomyLoops/badges/main/pipeline.svg)](https://gitlab.com/GauravAgarwalGarg/AutonomyLoops/-/pipelines)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Production-ready, multi-agent orchestration framework for steering, scaling, and governing autonomous AI agents.**

AutonomyLoops provides a standardized, plug-and-play architecture for organizations to deploy AI agents with enterprise-grade controls: multi-model support, human-in-the-loop (HITL) gates, structured observability, RBAC, and domain-adaptive steering across any industry vertical.

> **📖 Documentation:** [GitHub Pages](https://gauravagrawalgarg.github.io/AutonomyLoops/) · [GitLab Pages](https://gauravagrawalgarg.gitlab.io/AutonomyLoops/)
>
> **📦 Repositories:** [GitHub](https://github.com/GauravAgarwalGarg/AutonomyLoops) · [GitLab](https://gitlab.com/GauravAgarwalGarg/AutonomyLoops)

---

## Why AutonomyLoops?

| Problem | Solution |
|---|---|
| Agents run without guardrails | HITL gates, policy engines, kill switches |
| No observability into agent decisions | OpenTelemetry tracing, structured logging, decision audit trails |
| Locked to one LLM provider | Abstract provider layer (OpenAI, Anthropic, local models, Azure, Bedrock) |
| One-size-fits-all prompting | Industry-specific steering profiles with role/mode layering |
| No multi-agent coordination | Orchestrator pattern with state machines, message passing, delegation |
| Security is an afterthought | RBAC, token vault, secrets isolation, sandboxed tool execution |

---

## Quick Start

```bash
# 1. Install
pip install autonomy-loops

# Or from source:
git clone https://github.com/your-org/AutonomyLoops.git
cd AutonomyLoops
pip install -e ".[dev]"

# 2. Configure
cp autonomy-loops.example.yaml autonomy-loops.yaml
# Edit with your LLM provider keys and project settings

# 3. Run a single agent
autonomy-loops run --profile developer --mode code

# 4. Run multi-agent pipeline
autonomy-loops orchestrate --pipeline ci-review

# 5. Start the dashboard
autonomy-loops serve --port 8091
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AutonomyLoops Orchestrator                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐   │
│  │  Agent A  │  │  Agent B  │  │  Agent C  │  │  Agent N  │   │
│  │ (Coder)   │  │ (Reviewer)│  │ (Tester)  │  │ (Custom)  │   │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘   │
│        │               │               │               │         │
│  ┌─────▼───────────────▼───────────────▼───────────────▼─────┐  │
│  │                  Message Bus / State Machine                │  │
│  └─────┬───────────────┬───────────────┬───────────────┬─────┘  │
│        │               │               │               │         │
│  ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐  │
│  │  LLM      │  │  Tools    │  │  Policy   │  │  Telemetry│  │
│  │  Provider  │  │  Registry │  │  Engine   │  │  Exporter │  │
│  │  Layer     │  │           │  │  (HITL)   │  │  (OTel)   │  │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘  │
├─────────────────────────────────────────────────────────────────┤
│              Steering Layer (Roles + Modes + Plugins)            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
autonomy-loops/
├── autonomy_loops/              # Core Python package
│   ├── __init__.py
│   ├── cli.py                   # CLI entry point
│   ├── config.py                # Configuration loader (YAML/env/secrets)
│   ├── orchestrator.py          # Multi-agent orchestration engine
│   ├── agent.py                 # Single agent loop (plan → act → observe)
│   ├── state.py                 # Agent state machine
│   ├── providers/               # LLM provider abstraction
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract provider interface
│   │   ├── openai_provider.py   # OpenAI / Azure OpenAI
│   │   ├── anthropic_provider.py# Anthropic Claude
│   │   ├── bedrock_provider.py  # AWS Bedrock
│   │   └── local_provider.py    # Ollama / vLLM / local models
│   ├── tools/                   # Tool execution framework
│   │   ├── __init__.py
│   │   ├── registry.py          # Tool registration + discovery
│   │   ├── sandbox.py           # Sandboxed execution (subprocess/container)
│   │   ├── builtin/             # Built-in tools (file, shell, web, etc.)
│   │   │   ├── file_tools.py
│   │   │   ├── shell_tools.py
│   │   │   ├── web_tools.py
│   │   │   └── code_tools.py
│   │   └── mcp_bridge.py        # MCP server integration
│   ├── policy/                  # Governance and guardrails
│   │   ├── __init__.py
│   │   ├── engine.py            # Policy evaluation engine
│   │   ├── hitl.py              # Human-in-the-loop gates
│   │   ├── rbac.py              # Role-based access control
│   │   └── rules.py             # Declarative policy rules (YAML)
│   ├── telemetry/               # Observability
│   │   ├── __init__.py
│   │   ├── tracer.py            # OpenTelemetry tracing
│   │   ├── logger.py            # Structured JSON logging
│   │   ├── metrics.py           # Prometheus-compatible metrics
│   │   └── audit.py             # Decision audit trail
│   └── steering/                # Steering file loader
│       ├── __init__.py
│       ├── loader.py            # Load roles/modes/plugins by config
│       ├── resolver.py          # Resolve steering stack order
│       └── validator.py         # Validate steering file structure
├── roles/                       # Agent persona definitions
│   ├── developer.md
│   ├── reviewer.md
│   ├── architect.md
│   ├── tester.md
│   ├── devops.md
│   ├── security.md
│   └── product-owner.md
├── modes/                       # Lifecycle mode definitions
│   ├── mode-map.json
│   ├── requirements.md
│   ├── design.md
│   ├── code.md
│   ├── test.md
│   ├── deploy.md
│   └── review.md
├── plugins/                     # Industry-specific plugin packs
│   ├── plugin-registry.json
│   ├── fintech/                 # HFT, banking, compliance
│   │   ├── fintech-standards.md
│   │   └── fintech-patterns.md
│   ├── cloud-native/            # K8s, microservices, SaaS
│   │   ├── cloud-native-patterns.md
│   │   └── cloud-native-deploy.md
│   ├── embedded/                # RTOS, firmware, hardware
│   │   ├── embedded-standards.md
│   │   └── embedded-safety.md
│   ├── networking/              # Protocol stacks, SDN, 5G
│   │   ├── networking-patterns.md
│   │   └── networking-security.md
│   └── data-engineering/        # Pipelines, ML, analytics
│       ├── data-patterns.md
│       └── data-quality.md
├── pipelines/                   # Pre-built multi-agent workflows
│   ├── ci-review.yaml           # Code review pipeline
│   ├── feature-build.yaml       # Feature development pipeline
│   └── incident-response.yaml   # Incident triage pipeline
├── styles/                      # Team/org customization overlay
│   └── example/
│       ├── common.md
│       └── code.md
├── tests/                       # Test suite
│   ├── test_agent.py
│   ├── test_orchestrator.py
│   ├── test_providers.py
│   ├── test_policy.py
│   ├── test_steering.py
│   └── test_tools.py
├── docs/                        # Documentation
│   ├── getting-started.md
│   ├── configuration.md
│   ├── providers.md
│   ├── steering-guide.md
│   ├── plugins.md
│   ├── security.md
│   ├── deployment.md
│   └── api-reference.md
├── autonomy-loops.example.yaml  # Example configuration
├── pyproject.toml               # Python packaging
├── Dockerfile                   # Container deployment
├── docker-compose.yaml          # Full stack (agent + redis + otel)
└── Makefile                     # Developer convenience commands
```

---

## Core Concepts

### 1. Agents

An agent is an autonomous loop: **Plan → Act → Observe → Reflect**. Each agent has a role (persona), a mode (lifecycle phase), and access to tools.

```python
from autonomy_loops import Agent, Config

agent = Agent(
    role="developer",
    mode="code",
    provider="anthropic",
    model="claude-sonnet-4-20250514",
    tools=["file", "shell", "web"],
)
result = agent.run("Implement the user authentication module")
```

### 2. Orchestrator

The orchestrator coordinates multiple agents in a pipeline, manages handoffs, and enforces policies.

```python
from autonomy_loops import Orchestrator

orch = Orchestrator.from_pipeline("ci-review.yaml")
orch.run(context={"repo": ".", "branch": "feature/auth"})
```

### 3. Steering (Roles + Modes + Plugins)

Steering is the layered instruction system that shapes agent behavior:

1. **Role** Who the agent is (developer, reviewer, architect)
2. **Mode** What phase of work (requirements, code, test, deploy)
3. **Plugins** Domain knowledge packs (fintech, embedded, cloud-native)
4. **Styles** Team-specific overrides and conventions

### 4. Policy Engine

Declarative rules that govern agent behavior:

```yaml
# policy.yaml
rules:
  - name: no-production-writes
    trigger: tool_call
    condition: "tool.name == 'shell' and 'prod' in tool.args"
    action: require_approval
    approvers: ["oncall-lead"]

  - name: cost-guard
    trigger: llm_call
    condition: "estimated_tokens > 100000"
    action: require_approval
```

### 5. Providers

Swap LLM backends without changing agent code:

```yaml
# autonomy-loops.yaml
providers:
  anthropic:
    api_key: ${ANTHROPIC_API_KEY}
    default_model: claude-sonnet-4-20250514
  openai:
    api_key: ${OPENAI_API_KEY}
    default_model: gpt-4o
  bedrock:
    region: us-east-1
    default_model: anthropic.claude-3-5-sonnet
  local:
    base_url: http://localhost:11434
    default_model: llama3.1:70b
```

---

## Industry Plugins

| Plugin | Target Industries | Key Standards |
|---|---|---|
| `fintech` | HFT, Banking, Insurance | SOX, PCI-DSS, MiFID II, latency budgets |
| `cloud-native` | SaaS, PaaS, Cloud Infra | 12-Factor, CNCF, K8s patterns, SRE |
| `embedded` | IoT, Automotive, Aerospace, Medical | MISRA, IEC 61508, ISO 26262, DO-178C |
| `networking` | Telecom, SDN, 5G, CDN | RFC compliance, protocol correctness |
| `data-engineering` | ML, Analytics, Data Lakes | Data quality, lineage, GDPR |
| `hardware` | FPGA, ASIC, PCB | Timing constraints, power budgets |

Enable plugins in your config:

```yaml
steering:
  plugins: ["cloud-native", "fintech"]
```

---

## Configuration

```yaml
# autonomy-loops.yaml
project:
  name: my-service
  languages: [python, typescript]
  
steering:
  mode: code
  role: developer
  plugins: ["cloud-native"]
  styles_dir: ./styles/my-team
  
providers:
  default: anthropic
  anthropic:
    api_key: ${ANTHROPIC_API_KEY}
    default_model: claude-sonnet-4-20250514
    
policy:
  hitl_mode: approval_required  # none | notify | approval_required
  max_iterations: 50
  cost_limit_usd: 5.00
  allowed_tools: [file, shell, web, code]
  blocked_patterns: ["rm -rf /", "DROP TABLE"]

telemetry:
  enabled: true
  exporter: otlp
  endpoint: http://localhost:4317
  log_level: info
  audit_trail: true

security:
  rbac_enabled: true
  token_vault: env  # env | aws-secrets | vault | azure-keyvault
  sandbox_tools: true
```

---

## Deployment

### Docker

```bash
docker build -t autonomy-loops .
docker run -e ANTHROPIC_API_KEY=sk-... autonomy-loops run --profile developer
```

### Docker Compose (Full Stack)

```bash
docker-compose up  # Agent + Redis (state) + Jaeger (traces) + Prometheus (metrics)
```

### Kubernetes

```bash
helm install autonomy-loops ./charts/autonomy-loops \
  --set provider.anthropic.apiKey=$ANTHROPIC_API_KEY \
  --set telemetry.endpoint=http://otel-collector:4317
```

---

## Multi-Language Detection

AutonomyLoops automatically detects project languages and loads appropriate steering:

| Extensions | Language | Steering Loaded |
|---|---|---|
| `.py` | Python | PEP 8, type hints, async patterns |
| `.ts`, `.tsx` | TypeScript | Strict mode, React patterns, Node.js |
| `.go` | Go | Effective Go, error handling, concurrency |
| `.rs` | Rust | Ownership, lifetimes, unsafe boundaries |
| `.java` | Java | Spring patterns, concurrency, GC |
| `.c`, `.h` | C | Memory safety, MISRA, bounds checking |
| `.cpp`, `.cc` | C++ | RAII, move semantics, STL usage |
| `.sol` | Solidity | Reentrancy, gas optimization |
| `.v`, `.sv` | Verilog/SV | Timing, synthesis, simulation |
| `.tf` | Terraform | State management, modules, security |
| `.yaml` (k8s) | Kubernetes | Resource limits, security contexts |

---

## Security Model

- **Token Vault**: API keys never stored in config files. Use env vars, AWS Secrets Manager, HashiCorp Vault, or Azure Key Vault.
- **RBAC**: Define who can run which agents, with which tools, on which resources.
- **Sandboxed Execution**: Tool calls run in isolated subprocesses or containers.
- **Audit Trail**: Every agent decision, tool call, and LLM interaction is logged with correlation IDs.
- **Cost Guards**: Per-session and per-org spending limits with automatic circuit breakers.

---

## Contributing

```bash
# Setup dev environment
make dev-setup

# Run tests
make test

# Run linter
make lint

# Build docs
make docs
```

---

## License

MIT

---

## Roadmap

- [x] Core agent loop with plan/act/observe
- [x] Multi-provider LLM abstraction
- [x] Role and mode steering system
- [x] Industry plugin architecture
- [x] Policy engine with HITL gates
- [x] OpenTelemetry integration
- [ ] Visual pipeline editor (web UI)
- [ ] Agent marketplace (share steering profiles)
- [ ] Distributed agent execution (Ray/Celery)
- [ ] Fine-tuning pipeline for org-specific models
- [ ] Compliance reporting (SOC2, ISO 27001)
