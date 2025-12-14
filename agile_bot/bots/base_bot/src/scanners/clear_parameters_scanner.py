"""Scanner for validating function parameters are clear."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from .code_scanner import CodeScanner
from .violation import Violation


class ClearParametersScanner(CodeScanner):
    """Validates function parameters are clear and well-named."""
    
    def __init__(self):
        super().__init__()
        self.knowledge_graph = None
    
    def scan(self, knowledge_graph: Dict[str, Any], rule_obj: Any = None, test_files: Optional[List['Path']] = None, code_files: Optional[List['Path']] = None) -> List[Dict[str, Any]]:
        """Override scan to store knowledge_graph for use in scan_code_file."""
        self.knowledge_graph = knowledge_graph
        return super().scan(knowledge_graph, rule_obj, test_files=test_files, code_files=code_files)
    
    # Acceptable parameter names in specific contexts
    ACCEPTABLE_PARAMETER_NAMES = {
        'data',  # Acceptable in data processing/transformation functions
        'value',  # Acceptable in transformation/validation functions
        'item',  # Acceptable in iteration/callback functions
        'obj',  # Acceptable in generic object manipulation functions
        'param',  # Acceptable in parameter forwarding functions
        'arg',  # Acceptable in argument forwarding functions
        'kwargs', 'args',  # Standard Python parameter names
        'self', 'cls',  # Standard Python method parameters
    }
    
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        # Skip test files - they may use different parameter naming conventions
        if self._is_test_file(file_path):
            return violations
        
        # Extract domain terms from knowledge graph
        domain_terms = set()
        if self.knowledge_graph:
            domain_terms = self._extract_domain_terms(self.knowledge_graph)
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    violation = self._check_parameters(node, file_path, rule_obj, domain_terms)
                    if violation:
                        violations.append(violation)
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file and should be skipped."""
        path_str = str(file_path).lower()
        file_name = file_path.name.lower()
        
        # Skip test directories
        if '/test' in path_str or '/tests' in path_str or '\\test' in path_str or '\\tests' in path_str:
            return True
        
        # Skip test files (files starting with test_)
        if file_name.startswith('test_'):
            return True
        
        # Skip conftest files
        if file_name == 'conftest.py':
            return True
        
        return False
    
    def _check_parameters(self, func_node: ast.FunctionDef, file_path: Path, rule_obj: Any, domain_terms: set = None) -> Optional[Dict[str, Any]]:
        """Check if function parameters are clear."""
        if domain_terms is None:
            domain_terms = set()
        
        # Check for too many parameters (hard to understand)
        # Allow more parameters for initialization functions (__init__)
        max_params = 7 if func_node.name == '__init__' else 5
        if len(func_node.args.args) > max_params:
            line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
            return Violation(
                rule=rule_obj,
                violation_message=f'Function "{func_node.name}" has {len(func_node.args.args)} parameters - consider using parameter object or reducing parameters',
                location=str(file_path),
                line_number=line_number,
                severity='warning'
            ).to_dict()
        
        # Check for vague parameter names (excluding acceptable ones and domain terms)
        vague_names = ['thing', 'stuff', 'info']  # Removed acceptable names from list
        for arg in func_node.args.args:
            # Skip standard Python parameters
            if arg.arg in ['self', 'cls', 'args', 'kwargs']:
                continue
            
            arg_name_lower = arg.arg.lower()
            
            # Check if parameter name is a domain term (acceptable)
            if arg_name_lower in domain_terms:
                continue  # Domain term - acceptable
            
            # Check if parameter name contains domain terms (e.g., "planning_data", "agent_config")
            if domain_terms:
                arg_words = arg_name_lower.split('_')
                if any(word in domain_terms for word in arg_words):
                    continue  # Contains domain term - likely acceptable
            
            # Check if it's an acceptable parameter name in context
            if arg_name_lower in self.ACCEPTABLE_PARAMETER_NAMES:
                # Only flag if function name doesn't provide context
                # (e.g., "process_data(data)" is OK, but "process(data)" might need better name)
                if not self._function_name_provides_context(func_node.name, arg.arg):
                    continue
            
            if arg_name_lower in vague_names:
                line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Function "{func_node.name}" has vague parameter name "{arg.arg}" - use descriptive name',
                    location=str(file_path),
                    line_number=line_number,
                    severity='warning'
                ).to_dict()
        
        return None
    
    def _function_name_provides_context(self, func_name: str, param_name: str) -> bool:
        """Check if function name provides enough context for a generic parameter name.
        
        For example, "process_data(data)" provides context, but "process(data)" doesn't.
        """
        func_name_lower = func_name.lower()
        param_name_lower = param_name.lower()
        
        # If function name contains the parameter name or related terms, it provides context
        # e.g., "process_data" provides context for "data" parameter
        if param_name_lower in func_name_lower:
            return True
        
        # Check for related terms
        context_map = {
            'data': ['data', 'datum', 'content', 'payload'],
            'value': ['value', 'val', 'result', 'output'],
            'item': ['item', 'element', 'entry', 'record'],
            'obj': ['obj', 'object', 'instance', 'entity'],
        }
        
        if param_name_lower in context_map:
            for related_term in context_map[param_name_lower]:
                if related_term in func_name_lower:
                    return True
        
        return False

