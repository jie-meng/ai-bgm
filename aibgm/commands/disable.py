#!/usr/bin/env python3
"""
Disable command for AI BGM.
"""

import click

from aibgm.utils.common import set_bgm_enable


@click.command()
def disable():
    """Disable AI BGM."""
    set_bgm_enable(False)
    click.echo("bgm: disabled")
