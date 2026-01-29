#!/usr/bin/env python3
"""
Setup AI tool integration command for AI BGM.
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple

import click

from aibgm.commands.integrations import AIToolIntegration
from aibgm.commands.integrations.registry import IntegrationRegistry
from aibgm.utils.colors import BOLD, GREEN, RED, YELLOW, color_text


def load_settings(path: Path) -> dict:
    """Load settings from the settings file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(path: Path, settings: dict) -> None:
    """Save settings to the settings file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def check_tool_installed(integration: AIToolIntegration) -> bool:
    """Check if an AI tool is installed by verifying its config directory exists."""
    settings_path = integration.get_settings_path()
    return settings_path.parent.exists()


def setup_integration(integration: AIToolIntegration) -> Tuple[bool, str]:
    """
    Setup a single integration.

    Returns:
        Tuple of (success: bool, message: str)
    """
    settings_path = integration.get_settings_path()
    tool_id, tool_name = integration.get_tool_info()

    # Check if parent directory exists
    config_dir = settings_path.parent
    if not config_dir.exists():
        return (False, f"{tool_name}: Config directory not found ({config_dir})")

    # Load existing settings or create new if file doesn't exist
    if settings_path.exists():
        settings = load_settings(settings_path)
    else:
        settings = {}

    # Setup integration
    settings = integration.setup_hooks(settings)

    # Save updated settings
    save_settings(settings_path, settings)

    return (True, f"{tool_name}: Configured successfully [OK]")


@click.command()
def setup():
    """Setup AI BGM integration with AI tools."""
    # Get all available integrations
    integrations = IntegrationRegistry.get_all_integrations()

    # Check which tools are installed
    installed_tools: List[AIToolIntegration] = []
    not_installed_tools: List[Tuple[AIToolIntegration, str]] = []

    for integration in integrations:
        if check_tool_installed(integration):
            installed_tools.append(integration)
        else:
            tool_id, tool_name = integration.get_tool_info()
            not_installed_tools.append((integration, tool_name))

    # Display menu
    click.echo(color_text("Select AI tool:", BOLD))
    for i, integration in enumerate(integrations, 1):
        tool_id, tool_name = integration.get_tool_info()
        if check_tool_installed(integration):
            status = color_text("[Installed - can setup]", GREEN)
        else:
            status = color_text("[Not Installed]", RED)
        click.echo(f"{i}. {tool_name} {status}")
    click.echo(f"0. {color_text('All (auto-detect installed tools)', BOLD)}")

    # Get user selection
    try:
        user_input = click.prompt("\nEnter option", type=str).strip()
        if not user_input:
            click.echo("Cancelled")
            sys.exit(0)

        option = int(user_input)

        if option == 0:
            # All: Auto-detect and setup installed tools
            if not installed_tools:
                click.echo(color_text("\nNo installed AI tools detected", RED))
                click.echo("Please install and run one of the following tools first:")
                for _, tool_name in not_installed_tools:
                    click.echo(f"  - {tool_name}")
                sys.exit(0)

            click.echo(
                color_text(
                    f"\nDetected {len(installed_tools)} installed tools, starting setup...", YELLOW
                )
            )
            click.echo("-" * 50)

            success_count = 0
            fail_count = 0

            for integration in installed_tools:
                success, message = setup_integration(integration)
                if success:
                    success_count += 1
                    click.echo(color_text(message, GREEN))
                else:
                    fail_count += 1
                    click.echo(color_text(message, RED))

            click.echo("-" * 50)
            click.echo(color_text(f"Success: {success_count}, Failed: {fail_count}", BOLD))

            if not_installed_tools:
                click.echo()
                click.echo(color_text("Tools not detected (not installed):", YELLOW))
                for _, tool_name in not_installed_tools:
                    click.echo(f"  - {tool_name}")

            click.echo()
            click.echo(color_text("[OK] AI BGM setup complete!", GREEN))

        elif 1 <= option <= len(integrations):
            selected_integration = integrations[option - 1]
            tool_id, tool_name = selected_integration.get_tool_info()

            if not check_tool_installed(selected_integration):
                click.echo(color_text(f"\n{tool_name} is not installed", RED))
                click.echo(
                    f"Please install and run {tool_name} first. Config directory: {selected_integration.get_settings_path().parent}"
                )
                sys.exit(1)

            success, message = setup_integration(selected_integration)
            click.echo()
            if success:
                click.echo(color_text(f"[OK] {message}", GREEN))
            else:
                click.echo(color_text(f"[FAIL] {message}", RED))
            click.echo()

        else:
            click.echo(
                color_text(f"Error: Invalid option, please enter 0-{len(integrations)}", RED),
                err=True,
            )
            sys.exit(1)

    except ValueError:
        click.echo(color_text("Error: Please enter a valid number", RED), err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nCancelled")
        sys.exit(0)
