"""Scanner for validating objects are preferred over primitives in method signatures."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .code_scanner import CodeScanner
from .violation import Violation


class PrimitiveVsObjectScanner(CodeScanner):
    """Validates that methods prefer objects over primitives in signatures.
    
    This scanner detects when methods are passing primitives (especially IDs)
    when they should be passing domain objects. It allows primitives at
    presentation boundaries (UI/CLI rendering methods).
    """
    
    # Primitive type names that suggest objects should be used instead
    PRIMITIVE_TYPES = {'str', 'int', 'float', 'bool', 'dict', 'Dict', 'list', 'List', 'tuple', 'Tuple'}
    
    # Presentation boundary method name patterns (primitives OK here)
    PRESENTATION_METHOD_PATTERNS = [
        r'render', r'format', r'to_string', r'to_dict', r'to_json', r'to_xml',
        r'display', r'print', r'show', r'cli', r'ui', r'html', r'json',
        r'str\(', r'__str__', r'__repr__', r'serialize', r'marshal'
    ]
    
    # Parameter name patterns that suggest an object should be passed instead
    OBJECT_SUGGESTING_PATTERNS = [
        r'_id$',  # customer_id, order_id, etc.
        r'_ids$',  # customer_ids, order_ids, etc.
        r'_name$',  # customer_name, order_name (when customer/order object exists)
        r'_email$',  # customer_email (when customer object exists)
    ]
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        # Skip test files - they may use different patterns
        if self._is_test_file(file_path):
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_violations = self._check_function_parameters(node, content, file_path, rule_obj)
                    violations.extend(func_violations)
                    
                    return_violation = self._check_return_type(node, content, file_path, rule_obj)
                    if return_violation:
                        violations.append(return_violation)
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file and should be skipped."""
        path_str = str(file_path).lower()
        file_name = file_path.name.lower()
        
        # Skip test directories (but not if 'test' is part of a larger word like 'test_bot' or temp directory)
        # Only skip if '/test/' or '/tests/' or '\\test\\' or '\\tests\\' appears as directory separators
        import re
        if re.search(r'[/\\]test[/\\]', path_str) or re.search(r'[/\\]tests[/\\]', path_str):
            return True
        
        # Skip test files (files starting with test_)
        if file_name.startswith('test_'):
            return True
        
        # Skip conftest files
        if file_name == 'conftest.py':
            return True
        
        return False
    
    def _is_presentation_boundary(self, func_name: str, content: str, func_node: ast.FunctionDef) -> bool:
        """Check if function is at a presentation boundary where primitives are acceptable."""
        func_name_lower = func_name.lower()
        
        # Check method name patterns
        for pattern in self.PRESENTATION_METHOD_PATTERNS:
            if re.search(pattern, func_name_lower):
                return True
        
        # Check if function body contains presentation-related operations
        func_source = ast.get_source_segment(content, func_node) or ''
        presentation_keywords = ['print(', 'display', 'render', 'format', 'to_string', 'to_dict', 'cli', 'ui']
        if any(keyword in func_source.lower() for keyword in presentation_keywords):
            return True
        
        return False
    
    def _check_function_parameters(self, func_node: ast.FunctionDef, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check if function parameters should be objects instead of primitives."""
        violations = []
        
        # Skip presentation boundary methods
        if self._is_presentation_boundary(func_node.name, content, func_node):
            return violations
        
        # Skip __init__ methods - they often need primitives for construction
        if func_node.name == '__init__':
            return violations
        
        # Check each parameter
        for arg in func_node.args.args:
            # Skip self and cls
            if arg.arg in ('self', 'cls'):
                continue
            
            # Check if parameter has type annotation
            if arg.annotation:
                type_name = self._extract_type_name(arg.annotation, content)
                
                # Check if it's a primitive type
                if type_name and type_name in self.PRIMITIVE_TYPES:
                    # Check if parameter name suggests it should be an object
                    if self._suggests_object_should_be_passed(arg.arg):
                        line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
                        violation = Violation(
                            rule=rule_obj,
                            violation_message=f'Function "{func_node.name}" takes primitive "{arg.arg}: {type_name}" - consider passing domain object instead',
                            location=str(file_path),
                            line_number=line_number,
                            severity='warning'
                        ).to_dict()
                        violations.append(violation)
            
            # Even without type annotation, check parameter name patterns
            elif self._suggests_object_should_be_passed(arg.arg):
                line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
                violation = Violation(
                    rule=rule_obj,
                    violation_message=f'Function "{func_node.name}" takes "{arg.arg}" which suggests a primitive ID - consider passing domain object instead',
                    location=str(file_path),
                    line_number=line_number,
                    severity='warning'
                ).to_dict()
                violations.append(violation)
        
        return violations
    
    def _check_return_type(self, func_node: ast.FunctionDef, content: str, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if function return type should be an object instead of primitives."""
        # Skip presentation boundary methods
        if self._is_presentation_boundary(func_node.name, content, func_node):
            return None
        
        # Check return annotation
        if func_node.returns:
            return_type_name = self._extract_type_name(func_node.returns, content)
            
            # Check if returning Dict/List when it could be an object
            if return_type_name in ('Dict', 'dict', 'List', 'list', 'tuple', 'Tuple'):
                # Check if function name suggests it should return an object
                func_name_lower = func_node.name.lower()
                object_return_patterns = ['create', 'build', 'make', 'get', 'find', 'load', 'process', 'generate']
                
                if any(pattern in func_name_lower for pattern in object_return_patterns):
                    line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
                    return Violation(
                        rule=rule_obj,
                        violation_message=f'Function "{func_node.name}" returns "{return_type_name}" - consider returning domain object instead',
                        location=str(file_path),
                        line_number=line_number,
                        severity='warning'
                    ).to_dict()
        
        return None
    
    def _extract_type_name(self, annotation_node: ast.AST, content: str) -> Optional[str]:
        """Extract type name from annotation node."""
        if isinstance(annotation_node, ast.Name):
            return annotation_node.id
        elif isinstance(annotation_node, ast.Subscript):
            # Handle Dict[str, Any], List[str], etc.
            if isinstance(annotation_node.value, ast.Name):
                return annotation_node.value.id
        elif isinstance(annotation_node, ast.Attribute):
            # Handle typing.Dict, typing.List, etc.
            return annotation_node.attr
        
        return None
    
    def _suggests_object_should_be_passed(self, param_name: str) -> bool:
        """Check if parameter name suggests an object should be passed instead."""
        param_name_lower = param_name.lower()
        
        # Check for ID patterns
        for pattern in self.OBJECT_SUGGESTING_PATTERNS:
            if re.search(pattern, param_name_lower):
                return True
        
        return False

