---
title: Changelog
---

# Changelog

## v2.0.0 (2026-06-27)

### 🎉 Initial Release Complete Framework Rewrite

**AutonomyLoops** is born a production-ready, generic multi-agent orchestration framework.

#### Core Features

- **Agent Loop** Plan → Act → Observe → Reflect autonomous execution
- **Multi-Agent Orchestrator** DAG-based pipeline coordination with parallel execution
- **Provider Abstraction** OpenAI, Anthropic, AWS Bedrock, Local (Ollama/vLLM)
- **State Machine** Explicit transitions with full audit history
- **Tool Framework** Registry, sandboxed execution, async handlers
- **Policy Engine** Declarative rules, HITL gates, cost guards
- **Telemetry** OpenTelemetry tracing, structured logging, Prometheus metrics
- **CLI** `autonomy-loops run`, `orchestrate`, `serve`, `init`

#### Steering System

- **7 Roles** Developer, Reviewer, Architect, Tester, DevOps, Security, Product Owner
- **6 Modes** Requirements, Design, Code, Test, Deploy, Review
- **5 Industry Plugins** FinTech, Cloud Native, Embedded, Networking, Data Engineering
- **Team Styles** Layered customization with `common.md` + mode-specific overrides

#### Pipelines

- `ci-review.yaml` Multi-agent code review
- `feature-build.yaml` End-to-end feature development
- `incident-response.yaml` Automated triage and remediation

#### Deployment

- Docker + Docker Compose (with full observability stack)
- Kubernetes manifests + HPA
- GitHub Actions CI/CD with Pages deployment
- GitLab CI/CD with Pages deployment

#### Documentation

- MkDocs Material with modern theming
- Integration guides: OpenTelemetry, Prometheus, Grafana, Kafka, NSQ, NATS, gRPC, Protobuf
- Getting started, configuration, security, and deployment guides
