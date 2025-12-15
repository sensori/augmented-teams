from typing import Optional, Tuple
import importlib
from .scanner import Scanner


class ScannerLoader:
    def __init__(self, bot_name: str = None):
        self.bot_name = bot_name
    
    def load_scanner(self, scanner_module_path: str) -> Optional[type]:
        if not scanner_module_path:
            return None
        
        scanner_class, _ = self._load_scanner_class(scanner_module_path)
        return scanner_class
    
    def load_scanner_with_error(self, scanner_module_path: str) -> Tuple[Optional[type], Optional[str]]:
        if not scanner_module_path:
            return None, None
        
        return self._load_scanner_class(scanner_module_path)
    
    def _load_scanner_class(self, scanner_module_path: str) -> Tuple[Optional[type], Optional[str]]:
        try:
            module_path, class_name = scanner_module_path.rsplit('.', 1)
            
            paths_to_try = [module_path]
            
            scanner_name = class_name.lower().replace('scanner', '')
            base_bot_path = f'agile_bot.bots.base_bot.src.actions.validate_rules.scanners.{scanner_name}_scanner'
            paths_to_try.append(base_bot_path)
            
            if self.bot_name and self.bot_name != 'base_bot':
                bot_path = f'agile_bot.bots.{self.bot_name}.src.actions.validate_rules.scanners.{scanner_name}_scanner'
                paths_to_try.append(bot_path)
            
            for path in paths_to_try:
                try:
                    module = importlib.import_module(path)
                    if hasattr(module, class_name):
                        scanner_class = getattr(module, class_name)
                        
                        if isinstance(scanner_class, type) and hasattr(scanner_class, 'scan'):
                            if issubclass(scanner_class, Scanner):
                                return scanner_class, None
                except (ImportError, AttributeError):
                    continue
            
            return None, f"Scanner class not found: {scanner_module_path}"
        except Exception as e:
            return None, f"Error loading scanner {scanner_module_path}: {e}"


