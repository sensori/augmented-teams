from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Iterator, Dict, Any, TYPE_CHECKING
from datetime import datetime

from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig

if TYPE_CHECKING:
    from agile_bot.bots.base_bot.src.actions.action import Action
    from agile_bot.bots.base_bot.src.bot.behavior import Behavior


class Actions:
    def __init__(self, behavior_config, behavior):
        self.behavior_config = behavior_config
        self.behavior = behavior
        self.bot_name = behavior.bot_name
        self.bot_paths = behavior.bot_paths
        
        # Extract actions from behavior_config
        actions_workflow = getattr(behavior_config, "actions_workflow", [])
        if isinstance(actions_workflow, list):
            actions_list = actions_workflow
        else:
            # Handle case where actions_workflow is a dict with 'actions' key
            actions_list = actions_workflow.get('actions', []) if isinstance(actions_workflow, dict) else []
        
        # Instantiate Action objects for each action in config
        # Action will handle loading BaseActionConfig and merging with Behavior config
        self._actions: List[Action] = []
        for action_dict in actions_list:
            action_name = action_dict.get("name", "")
            if action_name:
                # Load base action config
                base_action_config = BaseActionConfig(action_name, self.bot_paths)
                # Override order from behavior.json if present (behavior.json is authoritative)
                if "order" in action_dict:
                    base_action_config._config["order"] = action_dict["order"]
                # Create ActivityTracker
                from agile_bot.bots.base_bot.src.actions.activity_tracker import ActivityTracker
                workspace_dir = self.bot_paths.workspace_directory
                activity_tracker = ActivityTracker(self.bot_paths, self.bot_name)
                
                # Instantiate concrete Action class (e.g., GatherContextAction)
                action_instance = self._instantiate_action(
                    action_name=action_name,
                    base_action_config=base_action_config,
                    behavior=behavior,
                    activity_tracker=activity_tracker
                )
                self._actions.append(action_instance)
        
        # Track current action index
        self._current_index: Optional[int] = None
        
        # Load state and set current action
        self.load_state()
    
    def _instantiate_action(self, action_name: str, base_action_config: BaseActionConfig, 
                           behavior: Behavior, activity_tracker) -> Action:
        import importlib
        
        # Get action class path (from custom_class or default)
        action_class_path = base_action_config.custom_class
        if not action_class_path:
            # Map action names to module names and class names
            action_module_mapping = {
                'clarify': ('clarify', 'clarify_action', 'ClarifyContextAction'),
                'strategy': ('strategy', 'strategy_action', 'StrategyAction'),
                'decide_strategy': ('strategy', 'strategy_action', 'StrategyAction'),
                'build': ('build', 'build_action', 'BuildKnowledgeAction'),
                'build_knowledge': ('build', 'build_action', 'BuildKnowledgeAction'),
                'validate': ('validate', 'validate_action', 'ValidateRulesAction'),
                'render': ('render', 'render_action', 'RenderOutputAction'),
                'render_output': ('render', 'render_action', 'RenderOutputAction'),
            }
            mapping = action_module_mapping.get(action_name)
            if mapping:
                module_name, module_file, action_class_name = mapping
                action_class_path = f"agile_bot.bots.base_bot.src.actions.{module_name}.{module_file}.{action_class_name}"
            else:
                # Default: try to construct from action name
                module_name = action_name
                action_class_name = action_name.title().replace('_', '') + 'Action'
                action_class_path = f"agile_bot.bots.base_bot.src.actions.{module_name}.{module_name}_action.{action_class_name}"
        
        # Import and instantiate action class
        module_path, class_name = action_class_path.rsplit(".", 1)
        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError as e:
            raise ValueError(
                f"Action '{action_name}' cannot be loaded: module '{module_path}' not found. "
                f"Action classes must exist for all configured actions. "
                f"Expected path: {action_class_path}"
            ) from e
        
        try:
            action_class = getattr(module, class_name)
        except AttributeError as e:
            raise ValueError(
                f"Action '{action_name}' cannot be loaded: class '{class_name}' not found in module '{module_path}'. "
                f"Action classes must exist for all configured actions."
            ) from e
        
        # Instantiate with BaseActionConfig, Behavior, ActivityTracker
        try:
            action_instance = action_class(
                base_action_config=base_action_config,
                behavior=behavior,
                activity_tracker=activity_tracker
            )
        except Exception as e:
            raise ValueError(
                f"Action '{action_name}' cannot be instantiated: {e}. "
                f"Action classes must be properly implemented for all configured actions."
            ) from e
        
        return action_instance
    
    @property
    def current(self) -> Optional[Action]:
        if self._current_index is not None and 0 <= self._current_index < len(self._actions):
            return self._actions[self._current_index]
        return None
    
    @property
    def names(self) -> List[str]:
        return [action.action_name for action in self._actions]
    
    def find_by_name(self, action_name: str) -> Optional[Action]:
        for action in self._actions:
            if action.action_name == action_name:
                return action
        return None
    
    def find_by_order(self, order: int) -> Optional[Action]:
        for action in self._actions:
            if action.order == order:
                return action
        return None
    
    def next(self) -> Optional[Action]:
        if self._current_index is None:
            return None
        
        next_index = self._current_index + 1
        if next_index < len(self._actions):
            return self._actions[next_index]
        return None
    
    def __iter__(self) -> Iterator[Action]:
        for action in self._actions:
            yield action
    
    def __getattr__(self, name: str):
        """Allow accessing actions as attributes (e.g., actions.clarify, actions.build())."""
        # Check if it's an action name
        action = self.find_by_name(name)
        if action:
            return action
        
        # Default behavior for unknown attributes
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def navigate_to(self, action_name: str):
        action = self.find_by_name(action_name)
        if action is None:
            raise ValueError(f"Action '{action_name}' not found")
        
        # Find index of action
        for i, a in enumerate(self._actions):
            if a.action_name == action_name:
                self._current_index = i
                self.save_state()
                return
    
    def close_current(self):
        if self._current_index is not None:
            current_action_obj = self.current
            if current_action_obj:
                self._save_completed_action(current_action_obj.action_name)
            
            # Move to next action if available
            next_action_obj = self.next()
            if next_action_obj:
                self._current_index += 1
                self.save_state()
    
    def forward_to_current(self) -> Optional['Action']:
        """Forward to current action - loads state, returns current Action object."""
        # Load state to sync with persisted state
        self.load_state()
        
        # Return current action object (CLI/MCP will execute it)
        return self.current
    
    def is_final_action(self) -> bool:
        try:
            if self.current is None:
                return False
            action_names = self.names
            if action_names and self.current.action_name == action_names[-1]:
                return True
        except Exception:
            pass
        return False
    
    def _get_next_action_reminder(self) -> str:
        """Get reminder for next action, or next behavior if this is the final action."""
        # If this is the final action, get next behavior reminder instead
        if self.is_final_action():
            return self._get_next_behavior_reminder()
        
        # Otherwise, get next action reminder
        try:
            next_action = self.next()
            if next_action:
                return (
                    f"After completing this action, the next action in sequence is `{next_action.action_name}`. "
                    f"When ready to continue, proceed with `{next_action.action_name}`."
                )
        except Exception:
            pass
        return ""
    
    def _get_next_behavior_reminder(self) -> str:
        """Internal: Get reminder for next behavior (only called when on final action)."""
        try:
            if not self.behavior or not self.behavior.bot:
                return ""
            # Get behavior names from behaviors collection
            behavior_names = self.behavior.bot.behaviors.names
            if not behavior_names:
                return ""
            # Find current behavior index
            try:
                current_index = behavior_names.index(self.behavior.name)
                if current_index + 1 < len(behavior_names):
                    next_behavior_name = behavior_names[current_index + 1]
                    # Get first action of next behavior
                    next_behavior = self.behavior.bot.behaviors.find_by_name(next_behavior_name)
                    first_action_name = None
                    if next_behavior and next_behavior.actions.names:
                        first_action_name = next_behavior.actions.names[0]
                    
                    if first_action_name:
                        return (
                            f"After completing this action, the next behavior in sequence is `{next_behavior_name}`. "
                            f"The first action in `{next_behavior_name}` is `{first_action_name}`. "
                            f"When the user is ready to continue, remind them: 'The next behavior in sequence is `{next_behavior_name}`. "
                            f"Would you like to continue with `{next_behavior_name}` or work on a different behavior?'"
                        )
                    else:
                        return (
                            f"After completing this behavior, the next behavior in sequence is `{next_behavior_name}`. "
                            f"When the user is ready to continue, remind them: 'The next behavior in sequence is `{next_behavior_name}`. "
                            f"Would you like to continue with `{next_behavior_name}` or work on a different behavior?'"
                        )
            except (ValueError, IndexError):
                pass
        except Exception:
            pass
        return ""
    
    def save_state(self):
        if self.current is None or self.behavior.bot_paths is None:
            return
        
        workspace_dir = self.behavior.bot_paths.workspace_directory
        state_file = workspace_dir / 'behavior_action_state.json'
        
        # Load existing state to preserve current_behavior and completed_actions
        state_data = {}
        if state_file.exists():
            try:
                state_data = json.loads(state_file.read_text(encoding='utf-8'))
            except Exception:
                pass
        
        # Only update current action (Behaviors collection manages current_behavior)
        current_action_obj = self.current
        if current_action_obj:
            state_data['current_action'] = f'{self.bot_name}.{self.behavior.name}.{current_action_obj.action_name}'
            state_data['timestamp'] = datetime.now().isoformat()
        
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
    
    def load_state(self):
        if self.bot_paths is None or len(self._actions) == 0:
            if len(self._actions) > 0:
                self._current_index = 0
            return
        
        workspace_dir = self.bot_paths.workspace_directory
        state_file = workspace_dir / 'behavior_action_state.json'
        
        # If no state file, set first action as current
        if not state_file.exists():
            if len(self._actions) > 0:
                self._current_index = 0
            return
        
        try:
            state_data = json.loads(state_file.read_text(encoding='utf-8'))
            current_action_full = state_data.get('current_action', '')
            current_behavior_full = state_data.get('current_behavior', '')
            
            # Check if current_behavior matches this behavior
            expected_behavior = f'{self.bot_name}.{self.behavior.name}'
            if current_behavior_full != expected_behavior:
                # Behavior doesn't match - set first action as current
                if len(self._actions) > 0:
                    self._current_index = 0
                return
            
            # Extract action name from format "bot.behavior.action" -> "action"
            if current_action_full:
                parts = current_action_full.split('.')
                if len(parts) >= 3:
                    saved_action_name = parts[-1]  # Last part is action name
                    
                    # Find and set current action
                    for i, action in enumerate(self._actions):
                        if action.action_name == saved_action_name:
                            self._current_index = i
                            return
            
            # If current_action is missing, fall back to completed_actions
            # Find the last completed action and set current to the next action after it
            completed_actions = state_data.get('completed_actions', [])
            if completed_actions:
                # Find the last completed action for this behavior
                last_completed_action_name = None
                expected_behavior_prefix = f'{self.bot_name}.{self.behavior.name}.'
                for completed_action in reversed(completed_actions):
                    action_state = completed_action.get('action_state', '')
                    if action_state.startswith(expected_behavior_prefix):
                        last_completed_action_name = action_state.split('.')[-1]
                        break
                
                # If we found a completed action, set current to the next action after it
                if last_completed_action_name:
                    for i, action in enumerate(self._actions):
                        if action.action_name == last_completed_action_name:
                            # Set to next action if available, otherwise stay at last completed
                            if i + 1 < len(self._actions):
                                self._current_index = i + 1
                            else:
                                self._current_index = i
                            return
            
            # If saved action not found and no completed actions, default to first
            if len(self._actions) > 0:
                self._current_index = 0
        except Exception:
            # If loading fails, default to first action
            if len(self._actions) > 0:
                self._current_index = 0
    
    def _save_completed_action(self, action_name: str):
        if self.behavior.bot_paths is None:
            return
        
        workspace_dir = self.behavior.bot_paths.workspace_directory
        state_file = workspace_dir / 'behavior_action_state.json'
        
        # Load existing state
        state_data = {}
        if state_file.exists():
            try:
                state_data = json.loads(state_file.read_text(encoding='utf-8'))
            except Exception:
                pass
        
        # Add completed action
        if 'completed_actions' not in state_data:
            state_data['completed_actions'] = []
        
        action_state = f'{self.bot_name}.{self.behavior.name}.{action_name}'
        state_data['completed_actions'].append({
            'action_state': action_state,
            'timestamp': datetime.now().isoformat()
        })
        
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
    
    def is_action_completed(self, action_name: str) -> bool:
        if self.behavior.bot_paths is None:
            return False
        
        workspace_dir = self.behavior.bot_paths.workspace_directory
        state_file = workspace_dir / 'behavior_action_state.json'
        
        if not state_file.exists():
            return False
        
        try:
            state_data = json.loads(state_file.read_text(encoding='utf-8'))
            completed_actions = state_data.get('completed_actions', [])
            
            # Check if this action is in completed_actions for this behavior
            action_state = f'{self.bot_name}.{self.behavior.name}.{action_name}'
            return any(
                action.get('action_state') == action_state
                for action in completed_actions
            )
        except Exception:
            return False

