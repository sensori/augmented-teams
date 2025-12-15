from typing import Any, Dict


class Content:
    def __init__(self, config_source: Any):
        instructions = getattr(config_source, "instructions", {}) or {}
        if isinstance(instructions, dict):
            self.instructions: Dict = instructions.get("content", {})
        else:
            self.instructions: Dict = {}
