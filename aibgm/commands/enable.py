#!/usr/bin/env python3
"""
Enable command for AI BGM.
"""

import click

from aibgm.utils.common import set_bgm_enable


@click.command()
def enable():
    """Enable AI BGM."""
    set_bgm_enable(True)
    click.echo("bgm: enabled")
