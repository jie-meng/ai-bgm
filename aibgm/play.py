#!/usr/bin/env python3
"""
Play music command for AI BGM.
"""

import os
import signal
import sys
import time
import platform
import subprocess
import random
from pathlib import Path

import click
import pygame

from aibgm.common import (
    get_assets_path,
    get_pid_file,
    load_selection,
    load_builtin_config,
    save_pid,
    cleanup_pid,
)


def kill_existing_process() -> bool:
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
            except ProcessLookupError:
                pass
            pid_file.unlink()
            return True
        except PermissionError:
            # Can't kill other user's process
            return False
    except (ValueError, IOError):
        return False


def play_music(selection: str, music_type: str, assets_path: Path, repeat: int = 1) -> None:
    """
    Play music based on selection and type.

    Args:
        selection: The selected configuration name (e.g., 'default', 'maou')
        music_type: Either 'work', 'end', or 'notification'
        assets_path: Path to the assets/sounds directory
        repeat: Number of times to play. -1 for infinite loop, 0 to skip.
    """
    config = load_builtin_config()

    if selection not in config:
        click.echo(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error: Configuration '{selection}' not found in config.json",
            err=True,
        )
        cleanup_pid()
        sys.exit(1)

    if music_type not in config[selection]:
        click.echo(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error: Music type '{music_type}' not found in configuration '{selection}'",
            err=True,
        )
        cleanup_pid()
        sys.exit(1)

    files = config[selection][music_type]

    if not files:
        # No files configured, do nothing
        cleanup_pid()
        return

    if repeat == 0:
        # Skip playback
        cleanup_pid()
        return

    # Randomly select one file
    selected_file = random.choice(files)

    # Build the full path
    full_path = assets_path / selection / selected_file

    if not full_path.exists():
        click.echo(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error: File not found: {full_path}",
            err=True,
        )
        click.echo(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Please ensure the file exists in: {assets_path / selection}",
            err=True,
        )
        cleanup_pid()
        sys.exit(1)

    click.echo(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Playing: {selected_file}")

    # Initialize pygame mixer
    try:
        pygame.mixer.init()
    except pygame.error as e:
        click.echo(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error initializing audio: {e}",
            err=True,
        )
        cleanup_pid()
        sys.exit(1)

    try:
        # Load the music file
        pygame.mixer.music.load(str(full_path))

        # Play the music
        if repeat == -1:
            # Infinite loop: -1 means loop forever in pygame
            pygame.mixer.music.play(loops=-1)
        else:
            # Play specified number of times (loops parameter is count-1)
            pygame.mixer.music.play(loops=repeat - 1)

        # Keep the script running while music plays
        while pygame.mixer.music.get_busy():
            # Check every 0.1 seconds
            time.sleep(0.1)

    except KeyboardInterrupt:
        click.echo(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Playback stopped by user")
    except pygame.error as e:
        click.echo(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error playing audio: {e}",
            err=True,
        )
    finally:
        # Stop the music and cleanup
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        cleanup_pid()


def start_background_player(music_type: str, count: int) -> None:
    """
    Start the BGM player in the background as a daemon process.

    Args:
        music_type: Either 'work', 'end', or 'notification'
        count: Number of times to play. -1 for infinite loop, 0 to skip.
    """
    # Kill any existing BGM player process first
    killed = kill_existing_process()

    # Use subprocess to start a detached background process
    # Get the Python executable
    python_exe = sys.executable

    # Get the current script path (main.py)
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))

    # Prepare arguments for the background process
    args = [python_exe, script_path, "play", "--daemon", music_type, str(count)]

    # Start the background process
    if platform.system() == "Windows":
        # On Windows, use CREATE_NO_WINDOW flag
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen(
            args,
            creationflags=DETACHED_PROCESS,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
    else:
        # On Unix-like systems
        subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True,
        )

    if killed:
        click.echo("Stopped previous BGM player")
    click.echo("BGM player started in background")

    # Give it a moment to start
    time.sleep(0.5)

    # Try to read the PID if it was saved
    pid_file = get_pid_file()
    if pid_file.exists():
        try:
            with open(pid_file, "r") as f:
                pid = f.read().strip()
                click.echo(f"Background player PID: {pid}")
        except Exception:
            pass


def run_player_daemon(music_type: str, count: int) -> None:
    """
    Run the player daemon (called with --daemon flag).

    Args:
        music_type: Either 'work', 'end', or 'notification'
        count: Number of times to play. -1 for infinite loop, 0 to skip.
    """
    # Redirect standard file descriptors to log file
    sys.stdout.flush()
    sys.stderr.flush()

    # Get log file path
    config_dir = Path.home() / ".config" / "ai-bgm"
    config_dir.mkdir(parents=True, exist_ok=True)
    log_file = config_dir / "bgm_player.log"

    # Redirect stdout and stderr to log file
    log_fd = os.open(str(log_file), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    os.dup2(log_fd, sys.stdout.fileno())
    os.dup2(log_fd, sys.stderr.fileno())
    os.close(log_fd)

    # Register cleanup handler
    def signal_handler(signum, frame):
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Received termination signal, stopping...")
        cleanup_pid()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Save current PID
    save_pid()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] BGM player daemon started (PID: {os.getpid()})")

    # Load the selected configuration
    selection = load_selection()

    # Get the assets path
    assets_path = get_assets_path()

    if not assets_path.exists():
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error: Assets directory not found: {assets_path}")
        cleanup_pid()
        sys.exit(1)

    # Play the music
    play_music(selection, music_type, assets_path, count)


@click.command()
@click.argument("music_type", type=click.Choice(["work", "end", "notification"]))
@click.argument("count", type=int, default=1, required=False)
@click.option("--daemon", is_flag=True, hidden=True, help="Run as daemon process (internal use only)")
def play(music_type: str, count: int, daemon: bool):
    """Play music based on saved configuration.

    MUSIC_TYPE: Type of music to play: 'work', 'end', or 'notification'
    COUNT: Number of times to play. -1 for infinite loop, 0 to skip. (default: 1)
    """
    if daemon:
        # Running as daemon
        run_player_daemon(music_type, count)
    else:
        # Start the player in background
        start_background_player(music_type, count)
