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
| `aibgm/ai_bgm_play.py` | Playback logic |
| `aibgm/ai_bgm_stop.py` | Kill player process |
| `aibgm/ai_bgm_select.py` | User selection |
| `aibgm/ai_bgm_setup.py` | AI tool hooks |

### Daemon Behavior

- PID file: `~/.config/ai-bgm/bgm_player.pid`
- Log file: `~/.config/ai-bgm/bgm_player.log`
- Kill with `SIGTERM`, fallback `SIGKILL`

## Common Tasks

### Add Music Config

```bash
# 1. Add files to aibgm/assets/sounds/<name>/
# 2. Update aibgm/config.json
{
  "<name>": {
    "work": ["file.mp3"],
    "end": ["end.mp3"]
  }
}
# 3. Test: ai-bgm-select
```

### Add CLI Option

In `ai_bgm_play.py` `main()`:
```python
parser.add_argument("--option", action="store_true")
# Use: args.option
```

### Add AI Tool

1. Add to `get_ai_tools()` in `ai_bgm_setup.py`
2. Implement setup function
3. Call in `main()`

## Testing

```bash
# Format
black aibgm/

# Lint
flake8 aibgm/

# Type check
mypy aibgm/

# Manual test
ai-bgm-play work -1
ai-bgm-stop
ai-bgm-select
```

## Constraints

- Don't modify `docs/Dev.md` (user maintains)
- Don't add new dependencies without approval
- Keep changes minimal and focused
- Test before committing

## Getting Help

- User guide: [README.md](README.md)
- Dev setup: [docs/Dev.md](docs/Dev.md)
