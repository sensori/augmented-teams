"""Scanner for validating natural English usage in code."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class NaturalEnglishCodeScanner(CodeScanner):
    """Validates that code uses natural English for method names, variable names, and relationships."""
    
    TECHNICAL_NOTATION_PATTERNS = [
        r'_0_1$',
        r'_1_star$',
        r'_optional$',
        r'_nullable$',
        r'_\d+$',
    ]
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    violation = self._check_natural_english(node, file_path, rule_obj)
                    if violation:
                        violations.append(violation)
                elif isinstance(node, ast.Name):
                    violation = self._check_variable_name(node, file_path, rule_obj)
                    if violation:
                        violations.append(violation)
        
        except (SyntaxError, UnicodeDecodeError):
            pass
        
        return violations
    
    def _check_natural_english(self, func_node: ast.FunctionDef, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if function name uses natural English."""
        func_name = func_node.name
        
        for pattern in self.TECHNICAL_NOTATION_PATTERNS:
            if re.search(pattern, func_name):
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Function "{func_name}" uses technical notation. Use natural English instead (e.g., "may_find" not "find_optional").',
                    location=str(file_path),
                    line_number=func_node.lineno,
                    severity='warning'
                ).to_dict()
        
        return None
    
    def _check_variable_name(self, name_node: ast.Name, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if variable name uses natural English."""
        var_name = name_node.id
        
        for pattern in self.TECHNICAL_NOTATION_PATTERNS:
            if re.search(pattern, var_name):
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Variable "{var_name}" uses technical notation. Use natural English instead.',
                    location=str(file_path),
                    line_number=name_node.lineno if hasattr(name_node, 'lineno') else None,
                    severity='info'
                ).to_dict()
        
        return None

