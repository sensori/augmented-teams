from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING, List
import logging
from agile_bot.bots.base_bot.src.actions.activity_tracker import ActivityTracker
from agile_bot.bots.base_bot.src.bot.workspace import (
    get_base_actions_directory
)
from agile_bot.bots.base_bot.src.utils import read_json_file

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from agile_bot.bots.base_bot.src.bot.behavior import Behavior


class Action:
    def __init__(self, behavior: 'Behavior', action_config: Dict[str, Any] = None,
                 action_name: str = None):
        """
        Args:
            behavior: The behavior this action belongs to
            action_config: Optional config dict from behavior.json
            action_name: Optional name (only used when loading from JSON via Actions._create_action_instance)
        """
        self.behavior = behavior
        
        # Derive action_name if not provided (for base Action class)
        if action_name is None:
            action_name = self._derive_action_name_from_class()
        
        # Store derived/provided name for config loading and property
        self._action_name = action_name
        
        from agile_bot.bots.base_bot.src.actions.activity_tracker import ActivityTracker
        self._activity_tracker = ActivityTracker(behavior.bot_paths, behavior.bot_name)
        
        # Use property to get final action name (may be overridden by subclass)
        # This ensures ValidateCodeFilesAction uses 'validate' instead of 'validate_code_files'
        final_action_name = self.action_name
        
        bot_directory = behavior.bot_paths.bot_directory if behavior and behavior.bot_paths else None
        base_actions_dir = get_base_actions_directory(bot_directory)
        base_config_path = base_actions_dir / final_action_name / "action_config.json"
        
        self._base_config = read_json_file(base_config_path)
        self._base_config['name'] = final_action_name
        
        if action_config:
            if "order" in action_config:
                self._base_config["order"] = action_config["order"]
            behavior_instructions = action_config.get("instructions", [])
            base_instructions = self._base_config.get("instructions", [])
            self._base_config["instructions"] = self._merge_instructions(
                base_instructions, behavior_instructions
            )
            self._base_config["custom_class"] = action_config.get("action_class") or action_config.get("custom_class")
            if "next_action" in action_config:
                self._base_config["next_action"] = action_config["next_action"]
        
        self.order = self._base_config.get("order", 0)
        self.next_action = self._base_config.get("next_action")
        self.action_class = self._base_config.get("action_class") or self._base_config.get("custom_class")
        self.workflow = self._base_config.get("workflow", True)
    
    def _derive_action_name_from_class(self) -> str:
        """Derive action name from class name for base Action class."""
        import re
        class_name = self.__class__.__name__
        
        if class_name.endswith('Action'):
            base_name = class_name[:-6]
        else:
            base_name = class_name
        
        # Convert CamelCase to snake_case
        snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', base_name).lower()
        
        # Normalize special cases
        normalization_map = {
            'render_output': 'render',
            'build_knowledge': 'build',
            'validate_rules': 'validate',
            'clarify_context': 'clarify',
        }
        
        return normalization_map.get(snake_case, snake_case)
    
    @property
    def action_name(self) -> str:
        """Action name - derived from class or loaded from config."""
        return self._action_name
    
    @action_name.setter
    def action_name(self, value: str):
        raise AttributeError("action_name is read-only. It's derived from the class name.")
    
    def _merge_instructions(self, base_instructions, behavior_instructions) -> List:
        if isinstance(base_instructions, list) and isinstance(behavior_instructions, list):
            return base_instructions + behavior_instructions
        elif isinstance(base_instructions, list):
            return base_instructions + [behavior_instructions] if behavior_instructions else base_instructions
        else:
            return behavior_instructions if behavior_instructions else base_instructions
    
    
    def _inject_clarification_data(self, instructions: Dict[str, Any]) -> list:
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
        bot_paths = self.behavior.bot_paths
        workspace_directory = bot_paths.workspace_directory
        docs_path = bot_paths.documentation_path
        context_dir = workspace_directory / docs_path / 'context'
        
        context_files = []
        if context_dir.exists() and context_dir.is_dir():
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
    
    def _inject_status_update_breadcrumbs(self, instructions: Dict[str, Any]) -> list:
        """Inject workflow progress breadcrumbs showing current behavior/action and remaining work."""
        if not self.behavior.bot:
            return []
        
        try:
            behaviors = self.behavior.bot.behaviors
            current_behavior = behaviors.current
            if not current_behavior:
                return []
            
            workspace_dir = self.behavior.bot_paths.workspace_directory
            state_file = workspace_dir / 'behavior_action_state.json'
            
            completed_actions = []
            if state_file.exists():
                import json
                state_data = json.loads(state_file.read_text(encoding='utf-8'))
                completed_actions = state_data.get('completed_actions', [])
            
            bot_name = self.behavior.bot_name
            all_behaviors = behaviors.names
            current_behavior_name = current_behavior.name
            
            completed_behaviors = []
            remaining_behaviors = []
            current_action_name = None
            remaining_actions_in_current = []
            
            for behavior_name in all_behaviors:
                behavior_obj = behaviors.find_by_name(behavior_name)
                if not behavior_obj:
                    continue
                
                behavior_prefix = f'{bot_name}.{behavior_name}.'
                behavior_actions = behavior_obj.actions.names
                completed_for_behavior = [
                    action.get('action_state', '').split('.')[-1]
                    for action in completed_actions
                    if action.get('action_state', '').startswith(behavior_prefix)
                ]
                
                if behavior_name == current_behavior_name:
                    current_action = current_behavior.actions.current
                    current_action_name = current_action.action_name if current_action else None
                    
                    if current_action_name:
                        current_index = behavior_actions.index(current_action_name) if current_action_name in behavior_actions else -1
                        remaining_actions_in_current = behavior_actions[current_index + 1:] if current_index >= 0 else behavior_actions
                else:
                    all_completed = len(completed_for_behavior) == len(behavior_actions) and len(behavior_actions) > 0
                    if all_completed:
                        completed_behaviors.append(behavior_name)
                    else:
                        remaining_behaviors.append({
                            'name': behavior_name,
                            'actions': behavior_actions,
                            'completed': completed_for_behavior
                        })
            
            lines = [
                "**WORKFLOW PROGRESS:**",
                ""
            ]
            
            if completed_behaviors:
                for behavior_name in completed_behaviors:
                    lines.append(f"  - [x] {behavior_name}")
            
            lines.append(f"  - [ ] {current_behavior_name}")
            if current_action_name:
                lines.append(f"       - [ ] {current_action_name}")
            for action_name in remaining_actions_in_current:
                lines.append(f"       - [ ] {action_name}")
            
            for remaining in remaining_behaviors:
                lines.append(f"  - [ ] {remaining['name']}")
                for action_name in remaining['actions']:
                    if action_name in remaining['completed']:
                        lines.append(f"    - [x] {action_name}")
                    else:
                        lines.append(f"    - [ ] {action_name}")
            
            next_action = remaining_actions_in_current[0] if remaining_actions_in_current else None
            if next_action:
                lines.append("")
                lines.append(f"**Next step:** To proceed, run: `{bot_name}_cli --behavior {current_behavior_name} --action {next_action}`")
            elif remaining_behaviors:
                next_behavior = remaining_behaviors[0]['name']
                next_behavior_obj = behaviors.find_by_name(next_behavior)
                if next_behavior_obj and next_behavior_obj.actions.names:
                    first_action = next_behavior_obj.actions.names[0]
                    lines.append("")
                    lines.append(f"**Next step:** To proceed, run: `{bot_name}_cli --behavior {next_behavior} --action {first_action}`")
            
            lines.append("")
            return lines
            
        except Exception as e:
            logger.debug(f"Failed to generate workflow progress breadcrumbs: {e}")
            return []
    
    @property
    def instructions(self) -> Dict[str, Any]:
        """Generate instructions with workflow breadcrumbs and context data."""
        base_instructions = self._base_config.get("instructions", [])
        merged = {
            'base_instructions': base_instructions if isinstance(base_instructions, list) else []
        }
        
        # Inject workflow progress breadcrumbs FIRST (before other context)
        context_instructions = []
        context_instructions.extend(self._inject_status_update_breadcrumbs(merged))
        try:
            context_instructions.extend(self._inject_clarification_data(merged))
            context_instructions.extend(self._inject_strategy_data(merged))
        except FileNotFoundError:
            pass
        context_instructions.extend(self._inject_context_files(merged))
        
        if context_instructions:
            merged['base_instructions'] = context_instructions + merged['base_instructions']
        
        return merged
    
    @property
    def tracker(self) -> ActivityTracker:
        return self._activity_tracker

    @property
    def base_actions_dir(self) -> Path:
        return get_base_actions_directory()
    
    @property
    def working_dir(self) -> Path:
        return self.behavior.bot_paths.workspace_directory
    
    @property
    def bot_dir(self) -> Path:
        return self.behavior.bot_paths.bot_directory
    
    
    def track_activity_on_start(self):
        self.tracker.track_start(self.behavior.bot_name, self.behavior.name, self.action_name)
    
    def track_activity_on_completion(self, outputs: dict = None, duration: int = None):
        self.tracker.track_completion(self.behavior.bot_name, self.behavior.name, self.action_name, outputs, duration)
    
    def execute(self, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        self.track_activity_on_start()
        result = self.do_execute(parameters or {})
        self.track_activity_on_completion(outputs=result)
        result = self._inject_reminders_if_final(result)
        return result
    
    def _inject_reminders_if_final(self, result: Dict[str, Any]) -> Dict[str, Any]:
        if not self.behavior or not self.behavior.actions:
            return result
        
        action_names = self.behavior.actions.names
        if not action_names or self.action_name != action_names[-1]:
            return result
        
        if not self.behavior.bot:
            if hasattr(self.behavior, 'actions') and hasattr(self.behavior.actions, 'behavior'):
                behavior_from_actions = self.behavior.actions.behavior
                if hasattr(behavior_from_actions, 'bot_paths'):
                    from agile_bot.bots.base_bot.src.bot.behaviors import Behaviors
                    logger.debug(f"Behavior {self.behavior.name} has no bot reference - reminder will be skipped. "
                               f"This may indicate the behavior was not created through Bot.__init__")
                return result
        
        reminder = self.behavior.actions._get_next_behavior_reminder()
        if not reminder:
            logger.debug(f"Reminder is empty for action {self.action_name} in behavior {self.behavior.name if self.behavior else None}. "
                        f"behavior.bot={self.behavior.bot if self.behavior else None}, "
                        f"behavior.bot.behaviors.names={self.behavior.bot.behaviors.names if self.behavior and self.behavior.bot else None}")
            return result
        
        if 'instructions' not in result:
            result['instructions'] = {}
        
        instructions = result['instructions']
        
        if not isinstance(instructions, dict):
            if isinstance(instructions, list):
                instructions = {'base_instructions': instructions}
            else:
                instructions = {}
            result['instructions'] = instructions
        
        base_instructions = instructions.get('base_instructions', [])
        
        if not base_instructions and isinstance(self.instructions, dict) and 'base_instructions' in self.instructions:
            base_instructions = list(self.instructions['base_instructions'])
            instructions['base_instructions'] = base_instructions
        
        if not isinstance(base_instructions, list):
            base_instructions = []
            instructions['base_instructions'] = base_instructions
        
        base_instructions = list(base_instructions)
        base_instructions.append("")
        base_instructions.append("**NEXT BEHAVIOR REMINDER:**")
        base_instructions.append(reminder)
        instructions['base_instructions'] = base_instructions
        result['instructions'] = instructions
        
        return result
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement do_execute()")
