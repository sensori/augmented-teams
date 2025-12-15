"""
BotPaths class.

Provides access to bot-related paths: workspace directory, bot directory, 
base actions directory, Python workspace root, and documentation path.
"""
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
    """Provides access to bot-related paths.
    
    Instantiated with: Workspace Path (optional, uses environment if not provided), Bot Directory (optional)
    Properties:
        workspace_directory: Path to workspace directory
        bot_directory: Path to bot directory
        base_actions_directory: Path to base_actions directory
        python_workspace_root: Path to Python workspace root
        documentation_path: Path to documentation directory (relative to workspace)
    Method:
        find_repo_root(): Find repository root (alias for python_workspace_root)
    """
    
    def __init__(self, workspace_path: Path = None, bot_directory: Path = None):
        """Initialize BotPaths.
        
        Args:
            workspace_path: Optional workspace path. If not provided, uses 
                          environment variables (WORKING_AREA, BOT_DIRECTORY).
            bot_directory: Optional bot directory. If not provided, uses environment.
                          
        Note:
            If workspace_path is provided, it's used as workspace_directory.
            Bot directory and other paths are still resolved from environment.
            Documentation path is read from bot_config.json if available.
        """
        if workspace_path:
            self._workspace_directory = Path(workspace_path)
        else:
            self._workspace_directory = get_workspace_directory()
        
        if bot_directory:
            self._bot_directory = Path(bot_directory)
        else:
            self._bot_directory = get_bot_directory()
        
        self._base_actions_directory = get_base_actions_directory(self._bot_directory)
        self._python_workspace_root = get_python_workspace_root()
        
        # Load documentation path from bot_config.json if available
        self._documentation_path = self._load_documentation_path()
    
    def _load_documentation_path(self) -> Path:
        """Load documentation path from bot_config.json or default to 'docs/stories'."""
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
        """Get workspace directory.
        
        Returns:
            Path to workspace directory where content files are created.
        """
        return self._workspace_directory
    
    @property
    def bot_directory(self) -> Path:
        """Get bot directory.
        
        Returns:
            Path to bot directory.
        """
        return self._bot_directory
    
    @property
    def base_actions_directory(self) -> Path:
        """Get base actions directory.
        
        Returns:
            Path to base_actions directory.
        """
        return self._base_actions_directory
    
    @property
    def python_workspace_root(self) -> Path:
        """Get Python workspace root.
        
        Returns:
            Path to Python workspace root (repository root for imports).
        """
        return self._python_workspace_root
    
    @property
    def documentation_path(self) -> Path:
        """Get documentation path.
        
        Returns:
            Path to documentation directory (relative to workspace_directory).
            Defaults to 'docs/stories' if not configured in bot_config.json.
        """
        return self._documentation_path
    
    def find_repo_root(self) -> Path:
        """Find repository root.
        
        Returns:
            Path to repository root (same as python_workspace_root).
        """
        return self.python_workspace_root
