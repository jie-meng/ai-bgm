#!/usr/bin/env python3
"""
Common functions for AI BGM.
"""

import json
import os
import sys
from pathlib import Path


def get_assets_path() -> Path:
    """
    Get the assets path.

    If installed via pip, use the package installation directory.
    If running directly, use the current directory.

    Returns:
        Path to the assets/sounds directory
    """
    # Try to get the package installation directory
    try:
        import importlib.resources as resources
        # For Python 3.9+
        pkg_path = resources.files("aibgm")
        assets_path = pkg_path / "assets" / "sounds"
        if assets_path.exists():
            return assets_path
    except (ImportError, AttributeError):
        pass

    # Fallback: use the directory where this script is located
    script_dir = Path(__file__).parent
    assets_path = script_dir / "assets" / "sounds"

    # If that doesn't exist, try current directory
    if not assets_path.exists():
        assets_path = Path.cwd() / "assets" / "sounds"

    return assets_path


def get_pid_file() -> Path:
    """Get the path to the PID file."""
    config_dir = Path.home() / ".config" / "ai-bgm"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "bgm_player.pid"


def get_selection_file() -> Path:
    """Get the path to the selection file."""
    config_dir = Path.home() / ".config" / "ai-bgm"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "selection.json"


def load_selection() -> str:
    """
    Load the selected BGM configuration from user config directory.

    Returns:
        The selected configuration name (e.g., 'default', 'maou')
    """
    config_path = get_selection_file()

    if not config_path.exists():
        # No configuration found, use default
        return "default"

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("selected", "default")


def load_builtin_config() -> dict:
    """
    Load the built-in config.json from the package, merged with config_ext.json if exists.

    Returns:
        Dictionary containing all BGM configurations
    """
    # Try to get the package installation directory first
    config_file = None
    try:
        import importlib.resources as resources
        # For Python 3.9+
        pkg_path = resources.files("aibgm")
        config_file = pkg_path / "config.json"
        if not config_file.exists():
            config_file = None
    except (ImportError, AttributeError):
        pass

    # Fallback: use the parent directory of this script (aibgm/)
    if config_file is None:
        script_dir = Path(__file__).parent.parent  # Go up from utils/ to aibgm/
        config_file = script_dir / "config.json"

    if not config_file.exists():
        print(f"Error: Config file not found at {config_file}")
        sys.exit(1)

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Load config_ext.json from the same directory if exists
    config_ext_file = config_file.parent / "config_ext.json"
    if config_ext_file.exists():
        with open(config_ext_file, "r", encoding="utf-8") as f:
            ext_config = json.load(f)
            # Merge: ext config overrides built-in config for same keys
            config.update(ext_config)

    return config


def save_pid() -> None:
    """Save the current process PID to the PID file."""
    pid_file = get_pid_file()
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))


def cleanup_pid() -> None:
    """Remove the PID file."""
    pid_file = get_pid_file()
    if pid_file.exists():
        pid_file.unlink()