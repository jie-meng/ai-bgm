#!/usr/bin/env python3
"""
CodeBuddy Code integration for AI BGM.

CodeBuddy Code uses the same declarative ``hooks`` format as Claude Code:
a ``hooks`` object keyed by event name -> array of matcher objects ->
array of command objects, stored in ``~/.codebuddy/settings.json``
(user-wide) or ``<project>/.codebuddy/settings.json`` (project-local).

Reference: https://www.codebuddy.ai/docs/cli/hooks-guide
"""

from pathlib import Path
from typing import Tuple

from mythril_agent_bgm.commands.integrations import AIToolIntegration


class CodeBuddyIntegration(AIToolIntegration):
    """Integration for CodeBuddy Code."""

    def get_tool_info(self) -> Tuple[str, str]:
        """Get CodeBuddy Code tool information."""
        return ("codebuddy", "CodeBuddy Code")

    def get_settings_path(self) -> Path:
        """Get CodeBuddy Code settings path."""
        return Path.home() / ".codebuddy" / "settings.json"

    def setup_hooks(self, settings: dict) -> dict:
        """
        Setup CodeBuddy Code hooks.

        Configures hooks for:
        - UserPromptSubmit: Start work music
        - Stop: Play done music
        - SessionEnd: Stop all music
        - Notification: Play notification music (only on permission_prompt, not idle_prompt)

        Args:
            settings: Existing settings dictionary

        Returns:
            Updated settings dictionary
        """
        hooks_config = {
            "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "bgm play work 0"}]}],
            "Stop": [{"hooks": [{"type": "command", "command": "bgm play done"}]}],
            "SessionEnd": [{"hooks": [{"type": "command", "command": "bgm stop"}]}],
            "Notification": [
                {
                    "matcher": "permission_prompt",
                    "hooks": [{"type": "command", "command": "bgm play notification 0"}],
                }
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

    def cleanup_hooks(self, settings: dict) -> dict:
        """Remove BGM hooks from CodeBuddy Code settings."""
        hooks = settings.get("hooks", {})
        for key in ("UserPromptSubmit", "Stop", "SessionEnd", "Notification"):
            hooks.pop(key, None)
        if not hooks:
            settings.pop("hooks", None)
        return settings
