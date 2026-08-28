#!/usr/bin/env python3
"""
ZCode integration for AI BGM.

ZCode stores hooks in ``~/.zcode/cli/config.json`` under a top-level
``hooks`` object shaped as::

    { "enabled": true, "events": { "<Event>": [ { "matcher": "...", "hooks": [...] } ] } }

Configuration-file hooks only run when ``hooks.enabled`` is true, so setup
sets it. ZCode supports exactly seven events (``SessionStart``,
``UserPromptSubmit``, ``PreToolUse``, ``PermissionRequest``, ``PostToolUse``,
``PostToolUseFailure``, ``Stop``) - there is no ``SessionEnd`` and no
``Notification``.

Reference: the ``zcode-configuration-guide`` and ``diagnosing-hooks`` skills
shipped with the ZCode client.
"""

from pathlib import Path
from typing import Dict, List, Tuple

from mythril_agent_bgm.commands.integrations import AIToolIntegration


class ZcodeIntegration(AIToolIntegration):
    """Integration for ZCode."""

    def get_tool_info(self) -> Tuple[str, str]:
        """Get ZCode tool information."""
        return ("zcode", "ZCode")

    def get_settings_path(self) -> Path:
        """Get ZCode settings path."""
        return Path.home() / ".zcode" / "cli" / "config.json"

    def setup_hooks(self, settings: dict) -> dict:
        """
        Setup ZCode hooks.

        Configures hooks for:
        - UserPromptSubmit: Start work music
        - Stop: Play done music
        - PermissionRequest: Play notification music
        - PostToolUse: Switch back to work music once the user answers a
          permission prompt. ``bgm play work 0`` is idempotent (a no-op while
          work music is already playing), so hooking it on a frequent event
          never restarts the current track.

        ZCode has no session-end event, so playback is not stopped when the
        session closes.

        Args:
            settings: Existing settings dictionary

        Returns:
            Updated settings dictionary
        """
        hooks = settings.setdefault("hooks", {})
        # Configuration-file hooks are skipped unless explicitly enabled.
        hooks["enabled"] = True
        events = hooks.setdefault("events", {})
        events.update(self._bgm_events())
        return settings

    def cleanup_hooks(self, settings: dict) -> dict:
        """Remove BGM hooks from ZCode settings."""
        hooks = settings.get("hooks", {})
        events = hooks.get("events", {})
        for event in self._bgm_events():
            events.pop(event, None)
        if not events:
            hooks.pop("events", None)
            hooks.pop("enabled", None)
        if not hooks:
            settings.pop("hooks", None)
        return settings

    @staticmethod
    def _bgm_events() -> Dict[str, List[dict]]:
        """Build the BGM hook matchers keyed by ZCode event name."""

        def entry(command: str) -> List[dict]:
            return [{"hooks": [{"type": "command", "command": command}]}]

        return {
            "UserPromptSubmit": entry("bgm play work 0"),
            "Stop": entry("bgm play done"),
            "PermissionRequest": entry("bgm play notification 0"),
            "PostToolUse": entry("bgm play work 0"),
        }
