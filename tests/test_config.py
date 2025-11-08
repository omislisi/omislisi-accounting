"""Tests for configuration module."""

import os
import tempfile
from pathlib import Path
import pytest
import yaml

from omislisi_accounting.config import load_config, get_reports_path


def test_load_config(tmp_path):
    """Test loading configuration from YAML file."""
    config_file = tmp_path / "config.yaml"
    config_data = {"reports_path": "/test/path"}

    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    config = load_config(config_file)
    assert config["reports_path"] == "/test/path"


def test_load_config_missing_file():
    """Test that missing config file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_config(Path("/nonexistent/path/config.yaml"))


def test_get_reports_path_from_env(monkeypatch):
    """Test that environment variable takes precedence."""
    monkeypatch.setenv("OMISLISI_REPORTS_PATH", "/env/path")
    path = get_reports_path()
    assert str(path) == "/env/path"


def test_get_reports_path_from_config(tmp_path, monkeypatch):
    """Test loading path from config file."""
    # Remove env var if set
    monkeypatch.delenv("OMISLISI_REPORTS_PATH", raising=False)

    config_file = tmp_path / "config.yaml"
    config_data = {"reports_path": "/config/path"}

    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    # Mock the load_config to use our test config
    import omislisi_accounting.config as config_module
    original_load = config_module.load_config

    def mock_load(path=None):
        if path is None:
            path = config_file
        return original_load(path)

    monkeypatch.setattr(config_module, "load_config", mock_load)

    path = get_reports_path()
    assert str(path) == "/config/path"

