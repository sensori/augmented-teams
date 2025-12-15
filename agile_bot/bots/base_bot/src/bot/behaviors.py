from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Iterator
from datetime import datetime
from agile_bot.bots.base_bot.src.bot.bot_config import BotConfig
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths


class Behaviors:
    def __init__(self, bot_config: BotConfig, bot_paths: BotPaths | None = None):
        self.bot_config = bot_config
        self.bot_name = bot_config.name
        self.bot_paths = bot_paths or BotPaths()
        self.bot_paths = bot_paths or bot_config.bot_paths
        
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        
        self._behaviors: List['Behavior'] = []
        for behavior_name in bot_config.behaviors_list:
            behavior = Behavior(
                name=behavior_name,
                bot_name=self.bot_name,
                bot_paths=self.bot_paths,
                bot_instance=None
            )
            self._behaviors.append(behavior)
        
        self._current_index: Optional[int] = None
        self.load_state()
    
    @property
    def current(self) -> Optional['Behavior']:
        if self._current_index is not None and 0 <= self._current_index < len(self._behaviors):
            return self._behaviors[self._current_index]
        return None
    
    def find_by_name(self, behavior_name: str) -> Optional['Behavior']:
        for behavior in self._behaviors:
            if behavior.name == behavior_name:
                return behavior
        return None
    
    def next(self) -> Optional['Behavior']:
        if self._current_index is None:
            return None
        
        next_index = self._current_index + 1
        if next_index < len(self._behaviors):
            return self._behaviors[next_index]
        return None
    
    def __iter__(self) -> Iterator['Behavior']:
        """Iterate all behaviors."""
        for behavior in self._behaviors:
            yield behavior
    
    def check_exists(self, behavior_name: str) -> bool:
        return self.find_by_name(behavior_name) is not None
    
    def navigate_to(self, behavior_name: str):
        behavior = self.find_by_name(behavior_name)
        if behavior is None:
            raise ValueError(f"Behavior '{behavior_name}' not found")
        
        for i, b in enumerate(self._behaviors):
            if b.name == behavior.name:
                self._current_index = i
                return
    
    def close_current(self):
        if self._current_index is not None:
            next_behavior = self.next()
            if next_behavior:
                self._current_index += 1
                self.save_state()
    
    def execute_current(self, action_name: str = None, action_class=None, parameters: dict = None):
        if self.current is None:
            raise ValueError("No current behavior to execute")
        
        result = None
        if action_name and action_class:
            result = self.current.execute_action(action_name, action_class, parameters)
        
        if result is not None:
            result = self._inject_next_behavior_reminder(result, action_name)
        
        return result
    
    def _inject_next_behavior_reminder(self, result: dict, action_name: str = None) -> dict:
        if not self._is_final_behavior():
            return result
        
        if action_name and self.current:
            action_names = self.current.actions.names
            if action_names and action_name != action_names[-1]:
                return result
        
        reminder = self._get_next_behavior_reminder()
        if not reminder:
            return result
        
        if isinstance(result, dict) and 'instructions' in result:
            instructions = result['instructions']
            if isinstance(instructions, dict) and 'base_instructions' in instructions:
                base_instructions = instructions.get('base_instructions', [])
                if isinstance(base_instructions, list):
                    base_instructions = list(base_instructions)
                    base_instructions.append("")
                    base_instructions.append("**NEXT BEHAVIOR REMINDER:**")
                    base_instructions.append(reminder)
                    instructions['base_instructions'] = base_instructions
                    result['instructions'] = instructions
        
        return result
    
    def _is_final_behavior(self) -> bool:
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
        if self.current is None or self.bot_paths is None:
            return
        
        workspace_dir = self.bot_paths.workspace_directory
        state_file = workspace_dir / 'behavior_action_state.json'
        
        state_data = {}
        if state_file.exists():
            try:
                state_data = json.loads(state_file.read_text(encoding='utf-8'))
            except Exception:
                pass
        
        state_data['current_behavior'] = f'{self.bot_name}.{self.current.name}'
        state_data['timestamp'] = datetime.now().isoformat()
        
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
    
    def load_state(self):
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
