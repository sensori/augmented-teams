"""Violation DTO class for rule violations."""

from typing import Optional, Dict, Any


class Violation:
    """Simple DTO class representing a rule violation.
    
    Properties provide access to violation data following 'tell don't ask' principle.
    """
    
    def __init__(
        self,
        rule_name: str,
        violation_message: str,
        line_number: Optional[int] = None,
        location: Optional[str] = None,
        severity: str = 'error',
        rule_file: Optional[str] = None
    ):
        """Initialize violation with required and optional fields.
        
        Args:
            rule_name: Name of the rule being violated
            violation_message: Description of the violation
            line_number: Line number where violation occurs (if applicable)
            location: Location in knowledge graph (e.g., 'epics[0].name')
            severity: Severity level ('error', 'warning', 'info')
            rule_file: Path to the rule file (if applicable)
        """
        self._rule_name = rule_name
        self._violation_message = violation_message
        self._line_number = line_number
        self._location = location
        self._severity = severity
        self._rule_file = rule_file
    
    @property
    def rule_name(self) -> str:
        """Get rule name."""
        return self._rule_name
    
    @property
    def violation_message(self) -> str:
        """Get violation message."""
        return self._violation_message
    
    @property
    def line_number(self) -> Optional[int]:
        """Get line number where violation occurs."""
        return self._line_number
    
    @property
    def location(self) -> Optional[str]:
        """Get location in knowledge graph."""
        return self._location
    
    @property
    def severity(self) -> str:
        """Get severity level."""
        return self._severity
    
    @property
    def rule_file(self) -> Optional[str]:
        """Get rule file path."""
        return self._rule_file
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary format.
        
        Returns:
            Dictionary representation of violation
        """
        result = {
            'rule_name': self._rule_name,
            'violation_message': self._violation_message,
            'severity': self._severity
        }
        
        if self._line_number is not None:
            result['line_number'] = self._line_number
        
        if self._location is not None:
            result['location'] = self._location
        
        if self._rule_file is not None:
            result['rule_file'] = self._rule_file
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Violation':
        """Create violation from dictionary.
        
        Args:
            data: Dictionary containing violation data
            
        Returns:
            Violation instance
        """
        return cls(
            rule_name=data.get('rule_name', 'unknown'),
            violation_message=data.get('violation_message', ''),
            line_number=data.get('line_number'),
            location=data.get('location'),
            severity=data.get('severity', 'error'),
            rule_file=data.get('rule_file')
        )

