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
        from agile_bot.bots.base_bot.src.bot.bot import BotResult
        
        current_behavior = bot.behaviors.current
        if current_behavior is None:
            if bot.behaviors.first:
                bot.behaviors.navigate_to(bot.behaviors.first.name)
                current_behavior = bot.behaviors.current
            else:
                raise ValueError("No behaviors available")
        if current_behavior is None:
            raise ValueError("No current behavior")
        
        action = current_behavior.actions.forward_to_current()
        if action is None:
            return BotResult(
                status='error',
                behavior=current_behavior.name if current_behavior else '',
                action='',
                data={'message': f'No current action found for behavior {current_behavior.name if current_behavior else "unknown"}'}
            )
        
        try:
            result_data = action.execute(parameters or {})
            return BotResult(
                status='completed',
                behavior=current_behavior.name,
                action=action.action_name,
                data=result_data
            )
        except Exception as e:
            return BotResult(
                status='error',
                behavior=current_behavior.name,
                action=action.action_name,
                data={'message': str(e), 'error': type(e).__name__}
            )


class BotToolGenerator:
    
    def __init__(self, bot_name: str, config_path: Path):
        self.bot_name = bot_name
        self.config_path = config_path
    
    def create_bot_tool(self) -> BotTool:
        return BotTool(
            bot_name=self.bot_name,
            config_path=self.config_path
        )

