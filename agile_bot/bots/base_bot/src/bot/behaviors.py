from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Optional, Iterator, Tuple, Dict, Any, TYPE_CHECKING
from datetime import datetime
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths

if TYPE_CHECKING:
    from agile_bot.bots.base_bot.src.bot.bot import BotResult

logger = logging.getLogger(__name__)


class Behaviors:
    def __init__(self, bot_name: str, bot_paths: BotPaths):
        self.bot_name = bot_name
        self.bot_paths = bot_paths
        
        from agile_bot.bots.base_bot.src.bot.behavior import Behavior
        from agile_bot.bots.base_bot.src.bot.behavior_config import BehaviorConfig
        
        self._behaviors: List['Behavior'] = []
        # Discover behaviors from folder structure and load their order from behavior.json
        behaviors_dir = self.bot_paths.bot_directory / 'behaviors'
        if behaviors_dir.exists():
            behavior_orders = []
            for item in behaviors_dir.iterdir():
                if item.is_dir() and not item.name.startswith('_') and not item.name.startswith('.'):
                    # Verify it has a behavior.json
                    if (item / 'behavior.json').exists():
                        # Load behavior config to get order
                        try:
                            behavior_config = BehaviorConfig(item.name, self.bot_paths, self.bot_name)
                            order = behavior_config._config.get('order', 999)  # Default to end if no order
                            behavior = Behavior(
                                name=item.name,
                                bot_name=self.bot_name,
                                bot_paths=self.bot_paths,
                                bot_instance=None
                            )
                            behavior_orders.append((order, behavior))
                        except Exception:
                            # If config load fails, skip this behavior
                            continue
            
            # Sort by order from behavior.json
            behavior_orders.sort(key=lambda x: x[0])
            self._behaviors = [behavior for _, behavior in behavior_orders]
        
        self._current_index: Optional[int] = None
        self.load_state()
    
    @property
    def current(self) -> Optional['Behavior']:
        if self._current_index is not None and 0 <= self._current_index < len(self._behaviors):
            return self._behaviors[self._current_index]
        return None
    
    @property
    def names(self) -> List[str]:
        """Return list of behavior names."""
        return [b.name for b in self._behaviors]
    
    @property
    def first(self) -> Optional['Behavior']:
        """Return first behavior."""
        return self._behaviors[0] if self._behaviors else None
    
    def is_empty(self) -> bool:
        """Check if behaviors collection is empty."""
        return len(self._behaviors) == 0
    
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
            if self.names and self.current.name == self.names[-1]:
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
                        if behavior.name == saved_behavior_name:
                            self._current_index = i
                            return
            
            # If saved behavior not found, default to first
            if len(self._behaviors) > 0:
                self._current_index = 0
        except Exception:
            # If loading fails, default to first behavior
            if len(self._behaviors) > 0:
                self._current_index = 0
    
    def initialize_state(self, confirmed_behavior: str):
        """Initialize behavior_action_state.json with confirmed behavior and first action."""
        if self.bot_paths is None:
            raise ValueError("Cannot initialize state without bot_paths")
        
        behavior_obj = self.find_by_name(confirmed_behavior)
        if behavior_obj is None:
            raise ValueError(
                f"Behavior '{confirmed_behavior}' not found. "
                f"Available behaviors: {', '.join(self.names)}."
            )
        
        workspace_dir = self.bot_paths.workspace_directory
        state_file = workspace_dir / 'behavior_action_state.json'
        
        # Get first action from behavior
        action_names = behavior_obj.actions.names
        first_action = action_names[0] if action_names else 'clarify'
        
        # Set current behavior
        self.navigate_to(confirmed_behavior)
        
        # Initialize state file
        state_data = {
            'current_behavior': f'{self.bot_name}.{behavior_obj.name}',
            'current_action': f'{self.bot_name}.{behavior_obj.name}.{first_action}',
            'completed_actions': [],
            'timestamp': datetime.now().isoformat()
        }
        
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
    
    def get_entry_state_result(self) -> 'BotResult':
        """Get result for entry state when no state file exists."""
        from agile_bot.bots.base_bot.src.bot.bot import BotResult
        
        return BotResult(
            status='requires_confirmation',
            behavior='',
            action='',
            data={
                'message': (
                    "**ENTRY STATE**\n\n"
                    "No behavior state found. Please select a behavior to start:\n\n"
                    f"{chr(10).join(f'- {b}' for b in self.names)}\n\n"
                    "Provide 'confirmed_behavior' in parameters to proceed."
                ),
                'behaviors': self.names,
                'requires_confirmation': True
            }
        )
    
    
    def does_requested_match_current(self, requested_behavior: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Check if requested behavior matches current behavior sequence."""
        if not self.current:
            return (True, None, None)
        
        current_behavior = self.current.name
        requested_behavior_obj = self.find_by_name(requested_behavior)
        requested_matched = requested_behavior_obj.name if requested_behavior_obj else None
        
        next_behavior_obj = self.next()
        expected_next = next_behavior_obj.name if next_behavior_obj else None
        
        if requested_matched is None:
            matches = False
        elif requested_matched == current_behavior:
            matches = True
        elif expected_next is None:
            matches = True
        else:
            matches = (requested_matched == expected_next)
        
        logger.debug(
            f"Behavior order check: requested={requested_behavior} ({requested_matched}), "
            f"current={current_behavior}, "
            f"expected_next={expected_next}, matches={matches}"
        )
        
        return (matches, current_behavior, expected_next)
    