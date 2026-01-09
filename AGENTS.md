# AGENTS.md

AI agent guidelines for working on the AI BGM project.

## System Context

**Project Type**: CLI tool for AI-assisted work sessions
**Language**: Python 3.9+
**Audio**: pygame.mixer
**Package**: pyproject.toml

## Key Facts for AI Agents

### What This Project Does

- Plays background music during AI-assisted work
- Auto-stops when AI finishes (via hooks)
- Supports multiple BGM configurations
- Runs as daemon process

### Important Conventions

- Use **Black** (line length 100) for formatting
- Type hints required for function signatures
- Use `pathlib.Path`, not `os.path`
- Config in `config.json`, user selection in `~/.config/ai-bgm/selection.json`

### Critical Paths

| Path | Purpose |
|------|---------|
| `aibgm/config.json` | BGM configurations |
| `aibgm/cli.py` | Unified CLI entry point |
| `main.py` | Local development entry (not packaged) |

### Daemon Behavior

- PID file: `~/.config/ai-bgm/bgm_player.pid`
- Log file: `~/.config/ai-bgm/bgm_player.log`
  - Auto-rotates at 1000 lines
  - Keeps last 500 lines
- Kill with `SIGTERM`, fallback `SIGKILL`

## Common Tasks

### Add Music Config

```bash
# 1. Add files to aibgm/assets/sounds/<name>/
# 2. Update aibgm/config.json
{
  "<name>": {
    "work": ["file.mp3"],
    "done": ["done.mp3"]
  }
}
# 3. Test: ai-bgm select
```

### Add CLI Option

In `cli.py`, use Click decorators:
```python
@cli.command()
@click.option("--option", is_flag=True)
def my_command(option):
    # Use: option
    pass
```

### Add AI Tool

Adding a new AI tool integration:

1. Create `aibgm/commands/integrations/<toolname>.py`
2. Implement `AIToolIntegration` abstract class
3. Register in `aibgm/commands/integrations/registry.py`

Example:
```python
from aibgm.commands.integrations import AIToolIntegration

class NewToolIntegration(AIToolIntegration):
    def get_tool_info(self) -> Tuple[str, str]:
        return ("newtool", "New Tool Name")
    
    def get_settings_path(self) -> Path:
        return Path.home() / ".newtool" / "settings.json"
    
    def setup_hooks(self, settings: dict) -> dict:
        # Configure hooks
        return settings
```

Then register:
```python
# In registry.py
_integrations = [
    ClaudeIntegration,
    IFlowIntegration,
    NewToolIntegration,  # Add here
]
```

## Testing

```bash
# Format
black aibgm/

# Lint
flake8 aibgm/

# Type check
mypy aibgm/

# Manual test
ai-bgm play work 0
ai-bgm stop
ai-bgm select
```

## Constraints

- Don't modify `docs/Dev.md` (user maintains)
- Don't add new dependencies without approval
- Keep changes minimal and focused
- Test before committing

## Getting Help

- User guide: [README.md](README.md)
- Dev setup: [docs/Dev.md](docs/Dev.md)
