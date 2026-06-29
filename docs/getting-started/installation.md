---
title: Installation
---

# Installation

## From PyPI

=== "Minimal (no provider SDKs)"

    ```bash
    pip install autonomy-loops
    ```

=== "With Anthropic"

    ```bash
    pip install "autonomy-loops[anthropic]"
    ```

=== "With OpenAI"

    ```bash
    pip install "autonomy-loops[openai]"
    ```

=== "All Providers"

    ```bash
    pip install "autonomy-loops[all]"
    ```

=== "Development"

    ```bash
    pip install "autonomy-loops[dev,all]"
    ```

## From Source

```bash
git clone https://github.com/GauravAgarwalGarg/AutonomyLoops.git
cd AutonomyLoops
pip install -e ".[dev,all]"
```

## Requirements

- Python 3.11 or higher
- An API key for at least one LLM provider (Anthropic, OpenAI, or a local model server)

## Verify Installation

```bash
autonomy-loops --version
# autonomy-loops, version 2.0.0
```

## Docker

```bash
docker pull ghcr.io/gauravagrawalgarg/autonomy-loops:latest
docker run --rm autonomy-loops --version
```
