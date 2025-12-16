from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING
import logging
from agile_bot.bots.base_bot.src.actions.activity_tracker import ActivityTracker
from agile_bot.bots.base_bot.src.bot.workspace import (
    get_base_actions_directory
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from agile_bot.bots.base_bot.src.bot.behavior import Behavior
    from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig


class Action:
    def __init__(self, base_action_config=None, behavior=None, activity_tracker: ActivityTracker = None, 
                 bot_name: str = None, action_name: str = None):
        # Priority: If base_action_config is provided, use it (preferred path)
        # Otherwise, if both bot_name and action_name are provided, use them to create BaseActionConfig
        if base_action_config is not None:
            # Use provided base_action_config
            if behavior is None:
                raise ValueError("behavior is required when base_action_config is provided")
            self.base_action_config = base_action_config
            self.behavior = behavior
            self.bot_name = behavior.bot_name
            self.action_name = base_action_config.action_name
            self._activity_tracker = activity_tracker
        elif bot_name is not None and action_name is not None:
            # Create BaseActionConfig from bot_name and action_name
            self.bot_name = bot_name
            self.behavior = behavior
            self.action_name = action_name
            from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig
            if behavior is None or behavior.bot_paths is None:
                raise ValueError("behavior and behavior.bot_paths are required when bot_name and action_name are provided")
            self.base_action_config = BaseActionConfig(action_name, behavior.bot_paths)
            self._activity_tracker = activity_tracker
        else:
            raise ValueError("Either base_action_config must be provided, or both bot_name and action_name must be provided")
        
        self.order = self.base_action_config.order
        self.action_class = self.base_action_config.custom_class
        self.instructions = self._load_and_merge_instructions()
    
    def _load_and_merge_instructions(self) -> Dict[str, Any]:
        # Handle case where base_action_config.instructions might be a dict or list
        base_instructions_raw = self.base_action_config.instructions
        if isinstance(base_instructions_raw, dict):
            # If it's a dict, extract the list from it (e.g., {"instructions": [...]})
            base_instructions = base_instructions_raw.get('instructions', [])
            if not isinstance(base_instructions, list):
                base_instructions = []
        elif isinstance(base_instructions_raw, list):
            base_instructions = base_instructions_raw.copy()
        else:
            base_instructions = []
        
        if self.behavior and hasattr(self.behavior, 'behavior_config'):
            behavior_config = self.behavior.behavior_config
            actions_workflow = getattr(behavior_config, 'actions_workflow', [])
            for action_dict in actions_workflow:
                if action_dict.get('name') == self.action_name:
                    behavior_instructions = action_dict.get('instructions', [])
                    if behavior_instructions:
                        # Handle case where behavior_instructions might be a dict or list
                        if isinstance(behavior_instructions, dict):
                            # Extract list from dict (e.g., {"behavior_instructions": [...]})
                            behavior_instructions_list = behavior_instructions.get('behavior_instructions', [])
                            if isinstance(behavior_instructions_list, list):
                                base_instructions.extend(behavior_instructions_list)
                        elif isinstance(behavior_instructions, list):
                            base_instructions.extend(behavior_instructions)
        
        merged = {
            'base_instructions': base_instructions
        }
        
        # Load clarification, strategy, and context file listing if available
        if self.behavior:
            context_instructions = []
            context_instructions.extend(self._inject_clarification_data(merged))
            context_instructions.extend(self._inject_strategy_data(merged))
            context_instructions.extend(self._inject_context_files(merged))
            
            if context_instructions:
                # Insert the context instructions at the beginning of base_instructions
                merged['base_instructions'] = context_instructions + merged['base_instructions']
        
        return merged
    
    def _inject_clarification_data(self, instructions: Dict[str, Any]) -> list:
        """Load and inject clarification.json data into instructions.
        
        Returns:
            List of instruction lines to add explaining clarification data
        """
        from agile_bot.bots.base_bot.src.actions.clarify.requirements_clarifications import RequirementsClarifications
        
        bot_paths = self.behavior.bot_paths
        clarification_data = RequirementsClarifications.load_all(bot_paths)
        
        if not clarification_data:
            return []
        
        instructions['clarification'] = clarification_data
        
        return [
            "",
            "**CLARIFICATION DATA AVAILABLE:**",
            "The 'clarification' data in your instructions contains answers to key questions and evidence gathered from previous clarification sessions across all behaviors.",
            "This data represents the context and requirements that have been established. Use this information to inform your decisions and ensure consistency with previously gathered requirements.",
            "The clarification data is organized by behavior name, with each behavior containing 'key_questions' (questions and answers) and 'evidence' (required and provided evidence)."
        ]
    
    def _inject_strategy_data(self, instructions: Dict[str, Any]) -> list:
        """Load and inject strategy.json data into instructions.
        
        Returns:
            List of instruction lines to add explaining strategy data
        """
        from agile_bot.bots.base_bot.src.actions.strategy.strategy_decision import StrategyDecision
        
        bot_paths = self.behavior.bot_paths
        strategy_data = StrategyDecision.load_all(bot_paths)
        
        if not strategy_data:
            return []
        
        instructions['strategy'] = strategy_data
        
        return [
            "",
            "**STRATEGY DATA AVAILABLE:**",
            "The 'strategy' data in your instructions contains planning decisions and assumptions made during previous strategy sessions across all behaviors.",
            "This data represents the strategic choices and assumptions that guide how work should be approached. Reference this data to ensure your actions align with established strategic decisions.",
            "The strategy data is organized by behavior name, with each behavior containing 'strategy_criteria' (decision criteria and decisions made), 'assumptions' (typical assumptions and assumptions made), and 'recommended_activities'."
        ]
    
    def _inject_context_files(self, instructions: Dict[str, Any]) -> list:
        """List and inject context file information into instructions.
        
        Returns:
            List of instruction lines to add explaining context files
        """
        bot_paths = self.behavior.bot_paths
        workspace_directory = bot_paths.workspace_directory
        docs_path = bot_paths.documentation_path
        context_dir = workspace_directory / docs_path / 'context'
        
        context_files = []
        if context_dir.exists():
            for file_path in context_dir.iterdir():
                if file_path.is_file():
                    context_files.append(file_path.name)
        
        if not context_files:
            return []
        
        instructions['context_files'] = context_files
        
        return [
            "",
            "**ORIGINAL CONTEXT FILES AVAILABLE:**",
            f"The following original context files are available in the docs/context/ folder: {', '.join(context_files)}",
            "These files contain the original input files, prompts, and source material provided at the start of the project.",
            "You can read these files directly from the docs/context/ folder when you need additional context or to reference the original requirements.",
            "Common files include 'input.txt' (original input), 'initial-context.md' (initial context), and other source materials."
        ]
    
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



