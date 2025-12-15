"""
Rules collection class.

Manages collection of Rule objects for a behavior or bot.
"""
from __future__ import annotations

from typing import List, Optional, Iterator, Dict, Any
from pathlib import Path
from agile_bot.bots.base_bot.src.utils import read_json_file


class Rules:
    """Collection of Rule objects.
    
    Domain Model:
        Instantiated with: Behavior (or BotConfig for common rules)
        Methods: find_by_name(), iterate()
        Property: instructions (returns Rule)
    """
    
    def __init__(self, behavior=None, bot_config=None, bot_paths=None):
        """Initialize Rules collection.
        
        Args:
            behavior: Behavior instance to load rules for (behavior-specific rules)
            bot_config: BotConfig instance (for bot-level/common rules)
            bot_paths: BotPaths instance (for resolving paths) - required when behavior is provided
            
        Note:
            Either behavior or bot_config should be provided, not both.
            If behavior is provided, loads behavior-specific and bot-level rules.
            If bot_config is provided, loads only bot-level/common rules.
        """
        self.behavior = behavior
        self.bot_config = bot_config
        
        if behavior:
            if not bot_paths:
                raise ValueError("bot_paths is required when behavior is provided")
            self.bot_name = behavior.bot_name
            self.behavior_name = behavior.name
            self.bot_paths = bot_paths
        elif bot_config:
            self.bot_name = bot_config.name
            self.behavior_name = 'common'
            self.bot_paths = bot_paths
        else:
            raise ValueError("Either behavior or bot_config must be provided")
        
        # Lazy load rules
        self._rules: Optional[List['Rule']] = None
        
        # Track violations from all rules
        self._all_violations: List[Dict[str, Any]] = []
    
    def _load_rules(self) -> List['Rule']:
        """Load all rules (bot-level and behavior-specific).
        
        Returns:
            List of Rule objects
        """
        if self._rules is not None:
            return self._rules
        
        # Import here to avoid circular import
        from agile_bot.bots.base_bot.src.actions.validate_rules.rule import Rule
        
        all_rules = []
        
        # Load bot-level rules from bot's own rules directory
        bot_rules = self._load_bot_rules()
        all_rules.extend(bot_rules)
        
        # Load behavior-specific rules if behavior is provided
        if self.behavior:
            behavior_rules = self._load_behavior_rules()
            all_rules.extend(behavior_rules)
        
        self._rules = all_rules
        return self._rules
    
    def _load_bot_rules(self) -> List['Rule']:
        """Load bot-level rules from bot's own rules directory.
        
        Returns:
            List of Rule objects
        """
        from agile_bot.bots.base_bot.src.actions.validate_rules.rule import Rule
        
        bot_rules = []
        
        # Get bot directory from bot_paths
        if not self.bot_paths:
            return bot_rules
        
        bot_dir = self.bot_paths.bot_directory
        if not bot_dir:
            return bot_rules
        
        # Load from bot's own rules directory
        bot_rules_dir = bot_dir / 'rules'
        if bot_rules_dir.exists() and bot_rules_dir.is_dir():
            for rule_file in bot_rules_dir.glob('*.json'):
                # Rule object loads its own JSON file and scanner
                rule_obj = Rule(
                    rule_file_path=rule_file,
                    behavior_name='common',
                    bot_name=self.bot_name
                )
                bot_rules.append(rule_obj)
        
        return bot_rules
    
    def _load_behavior_rules(self) -> List['Rule']:
        """Load behavior-specific rules.
        
        Returns:
            List of Rule objects
        """
        from agile_bot.bots.base_bot.src.actions.validate_rules.rule import Rule
        
        behavior_rules = []
        
        # Find behavior folder
        if not self.behavior or not self.bot_paths:
            return behavior_rules
        
        try:
            from agile_bot.bots.base_bot.src.bot.behavior import Behavior
            behavior_folder = Behavior.find_behavior_folder(
                self.bot_paths.bot_directory,
                self.bot_name,
                self.behavior_name
            )
            behavior_rules_dir = behavior_folder / 'rules'
        except FileNotFoundError:
            return behavior_rules
        
        if not behavior_rules_dir.exists():
            return behavior_rules
        
        behavior_file = behavior_rules_dir / 'validation_rules.json'
        if behavior_file.exists():
            behavior_data = read_json_file(behavior_file)
            rules_list = behavior_data.get('rules', [])
            for rule_data in rules_list:
                # Pass rule_content directly for embedded rules
                rule_obj = Rule(
                    rule_file_path=behavior_file,
                    behavior_name=self.behavior_name,
                    bot_name=self.bot_name,
                    rule_content=rule_data
                )
                behavior_rules.append(rule_obj)
        # Otherwise load all .json files from rules directory
        elif behavior_rules_dir.is_dir():
            for rule_file in behavior_rules_dir.glob('*.json'):
                # Rule object loads its own JSON file and scanner
                rule_obj = Rule(
                    rule_file_path=rule_file,
                    behavior_name=self.behavior_name,
                    bot_name=self.bot_name
                )
                behavior_rules.append(rule_obj)
        
        return behavior_rules
    
    def find_by_name(self, rule_name: str) -> Optional['Rule']:
        """Find rule by name.
        
        Domain Model: Find by name: Rule
        
        Args:
            rule_name: Name of rule to find (filename without extension)
            
        Returns:
            Rule object if found, None otherwise.
        """
        rules = self._load_rules()
        for rule in rules:
            if rule.name == rule_name:
                return rule
        return None
    
    def __iter__(self) -> Iterator['Rule']:
        """Iterate all rules.
        
        Domain Model: Iterate: Rule
        
        Yields:
            Rule objects in order (bot-level first, then behavior-specific).
        """
        rules = self._load_rules()
        for rule in rules:
            yield rule
    
    
    @property
    def instructions(self) -> Optional['Rule']:
        """Get instructions rule (first rule with instructions, or None).
        
        Domain Model: Instructions: Injected instructions
        
        Returns:
            First Rule object that has instructions, or None.
        """
        rules = self._load_rules()
        for rule in rules:
            if hasattr(rule, 'instruction') and rule.instruction:
                return rule
        return None
    
    def add_violations(self, violations: List[Dict[str, Any]]) -> None:
        """Add violations from a rule to the collection.
        
        Args:
            violations: List of violation dictionaries to add
        """
        self._all_violations.extend(violations)
    
    @property
    def violations(self) -> List[Dict[str, Any]]:
        """Get all violations from all rules in the collection.
        
        Returns:
            List of all violation dictionaries from all rules.
        """
        return self._all_violations
    
    @property
    def violation_summary(self) -> List[str]:
        """Get summary of violations by rule.
        
        Returns:
            List of summary strings, one per rule with violations.
        """
        summary = []
        for rule in self._load_rules():
            if rule.has_scanner and rule.violations:
                file_by_file_count = len(rule.file_by_file_violations)
                cross_file_count = len(rule.cross_file_violations)
                if file_by_file_count > 0 or cross_file_count > 0:
                    summary.append(
                        f"Rule {rule.rule_file}: "
                        f"{file_by_file_count} file-by-file, {cross_file_count} cross-file violations"
                    )
        return summary
    
    def validate(self, knowledge_graph: Dict[str, Any], files: Optional[Dict[str, List[Path]]] = None) -> List[Dict[str, Any]]:
        """Validate rules against knowledge graph and files.
        
        Iterates over all rules, scans them if they have scanners, and builds
        the processed rules list with scanner results.
        
        Args:
            knowledge_graph: The knowledge graph to validate against
            files: Optional dictionary mapping file type keys to lists of file paths
                   (e.g., {'test': [...], 'src': [...]})
        
        Returns:
            List of rule dictionaries with scanner_results populated
        
        Raises:
            ScannerExecutionError: If a scanner fails to execute or load
        """
        from pathlib import Path
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Import here to avoid circular import
        from agile_bot.bots.base_bot.src.actions.validate_rules.validate_rules_action import ScannerExecutionError
        
        files = files or {}
        processed_rules = []
        
        for rule in self:
            # Build rule result dict from rule properties
            rule_result = {
                'rule_file': rule.rule_file,
                'rule_content': rule.rule_content
            }
            
            # Scan if rule has a scanner
            if rule.has_scanner:
                try:
                    scanner_results = rule.scan(knowledge_graph, files)
                    rule_result['scanner_results'] = scanner_results
                    
                    # Track violations in rules collection
                    self.add_violations(rule.violations)
                except Exception as e:
                    logger.error(f"Scanner execution failed for rule {rule.rule_file}: {e}", exc_info=True)
                    scanner_path = rule.scanner_path if rule else 'unknown'
                    raise ScannerExecutionError(rule.rule_file, scanner_path, e) from e
            elif rule.scanner_path:
                # Scanner failed to load - exceptional circumstance, raise error
                error_msg = f"Scanner failed to load: {rule.scanner_path}"
                logger.error(f"Scanner failed to load for rule {rule.rule_file}: {error_msg}")
                raise ScannerExecutionError(rule.rule_file, rule.scanner_path, RuntimeError(error_msg))
            else:
                # No scanner - empty results
                rule_result['scanner_results'] = {}
            
            processed_rules.append(rule_result)
        
        return processed_rules

