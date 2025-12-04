from pathlib import Path
from typing import Dict, Any, List


class BehaviorTool:
    
    def __init__(self, bot_name: str, behavior_name: str, config_path: Path, workspace_root: Path):
        self.bot_name = bot_name
        self.behavior_name = behavior_name
        self.config_path = config_path
        self.workspace_root = workspace_root
        self.name = f'{bot_name}_{behavior_name}_tool'
    
    def invoke(self, parameters: Dict[str, Any] = None):
        from agile_bot.bots.base_bot.src.bot.bot import Bot
        
        bot = Bot(
            bot_name=self.bot_name,
            workspace_root=self.workspace_root,
            config_path=self.config_path
        )
        
        behavior = getattr(bot, self.behavior_name)
        return behavior.forward_to_current_action()


class BehaviorToolGenerator:
    
    def __init__(self, bot_name: str, config_path: Path, workspace_root: Path):
        self.bot_name = bot_name
        self.config_path = config_path
        self.workspace_root = workspace_root
        
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
                workspace_root=self.workspace_root
            )
            tools.append(tool)
        
        return tools

