#!/usr/bin/env python
"""Select BGM configuration and save it to user config directory."""

import json
import sys
from pathlib import Path


def get_config_path():
    """Get the path to the user config directory."""
    config_dir = Path.home() / ".config" / "ai-bgm"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "selection.json"


def load_builtin_config():
    """Load the built-in config.json from the package, merged with config_ext.json if exists."""
    # Get the directory where this script is located
    current_dir = Path(__file__).parent
    config_file = current_dir / "config.json"
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Load config_ext.json from the same directory if exists
    config_ext_file = current_dir / "config_ext.json"
    if config_ext_file.exists():
        with open(config_ext_file, "r", encoding="utf-8") as f:
            ext_config = json.load(f)
            # Merge: ext config overrides built-in config for same keys
            config.update(ext_config)

    return config


def load_current_selection():
    """Load the current selection from user config directory."""
    config_path = get_config_path()
    if not config_path.exists():
        return None

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("selected")


def save_selection(selection):
    """Save the selected BGM configuration to user config directory."""
    config_path = get_config_path()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({"selected": selection}, f)
    print(f"Selected: {selection}")
    print(f"Config saved to: {config_path}")


def main():
    """Main function to select BGM configuration."""
    config = load_builtin_config()
    options = list(config.keys())

    if not options:
        print("Error: No available BGM configuration")
        sys.exit(1)

    # Load current selection
    current_selection = load_current_selection()

    print("Please select BGM configuration:")
    for i, option in enumerate(options, 1):
        current_marker = " (current)" if option == current_selection else ""
        print(f"{i}. {option}{current_marker}")

    try:
        default_index = options.index(current_selection) + 1 if current_selection in options else 1
        user_input = input(f"Enter option (1-{len(options)}, current {default_index}): ").strip()
        if not user_input:
            if current_selection and current_selection in options:
                selection = current_selection
            else:
                selection = options[0]
        else:
            index = int(user_input) - 1
            if 0 <= index < len(options):
                selection = options[index]
            else:
                print(f"Error: Invalid option, please enter 1-{len(options)}")
                sys.exit(1)
    except ValueError:
        print("Error: Please enter a valid number")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(0)

    save_selection(selection)


if __name__ == "__main__":
    main()
