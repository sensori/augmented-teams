from __future__ import annotations

from typing import List, Optional, Iterator, Dict, Any, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from agile_bot.bots.base_bot.src.actions.validate.rule import Rule


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
        
        self._rules: Optional[List['Rule']] = None
        self._all_violations: List[Dict[str, Any]] = []
    
    def _load_rules(self) -> List['Rule']:
        if self._rules is not None:
            return self._rules
        
        from agile_bot.bots.base_bot.src.actions.validate.rule import Rule
        
        all_rules = []
        bot_rules = self._load_bot_rules()
        all_rules.extend(bot_rules)
        
        if self.behavior:
            behavior_rules = self._load_behavior_rules()
            all_rules.extend(behavior_rules)
        
        self._rules = all_rules
        return self._rules
    
    def _load_bot_rules(self) -> List['Rule']:
        from agile_bot.bots.base_bot.src.actions.validate.rule import Rule
        
        bot_rules = []
        bot_dir = self.bot_paths.bot_directory
        bot_rules_dir = bot_dir / 'rules'
        for rule_file in bot_rules_dir.glob('*.json'):
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
        behavior_folder = self.bot_paths.bot_directory / 'behaviors' / self.behavior_name
        behavior_rules_dir = behavior_folder / 'rules'
        
        for rule_file in behavior_rules_dir.glob('*.json'):
            rule_obj = Rule(
                rule_file_path=rule_file,
                behavior_name=self.behavior_name,
                bot_name=self.bot_name
            )
            behavior_rules.append(rule_obj)
        
        rule_subdirs = ['3_rules', 'rules']
        for subdir_name in rule_subdirs:
            subdir = behavior_folder / subdir_name
            if subdir != behavior_rules_dir:
                for rule_file in subdir.rglob('*.json'):
                    if behavior_rules_dir.exists() and rule_file.is_relative_to(behavior_rules_dir):
                        continue
                    try:
                        rule_obj = Rule(
                            rule_file_path=rule_file,
                            behavior_name=self.behavior_name,
                            bot_name=self.bot_name
                        )
                        behavior_rules.append(rule_obj)
                    except Exception:
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
        
        from agile_bot.bots.base_bot.src.actions.validate.validate_action import ScannerExecutionError
        
        files = files or {}
        processed_rules = []
        
        for rule in self:
            rule_result = {
                'rule_file': rule.rule_file,
                'rule_content': rule.rule_content
            }
            
            if rule.has_scanner:
                try:
                    scanner_results = rule.scan(knowledge_graph, files)
                    rule_result['scanner_results'] = scanner_results
                    self.add_violations(rule.violations)
                except Exception as e:
                    logger.error(f"Scanner execution failed for rule {rule.rule_file}: {e}", exc_info=True)
                    scanner_path = rule.scanner_path if rule else 'unknown'
                    raise ScannerExecutionError(rule.rule_file, scanner_path, e) from e
            elif rule.scanner_path:
                error_msg = f"Scanner failed to load: {rule.scanner_path}"
                logger.error(f"Scanner failed to load for rule {rule.rule_file}: {error_msg}")
                raise ScannerExecutionError(rule.rule_file, rule.scanner_path, RuntimeError(error_msg))
            else:
                rule_result['scanner_results'] = {}
            
            processed_rules.append(rule_result)
        
        return processed_rules
