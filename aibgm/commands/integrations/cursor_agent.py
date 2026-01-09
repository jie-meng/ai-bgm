#!/usr/bin/env python3
"""
Cursor Agent integration for AI BGM.
"""

import shutil
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

        This method copies hook scripts to ~/.cursor/hooks/ and configures
        hooks.json to reference them using relative paths.

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

        # Copy hook scripts to ~/.cursor/hooks/
        cursor_hooks_dir = Path.home() / ".cursor" / "hooks"
        cursor_hooks_dir.mkdir(parents=True, exist_ok=True)

        # Get the source hooks directory from the package
        package_hooks_dir = Path(__file__).parent.parent.parent / "assets" / "hooks"

        # Copy generic AI BGM hook scripts
        # These scripts are reusable across different AI tool integrations
        hook_scripts = ["ai-bgm-play-work.sh", "ai-bgm-play-done.sh", "ai-bgm-stop.sh"]
        for script_name in hook_scripts:
            src = package_hooks_dir / script_name
            dst = cursor_hooks_dir / script_name
            if src.exists():
                shutil.copy2(src, dst)
                # Ensure execute permission
                dst.chmod(0o755)

        # Configure hooks for AI BGM using relative paths
        # beforeSubmitPrompt: User submits a prompt -> start work music
        settings["hooks"]["beforeSubmitPrompt"] = [{"command": "./hooks/ai-bgm-play-work.sh"}]

        # stop: Agent stops -> play done music
        settings["hooks"]["stop"] = [{"command": "./hooks/ai-bgm-play-done.sh"}]

        return settings
