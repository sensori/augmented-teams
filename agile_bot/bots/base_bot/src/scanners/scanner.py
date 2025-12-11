"""Base Scanner class for validation rule scanners."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class Scanner(ABC):
    """Base class for validation rule scanners.
    
    Scanners validate knowledge graphs against rules and return violations.
    Each scanner is associated with a specific rule and implements the scan method.
    """
    
    @abstractmethod
    def scan(self, knowledge_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan knowledge graph for rule violations.
        
        Args:
            knowledge_graph: The knowledge graph to validate (typically story-graph.json structure)
            
        Returns:
            List of violation dictionaries, each containing:
            - rule_name: Name of the rule being violated
            - line_number: Line number where violation occurs (if applicable)
            - location: Location in knowledge graph (e.g., 'epics[0].name')
            - violation_message: Description of the violation
            - severity: Severity level ('error', 'warning', 'info')
            
        Raises:
            Exception: If scanner execution fails (exceptions should not be swallowed)
        """
        pass

