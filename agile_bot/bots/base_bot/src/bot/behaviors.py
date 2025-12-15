"""
Behaviors collection class.

Manages collection of Behavior objects and tracks current behavior.
State is persisted to behavior_action_state.json.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Iterator
from datetime import datetime
from agile_bot.bots.base_bot.src.bot.bot_config import BotConfig
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths


class Behaviors:
    """Collection of Behavior objects with state persistence.
    
    Instantiated with: BotConfig
    Properties:
        current: Behavior (persisted to behavior_action_state.json)
    Methods:
        find_by_name(): Find behavior by name
        next(): Get next behavior in sequence
        iterate(): Iterate all behaviors
        check_exists(): Check if behavior exists
        navigate_to(): Navigate to specific behavior
        close_current(): Close current behavior
        execute_current(): Execute current behavior
        save_state(): Save current behavior to behavior_action_state.json
        load_state(): Load current behavior from behavior_action_state.json
    """
    
    def __init__(self, bot_config: BotConfig, bot_paths: BotPaths | None = None):
        """Initialize Behaviors collection.
        
        Args:
            bot_config: BotConfig instance containing behaviors list
            bot_paths: BotPaths instance (required for state persistence)
            
        Note:
            Automatically loads state from behavior_action_state.json if it exists.
            Otherwise, sets first behavior as current.
        """
        self.bot_config = bot_config
        self.bot_name = bot_config.name
        self.bot_paths = bot_paths or BotPaths()
        self.bot_paths = bot_paths or bot_config.bot_paths
        
        # Create Behavior objects for each behavior in config
        # Import here to avoid circular import
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        
        self._behaviors: List['Behavior'] = []
        for behavior_name in bot_config.behaviors_list:
            behavior = Behavior(
                name=behavior_name,
                bot_name=self.bot_name,
                bot_paths=self.bot_paths,
                bot_instance=None  # Will be set by Bot if needed
            )
            self._behaviors.append(behavior)
        
        # Load state and set current behavior
        self._current_index: Optional[int] = None
        self.load_state()
    
    @property
    def current(self) -> Optional['Behavior']:
        """Get current behavior.
        
        Returns:
            Current Behavior object, or None if no behaviors exist.
        """
        if self._current_index is not None and 0 <= self._current_index < len(self._behaviors):
            return self._behaviors[self._current_index]
        return None
    
    def find_by_name(self, behavior_name: str) -> Optional[Behavior]:
        """Find behavior by name.
        
        Args:
            behavior_name: Name of behavior to find (e.g., 'shape', '1_shape')
            
        Returns:
            Behavior object if found, None otherwise.
        """
        for behavior in self._behaviors:
            # Match by exact name
            if behavior.name == behavior_name:
                return behavior
        return None
    
    def next(self) -> Optional['Behavior']:
        """Get next behavior in sequence.
        
        Returns:
            Next Behavior object, or None if at last behavior or no current behavior.
        """
        if self._current_index is None:
            return None
        
        next_index = self._current_index + 1
        if next_index < len(self._behaviors):
            return self._behaviors[next_index]
        return None
    
    def iterate(self) -> Iterator['Behavior']:
        """Iterate all behaviors.
        
        Yields:
            Behavior objects in order.
        """
        for behavior in self._behaviors:
            yield behavior
    
    def check_exists(self, behavior_name: str) -> bool:
        """Check if behavior exists.
        
        Args:
            behavior_name: Name of behavior to check
            
        Returns:
            True if behavior exists, False otherwise.
        """
        return self.find_by_name(behavior_name) is not None
    
    def navigate_to(self, behavior_name: str):
        """Navigate to specific behavior.
        
        Args:
            behavior_name: Name of behavior to navigate to
            
        Raises:
            ValueError: If behavior not found
        """
        behavior = self.find_by_name(behavior_name)
        if behavior is None:
            raise ValueError(f"Behavior '{behavior_name}' not found")
        
        # Find index of behavior
        for i, b in enumerate(self._behaviors):
            if b.name == behavior.name:
                self._current_index = i
                return
    
    def close_current(self):
        """Close current behavior (mark as complete and move to next).
        
        Note:
            This is a placeholder for future implementation.
            Currently just moves to next behavior.
        """
        if self._current_index is not None:
            # Move to next behavior if available
            next_behavior = self.next()
            if next_behavior:
                self._current_index += 1
                self.save_state()
    
    def execute_current(self, action_name: str = None, action_class=None, parameters: dict = None):
        """Execute current behavior.
        
        Domain Model: Execute current: Behavior
        
        Args:
            action_name: Optional action name to execute
            action_class: Optional action class to execute
            parameters: Optional parameters for action
            
        Returns:
            Result from behavior execution (with next behavior reminder injected if final behavior and final action)
            
        Raises:
            ValueError: If no current behavior
        """
        if self.current is None:
            raise ValueError("No current behavior to execute")
        
        result = None
        if action_name and action_class:
            # Execute action through behavior (which calls Actions.execute_current())
            result = self.current.execute_action(action_name, action_class, parameters)
        # If no action specified, behavior might have default execution
        # This is a placeholder for future implementation
        
        # Inject next behavior reminder if this is the final behavior AND final action
        if result is not None:
            result = self._inject_next_behavior_reminder(result, action_name)
        
        return result
    
    def _inject_next_behavior_reminder(self, result: dict, action_name: str = None) -> dict:
        """Inject next behavior reminder into instructions if current behavior is final and action is final.
        
        Domain Model: Inject next behavior reminder: Behavior
        
        Args:
            result: Result dict from action execution
            action_name: Name of the action that was executed (to check if it's final)
        """
        # Check if current behavior is final
        if not self._is_final_behavior():
            return result
        
        # Check if the executed action is the final action in the behavior
        if action_name and self.current:
            action_names = self.current.actions.names
            if action_names and action_name != action_names[-1]:
                # Not the final action, don't inject behavior reminder
                return result
        
        # Get next behavior reminder
        reminder = self._get_next_behavior_reminder()
        if not reminder:
            return result
        
        # Inject reminder into instructions if they exist
        if isinstance(result, dict) and 'instructions' in result:
            instructions = result['instructions']
            if isinstance(instructions, dict) and 'base_instructions' in instructions:
                base_instructions = instructions.get('base_instructions', [])
                if isinstance(base_instructions, list):
                    base_instructions = list(base_instructions)  # Make mutable copy
                    base_instructions.append("")
                    base_instructions.append("**NEXT BEHAVIOR REMINDER:**")
                    base_instructions.append(reminder)
                    instructions['base_instructions'] = base_instructions
                    result['instructions'] = instructions
        
        return result
    
    def _is_final_behavior(self) -> bool:
        """Check if current behavior is the final behavior."""
        try:
            if self.current is None:
                return False
            behaviors_list = self.bot_config.behaviors_list
            if behaviors_list and self.current.name == behaviors_list[-1]:
                return True
        except Exception:
            pass
        return False
    
    def _get_next_behavior_reminder(self) -> str:
        """Get reminder about next behavior if current is final."""
        try:
            next_behavior = self.next()
            if next_behavior:
                return (
                    f"After completing this behavior, the next behavior in sequence is `{next_behavior.name}`. "
                    f"When the user is ready to continue, remind them: 'The next behavior in sequence is `{next_behavior.name}`. "
                    f"Would you like to continue with `{next_behavior.name}` or work on a different behavior?'"
                )
        except Exception:
            pass
        return ""
    
    def save_state(self):
        """Save current behavior state to behavior_action_state.json.
        
        Only updates current_behavior field. Actions collection manages current_action.
        """
        if self.current is None or self.bot_paths is None:
            return
        
        workspace_dir = self.bot_paths.workspace_directory
        state_file = workspace_dir / 'behavior_action_state.json'
        
        # Load existing state to preserve current_action and completed_actions
        state_data = {}
        if state_file.exists():
            try:
                state_data = json.loads(state_file.read_text(encoding='utf-8'))
            except Exception:
                pass
        
        # Only update current behavior (Actions collection manages current_action)
        state_data['current_behavior'] = f'{self.bot_name}.{self.current.name}'
        state_data['timestamp'] = datetime.now().isoformat()
        
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
    
    def load_state(self):
        """Load current behavior state from behavior_action_state.json.
        
        If file doesn't exist or behavior not found, sets first behavior as current.
        """
        if self.bot_paths is None:
            if len(self._behaviors) > 0:
                self._current_index = 0
            return
        
        workspace_dir = self.bot_paths.workspace_directory
        state_file = workspace_dir / 'behavior_action_state.json'
        
        # If no state file, set first behavior as current
        if not state_file.exists() or len(self._behaviors) == 0:
            if len(self._behaviors) > 0:
                self._current_index = 0
            return
        
        try:
            state_data = json.loads(state_file.read_text(encoding='utf-8'))
            current_behavior_full = state_data.get('current_behavior', '')
            
            # Extract behavior name from format "bot_name.behavior_name"
            if current_behavior_full:
                parts = current_behavior_full.split('.')
                if len(parts) >= 2:
                    saved_behavior_name = '.'.join(parts[1:])  # Handle behaviors with dots in name
                    
                    # Find and set current behavior
                    for i, behavior in enumerate(self._behaviors):
                        if behavior.name == saved_behavior_name or behavior.name.endswith(f'_{saved_behavior_name}'):
                            self._current_index = i
                            return
            
            # If saved behavior not found, default to first
            if len(self._behaviors) > 0:
                self._current_index = 0
        except Exception:
            # If loading fails, default to first behavior
            if len(self._behaviors) > 0:
                self._current_index = 0
