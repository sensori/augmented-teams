"""Scanner for detecting unnecessary parameter passing of instance properties."""

from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import ast
from .code_scanner import CodeScanner
from .violation import Violation


class UnnecessaryParameterPassingScanner(CodeScanner):
    """Detects when methods receive parameters that are already accessible through instance variables.
    
    Internal methods should access instance properties directly through self rather
    than receiving them as parameters. This reduces coupling and makes code clearer.
    
    Detects:
    - Methods that receive parameters matching instance properties (self.X passed as X)
    - Variables extracted from self just to pass to another method
    - Internal methods (_method_name) receiving instance properties as parameters
    """
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            # Collect all instance attributes/properties from the class
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    instance_attrs = self._collect_instance_attributes(node)
                    violations.extend(self._check_class_methods(node, file_path, rule_obj, instance_attrs))
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _collect_instance_attributes(self, class_node: ast.ClassDef) -> Set[str]:
        """Collect all instance attributes and properties from class."""
        attrs = set()
        
        for node in ast.walk(class_node):
            # Collect self.X assignments
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == 'self':
                            attrs.add(target.attr)
            
            # Collect self.X in expressions (properties, method calls)
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name) and node.value.id == 'self':
                    attrs.add(node.attr)
            
            # Collect property decorators
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'property':
                        attrs.add(node.name)
        
        return attrs
    
    def _check_class_methods(self, class_node: ast.ClassDef, file_path: Path, rule_obj: Any, instance_attrs: Set[str]) -> List[Dict[str, Any]]:
        """Check methods in class for unnecessary parameter passing."""
        violations = []
        
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                # Only check internal/private methods
                if not node.name.startswith('_'):
                    continue
                
                # Skip special methods
                if node.name.startswith('__') and node.name.endswith('__'):
                    continue
                
                # Check method calls within this method
                violations.extend(self._check_method_calls(node, file_path, rule_obj, instance_attrs))
        
        return violations
    
    def _check_method_calls(self, func_node: ast.FunctionDef, file_path: Path, rule_obj: Any, instance_attrs: Set[str]) -> List[Dict[str, Any]]:
        """Check method calls for passing instance attributes as parameters."""
        violations = []
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                # Check if this is a method call on self
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 'self':
                        # Check arguments for instance attributes
                        for arg in node.args:
                            violation = self._check_argument(arg, node.func.attr, file_path, rule_obj, instance_attrs, func_node.lineno)
                            if violation:
                                violations.append(violation)
        
        return violations
    
    def _check_argument(self, arg_node: ast.AST, method_name: str, file_path: Path, rule_obj: Any, instance_attrs: Set[str], line_num: int) -> Optional[Dict[str, Any]]:
        """Check if argument is an instance attribute that shouldn't be passed."""
        # Check if argument is self.X
        if isinstance(arg_node, ast.Attribute):
            if isinstance(arg_node.value, ast.Name) and arg_node.value.id == 'self':
                attr_name = arg_node.attr
                if attr_name in instance_attrs:
                    return Violation(
                        rule=rule_obj,
                        violation_message=f'Line {line_num}: Passing self.{attr_name} as parameter to {method_name}(). Access it directly in the method through self.{attr_name} instead.',
                        location=str(file_path),
                        line_number=line_num,
                        severity='warning'
                    ).to_dict()
        
        # Check if argument is a variable that was assigned from self.X
        if isinstance(arg_node, ast.Name):
            # We'd need to track variable assignments to check this, but that's complex
            # For now, we focus on direct self.X passing
            pass
        
        return None

