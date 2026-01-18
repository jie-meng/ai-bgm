#!/usr/bin/env python3
"""
Stop music command for AI BGM.
"""

import os
import signal
import sys
import time
import fcntl
import subprocess
from pathlib import Path

import click

from aibgm.utils.common import get_pid_file, get_lock_file


def kill_existing_player() -> bool:
    """
    Kill all existing BGM player processes.

    Returns:
        True if at least one process was killed, False otherwise.
    """
    killed_any = False
    pid_file = get_pid_file()

    # Kill all processes matching ai-bgm play --daemon
    try:
        # Use pgrep to find all ai-bgm daemon processes
        result = subprocess.run(
            ["pgrep", "-f", "ai-bgm play --daemon"],
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

            # Wait longer for processes to terminate gracefully
            for _ in range(20):  # Wait up to 2 seconds
                time.sleep(0.1)
                result = subprocess.run(
                    ["pgrep", "-f", "ai-bgm play --daemon"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0 or not result.stdout.strip():
                    # All processes terminated
                    break
            else:
                # Force kill any remaining processes
                result = subprocess.run(
                    ["pgrep", "-f", "ai-bgm play --daemon"],
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
                    time.sleep(0.2)
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
                # Wait longer for the process to terminate gracefully
                for _ in range(20):  # Wait up to 2 seconds
                    time.sleep(0.1)
                    try:
                        os.kill(old_pid, 0)
                    except ProcessLookupError:
                        # Process terminated
                        break
                else:
                    # Force kill if still running after 2 seconds
                    try:
                        os.kill(old_pid, signal.SIGKILL)
                        time.sleep(0.2)
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
    # Use file lock to prevent race with concurrent start
    lock_file = get_lock_file()
    lock_fd = None

    try:
        lock_fd = os.open(str(lock_file), os.O_CREAT | os.O_RDWR, 0o644)
        # Try to acquire exclusive lock (will block if another process holds it)
        fcntl.flock(lock_fd, fcntl.LOCK_EX)

        # Kill any existing BGM player process
        killed = kill_existing_player()
        if killed:
            click.echo("Stopped BGM player")
        else:
            click.echo("No BGM player is currently running")
    finally:
        # Release lock
        if lock_fd is not None:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)
