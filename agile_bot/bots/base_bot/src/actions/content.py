"""
Content class.

Placeholder for behavior content configuration.
"""
from typing import Any, Dict


class Content:
    """Represents content configuration for a behavior."""

    def __init__(self, config_source: Any):
        instructions = getattr(config_source, "instructions", {}) or {}
        # Handle both dict and list formats for instructions
        if isinstance(instructions, dict):
            self.instructions: Dict = instructions.get("content", {})
        else:
            # If instructions is a list or other type, default to empty dict
            self.instructions: Dict = {}
