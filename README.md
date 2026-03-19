# mythril-agent-bgm

A cross-platform CLI tool that plays background music during AI-assisted work sessions and integrates with AI tools.

## Install

```bash
pip install mythril-agent-bgm

# Upgrade
pip install -U mythril-agent-bgm
```

If you encounter an `externally-managed-environment` error:

```bash
pip install mythril-agent-bgm --break-system-packages

# Upgrade
pip install -U mythril-agent-bgm --break-system-packages
```

This installs the `bgm` CLI command.

## Setup and Use

```bash
# 1. On first run, a user config directory is created automatically.
#    It includes a starter config and a README explaining how to customize.

# 2. Customize your BGM by editing the config in your user directory:
#    - Linux/macOS: ~/.config/mythril-agent-bgm/
#    - Windows:     %APPDATA%\mythril-agent-bgm\

# 3. Add your audio files directly into sounds/ (no subdirectories)
mkdir -p ~/.config/mythril-agent-bgm/sounds
cp /path/to/your/song.mp3 ~/.config/mythril-agent-bgm/sounds/

# 4. Edit ~/.config/mythril-agent-bgm/config.json to register your collection:
#    {
#      "my_collection": {
#        "work": ["song.mp3"],
#        "done": ["complete.mp3"]
#      }
#    }

# 5. Select your configuration
bgm select

# 6. Start playing
bgm play work 0     # Loop indefinitely
bgm play done       # Play once when done

# 7. Setup AI tool integration
bgm setup
```

## How It Works

- **Built-in config**: comes from the installed package
- **Your config**: lives in `~/.config/mythril-agent-bgm/config.json`
- **Merge**: if the same config key exists in both, your fields override built-in ones
- **Audio files**: all mp3s live directly in `sounds/` (no subdirectories); user sounds checked first, built-in second; same filename = user wins

## Built-in BGM

The package includes a `default` configuration with royalty-free music from [Maou Audio](https://maou.audio/).
License: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

To use the built-in config without customization:

```bash
bgm select   # choose "default"
bgm play work 0
```

## CLI Commands

```bash
bgm play work 0         # Loop work music indefinitely
bgm play work 3         # Play work music 3 times
bgm play done           # Play done music once
bgm play notification    # Play notification sound
bgm stop                # Stop music
bgm toggle              # Toggle play/stop
bgm select              # Choose configuration
bgm setup               # Setup AI tool integration
bgm cleanup             # Remove AI tool integration
bgm enable              # Enable BGM
bgm disable             # Disable BGM
```

## Customize Your BGM

Your config directory is created automatically on first run:

| Platform | Path |
|----------|------|
| Linux/macOS | `~/.config/mythril-agent-bgm/` |
| Windows | `%APPDATA%\mythril-agent-bgm\` |

It contains:

- `config.json` — your BGM configurations
- `sounds/` — your personal audio files (place mp3s directly here, no subdirectories)
- `README.md` — guide for customization

See the `README.md` inside that directory for full details.

### Config Structure

```json
{
  "my_collection": {
    "work": ["default_boss.mp3", "default_castle.mp3", ...],
    "done": ["default_congratulations.mp3"],
    "notification": ["default_pause.mp3"]
  }
}
```

### Audio File Rules

- Place all `.mp3` files directly in `sounds/` — subdirectories are not recognized
- Reference files by bare filename: `"song.mp3"`
- If your file has the same name as a built-in file, yours takes priority

## Editor Integration

### Neovim

```lua
keymap.set("n", "<F10>", function()
  vim.fn.jobstart("bgm toggle")
end, { desc = "Toggle AI BGM" })
```

### Vim

```vim
nnoremap <F10> :call system('bgm toggle')<CR>
```

## Troubleshooting

```bash
# Check pygame
pip show pygame

# View daemon log
cat ~/.config/mythril-agent-bgm/bgm_player.log

# Force kill if music won't stop
ps aux | grep bgm
kill <pid>
rm ~/.config/mythril-agent-bgm/bgm_player.pid
```

## Uninstall

```bash
# Remove the package
pip uninstall mythril-agent-bgm

# Remove user data (optional)
rm -rf ~/.config/mythril-agent-bgm
```

## Development

See [docs/Dev.md](docs/Dev.md) for the development guide.

## License

MIT
