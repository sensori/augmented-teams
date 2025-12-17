from pathlib import Path
from typing import Dict, Any, List, Optional
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths


class ValidationScope:
    def __init__(self, parameters: Dict[str, Any], bot_paths: Optional[BotPaths] = None):
        self._parameters = parameters or {}
        self._bot_paths = bot_paths
        self._scope_config: Dict[str, Any] = {}
        self._repo_root: Optional[Path] = None
        self._build_scope()
        if self._bot_paths:
            self._repo_root = self._find_repo_root()
    
    def _build_scope(self):
        path_params = {'test', 'src'}
        
        for key, value in self._parameters.items():
            if value is None:
                continue
            
            if key in path_params:
                if not isinstance(value, list):
                    value = [value]
                
                self._scope_config[key] = [
                    str(Path(p)).replace('\\', '/') for p in value
                ]
            elif key == 'validate_all' and value is True:
                self._scope_config['all'] = True
            else:
                self._scope_config[key] = value
    
    @property
    def scope(self) -> Dict[str, Any]:
        return self._scope_config
    
    def files(self, key: str) -> List[Path]:
        files_list = self._scope_config.get(key, [])
        
        if not files_list and self._bot_paths:
            files_list = self._auto_discover_files(key)
            if files_list:
                self._scope_config[key] = files_list
        
        resolved_paths = []
        for file_path_str in files_list:
            file_path = Path(file_path_str)
            
            if file_path.is_absolute():
                resolved_paths.append(file_path)
            else:
                if self._repo_root:
                    resolved_path = self._repo_root / file_path
                    resolved_paths.append(resolved_path)
                elif self._bot_paths:
                    resolved_path = self._bot_paths.workspace_directory / file_path
                    resolved_paths.append(resolved_path)
                else:
                    resolved_paths.append(file_path)
        
        return resolved_paths
    
    def all_files(self) -> Dict[str, List[Path]]:
        all_files_dict = {}
        file_keys = {'test', 'src'}
        
        for key in file_keys:
            files = self.files(key)
            if files:
                all_files_dict[key] = files
        
        return all_files_dict
    
    def _find_repo_root(self) -> Optional[Path]:
        if not self._bot_paths:
            return None
        
        workspace_path = self._bot_paths.workspace_directory
        current = workspace_path.resolve()
        
        for i in range(10):
            if (current / '.git').exists() or (current / 'agile_bot').exists():
                return current
            if current.parent == current:
                break
            current = current.parent
        
        workspace_str = str(workspace_path.resolve())
        if 'demo' in workspace_str:
            parts = workspace_path.resolve().parts
            if 'demo' in parts:
                demo_idx = parts.index('demo')
                return Path(*parts[:demo_idx]) if demo_idx > 0 else workspace_path.resolve().parent
            else:
                return workspace_path.resolve().parent
        else:
            return workspace_path.resolve().parent
    
    def _auto_discover_files(self, key: str) -> List[str]:
        if not self._bot_paths:
            return []
        
        dir_name = key
        workspace_directory = self._bot_paths.workspace_directory
        search_dir = workspace_directory / dir_name
        
        discovered_files = []
        
        if key == 'test':
            discovered_files.extend(search_dir.glob('test_*.py'))
        else:
            discovered_files.extend(search_dir.rglob('*.py'))
        
        return [str(f) for f in discovered_files]
