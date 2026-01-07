#!/usr/bin/env python3
"""
AI BGM Play Module
Plays music based on saved configuration and type (work or end).
"""

import json
import os
import signal
import sys
import random
import time
import platform
import subprocess
from pathlib import Path
import pygame


def get_assets_path() -> Path:
    """
    Get the assets path.

    If installed via pip, use the package installation directory.
    If running directly, use the current directory.

    Returns:
        Path to the assets/sounds directory
    """
    # Try to get the package installation directory
    try:
        import importlib.resources as resources
        # For Python 3.9+
        pkg_path = resources.files("aibgm")
        assets_path = pkg_path / "assets" / "sounds"
        if assets_path.exists():
            return assets_path
    except (ImportError, AttributeError):
        pass

    # Fallback: use the directory where this script is located
    script_dir = Path(__file__).parent
    assets_path = script_dir / "assets" / "sounds"

    # If that doesn't exist, try current directory
    if not assets_path.exists():
        assets_path = Path.cwd() / "assets" / "sounds"

    return assets_path


def get_pid_file() -> Path:
    """Get the path to the PID file."""
    config_dir = Path.home() / ".config" / "ai-bgm"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "bgm_player.pid"


def load_selection() -> str:
    """
    Load the selected BGM configuration from user config directory.

    Returns:
        The selected configuration name (e.g., 'default', 'maou')
    """
    config_path = Path.home() / ".config" / "ai-bgm" / "selection.json"

    if not config_path.exists():
        # No configuration found, use default
        return "default"

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("selected", "default")


def load_builtin_config() -> dict:
    """
    Load the built-in config.json from the package, merged with config_ext.json if exists.

    Returns:
        Dictionary containing all BGM configurations
    """
    script_dir = Path(__file__).parent
    config_file = script_dir / "config.json"

    if not config_file.exists():
        print(f"Error: Config file not found at {config_file}")
        sys.exit(1)

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Load config_ext.json from the same directory if exists
    config_ext_file = script_dir / "config_ext.json"
    if config_ext_file.exists():
        with open(config_ext_file, "r", encoding="utf-8") as f:
            ext_config = json.load(f)
            # Merge: ext config overrides built-in config for same keys
            config.update(ext_config)

    return config


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
            import time
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


def save_pid() -> None:
    """Save the current process PID to the PID file."""
    pid_file = get_pid_file()
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))


def cleanup_pid() -> None:
    """Remove the PID file."""
    pid_file = get_pid_file()
    if pid_file.exists():
        pid_file.unlink()


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
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error: Configuration '{selection}' not found in config.json")
        cleanup_pid()
        sys.exit(1)

    if music_type not in config[selection]:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error: Music type '{music_type}' not found in configuration '{selection}'")
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
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error: File not found: {full_path}")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Please ensure the file exists in: {assets_path / selection}")
        cleanup_pid()
        sys.exit(1)

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Playing: {selected_file}")

    # Initialize pygame mixer
    try:
        pygame.mixer.init()
    except pygame.error as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error initializing audio: {e}")
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
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Playback stopped by user")
    except pygame.error as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error playing audio: {e}")
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
    
    # Get the current script path
    script_path = os.path.abspath(__file__)
    
    # Prepare arguments for the background process
    args = [python_exe, script_path, "--daemon", music_type, str(count)]
    
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
            close_fds=True
        )
    else:
        # On Unix-like systems
        subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True
        )
    
    if killed:
        print("Stopped previous BGM player")
    print("BGM player started in background")
    
    # Give it a moment to start
    time.sleep(0.5)
    
    # Try to read the PID if it was saved
    pid_file = get_pid_file()
    if pid_file.exists():
        try:
            with open(pid_file, "r") as f:
                pid = f.read().strip()
                print(f"Background player PID: {pid}")
        except:
            pass


def _run_player_daemon(music_type: str, count: int) -> None:
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


def main():
    """Main entry point for the ai-bgm-play script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Play music based on saved configuration"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process (internal use only)"
    )
    parser.add_argument(
        "type",
        choices=["work", "end", "notification"],
        help="Type of music to play: 'work', 'end', or 'notification'"
    )
    parser.add_argument(
        "count",
        type=int,
        nargs="?",
        default=1,
        help="Number of times to play. -1 for infinite loop, 0 to skip. (default: 1)"
    )

    args = parser.parse_args()

    if args.daemon:
        # Running as daemon
        _run_player_daemon(args.type, args.count)
    else:
        # Start the player in background
        start_background_player(args.type, args.count)


if __name__ == "__main__":
    main()
