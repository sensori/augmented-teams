"""Base TestScanner class for validating test files."""

from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
from pathlib import Path
import ast
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
    
    def scan_cross_file(
        self,
        rule_obj: Any = None,
        test_files: Optional[List[Path]] = None,
        code_files: Optional[List[Path]] = None
    ) -> List[Dict[str, Any]]:
        """Scan across all test files for cross-file violations.
        
        Override this method in subclasses to detect violations that require
        analyzing multiple files together (e.g., duplication, helper function
        placement, inconsistent naming patterns).
        
        Args:
            rule_obj: Rule object reference
            test_files: List of all test file paths to analyze together
            code_files: Not used by TestScanner (for CodeScanner)
            
        Returns:
            List of violation dictionaries for cross-file issues
        """
        # Default implementation - subclasses override
        return []
    
    def _parse_test_file(self, test_file_path: Path) -> Optional[Tuple[str, ast.AST]]:
        """Parse a test file and return its content and AST tree.
        
        Reusable helper method for cross-file scanning.
        
        Args:
            test_file_path: Path to test file
            
        Returns:
            Tuple of (content, tree) or None if file cannot be parsed
        """
        if not test_file_path.exists():
            return None
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(test_file_path))
            return (content, tree)
        except (SyntaxError, UnicodeDecodeError):
            return None
    
    def _get_all_test_files_parsed(
        self, 
        test_files: Optional[List[Path]]
    ) -> List[Tuple[Path, str, ast.AST]]:
        """Parse all test files and return list of (path, content, tree) tuples.
        
        Reusable helper method for cross-file scanning.
        
        Args:
            test_files: List of test file paths
            
        Returns:
            List of tuples (file_path, content, tree) for successfully parsed files
        """
        parsed_files = []
        if test_files:
            for test_file_path in test_files:
                parsed = self._parse_test_file(test_file_path)
                if parsed:
                    content, tree = parsed
                    parsed_files.append((test_file_path, content, tree))
        return parsed_files

