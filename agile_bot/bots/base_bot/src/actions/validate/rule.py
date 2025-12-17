from pathlib import Path
from typing import Dict, Any, List, Optional
from agile_bot.bots.base_bot.src.utils import read_json_file


class Rule:
    def __init__(self, rule_file_path: Path, behavior_name: str, bot_name: str, rule_content: Optional[Dict[str, Any]] = None):
        self._rule_file_path = Path(rule_file_path)
        self._behavior_name = behavior_name
        self._bot_name = bot_name
    
        if rule_content is not None:
            self._rule_content = rule_content
            self._rule_file = f"{self._rule_file_path.name}#embedded"
            self._name = rule_content.get('name', 'unknown') or self._rule_file_path.stem
        else:
            self._rule_content = read_json_file(self._rule_file_path)
            self._rule_file = self._rule_file_path.name
            self._name = self._rule_file.replace('.json', '') if self._rule_file else 'unknown'
        
        scanner_path = self._rule_content.get('scanner')
        if scanner_path:
            self._scanner = self._load_scanner(scanner_path)
        else:
            self._scanner = None
        
        self._file_by_file_violations: List[Dict[str, Any]] = []
        self._cross_file_violations: List[Dict[str, Any]] = []
        self._scan_error: Optional[str] = None
    
    def _load_scanner(self, scanner_module_path: str) -> Optional[type]:
        from agile_bot.bots.base_bot.src.actions.validate.scanners.scanner_loader import ScannerLoader
        
        scanner_loader = ScannerLoader(self._bot_name)
        return scanner_loader.load_scanner(scanner_module_path)
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def rule_file(self) -> str:
        return self._rule_file
    
    @property
    def behavior_name(self) -> str:
        return self._behavior_name
    
    @property
    def scanner(self):
        if not self._scanner:
            return None
        return self._scanner()
    
    @property
    def scanner_class(self) -> Optional[type]:
        return self._scanner
    
    @property
    def description(self) -> str:
        return self._rule_content.get('description', '')
    
    @property
    def examples(self) -> List[Dict[str, Any]]:
        return self._rule_content.get('examples', [])
    
    @property
    def scanner_path(self) -> Optional[str]:
        return self._rule_content.get('scanner')
    
    @property
    def rule_content(self) -> Dict[str, Any]:
        return self._rule_content
    
    @property
    def instruction(self) -> Optional[str]:
        return self._rule_content.get('instruction')
    
    @property
    def has_scanner(self) -> bool:
        return self._scanner is not None
    
    @property
    def requires_two_pass_scan(self) -> bool:
        if not self._scanner:
            return False
        
        # Check if scanner is a CodeScanner or TestScanner from the validate scanners module
        from agile_bot.bots.base_bot.src.actions.validate.scanners.code_scanner import CodeScanner
        from agile_bot.bots.base_bot.src.actions.validate.scanners.test_scanner import TestScanner
        
        return (
            issubclass(self._scanner, TestScanner) or 
            issubclass(self._scanner, CodeScanner)
        )
    
    def scan(self, knowledge_graph: Dict[str, Any], files: Optional[Dict[str, List[Path]]] = None) -> Dict[str, Any]:
        files = files or {}
        test_files = files.get('test', [])
        code_files = files.get('src', [])
        
        self._file_by_file_violations = []
        self._cross_file_violations = []
        self._scan_error = None
        
        if not self.has_scanner:
            return {}
        
        try:
            scanner_instance = self.scanner
            if not scanner_instance:
                return {}
            
            violations_file_by_file = scanner_instance.scan(
                knowledge_graph,
                rule_obj=self,
                test_files=test_files,
                code_files=code_files
            )
            
            if violations_file_by_file is not None:
                if isinstance(violations_file_by_file, list):
                    self._file_by_file_violations = violations_file_by_file
                else:
                    self._file_by_file_violations = [violations_file_by_file] if violations_file_by_file else []
            else:
                self._file_by_file_violations = []
            
            if not hasattr(self, '_file_by_file_violations') or self._file_by_file_violations is None:
                self._file_by_file_violations = []
            
            if self.requires_two_pass_scan and files and hasattr(scanner_instance, 'scan_cross_file'):
                violations_cross_file = scanner_instance.scan_cross_file(
                    rule_obj=self,
                    test_files=test_files,
                    code_files=code_files
                )
                
                if violations_cross_file:
                    self._cross_file_violations = violations_cross_file
            
            if self.requires_two_pass_scan:
                return {
                    'file_by_file': {'violations': self._file_by_file_violations},
                    'cross_file': {'violations': self._cross_file_violations}
                }
            else:
                return {
                    'violations': self._file_by_file_violations
                }
        
        except Exception as e:
            self._scan_error = str(e)
            
            if self.requires_two_pass_scan:
                return {
                    'file_by_file': {'violations': [], 'error': self._scan_error},
                    'cross_file': {'violations': []}
                }
            else:
                return {
                    'violations': [],
                    'error': self._scan_error
                }
    
    @property
    def violations(self) -> List[Dict[str, Any]]:
        all_violations = []
        if hasattr(self, '_file_by_file_violations'):
            all_violations.extend(self._file_by_file_violations)
        if hasattr(self, '_cross_file_violations'):
            all_violations.extend(self._cross_file_violations)
        return all_violations
    
    @property
    def file_by_file_violations(self) -> List[Dict[str, Any]]:
        return getattr(self, '_file_by_file_violations', [])
    
    @property
    def cross_file_violations(self) -> List[Dict[str, Any]]:
        return getattr(self, '_cross_file_violations', [])
    
    @property
    def scanner_results(self) -> Dict[str, Any]:
        if not hasattr(self, '_file_by_file_violations'):
            return {}
        
        if self.requires_two_pass_scan:
            result = {
                'file_by_file': {'violations': self._file_by_file_violations},
                'cross_file': {'violations': self._cross_file_violations}
            }
            if self._scan_error:
                result['file_by_file']['error'] = self._scan_error
            return result
        else:
            result = {'violations': self._file_by_file_violations}
            if self._scan_error:
                result['error'] = self._scan_error
            return result
    
    def formatted_text(self) -> List[str]:
        formatted = []
        
        rule_description = self.description
        
        formatted.append(f"\n**Rule:** {self.rule_file}")
        if rule_description:
            formatted.append(f"{rule_description}")
        
        if 'do' in self._rule_content:
            do_examples = self._rule_content.get('do', {}).get('examples', [])
            if do_examples:
                formatted.append("\n**DO:**")
                for example in do_examples:
                    desc = example.get('description', '')
                    content = example.get('content', '')
                    if isinstance(content, list):
                        content = '\n'.join(content)
                    if desc:
                        formatted.append(f"- {desc}: {content}")
                    else:
                        formatted.append(f"- {content}")
        
        if 'dont' in self._rule_content:
            dont_examples = self._rule_content.get('dont', {}).get('examples', [])
            if dont_examples:
                formatted.append("\n**DON'T:**")
                for example in dont_examples:
                    desc = example.get('description', '')
                    content = example.get('content', '')
                    if isinstance(content, list):
                        content = '\n'.join(content)
                    if desc:
                        formatted.append(f"- {desc}: {content}")
                    else:
                        formatted.append(f"- {content}")
        
        if 'examples' in self._rule_content:
            examples = self._rule_content.get('examples', [])
            for example in examples:
                if 'do' in example:
                    do_content = example.get('do', {})
                    desc = do_content.get('description', '')
                    content = do_content.get('content', '')
                    if isinstance(content, list):
                        content = '\n'.join(content)
                    formatted.append(f"\n**DO:** {desc}")
                    formatted.append(content)
                if 'dont' in example:
                    dont_content = example.get('dont', {})
                    desc = dont_content.get('description', '')
                    content = dont_content.get('content', '')
                    if isinstance(content, list):
                        content = '\n'.join(content)
                    formatted.append(f"\n**DON'T:** {desc}")
                    formatted.append(content)
        
        formatted.append("")
        return formatted
