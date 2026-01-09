#!/usr/bin/env python3
"""
Cursor Agent integration for AI BGM.
"""

from pathlib import Path
from typing import Tuple

from aibgm.commands.integrations import AIToolIntegration


class CursorAgentIntegration(AIToolIntegration):
    """Integration for Cursor Agent."""

    def get_tool_info(self) -> Tuple[str, str]:
        """Get Cursor Agent tool information."""
        return ("cursor-agent", "Cursor Agent")

    def get_settings_path(self) -> Path:
        """Get Cursor Agent hooks configuration path."""
        return Path.home() / ".cursor" / "hooks.json"

    def setup_hooks(self, settings: dict) -> dict:
        """
        Setup Cursor Agent hooks.

        Configures hooks for:
        - beforeSubmitPrompt: Start work music when user submits a prompt
        - stop: Play done music and stop all music when agent stops

        Args:
            settings: Existing hooks configuration dictionary

        Returns:
            Updated hooks configuration dictionary
        """
        # Cursor uses a different structure: version + hooks
        if "version" not in settings:
            settings["version"] = 1

        if "hooks" not in settings:
            settings["hooks"] = {}

        # Configure hooks for AI BGM
        # beforeSubmitPrompt: User submits a prompt -> start work music
        settings["hooks"]["beforeSubmitPrompt"] = [{"command": "ai-bgm play work 0"}]

        # stop: Agent stops -> play done music
        settings["hooks"]["stop"] = [{"command": "ai-bgm play done"}]

        return settings
