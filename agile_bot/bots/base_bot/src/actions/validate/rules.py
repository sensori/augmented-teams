from __future__ import annotations

from typing import List, Optional, Iterator, Dict, Any
from pathlib import Path


class Rules:
    def __init__(self, behavior=None, bot_config=None, bot_paths=None):
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
        if self._rules is not None:
            return self._rules
        
        # Import here to avoid circular import
        from agile_bot.bots.base_bot.src.actions.validate.rule import Rule
        
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
        from agile_bot.bots.base_bot.src.actions.validate.rule import Rule
        
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
        from agile_bot.bots.base_bot.src.actions.validate.rule import Rule
        
        behavior_rules = []
        
        # Find behavior folder
        if not self.behavior or not self.bot_paths:
            return behavior_rules
        
       
        behavior_folder = self.bot_paths.bot_directory / 'behaviors' / self.behavior_name
        behavior_rules_dir = behavior_folder / 'rules'
        
        # Load all .json files from rules directory if it exists
        if behavior_rules_dir.exists() and behavior_rules_dir.is_dir():
            for rule_file in behavior_rules_dir.glob('*.json'):
                # Rule object loads its own JSON file and scanner
                rule_obj = Rule(
                    rule_file_path=rule_file,
                    behavior_name=self.behavior_name,
                    bot_name=self.bot_name
                )
                behavior_rules.append(rule_obj)
        
        # Also check for rules in specific rule subdirectories (e.g., 3_rules)
        # This handles cases where rules are organized in subdirectories
        # Only check known rule subdirectories to avoid loading guardrails/config files
        rule_subdirs = ['3_rules', 'rules']
        if behavior_folder.exists():
            for subdir_name in rule_subdirs:
                subdir = behavior_folder / subdir_name
                if subdir.exists() and subdir.is_dir() and subdir != behavior_rules_dir:
                    # Check if this subdirectory contains rule files
                    for rule_file in subdir.rglob('*.json'):
                        # Skip if this file was already loaded from rules directory
                        if behavior_rules_dir.exists() and rule_file.is_relative_to(behavior_rules_dir):
                            continue
                        # Rule object loads its own JSON file and scanner
                        # Add rules even if they don't have scanners (they provide context)
                        try:
                            rule_obj = Rule(
                                rule_file_path=rule_file,
                                behavior_name=self.behavior_name,
                                bot_name=self.bot_name
                            )
                            # Add all rules (with or without scanners) - rules without scanners still provide context
                            behavior_rules.append(rule_obj)
                        except Exception:
                            # Skip files that can't be loaded as rules
                            continue
        
        return behavior_rules
    
    def find_by_name(self, rule_name: str) -> Optional['Rule']:
        rules = self._load_rules()
        for rule in rules:
            if rule.name == rule_name:
                return rule
        return None
    
    def __iter__(self) -> Iterator['Rule']:
        rules = self._load_rules()
        for rule in rules:
            yield rule
    
    def __len__(self) -> int:
        """Return the number of rules."""
        return len(self._load_rules())
    
    def add_violations(self, violations: List[Dict[str, Any]]) -> None:
        self._all_violations.extend(violations)
    
    @property
    def violations(self) -> List[Dict[str, Any]]:
        return self._all_violations
    
    @property
    def violation_summary(self) -> List[str]:
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
    
    def formatted_rules(self) -> str:
        rules = self._load_rules()
        if not rules:
            return "No validation rules found."
        
        formatted_sections = []
        bot_rules = []
        behavior_rules = []
        
        for rule in rules:
            rule_file = rule.rule_file
            
            if 'base_bot/rules' in rule_file or (not 'behaviors' in rule_file and '/rules/' in rule_file):
                bot_rules.append(rule)
            else:
                behavior_rules.append(rule)
        
        if bot_rules:
            formatted_sections.append("**Bot-level rules:**")
            for rule in bot_rules:
                formatted_sections.extend(rule.formatted_text())
        
        if behavior_rules:
            formatted_sections.append("**Behavior-level rules:**")
            for rule in behavior_rules:
                formatted_sections.extend(rule.formatted_text())
        
        if not formatted_sections:
            return "No validation rules found."
        
        return "\n".join(formatted_sections)
    
    def validate(self, knowledge_graph: Dict[str, Any], files: Optional[Dict[str, List[Path]]] = None) -> List[Dict[str, Any]]:
        from pathlib import Path
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Import here to avoid circular import
        from agile_bot.bots.base_bot.src.actions.validate.validate_action import ScannerExecutionError
        
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

