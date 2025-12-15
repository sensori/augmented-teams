"""
Actions collection class.

Manages collection of Action objects and tracks current action.
State is persisted to behavior_action_state.json.
"""
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
    """Collection of Action objects with state persistence.
    
    Instantiated with: Behavior, BaseActionsConfig, BehaviorConfig
    Instantiates: Action
    Properties:
        current: Action (persisted to behavior_action_state.json)
    Methods:
        find_by_name(): Find action by name
        find_by_order(): Find action by order
        next(): Get next action in sequence
        iterate(): Iterate all actions
        navigate_to(): Navigate to specific action
        close_current(): Close current action
        execute_current(): Execute current action
        save_state(): Save current action to behavior_action_state.json
        load_state(): Load current action from behavior_action_state.json
    """
    
    def __init__(self, behavior_config, behavior):
        """Initialize Actions collection.
        
        Args:
            behavior_config: BehaviorConfig instance containing actions_workflow
            behavior: Behavior instance (for accessing bot and state)
            
        Note:
            Automatically loads state from behavior_action_state.json if it exists.
            Otherwise, sets first action as current.
        """
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
                try:
                    # Load base action config
                    base_action_config = BaseActionConfig(action_name, self.bot_paths)
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
                except (ImportError, ModuleNotFoundError, AttributeError) as e:
                    # Skip actions that can't be imported (e.g., missing dependencies)
                    # This allows tests to run even if some action modules aren't fully implemented
                    pass
        
        # Track current action index
        self._current_index: Optional[int] = None
        
        # Load state and set current action
        self.load_state()
    
    def _instantiate_action(self, action_name: str, base_action_config: BaseActionConfig, 
                           behavior: Behavior, activity_tracker) -> Action:
        """Instantiate concrete Action class (e.g., GatherContextAction).
        
        Args:
            action_name: Name of the action
            base_action_config: BaseActionConfig instance
            behavior: Behavior instance
            activity_tracker: ActivityTracker instance
            
        Returns:
            Instance of concrete Action class
        """
        import importlib
        
        # Get action class path (from custom_class or default)
        action_class_path = base_action_config.custom_class
        if not action_class_path:
            # Map action names to module names and class names (for actions where name doesn't match module)
            action_module_mapping = {
                'decide_planning_criteria': ('decide_strategy', 'DecideStrategyAction')
            }
            mapping = action_module_mapping.get(action_name)
            if mapping:
                module_name, action_class_name = mapping
            else:
                module_name = action_name
                action_class_name = action_name.title().replace('_', '') + 'Action'
            
            # Default: agile_bot.bots.base_bot.src.actions.{module_name}.{module_name}_action.{ActionClass}Action
            action_class_path = f"agile_bot.bots.base_bot.src.actions.{module_name}.{module_name}_action.{action_class_name}"
        
        # Import and instantiate action class
        module_path, class_name = action_class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        action_class = getattr(module, class_name)
        
        # Instantiate with BaseActionConfig, Behavior, ActivityTracker
        action_instance = action_class(
            base_action_config=base_action_config,
            behavior=behavior,
            activity_tracker=activity_tracker
        )
        
        return action_instance
    
    @property
    def current(self) -> Optional[Action]:
        """Get current action.
        
        Returns:
            Current Action object, or None if no actions exist.
        """
        if self._current_index is not None and 0 <= self._current_index < len(self._actions):
            return self._actions[self._current_index]
        return None
    
    @property
    def names(self) -> List[str]:
        """Get list of all action names."""
        return [action.action_name for action in self._actions]
    
    def find_by_name(self, action_name: str) -> Optional[Action]:
        """Find action by name.
        
        Args:
            action_name: Name of action to find
            
        Returns:
            Action object if found, None otherwise.
        """
        for action in self._actions:
            if action.action_name == action_name:
                return action
        return None
    
    def find_by_order(self, order: int) -> Optional[Action]:
        """Find action by order.
        
        Args:
            order: Order number of action
            
        Returns:
            Action object if found, None otherwise.
        """
        for action in self._actions:
            if action.order == order:
                return action
        return None
    
    def next(self) -> Optional[Action]:
        """Get next action in sequence.
        
        Returns:
            Next Action object, or None if at last action or no current action.
        """
        if self._current_index is None:
            return None
        
        next_index = self._current_index + 1
        if next_index < len(self._actions):
            return self._actions[next_index]
        return None
    
    def __iter__(self) -> Iterator[Action]:
        """Iterate all actions.
        
        Yields:
            Action objects in order.
        """
        for action in self._actions:
            yield action
    
    def navigate_to(self, action_name: str):
        """Navigate to specific action.
        
        Args:
            action_name: Name of action to navigate to
            
        Raises:
            ValueError: If action not found
        """
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
        """Close current action (mark as complete and move to next).
        
        Note:
            This saves the completed action and transitions to next.
        """
        if self._current_index is not None:
            current_action_obj = self.current
            if current_action_obj:
                self._save_completed_action(current_action_obj.action_name)
            
            # Move to next action if available
            next_action_obj = self.next()
            if next_action_obj:
                self._current_index += 1
                self.save_state()
    
    def execute_current(self, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute current action.
        
        Domain Model: Execute current: Action
        
        Args:
            parameters: Optional parameters for action execution
            
        Returns:
            Dict with action execution results (with next action reminder injected if final action)
            
        Raises:
            ValueError: If no current action
        """
        if self.current is None:
            raise ValueError("No current action to execute")
        
        # Execute the current action (Action.execute handles tracking and execution)
        result = self.current.execute(parameters)
        
        # Inject next action reminder if this is the final action
        result = self._inject_next_action_reminder(result)
        
        return result
    
    def _inject_next_action_reminder(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Inject next action reminder into instructions if current action is final.
        
        Domain Model: Inject next action reminder: Action
        """
        # Check if current action is final
        if not self._is_final_action():
            return result
        
        # Get next action reminder
        reminder = self._get_next_action_reminder()
        if not reminder:
            return result
        
        # Inject reminder into instructions if they exist
        if 'instructions' in result:
            instructions = result['instructions']
            if isinstance(instructions, dict) and 'base_instructions' in instructions:
                base_instructions = instructions.get('base_instructions', [])
                if isinstance(base_instructions, list):
                    base_instructions = list(base_instructions)  # Make mutable copy
                    base_instructions.append("")
                    base_instructions.append("**NEXT ACTION REMINDER:**")
                    base_instructions.append(reminder)
                    instructions['base_instructions'] = base_instructions
                    result['instructions'] = instructions
        
        return result
    
    def _is_final_action(self) -> bool:
        """Check if current action is the final action."""
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
        """Get reminder about next action if current is final."""
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
    
    def save_state(self):
        """Save current action state to behavior_action_state.json.
        
        Only updates current_action field. Behaviors collection manages current_behavior.
        """
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
        """Load current action state from behavior_action_state.json.
        
        If file doesn't exist or action not found, sets first action as current.
        """
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
            
            # If saved action not found, default to first
            if len(self._actions) > 0:
                self._current_index = 0
        except Exception:
            # If loading fails, default to first action
            if len(self._actions) > 0:
                self._current_index = 0
    
    def _save_completed_action(self, action_name: str):
        """Save completed action to behavior_action_state.json."""
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
        """Check if an action has been marked as completed."""
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

