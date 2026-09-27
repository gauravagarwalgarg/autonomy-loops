"""Goal planner decomposes a goal into actionable steps."""
import re
import sys
from pathlib import Path
from datetime import datetime


PLANS_DIR = Path(".orbit/plans")


def plan_goal(goal: str) -> None:
    """Break a goal into steps using the plan-task skill or fallback."""
    from orbit.runner import find_skill, run_skill

    print(f"🪐 Planning: {goal}\n")

    # Try using the plan-task skill
    skill_path = find_skill("plan-task")
    if skill_path:
        output = run_skill("plan-task", goal)
        print(output)
    else:
        # Fallback: generate a basic plan structure
        output = _fallback_plan(goal)
        print(output)

    # Save plan to file
    save_plan(goal, output)


def _fallback_plan(goal: str) -> str:
    """Generate a basic plan template when no LLM is available."""
    return f"""# Plan: {goal}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Steps

1. [ ] Research Understand requirements and constraints
2. [ ] Design Outline the approach and key decisions
3. [ ] Implement Write the core logic
4. [ ] Test Verify correctness and edge cases
5. [ ] Integrate Connect with existing systems
6. [ ] Document Update docs and README

---
*Tip: Run with an LLM backend for detailed, goal-specific plans.*
*Set ORBIT_BACKEND=ollama or ORBIT_BACKEND=openai*
"""


def save_plan(goal: str, content: str) -> None:
    """Save plan to .orbit/plans/<slug>.md"""
    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    slug = _slugify(goal)
    plan_path = PLANS_DIR / f"{slug}.md"
    plan_path.write_text(f"# {goal}\n\n{content}\n")
    print(f"\n💾 Plan saved: {plan_path}")


def _slugify(text: str) -> str:
    """Convert text to a filename-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60].strip("-")
