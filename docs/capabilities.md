# Capabilities & AI Integration

## What AutonomyLoops Can Do

### Agent Capabilities

| Capability | How | Status |
|-----------|-----|--------|
| **Code Review** | `orbit run review-code` | ✅ Built-in skill |
| **Code Generation** | Agent loop with verify step | ✅ via `autonomy-loops run` |
| **Commit Messages** | `git diff | orbit run commit-msg` | ✅ Built-in skill |
| **Goal Planning** | `orbit plan "feature description"` | ✅ Built-in |
| **Multi-Agent Pipelines** | Orchestrator with step dependencies | ✅ YAML config |
| **Cost Tracking** | Per-run token logging | ✅ `.orbit/history.jsonl` |
| **Loop Readiness** | `orbit audit` (0-100 score) | ✅ Built-in |
| **Context Engineering** | `orbit context` (git-aware) | ✅ Built-in |
| **RAG** | Via provider tools + file ingestion | 🔜 Planned |
| **MCP Server** | Expose skills as MCP tools | 🔜 Planned |
| **Vector Search** | Embedding-based skill selection | 🔜 Planned |

### LLM Providers

| Provider | Type | Model Examples | Config |
|----------|------|----------------|--------|
| **ollama** (default) | Local, free, private | codellama, llama3.1, deepseek-coder, phi3, mistral | `ORBIT_BACKEND=ollama` |
| **OpenAI** | Cloud API | gpt-4o, gpt-4o-mini, o1-preview | `ORBIT_BACKEND=openai` |
| **Anthropic** | Cloud API | claude-sonnet-4-20250514, claude-3.5-haiku | Via provider config |
| **Google** | Cloud API | gemini-2.0-flash, gemini-pro | Via OpenAI-compatible proxy |
| **Azure OpenAI** | Enterprise cloud | gpt-4, gpt-35-turbo | Via provider config |
| **AWS Bedrock** | Enterprise cloud | Claude, Llama, Titan | Via provider config |
| **Local (any GGUF)** | Self-hosted | Any model via ollama or llama.cpp | `ORBIT_MODEL=<name>` |

### Tool Integrations

| Tool | What orbit Does With It | How |
|------|------------------------|-----|
| **Kiro** | Steering files teach Kiro about orbit | `.kiro/steering/orbit.md` |
| **Codex** | Skills invoked from Codex agent sessions | Shell command calls |
| **Claude Code** | Skills as part of loop-engineering patterns | SKILL.md format |
| **Copilot** | Context piping for better completions | `orbit context` output |
| **MCP** | Skill exposure as model-callable tools | MCP server (planned) |

---

## RAG (Retrieval-Augmented Generation)

### Current State

orbit's context engineering (`orbit context`) provides **git-aware RAG** without a vector database:
- Current branch, recent commits, changed files
- Staged diff as context for skills
- Project structure for planning

### Future: Full RAG Pipeline

```
Documents → Chunking → Embedding → Vector Store → Retrieval → LLM
                                                       ↑
                                            orbit skill query
```

**Planned implementation:**
- `orbit index` Index project files into local vector store (ChromaDB or SQLite-VSS)
- `orbit search "query"` Retrieve relevant chunks
- Skills auto-retrieve context before LLM call

### Why We Don't Ship RAG Today

1. **Complexity vs value**: For most developer tasks, git context + file piping is sufficient
2. **Dependencies**: Vector DBs add heavy deps (numpy, chromadb, etc.)
3. **Privacy**: Embedding models may phone home
4. **orbit's philosophy**: Start simple, add complexity when justified

### How to Do RAG Now (Manual)

```bash
# Index → Search → Pipe to skill
grep -rn "def " src/ | orbit run summarize    # poor man's RAG
cat relevant_file.py | orbit run explain       # targeted context
orbit context | orbit run plan-task            # git-aware planning
```

---

## LangChain Interop

AutonomyLoops is NOT LangChain, but they can coexist:

```python
# Use orbit skills inside a LangChain chain
import subprocess

def orbit_skill(skill_name: str, input_text: str) -> str:
    result = subprocess.run(
        ["orbit", "run", skill_name],
        input=input_text, capture_output=True, text=True
    )
    return result.stdout

# LangChain tool wrapping orbit
from langchain.tools import Tool
review_tool = Tool(
    name="code_review",
    func=lambda code: orbit_skill("review-code", code),
    description="Review code using orbit's review-code skill"
)
```

---

## Agent Architecture Patterns

### Pattern 1: Single Skill (orbit)

```bash
input | orbit run <skill>
```

One shot. Stateless. Fast. Good for: commit messages, quick reviews, explanations.

### Pattern 2: Loop (orbit plan → run → verify)

```bash
orbit plan "add caching"     # decompose
orbit run plan-task           # execute step
orbit audit                   # verify progress
```

Iterative. Stateful (plans saved). Good for: feature implementation, refactoring.

### Pattern 3: Multi-Agent Pipeline (autonomy-loops)

```yaml
# pipeline.yaml
steps:
  planner:
    role: architect
    mode: design
    task: "Design the caching layer"
  implementer:
    role: developer
    mode: code
    depends_on: planner
    task: "Implement based on planner output"
  reviewer:
    role: reviewer
    mode: review
    depends_on: implementer
```

```bash
autonomy-loops orchestrate --pipeline pipeline.yaml
```

Multi-agent. Parallel where possible. Good for: large features, CI integration.

### Pattern 4: Autonomous Loop (L3)

Agent runs continuously, finds work, executes, verifies. Needs:
- `LOOP.md` defining purpose
- `STATE.md` tracking progress
- Budget limits (token cap)
- Kill switch (policy engine)

---

## Testing with Different Models

### Quick benchmark: same skill, different models

```bash
# Compare code review quality across models
export CODE="def divide(a, b): return a / b"

echo "$CODE" | ORBIT_MODEL=phi3:mini orbit run review-code
echo "$CODE" | ORBIT_MODEL=codellama orbit run review-code
echo "$CODE" | ORBIT_MODEL=llama3.1 orbit run review-code
echo "$CODE" | ORBIT_MODEL=deepseek-coder-v2:16b orbit run review-code
```

### Model selection strategy

| Criteria | Choose |
|----------|--------|
| Speed matters, quality OK | `phi3:mini` (2s response) |
| Code-specific task | `qwen2.5-coder` or `codellama` |
| Reasoning/planning | `llama3.1:8b` |
| Maximum quality | `deepseek-coder-v2:16b` (needs 16GB RAM) |
| Production/billing OK | `gpt-4o-mini` via OpenAI |
