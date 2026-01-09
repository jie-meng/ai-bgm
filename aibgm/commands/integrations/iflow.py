#!/usr/bin/env python3
"""
iFlow CLI integration for AI BGM.
"""

from pathlib import Path
from typing import Tuple

from aibgm.commands.integrations import AIToolIntegration


class IFlowIntegration(AIToolIntegration):
    """Integration for iFlow CLI."""

    def get_tool_info(self) -> Tuple[str, str]:
        """Get iFlow CLI tool information."""
        return ("iflow", "iFlow CLI")

    def get_settings_path(self) -> Path:
        """Get iFlow CLI settings path."""
        return Path.home() / ".iflow" / "settings.json"

    def setup_hooks(self, settings: dict) -> dict:
        """
        Setup iFlow CLI hooks.

        Configures hooks for:
        - UserPromptSubmit: Start work music
        - Stop: Play done music
        - SessionEnd: Stop all music
        - Notification: Play notification music

        Args:
            settings: Existing settings dictionary

        Returns:
            Updated settings dictionary
        """
        hooks_config = {
            "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "ai-bgm play work 0"}]}],
            "Stop": [{"hooks": [{"type": "command", "command": "ai-bgm play done"}]}],
            "SessionEnd": [{"hooks": [{"type": "command", "command": "ai-bgm stop"}]}],
            "Notification": [
                {"hooks": [{"type": "command", "command": "ai-bgm play notification 0"}]}
            ],
        }

        # Initialize hooks if it doesn't exist
        if "hooks" not in settings:
            settings["hooks"] = {}

        # Update hooks, keep other hooks intact
        settings["hooks"]["UserPromptSubmit"] = hooks_config["UserPromptSubmit"]
        settings["hooks"]["Stop"] = hooks_config["Stop"]
        settings["hooks"]["SessionEnd"] = hooks_config["SessionEnd"]
        settings["hooks"]["Notification"] = hooks_config["Notification"]

        return settings
