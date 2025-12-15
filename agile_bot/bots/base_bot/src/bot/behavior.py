"""
Behavior class module.

Encapsulates behavior configuration and collaborators.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from agile_bot.bots.base_bot.src.bot.behavior_config import BehaviorConfig
from agile_bot.bots.base_bot.src.actions.guardrails import Guardrails
from agile_bot.bots.base_bot.src.actions.content import Content
from agile_bot.bots.base_bot.src.actions.validate_rules.rules import Rules
from agile_bot.bots.base_bot.src.actions.actions import Actions
from agile_bot.bots.base_bot.src.bot.trigger_words import TriggerWords
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths

if TYPE_CHECKING:
    from agile_bot.bots.base_bot.src.bot.bot import BotResult


class Behavior:
    """Behavior aggregates config and collaborators.
    
    Domain Model:
        Instantiated with: Name, BotConfig
        Instantiates: Guardrails, Content, Rules, Actions, TriggerWords
        Properties: folder, guardrails, content, rules, actions
        Method: matches_trigger
        Properties from BehaviorConfig: description, goal, inputs, outputs
    """

    def __init__(self, name: str, bot_name: str, bot_paths: BotPaths, bot_instance=None):
        self.name = name
        self.bot_name = bot_name
        self.bot_paths = bot_paths
        self.bot = bot_instance  # Reference to parent Bot instance

        # Load behavior configuration via BehaviorConfig
        self.behavior_config = BehaviorConfig(self.name, self.bot_paths)
        self.description = self.behavior_config.description
        self.goal = self.behavior_config.goal
        self.inputs = self.behavior_config.inputs
        self.outputs = self.behavior_config.outputs

        # Instantiate collaborators (per domain model)
        self.guardrails = Guardrails(self.behavior_config)
        self.content = Content(self.behavior_config)
        self.rules_collection = Rules(behavior=self, bot_paths=self.bot_paths)
        self.actions = Actions(self.behavior_config, self)
        self.trigger_words = TriggerWords(self.behavior_config)

    @property
    def folder(self) -> Path:
        """Get behavior's folder path in behaviors directory."""
        return self.bot_paths.bot_directory / "behaviors" / self.name

    @property
    def rules(self):
        """Get all rules for this behavior (delegated to Rules collection).
        
        Domain Model: rules: Rules
        """
        return list(self.rules_collection.iterate())

    def matches_trigger(self, text: str) -> bool:
        """Determine if provided text matches configured trigger words/patterns."""
        return self.trigger_words.matches(text)
    
    @staticmethod
    def find_behavior_folder(bot_directory: Path, bot_name: str, behavior_name: str) -> Path:
        """Find behavior folder by name, handling numbered prefixes.
        
        Args:
            bot_directory: Bot directory path
            bot_name: Bot name (unused, kept for compatibility)
            behavior_name: Behavior name (e.g., 'shape', 'discovery')
            
        Returns:
            Path to behavior folder (e.g., '1_shape', '5_exploration')
            
        Raises:
            FileNotFoundError: If behavior folder not found
        """
        behaviors_dir = bot_directory / 'behaviors'
        if not behaviors_dir.exists():
            raise FileNotFoundError(f"Behavior folder not found: {behavior_name}")
        
        # First try exact match
        exact_folder = behaviors_dir / behavior_name
        if exact_folder.exists() and exact_folder.is_dir():
            return exact_folder
        
        # Then try numbered prefix (e.g., '1_shape' for 'shape')
        for folder in behaviors_dir.iterdir():
            if folder.is_dir():
                # Check if folder name ends with behavior_name (e.g., '1_shape' ends with 'shape')
                if folder.name.endswith(f'_{behavior_name}') or folder.name == behavior_name:
                    return folder
        
        raise FileNotFoundError(f"Behavior folder not found: {behavior_name}")

    # ============================================================================
    # LEGACY METHODS - Not in domain model, kept for refactoring reference
    # ============================================================================
    
    # @property
    # def scanners(self) -> List[type]:
    #     """Get all scanners across all rules for this behavior."""
    #     return self.rules_collection.scanners()

    # def navigate_to_action(self, action_name: str, parameters: Dict[str, Any] = None, out_of_order: bool = False) -> "BotResult":
    #     """Navigate to a specific action and execute it."""
    #     self.actions.navigate_to(action_name)
    #     if not hasattr(self, action_name):
    #         raise AttributeError(f"Behavior {self.name} does not have action method '{action_name}'")
    #     action_method = getattr(self, action_name)
    #     result = action_method(parameters=parameters)
    #     if result is None:
    #         raise RuntimeError(f"Action method '{action_name}' returned None instead of BotResult")
    #     if not (result.data and result.data.get("requires_confirmation")):
    #         self.actions.save_state()
    #     if self.actions.is_action_completed(action_name):
    #         self.actions.close_current()
    #     return result

    # def execute_action(self, action_name: str, action_class, parameters: Dict[str, Any] = None) -> "BotResult":
    #     """Execute an action."""
    #     if self.actions.current != action_name:
    #         self.actions.navigate_to(action_name)
    #     working_dir = self.bot_paths.workspace_directory
    #     self.actions.save_state()
    #     action = action_class(bot_name=self.bot_name, behavior=self, action_name=action_name)
    #     data = action.execute(parameters)
    #     if data is None:
    #         data = {}
    #     if working_dir:
    #         data["working_dir"] = str(working_dir)
    #     from agile_bot.bots.base_bot.src.bot.bot import BotResult
    #     result = BotResult(status="completed", behavior=self.name, action=action_name, data=data)
    #     if not (result.data and result.data.get("requires_confirmation")):
    #         self.actions.save_state()
    #     if self.actions.is_action_completed(action_name):
    #         self.actions.close_current()
    #     return result

    # def initialize_workspace(self, parameters: Dict[str, Any] = None) -> "BotResult":
    #     """Initialize workspace - currently just forwards to gather_context."""
    #     return self.gather_context(parameters)

    # def gather_context(self, parameters: Dict[str, Any] = None) -> "BotResult":
    #     from agile_bot.bots.base_bot.src.bot.gather_context_action import GatherContextAction
    #     return self.execute_action("gather_context", GatherContextAction, parameters)

    # def decide_planning_criteria(self, parameters: Dict[str, Any] = None) -> "BotResult":
    #     from agile_bot.bots.base_bot.src.bot.planning_action import PlanningAction
    #     return self.execute_action("decide_planning_criteria", PlanningAction, parameters)

    # def build_knowledge(self, parameters: Dict[str, Any] = None) -> "BotResult":
    #     from agile_bot.bots.base_bot.src.bot.build_knowledge_action import BuildKnowledgeAction
    #     return self.execute_action("build_knowledge", BuildKnowledgeAction, parameters)

    # def render_output(self, parameters: Dict[str, Any] = None) -> "BotResult":
    #     from agile_bot.bots.base_bot.src.bot.render_output_action import RenderOutputAction
    #     return self.execute_action("render_output", RenderOutputAction, parameters)

    # def _get_action_class(self, action_name: str, default_action_class):
    #     """Get action class for a given action, checking for custom override in behavior.json."""
    #     try:
    #         behavior_file = self.folder / "behavior.json"
    #         if behavior_file.exists():
    #             behavior_config = read_json_file(behavior_file)
    #             actions_workflow = behavior_config.get("actions_workflow", {})
    #             actions = actions_workflow.get("actions", [])
    #             for action_config in actions:
    #                 if action_config.get("name") == action_name:
    #                     action_class_path = action_config.get("action_class")
    #                     if action_class_path:
    #                         module_path, class_name = action_class_path.rsplit(".", 1)
    #                         module = importlib.import_module(module_path)
    #                         custom_action_class = getattr(module, class_name)
    #                         return custom_action_class
    #     except (FileNotFoundError, Exception) as e:
    #         logger.debug(f"Could not load custom action class for {action_name}: {e}")
    #     return default_action_class

    # def validate_rules(self, parameters: Dict[str, Any] = None) -> "BotResult":
    #     from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
    #     action_class = self._get_action_class("validate_rules", ValidateRulesAction)
    #     return self.execute_action("validate_rules", action_class, parameters)

    # def test_validate(self, parameters: Dict[str, Any] = None) -> "BotResult":
    #     from agile_bot.bots.base_bot.src.bot.test_validate_action import TestValidateAction
    #     action_class = self._get_action_class("test_validate", TestValidateAction)
    #     return self.execute_action("test_validate", action_class, parameters)

    # def code_quality(self, parameters: Dict[str, Any] = None) -> "BotResult":
    #     from agile_bot.bots.base_bot.src.bot.code_quality_action import CodeQualityAction
    #     action_class = self._get_action_class("code_quality", CodeQualityAction)
    #     return self.execute_action("code_quality", action_class, parameters)

    # def does_requested_action_match_current(self, requested_action: str) -> Tuple[bool, Optional[str], Optional[str]]:
    #     """Check if requested action matches current action or expected next action."""
    #     self.actions.load_state()
    #     current_action = self.actions.current
    #     if not current_action:
    #         return True, None, None
    #     if current_action not in self.actions.names:
    #         return True, current_action, None
    #     current_index = self.actions.names.index(current_action)
    #     expected_next = self.actions.names[current_index + 1] if current_index + 1 < len(self.actions.names) else None
    #     if requested_action == current_action:
    #         matches = True
    #     elif expected_next is None:
    #         matches = True
    #     else:
    #         matches = requested_action == expected_next
    #     return matches, current_action, expected_next

    # def forward_to_current_action(self, parameters: Dict[str, Any] = None) -> "BotResult":
    #     """Execute the current action, saving state and advancing when complete."""
    #     self.actions.load_state()
    #     current_action = self.actions.current
    #     if not current_action:
    #         if self.actions.names:
    #             current_action = self.actions.names[0]
    #             self.actions.navigate_to(current_action)
    #         else:
    #             raise ValueError("No actions available to execute.")
    #     if not hasattr(self, current_action):
    #         raise AttributeError(f"Behavior {self.name} does not have action method '{current_action}'")
    #     action_method = getattr(self, current_action)
    #     result = action_method(parameters=parameters)
    #     if result is None:
    #         raise RuntimeError(f"Action method '{current_action}' returned None instead of BotResult")
    #     if not (result.data and result.data.get("requires_confirmation")):
    #         self.actions.save_state()
    #     if self.actions.is_action_completed(current_action):
    #         self.actions.close_current()
    #     return result
