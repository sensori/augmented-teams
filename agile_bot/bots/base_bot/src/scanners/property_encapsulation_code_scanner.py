"""Scanner for validating property encapsulation in code."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class PropertyEncapsulationCodeScanner(CodeScanner):
    """Validates that code encapsulates state and behavior through properties."""
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_violations = self._check_encapsulation(node, content, file_path, rule_obj)
                    violations.extend(class_violations)
        
        except (SyntaxError, UnicodeDecodeError):
            pass
        
        return violations
    
    def _check_encapsulation(self, class_node: ast.ClassDef, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check if class follows property encapsulation."""
        violations = []
        class_source = ast.get_source_segment(content, class_node) or ''
        
        # Check for public fields (no _ prefix) that should be private
        for node in ast.walk(class_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        field_name = target.id
                        # Check if it's a public field (no _ prefix) assigned in __init__
                        if not field_name.startswith('_') and not field_name.startswith('__'):
                            # Check if it's in __init__
                            parent = self._get_parent_function(node)
                            if parent and isinstance(parent, ast.FunctionDef) and parent.name == '__init__':
                                violations.append(
                                    Violation(
                                        rule=rule_obj,
                                        violation_message=f'Class "{class_node.name}" has public field "{field_name}". Use private field (prefix with _) and expose via property if needed.',
                                        location=str(file_path),
                                        line_number=node.lineno,
                                        severity='warning'
                                    ).to_dict()
                                )
        
        # Check for methods that return mutable references
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                # Check if method returns self.attribute directly (mutable reference)
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Return) and stmt.value:
                        if isinstance(stmt.value, ast.Attribute):
                            violations.append(
                                Violation(
                                    rule=rule_obj,
                                    violation_message=f'Method "{node.name}" in class "{class_node.name}" returns mutable reference. Return defensive copy or use property.',
                                    location=str(file_path),
                                    line_number=stmt.lineno,
                                    severity='warning'
                                ).to_dict()
                            )
        
        # Check for calculate/compute methods that should be properties
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef):
                method_name_lower = node.name.lower()
                if method_name_lower.startswith(('calculate_', 'compute_', 'derive_')):
                    # Check if it takes no self parameters (besides self)
                    if len(node.args.args) <= 1:  # Only self
                        violations.append(
                            Violation(
                                rule=rule_obj,
                                violation_message=f'Method "{node.name}" in class "{class_node.name}" should be a property instead of a method (use @property decorator).',
                                location=str(file_path),
                                line_number=node.lineno,
                                severity='warning'
                            ).to_dict()
                        )
        
        return violations
    
    def _get_parent_function(self, node: ast.AST) -> Optional[ast.FunctionDef]:
        """Get the parent function of a node."""
        for parent in ast.walk(node):
            if isinstance(parent, ast.FunctionDef):
                for child in ast.walk(parent):
                    if child == node:
                        return parent
        return None


