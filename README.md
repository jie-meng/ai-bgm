# mythril-agent-bgm

A cross-platform CLI tool that plays background music during AI-assisted work sessions and integrates with AI tools.

## Install

```bash
pip install mythril-agent-bgm

# Upgrade
pip install -U mythril-agent-bgm
```

This installs the `bgm` CLI command.

## Quick Start

Running any `bgm` command for the first time auto-creates `~/.config/mythril-agent-bgm/` with a starter config.

1. `bgm setup` — install AI tool integration hooks (e.g. Claude, Cursor Agent)
2. `bgm select` — pick a configuration (`default` uses built-in music; `my_collection` uses your own)
3. `bgm enable` — enable BGM (auto-starts music when AI starts working)

### Customize with your own audio

1. Copy your `.mp3` files into `~/.config/mythril-agent-bgm/sounds/` (no subdirectories)
2. Edit `~/.config/mythril-agent-bgm/config.json` and change `"my_collection"` → your files:

```json
{
  "my_collection": {
    "work": ["my_song.mp3", "another.mp3"],
    "done": ["done.mp3"]
  }
}
```

3. Run `bgm select` and pick `my_collection`

Rename `my_collection` to anything you like — it's just a key.

## CLI Commands

```bash
bgm play work 0          # Loop work music indefinitely
bgm play work 3          # Play work music 3 times
bgm play done            # Play done music once
bgm play notification    # Play notification sound
bgm stop                 # Stop music
bgm toggle               # Toggle play/stop
bgm select               # Choose configuration
bgm setup                # Setup AI tool integration
bgm cleanup              # Remove AI tool integration
bgm enable               # Enable BGM
bgm disable              # Disable BGM
```

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
