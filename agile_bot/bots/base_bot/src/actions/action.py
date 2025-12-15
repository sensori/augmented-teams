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
    """Base class for all action implementations.
    
    Domain Model:
        Instantiated with: BaseActionConfig, Behavior, ActivityTracker
        Properties: Instructions (from BaseActionConfig, Behavior), action class (from BaseActionConfig), order (from BaseActionConfig)
        Methods: Execute (instructions, Instructions), Track activity start, Track activity completion
    """
    
    def __init__(self, base_action_config=None, behavior=None, activity_tracker: ActivityTracker = None, 
                 bot_name: str = None, action_name: str = None):
        """Initialize Action.
        
        Domain Model: Instantiated with: BaseActionConfig, Behavior, ActivityTracker
        
        Supports both new signature (base_action_config, behavior, activity_tracker) 
        and old signature (bot_name, behavior, action_name) for backward compatibility.
        
        Args:
            base_action_config: BaseActionConfig instance with action config (new signature)
            behavior: Behavior instance
            activity_tracker: Optional ActivityTracker instance (will be created if not provided)
            bot_name: Bot name (old signature - for backward compatibility)
            action_name: Action name (old signature - for backward compatibility)
        """
        # Handle old signature (bot_name, behavior, action_name)
        if bot_name is not None and action_name is not None:
            self.bot_name = bot_name
            self.behavior = behavior
            self.action_name = action_name
            # Create BaseActionConfig from action_name
            from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig
            self.base_action_config = BaseActionConfig(action_name, behavior.bot_paths)
            self._activity_tracker = activity_tracker
        else:
            # New signature (base_action_config, behavior, activity_tracker)
            self.base_action_config = base_action_config
            self.behavior = behavior
            self.bot_name = behavior.bot_name
            self.action_name = base_action_config.action_name
            self._activity_tracker = activity_tracker
        
        # Properties from BaseActionConfig
        self.order = self.base_action_config.order
        self.action_class = self.base_action_config.custom_class
        
        # Load and merge instructions from BaseActionConfig and Behavior
        # Domain Model: Instructions: BaseActionConfig, Behavior
        self.instructions = self._load_and_merge_instructions()
    
    def _load_and_merge_instructions(self) -> Dict[str, Any]:
        """Load and merge instructions from BaseActionConfig and Behavior.
        
        Domain Model: Instructions: BaseActionConfig, Behavior
        
        Returns:
            Merged instructions dict with base_instructions from BaseActionConfig
            and behavior-specific instructions from Behavior config.
        """
        # Start with base instructions from BaseActionConfig (always a list)
        base_instructions = self.base_action_config.instructions.copy()
        
        # Merge with behavior-specific instructions if available
        if self.behavior and hasattr(self.behavior, 'behavior_config'):
            behavior_config = self.behavior.behavior_config
            # Get behavior-specific action config from actions_workflow
            actions_workflow = getattr(behavior_config, 'actions_workflow', [])
            for action_dict in actions_workflow:
                if action_dict.get('name') == self.action_name:
                    # Merge behavior-specific instructions (also a list)
                    behavior_instructions = action_dict.get('instructions', [])
                    if behavior_instructions:
                        base_instructions.extend(behavior_instructions)
        
        merged = {
            'base_instructions': base_instructions
        }
        
        return merged
    
    @property
    def tracker(self) -> ActivityTracker:
        """Get activity tracker (lazy initialization)."""
        if self._activity_tracker is None:
            self._activity_tracker = ActivityTracker(self.behavior.bot_paths, self.bot_name)
        return self._activity_tracker

    @property
    def base_actions_dir(self) -> Path:
        """Get base actions directory.
        
        Returns path to base_actions folder, checking bot_directory first,
        then falling back to base_bot's base_actions folder.
        
        For tests: Always create base_actions in bot_directory to ensure isolation.
        For production: Falls back to shared base_bot/base_actions if bot doesn't have its own.
        """
        return get_base_actions_directory(bot_directory=self.behavior.bot_paths.bot_directory)
    
    @property
    def working_dir(self) -> Path:
        """Get workspace directory where content files are created."""
        return self.behavior.bot_paths.workspace_directory
    
    @property
    def bot_dir(self) -> Path:
        """Get bot directory where bot code lives."""
        return self.behavior.bot_paths.bot_directory
    
    
    def track_activity_on_start(self):
        self.tracker.track_start(self.bot_name, self.behavior.name, self.action_name)
    
    def track_activity_on_completion(self, outputs: dict = None, duration: int = None):
        self.tracker.track_completion(self.bot_name, self.behavior.name, self.action_name, outputs, duration)
    
    def execute(self, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute this action.
        
        Domain Model: Execute: instructions, Instructions
        
        Template method that automatically tracks activity. Override do_execute() in subclasses.
        
        Args:
            parameters: Optional parameters for action execution
            
        Returns:
            Dict with action execution results
        """
        # Track start
        self.track_activity_on_start()
        
        # Execute action logic (subclass implements this)
        result = self.do_execute(parameters or {})
        
        # Track completion
        self.track_activity_on_completion(outputs=result)
        
        return result
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Override this in subclasses to implement action logic."""
        raise NotImplementedError("Subclasses must implement do_execute()")



