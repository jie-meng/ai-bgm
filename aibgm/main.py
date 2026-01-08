#!/usr/bin/env python3
"""
AI BGM - AI CLI Background Music Player
A unified CLI tool for playing background music during AI-assisted work sessions.
"""

import click

from aibgm.play import play
from aibgm.stop import stop
from aibgm.select import select
from aibgm.setup import setup


@click.group()
def cli():
    """AI CLI Background Music Player - Plays work music in loop and end music when done."""
    pass


# Add subcommands
cli.add_command(play)
cli.add_command(stop)
cli.add_command(select)
cli.add_command(setup)


if __name__ == "__main__":
    cli()