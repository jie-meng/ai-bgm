# Tests

This directory contains tests for AI BGM, focusing on cross-platform compatibility.

## Running Tests

### Windows Compatibility Test

Tests configuration paths, signal handling, and fcntl availability:

```bash
python tests/test_windows_compat.py
```

This test verifies:
- ✅ Configuration directories use correct paths for each platform
  - Linux/macOS: `~/.config/ai-bgm/`
  - Windows: `%APPDATA%\ai-bgm\`
- ✅ Signal availability (SIGINT, SIGTERM, SIGKILL, CTRL_BREAK_EVENT)
- ✅ fcntl module availability (Unix only)

### Expected Output

On **macOS/Linux**:
```
Platform: Darwin / Linux
✓ Configuration paths test passed!
✓ Unix signal support verified
✓ fcntl available on Unix-like system
✓ ALL TESTS PASSED!
```

On **Windows**:
```
Platform: Windows
✓ Configuration paths test passed!
✓ Windows signal support verified
✓ fcntl correctly unavailable on Windows
✓ ALL TESTS PASSED!
```

## Test Coverage

Currently focused on:
- Cross-platform file system paths
- Signal handling compatibility
- Platform-specific module availability

## Adding New Tests

When adding new tests:
1. Create test file in `tests/` directory
2. Follow naming convention: `test_*.py`
3. Ensure tests are excluded from package installation (see `pyproject.toml`)
