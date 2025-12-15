"""
BaseActionConfig class.

Loads base action configuration from base_actions folder.
"""
from pathlib import Path
from typing import Optional, Dict, Any

from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.bot.workspace import get_base_actions_directory


class BaseActionConfig:
    """Base action configuration loaded from base_actions/{action_name}/action_config.json.
    
    Instantiated with: Actions, Workspace
    Properties:
        order: Order number from config
        next_action: Next action name from config
        custom_class: Custom action class path from config (if any)
        instructions: Instructions from config
    """
    
    def __init__(self, action_name: str, bot_paths: BotPaths):
        """Initialize BaseActionConfig.
        
        Args:
            action_name: Name of the action (e.g., 'gather_context')
            bot_paths: BotPaths instance with environment-derived paths
            
        Raises:
            FileNotFoundError: If action_config.json is not found
        """
        self.action_name = action_name
        self.bot_paths = bot_paths
        
        # Find base actions directory
        base_actions_dir = get_base_actions_directory(bot_directory=bot_paths.bot_directory)
        self.config_path = base_actions_dir / action_name / "action_config.json"
        
        # Store action_name in config for Action base class
        if not hasattr(self, '_config'):
            self._config = {}
        self._config['name'] = action_name
        
        # Load config if exists (some actions may not have config)
        if self.config_path.exists():
            self._config = read_json_file(self.config_path)
        else:
            # Default config for actions without action_config.json
            self._config = {
                "name": action_name,
                "workflow": True,
                "order": 0
            }
    
    @property
    def order(self) -> int:
        """Get order number from config."""
        return self._config.get("order", 0)
    
    @property
    def next_action(self) -> Optional[str]:
        """Get next action name from config."""
        return self._config.get("next_action")
    
    @property
    def custom_class(self) -> Optional[str]:
        """Get custom action class path from config."""
        return self._config.get("action_class") or self._config.get("custom_class")
    
    @property
    def instructions(self) -> list:
        """Get instructions from config."""
        return self._config.get("instructions", [])
    
    @property
    def workflow(self) -> bool:
        """Get workflow flag from config."""
        return self._config.get("workflow", True)

