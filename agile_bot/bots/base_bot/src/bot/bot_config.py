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
        self.config_path = self.bot_paths.bot_directory / 'bot_config.json'
        
        if not self.config_path.exists():
            raise FileNotFoundError(f'Bot config not found at {self.config_path}')
        
        self._config = read_json_file(self.config_path)
    
    @property
    def name(self) -> str:
        return self._config.get('name', self.bot_name)
    
    @property
    def behaviors_list(self) -> List[str]:
        """Discover behaviors from folder structure, ordered by 'order' field in behavior.json.
        
        Behaviors are defined by folders in {bot_directory}/behaviors/ that contain behavior.json.
        Order comes from the 'order' field in each behavior's behavior.json file.
        """
        from agile_bot.bots.base_bot.src.bot.behavior_config import BehaviorConfig
        
        behaviors_dir = self.bot_paths.bot_directory / 'behaviors'
        if behaviors_dir.exists():
            behavior_orders = []
            for item in behaviors_dir.iterdir():
                if item.is_dir() and not item.name.startswith('_') and not item.name.startswith('.'):
                    # Verify it has a behavior.json
                    if (item / 'behavior.json').exists():
                        try:
                            behavior_config = BehaviorConfig(item.name, self.bot_paths, self.bot_name)
                            order = behavior_config._config.get('order', 999)  # Default to end if no order
                            behavior_orders.append((order, item.name))
                        except Exception:
                            # If config load fails, skip this behavior
                            continue
            
            # Sort by order from behavior.json
            behavior_orders.sort(key=lambda x: x[0])
            return [name for _, name in behavior_orders]
        return []
    
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
