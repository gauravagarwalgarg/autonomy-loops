"""Tests for configuration loading."""

import os
import tempfile
from pathlib import Path

import pytest

from autonomy_loops.config import Config, ProviderConfig, _interpolate_env


class TestEnvInterpolation:
    """Test environment variable interpolation."""

    def test_interpolates_env_vars(self, monkeypatch):
        monkeypatch.setenv("MY_API_KEY", "sk-test-123")
        result = _interpolate_env("Bearer ${MY_API_KEY}")
        assert result == "Bearer sk-test-123"

    def test_missing_env_var_becomes_empty(self):
        result = _interpolate_env("${NONEXISTENT_VAR_12345}")
        assert result == ""

    def test_nested_dict_interpolation(self, monkeypatch):
        monkeypatch.setenv("DB_HOST", "localhost")
        data = {"connection": {"host": "${DB_HOST}", "port": 5432}}
        result = _interpolate_env(data)
        assert result == {"connection": {"host": "localhost", "port": 5432}}

    def test_list_interpolation(self, monkeypatch):
        monkeypatch.setenv("ITEM", "hello")
        data = ["${ITEM}", "world"]
        result = _interpolate_env(data)
        assert result == ["hello", "world"]

    def test_non_string_passthrough(self):
        assert _interpolate_env(42) == 42
        assert _interpolate_env(True) is True
        assert _interpolate_env(None) is None


class TestConfigLoad:
    """Test config file loading."""

    def test_default_config(self):
        config = Config()
        assert config.project.name == "unnamed"
        assert config.default_provider == "anthropic"
        assert config.policy.max_iterations == 50
        assert config.telemetry.enabled is True

    def test_load_from_yaml(self, tmp_path, monkeypatch):
        config_content = """
project:
  name: test-project
  languages: [python, go]

steering:
  mode: test
  role: tester
  plugins: [cloud-native]

providers:
  default: openai
  openai:
    api_key: test-key
    default_model: gpt-4o

policy:
  max_iterations: 25
  cost_limit_usd: 2.50
"""
        config_file = tmp_path / "autonomy-loops.yaml"
        config_file.write_text(config_content)

        config = Config.load(config_file)
        assert config.project.name == "test-project"
        assert config.project.languages == ["python", "go"]
        assert config.steering.mode == "test"
        assert config.steering.plugins == ["cloud-native"]
        assert config.default_provider == "openai"
        assert config.policy.max_iterations == 25

    def test_load_missing_file_returns_defaults(self):
        config = Config.load("/nonexistent/path/config.yaml")
        assert config.project.name == "unnamed"


class TestProviderConfig:
    """Test provider configuration."""

    def test_defaults(self):
        pc = ProviderConfig()
        assert pc.api_key == ""
        assert pc.max_retries == 3
        assert pc.timeout_seconds == 120
