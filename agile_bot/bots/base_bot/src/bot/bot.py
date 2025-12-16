from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import json
from datetime import datetime

from agile_bot.bots.base_bot.src.bot.bot_config import BotConfig
from agile_bot.bots.base_bot.src.bot.behaviors import Behaviors
from agile_bot.bots.base_bot.src.bot.behavior import Behavior
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
import logging

logger = logging.getLogger(__name__)
__all__ = ["Bot", "BotResult", "Behavior"]


class BotResult:
    def __init__(self, status: str, behavior: str, action: str, data: Dict[str, Any] = None):
        self.status = status
        self.behavior = behavior
        self.action = action
        self.data = data or {}
        self.executed_instructions_from = f'{behavior}/{action}'


class Bot:
    
    def __init__(self, bot_name: str, bot_directory: Path, config_path: Path):
        self.name = bot_name
        self.bot_name = bot_name
        self.config_path = Path(config_path)
        
        self.bot_paths = BotPaths(bot_directory=bot_directory)
        self.bot_config = BotConfig(bot_name, self.bot_paths)
        self.behaviors = Behaviors(bot_name, self.bot_paths)
        
        self.behaviors._bot_instance = self
        for behavior in self.behaviors:
            behavior.bot = self
    
    def __getattr__(self, name: str):
        """Allow accessing behaviors as attributes (e.g., bot.code, bot.shape)."""
        # Check if it's a behavior name
        behavior = self.behaviors.find_by_name(name)
        if behavior:
            return behavior
        
        # Default for unknown attributes
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")