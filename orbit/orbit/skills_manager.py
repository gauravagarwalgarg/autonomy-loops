"""Skills manager add and manage skill templates."""
from pathlib import Path


TEMPLATE = """---
model: codellama
temperature: 0.3
description: {description}
---
You are a helpful assistant. Given the user's input, provide a clear and useful response.

Customize this system prompt for your specific use case.
"""


def add_skill(name: str) -> None:
    """Create a new skill template in the local .orbit/skills/ directory."""
    skills_dir = Path(".orbit/skills")
    skills_dir.mkdir(parents=True, exist_ok=True)

    skill_path = skills_dir / f"{name}.md"
    if skill_path.exists():
        print(f"⚠️  Skill '{name}' already exists: {skill_path}")
        return

    description = f"Custom skill: {name}"
    content = TEMPLATE.format(description=description)
    skill_path.write_text(content)
    print(f"✅ Created skill: {skill_path}")
    print(f"   Edit the file to customize the system prompt.")
    print(f"   Run: orbit run {name}")
