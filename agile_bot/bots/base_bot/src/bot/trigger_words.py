import re
from typing import List, Dict, Any


class TriggerWords:
    def __init__(self, behavior_config: Any):
        self._behavior_config = behavior_config
        self._triggers = getattr(behavior_config, "trigger_words", None)

    def matches(self, text: str) -> bool:
        if not self._triggers:
            return False

        patterns: List[str] = []
        if isinstance(self._triggers, dict):
            patterns = self._triggers.get("patterns", [])
        elif isinstance(self._triggers, list):
            patterns = self._triggers

        for pattern in patterns:
            if self.match_pattern(pattern, text):
                return True
        return False
    
    def match_pattern(self, pattern: str, text: str) -> bool:
        try:
            if re.search(pattern, text, flags=re.IGNORECASE):
                return True
        except re.error:
            if pattern.lower() in text.lower():
                return True
        return False
    
    @property
    def priority(self) -> int:
        if isinstance(self._triggers, dict):
            return self._triggers.get("priority", 0)
        return 0



