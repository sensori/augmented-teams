"""
TriggerWords class.

Handles trigger word matching for behaviors.
"""
import re
from typing import List, Union, Dict, Any, Optional


class TriggerWords:
    """Evaluate trigger word patterns from behavior configuration.
    
    Domain Model:
        Instantiated with: Behavior, BehaviorConfig
        Method: match_pattern()
        Property: priority
    """

    def __init__(self, behavior_config: Any, behavior: Optional[Any] = None):
        """Initialize TriggerWords.
        
        Domain Model: Instantiated with: Behavior, BehaviorConfig
        
        Args:
            behavior_config: BehaviorConfig instance (provides trigger_words property)
            behavior: Optional Behavior instance (for backward compatibility, can be None)
        """
        # behavior_config expected to provide trigger_words property (BehaviorConfig)
        self._behavior_config = behavior_config
        self._behavior = behavior
        self._triggers = getattr(behavior_config, "trigger_words", None)

    def matches(self, text: str) -> bool:
        """Return True if text matches any configured trigger pattern.
        
        Domain Model: matches_trigger (delegated from Behavior)
        """
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
        """Match a single pattern against text.
        
        Domain Model: match_pattern() method
        
        Args:
            pattern: Pattern string (regex or literal)
            text: Text to match against
            
        Returns:
            True if pattern matches text
        """
        try:
            if re.search(pattern, text, flags=re.IGNORECASE):
                return True
        except re.error:
            # Fallback to literal string matching if regex is invalid
            if pattern.lower() in text.lower():
                return True
        return False
    
    @property
    def priority(self) -> int:
        """Get priority for trigger words.
        
        Domain Model: priority property
        
        Returns:
            Priority value (higher = more important), defaults to 0
        """
        if isinstance(self._triggers, dict):
            return self._triggers.get("priority", 0)
        return 0



