"""
ScannerLoader service.

Extracts scanner loading logic from Rule class.
"""
from typing import Optional, Tuple
import importlib
from agile_bot.bots.base_bot.src.scanners.scanner import Scanner


class ScannerLoader:
    """Service for loading scanner classes from module paths.
    
    Domain Model:
        Dependencies: None (utility service)
    """
    
    def __init__(self, bot_name: str = None):
        """Initialize ScannerLoader.
        
        Args:
            bot_name: Name of bot (for bot-specific scanner paths)
        """
        self.bot_name = bot_name
    
    def load_scanner(self, scanner_module_path: str) -> Optional[type]:
        """Load scanner class from module path.
        
        Tries multiple locations:
        1. Exact path specified
        2. base_bot/src/scanners/ (always checked)
        3. Bot's src/scanners/ (if bot_name is set)
        
        Validates that scanner class inherits from Scanner base class.
        
        Args:
            scanner_module_path: Module path to scanner class (e.g., 'agile_bot.bots.base_bot.src.scanners.story_scanner.StoryScanner')
            
        Returns:
            Scanner class if found and valid, None otherwise.
        """
        if not scanner_module_path:
            return None
        
        scanner_class, _ = self._load_scanner_class(scanner_module_path)
        return scanner_class
    
    def load_scanner_with_error(self, scanner_module_path: str) -> Tuple[Optional[type], Optional[str]]:
        """Load scanner class from module path, returning both class and error message.
        
        Args:
            scanner_module_path: Module path to scanner class
            
        Returns:
            Tuple of (scanner_class, error_message). Both may be None.
        """
        if not scanner_module_path:
            return None, None
        
        return self._load_scanner_class(scanner_module_path)
    
    def _load_scanner_class(self, scanner_module_path: str) -> Tuple[Optional[type], Optional[str]]:
        """Load scanner class from module path.
        
        Tries multiple locations:
        1. Exact path specified
        2. base_bot/src/scanners/ (always checked)
        3. Bot's src/scanners/ (if bot_name is set)
        
        Validates that scanner class inherits from Scanner base class.
        
        Args:
            scanner_module_path: Module path to scanner class
            
        Returns:
            Tuple of (scanner_class, error_message). Both may be None.
        """
        try:
            module_path, class_name = scanner_module_path.rsplit('.', 1)
            
            paths_to_try = [module_path]
            
            scanner_name = class_name.lower().replace('scanner', '')
            base_bot_path = f'agile_bot.bots.base_bot.src.scanners.{scanner_name}_scanner'
            paths_to_try.append(base_bot_path)
            
            if self.bot_name and self.bot_name != 'base_bot':
                bot_path = f'agile_bot.bots.{self.bot_name}.src.scanners.{scanner_name}_scanner'
                paths_to_try.append(bot_path)
            
            for path in paths_to_try:
                try:
                    module = importlib.import_module(path)
                    if hasattr(module, class_name):
                        scanner_class = getattr(module, class_name)
                        
                        if isinstance(scanner_class, type) and hasattr(scanner_class, 'scan'):
                            # Validate it inherits from Scanner
                            if issubclass(scanner_class, Scanner):
                                return scanner_class, None
                except (ImportError, AttributeError):
                    continue
            
            return None, f"Scanner class not found: {scanner_module_path}"
        except Exception as e:
            return None, f"Error loading scanner {scanner_module_path}: {e}"


