#!/usr/bin/env python3
"""
Registry for AI tool integrations.
"""

from typing import List, Type

from aibgm.commands.integrations import AIToolIntegration
from aibgm.commands.integrations.claude import ClaudeIntegration
from aibgm.commands.integrations.iflow import IFlowIntegration


class IntegrationRegistry:
    """
    Registry for managing AI tool integrations.

    To add a new integration:
    1. Create a new file in aibgm/commands/integrations/
    2. Implement AIToolIntegration abstract class
    3. Register it in _integrations list below
    """

    # Register all available integrations here
    _integrations: List[Type[AIToolIntegration]] = [
        ClaudeIntegration,
        IFlowIntegration,
    ]

    @classmethod
    def get_all_integrations(cls) -> List[AIToolIntegration]:
        """
        Get all registered integration instances.

        Returns:
            List of integration instances
        """
        return [integration_class() for integration_class in cls._integrations]

    @classmethod
    def get_integration_by_id(cls, tool_id: str) -> AIToolIntegration:
        """
        Get integration instance by tool ID.

        Args:
            tool_id: Tool identifier (e.g., 'claude', 'iflow')

        Returns:
            Integration instance

        Raises:
            ValueError: If tool_id is not found
        """
        for integration in cls.get_all_integrations():
            if integration.get_tool_info()[0] == tool_id:
                return integration

        raise ValueError(f"Unknown AI tool: {tool_id}")
