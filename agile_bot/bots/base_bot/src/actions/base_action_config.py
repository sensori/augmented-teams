from pathlib import Path
from typing import Optional, Dict, Any

from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.bot.workspace import get_base_actions_directory


class BaseActionConfig:
    def __init__(self, action_name: str, bot_paths: BotPaths):
        self.action_name = action_name
        self.bot_paths = bot_paths
        
        base_actions_dir = get_base_actions_directory(bot_directory=bot_paths.bot_directory)
        
        possible_dirs = [action_name]
        
        self.config_path = None
        for dir_name in possible_dirs:
            candidate_path = base_actions_dir / dir_name / "action_config.json"
            self.config_path = candidate_path
            break
        
        if self.config_path is None:
            self.config_path = base_actions_dir / action_name / "action_config.json"
        
        if not hasattr(self, '_config'):
            self._config = {}
        self._config['name'] = action_name
        
        # Try to load config file, use empty dict if it doesn't exist
        try:
            self._config = read_json_file(self.config_path)
        except FileNotFoundError:
            # Use default config if file doesn't exist (for test scenarios)
            self._config = {}
        self._config['name'] = action_name
        self.action_name = action_name
    
    @property
    def order(self) -> int:
        return self._config.get("order", 0)
    
    @property
    def next_action(self) -> Optional[str]:
        return self._config.get("next_action")
    
    @property
    def custom_class(self) -> Optional[str]:
        return self._config.get("action_class") or self._config.get("custom_class")
    
    @property
    def instructions(self) -> list:
        return self._config.get("instructions", [])
    
    @property
    def workflow(self) -> bool:
        return self._config.get("workflow", True)
