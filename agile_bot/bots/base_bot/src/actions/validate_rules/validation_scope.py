"""
ValidationScope class.

Encapsulates validation scope configuration from parameters.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths


class ValidationScope:
    """Validation scope configuration.
    
    Domain Model:
        Properties: story_names, increment_priorities, epic_names, test, src, all
    """
    
    def __init__(self, parameters: Dict[str, Any], bot_paths: Optional[BotPaths] = None):
        """Initialize ValidationScope from parameters.
        
        Args:
            parameters: Parameters dict from action execution
            bot_paths: BotPaths instance for accessing workspace directory (optional)
        """
        self._parameters = parameters or {}
        self._bot_paths = bot_paths
        self._scope_config: Dict[str, Any] = {}
        self._repo_root: Optional[Path] = None
        self._build_scope()
        if self._bot_paths:
            self._repo_root = self._find_repo_root()
    
    def _build_scope(self):
        """Build scope configuration from parameters."""
        # Parameters that need path normalization
        path_params = {'test', 'src'}
        
        for key, value in self._parameters.items():
            if value is None:
                continue
            
            # Handle path parameters (normalize paths)
            if key in path_params:
                # Ensure it's a list
                if not isinstance(value, list):
                    value = [value]
                
                # Normalize paths
                self._scope_config[key] = [
                    str(Path(p)).replace('\\', '/') for p in value
                ]
            # Handle validate_all flag
            elif key == 'validate_all' and value is True:
                self._scope_config['all'] = True
            # Add other parameters directly
            else:
                self._scope_config[key] = value
    
    @property
    def scope(self) -> Dict[str, Any]:
        """Get scope configuration dict.
        
        Domain Model: scope
        """
        return self._scope_config
    
    def files(self, key: str) -> List[Path]:
        """Get list of resolved file paths for the given key.
        
        Auto-discovers files if none are provided and bot_paths is available.
        All paths are resolved to absolute Path objects.
        
        Args:
            key: File type key ('test', 'src', etc.)
        
        Returns:
            List of resolved Path objects
        """
        files_list = self._scope_config.get(key, [])
        
        # Auto-discover if no files provided and bot_paths is available
        if not files_list and self._bot_paths:
            files_list = self._auto_discover_files(key)
            # Cache discovered files in scope config
            if files_list:
                self._scope_config[key] = files_list
        
        # Resolve all paths to absolute Path objects
        resolved_paths = []
        for file_path_str in files_list:
            file_path = Path(file_path_str)
            
            # If absolute path, use as-is
            if file_path.is_absolute():
                resolved_paths.append(file_path)
            else:
                # Resolve against repo root (files are relative to repo root)
                if self._repo_root:
                    resolved_path = self._repo_root / file_path
                    resolved_paths.append(resolved_path)
                elif self._bot_paths:
                    # Fallback: resolve against workspace
                    resolved_path = self._bot_paths.workspace_directory / file_path
                    resolved_paths.append(resolved_path)
                else:
                    # No resolution possible, use as-is
                    resolved_paths.append(file_path)
        
        return resolved_paths
    
    def all_files(self) -> Dict[str, List[Path]]:
        """Get all files from all keys in scope.
        
        Returns:
            Dictionary mapping file type keys to lists of resolved Path objects
        """
        all_files_dict = {}
        # Get all file keys from scope config (test, src, etc.)
        file_keys = {'test', 'src'}  # Known file keys, can be extended
        
        for key in file_keys:
            files = self.files(key)
            if files:
                all_files_dict[key] = files
        
        return all_files_dict
    
    def _find_repo_root(self) -> Optional[Path]:
        """Find repository root by looking for common markers.
        
        Returns:
            Path to repo root, or None if not found
        """
        if not self._bot_paths:
            return None
        
        workspace_path = self._bot_paths.workspace_directory
        current = workspace_path.resolve()  # Resolve to absolute path first
        
        # Look up to 10 levels up for repo markers
        for i in range(10):
            if (current / '.git').exists() or (current / 'agile_bot').exists():
                return current
            if current.parent == current:  # Reached filesystem root
                break
            current = current.parent
        
        # Fallback: use workspace's absolute path parent if we're in a demo subdirectory
        workspace_str = str(workspace_path.resolve())
        if 'demo' in workspace_str:
            # Find where 'demo' appears and use that as a hint
            parts = workspace_path.resolve().parts
            if 'demo' in parts:
                demo_idx = parts.index('demo')
                return Path(*parts[:demo_idx]) if demo_idx > 0 else workspace_path.resolve().parent
            else:
                return workspace_path.resolve().parent
        else:
            return workspace_path.resolve().parent
    
    def _auto_discover_files(self, key: str) -> List[str]:
        """Auto-discover files for the given key.
        
        Args:
            key: File type key ('test', 'src', etc.)
        
        Returns:
            List of discovered file paths
        """
        if not self._bot_paths:
            return []
        
        # Use key name directly as directory name
        dir_name = key
        workspace_directory = self._bot_paths.workspace_directory
        search_dir = workspace_directory / dir_name
        
        discovered_files = []
        
        if search_dir.exists() and search_dir.is_dir():
            # Find all Python files (can be extended for other file types)
            if key == 'test':
                # For tests, look for test_*.py files
                discovered_files.extend(search_dir.glob('test_*.py'))
            else:
                # For src and other directories, look for all .py files
                discovered_files.extend(search_dir.rglob('*.py'))
        
        return [str(f) for f in discovered_files]

