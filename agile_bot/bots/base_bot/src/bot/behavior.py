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