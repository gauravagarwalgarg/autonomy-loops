"""Tests for the steering loader."""

import pytest

from autonomy_loops.config import Config, SteeringConfig
from autonomy_loops.steering.loader import SteeringLoader


@pytest.fixture
def steering_dir(tmp_path):
    """Create a temporary steering file structure."""
    roles = tmp_path / "roles"
    roles.mkdir()
    (roles / "developer.md").write_text("# Developer\nWrite code.")
    (roles / "tester.md").write_text("# Tester\nWrite tests.")

    modes = tmp_path / "modes"
    modes.mkdir()
    (modes / "code.md").write_text("# Code Mode\nFocus on implementation.")
    (modes / "test.md").write_text("# Test Mode\nFocus on testing.")

    plugins = tmp_path / "plugins"
    plugins.mkdir()
    fintech = plugins / "fintech"
    fintech.mkdir()
    (fintech / "standards.md").write_text("# FinTech Standards\nLatency matters.")

    styles = tmp_path / "styles"
    styles.mkdir()
    (styles / "common.md").write_text("# Team Rules\nBe nice.")
    (styles / "code.md").write_text("# Code Style\nUse black.")

    return tmp_path


class TestSteeringLoader:
    """Test steering file loading."""

    def test_loads_role(self, steering_dir):
        config = Config(steering=SteeringConfig(role="developer", styles_dir=None))
        loader = SteeringLoader(config, base_dir=steering_dir)
        parts = loader.load(role="developer")
        assert any("Developer" in p for p in parts)

    def test_loads_mode(self, steering_dir):
        config = Config(steering=SteeringConfig(mode="code", styles_dir=None))
        loader = SteeringLoader(config, base_dir=steering_dir)
        parts = loader.load(mode="code")
        assert any("Code Mode" in p for p in parts)

    def test_loads_plugin(self, steering_dir):
        config = Config(steering=SteeringConfig(plugins=["fintech"], styles_dir=None))
        loader = SteeringLoader(config, base_dir=steering_dir)
        parts = loader.load()
        assert any("FinTech" in p for p in parts)

    def test_loads_styles(self, steering_dir):
        styles_dir = steering_dir / "styles"
        config = Config(
            steering=SteeringConfig(
                mode="code",
                styles_dir=str(styles_dir),
            )
        )
        loader = SteeringLoader(config, base_dir=steering_dir)
        parts = loader.load(mode="code")
        assert any("Team Rules" in p for p in parts)
        assert any("Code Style" in p for p in parts)

    def test_missing_role_returns_none(self, steering_dir):
        config = Config(steering=SteeringConfig(role="nonexistent", styles_dir=None))
        loader = SteeringLoader(config, base_dir=steering_dir)
        parts = loader.load(role="nonexistent")
        # Should still work, just without role content
        assert isinstance(parts, list)

    def test_list_available_roles(self, steering_dir):
        config = Config()
        loader = SteeringLoader(config, base_dir=steering_dir)
        roles = loader.list_available_roles()
        assert "developer" in roles
        assert "tester" in roles

    def test_list_available_modes(self, steering_dir):
        config = Config()
        loader = SteeringLoader(config, base_dir=steering_dir)
        modes = loader.list_available_modes()
        assert "code" in modes
        assert "test" in modes
