"""orbit CLI Alias for autonomy-loops skill commands.

orbit is the lightweight second-brain interface. It's merged into the
main autonomy-loops CLI but also works standalone via this entry point.
"""
import argparse
import sys

from orbit import __version__


def main():
    """orbit entry point delegates to autonomy-loops CLI if available, else standalone."""
    # Try to use the merged CLI first
    try:
        from autonomy_loops.cli import main as al_main
        # Remap: 'orbit run X' → 'autonomy-loops skill X'
        # But keep orbit's own subcommands working directly
        sys.argv[0] = "autonomy-loops"
        if len(sys.argv) > 1 and sys.argv[1] == "run":
            sys.argv[1] = "skill"
        al_main(standalone_mode=False)
        return
    except (ImportError, Exception):
        pass

    # Fallback: standalone orbit (no autonomy_loops deps)
    _standalone_main()


def _standalone_main():
    """Standalone orbit CLI when autonomy_loops is not importable."""
    parser = argparse.ArgumentParser(
        prog="orbit",
        description="🪐 orbit Second Brain Agent Orchestrator CLI",
    )
    parser.add_argument("--version", action="version", version=f"orbit {__version__}")
    sub = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="Execute a skill (prompt template + LLM)")
    run_p.add_argument("skill", help="Skill name to execute")
    run_p.add_argument("--input", "-i", help="Input text (default: read stdin)")
    run_p.add_argument("--model", "-m", default="", help="Override model")

    sub.add_parser("skills", help="List available skills")

    plan_p = sub.add_parser("plan", help="Break a goal into steps")
    plan_p.add_argument("goal", nargs="+", help="Goal description")

    sub.add_parser("audit", help="Score loop readiness")
    sub.add_parser("state", help="Show loop state")
    sub.add_parser("context", help="Show git context")

    add_p = sub.add_parser("add", help="Add a new skill template")
    add_p.add_argument("name", help="Skill name")

    args = parser.parse_args()

    if args.command == "run":
        from orbit.runner import run_skill
        input_text = args.input or (sys.stdin.read() if not sys.stdin.isatty() else "")
        print(run_skill(args.skill, input_text, args.model))
    elif args.command == "skills":
        from orbit.runner import list_skills
        list_skills()
    elif args.command == "plan":
        from orbit.planner import plan_goal
        plan_goal(" ".join(args.goal))
    elif args.command == "audit":
        from orbit.audit import audit_project
        audit_project()
    elif args.command == "state":
        from orbit.state import show_state
        show_state()
    elif args.command == "context":
        from orbit.context import show_context
        show_context()
    elif args.command == "add":
        from orbit.skills_manager import add_skill
        add_skill(args.name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
