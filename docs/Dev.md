# Development Guide

## Development Environment Setup

### 1. Clone and Install

```bash
git clone <repo-url>
cd ai-bgm

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### 2. Code Quality Tools

Installs with `.[dev]`:
- **Black** - Code formatting
- **Flake8** - Linting
- **MyPy** - Type checking
- **Pytest** - Testing (placeholder)

### 3. Commands

```bash
# Format code
black aibgm/

# Lint
flake8 aibgm/

# Type check
mypy aibgm/

# All checks
black aibgm/ && flake8 aibgm/ && mypy aibgm/
```

## Technical Design

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      CLI Layer                          │
│  ai-bgm-play / ai-bgm-stop / ai-bgm-select / ai-bgm-setup │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                     Core Modules                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ai_bgm_play.py│  │ai_bgm_stop.py│  │ai_bgm_select.py│ │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Configuration                         │
│              config.json + selection.json               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Audio Output                          │
│                     pygame.mixer                        │
└─────────────────────────────────────────────────────────┘
```

### Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `ai_bgm_play.py` | Music playback, daemon mode, PID management |
| `ai_bgm_stop.py` | Kill playing process |
| `ai_bgm_select.py` | Interactive configuration selection |
| `ai_bgm_setup.py` | AI tool hooks integration |

### Configuration System

**config.json** (built-in):
```json
{
  "maou": {
    "work": ["castle.mp3", "boss.mp3"],
    "end": ["congratulations.mp3"]
  }
}
```

**selection.json** (user-specific):
```json
{"selected": "maou"}
```

Location: `~/.config/ai-bgm/`

### Key Design Patterns

1. **Daemon Mode**: Player runs detached with PID tracking at `~/.config/ai-bgm/bgm_player.pid`
2. **Log Output**: Daemon logs to `~/.config/ai-bgm/bgm_player.log`
3. **Signal Handling**: Graceful shutdown on SIGTERM/SIGINT
4. **Cross-Platform**: Uses `platform.system()` for Windows/Unix differences

### Dependency Graph

```
pygame>=2.6.1
```

Python stdlib:
- `argparse` - CLI
- `pathlib` - Path handling
- `signal` - Process signals
- `subprocess` - Daemon spawning
- `json` - Configuration

## Adding New Features

### Add New AI Tool Integration

1. Update `get_ai_tools()` in `ai_bgm_setup.py`:

```python
def get_ai_tools():
    return [
        ("iflow", "iFlow CLI"),
        ("newtool", "New Tool Name"),  # Add here
    ]
```

2. Implement setup function:

```python
def setup_newtool(settings: dict) -> dict:
    # Configure hooks
    settings["hooks"] = {...}
    return settings
```

3. Call in `main()`:

```python
if tool_id == "newtool":
    settings = setup_newtool(settings)
```

### Add New Music Configuration

1. Create directory: `aibgm/assets/sounds/<name>/`
2. Add audio files
3. Update `aibgm/config.json`

### Add CLI Option

In `ai_bgm_play.py` `main()`:

```python
parser.add_argument("--new-option", action="store_true")
# Then use: args.new_option
```

## Testing

### Manual Testing Checklist

- [ ] `ai-bgm-play work -1` loops correctly
- [ ] `ai-bgm-play end` plays once
- [ ] `ai-bgm-stop` kills player
- [ ] `ai-bgm-select` updates selection
- [ ] `ai-bgm-setup` creates valid hooks
- [ ] New config appears in selection
- [ ] Audio files play without error

### Debug Commands

```bash
# Check daemon status
ps aux | grep ai-bgm

# View logs
tail -f ~/.config/ai-bgm/bgm_player.log

# Check PID file
cat ~/.config/ai-bgm/bgm_player.pid

# Test pygame directly
python -c "import pygame; pygame.mixer.init(); print('OK')"
```

## Distribution

### Build

```bash
# Wheel
pip wheel .

# Source
python -m build
```

### Version Bump

Update `version` in `pyproject.toml`:

```toml
[project]
version = "0.2.0"
```

## Code Style

- **Black** line length: 100
- **Python**: 3.9+
- **Type hints**: Required for public functions
- **Docstrings**: For classes and public methods

See [AGENTS.md](../AGENTS.md) for AI agent guidelines.
