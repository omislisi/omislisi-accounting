"""Configuration settings for the application."""

import os
from pathlib import Path
import yaml


def load_config(config_path: Path = None) -> dict:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file. If None, looks for config.yaml in project root.

    Returns:
        Dictionary with configuration values
    """
    if config_path is None:
        # Find project root (where config.yaml should be)
        project_root = Path(__file__).parent.parent
        config_path = project_root / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            f"Please create config.yaml based on config.yaml.example"
        )

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return config


def get_reports_path() -> Path:
    """
    Get the reports path from configuration.

    Priority:
    1. Environment variable OMISLISI_REPORTS_PATH
    2. config.yaml file
    3. Default fallback (for backwards compatibility)

    Returns:
        Path to reports directory
    """
    # Check environment variable first
    env_path = os.getenv("OMISLISI_REPORTS_PATH")
    if env_path:
        return Path(env_path)

    # Load from config file
    try:
        config = load_config()
        reports_path = config.get("reports_path")
        if reports_path:
            return Path(reports_path)
    except FileNotFoundError:
        # Fallback to default if config file doesn't exist
        pass

    # Default fallback (shouldn't normally be reached)
    return Path.home() / "Documents" / "reports"


# Load configuration
try:
    _config = load_config()
    REPORTS_PATH = Path(_config.get("reports_path", get_reports_path()))
except FileNotFoundError:
    # Use environment variable or default if config file doesn't exist
    REPORTS_PATH = get_reports_path()

