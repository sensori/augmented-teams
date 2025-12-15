from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.bot.workspace import get_workspace_directory


class BotTool:
    
    def __init__(self, bot_name: str, config_path: Path):
        self.bot_name = bot_name
        self.config_path = config_path
        self.name = f'{bot_name}_tool'
    
    def invoke(self, parameters: Dict[str, Any] = None):
        from agile_bot.bots.base_bot.src.bot.bot import Bot
        from agile_bot.bots.base_bot.src.bot.workspace import get_bot_directory
        
        bot_directory = get_bot_directory()

        bot = Bot(
            bot_name=self.bot_name,
            bot_directory=bot_directory,
            config_path=self.config_path
        )
        return bot.forward_to_current_behavior_and_current_action()


class BotToolGenerator:
    
    def __init__(self, bot_name: str, config_path: Path):
        self.bot_name = bot_name
        self.config_path = config_path
    
    def create_bot_tool(self) -> BotTool:
        return BotTool(
            bot_name=self.bot_name,
            config_path=self.config_path
        )

