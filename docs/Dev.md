# Development Guide

## Development Environment Setup

### 1. Clone and Install

```bash
git clone <repo-url>
cd ai-bgm

# Install in editable mode
pip install -e .
```

### 2. Code Quality Tools

Recommended tools:
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
│           ai-bgm (play/stop/select/setup)               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                     Core Module                         │
│                    cli.py (Click)                       │
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
| `cli.py` | Unified CLI with subcommands for play/stop/select/setup/enable |
| `main.py` | Local development entry point (not packaged) |
| `commands/` | Individual command implementations |
| `utils/common.py` | Configuration, PID, and path management |
| `utils/logger.py` | Log management with automatic rotation |

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

1. **Click CLI**: Uses Click 8.3.1 for unified command structure
2. **Daemon Mode**: Player runs detached with PID tracking at `~/.config/ai-bgm/bgm_player.pid`
3. **Log Management**: Automatic log rotation
   - Max 1000 lines before rotation
   - Keeps 500 most recent lines
   - Logs to `~/.config/ai-bgm/bgm_player.log`
4. **Signal Handling**: Graceful shutdown on SIGTERM/SIGINT
5. **Cross-Platform**: Uses `platform.system()` for Windows/Unix differences

### Dependency Graph

```
pygame>=2.6.1
click>=8.3.1
```

Python stdlib:
- `pathlib` - Path handling
- `signal` - Process signals
- `subprocess` - Daemon spawning
- `json` - Configuration

## Adding New Features

### Add New AI Tool Integration

Adding a new AI tool integration is now streamlined with the modular integration system.

#### Step 1: Create Integration File

Create a new file in `aibgm/commands/integrations/<toolname>.py`:

```python
#!/usr/bin/env python3
"""
New Tool integration for AI BGM.
"""

from pathlib import Path
from typing import Tuple

from aibgm.commands.integrations import AIToolIntegration


class NewToolIntegration(AIToolIntegration):
    """Integration for New Tool."""

    def get_tool_info(self) -> Tuple[str, str]:
        """Get tool information."""
        return ("newtool", "New Tool Name")

    def get_settings_path(self) -> Path:
        """Get settings path."""
        return Path.home() / ".newtool" / "settings.json"

    def setup_hooks(self, settings: dict) -> dict:
        """
        Setup hooks for New Tool.

        Args:
            settings: Existing settings dictionary

        Returns:
            Updated settings dictionary
        """
        hooks_config = {
            "UserPromptSubmit": [
                {"hooks": [{"type": "command", "command": "ai-bgm play work 0"}]}
            ],
            "Stop": [{"hooks": [{"type": "command", "command": "ai-bgm play done"}]}],
            "SessionEnd": [{"hooks": [{"type": "command", "command": "ai-bgm stop"}]}],
        }

        # Initialize hooks if it doesn't exist
        if "hooks" not in settings:
            settings["hooks"] = {}

        # Update hooks
        settings["hooks"]["UserPromptSubmit"] = hooks_config["UserPromptSubmit"]
        settings["hooks"]["Stop"] = hooks_config["Stop"]
        settings["hooks"]["SessionEnd"] = hooks_config["SessionEnd"]

        return settings
```

#### Step 2: Register Integration

Add your integration to `aibgm/commands/integrations/registry.py`:

```python
from aibgm.commands.integrations.newtool import NewToolIntegration

class IntegrationRegistry:
    _integrations: List[Type[AIToolIntegration]] = [
        ClaudeIntegration,
        IFlowIntegration,
        NewToolIntegration,  # Add here
    ]
```

#### Step 3: Test

```bash
ai-bgm setup
# Your new tool should appear in the menu
```

**That's it!** No need to modify `setup.py` or any other files.

#### Integration Architecture

```
aibgm/commands/integrations/
├── __init__.py           # Base AIToolIntegration class
├── registry.py           # Integration registry
├── claude.py             # Claude Code integration
├── iflow.py              # iFlow CLI integration
└── <newtool>.py          # Your new integration
```

**Key Points:**
- Each integration is isolated in its own file
- All integrations implement the same `AIToolIntegration` interface
- Registry automatically discovers and provides all integrations
- Easy to add, remove, or modify integrations without affecting others

#### Claude Code Hooks Configuration

For Claude Code, hooks are configured in `~/.claude/settings.json` with support for various hook events. See the official documentation for details:
- [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks)

#### iFlow CLI Hooks Configuration

For iFlow CLI, the hooks are configured via the `userpromptsubmit` hook. See the official documentation for details:
- [iFlow CLI Hooks Documentation](https://platform.iflow.cn/en/cli/examples/hooks#8-userpromptsubmit-hook)

### Add New Music Configuration

1. Create directory: `aibgm/assets/sounds/<name>/`
2. Add audio files
3. Update `aibgm/config.json`

### Add CLI Option

In `cli.py`, use Click decorators:

```python
@cli.command()
@click.option("--new-option", is_flag=True)
def my_command(new_option):
    # Use: new_option
    pass
```

## Testing

### Manual Testing Checklist

- [ ] `ai-bgm play work 0` loops correctly
- [ ] `ai-bgm play done` plays once
- [ ] `ai-bgm stop` kills player
- [ ] `ai-bgm select` updates selection
- [ ] `ai-bgm setup` creates valid hooks
- [ ] New config appears in selection
- [ ] Audio files play without error

### Debug Commands

```bash
# Check daemon status
ps aux | grep "ai-bgm"

# View logs
tail -f ~/.config/ai-bgm/bgm_player.log

# Check PID file
cat ~/.config/ai-bgm/bgm_player.pid

# Test pygame directly
python -c "import pygame; pygame.mixer.init(); print('OK')"

# Test click
python -c "import click; print('OK')"
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
