#!/usr/bin/env python3
"""
AI BGM Stop Module
Stops the currently playing music.
"""

import os
import sys
import signal
import time
from pathlib import Path


def get_pid_file() -> Path:
    """Get the path to the PID file."""
    config_dir = Path.home() / ".config" / "ai-bgm"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "bgm_player.pid"


def kill_existing_player() -> bool:
    """
    Kill any existing BGM player process.

    Returns:
        True if a process was killed, False otherwise.
    """
    pid_file = get_pid_file()

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
            
            # Clean up PID file
            if pid_file.exists():
                pid_file.unlink()
            return True
        except PermissionError:
            # Can't kill other user's process
            return False
    except (ValueError, IOError):
        return False


class BGMStopper:
    """Handles stopping work music and playing end music."""

    def __init__(self):
        """Initialize the BGM stopper."""
        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def stop_music(self) -> None:
        """
        Stop any playing music.
        """
        # Kill any existing BGM player process
        killed = kill_existing_player()
        if killed:
            print("Stopped BGM player")
        else:
            print("No BGM player is currently running")

    def _signal_handler(self, signum, frame):
        """Handle termination signals gracefully."""
        print("\nReceived termination signal, stopping playback...")
        sys.exit(0)


def main():
    """Main entry point for the ai-bgm-stop script."""
    # Create stopper and stop music
    stopper = BGMStopper()
    stopper.stop_music()


if __name__ == "__main__":
    main()
