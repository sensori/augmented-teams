"""Scanner for validating explicit dependencies in code."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from .code_scanner import CodeScanner
from .violation import Violation


class ExplicitDependenciesScanner(CodeScanner):
    """Validates dependencies are explicit (not hidden)."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            # Check for hidden dependencies (global variables, singletons)
            violations.extend(self._check_hidden_dependencies(tree, file_path, rule_obj))
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_hidden_dependencies(self, tree: ast.AST, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for hidden dependencies (globals, singletons)."""
        violations = []
        
        # Check for global variable usage (hidden dependency)
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                violation = Violation(
                    rule=rule_obj,
                    violation_message=f'Global variable usage detected - dependencies should be explicit (passed as parameters)',
                    location=str(file_path),
                    line_number=node.lineno if hasattr(node, 'lineno') else None,
                    severity='warning'
                ).to_dict()
                violations.append(violation)
        
        return violations

