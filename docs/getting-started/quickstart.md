---
title: Quick Start
---

# Quick Start

## 1. Initialize Your Project

```bash
cd your-project/
autonomy-loops init
```

This creates:

- `autonomy-loops.yaml` Configuration file
- `styles/common.md` Team conventions (customize later)

## 2. Set Your API Key

=== "Anthropic (recommended)"

    ```bash
    export ANTHROPIC_API_KEY="sk-ant-api03-..."
    ```

=== "OpenAI"

    ```bash
    export OPENAI_API_KEY="sk-..."
    ```

=== "Local (Ollama)"

    ```bash
    # Start Ollama first
    ollama serve
    ollama pull llama3.1:70b
    ```

## 3. Run Your First Agent

```bash
autonomy-loops run \
  --role developer \
  --mode code \
  --task "Create a FastAPI health check endpoint with proper error handling"
```

## 4. Run a Multi-Agent Pipeline

```bash
autonomy-loops orchestrate --pipeline pipelines/ci-review.yaml
```

## 5. Start the Dashboard

```bash
autonomy-loops serve --port 8091
# Open http://localhost:8091
```

## What Just Happened?

1. The **steering loader** assembled a system prompt from your role (`developer`) + mode (`code`) + any plugins
2. The **agent loop** executed Plan → Act → Observe → Reflect until the task was complete
3. The **policy engine** checked each tool call against your rules
4. The **telemetry system** logged traces, metrics, and an audit trail

## Next Steps

- [Configure providers and policies](../configuration/index.md)
- [Explore available roles and modes](../roles-modes/index.md)
- [Add industry plugins](../plugins/index.md)
- [Set up observability](../integrations/observability.md)
