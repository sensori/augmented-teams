"""
Content class.

Placeholder for behavior content configuration.
"""
from typing import Any, Dict


class Content:
    """Represents content configuration for a behavior."""

    def __init__(self, config_source: Any):
        instructions = getattr(config_source, "instructions", {}) or {}
        self.instructions: Dict = instructions.get("content", {})
