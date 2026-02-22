"""
config.py - Configuration loader for the Medical Data Gateway.

Loads settings from config.yaml with sensible defaults so that no
path or tuning parameter is hard-coded inside a module.
"""

import os
import yaml
from typing import Any

# Resolve the config file relative to the repo root, not the CWD,
# so imports work regardless of where the script is launched from.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CONFIG_PATH = os.path.join(_REPO_ROOT, "config.yaml")

_DEFAULTS: dict[str, Any] = {
    "paths": {
        "input_folder": "data/raw",
        "output_folder": "data/processed",
        "reports_folder": "reports",
    },
    "anonymization": {
        "station_name": "REMOTE_MOBILE_01",
    },
    "pipeline": {
        "max_files": None,
        "retry": {
            "max_attempts": 5,
            "base_delay": 1.0,
            "max_delay": 30.0,
        },
    },
    "clustering": {
        "n_clusters": 3,
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge *override* into *base*, returning a new dict."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(config_path: str = _CONFIG_PATH) -> dict[str, Any]:
    """
    Load the YAML configuration file and merge it with built-in defaults.

    Parameters
    ----------
    config_path : str
        Path to config.yaml. Defaults to the repo-root config.yaml.

    Returns
    -------
    dict
        Merged configuration dictionary.
    """
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            user_config = yaml.safe_load(f) or {}
    else:
        user_config = {}

    return _deep_merge(_DEFAULTS, user_config)


# Module-level singleton so callers can just do `from src.config import CONFIG`
CONFIG = load_config()
