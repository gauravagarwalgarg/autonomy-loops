"""
orbit CLI tests run without LLM backend.
Tests: skill loading, context gathering, audit scoring, CLI parsing.

Run: python -m pytest tests/ -v
  Or: python tests/test_orbit.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orbit.runner import find_skill, parse_skill, list_skills, BUILTIN_SKILLS
from orbit.context import gather_context
from orbit.cli import main


def test_builtin_skills_exist():
    """All 5 built-in skills should be discoverable."""
    expected = ["summarize", "review-code", "plan-task", "explain", "commit-msg"]
    for name in expected:
        path = find_skill(name)
        assert path is not None, f"Skill '{name}' not found"
        assert path.exists(), f"Skill file doesn't exist: {path}"
    print("✓ All 5 built-in skills found")


def test_skill_parsing():
    """Skills should parse frontmatter correctly."""
    path = find_skill("review-code")
    meta, body = parse_skill(path)
    assert "model" in meta, "Frontmatter missing 'model'"
    assert "description" in meta, "Frontmatter missing 'description'"
    assert len(body) > 20, "System prompt body too short"
    print(f"✓ Skill parsed: model={meta['model']}, desc={meta['description'][:40]}...")


def test_context_gathering():
    """Context should return a dict with project info."""
    ctx = gather_context()
    assert "cwd" in ctx, "Context missing 'cwd'"
    assert isinstance(ctx, dict), "Context should be a dict"
    assert len(ctx) >= 2, "Context should have at least 2 keys"
    print(f"✓ Context gathered: keys={list(ctx.keys())}")


def test_audit_scoring():
    """Audit command should run without error."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "orbit", "audit"],
        capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    assert "Score:" in result.stdout, f"'Score:' not in output: {result.stdout}"
    print(f"✓ Audit runs successfully")


def test_cli_version(capsys=None):
    """CLI should respond to --version."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "orbit", "--version"],
        capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    assert "0.1.0" in result.stdout, f"Version not found in: {result.stdout}"
    print(f"✓ CLI version: {result.stdout.strip()}")


def test_cli_skills_list():
    """CLI 'skills' command should list built-in skills."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "orbit", "skills"],
        capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    assert "review-code" in result.stdout, f"'review-code' not in output: {result.stdout}"
    assert "summarize" in result.stdout, f"'summarize' not in output: {result.stdout}"
    print("✓ CLI skills command works")


if __name__ == "__main__":
    print("=" * 50)
    print("orbit CLI Test Suite (no LLM required)")
    print("=" * 50)
    test_builtin_skills_exist()
    test_skill_parsing()
    test_context_gathering()
    test_audit_scoring()
    test_cli_version()
    test_cli_skills_list()
    print("=" * 50)
    print("All tests passed! ✓")
