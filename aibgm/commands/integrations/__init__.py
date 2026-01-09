#!/usr/bin/env python3
"""
Base class for AI tool integrations.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple


class AIToolIntegration(ABC):
    """
    Abstract base class for AI tool integrations.

    Each integration must implement:
    - get_tool_info(): Return (tool_id, tool_name)
    - get_settings_path(): Return path to settings file
    - setup_hooks(settings): Configure hooks in settings
    """

    @abstractmethod
    def get_tool_info(self) -> Tuple[str, str]:
        """
        Get tool information.

        Returns:
            Tuple of (tool_id, tool_name)
        """
        pass

    @abstractmethod
    def get_settings_path(self) -> Path:
        """
        Get the path to the tool's settings file.

        Returns:
            Path to settings.json
        """
        pass

    @abstractmethod
    def setup_hooks(self, settings: dict) -> dict:
        """
        Setup hooks in the settings dictionary.

        Args:
            settings: Existing settings dictionary

        Returns:
            Updated settings dictionary
        """
        pass

    def validate_settings_path(self) -> bool:
        """
        Check if settings file exists.

        Returns:
            True if settings file exists, False otherwise
        """
        return self.get_settings_path().exists()
