from pathlib import Path
from typing import Dict, Any, List
from agile_bot.bots.base_bot.src.bot.workspace import get_workspace_directory


class BehaviorTool:
    
    def __init__(self, bot_name: str, behavior_name: str, config_path: Path):
        self.bot_name = bot_name
        self.behavior_name = behavior_name
        self.config_path = config_path
        self.name = f'{bot_name}_{behavior_name}_tool'
    
    def invoke(self, parameters: Dict[str, Any] = None):
        from agile_bot.bots.base_bot.src.bot.bot import Bot, BotResult
        from agile_bot.bots.base_bot.src.bot.workspace import get_bot_directory
        
        bot_directory = get_bot_directory()

        bot = Bot(
            bot_name=self.bot_name,
            bot_directory=bot_directory,
            config_path=self.config_path
        )
        
        behavior = getattr(bot, self.behavior_name)
        action = behavior.actions.forward_to_current()
        if action is None:
            return BotResult(
                status='error',
                behavior=self.behavior_name,
                action='',
                data={'message': f'No current action found for behavior {self.behavior_name}'}
            )
        
        try:
            result_data = action.execute(parameters or {})
            return BotResult(
                status='completed',
                behavior=self.behavior_name,
                action=action.action_name,
                data=result_data
            )
        except Exception as e:
            return BotResult(
                status='error',
                behavior=self.behavior_name,
                action=action.action_name,
                data={'message': str(e), 'error': type(e).__name__}
            )


class BehaviorToolGenerator:
    
    def __init__(self, bot_name: str, config_path: Path):
        self.bot_name = bot_name
        self.config_path = config_path
        
        # Load bot config to get behaviors
        import json
        self.config = json.loads(config_path.read_text(encoding='utf-8'))
    
    def create_behavior_tools(self) -> List[BehaviorTool]:
        tools = []
        
        for behavior_name in self.config.get('behaviors', []):
            tool = BehaviorTool(
                bot_name=self.bot_name,
                behavior_name=behavior_name,
                config_path=self.config_path,
            )
            tools.append(tool)
        
        return tools

