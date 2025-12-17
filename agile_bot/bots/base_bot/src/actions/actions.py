from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Iterator, Dict, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from agile_bot.bots.base_bot.src.actions.action import Action
    from agile_bot.bots.base_bot.src.bot.behavior import Behavior


class Actions:
    def __init__(self, behavior: 'Behavior'):
        self.behavior = behavior
        
        actions_workflow = behavior._config.get("actions_workflow", {})
        actions_list = actions_workflow.get("actions", [])
        
        actions_list = sorted(actions_list, key=lambda x: x.get("order", 0))
        
        self._actions: List[Action] = []
        for action_dict in actions_list:
            action_name = action_dict.get("name", "")
            if action_name:
                action_instance = self._create_action_instance(
                    action_name=action_name,
                    behavior=behavior,
                    action_config=action_dict
                )
                self._actions.append(action_instance)
        
        self._current_index: Optional[int] = None
        self.load_state()
    
    def _create_action_instance(self, action_name: str, behavior: 'Behavior',
                               action_config: Dict[str, Any]) -> Action:
        import importlib
        from agile_bot.bots.base_bot.src.bot.workspace import get_base_actions_directory
        from agile_bot.bots.base_bot.src.utils import read_json_file
        
        custom_class = action_config.get("action_class") or action_config.get("custom_class")
        
        if not custom_class:
            base_actions_dir = get_base_actions_directory()
            # Normalize action name for path lookup (render_output -> render)
            normalized_action_name = 'render' if action_name == 'render_output' else action_name
            action_config_path = base_actions_dir / normalized_action_name / "action_config.json"
            base_config = read_json_file(action_config_path)
            custom_class = base_config.get("action_class") or base_config.get("custom_class")
        
        action_class_path = custom_class
        if not action_class_path:
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
                module_name = action_name
                action_class_name = action_name.title().replace('_', '') + 'Action'
                action_class_path = f"agile_bot.bots.base_bot.src.actions.{module_name}.{module_name}_action.{action_class_name}"
        
        module_path, class_name = action_class_path.rsplit(".", 1)
        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError as e:
            raise ValueError(
                f"Action '{action_name}' cannot be loaded: module '{module_path}' not found. "
                f"Expected path: {action_class_path}"
            ) from e
        
        try:
            action_class = getattr(module, class_name)
        except AttributeError as e:
            raise ValueError(
                f"Action '{action_name}' cannot be loaded: class '{class_name}' not found in module '{module_path}'. "
                f"Expected class: {action_class_path}"
            ) from e
        
        # Only pass action_name for base Action class; extended classes derive it from class name
        from agile_bot.bots.base_bot.src.actions.action import Action as BaseAction
        if action_class is BaseAction:
            return action_class(
                action_name=action_name,
                behavior=behavior,
                action_config=action_config
            )
        else:
            return action_class(
                behavior=behavior,
                action_config=action_config
            )
    
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
        action = self.find_by_name(name)
        if action:
            return action
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def navigate_to(self, action_name: str, out_of_order: bool = False):
        action = self.find_by_name(action_name)
        if action is None:
            raise ValueError(f"Action '{action_name}' not found")
        
        target_index = None
        for i, a in enumerate(self._actions):
            if a.action_name == action_name:
                target_index = i
                self._current_index = i
                break
        
        if target_index is None:
            return
        
        if out_of_order and self.behavior.bot_paths:
            workspace_dir = self.behavior.bot_paths.workspace_directory
            state_file = workspace_dir / 'behavior_action_state.json'
            
            state_data = json.loads(state_file.read_text(encoding='utf-8'))
            completed_actions = state_data.get('completed_actions', [])
            
            if completed_actions:
                action_names_after_target = [a.action_name for a in self._actions[target_index + 1:]]
                
                expected_behavior_prefix = f'{self.behavior.bot_name}.{self.behavior.name}.'
                filtered_completed = []
                for completed_action in completed_actions:
                    action_state = completed_action.get('action_state', '')
                    if action_state.startswith(expected_behavior_prefix):
                        completed_action_name = action_state.split('.')[-1]
                        if completed_action_name not in action_names_after_target:
                            filtered_completed.append(completed_action)
                    else:
                        filtered_completed.append(completed_action)
                
                state_data['completed_actions'] = filtered_completed
                state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
        
        self.save_state()
    
    def close_current(self):
        if self.behavior.bot_paths is None:
            return
        
        if self._current_index is None:
            return
        
        current_action_obj = self.current
        if current_action_obj is None:
            return
        
        workspace_dir = self.behavior.bot_paths.workspace_directory
        state_file = workspace_dir / 'behavior_action_state.json'
        
        expected_behavior = f'{self.behavior.bot_name}.{self.behavior.name}'
        
        # Load existing state or create new
        if state_file.exists():
            state_data = json.loads(state_file.read_text(encoding='utf-8'))
        else:
            state_data = {
                'current_behavior': expected_behavior,
                'current_action': '',
                'completed_actions': [],
                'timestamp': datetime.now().isoformat()
            }
        
        if 'current_behavior' not in state_data:
            state_data['current_behavior'] = expected_behavior
        
        if 'completed_actions' not in state_data:
            state_data['completed_actions'] = []
        
        action_to_complete = current_action_obj.action_name
        action_state = f'{self.behavior.bot_name}.{self.behavior.name}.{action_to_complete}'
        
        if 'completed_actions' not in state_data:
            state_data['completed_actions'] = []
        
        completed_actions_list = state_data.get('completed_actions', [])
        
        is_already_completed = any(
            a.get('action_state') == action_state 
            for a in completed_actions_list
        )
        
        new_completed_action_entry = {
            'action_state': action_state,
            'timestamp': datetime.now().isoformat()
        }
        if not is_already_completed:
            new_completed_actions = completed_actions_list + [new_completed_action_entry]
            state_data['completed_actions'] = new_completed_actions
        else:
            state_data['completed_actions'] = completed_actions_list
        
        if 'completed_actions' not in state_data:
            state_data['completed_actions'] = completed_actions_list if completed_actions_list else []
        
        next_action_obj = self.next()
        if next_action_obj:
            self._current_index += 1
        
        current_action_obj = self.current
        if current_action_obj:
            state_data['current_action'] = f'{self.behavior.bot_name}.{self.behavior.name}.{current_action_obj.action_name}'
        
        state_data['timestamp'] = datetime.now().isoformat()
        
        if 'completed_actions' not in state_data:
            state_data['completed_actions'] = []
        elif not isinstance(state_data.get('completed_actions'), list):
            existing = state_data.get('completed_actions')
            state_data['completed_actions'] = [existing] if existing else []
        
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
    
    def forward_to_current(self) -> Optional['Action']:
        self.load_state()
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
        if self.is_final_action():
            return self._get_next_behavior_reminder()
        
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
        try:
            if not self.behavior or not self.behavior.bot:
                return ""
            behavior_names = self.behavior.bot.behaviors.names
            if not behavior_names:
                return ""
            try:
                current_index = behavior_names.index(self.behavior.name)
                if current_index + 1 < len(behavior_names):
                    next_behavior_name = behavior_names[current_index + 1]
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
        
        expected_behavior = f'{self.behavior.bot_name}.{self.behavior.name}'
        
        # Load existing state or create new
        if state_file.exists():
            state_data = json.loads(state_file.read_text(encoding='utf-8'))
        else:
            state_data = {
                'current_behavior': expected_behavior,
                'current_action': '',
                'completed_actions': [],
                'timestamp': datetime.now().isoformat()
            }
        
        if 'completed_actions' not in state_data:
            state_data['completed_actions'] = []
        
        # Always update current_behavior to reflect the current behavior
        state_data['current_behavior'] = expected_behavior
        
        current_action_obj = self.current
        if current_action_obj:
            state_data['current_action'] = f'{self.behavior.bot_name}.{self.behavior.name}.{current_action_obj.action_name}'
            state_data['timestamp'] = datetime.now().isoformat()
        
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
    
    def load_state(self):
        if self.behavior.bot_paths is None or len(self._actions) == 0:
            if len(self._actions) > 0:
                self._current_index = 0
            return
        
        workspace_dir = self.behavior.bot_paths.workspace_directory
        state_file = workspace_dir / 'behavior_action_state.json'
        
        if not state_file.exists():
            if len(self._actions) > 0:
                self._current_index = 0
            return
        
        try:
            state_data = json.loads(state_file.read_text(encoding='utf-8'))
            current_action_full = state_data.get('current_action', '')
            current_behavior_full = state_data.get('current_behavior', '')
            
            expected_behavior = f'{self.behavior.bot_name}.{self.behavior.name}'
            if current_behavior_full != expected_behavior:
                if len(self._actions) > 0:
                    self._current_index = 0
                return
            
            if current_action_full:
                parts = current_action_full.split('.')
                if len(parts) >= 3:
                    saved_action_name = parts[-1]
                    
                    for i, action in enumerate(self._actions):
                        if action.action_name == saved_action_name:
                            self._current_index = i
                            return
            
            completed_actions = state_data.get('completed_actions', [])
            if completed_actions:
                last_completed_action_name = None
                expected_behavior_prefix = f'{self.behavior.bot_name}.{self.behavior.name}.'
                for completed_action in reversed(completed_actions):
                    action_state = completed_action.get('action_state', '')
                    if action_state.startswith(expected_behavior_prefix):
                        last_completed_action_name = action_state.split('.')[-1]
                        break
                
                if last_completed_action_name:
                    for i, action in enumerate(self._actions):
                        if action.action_name == last_completed_action_name:
                            if i + 1 < len(self._actions):
                                self._current_index = i + 1
                            else:
                                self._current_index = i
                            return
            
            if len(self._actions) > 0:
                self._current_index = 0
        except Exception:
            if len(self._actions) > 0:
                self._current_index = 0
    
    def _save_completed_action(self, action_name: str):
        if self.behavior.bot_paths is None:
            return
        
        workspace_dir = self.behavior.bot_paths.workspace_directory
        state_file = workspace_dir / 'behavior_action_state.json'
        
        # Load existing state or create new
        if state_file.exists():
            state_data = json.loads(state_file.read_text(encoding='utf-8'))
        else:
            state_data = {
                'current_behavior': f'{self.behavior.bot_name}.{self.behavior.name}',
                'current_action': '',
                'completed_actions': [],
                'timestamp': datetime.now().isoformat()
            }
        
        if 'completed_actions' not in state_data:
            state_data['completed_actions'] = []
        
        action_state = f'{self.behavior.bot_name}.{self.behavior.name}.{action_name}'
        
        if not any(a.get('action_state') == action_state for a in state_data['completed_actions']):
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
        
        state_data = json.loads(state_file.read_text(encoding='utf-8'))
        completed_actions = state_data.get('completed_actions', [])
        
        action_state = f'{self.behavior.bot_name}.{self.behavior.name}.{action_name}'
        return any(
            action.get('action_state') == action_state
            for action in completed_actions
        )
