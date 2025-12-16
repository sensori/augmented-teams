from pathlib import Path
import json
from typing import Dict, Any
from agile_bot.bots.base_bot.src.bot.bot import Bot


class MCPServer:
    
    def __init__(self, bot_name: str, bot_directory: Path, config_path: Path):
        self.bot_name = bot_name
        self.bot_directory = Path(bot_directory)
        self.config_path = Path(config_path)
        self.bot = None
    
    def start(self):
        self.bot = Bot(
            bot_name=self.bot_name,
            bot_directory=self.bot_directory,
            config_path=self.config_path
        )
    
    def invoke_tool(self, tool_name: str, parameters: Dict[str, Any]):

        if self.bot is None:
            raise RuntimeError('Bot not initialized. Call start() first.')
        
        # Extract behavior and action from tool name
        # Format: {bot_name}_{behavior}_{action}
        parts = tool_name.split('_')
        if len(parts) >= 3:
            # Remove bot name parts and get behavior + action
            # e.g., 'test_bot_shape_clarify' -> ['shape', 'clarify']
            without_bot_name = '_'.join(parts[2:])  # Get everything after 'test_bot'
            
            # Try to find the split point between behavior and action
            # Common actions: clarify, strategy, build, render, validate, etc.
            action_keywords = ['clarify', 'strategy', 'build', 
                              'render', 'validate', 'test_validate']
            
            behavior = None
            action = None
            for action_keyword in action_keywords:
                if without_bot_name.endswith(action_keyword):
                    action = action_keyword
                    behavior = without_bot_name[:-(len(action_keyword) + 1)]  # +1 for underscore
                    break
            
            if behavior and action:
                parameters['behavior'] = behavior
                parameters['action'] = action
        
        return self.bot.invoke_tool(tool_name, parameters)

