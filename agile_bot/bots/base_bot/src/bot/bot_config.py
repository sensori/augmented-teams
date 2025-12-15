from pathlib import Path
from typing import List, Dict, Any, Optional
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths


class BotConfig:
    def __init__(self, bot_name: str, bot_paths: BotPaths):
        self.bot_name = bot_name
        
        if not isinstance(bot_paths, BotPaths):
            raise TypeError("bot_paths must be an instance of BotPaths")
        
        self.bot_paths = bot_paths
        # Check bot_config.json in bot directory first, then fall back to config/bot_config.json
        config_path_in_bot = self.bot_paths.bot_directory / 'bot_config.json'
        config_path_in_config = self.bot_paths.bot_directory / 'config' / 'bot_config.json'
        
        if config_path_in_bot.exists():
            self.config_path = config_path_in_bot
        elif config_path_in_config.exists():
            self.config_path = config_path_in_config
        else:
            raise FileNotFoundError(
                f'Bot config not found at {config_path_in_bot} or {config_path_in_config}'
            )
        
        self._config = read_json_file(self.config_path)
    
    @property
    def name(self) -> str:
        return self._config.get('name', self.bot_name)
    
    @property
    def behaviors_list(self) -> List[str]:
        return self._config.get('behaviors', [])
    
    @property
    def base_actions_path(self) -> Path:
        return self.bot_paths.bot_directory / 'base_actions'
    
    @property
    def description(self) -> str:
        return self._config.get('description', '')
    
    @property
    def goal(self) -> str:
        return self._config.get('goal', '')
    
    @property
    def instructions(self) -> List[str]:
        return self._config.get('instructions', [])
    
    @property
    def mcp(self) -> Dict[str, Any]:
        return self._config.get('mcp', {})
    
    @property
    def trigger_words(self) -> List[str]:
        return self._config.get('trigger_words', [])
    
    @property
    def working_area(self) -> Optional[str]:
        return self._config.get('WORKING_AREA')
