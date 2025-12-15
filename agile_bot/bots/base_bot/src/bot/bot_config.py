"""
BotConfig class.

Represents bot configuration loaded from bot_config.json.
Mirrors the folder/JSON structure per design philosophy.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths


class BotConfig:
    """Bot configuration loaded from bot_config.json.
    
    Instantiated with: Bot Name, BotPaths
    Properties:
        name: Bot name from config
        behaviors_list: List of behavior names from config
        base_actions_path: Path to base_actions directory
        description: Bot description from config
        goal: Bot goal from config
        instructions: Bot instructions list from config
        mcp: MCP configuration dict from config
        trigger_words: List of trigger words from config
        working_area: WORKING_AREA from config (legacy field)
    """
    
    def __init__(self, bot_name: str, bot_paths: BotPaths):
        """Initialize BotConfig.
        
        Args:
            bot_name: Name of the bot (e.g., 'story_bot')
            bot_paths: BotPaths instance with environment-derived paths
            
        Raises:
            FileNotFoundError: If bot_config.json is not found
            ValueError: If config file contains invalid JSON
        """
        self.bot_name = bot_name
        
        if not isinstance(bot_paths, BotPaths):
            raise TypeError("bot_paths must be an instance of BotPaths")
        
        self.bot_paths = bot_paths
        self.config_path = self.bot_paths.bot_directory / 'config' / 'bot_config.json'
        
        # Load config
        if not self.config_path.exists():
            raise FileNotFoundError(f'Bot config not found at {self.config_path}')
        
        # read_json_file already handles UTF-8 and raises appropriate errors
        self._config = read_json_file(self.config_path)
    
    @property
    def name(self) -> str:
        """Get bot name from config.
        
        Returns:
            Bot name from config file, or bot_name if not in config.
        """
        return self._config.get('name', self.bot_name)
    
    @property
    def behaviors_list(self) -> List[str]:
        """Get behaviors list from config.
        
        Returns:
            List of behavior names from bot_config.json, or empty list if missing.
        """
        return self._config.get('behaviors', [])
    
    @property
    def base_actions_path(self) -> Path:
        """Get base actions path.
        
        Returns:
            Path to base_actions directory in bot directory.
        """
        return self.bot_paths.bot_directory / 'base_actions'
    
    @property
    def description(self) -> str:
        """Get bot description from config.
        
        Returns:
            Bot description from bot_config.json, or empty string if missing.
        """
        return self._config.get('description', '')
    
    @property
    def goal(self) -> str:
        """Get bot goal from config.
        
        Returns:
            Bot goal from bot_config.json, or empty string if missing.
        """
        return self._config.get('goal', '')
    
    @property
    def instructions(self) -> List[str]:
        """Get bot instructions from config.
        
        Returns:
            List of instruction strings from bot_config.json, or empty list if missing.
        """
        return self._config.get('instructions', [])
    
    @property
    def mcp(self) -> Dict[str, Any]:
        """Get MCP configuration from config.
        
        Returns:
            MCP configuration dict from bot_config.json, or empty dict if missing.
        """
        return self._config.get('mcp', {})
    
    @property
    def trigger_words(self) -> List[str]:
        """Get trigger words from config.
        
        Returns:
            List of trigger words from bot_config.json, or empty list if missing.
        """
        return self._config.get('trigger_words', [])
    
    @property
    def working_area(self) -> Optional[str]:
        """Get WORKING_AREA from config (legacy field).
        
        Returns:
            WORKING_AREA from bot_config.json, or None if missing.
        """
        return self._config.get('WORKING_AREA')
