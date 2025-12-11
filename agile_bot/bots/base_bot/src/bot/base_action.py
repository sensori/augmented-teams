from pathlib import Path
from typing import Dict, Any, Optional
from agile_bot.bots.base_bot.src.state.activity_tracker import ActivityTracker
from agile_bot.bots.base_bot.src.state.workspace import (
    get_workspace_directory, 
    get_bot_directory,
    get_python_workspace_root,
    get_base_actions_directory
)


class BaseAction:
    
    def __init__(self, bot_name: str, behavior: str, bot_directory: Path, action_name: str):
        """Initialize BaseAction.
        
        Args:
            bot_name: Name of the bot
            behavior: Name of the behavior
            bot_directory: Directory where bot code lives
            action_name: Name of this action
            
        Note:
            workspace_directory is auto-detected from get_workspace_directory()
        """
        self.bot_name = bot_name
        self.behavior = behavior
        self.bot_directory = Path(bot_directory)
        self.action_name = action_name
    
    @property
    def workspace_directory(self) -> Path:
        """Get workspace directory (auto-detected from environment/agent.json)."""
        return get_workspace_directory()

    @property
    def tracker(self):
        """Get activity tracker (lazy initialization)."""
        if not hasattr(self, '_tracker'):
            self._tracker = ActivityTracker(self.workspace_directory, self.bot_name)
        return self._tracker

    @property
    def base_actions_dir(self) -> Path:
        """Get base actions directory.
        
        Returns path to base_actions folder, checking bot_directory first,
        then falling back to base_bot's base_actions folder.
        
        For tests: Always create base_actions in bot_directory to ensure isolation.
        For production: Falls back to shared base_bot/base_actions if bot doesn't have its own.
        """
        return get_base_actions_directory(bot_directory=self.bot_directory)
    

    @property
    def working_dir(self) -> Path:
        """Get workspace directory where content files are created."""
        return get_workspace_directory()
    
    @property
    def bot_dir(self) -> Path:
        """Get bot directory where bot code lives."""
        return self.bot_directory
    
    
    def track_activity_on_start(self):
        self.tracker.track_start(self.bot_name, self.behavior, self.action_name)
    
    def track_activity_on_completion(self, outputs: dict = None, duration: int = None):
        self.tracker.track_completion(self.bot_name, self.behavior, self.action_name, outputs, duration)
    
    def execute(self, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Template method that automatically tracks activity. Override do_execute() in subclasses."""
        # Track start
        self.track_activity_on_start()
        
        # Execute action logic (subclass implements this)
        result = self.do_execute(parameters or {})
        
        # Inject next behavior reminder if this is the final action
        result = self._inject_next_behavior_reminder(result)
        
        # Track completion
        self.track_activity_on_completion(outputs=result)
        
        return result
    
    def _inject_next_behavior_reminder(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Inject next behavior reminder into instructions if this is the final action."""
        # Check if this is the final action
        if not self._is_final_action():
            return result
        
        # Get next behavior reminder
        reminder = self._get_next_behavior_reminder()
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
                    base_instructions.append("**NEXT BEHAVIOR REMINDER:**")
                    base_instructions.append(reminder)
                    instructions['base_instructions'] = base_instructions
                    result['instructions'] = instructions
        
        return result
    
    def _is_final_action(self) -> bool:
        """Check if this is the final action in the behavior's workflow."""
        try:
            from agile_bot.bots.base_bot.src.bot.bot import load_workflow_states_and_transitions
            states, _ = load_workflow_states_and_transitions(self.bot_directory)
            if states and self.action_name == states[-1]:
                return True
        except Exception as e:
            # Log exception for debugging but don't fail
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Failed to check if action is final: {e}")
            pass
        return False
    
    def _get_next_behavior_reminder(self) -> str:
        """Get reminder about next behavior if this is the final action."""
        try:
            from agile_bot.bots.base_bot.src.utils import read_json_file
            
            # Load bot config to get behavior sequence
            # Try config/bot_config.json first, then bot_config.json
            bot_config_file = self.bot_directory / 'config' / 'bot_config.json'
            if not bot_config_file.exists():
                bot_config_file = self.bot_directory / 'bot_config.json'
            
            if not bot_config_file.exists():
                return ""
            
            bot_config = read_json_file(bot_config_file)
            behaviors = bot_config.get('behaviors', [])
            
            if not behaviors:
                return ""
            
            # Find current behavior index and next behavior
            try:
                current_index = behaviors.index(self.behavior)
                if current_index + 1 < len(behaviors):
                    next_behavior = behaviors[current_index + 1]
                    return (
                        f"After completing this behavior, the next behavior in sequence is `{next_behavior}`. "
                        f"When the user is ready to continue, remind them: 'The next behavior in sequence is `{next_behavior}`. "
                        f"Would you like to continue with `{next_behavior}` or work on a different behavior?'"
                    )
            except ValueError:
                # Current behavior not in list
                pass
            
        except Exception:
            # If anything fails, just return empty (non-blocking)
            pass
        
        return ""
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Override this in subclasses to implement action logic."""
        raise NotImplementedError("Subclasses must implement do_execute()")
    
    def finalize_and_transition(self, next_action: Optional[str] = None):
        class TransitionResult:
            pass
        
        result = TransitionResult()
        result.next_action = next_action
        return result

