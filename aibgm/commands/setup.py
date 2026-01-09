#!/usr/bin/env python3
"""
Setup AI tool integration command for AI BGM.
"""

import json
import sys
from pathlib import Path

import click

from aibgm.commands.integrations.registry import IntegrationRegistry


def load_settings(path: Path) -> dict:
    """Load settings from the settings file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(path: Path, settings: dict) -> None:
    """Save settings to the settings file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


@click.command()
def setup():
    """Setup AI BGM integration with AI tools."""
    # Get all available integrations
    integrations = IntegrationRegistry.get_all_integrations()

    # Display menu
    click.echo("Select AI tool:")
    for i, integration in enumerate(integrations, 1):
        tool_id, tool_name = integration.get_tool_info()
        click.echo(f"{i}. {tool_name}")

    # Get user selection
    try:
        user_input = click.prompt("Enter option", type=str).strip()
        if not user_input:
            click.echo("Cancelled")
            sys.exit(0)

        index = int(user_input) - 1
        if 0 <= index < len(integrations):
            selected_integration = integrations[index]
        else:
            click.echo(
                f"Error: Invalid option, please enter 1-{len(integrations)}",
                err=True,
            )
            sys.exit(1)
    except ValueError:
        click.echo("Error: Please enter a valid number", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nCancelled")
        sys.exit(0)

    # Get settings path
    settings_path = selected_integration.get_settings_path()

    if not settings_path.exists():
        click.echo(f"Error: Settings file not found at {settings_path}", err=True)
        sys.exit(1)

    # Load existing settings
    settings = load_settings(settings_path)

    # Setup integration
    settings = selected_integration.setup_hooks(settings)

    # Save updated settings
    save_settings(settings_path, settings)

    tool_id, tool_name = selected_integration.get_tool_info()
    click.echo(f"Successfully configured AI BGM for {tool_name}")
    click.echo(f"Settings saved to: {settings_path}")
