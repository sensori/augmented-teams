from pathlib import Path
import os
from agile_bot.bots.base_bot.src.bot.workspace import (
    get_workspace_directory,
    get_bot_directory,
    get_base_actions_directory,
    get_python_workspace_root
)
from agile_bot.bots.base_bot.src.utils import read_json_file


class BotPaths:
    def __init__(self, workspace_path: Path = None, bot_directory: Path = None):

        if workspace_path:
            self._workspace_directory = Path(workspace_path)
        else:
            self._workspace_directory = get_workspace_directory()
        
        if bot_directory:
            self._bot_directory = Path(bot_directory)
        else:
            self._bot_directory = get_bot_directory()
        
        self._base_actions_directory = get_base_actions_directory(self._bot_directory)
        
        # Always get python_workspace_root from get_python_workspace_root()
        # This is reliable and based on the file location. If it fails, let it crash.
        self._python_workspace_root = get_python_workspace_root()
        
        # Load documentation path from bot_config.json if available
        self._documentation_path = self._load_documentation_path()
    
    def _load_documentation_path(self) -> Path:
        bot_config_path = self._bot_directory / 'config' / 'bot_config.json'
        if bot_config_path.exists():
            try:
                config = read_json_file(bot_config_path)
                docs_path = config.get('docs_path', 'docs/stories')
                return Path(docs_path)
            except Exception:
                pass
        return Path('docs/stories')
    
    @property
    def workspace_directory(self) -> Path:
        return self._workspace_directory
    
    @property
    def bot_directory(self) -> Path:
        return self._bot_directory
    
    @property
    def base_actions_directory(self) -> Path:
        return self._base_actions_directory
    
    @property
    def python_workspace_root(self) -> Path:
        return self._python_workspace_root
    
    @property
    def documentation_path(self) -> Path:
        return self._documentation_path
    
    def find_repo_root(self) -> Path:
        return self.python_workspace_root
