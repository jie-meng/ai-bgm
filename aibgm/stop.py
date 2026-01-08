#!/usr/bin/env python3
"""
Stop music command for AI BGM.
"""

import os
import signal
import sys
import time
import subprocess
from pathlib import Path

import click

from aibgm.common import get_pid_file


def kill_existing_player() -> bool:
    """
    Kill all existing BGM player processes.

    Returns:
        True if at least one process was killed, False otherwise.
    """
    killed_any = False
    pid_file = get_pid_file()

    # Kill all processes matching main.py
    try:
        # Use pgrep to find all main.py processes
        result = subprocess.run(
            ["pgrep", "-f", "main.py"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0 and result.stdout.strip():
            pids = [int(pid) for pid in result.stdout.strip().split("\n")]
            for pid in pids:
                try:
                    os.kill(pid, signal.SIGTERM)
                    killed_any = True
                except (ProcessLookupError, PermissionError):
                    pass

            # Wait a bit for processes to terminate
            time.sleep(0.5)

            # Force kill any remaining processes
            result = subprocess.run(
                ["pgrep", "-f", "main.py"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.stdout.strip():
                pids = [int(pid) for pid in result.stdout.strip().split("\n")]
                for pid in pids:
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        pass
    except (FileNotFoundError, subprocess.SubprocessError):
        # pgrep not available or failed, fallback to PID file method
        if not pid_file.exists():
            return False

        try:
            with open(pid_file, "r") as f:
                old_pid = int(f.read().strip())

            # Check if the process is still running
            try:
                os.kill(old_pid, 0)  # This just checks if process exists
            except ProcessLookupError:
                # Process doesn't exist, remove stale PID file
                pid_file.unlink()
                return False

            # Kill the existing process
            try:
                os.kill(old_pid, signal.SIGTERM)
                # Wait a bit for the process to terminate
                time.sleep(0.5)
                # Force kill if still running
                try:
                    os.kill(old_pid, 0)
                    os.kill(old_pid, signal.SIGKILL)
                    time.sleep(0.2)  # Give it time to be killed
                except ProcessLookupError:
                    pass

                killed_any = True
            except PermissionError:
                # Can't kill other user's process
                return False
        except (ValueError, IOError):
            return False

    # Clean up PID file
    if pid_file.exists():
        try:
            pid_file.unlink()
        except (FileNotFoundError, PermissionError):
            pass

    return killed_any


@click.command()
def stop():
    """Stop any playing music."""
    # Kill any existing BGM player process
    killed = kill_existing_player()
    if killed:
        click.echo("Stopped BGM player")
    else:
        click.echo("No BGM player is currently running")
