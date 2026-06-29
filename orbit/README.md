# orbit 🪐

> Second Brain Agent Orchestrator your CLI for agentic loops.

## Install

```bash
cd autonomy-loops/orbit
pip install -e .
```

## Usage

```bash
# Run a skill on stdin
echo "def foo(): pass" | orbit run review-code

# Plan a goal
orbit plan "Add rate limiting to the API service"

# List skills
orbit skills

# Get project context
orbit context

# Audit loop readiness
orbit audit

# Show loop state
orbit state

# Add a custom skill
orbit add my-custom-skill
```

## Concepts

| Concept | Source Inspiration | orbit Equivalent |
|---------|-------------------|-----------------|
| Fabric patterns | fabric-design | orbit skills (markdown prompt files) |
| Loop lifecycle | loop-engineering | orbit plan → run → verify |
| Skill registry | tower-registry | .orbit/skills/ directory |
| Agent orchestration | zeroshot | orbit run with LLM backends |

## Configuration

```bash
export ORBIT_BACKEND=ollama    # or "openai"
export ORBIT_MODEL=codellama   # any ollama model
export OPENAI_API_KEY=sk-...   # for openai backend
```

## Adding Skills

Skills are markdown files with YAML frontmatter:

```markdown
---
model: codellama
temperature: 0.3
description: What this skill does
---
System prompt goes here. The user's input is appended below this.
```

Place in `.orbit/skills/` (project-local) or `~/.orbit/skills/` (global).

## Architecture: autonomy_loops vs orbit

```
┌─────────────────────────────────────────────────────────────────┐
│                     Developer Workflow                            │
│                                                                   │
│  $ orbit run review-code      ←── lightweight, daily use         │
│  $ orbit plan "add auth"                                         │
│  $ orbit audit                                                   │
│  $ orbit context                                                 │
│                                                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │ (when task needs multi-agent power)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Orchestration Engine                          │
│                                                                   │
│  $ autonomy-loops run --role developer --mode code               │
│  $ autonomy-loops orchestrate --pipeline ci-review               │
│  $ autonomy-loops serve --port 8091                              │
│                                                                   │
│  ┌──────────┐  ┌────────────┐  ┌────────┐  ┌──────────────┐   │
│  │  Agent   │  │Orchestrator│  │ Policy │  │  Providers   │   │
│  │  Loop    │  │  Pipeline  │  │ Engine │  │ (OpenAI/etc) │   │
│  └──────────┘  └────────────┘  └────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### When to use which:

| I want to... | Use |
|-------------|-----|
| Review code quickly | `orbit run review-code` |
| Generate a commit message | `git diff | orbit run commit-msg` |
| Plan a feature | `orbit plan "..."` |
| Check project maturity | `orbit audit` |
| Run a multi-agent pipeline | `autonomy-loops orchestrate --pipeline X` |
| Deploy an agent with RBAC | `autonomy-loops run --role X --mode Y` |
| Start the dashboard | `autonomy-loops serve` |

### Why two tools, not one:

| | orbit | autonomy-loops |
|---|---|---|
| **Deps** | stdlib + pyyaml | click, pydantic, opentelemetry, etc |
| **Speed** | Instant startup | Heavier import chain |
| **Scope** | Single skill/task | Multi-agent coordination |
| **LLM** | ollama/openai direct | Provider abstraction layer |
| **State** | `.orbit/` files | State machine + persistence |
| **Use case** | Personal second brain | Team/org agent platform |

orbit is the **pocket knife**. autonomy-loops is the **workshop**.

## Loop Lifecycle

```
plan → act → verify → iterate
 │      │      │        │
 │      │      │        └── orbit plan (refine)
 │      │      └── orbit audit (score)
 │      └── orbit run <skill> (execute)
 └── orbit plan <goal> (decompose)
```
