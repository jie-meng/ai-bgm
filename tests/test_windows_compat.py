#!/usr/bin/env python3
"""
Test script to verify Windows compatibility.
Run this on different platforms to check paths and signal handling.
"""

import signal
from pathlib import Path
from aibgm.utils.common import get_config_dir, get_pid_file, get_log_file, get_selection_file
from aibgm.utils.platform_utils import is_windows, is_unix, get_platform_name


def test_config_paths():
    """Test cross-platform configuration paths."""
    print("=" * 60)
    print("AI BGM - Cross-Platform Configuration Paths Test")
    print("=" * 60)
    print(f"\nPlatform: {get_platform_name()}")
    import platform
    print(f"Python Version: {platform.python_version()}")
    print(f"Home Directory: {Path.home()}")
    
    print("\n" + "-" * 60)
    print("Configuration Paths:")
    print("-" * 60)
    
    config_dir = get_config_dir()
    print(f"Config Directory: {config_dir}")
    print(f"  - Exists: {config_dir.exists()}")
    
    pid_file = get_pid_file()
    print(f"\nPID File: {pid_file}")
    print(f"  - Parent exists: {pid_file.parent.exists()}")
    
    log_file = get_log_file()
    print(f"\nLog File: {log_file}")
    print(f"  - Parent exists: {log_file.parent.exists()}")
    
    selection_file = get_selection_file()
    print(f"\nSelection File: {selection_file}")
    print(f"  - Parent exists: {selection_file.parent.exists()}")
    
    print("\n" + "-" * 60)
    print("Expected Paths by Platform:")
    print("-" * 60)
    
    if is_windows():
        import os
        appdata = os.getenv("APPDATA", "C:\\Users\\<user>\\AppData\\Roaming")
        expected = f"{appdata}\\ai-bgm\\"
        print(f"Windows: {expected}")
        # Verify the path is correct
        assert str(config_dir).endswith("ai-bgm"), f"Config dir should end with 'ai-bgm': {config_dir}"
        assert "AppData" in str(config_dir) or str(config_dir).endswith("ai-bgm"), \
            f"Windows config should use AppData or fallback: {config_dir}"
    else:
        expected = "~/.config/ai-bgm/"
        print(f"Unix (macOS/Linux): {expected}")
        assert ".config" in str(config_dir), f"Unix should use .config: {config_dir}"
    
    print("\n✓ Configuration paths test passed!")


def test_signal_availability():
    """Test signal availability on different platforms."""
    print("\n" + "=" * 60)
    print("Signal Availability Test")
    print("=" * 60)
    
    signals_to_check = [
        ("SIGINT", signal.SIGINT, "Universal - Ctrl+C"),
        ("SIGTERM", getattr(signal, "SIGTERM", None), "Terminate signal"),
        ("SIGKILL", getattr(signal, "SIGKILL", None), "Force kill (Unix only)"),
        ("CTRL_BREAK_EVENT", getattr(signal, "CTRL_BREAK_EVENT", None), "Windows Ctrl+Break"),
    ]
    
    print(f"\nPlatform: {get_platform_name()}")
    print("-" * 60)
    
    for name, sig, description in signals_to_check:
        if sig is not None:
            print(f"✓ {name:20} Available  - {description}")
        else:
            print(f"✗ {name:20} Not Available - {description}")
    
    # Verify expected signals for each platform
    if is_windows():
        assert hasattr(signal, "SIGINT"), "Windows should have SIGINT"
        assert hasattr(signal, "SIGTERM"), "Windows should have SIGTERM"
        print("\n✓ Windows signal support verified")
    else:
        assert hasattr(signal, "SIGINT"), "Unix should have SIGINT"
        assert hasattr(signal, "SIGTERM"), "Unix should have SIGTERM"
        assert hasattr(signal, "SIGKILL"), "Unix should have SIGKILL"
        print("\n✓ Unix signal support verified")


def test_fcntl_availability():
    """Test fcntl module availability."""
    print("\n" + "=" * 60)
    print("fcntl Module Availability Test")
    print("=" * 60)
    
    print(f"\nPlatform: {get_platform_name()}")
    
    if is_windows():
        try:
            import fcntl
            print("✗ UNEXPECTED: fcntl should NOT be available on Windows")
            assert False, "fcntl should not be available on Windows"
        except ImportError:
            print("✓ fcntl correctly unavailable on Windows")
    else:
        try:
            import fcntl
            print("✓ fcntl available on Unix-like system")
        except ImportError:
            print("✗ UNEXPECTED: fcntl should be available on Unix")
            assert False, "fcntl should be available on Unix"


def main():
    """Run all compatibility tests."""
    try:
        test_config_paths()
        test_signal_availability()
        test_fcntl_availability()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    exit(main())
