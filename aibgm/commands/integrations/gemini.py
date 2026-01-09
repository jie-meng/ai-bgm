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
        - BeforeAgent: User submits prompt -> start work music
        - AfterAgent: Agent loop ends -> play done music
        - SessionEnd: Session ends -> stop all music

        Args:
            settings: Existing settings dictionary

        Returns:
            Updated settings dictionary
        """
        # Initialize hooks if it doesn't exist
        if "hooks" not in settings:
            settings["hooks"] = {}

        # Configure hooks for AI BGM
        settings["hooks"]["BeforeAgent"] = [{"type": "command", "command": "ai-bgm play work 0"}]
        settings["hooks"]["AfterAgent"] = [{"type": "command", "command": "ai-bgm play done"}]
        settings["hooks"]["SessionEnd"] = [{"type": "command", "command": "ai-bgm stop"}]

        return settings
