"""Violation DTO class for rule violations."""

from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from agile_bot.bots.base_bot.src.actions.validate.rule import Rule


class Violation:
    """Simple DTO class representing a rule violation.
    
    A violation only needs access to the rule that created it.
    All rule-related information is accessed through the rule property.
    """
    
    def __init__(
        self,
        rule: 'Rule',
        violation_message: str,
        line_number: Optional[int] = None,
        location: Optional[str] = None,
        severity: str = 'error'
    ):
        """Initialize violation with required and optional fields.
        
        Args:
            rule: Rule object that created this violation
            violation_message: Description of the violation
            line_number: Line number where violation occurs (if applicable)
            location: Location in knowledge graph (e.g., 'epics[0].name')
            severity: Severity level ('error', 'warning', 'info')
        """
        if not hasattr(rule, 'name') or not hasattr(rule, 'rule_file'):
            raise TypeError(f"rule must be a Rule object, got {type(rule)}")
        
        self._rule = rule
        self._violation_message = violation_message
        self._line_number = line_number
        self._location = location
        self._severity = severity
    
    @property
    def rule(self) -> 'Rule':
        """Get rule object that created this violation."""
        return self._rule
    
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary format.
        
        Returns:
            Dictionary representation of violation with rule name and rule_file
            accessed from the Rule object.
        """
        result = {
            'rule': self._rule.name,
            'rule_file': self._rule.rule_file,
            'violation_message': self._violation_message,
            'severity': self._severity,
            'line_number': self._line_number  # Always include, even if None
        }
        
        if self._location is not None:
            result['location'] = self._location
        
        return result

