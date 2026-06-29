"""Loop readiness auditor scores project's agentic loop maturity."""
from pathlib import Path


CHECKS = [
    ("LOOP.md exists", Path("LOOP.md"), 15),
    ("STATE.md exists", Path("STATE.md"), 15),
    (".orbit/ directory", Path(".orbit"), 10),
    (".orbit/skills/ with skills", Path(".orbit/skills"), 15),
    (".orbit/plans/ with plans", Path(".orbit/plans"), 10),
    ("BUDGET.md or budget tracking", Path("BUDGET.md"), 10),
    ("README.md exists", Path("README.md"), 5),
    (".orbit/history.jsonl (run log)", Path(".orbit/history.jsonl"), 10),
    ("DECISIONS.md (decision log)", Path("DECISIONS.md"), 5),
    ("tests/ directory", Path("tests"), 5),
]


def audit_project() -> None:
    """Score project loop readiness and suggest improvements."""
    score = 0
    max_score = 0
    results = []

    for label, path, points in CHECKS:
        max_score += points
        exists = path.exists()
        if exists and path.is_dir():
            # Directories must have content
            exists = any(path.iterdir()) if path.exists() else False
        if exists:
            score += points
            results.append(("✅", label, points))
        else:
            results.append(("❌", label, points))

    # Display results
    pct = int((score / max_score) * 100) if max_score else 0
    level = _maturity_level(pct)

    print(f"🪐 Loop Readiness Audit")
    print(f"{'=' * 40}")
    print(f"Score: {score}/{max_score} ({pct}%) {level}\n")

    for icon, label, points in results:
        print(f"  {icon} {label} (+{points})")

    print(f"\n{'=' * 40}")
    _suggest_next(results)


def _maturity_level(pct: int) -> str:
    """Map percentage to maturity level."""
    if pct >= 90:
        return "Level 5: Autonomous"
    elif pct >= 70:
        return "Level 4: Managed"
    elif pct >= 50:
        return "Level 3: Defined"
    elif pct >= 25:
        return "Level 2: Emerging"
    else:
        return "Level 1: Initial"


def _suggest_next(results: list) -> None:
    """Suggest next steps based on missing items."""
    missing = [label for icon, label, _ in results if icon == "❌"]
    if not missing:
        print("🎉 All checks pass! Your project is fully loop-ready.")
        return

    print("\n📋 Next steps to level up:")
    for i, item in enumerate(missing[:3], 1):
        print(f"  {i}. Add {item}")
