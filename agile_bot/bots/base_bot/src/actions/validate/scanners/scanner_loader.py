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
            
            # Extract scanner name from class name (handle camelCase)
            # Convert VerbNounScanner -> verb_noun
            import re
            scanner_name = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower().replace('_scanner', '').replace('scanner', '')
            
            # Also try extracting from module path if it's in old format
            if 'src.scanners.' in module_path:
                # Extract scanner name from old path format: agile_bot.bots.base_bot.src.scanners.verb_noun_scanner
                path_parts = module_path.split('.')
                if 'scanners' in path_parts:
                    scanner_idx = path_parts.index('scanners')
                    if scanner_idx + 1 < len(path_parts):
                        scanner_name_from_path = path_parts[scanner_idx + 1].replace('_scanner', '')
                        if scanner_name_from_path:
                            scanner_name = scanner_name_from_path
            
            # Try validate.scanners path format first
            base_bot_path = f'agile_bot.bots.base_bot.src.actions.validate.scanners.{scanner_name}_scanner'
            paths_to_try.append(base_bot_path)
            
            # Try old path format for backward compatibility
            old_base_bot_path = f'agile_bot.bots.base_bot.src.scanners.{scanner_name}_scanner'
            paths_to_try.append(old_base_bot_path)
            
            if self.bot_name and self.bot_name != 'base_bot':
                bot_path = f'agile_bot.bots.{self.bot_name}.src.actions.validate.scanners.{scanner_name}_scanner'
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


