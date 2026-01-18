#!/usr/bin/env python3
"""
Gemini CLI integration for AI BGM.
"""

from pathlib import Path
from typing import Tuple

from aibgm.commands.integrations import AIToolIntegration


class GeminiIntegration(AIToolIntegration):
    """Integration for Gemini CLI."""

    def get_tool_info(self) -> Tuple[str, str]:
        """Get Gemini CLI tool information."""
        return ("gemini", "Gemini CLI")

    def get_settings_path(self) -> Path:
        """Get Gemini CLI settings path."""
        return Path.home() / ".gemini" / "settings.json"

    def setup_hooks(self, settings: dict) -> dict:
        """
        Setup Gemini CLI hooks.

        Configures hooks for:
        - BeforeModel: User submits prompt -> start work music
        - AfterModel: Model response ends -> play done music
        - SessionEnd: Session ends -> stop all music

        Args:
            settings: Existing settings dictionary

        Returns:
            Updated settings dictionary
        """
        # Enable hooks in tools
        if "tools" not in settings:
            settings["tools"] = {}
        settings["tools"]["enableHooks"] = True

        # Initialize hooks if it doesn't exist
        if "hooks" not in settings:
            settings["hooks"] = {}

        # Configure hooks for AI BGM
        settings["hooks"]["BeforeModel"] = [
            {
                "matcher": "*",
                "hooks": [
                    {
                        "name": "Play work music",
                        "type": "command",
                        "command": "ai-bgm play work 0",
                        "description": "Play work music",
                    }
                ],
            }
        ]
        settings["hooks"]["AfterModel"] = [
            {
                "matcher": "*",
                "hooks": [
                    {
                        "name": "Play done music",
                        "type": "command",
                        "command": "ai-bgm play done",
                        "description": "Play done music",
                    }
                ],
            }
        ]
        settings["hooks"]["SessionEnd"] = [
            {
                "matcher": "*",
                "hooks": [
                    {
                        "name": "Stop music",
                        "type": "command",
                        "command": "ai-bgm stop",
                        "description": "Stop all music",
                    }
                ],
            }
        ]

        return settings
