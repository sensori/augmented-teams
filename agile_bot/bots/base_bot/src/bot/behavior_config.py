from pathlib import Path
from typing import Any, Dict, List

from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
from agile_bot.bots.base_bot.src.utils import read_json_file


class BehaviorConfig:
    def __init__(self, behavior_name: str, bot_paths: BotPaths, bot_name: str = None):
        if not isinstance(bot_paths, BotPaths):
            raise TypeError("bot_paths must be an instance of BotPaths")

        self.behavior_name = behavior_name
        self.bot_paths = bot_paths
        self.bot_name = bot_name or (bot_paths.bot_name if hasattr(bot_paths, 'bot_name') else 'unknown')
        
        self.behavior_directory = self.bot_paths.bot_directory / "behaviors" / behavior_name
        self.config_path = self.behavior_directory / "behavior.json"

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Behavior config not found at {self.config_path}. "
                "Each behavior must define its own behavior.json."
            )

        self._config = read_json_file(self.config_path)

    @property
    def description(self) -> str:
        return self._config.get("description", "")

    @property
    def goal(self) -> str:
        return self._config.get("goal", "")

    @property
    def inputs(self) -> List[Any]:
        return self._config.get("inputs", [])

    @property
    def outputs(self) -> List[Any]:
        return self._config.get("outputs", [])

    @property
    def base_actions_path(self) -> Path:
        return self.bot_paths.base_actions_directory

    @property
    def instructions(self) -> Dict[str, Any]:
        return self._config.get("instructions", {})

    @property
    def trigger_words(self) -> List[Any]:
        return self._config.get("trigger_words", [])

    @property
    def actions_workflow(self) -> List[Dict[str, Any]]:
        actions = self._config.get("actions_workflow", {}).get("actions", [])
        if not isinstance(actions, list):
            return []

        def order_key(action: Dict[str, Any]) -> Any:
            return action.get("order", 0)

        return sorted(actions, key=order_key)

    @property
    def actions(self) -> List[str]:
        return [action.get("name", "") for action in self.actions_workflow if action.get("name")]