"""Steering loader assembles the agent's instruction stack.

The steering stack is loaded in this order:
1. Role file (who the agent is)
2. Mode file (what lifecycle phase)
3. Plugin files (domain knowledge packs)
4. Team style files (org/team overrides)

Each layer adds to the system prompt, with later layers taking precedence.
"""

from __future__ import annotations

from pathlib import Path

from autonomy_loops.config import Config

# Default paths relative to package installation
_PACKAGE_DIR = Path(__file__).parent.parent.parent
_ROLES_DIR = _PACKAGE_DIR / "roles"
_MODES_DIR = _PACKAGE_DIR / "modes"
_PLUGINS_DIR = _PACKAGE_DIR / "plugins"


class SteeringLoader:
    """Loads and assembles steering files into a system prompt stack."""

    def __init__(self, config: Config, *, base_dir: Path | None = None) -> None:
        self._config = config
        self._base_dir = base_dir or _PACKAGE_DIR

    def load(self, *, role: str | None = None, mode: str | None = None) -> list[str]:
        """Load the full steering stack.

        Args:
            role: Override role from config.
            mode: Override mode from config.

        Returns:
            List of steering content strings (in load order).
        """
        parts: list[str] = []

        # 1. Load role
        role_name = role or self._config.steering.role
        role_content = self._load_role(role_name)
        if role_content:
            parts.append(role_content)

        # 2. Load mode
        mode_name = mode or self._config.steering.mode
        mode_content = self._load_mode(mode_name)
        if mode_content:
            parts.append(mode_content)

        # 3. Load plugins
        for plugin_id in self._config.steering.plugins:
            plugin_content = self._load_plugin(plugin_id)
            if plugin_content:
                parts.append(plugin_content)

        # 4. Load team styles
        styles_content = self._load_styles(mode_name)
        parts.extend(styles_content)

        return parts

    def _load_role(self, role: str) -> str | None:
        """Load a role definition file."""
        role_file = self._base_dir / "roles" / f"{role}.md"
        if role_file.exists():
            return role_file.read_text(encoding="utf-8")
        return None

    def _load_mode(self, mode: str) -> str | None:
        """Load a mode definition file."""
        mode_file = self._base_dir / "modes" / f"{mode}.md"
        if mode_file.exists():
            return mode_file.read_text(encoding="utf-8")
        return None

    def _load_plugin(self, plugin_id: str) -> str | None:
        """Load all skill files for a plugin."""
        plugin_dir = self._base_dir / "plugins" / plugin_id
        if not plugin_dir.is_dir():
            return None

        parts: list[str] = []
        for md_file in sorted(plugin_dir.glob("*.md")):
            parts.append(md_file.read_text(encoding="utf-8"))

        return "\n\n---\n\n".join(parts) if parts else None

    def _load_styles(self, mode: str) -> list[str]:
        """Load team style overrides."""
        styles_dir_name = self._config.steering.styles_dir
        if not styles_dir_name:
            return []

        styles_dir = Path(styles_dir_name)
        if not styles_dir.is_dir():
            return []

        parts: list[str] = []

        # common.md always loaded
        common = styles_dir / "common.md"
        if common.exists():
            parts.append(common.read_text(encoding="utf-8"))

        # {mode}.md mode-specific
        mode_style = styles_dir / f"{mode}.md"
        if mode_style.exists():
            parts.append(mode_style.read_text(encoding="utf-8"))

        # checklist-{mode}.md review checklists
        checklist = styles_dir / f"checklist-{mode}.md"
        if checklist.exists():
            parts.append(checklist.read_text(encoding="utf-8"))

        return parts

    def list_available_roles(self) -> list[str]:
        """List all available role names."""
        roles_dir = self._base_dir / "roles"
        if not roles_dir.is_dir():
            return []
        return [f.stem for f in roles_dir.glob("*.md")]

    def list_available_modes(self) -> list[str]:
        """List all available mode names."""
        modes_dir = self._base_dir / "modes"
        if not modes_dir.is_dir():
            return []
        return [f.stem for f in modes_dir.glob("*.md")]

    def list_available_plugins(self) -> list[str]:
        """List all available plugin IDs."""
        plugins_dir = self._base_dir / "plugins"
        if not plugins_dir.is_dir():
            return []
        return [d.name for d in plugins_dir.iterdir() if d.is_dir()]
