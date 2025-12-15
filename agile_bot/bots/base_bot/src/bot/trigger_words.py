"""
TriggerWords class.

Handles trigger word matching for behaviors.
"""
import re
from typing import List, Union, Dict, Any


class TriggerWords:
    """Evaluate trigger word patterns from behavior configuration."""

    def __init__(self, config_source: Any):
        # config_source expected to provide trigger_words property (BehaviorConfig)
        self._triggers = getattr(config_source, "trigger_words", None)

    def matches(self, text: str) -> bool:
        """Return True if text matches any configured trigger pattern."""
        if not self._triggers:
            return False

        patterns: List[str] = []
        if isinstance(self._triggers, dict):
            patterns = self._triggers.get("patterns", [])
        elif isinstance(self._triggers, list):
            patterns = self._triggers

        for pattern in patterns:
            try:
                if re.search(pattern, text, flags=re.IGNORECASE):
                    return True
            except re.error:
                if pattern.lower() in text.lower():
                    return True
        return False


