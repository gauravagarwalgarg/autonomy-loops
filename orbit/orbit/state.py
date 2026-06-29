"""State manager shows current loop state, tasks, and budget."""
import json
from pathlib import Path
from datetime import datetime


ORBIT_DIR = Path(".orbit")
HISTORY_FILE = Path.home() / ".orbit" / "history.jsonl"
STATE_FILE = Path("STATE.md")


def show_state() -> None:
    """Display current loop state: active tasks, budget, recent activity."""
    print("🪐 Loop State\n")

    # Show STATE.md if present
    if STATE_FILE.exists():
        print("## State File")
        content = STATE_FILE.read_text().strip()
        # Show first 20 lines
        lines = content.splitlines()[:20]
        for line in lines:
            print(f"  {line}")
        if len(content.splitlines()) > 20:
            print(f"  ... ({len(content.splitlines()) - 20} more lines)")
        print()

    # Show recent run history
    _show_recent_history()

    # Show active plans
    _show_active_plans()

    # Show budget summary
    _show_budget()


def _show_recent_history() -> None:
    """Show last 5 skill runs."""
    if not HISTORY_FILE.exists():
        print("## History: No runs yet\n")
        return

    entries = []
    with open(HISTORY_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    if not entries:
        return

    print(f"## Recent Activity ({len(entries)} total runs)")
    for entry in entries[-5:]:
        ts = entry.get("ts", "?")[:16]
        skill = entry.get("skill", "?")
        model = entry.get("model", "?")
        tokens = entry.get("input_tokens", 0) + entry.get("output_tokens", 0)
        print(f"  {ts}  {skill:<18} {model:<12} ~{tokens} tokens")
    print()


def _show_active_plans() -> None:
    """Show plans in .orbit/plans/."""
    plans_dir = ORBIT_DIR / "plans"
    if not plans_dir.exists():
        return

    plans = sorted(plans_dir.glob("*.md"))
    if plans:
        print(f"## Plans ({len(plans)})")
        for p in plans[-5:]:
            print(f"  📋 {p.stem}")
        print()


def _show_budget() -> None:
    """Show estimated token budget usage."""
    if not HISTORY_FILE.exists():
        return

    total_tokens = 0
    with open(HISTORY_FILE) as f:
        for line in f:
            if line.strip():
                try:
                    entry = json.loads(line)
                    total_tokens += entry.get("input_tokens", 0) + entry.get("output_tokens", 0)
                except json.JSONDecodeError:
                    pass

    if total_tokens > 0:
        print(f"## Budget")
        print(f"  Total tokens used: ~{total_tokens:,}")
        print(f"  Estimated cost: ~${total_tokens * 0.000003:.4f} (at $3/1M tokens)")
        print()
