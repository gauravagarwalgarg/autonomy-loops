"""Skill runner executes a prompt template against an LLM."""
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

ORBIT_DIR = Path.home() / ".orbit"
SKILLS_DIR = ORBIT_DIR / "skills"
HISTORY_FILE = ORBIT_DIR / "history.jsonl"
BUILTIN_SKILLS = Path(__file__).parent / "skills"


def run_skill(skill_name: str, input_text: str = "", model: str = "") -> str:
    """Load skill, merge with input, call LLM, return output."""
    skill_path = find_skill(skill_name)
    if not skill_path:
        print(f"Skill '{skill_name}' not found. Run 'orbit skills' to list available.", file=sys.stderr)
        sys.exit(1)

    # Parse skill file (markdown with YAML frontmatter)
    meta, system_prompt = parse_skill(skill_path)
    model = model or meta.get("model", os.environ.get("ORBIT_MODEL", "codellama"))

    # Build full prompt
    full_prompt = f"{system_prompt}\n\n---\nUser Input:\n{input_text}"

    # Call LLM
    backend = os.environ.get("ORBIT_BACKEND", "ollama")
    if backend == "ollama":
        output = call_ollama(model, full_prompt)
    elif backend == "openai":
        output = call_openai(model, system_prompt, input_text)
    else:
        output = f"Unknown backend: {backend}"

    # Log
    log_run(skill_name, model, len(input_text), len(output))
    return output


def find_skill(name: str) -> Path | None:
    """Search for a skill by name in skills directories."""
    # Check project-local skills first
    local = Path(".orbit/skills") / f"{name}.md"
    if local.exists():
        return local
    # Then global
    global_skill = SKILLS_DIR / f"{name}.md"
    if global_skill.exists():
        return global_skill
    # Then built-in
    builtin = BUILTIN_SKILLS / f"{name}.md"
    if builtin.exists():
        return builtin
    return None


def parse_skill(path: Path) -> tuple[dict, str]:
    """Parse skill markdown: YAML frontmatter + body as system prompt."""
    content = path.read_text()
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                import yaml
                meta = yaml.safe_load(parts[1]) or {}
            except ImportError:
                # Fallback: simple key: value parsing
                meta = _parse_frontmatter_simple(parts[1])
            except Exception:
                meta = {}
            return meta, parts[2].strip()
    return {}, content.strip()


def _parse_frontmatter_simple(text: str) -> dict:
    """Parse YAML-like frontmatter without pyyaml dependency."""
    meta = {}
    for line in text.strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            # Try numeric conversion
            try:
                value = float(value)
                if value == int(value):
                    value = int(value)
            except (ValueError, TypeError):
                pass
            meta[key] = value
    return meta


def call_ollama(model: str, prompt: str) -> str:
    """Call ollama CLI."""
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt, capture_output=True, text=True, timeout=120
        )
        return result.stdout
    except FileNotFoundError:
        return "Error: ollama not installed (https://ollama.ai)"
    except subprocess.TimeoutExpired:
        return "Error: LLM call timed out (120s)"


def call_openai(model: str, system: str, user: str) -> str:
    """Call OpenAI API."""
    import urllib.request
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        return "Error: OPENAI_API_KEY not set"
    data = json.dumps({"model": model or "gpt-4o-mini", "messages": [
        {"role": "system", "content": system},
        {"role": "user", "content": user}
    ], "temperature": 0.3}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions",
        data=data, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"


def log_run(skill: str, model: str, input_len: int, output_len: int) -> None:
    """Append usage record to history."""
    ORBIT_DIR.mkdir(parents=True, exist_ok=True)
    entry = {"ts": datetime.now().isoformat(), "skill": skill, "model": model,
             "input_tokens": input_len // 4, "output_tokens": output_len // 4}
    with open(HISTORY_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def list_skills() -> None:
    """List all available skills from all sources."""
    sources = [
        ("built-in", BUILTIN_SKILLS),
        ("global", SKILLS_DIR),
        ("local", Path(".orbit/skills")),
    ]
    found = False
    for label, directory in sources:
        if directory.exists():
            skills = sorted(directory.glob("*.md"))
            if skills:
                print(f"\n  [{label}] {directory}")
                for s in skills:
                    meta, _ = parse_skill(s)
                    desc = meta.get("description", "")
                    print(f"    • {s.stem:<20} {desc}")
                found = True
    if not found:
        print("No skills found. Run 'orbit add <name>' to create one.")
    print()
