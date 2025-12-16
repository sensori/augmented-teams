"""Scanner for validating delegation to lowest-level objects in code."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from .code_scanner import CodeScanner
from .violation import Violation


class DelegationCodeScanner(CodeScanner):
    """Validates that code delegates responsibilities to the lowest-level object."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_violations = self._check_delegation(node, content, file_path, rule_obj)
                    violations.extend(class_violations)
        
        except (SyntaxError, UnicodeDecodeError):
            pass
        
        return violations
    
    def _check_delegation(self, class_node: ast.ClassDef, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check if class delegates properly."""
        violations = []
        
        # Check for methods that iterate through collections instead of delegating
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef):
                # Check if method iterates through self.collection instead of delegating
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.For):
                        # Check if it's iterating through a collection attribute
                        if isinstance(stmt.iter, ast.Attribute):
                            if isinstance(stmt.iter.value, ast.Name) and stmt.iter.value.id == 'self':
                                # This might be doing what collection should do
                                collection_name = stmt.iter.attr
                                if self._is_collection_name(collection_name):
                                    violations.append(
                                        Violation(
                                            rule=rule_obj,
                                            violation_message=f'Method "{node.name}" in class "{class_node.name}" iterates through "{collection_name}" instead of delegating to collection class. Delegate to collection class instead.',
                                            location=str(file_path),
                                            line_number=stmt.lineno,
                                            severity='info'
                                        ).to_dict()
                                    )
        
        return violations
    
    def _is_collection_name(self, name: str) -> bool:
        """Check if name indicates a collection."""
        name_lower = name.lower()
        return (name_lower.endswith('s') and len(name_lower) > 3) or 'collection' in name_lower or 'list' in name_lower




