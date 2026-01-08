#!/usr/bin/env python3
"""
AI BGM - AI CLI Background Music Player
A unified CLI tool for playing background music during AI-assisted work sessions.
"""

import click

from aibgm.commands.play import play
from aibgm.commands.stop import stop
from aibgm.commands.select import select
from aibgm.commands.setup import setup


@click.group()
def cli():
    """AI CLI Background Music Player - Plays work music in loop and done music when finished."""
    pass


# Add subcommands
cli.add_command(play)
cli.add_command(stop)
cli.add_command(select)
cli.add_command(setup)


if __name__ == "__main__":
    cli()