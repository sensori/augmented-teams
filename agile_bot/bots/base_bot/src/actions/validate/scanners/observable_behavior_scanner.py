"""Scanner for validating tests focus on observable behavior."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .test_scanner import TestScanner
from .violation import Violation


class ObservableBehaviorScanner(TestScanner):
    """Detects testing of internal calls/framework logic instead of observable behavior."""
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_file_path.exists():
            return violations
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            
            # Check for internal testing patterns
            violations.extend(self._check_internal_testing(content, test_file_path, rule_obj))
        
        except (UnicodeDecodeError, Exception):
            # Skip binary files or files with encoding issues
            pass
        
        return violations
    
    def _check_internal_testing(self, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Check for testing of internal calls/framework logic."""
        violations = []
        lines = content.split('\n')
        
        # Patterns that indicate testing internal implementation
        internal_patterns = [
            r'\.toHaveBeenCalled',  # Jest mock assertions
            r'\.assert_called',  # Python mock assertions
            r'\.mock\.',  # Mock internals
            r'\.spyOn\(',  # Spy creation
            r'assert.*\.call_count',  # Checking call counts
            r'assert.*\.call_args',  # Checking call arguments
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in internal_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Line {line_num} tests internal implementation (mocks/spies) - tests should focus on observable behavior, not internal calls',
                        location=str(file_path),
                        line_number=line_num,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations

