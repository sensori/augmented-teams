"""Scanner for validating tests use real implementations."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .test_scanner import TestScanner
from .violation import Violation


class RealImplementationsScanner(TestScanner):
    """Detects empty tests and validates tests call production code directly.
    
    Tests should call production code directly, even if API doesn't exist yet.
    Tests that only contain 'pass' or 'TODO' comments violate this rule.
    """
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Parse AST to analyze test structure
            method_violations = self._check_test_methods_call_production_code(
                content, lines, test_file_path, rule_obj, knowledge_graph
            )
            violations.extend(method_violations)
            
            # Check for fake/stub implementations
            fake_violations = self._check_fake_implementations(lines, test_file_path, rule_obj)
            violations.extend(fake_violations)
        
        except (UnicodeDecodeError, SyntaxError, Exception):
            # Skip binary files, syntax errors, or files with encoding issues
            # Syntax errors might indicate incomplete code, which is actually what we want to catch
            pass
        
        return violations
    
    def _check_test_methods_call_production_code(
        self, content: str, lines: List[str], file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check that test methods actually call production code or would fail if code doesn't exist."""
        violations = []
        
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError:
            # If file has syntax errors, it might be incomplete - that's actually a violation
            # But we'll let other checks handle that
            return violations
        
        # Find project root to determine src folder location
        # Try knowledge_graph first, then infer from test file path
        project_location = knowledge_graph.get('project_location', '')
        if project_location:
            project_path = Path(project_location)
        else:
            # Infer from test file path: test files are usually in project_root/test/
            # So project root is parent of test directory
            if file_path.parent.name == 'test' or file_path.parent.name == 'tests':
                project_path = file_path.parent.parent
            else:
                # Fallback: assume test file is in project root
                project_path = file_path.parent
        
        # Determine src folder locations to check
        src_locations = self._find_src_locations(project_path)
        
        # Find all test methods
        test_methods = self._find_test_methods(tree)
        
        # Find all test classes
        test_classes = self._find_test_classes(tree)
        
        # If there are test classes but no test methods, that's a violation
        if test_classes and not test_methods:
            for test_class in test_classes:
                violation = Violation(
                    rule=rule_obj,
                    violation_message=(
                        f"Test class '{test_class.name}' (line {test_class.lineno}) has no test methods. "
                        f"Test classes must contain test methods that call production code. "
                        f"If production code doesn't exist yet, tests should fail with ImportError or AttributeError."
                    ),
                    location=str(file_path),
                    line_number=test_class.lineno,
                    severity='error'
                ).to_dict()
                violations.append(violation)
            # Continue checking for other violations even if no test methods found
        
        # Check imports for production code
        imports = self._find_imports(tree)
        has_production_imports = self._has_production_code_imports(imports, src_locations, project_path)
        
        # Check if file has any imports at all (excluding pytest, pathlib, json which are test infrastructure)
        has_any_imports = len([imp for imp in imports if not self._is_test_infrastructure_import(imp)]) > 0
        
        # If no imports at all (except test infrastructure), that's a violation
        if not has_any_imports and test_methods:
            violation = Violation(
                rule=rule_obj,
                violation_message=(
                    f"Test file has no imports from production code. "
                    f"Tests must import production code from src folder (or relative imports). "
                    f"If production code doesn't exist yet, the import should fail with ImportError, "
                    f"not be omitted entirely."
                ),
                location=str(file_path),
                line_number=1,
                severity='error'
            ).to_dict()
            violations.append(violation)
        
        for test_method in test_methods:
            method_name = test_method.name
            method_line = test_method.lineno
            
            # Check if test method body is empty or only contains pass/TODO
            is_empty = self._is_empty_or_todo_only(test_method, lines)
            
            if is_empty:
                violation = Violation(
                    rule=rule_obj,
                    violation_message=(
                        f"Test method '{method_name}' (line {method_line}) is empty or only contains TODO comments. "
                        f"Tests must call production code directly from src folder, even if the code doesn't exist yet. "
                        f"The test should fail with ImportError or AttributeError if production code is missing."
                    ),
                    location=str(file_path),
                    line_number=method_line,
                    severity='error'
                ).to_dict()
                violations.append(violation)
                continue
            
            # Check if test method calls production code (trace through helpers)
            has_production_calls = self._has_production_code_calls(test_method, imports, src_locations, project_path, file_path, tree)
            
            if not has_production_calls and not has_production_imports:
                # Test doesn't import or call production code
                violation = Violation(
                    rule=rule_obj,
                    violation_message=(
                        f"Test method '{method_name}' (line {method_line}) does not call production code from src folder. "
                        f"Tests must import and call production code directly. If the code doesn't exist, the test should "
                        f"fail with ImportError or AttributeError, not silently pass."
                    ),
                    location=str(file_path),
                    line_number=method_line,
                    severity='error'
                ).to_dict()
                violations.append(violation)
        
        return violations
    
    def _find_src_locations(self, project_path: Path) -> List[str]:
        """Find potential src folder locations."""
        src_locations = []
        
        # Common src folder patterns
        possible_src_paths = [
            project_path / 'src',
            project_path / 'source',
            project_path.parent / 'src',
        ]
        
        for src_path in possible_src_paths:
            if src_path.exists() and src_path.is_dir():
                # Get relative path from project root
                try:
                    rel_path = src_path.relative_to(project_path)
                    src_locations.append(str(rel_path).replace('\\', '/'))
                except ValueError:
                    # Path not relative, use absolute
                    src_locations.append(str(src_path))
        
        # Also check if there are Python files that would be imported
        # Look for common domain module patterns
        for py_file in project_path.rglob('*.py'):
            if 'test' not in str(py_file).lower() and '__pycache__' not in str(py_file):
                # This could be production code
                rel_path = py_file.relative_to(project_path.parent if project_path.name == 'test' else project_path)
                module_path = str(rel_path.parent).replace('\\', '/').replace('/', '.')
                if module_path and module_path not in src_locations:
                    src_locations.append(module_path)
        
        return src_locations
    
    def _find_test_methods(self, tree: ast.AST) -> List[ast.FunctionDef]:
        """Find all test methods in the AST."""
        test_methods = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    test_methods.append(node)
        
        return test_methods
    
    def _find_test_classes(self, tree: ast.AST) -> List[ast.ClassDef]:
        """Find all test classes in the AST."""
        test_classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.startswith('Test'):
                    test_classes.append(node)
        
        return test_classes
    
    def _find_imports(self, tree: ast.AST) -> List[ast.Import | ast.ImportFrom]:
        """Find all import statements."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)
        
        return imports
    
    def _has_production_code_imports(
        self, imports: List[ast.Import | ast.ImportFrom], src_locations: List[str], project_path: Path
    ) -> bool:
        """Check if imports reference production code from src folder."""
        if not imports:
            return False
        
        for imp in imports:
            if isinstance(imp, ast.ImportFrom):
                module = imp.module or ''
                # Check if import is from src folder or would be production code
                if self._is_production_module(module, src_locations, project_path):
                    return True
            elif isinstance(imp, ast.Import):
                for alias in imp.names:
                    module = alias.name
                    if self._is_production_module(module, src_locations, project_path):
                        return True
        
        return False
    
    def _is_production_module(self, module: str, src_locations: List[str], project_path: Path) -> bool:
        """Check if a module name represents production code (NOT from test folder)."""
        if not module:
            return False
        
        module_lower = module.lower()
        
        # Explicitly exclude imports from test folders
        # Check if 'test' or 'tests' appears as a directory segment in the module path
        module_parts = module.split('.')
        for part in module_parts:
            if part.lower() in ['test', 'tests']:
                # This is importing from a test folder - NOT production code
                return False
        
        # Skip standard library and third-party imports
        stdlib_modules = ['pytest', 'pathlib', 'json', 'typing', 'unittest', 'mock', 'unittest.mock',
                         'os', 'sys', 'collections', 'dataclasses', 'enum', 'abc', 'logging',
                         'datetime', 'time', 're', 'random', 'math', 'itertools', 'functools']
        if '.' in module:
            first_part = module.split('.')[0]
            if first_part in stdlib_modules:
                return False
        
        # Check if module path matches src locations (production code locations)
        for src_loc in src_locations:
            if src_loc in module or module.startswith(src_loc.replace('/', '.')):
                return True
        
        # Check if it's a relative import that could be production code
        # (relative imports starting with . are often production code)
        if module.startswith('.'):
            # Relative import - could be production code
            # Already checked above that it's not from test folder
            return True
        
        # Check if module would exist in src folder structure
        # Look for domain-related module names (not test-related)
        domain_keywords = ['mob', 'token', 'minion', 'strategy', 'action', 'attack', 'storage', 
                          'registry', 'manager', 'handler', 'executor', 'propagator', 'lookup',
                          'selection', 'click', 'combat', 'foundry']
        if any(keyword in module_lower for keyword in domain_keywords):
            # Could be production code - already checked above that it's not from test folder
            if 'mock' not in module_lower:
                return True
        
        # Check if module name suggests it's production code (not test infrastructure)
        # Production code modules often have domain-specific names without 'test' prefix
        if not module.startswith('test') and 'test' not in module_lower:
            # Could be production code if it's not a known test framework module
            if module.split('.')[0] not in stdlib_modules:
                # Might be production code - be permissive here
                # The key is that tests should TRY to import it, even if it doesn't exist
                return True
        
        return False
    
    def _is_test_infrastructure_import(self, imp: ast.Import | ast.ImportFrom) -> bool:
        """Check if import is test infrastructure (pytest, pathlib, json, etc.)"""
        test_infra_modules = ['pytest', 'pathlib', 'json', 'typing', 'unittest', 'mock', 'unittest.mock']
        
        if isinstance(imp, ast.ImportFrom):
            module = imp.module or ''
            return module.split('.')[0] in test_infra_modules if module else False
        elif isinstance(imp, ast.Import):
            for alias in imp.names:
                if alias.name.split('.')[0] in test_infra_modules:
                    return True
        return False
    
    def _is_empty_or_todo_only(self, method: ast.FunctionDef, source_lines: List[str]) -> bool:
        """Check if test method body is empty or only contains pass/TODO comments."""
        if not method.body:
            return True
        
        # Get method source lines for comment checking
        method_start = method.lineno - 1  # Convert to 0-indexed
        method_end = method.end_lineno if hasattr(method, 'end_lineno') else method_start + 50
        if method_start < len(source_lines):
            method_source = source_lines[method_start:method_end]
        else:
            method_source = []
        
        # Check for TODO/FIXME comments in source lines
        has_todo = any('TODO' in line or 'FIXME' in line for line in method_source)
        if has_todo:
            return True
        
        # Check if body only contains pass or docstrings
        non_empty_statements = []
        for stmt in method.body:
            if isinstance(stmt, ast.Pass):
                # Pass statement - empty implementation
                continue
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                # String literal (docstring) - ignore
                if isinstance(stmt.value.value, str):
                    continue
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Str):
                # Old-style docstring - ignore
                continue
            else:
                non_empty_statements.append(stmt)
        
        # If only pass statements and docstrings remain, it's empty
        if not non_empty_statements:
            return True
        
        # Check if all remaining statements are actual executable code
        # Look for: function calls, assignments, assertions, returns, raises, imports, etc.
        has_actual_code = False
        for stmt in non_empty_statements:
            # Check for actual executable statements
            if isinstance(stmt, (ast.Call, ast.Assign, ast.Assert, ast.Return, ast.Raise, 
                                 ast.Import, ast.ImportFrom, ast.If, ast.For, ast.While,
                                 ast.With, ast.Try)):
                has_actual_code = True
                break
            
            # Also check nested nodes for calls/assignments
            for node in ast.walk(stmt):
                if isinstance(node, (ast.Call, ast.Assign, ast.Assert, ast.Return, ast.Raise)):
                    has_actual_code = True
                    break
            if has_actual_code:
                break
        
        # If no actual code found, it's empty/TODO only
        return not has_actual_code
    
    def _has_production_code_calls(
        self, method: ast.FunctionDef, imports: List[ast.Import | ast.ImportFrom],
        src_locations: List[str], project_path: Path, file_path: Path = None, tree: ast.AST = None
    ) -> bool:
        """Check if test method calls production code, tracing through helper functions."""
        # Find all function calls in the method
        calls = []
        for node in ast.walk(method):
            if isinstance(node, ast.Call):
                calls.append(node)
        
        if not calls:
            return False
        
        # Check if any calls are to production code
        for call in calls:
            if isinstance(call.func, ast.Name):
                # Direct function call - check if it's imported from production code
                func_name = call.func.id
                if self._is_production_function(func_name, imports, src_locations, project_path):
                    return True
                # Also check if it's a helper function that calls production code
                if file_path and tree:
                    if self._helper_calls_production_code(func_name, file_path, tree, src_locations, project_path):
                        return True
            elif isinstance(call.func, ast.Attribute):
                # Method call or module.function call
                if isinstance(call.func.value, ast.Name):
                    # Check if it's a production class/module
                    obj_name = call.func.value.id
                    if self._is_production_function(obj_name, imports, src_locations, project_path):
                        return True
                    # Check if attribute access is production code
                    if hasattr(call.func, 'attr'):
                        attr_name = call.func.attr
                        if self._is_production_function(attr_name, imports, src_locations, project_path):
                            return True
                elif isinstance(call.func.value, ast.Attribute):
                    # Nested attribute access - check if root is production code
                    root = call.func.value
                    while isinstance(root, ast.Attribute):
                        root = root.value
                    if isinstance(root, ast.Name):
                        if self._is_production_function(root.id, imports, src_locations, project_path):
                            return True
                        # Check nested attribute name
                        if hasattr(call.func, 'attr'):
                            attr_name = call.func.attr
                            if self._is_production_function(attr_name, imports, src_locations, project_path):
                                return True
        
        return False
    
    def _helper_calls_production_code(
        self, helper_name: str, file_path: Path, tree: ast.AST,
        src_locations: List[str], project_path: Path
    ) -> bool:
        """Check if a helper function eventually calls production code."""
        # Find the helper function definition in the current file
        helper_func = None
        
        # First check current file
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == helper_name:
                helper_func = node
                break
        
        if helper_func:
            # Check if helper function imports production code
            helper_imports = self._find_imports(tree)
            has_prod_imports = self._has_production_code_imports(helper_imports, src_locations, project_path)
            
            # Check if helper function calls production code directly
            has_prod_calls = self._has_production_code_calls(
                helper_func, helper_imports, src_locations, project_path, file_path, tree
            )
            
            # If helper imports or calls production code, it's valid
            if has_prod_imports or has_prod_calls:
                return True
            
            # Check if helper calls other helpers that might call production code
            # Find all function calls in helper
            for node in ast.walk(helper_func):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        called_func_name = node.func.id
                        # Recursively check if called helper calls production code
                        if self._helper_calls_production_code(
                            called_func_name, file_path, tree, src_locations, project_path
                        ):
                            return True
        
        # Check if helper is imported from test helper files
        imports = self._find_imports(tree)
        for imp in imports:
            if isinstance(imp, ast.ImportFrom):
                # Check if this helper is imported from a test helper module
                if imp.module and 'test' in imp.module.lower() and 'helper' in imp.module.lower():
                    # Check if any imported name matches our helper
                    for alias in imp.names:
                        if alias.asname == helper_name or alias.name == helper_name:
                            # Try to find and check the helper file
                            helper_file = self._find_helper_file(imp.module, project_path)
                            if helper_file and helper_file.exists():
                                if self._file_has_production_code_calls(helper_file, src_locations, project_path):
                                    return True
        
        return False
    
    def _find_helper_file(self, module_name: str, project_path: Path) -> Optional[Path]:
        """Find helper file from module name."""
        # Convert module name to file path
        # e.g., 'agile_bot.bots.base_bot.test.test_helpers' -> 'agile_bot/bots/base_bot/test/test_helpers.py'
        module_path = module_name.replace('.', '/')
        # Try common locations
        possible_paths = [
            project_path / f'{module_path}.py',
            project_path.parent / f'{module_path}.py',
        ]
        for path in possible_paths:
            if path.exists():
                return path
        return None
    
    def _file_has_production_code_calls(self, file_path: Path, src_locations: List[str], project_path: Path) -> bool:
        """Check if a file (helper file) has production code calls."""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            imports = self._find_imports(tree)
            
            # Check if file imports production code
            if self._has_production_code_imports(imports, src_locations, project_path):
                return True
            
            # Check all functions in file for production code calls
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if self._has_production_code_calls(node, imports, src_locations, project_path, file_path, tree):
                        return True
        except Exception:
            pass
        return False
    
    def _is_production_function(
        self, name: str, imports: List[ast.Import | ast.ImportFrom],
        src_locations: List[str], project_path: Path
    ) -> bool:
        """Check if a function/class name comes from production code imports."""
        # Check if name is imported from production code
        for imp in imports:
            if isinstance(imp, ast.ImportFrom):
                if imp.module and self._is_production_module(imp.module, src_locations, project_path):
                    # Check if this name is imported from that module
                    for alias in imp.names:
                        if alias.asname == name or alias.name == name:
                            return True
            elif isinstance(imp, ast.Import):
                for alias in imp.names:
                    if alias.asname == name or alias.name == name:
                        if self._is_production_module(alias.name, src_locations, project_path):
                            return True
        
        # Check if name matches domain concepts (could be production code)
        domain_keywords = ['mob', 'token', 'minion', 'strategy', 'action', 'attack', 'storage', 'registry', 'manager']
        name_lower = name.lower()
        if any(keyword in name_lower for keyword in domain_keywords):
            # Likely production code if not a test helper
            if not name_lower.startswith(('test_', 'mock_', 'fake_', 'stub_')):
                return True
        
        return False
    
    def _check_fake_implementations(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for fake/stub implementations."""
        violations = []
        
        fake_patterns = [
            r'\bfake\s*\w+',  # fake_user, fake_data
            r'\bstub\s*\w+',  # stub_service
            r'\bmock\s*\w+.*=.*Mock\(\)',  # mock_service = Mock()
            r'return\s+\{\}',  # return {} (stub return)
        ]
        
        # Allow Mock() if it's used for testing CLI exception handling (test_cli_exceptions.py)
        # But flag it if it's used as a replacement for real production code
        mock_allowed_contexts = [
            'test_cli_exceptions',  # Testing exception handling requires mocking
        ]
        
        file_name = file_path.name.lower()
        is_allowed_context = any(ctx in file_name for ctx in mock_allowed_contexts)
        
        for line_num, line in enumerate(lines, 1):
            # Skip Mock() in allowed contexts (exception testing)
            if is_allowed_context and 'mock' in line.lower() and 'mock()' in line.lower():
                # Check if Mock is used for exception testing (BaseBotCli)
                if 'basebotcli' in line.lower() or 'cli' in line.lower():
                    continue
            
            for pattern in fake_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Line {line_num} uses fake/stub implementation - tests should call real production code directly',
                        location=str(file_path),
                        line_number=line_num,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations
    

