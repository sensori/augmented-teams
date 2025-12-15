"""
Trigger Router - Maps user trigger messages to bot/behavior/action routes.

Uses two-stage routing:
1. First stage: Match to which BOT (from bot registry)
2. Second stage: Match to which BEHAVIOR/ACTION within that bot

Loads trigger patterns from bot registry and trigger_words.json files.
"""
from pathlib import Path
from typing import Dict, List, Optional
import json


class TriggerRouter:
    """Routes trigger messages to appropriate bot behaviors and actions using two-stage routing."""
    
    def __init__(self, workspace_root: Path, bot_name: Optional[str] = None):
        """Initialize trigger router.
        
        Args:
            workspace_root: Root workspace directory
            bot_name: Name of specific bot (if None, discovers all bots from registry)
        """
        self.workspace_root = Path(workspace_root)
        self.bot_name = bot_name
        self._bot_registry = self._load_bot_registry()
        
        if bot_name:
            # Single-bot mode (for backward compatibility)
            self._bot_triggers = {bot_name: self._load_bot_triggers(bot_name)}
            self._behavior_triggers = {bot_name: self._load_behavior_triggers(bot_name)}
            self._action_triggers = {bot_name: self._load_action_triggers(bot_name)}
        else:
            # Multi-bot mode - triggers loaded on demand
            self._bot_triggers = {}
            self._behavior_triggers = {}
            self._action_triggers = {}
    
    def match_trigger(
        self,
        message: str,
        current_behavior: Optional[str] = None,
        current_action: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """Match trigger message to bot/behavior/action route using two-stage routing.
        
        Stage 1: Match to which bot (from registry)
        Stage 2: Within that bot, match in order of specificity:
            1. Action-explicit triggers (behavior + action specified)
            2. Behavior triggers (behavior specified, uses current action)
            3. Close triggers (close current action)
            4. Bot-only triggers (uses current behavior and action)
        
        Args:
            message: User's trigger message
            current_behavior: Current behavior from workflow state
            current_action: Current action from workflow state
            
        Returns:
            Dict with bot_name, behavior_name, action_name, match_type
            or None if no match found
        """
        message_lower = message.lower().strip()
        
        # Stage 1: Determine which bot
        target_bot = self.bot_name if self.bot_name else self._match_bot_from_registry(message_lower)
        
        if not target_bot:
            return None
        
        # Load bot's triggers if not already loaded
        if target_bot not in self._behavior_triggers:
            self._behavior_triggers[target_bot] = self._load_behavior_triggers(target_bot)
            self._action_triggers[target_bot] = self._load_action_triggers(target_bot)
            self._bot_triggers[target_bot] = self._load_bot_triggers(target_bot)
        
        # Stage 2: Match behavior/action within the bot
        # Try action-explicit match first (most specific)
        route = self._match_action_explicit(message_lower, target_bot)
        if route:
            return route
        
        # Try behavior match (forwards to current action)
        route = self._match_behavior(message_lower, current_action, target_bot)
        if route:
            return route
        
        # Try close match
        route = self._match_close(message_lower, target_bot)
        if route:
            return route
        
        # Try bot-only match (least specific)
        route = self._match_bot_only(message_lower, current_behavior, current_action, target_bot)
        if route:
            return route
        
        return None
    
    def _match_bot_from_registry(self, message: str) -> Optional[str]:
        """Match message to a bot from the registry.
        
        Args:
            message: Lowercase trigger message
            
        Returns:
            Bot name or None
        """
        for bot_name, bot_info in self._bot_registry.items():
            # Try registry patterns first (for backward compatibility)
            patterns = bot_info.get('trigger_patterns', [])
            
            # If no patterns in registry, load from bot's trigger_words.json
            if not patterns:
                patterns = self._load_bot_triggers(bot_name)
            
            if self._message_matches_patterns(message, patterns):
                return bot_name
        return None
    
    def _match_action_explicit(self, message: str, target_bot: str) -> Optional[Dict[str, str]]:
        """Match message against action-explicit triggers.
        
        Args:
            message: Lowercase trigger message
            target_bot: Bot name to search within
            
        Returns:
            Route dict or None
        """
        action_triggers = self._action_triggers.get(target_bot, {})
        for behavior, action_patterns in action_triggers.items():
            for action, patterns in action_patterns.items():
                if self._message_matches_patterns(message, patterns):
                    return {
                        'bot_name': target_bot,
                        'behavior_name': behavior,
                        'action_name': action,
                        'match_type': 'bot_behavior_action'
                    }
        return None
    
    def _match_behavior(self, message: str, current_action: Optional[str], target_bot: str) -> Optional[Dict[str, str]]:
        """Match message against behavior triggers.
        
        Args:
            message: Lowercase trigger message
            current_action: Current action to forward to
            target_bot: Bot name to search within
            
        Returns:
            Route dict or None
        """
        behavior_triggers = self._behavior_triggers.get(target_bot, {})
        for behavior, patterns in behavior_triggers.items():
            if self._message_matches_patterns(message, patterns):
                return {
                    'bot_name': target_bot,
                    'behavior_name': behavior,
                    'action_name': current_action,
                    'match_type': 'bot_and_behavior'
                }
        return None
    
    def _match_close(self, message: str, target_bot: str) -> Optional[Dict[str, str]]:
        """Match message against close triggers.
        
        Args:
            message: Lowercase trigger message
            target_bot: Bot name
            
        Returns:
            Route dict or None
        """
        close_keywords = ['close', 'done', 'continue', 'next', 'finish', 'complete']
        
        if any(keyword in message for keyword in close_keywords):
            return {
                'bot_name': target_bot,
                'behavior_name': None,
                'action_name': 'close_current_action',
                'match_type': 'close'
            }
        return None
    
    def _match_bot_only(
        self,
        message: str,
        current_behavior: Optional[str],
        current_action: Optional[str],
        target_bot: str
    ) -> Optional[Dict[str, str]]:
        """Match message against bot-only triggers.
        
        Args:
            message: Lowercase trigger message
            current_behavior: Current behavior to forward to
            current_action: Current action to forward to
            target_bot: Bot name
            
        Returns:
            Route dict or None
        """
        bot_triggers = self._bot_triggers.get(target_bot, [])
        if self._message_matches_patterns(message, bot_triggers):
            return {
                'bot_name': target_bot,
                'behavior_name': current_behavior,
                'action_name': current_action,
                'match_type': 'bot_only'
            }
        return None
    
    def _message_matches_patterns(self, message: str, patterns: List[str]) -> bool:
        """Check if message matches any of the given patterns.
        
        Args:
            message: Lowercase message to match
            patterns: List of trigger patterns (will be lowercased)
            
        Returns:
            True if message matches any pattern
        """
        for pattern in patterns:
            if pattern.lower().strip() in message or message in pattern.lower().strip():
                return True
        return False
    
    def _load_bot_registry(self) -> Dict[str, Dict]:
        """Load bot registry.
        
        Returns:
            Dict mapping bot name -> bot info {trigger_patterns, cli_path}
        """
        registry_path = self.workspace_root / 'agile_bot' / 'bots' / 'registry.json'
        
        if not registry_path.exists():
            return {}
        
        try:
            content = registry_path.read_text(encoding='utf-8')
            return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _load_bot_triggers(self, bot_name: str) -> List[str]:
        """Load bot-level trigger patterns.
        
        Args:
            bot_name: Name of the bot
        
        Returns:
            List of trigger patterns
        """
        trigger_file = self.workspace_root / 'agile_bot' / 'bots' / bot_name / 'trigger_words.json'
        return self._load_patterns_from_file(trigger_file)
    
    def _load_behavior_triggers(self, bot_name: str) -> Dict[str, List[str]]:
        """Load behavior-level trigger patterns for all behaviors.
        
        Args:
            bot_name: Name of the bot
        
        Returns:
            Dict mapping behavior name -> trigger patterns
        """
        behaviors_dir = self.workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors'
        
        if not behaviors_dir.exists():
            return {}
        
        behavior_triggers = {}
        
        for behavior_dir in behaviors_dir.iterdir():
            if not behavior_dir.is_dir() or behavior_dir.name.startswith('_'):
                continue
            
            behavior_name = self._extract_behavior_name(behavior_dir.name)
            behavior_file = behavior_dir / 'behavior.json'
            
            # Load from behavior.json (new format)
            if behavior_file.exists():
                try:
                    content = behavior_file.read_text(encoding='utf-8')
                    behavior_data = json.loads(content)
                    trigger_words = behavior_data.get('trigger_words', {})
                    patterns = trigger_words.get('patterns', [])
                    if patterns:
                        behavior_triggers[behavior_name] = patterns
                except Exception:
                    pass
        
        return behavior_triggers
    
    def _load_action_triggers(self, bot_name: str) -> Dict[str, Dict[str, List[str]]]:
        """Load action-level trigger patterns for all behaviors and actions.
        
        Args:
            bot_name: Name of the bot
        
        Returns:
            Dict mapping behavior -> action -> trigger patterns
        """
        behaviors_dir = self.workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors'
        
        if not behaviors_dir.exists():
            return {}
        
        action_triggers = {}
        
        for behavior_dir in behaviors_dir.iterdir():
            if not behavior_dir.is_dir() or behavior_dir.name.startswith('_'):
                continue
            
            behavior_name = self._extract_behavior_name(behavior_dir.name)
            action_triggers[behavior_name] = {}
            
            # Check all subdirectories for action trigger words
            for action_dir in behavior_dir.iterdir():
                if not action_dir.is_dir() or action_dir.name.startswith('_'):
                    continue
                
                action_name = self._extract_action_name(action_dir.name)
                trigger_file = action_dir / 'trigger_words.json'
                
                patterns = self._load_patterns_from_file(trigger_file)
                if patterns:
                    action_triggers[behavior_name][action_name] = patterns
        
        return action_triggers
    
    def _extract_behavior_name(self, dir_name: str) -> str:
        """Extract behavior name from directory name.
        
        Args:
            dir_name: Directory name
            
        Returns:
            Behavior name
        """
        return dir_name
    
    def _extract_action_name(self, dir_name: str) -> str:
        """Extract action name from directory name.
        
        Args:
            dir_name: Directory name
            
        Returns:
            Action name
        """
        return dir_name
    
    def _load_patterns_from_file(self, file_path: Path) -> List[str]:
        """Load trigger patterns from JSON file.
        
        Args:
            file_path: Path to trigger_words.json file
            
        Returns:
            List of patterns, or empty list if file doesn't exist or is invalid
        """
        if not file_path.exists():
            return []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            data = json.loads(content)
            return data.get('patterns', [])
        except (json.JSONDecodeError, IOError):
            return []

