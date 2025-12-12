"""Base CodeScanner class for validating source code files."""

from abc import abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path  # Needed at runtime for Path operations
from .scanner import Scanner
from .violation import Violation


class CodeScanner(Scanner):
    """Base class for code validation scanners.
    
    CodeScanners validate Python/JavaScript source code files against rules.
    Each scanner implements scan_code_file() to check a single file.
    """
    
    def scan(
        self, 
        knowledge_graph: Dict[str, Any], 
        rule_obj: Any = None,
        test_files: Optional[List['Path']] = None,
        code_files: Optional[List['Path']] = None
    ) -> List[Dict[str, Any]]:
        """Scan code files for rule violations.
        
        Args:
            knowledge_graph: Story graph structure
            rule_obj: Rule object reference (for creating Violations)
            test_files: Not used by CodeScanner (for TestScanner)
            code_files: List of code file paths to scan (from parameters, not knowledge_graph)
            
        Returns:
            List of violation dictionaries
        """
        if not rule_obj:
            raise ValueError("rule_obj parameter is required for CodeScanner")
        
        violations = []
        
        # Scan code files if provided via parameters
        if code_files:
            for code_file_path in code_files:
                if code_file_path.exists():
                    file_violations = self.scan_code_file(code_file_path, rule_obj)
                    violations.extend(file_violations if isinstance(file_violations, list) else [])
        
        return violations
    
    @abstractmethod
    def scan_code_file(self, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        """Scan a single code file for violations.
        
        Args:
            file_path: Path to code file to scan
            rule_obj: Rule object reference
            
        Returns:
            List of violation dictionaries
        """
        pass

