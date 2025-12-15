from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING
from agile_bot.bots.base_bot.src.actions.activity_tracker import ActivityTracker
from agile_bot.bots.base_bot.src.bot.workspace import (
    get_base_actions_directory
)

if TYPE_CHECKING:
    from agile_bot.bots.base_bot.src.bot.behavior import Behavior
    from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig


class Action:
    def __init__(self, base_action_config=None, behavior=None, activity_tracker: ActivityTracker = None, 
                 bot_name: str = None, action_name: str = None):
        if bot_name is not None and action_name is not None:
            self.bot_name = bot_name
            self.behavior = behavior
            self.action_name = action_name
            from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig
            self.base_action_config = BaseActionConfig(action_name, behavior.bot_paths)
            self._activity_tracker = activity_tracker
        else:
            self.base_action_config = base_action_config
            self.behavior = behavior
            self.bot_name = behavior.bot_name
            self.action_name = base_action_config.action_name
            self._activity_tracker = activity_tracker
        
        self.order = self.base_action_config.order
        self.action_class = self.base_action_config.custom_class
        self.instructions = self._load_and_merge_instructions()
    
    def _load_and_merge_instructions(self) -> Dict[str, Any]:
        base_instructions = self.base_action_config.instructions.copy()
        
        if self.behavior and hasattr(self.behavior, 'behavior_config'):
            behavior_config = self.behavior.behavior_config
            actions_workflow = getattr(behavior_config, 'actions_workflow', [])
            for action_dict in actions_workflow:
                if action_dict.get('name') == self.action_name:
                    behavior_instructions = action_dict.get('instructions', [])
                    if behavior_instructions:
                        base_instructions.extend(behavior_instructions)
        
        merged = {
            'base_instructions': base_instructions
        }
        
        return merged
    
    @property
    def tracker(self) -> ActivityTracker:
        if self._activity_tracker is None:
            self._activity_tracker = ActivityTracker(self.behavior.bot_paths, self.bot_name)
        return self._activity_tracker

    @property
    def base_actions_dir(self) -> Path:
        return get_base_actions_directory(bot_directory=self.behavior.bot_paths.bot_directory)
    
    @property
    def working_dir(self) -> Path:
        return self.behavior.bot_paths.workspace_directory
    
    @property
    def bot_dir(self) -> Path:
        return self.behavior.bot_paths.bot_directory
    
    
    def track_activity_on_start(self):
        self.tracker.track_start(self.bot_name, self.behavior.name, self.action_name)
    
    def track_activity_on_completion(self, outputs: dict = None, duration: int = None):
        self.tracker.track_completion(self.bot_name, self.behavior.name, self.action_name, outputs, duration)
    
    def execute(self, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        self.track_activity_on_start()
        result = self.do_execute(parameters or {})
        self.track_activity_on_completion(outputs=result)
        return result
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement do_execute()")



