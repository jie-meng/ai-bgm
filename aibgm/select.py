#!/usr/bin/env python3
"""
Select configuration command for AI BGM.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from aibgm.common import get_selection_file, load_builtin_config


def load_current_selection() -> Optional[str]:
    """Load the current selection from user config directory."""
    config_path = get_selection_file()
    if not config_path.exists():
        return None

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("selected")


def save_selection(selection: str) -> None:
    """Save the selected BGM configuration to user config directory."""
    config_path = get_selection_file()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({"selected": selection}, f)
    click.echo(f"Selected: {selection}")
    click.echo(f"Config saved to: {config_path}")


@click.command()
def select():
    """Interactively select BGM configuration."""
    config = load_builtin_config()
    options = list(config.keys())

    if not options:
        click.echo("Error: No available BGM configuration", err=True)
        sys.exit(1)

    # Load current selection
    current_selection = load_current_selection()

    click.echo("Please select BGM configuration:")
    for i, option in enumerate(options, 1):
        current_marker = " (current)" if option == current_selection else ""
        click.echo(f"{i}. {option}{current_marker}")

    try:
        default_index = (
            options.index(current_selection) + 1
            if current_selection in options
            else 1
        )
        user_input = (
            click.prompt(
                f"Enter option (1-{len(options)}, current {default_index})",
                default=str(default_index),
                show_default=False,
            )
            .strip()
        )
        if not user_input:
            if current_selection and current_selection in options:
                selection = current_selection
            else:
                selection = options[0]
        else:
            index = int(user_input) - 1
            if 0 <= index < len(options):
                selection = options[index]
            else:
                click.echo(
                    f"Error: Invalid option, please enter 1-{len(options)}",
                    err=True,
                )
                sys.exit(1)
    except ValueError:
        click.echo("Error: Please enter a valid number", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nCancelled")
        sys.exit(0)

    save_selection(selection)