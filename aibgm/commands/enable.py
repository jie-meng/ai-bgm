#!/usr/bin/env python3
"""
Enable/Disable command for AI BGM.
"""

import json
from pathlib import Path

import click

from aibgm.utils.common import get_selection_file


def load_enable_state() -> bool:
    """
    Load the enable state from user config directory.

    Returns:
        True if enabled (default), False if disabled
    """
    config_path = get_selection_file()
    if not config_path.exists():
        return True

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("enable", True)
    except (json.JSONDecodeError, IOError):
        return True


def save_enable_state(enable: bool) -> None:
    """
    Save the enable state to user config directory.

    Args:
        enable: True to enable, False to disable
    """
    config_path = get_selection_file()

    # Load existing config or create new one
    data = {}
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Update enable state
    data["enable"] = enable

    # Save config
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


@click.command()
def enable():
    """Toggle AI BGM enable/disable state."""
    current_state = load_enable_state()
    new_state = not current_state

    save_enable_state(new_state)

    if new_state:
        click.echo("ai-bgm: enabled")
    else:
        click.echo("ai-bgm: disabled")
