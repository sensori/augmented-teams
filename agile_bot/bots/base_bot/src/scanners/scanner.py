"""Base Scanner class for validation rule scanners."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class Scanner(ABC):
    """Base class for validation rule scanners.
    
    Scanners validate knowledge graphs against rules and return violations.
    Each scanner is associated with a specific rule and implements the scan method.
    """
    
    @abstractmethod
    def scan(
        self, 
        knowledge_graph: Dict[str, Any], 
        rule_obj: Any = None,
        test_files: Optional[List['Path']] = None,
        code_files: Optional[List['Path']] = None
    ) -> List[Dict[str, Any]]:
        """Scan knowledge graph for rule violations.
        
        Args:
            knowledge_graph: The knowledge graph to validate (typically story-graph.json structure)
            rule_obj: Optional Rule object reference (for creating Violations with rule reference)
            test_files: Optional list of test file paths (for TestScanner instances)
            code_files: Optional list of code file paths (for CodeScanner instances)
            
        Returns:
            List of violation dictionaries or Violation objects, each containing:
            - rule: Rule object reference or rule name string
            - line_number: Line number where violation occurs (if applicable)
            - location: Location in knowledge graph (e.g., 'epics[0].name')
            - violation_message: Description of the violation
            - severity: Severity level ('error', 'warning', 'info')
            
        Raises:
            Exception: If scanner execution fails (exceptions should not be swallowed)
        """
        pass

