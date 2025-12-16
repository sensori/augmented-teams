from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict, Any

from agile_bot.bots.base_bot.src.bot.behavior_config import BehaviorConfig
from agile_bot.bots.base_bot.src.actions.guardrails import Guardrails
from agile_bot.bots.base_bot.src.actions.content import Content
from agile_bot.bots.base_bot.src.actions.validate.rules import Rules
from agile_bot.bots.base_bot.src.actions.actions import Actions
from agile_bot.bots.base_bot.src.bot.trigger_words import TriggerWords
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths

if TYPE_CHECKING:
    from agile_bot.bots.base_bot.src.bot.bot import BotResult


class Behavior:
    def __init__(self, name: str, bot_name: str, bot_paths: BotPaths, bot_instance=None):
        self.name = name
        self.bot_name = bot_name
        self.bot_paths = bot_paths
        self.bot = bot_instance

        self.behavior_config = BehaviorConfig(self.name, self.bot_paths, self.bot_name)
        self.description = self.behavior_config.description
        self.goal = self.behavior_config.goal
        self.inputs = self.behavior_config.inputs
        self.outputs = self.behavior_config.outputs

        self.guardrails = Guardrails(self.behavior_config)
        self.content = Content(self.behavior_config)
        self.rules = Rules(behavior=self, bot_paths=self.bot_paths)
        self.actions = Actions(self.behavior_config, self)
        self.trigger_words = TriggerWords(self.behavior_config)

    @property
    def folder(self) -> Path:
        return self.bot_paths.bot_directory / "behaviors" / self.name

    def matches_trigger(self, text: str) -> bool:
        return self.trigger_words.matches(text)
    
    def forward_to_current_action(self, parameters: Dict[str, Any] = None) -> 'BotResult':
        """Forward to current action in this behavior's workflow.
        
        Loads state, gets current action, executes it, and returns BotResult.
        """
        from agile_bot.bots.base_bot.src.bot.bot import BotResult
        
        # Load state to sync with persisted state
        self.actions.load_state()
        
        # Get current action
        current_action = self.actions.current
        if current_action is None:
            # No current action - return error result
            return BotResult(
                status='error',
                behavior=self.name,
                action='',
                data={'message': f'No current action found for behavior {self.name}'}
            )
        
        # Execute current action
        try:
            result = current_action.execute(parameters or {})
            
            # Return BotResult with action result
            return BotResult(
                status='completed',
                behavior=self.name,
                action=current_action.action_name,
                data=result
            )
        except Exception as e:
            return BotResult(
                status='error',
                behavior=self.name,
                action=current_action.action_name if current_action else '',
                data={'message': str(e), 'error': type(e).__name__}
            )
    
    def does_requested_action_match_current(self, requested_action: str) -> tuple[bool, str | None, str | None]:
        """Check if requested action matches current action.
        
        Returns:
            Tuple of (matches: bool, current_action: str | None, expected_next: str | None)
        """
        # Load state to sync with persisted state
        self.actions.load_state()
        
        current_action = self.actions.current
        current_action_name = current_action.action_name if current_action else None
        
        if current_action_name == requested_action:
            return (True, current_action_name, None)
        
        # Find expected next action
        expected_next = None
        if current_action:
            # Get next action from the actions collection
            next_action = self.actions.next()
            if next_action:
                expected_next = next_action.action_name
        
        return (False, current_action_name, expected_next)
    
    def navigate_to_action(self, action_name: str, parameters: Dict[str, Any] = None, out_of_order: bool = False) -> 'BotResult':
        """Navigate to a specific action and execute it.
        
        Args:
            action_name: Name of the action to navigate to
            parameters: Parameters to pass to the action
            out_of_order: Whether this navigation is out of order
            
        Returns:
            BotResult from executing the action
        """
        from agile_bot.bots.base_bot.src.bot.bot import BotResult
        
        # Navigate to the action
        self.actions.navigate_to(action_name)
        
        # Execute the action
        current_action = self.actions.current
        if current_action is None:
            return BotResult(
                status='error',
                behavior=self.name,
                action=action_name,
                data={'message': f'Action {action_name} not found in behavior {self.name}'}
            )
        
        try:
            result = current_action.execute(parameters or {})
            return BotResult(
                status='completed',
                behavior=self.name,
                action=current_action.action_name,
                data=result
            )
        except Exception as e:
            return BotResult(
                status='error',
                behavior=self.name,
                action=current_action.action_name,
                data={'message': str(e), 'error': type(e).__name__}
            )
    
    def __getattr__(self, name: str):
        """Allow accessing actions as methods (e.g., behavior.gather_context(), behavior.clarify())."""
        # Check if it's an action name
        action = self.actions.find_by_name(name)
        if action:
            # Return a callable that executes the action
            def execute_action(parameters: Dict[str, Any] = None) -> 'BotResult':
                from agile_bot.bots.base_bot.src.bot.bot import BotResult
                try:
                    # Navigate to the action first (this saves workflow state)
                    self.actions.navigate_to(name)
                    result = action.execute(parameters or {})
                    return BotResult(
                        status='completed',
                        behavior=self.name,
                        action=action.action_name,
                        data=result
                    )
                except Exception as e:
                    return BotResult(
                        status='error',
                        behavior=self.name,
                        action=action.action_name,
                        data={'message': str(e), 'error': type(e).__name__}
                    )
            return execute_action
        
        # Default behavior for unknown attributes
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")