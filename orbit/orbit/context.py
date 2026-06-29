"""Context engineering gathers project context for LLM consumption."""
import json
import subprocess
import sys
from pathlib import Path


def show_context(output_format: str = "markdown") -> None:
    """Gather and display current project context."""
    ctx = gather_context()

    if output_format == "json":
        print(json.dumps(ctx, indent=2))
    else:
        print(_format_markdown(ctx))


def gather_context() -> dict:
    """Collect context: git info, directory structure, recent changes."""
    ctx = {
        "cwd": str(Path.cwd()),
        "git_branch": _run_git("rev-parse", "--abbrev-ref", "HEAD"),
        "git_status": _run_git("status", "--short"),
        "recent_commits": _run_git("log", "--oneline", "-5"),
        "changed_files": _run_git("diff", "--name-only"),
        "staged_files": _run_git("diff", "--cached", "--name-only"),
    }
    return ctx


def _format_markdown(ctx: dict) -> str:
    """Format context as readable markdown."""
    lines = ["# 🪐 Current Context\n"]

    lines.append(f"**Directory:** `{ctx['cwd']}`")
    lines.append(f"**Branch:** `{ctx['git_branch']}`\n")

    if ctx["git_status"]:
        lines.append("## Status")
        lines.append(f"```\n{ctx['git_status']}\n```\n")

    if ctx["staged_files"]:
        lines.append("## Staged")
        lines.append(f"```\n{ctx['staged_files']}\n```\n")

    if ctx["changed_files"]:
        lines.append("## Changed (unstaged)")
        lines.append(f"```\n{ctx['changed_files']}\n```\n")

    if ctx["recent_commits"]:
        lines.append("## Recent Commits")
        lines.append(f"```\n{ctx['recent_commits']}\n```\n")

    return "\n".join(lines)


def _run_git(*args: str) -> str:
    """Run a git command and return output, or empty string on failure."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
