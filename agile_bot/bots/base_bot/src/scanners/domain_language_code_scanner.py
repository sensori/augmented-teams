"""Scanner for validating domain-specific language in code."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class DomainLanguageCodeScanner(CodeScanner):
    """Validates that code uses domain-specific language, not generic terms."""
    
    GENERIC_TERMS = ['data', 'config', 'parameter', 'result']
    GENERATE_PATTERNS = [r'^generate_', r'^calculate_']
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_violations = self._check_domain_language(node, file_path, rule_obj)
                    violations.extend(class_violations)
                elif isinstance(node, ast.FunctionDef):
                    func_violation = self._check_function_domain_language(node, file_path, rule_obj)
                    if func_violation:
                        violations.append(func_violation)
        
        except (SyntaxError, UnicodeDecodeError):
            pass
        
        return violations
    
    def _check_domain_language(self, class_node: ast.ClassDef, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check if class uses domain-specific language."""
        violations = []
        class_name_lower = class_node.name.lower()
        
        # Check class name for generic terms
        for term in self.GENERIC_TERMS:
            if term in class_name_lower and not self._is_domain_specific(class_node.name):
                violations.append(
                    Violation(
                        rule=rule_obj,
                        violation_message=f'Class "{class_node.name}" uses generic term "{term}". Use domain-specific language instead.',
                        location=str(file_path),
                        line_number=class_node.lineno,
                        severity='warning'
                    ).to_dict()
                )
        
        return violations
    
    def _check_function_domain_language(self, func_node: ast.FunctionDef, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if function uses domain-specific language."""
        func_name_lower = func_node.name.lower()
        
        # Check for generate/calculate patterns
        for pattern in self.GENERATE_PATTERNS:
            if re.search(pattern, func_name_lower):
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Function "{func_node.name}" uses generate/calculate. Use property instead (e.g., "recommended_trades" not "generate_recommendation").',
                    location=str(file_path),
                    line_number=func_node.lineno,
                    severity='warning'
                ).to_dict()
        
        # Check parameters for generic terms
        for arg in func_node.args.args:
            if arg.arg.lower() in self.GENERIC_TERMS:
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Function "{func_node.name}" uses generic parameter name "{arg.arg}". Use domain-specific language instead.',
                    location=str(file_path),
                    line_number=func_node.lineno,
                    severity='warning'
                ).to_dict()
        
        return None
    
    def _is_domain_specific(self, name: str) -> bool:
        """Check if name contains domain-specific context."""
        # Simple heuristic: if it's just "Data" or "Config" it's generic
        return len(name.split()) > 1 or name.lower() not in ['data', 'config', 'parameter', 'result']




