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
        self.rules_collection = Rules(behavior=self, bot_paths=self.bot_paths)
        self.actions = Actions(self.behavior_config, self)
        self.trigger_words = TriggerWords(self.behavior_config)

    @property
    def folder(self) -> Path:
        return self.bot_paths.bot_directory / "behaviors" / self.name

    @property
    def rules(self):
        return list(self.rules_collection)

    def matches_trigger(self, text: str) -> bool:
        return self.trigger_words.matches(text)
    
    @staticmethod
    def find_behavior_folder(bot_directory: Path, bot_name: str, behavior_name: str) -> Path:
        behaviors_dir = bot_directory / 'behaviors'
        if not behaviors_dir.exists():
            raise FileNotFoundError(f"Behavior folder not found: {behavior_name}")
        
        exact_folder = behaviors_dir / behavior_name
        if exact_folder.exists() and exact_folder.is_dir():
            return exact_folder
        
        for folder in behaviors_dir.iterdir():
            if folder.is_dir():
                if folder.name.endswith(f'_{behavior_name}') or folder.name == behavior_name:
                    return folder
        
        raise FileNotFoundError(f"Behavior folder not found: {behavior_name}")