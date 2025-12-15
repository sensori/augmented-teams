"""Scanner for validating one concept per test."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .test_scanner import TestScanner
from .violation import Violation


class OneConceptPerTestScanner(TestScanner):
    """Validates tests focus on one concept per test."""
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(test_file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        violation = self._check_one_concept(node, test_file_path, content, rule_obj)
                        if violation:
                            violations.append(violation)
        
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors
            pass
        
        return violations
    
    def _check_one_concept(self, test_node: ast.FunctionDef, file_path: Path, content: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        """Check if test focuses on one concept."""
        test_name = test_node.name.lower()
        
        # Multiple concept indicators
        multi_concept_patterns = [
            r'\b(and|or|then|also|plus)\b',  # "test_validates_and_saves"
            r'_(and|or|then|also|plus)_',  # Multiple actions
        ]
        
        for pattern in multi_concept_patterns:
            if re.search(pattern, test_name):
                # Count how many concepts (words separated by _)
                words = test_name.split('_')
                if len(words) > 8:  # Very long test name suggests multiple concepts
                    line_number = test_node.lineno if hasattr(test_node, 'lineno') else None
                    return Violation(
                        rule=rule_obj,
                        violation_message=f'Test "{test_node.name}" appears to test multiple concepts - split into separate tests, one concept per test',
                        location=str(file_path),
                        line_number=line_number,
                        severity='warning'
                    ).to_dict()
        
        return None

