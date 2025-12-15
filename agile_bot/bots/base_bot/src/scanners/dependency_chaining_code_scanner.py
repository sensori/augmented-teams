"""Scanner for validating dependency chaining in code."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from .code_scanner import CodeScanner
from .violation import Violation


class DependencyChainingCodeScanner(CodeScanner):
    """Validates that code chains dependencies properly with constructor injection."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_violations = self._check_dependency_chaining(node, file_path, rule_obj)
                    violations.extend(class_violations)
        
        except (SyntaxError, UnicodeDecodeError):
            pass
        
        return violations
    
    def _check_dependency_chaining(self, class_node: ast.ClassDef, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check if class chains dependencies properly."""
        violations = []
        
        # Find __init__ method
        init_method = None
        init_params = []
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef) and node.name == '__init__':
                init_method = node
                init_params = [arg.arg for arg in node.args.args if arg.arg != 'self']
                break
        
        if not init_method:
            return violations
        
        # Check other methods for parameters that should be injected
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef) and node.name != '__init__':
                method_params = [arg.arg for arg in node.args.args if arg.arg != 'self']
                
                # Check if method takes parameters that are in __init__ (should use self.param instead)
                for param in method_params:
                    if param in init_params:
                        violations.append(
                            Violation(
                                rule=rule_obj,
                                violation_message=f'Method "{node.name}" in class "{class_node.name}" takes parameter "{param}" that is already injected in __init__. Use self.{param} instead.',
                                location=str(file_path),
                                line_number=node.lineno,
                                severity='warning'
                            ).to_dict()
                        )
        
        return violations


