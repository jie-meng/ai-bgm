# AI BGM

AI CLI Background Music Player - A cross-platform tool that plays work music during work sessions and integrates with AI tools.

## Quick Start

```bash
# 1. Install
pip install .

# 2. Setup AI tool integration (e.g., Claude Code)
ai-bgm setup

# 3. Select your BGM configuration
ai-bgm select

# 4. Done! Music will auto-play when AI is working
```

## Installation

### Prerequisites

- Python 3.9+
- pip

### Install

```bash
pip install .
```

This installs CLI command:
- `ai-bgm` - Unified CLI with subcommands: play, stop, select, setup

### System Dependencies

**macOS**: None required.

**Linux**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev libsdl2-dev

# Fedora
sudo dnf install python3-devel SDL2-devel
```

**Windows**: None required.

## Usage

### First Time Setup

#### 1. Select BGM Configuration

```bash
ai-bgm select
```

Interactively choose from available configurations (e.g., `maou`, `default`). Selection is saved to `~/.config/ai-bgm/selection.json`.

#### 2. Setup AI Tool Integration

```bash
ai-bgm setup
```

Currently supports **Claude Code** and **iFlow CLI** - music auto-plays when you submit prompts and stops when done.

### Manual Commands

#### Play Work Music

```bash
ai-bgm play work 0     # Loop indefinitely
ai-bgm play work 3     # Play 3 times
ai-bgm play done       # Play done music once
```

#### Stop Music

```bash
ai-bgm stop
```

Stops any playing music.

### Test BGM

```bash
# Test play (single done music)
ai-bgm play done

# Test work music loop (Ctrl+C to stop)
ai-bgm play work 0

# Verify configuration
ai-bgm select
```

## Custom Configuration

### Add Custom Music

#### Method 1: Using config_ext.json (Recommended for copyrighted music)

For copyrighted music that should NOT be committed to the repository:

1. **Create a music directory** in `aibgm/assets/sounds/<your-config>/`

```bash
mkdir -p aibgm/assets/sounds/my_collection
cp /path/to/your/song.mp3 aibgm/assets/sounds/my_collection/
```

2. **Create or edit `aibgm/config_ext.json`** (this file is ignored by git):

```json
{
  "my_collection": {
    "work": ["song1.mp3", "song2.mp3"],
    "done": ["complete.mp3"]
  }
}
```

3. **Select your config**:

```bash
ai-bgm-select
```

**How it works**:
- `config.json` contains built-in configurations (default, maou)
- `config_ext.json` contains your custom configurations
- If a key exists in both files, `config_ext.json` takes precedence
- `config_ext.json` is gitignored, so your copyrighted music won't be uploaded

#### Method 2: Using config.json (For royalty-free music only)

For royalty-free music that can be shared:

1. **Place audio files** in `aibgm/assets/sounds/<your-config>/`

```bash
mkdir -p aibgm/assets/sounds/my_music
cp /path/to/your/song.mp3 aibgm/assets/sounds/my_music/
```

2. **Update config.json**:

```json
{
  "my_music": {
    "work": ["song1.mp3", "song2.mp3"],
    "done": ["complete.mp3"]
  }
}
```

3. **Select your config**:

```bash
ai-bgm select
```

### Music Licensing

**IMPORTANT**: Only music that is free for commercial use or royalty-free should be committed to this repository.

**Included Configurations**:

- **default**: Minimal sound effects (bubble pop for completion)
- **maou**: Music from [魔王魂 (Maou Audio)](https://maou.audio/)
  - License: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
  - Free for personal and commercial use
  - Modification and redistribution allowed with attribution
  - **DO NOT**: Use for AI music training, claim as your own, or sell on streaming platforms
  - Attribution: "音乐：魔王魂" (Music: Maou Audio)

**⚠️ Copyright Warning**:

- Do NOT commit copyrighted music files to this repository
- Only add music that you have explicit permission to use and distribute
- **For copyrighted music**: Use `config_ext.json` and custom directories in `assets/sounds/`
  - These are automatically gitignored and won't be uploaded
  - Perfect for personal music collections
  - Example: Create `assets/sounds/my_collection/` and configure it in `config_ext.json`
- **For royalty-free music**: Add to `config.json` and appropriate directories
- The `.gitignore` file is configured to ignore all directories except `default` and `maou`

3. **Select your config**:

```bash
ai-bgm select
```

### Config Structure

| Field | Description |
|-------|-------------|
| `work` | List of music files to play during work |
| `done` | List of music files to play when done |

**Note**: File paths are relative to `aibgm/assets/sounds/<config-name>/`

## File Structure

```
ai-bgm/
├── aibgm/
│   ├── main.py            # Unified CLI entry point
│   ├── config.json        # Built-in music configurations
│   ├── config_ext.json    # Custom music configurations (gitignored)
│   └── assets/sounds/     # Audio files
│       ├── default/
│       └── maou/
├── docs/
│   └── Dev.md             # Development guide
├── pyproject.toml
└── README.md
```

## Troubleshooting

**No sound?**
```bash
# Check pygame
pip show pygame

# Check log
cat ~/.config/ai-bgm/bgm_player.log
```

**Music won't stop?**
```bash
# Kill stale process
ps aux | grep ai-bgm
kill <pid>
rm ~/.config/ai-bgm/bgm_player.pid
```

## License

MIT

## Development

See [docs/Dev.md](docs/Dev.md) for development guide.
