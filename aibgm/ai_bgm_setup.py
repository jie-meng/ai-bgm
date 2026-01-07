#!/usr/bin/env python3
"""Setup AI BGM integration with AI tools."""

import json
import sys
from pathlib import Path


def get_ai_tools():
    """Get supported AI tools."""
    return [
        ("iflow", "iFlow CLI"),
    ]


def get_settings_path(tool: str) -> Path:
    """Get the settings path for the specified AI tool."""
    home = Path.home()

    if tool == "iflow":
        return home / ".iflow" / "settings.json"

    raise ValueError(f"Unknown AI tool: {tool}")


def load_settings(path: Path) -> dict:
    """Load settings from the settings file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(path: Path, settings: dict) -> None:
    """Save settings to the settings file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def setup_iflow(settings: dict) -> dict:
    """Setup iFlow integration.

    Args:
        settings: The existing settings dictionary.

    Returns:
        Updated settings dictionary.
    """
    hooks_config = {
        "UserPromptSubmit": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": "ai-bgm-play work -1",
                    }
                ]
            }
        ],
        "Stop": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": "ai-bgm-play end",
                    }
                ]
            }
        ],
        "SessionEnd": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": "ai-bgm-stop",
                    }
                ]
            }
        ],
        "Notification": [
            {
                "matcher": ".*permission.*",
                "hooks": [
                    {
                        "type": "command",
                        "command": "ai-bgm-play notification -1",
                    }
                ]
            }
        ]
    }

    # Initialize hooks if it doesn't exist
    if "hooks" not in settings:
        settings["hooks"] = {}

    # Update only UserPromptSubmit, Stop, SessionEnd, and Notification, keep other hooks intact
    settings["hooks"]["UserPromptSubmit"] = hooks_config["UserPromptSubmit"]
    settings["hooks"]["Stop"] = hooks_config["Stop"]
    settings["hooks"]["SessionEnd"] = hooks_config["SessionEnd"]
    settings["hooks"]["Notification"] = hooks_config["Notification"]

    return settings


def main():
    """Main function to setup AI BGM integration."""
    ai_tools = get_ai_tools()

    print("Select AI tool:")
    for i, (tool_id, tool_name) in enumerate(ai_tools, 1):
        print(f"{i}. {tool_name}")

    try:
        user_input = input("Enter option: ").strip()
        if not user_input:
            print("Cancelled")
            sys.exit(0)

        index = int(user_input) - 1
        if 0 <= index < len(ai_tools):
            tool_id = ai_tools[index][0]
        else:
            print(f"Error: Invalid option, please enter 1-{len(ai_tools)}")
            sys.exit(1)
    except ValueError:
        print("Error: Please enter a valid number")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(0)

    # Get settings path
    settings_path = get_settings_path(tool_id)

    if not settings_path.exists():
        print(f"Error: Settings file not found at {settings_path}")
        sys.exit(1)

    # Load existing settings
    settings = load_settings(settings_path)

    # Setup integration based on tool type
    if tool_id == "iflow":
        settings = setup_iflow(settings)
    else:
        print(f"Error: Unknown tool: {tool_id}")
        sys.exit(1)

    # Save updated settings
    save_settings(settings_path, settings)

    print(f"Successfully configured AI BGM for {ai_tools[index][1]}")
    print(f"Settings saved to: {settings_path}")


if __name__ == "__main__":
    main()
