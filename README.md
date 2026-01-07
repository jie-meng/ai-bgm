# AI BGM

AI CLI Background Music Player - A cross-platform tool that plays work music during work sessions and integrates with AI tools.

## Quick Start

```bash
# 1. Install
pip install -e .

# 2. Setup AI tool integration (e.g., iFlow CLI)
ai-bgm-setup

# 3. Select your BGM configuration
ai-bgm-select

# 4. Done! Music will auto-play when AI is working
```

## Installation

### Prerequisites

- Python 3.9+
- pip

### Install

```bash
pip install -e .
```

This installs CLI commands:
- `ai-bgm-play` - Play music
- `ai-bgm-stop` - Stop music
- `ai-bgm-select` - Select configuration
- `ai-bgm-setup` - Setup AI tool integration

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
ai-bgm-select
```

Interactively choose from available configurations (e.g., `maou`, `default`). Selection is saved to `~/.config/ai-bgm/selection.json`.

#### 2. Setup AI Tool Integration

```bash
ai-bgm-setup
```

Currently supports **iFlow CLI** - music auto-plays when you submit prompts and stops when done.

### Manual Commands

#### Play Work Music

```bash
ai-bgm-play work -1    # Loop indefinitely
ai-bgm-play work 3     # Play 3 times
ai-bgm-play end        # Play end music once
```

#### Stop Music

```bash
ai-bgm-stop
```

Stops any playing music.

### Test BGM

```bash
# Test play (single end music)
ai-bgm-play end

# Test work music loop (Ctrl+C to stop)
ai-bgm-play work -1

# Verify configuration
ai-bgm-select
```

## Custom Configuration

### Add Custom Music

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
    "end": ["complete.mp3"]
  }
}
```

3. **Select your config**:

```bash
ai-bgm-select
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
- Personal music collections should be kept locally and NOT committed
- The `.gitignore` file is configured to ignore all directories except `default` and `maou`

### Config Structure

| Field | Description |
|-------|-------------|
| `work` | List of music files to play during work |
| `end` | List of music files to play when done |

**Note**: File paths are relative to `aibgm/assets/sounds/<config-name>/`

## File Structure

```
ai-bgm/
├── aibgm/
│   ├── ai_bgm_play.py     # Music playback
│   ├── ai_bgm_stop.py     # Stop music
│   ├── ai_bgm_select.py   # Configuration selection
│   ├── ai_bgm_setup.py    # AI tool integration
│   ├── config.json        # Music configurations
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
