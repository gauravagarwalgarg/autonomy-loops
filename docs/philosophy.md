# Philosophy & Design Choices

## Core Belief

> **An agent without a loop is just a prompt. A loop without governance is just chaos.**

AutonomyLoops exists because the industry needs a middle ground between "paste into ChatGPT" and "build a custom LangChain monolith." We chose a different path.

## Design Principles

### 1. Loops > Chains

LangChain chains are **linear**: input → step → step → output. Real agent work is **iterative**: plan → act → verify → revise → verify → done. We model this as a loop with exit conditions, not a pipeline with fixed steps.

```
LangChain:   input ──► chain step 1 ──► chain step 2 ──► output
                           (linear, fragile)

AutonomyLoops: goal ──► plan ──► act ──► verify ──┐
                         ▲                         │
                         └────── revise ◄──────────┘
                              (iterative, resilient)
```

### 2. Skills > Prompts

A prompt is disposable. A **skill** is versioned, discoverable, team-shareable, and testable. Every prompt in this system lives as a markdown file with metadata:

```yaml
---
model: codellama
temperature: 0.3
description: Review code for bugs
---
System prompt content here...
```

This is the **fabric pattern** adapted: your prompt library is your intellectual property, stored as code, evolved via git.

### 3. Governance > Speed

We will always trade 10% speed for 100% auditability. Every agent action is logged. Every decision has a paper trail. Every escalation has a human gate. This isn't academic it's how you deploy agents in regulated environments (finance, defense, healthcare).

### 4. Local-First > Cloud-First

Your code should never leave your machine by default. orbit uses ollama (local inference) as the primary backend. Cloud providers are opt-in, not opt-out. This makes the tool:
- Safe for proprietary code
- Free to experiment with
- Fast (no network latency)
- Private (no telemetry)

### 5. Composable > Monolithic

Every component is independently useful:
- `orbit` works without `autonomy_loops` (zero deps)
- Skills work without the orchestrator
- The policy engine works without providers
- Telemetry is optional, not mandatory

## Why Not LangChain?

| Concern | LangChain | AutonomyLoops |
|---------|-----------|---------------|
| **Abstraction overhead** | 15+ imports for hello world | `orbit run explain` (zero imports) |
| **Vendor lock-in** | Tightly coupled to OpenAI patterns | Provider-agnostic (ollama, OpenAI, Anthropic, any) |
| **Governance** | Afterthought | First-class (RBAC, HITL, policy engine) |
| **Skill reuse** | Custom chains per project | Shared skill files across team/org |
| **Cost control** | Manual token counting | Built-in budget tracking + kill switches |
| **Local inference** | Awkward integration | Native ollama support, default backend |
| **Complexity** | Framework you must learn | CLI you just use |

LangChain solves **tooling orchestration** (call APIs in sequence). We solve **agent governance** (run loops safely at scale).

## Why Not Raw API Calls?

Because after the 5th time you:
- Rewrite the same "review this code" prompt
- Forget to track token costs
- Ship without checking if the agent hallucinated
- Lose the context of what the agent was trying to do

...you want a system. That system is AutonomyLoops.

## The Two Layers

```
╔══════════════════════════════════════════════════╗
║  orbit (Developer CLI)                           ║
║  • Skills (prompt templates)                     ║
║  • Context (git awareness)                       ║
║  • Audit (loop readiness)                        ║
║  • Plan (goal decomposition)                     ║
║  Deps: stdlib + pyyaml                           ║
╠══════════════════════════════════════════════════╣
║  autonomy_loops (Orchestration Engine)           ║
║  • Multi-agent pipelines                         ║
║  • Provider abstraction                          ║
║  • Policy engine (RBAC, HITL)                    ║
║  • State machines                                ║
║  • Telemetry (OpenTelemetry)                     ║
║  Deps: click, pydantic, providers                ║
╚══════════════════════════════════════════════════╝
```

orbit is what you use on day 1. autonomy_loops is what you grow into on day 100.

## Influence Map

| Source | What We Took | What We Changed |
|--------|-------------|-----------------|
| [fabric](https://github.com/danielmiessler/fabric) | Prompt-as-file pattern | Added frontmatter, skill registry, LLM routing |
| [loop-engineering](https://github.com/cobusgreyling/loop-engineering) | Loop lifecycle (plan→act→verify) | Added governance, budget, maturity levels |
| [tower-registry](https://github.com/user/tower-registry) | Skill discoverability via JSON | Simplified to file-based (.orbit/skills/) |
| [zeroshot](https://github.com/the-open-engine/zeroshot) | Plan→implement→validate pattern | Merged into single CLI, not separate agents |
| LangChain | Provider abstraction | Removed chain complexity, kept provider swap |
| CrewAI | Role-based agents | Added mode layering (role × mode matrix) |
