# orbit Unified CLI Guide

## What is orbit?

orbit is the **developer-facing interface** to AutonomyLoops. One tool, two modes:

| Mode | Entry Point | Deps | Use Case |
|------|------------|------|----------|
| **Lightweight** | `orbit <cmd>` | stdlib + pyyaml | Daily skills, context, audit |
| **Full engine** | `autonomy-loops <cmd>` | click, pydantic, providers | Multi-agent orchestration |

Both share the same skill library and loop state.

---

## Install

```bash
cd autonomy-loops/orbit
pip install -e .

# Verify
orbit --version
orbit skills
```

---

## Commands (Merged)

```bash
# ─── Skill execution (lightweight, daily use) ───────────────────
orbit run <skill>         # Execute a skill against LLM
orbit skills              # List all available skills
orbit plan <goal>         # Decompose goal into steps
orbit audit               # Score loop readiness 0-100
orbit context             # Git branch + status + changes
orbit state               # History + budget tracking
orbit add <name>          # Create new skill template

# ─── Full orchestration (heavy, multi-agent) ────────────────────
autonomy-loops run --role dev --mode code --task "..."
autonomy-loops orchestrate --pipeline ci-review.yaml
autonomy-loops serve --port 8091
autonomy-loops init

# ─── Merged orbit commands also via autonomy-loops ──────────────
autonomy-loops skill <name>
autonomy-loops skills
autonomy-loops audit
autonomy-loops context
autonomy-loops plan "..."
```

---

## Testing with LLaMA (ollama)

### Setup (one-time)

```bash
# 1. Install ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull a model
ollama pull llama3.1        # 4.7 GB, good general reasoning
ollama pull codellama       # 3.8 GB, code-focused (default for orbit)

# 3. Configure orbit
export ORBIT_BACKEND=ollama
export ORBIT_MODEL=llama3.1   # or codellama
```

### Test end-to-end

```bash
# Test 1: Review code
echo 'def divide(a, b): return a / b' | orbit run review-code
# Expected: mentions ZeroDivisionError, suggests guard

# Test 2: Generate commit message
git diff --staged | orbit run commit-msg
# Expected: conventional commit format

# Test 3: Plan a feature
orbit plan "Add rate limiting to the REST API"
# Expected: numbered steps with file paths

# Test 4: Explain code
cat autonomy_loops/agent.py | orbit run explain
# Expected: plain English description of the agent loop

# Test 5: Summarize
git log --oneline -20 | orbit run summarize
# Expected: bullet-point summary of recent work
```

### Switch models mid-session

```bash
# Quick task (small model, fast)
ORBIT_MODEL=phi3:mini orbit run commit-msg <<< "$(git diff --staged)"

# Deep analysis (large model, slower)
ORBIT_MODEL=deepseek-coder-v2:16b orbit run review-code < complex_file.py
```

---

## Testing with Kiro

### Method 1: Terminal commands (simplest)

In Kiro chat, type any of:

```
Run `orbit skills` in the terminal
```

```
Run `orbit audit` and explain the score
```

```
Run `orbit context` and summarize what I'm working on
```

```
Pipe autonomy_loops/cli.py to `orbit run review-code` and list issues
```

### Method 2: Kiro Steering (project-aware)

The repo includes `.kiro/steering/orbit.md` which teaches Kiro about orbit. When this steering is active, Kiro will:

- Suggest `orbit run review-code` when you ask for code review
- Suggest `orbit plan "..."` when you describe a feature
- Suggest `orbit audit` when you ask about project health

### Method 3: Kiro Hook (auto-trigger)

Create a hook that runs orbit on every file save:

```json
{
  "name": "orbit-review",
  "version": "1.0.0",
  "when": { "type": "fileEdited", "patterns": ["*.py"] },
  "then": { "type": "runCommand", "command": "orbit run review-code < ${file}" }
}
```

### Method 4: MCP Server (tool calling)

For deeper integration where Kiro directly invokes orbit as a tool:

Add to your `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "orbit": {
      "command": "python3",
      "args": ["-c", "from orbit.mcp_server import serve; serve()"],
      "env": { "ORBIT_BACKEND": "ollama", "ORBIT_MODEL": "codellama" }
    }
  }
}
```

> Note: `orbit.mcp_server` is on the roadmap. For now, use Method 1-3.

---

## Verification Checklist

Run these to confirm everything works:

```bash
# 1. orbit standalone (no deps beyond stdlib)
orbit --version                        # → orbit 0.1.0
orbit skills                           # → lists 5 built-in skills
orbit audit                            # → shows score + maturity level
orbit context                          # → git branch + status

# 2. orbit + ollama (requires ollama running)
ollama list                            # → shows downloaded models
echo "hello world" | orbit run explain # → LLM explains the input

# 3. orbit tests (no LLM required)
cd orbit && python3 tests/test_orbit.py
# → All tests passed! ✓

# 4. Full CLI (requires autonomy_loops deps)
autonomy-loops --version               # → autonomy-loops 2.0.0
autonomy-loops skills                  # → same skill list as orbit
```

---

## Architecture (After Merge)

```
autonomy-loops/
│
├── autonomy_loops/              # Heavy orchestration engine
│   ├── cli.py                   # Click CLI (run, orchestrate, serve, init)
│   │   └── + skill, skills,    #   + merged orbit commands
│   │       audit, context,
│   │       plan, state
│   ├── agent.py                 # Agent loop (plan→act→verify)
│   ├── orchestrator.py          # Multi-agent pipeline
│   ├── providers/               # LLM providers (OpenAI, Anthropic, etc)
│   ├── policy/                  # RBAC, HITL gates, kill switches
│   ├── steering/                # Role/mode layering
│   ├── telemetry/               # OpenTelemetry tracing
│   └── tools/                   # File, shell, web tool execution
│
├── orbit/                       # Lightweight skill layer
│   └── orbit/
│       ├── cli.py               # Standalone fallback (argparse, no deps)
│       ├── runner.py            # Skill execution (ollama/openai)
│       ├── planner.py           # Goal decomposition
│       ├── context.py           # Git context engineering
│       ├── audit.py             # Loop readiness scoring
│       ├── state.py             # Budget/history tracking
│       └── skills/              # Prompt templates (*.md)
│           ├── review-code.md
│           ├── commit-msg.md
│           ├── plan-task.md
│           ├── explain.md
│           └── summarize.md
│
├── docs/                        # MkDocs documentation
│   ├── orbit-guide.md           # ← This file
│   └── orbit-ollama-setup.md    # First principles ollama setup
│
└── .kiro/steering/orbit.md      # Kiro awareness of orbit
```

---

## FAQ

**Q: Do I need ollama to use orbit?**
A: No. `orbit audit`, `orbit context`, `orbit skills` work without any LLM. Only `orbit run` needs a backend.

**Q: Can I use GPT-4 instead of local models?**
A: Yes. `export ORBIT_BACKEND=openai ORBIT_MODEL=gpt-4o OPENAI_API_KEY=sk-...`

**Q: Is my code sent to the cloud?**
A: Only if you set `ORBIT_BACKEND=openai`. With ollama, everything stays local.

**Q: How do I add a custom skill for my team?**
A: `orbit add my-skill` creates a template. Edit `.orbit/skills/my-skill.md`, commit to git. Team shares it.

**Q: What's the difference between orbit and autonomy-loops?**
A: orbit = pocket knife (personal, instant). autonomy-loops = workshop (team, orchestrated). Same repo, same skills, different depth.
