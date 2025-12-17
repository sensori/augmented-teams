from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict, Any

from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.actions.guardrails import Guardrails
from agile_bot.bots.base_bot.src.actions.content import Content
from agile_bot.bots.base_bot.src.actions.validate.rules import Rules
from agile_bot.bots.base_bot.src.actions.actions import Actions
from agile_bot.bots.base_bot.src.bot.trigger_words import TriggerWords
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths

if TYPE_CHECKING:
    from agile_bot.bots.base_bot.src.bot.bot import BotResult


class Behavior:
    def __init__(self, name: str, bot_paths: BotPaths, bot_instance=None):
        self.bot_name = bot_paths.bot_directory.name
        self.name = name
        self.bot_paths = bot_paths
        self.bot = bot_instance

        self.behavior_directory = self.bot_paths.bot_directory / "behaviors" / name
        self.config_path = self.behavior_directory / "behavior.json"

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Behavior config not found at {self.config_path}. "
                "Each behavior must define its own behavior.json."
            )

        self._config = read_json_file(self.config_path)

        self.description = self._config.get("description", "")
        self.goal = self._config.get("goal", "")
        self.inputs = self._config.get("inputs", [])
        self.outputs = self._config.get("outputs", [])
        self.instructions = self._config.get("instructions", {})
        self.trigger_words = self._config.get("trigger_words", [])
        self.order = self._config.get("order", 999)

        self.guardrails = Guardrails(self)
        self.content = Content(self)
        self.rules = Rules(behavior=self, bot_paths=self.bot_paths)
        self.actions = Actions(self)
        self.trigger_words_obj = TriggerWords(self)

    @property
    def folder(self) -> Path:
        return self.behavior_directory

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