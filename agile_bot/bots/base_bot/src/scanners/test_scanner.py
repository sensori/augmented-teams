"""Base TestScanner class for validating test files."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
from .scanner import Scanner
from .violation import Violation

if TYPE_CHECKING:
    from pathlib import Path as PathType


class TestScanner(Scanner):
    """Base class for test validation scanners.
    
    TestScanners scan test code files to verify test quality and test-story mapping.
    
    Test scanners validate:
    1. Test code files (test classes match stories, methods match scenarios)
    2. Test code quality (via code scanning)
    
    Note: TestScanner does NOT scan story nodes - it only scans test files.
    """
    
    def scan(
        self, 
        knowledge_graph: Dict[str, Any], 
        rule_obj: Any = None,
        test_files: Optional[List['Path']] = None,
        code_files: Optional[List['Path']] = None
    ) -> List[Dict[str, Any]]:
        """Scan test files for violations.
        
        Args:
            knowledge_graph: Story graph structure
            rule_obj: Rule object reference
            test_files: List of test file paths to scan (from parameters, not knowledge_graph)
            code_files: Not used by TestScanner (for CodeScanner)
            
        Returns:
            List of violation dictionaries from test code scanning
        """
        violations = []
        
        # Scan test files if provided via parameters
        if test_files:
            for test_file_path in test_files:
                if test_file_path.exists():
                    code_violations = self.scan_test_file(test_file_path, rule_obj, knowledge_graph)
                    violations.extend(code_violations)
        
        return violations
    
    def scan_test_file(self, test_file_path: Path, rule_obj: Any, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan a test file for violations.
        
        Args:
            test_file_path: Path to test file
            rule_obj: Rule object reference
            knowledge_graph: Story graph for mapping verification
            
        Returns:
            List of violation dictionaries
        """
        # Default implementation - subclasses override
        return []

