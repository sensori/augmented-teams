"""
Mob Name Validator Service

Validates mob names according to business rules.
"""
from typing import List, Set, Optional


class MobNameValidationError(Exception):
    """Base exception for mob name validation errors."""
    pass


class EmptyMobNameError(MobNameValidationError):
    """Raised when mob name is empty."""
    pass


class DuplicateMobNameError(MobNameValidationError):
    """Raised when mob name already exists."""
    pass


class MobNameValidator:
    """
    Service for validating mob names.
    
    Validates that mob names are not empty and are unique against
    existing mob names.
    """
    
    def __init__(self, existing_mob_names: Optional[List[str]] = None):
        """
        Initialize mob name validator.
        
        Args:
            existing_mob_names: List of existing mob names to check against
        """
        self._existing_names: Set[str] = set(
            existing_mob_names if existing_mob_names else []
        )
    
    def validate_and_assign_name(self, mob, name: str) -> None:
        """
        Validate mob name and assign it to mob.
        
        Args:
            mob: Mob domain object to assign name to
            name: Name to validate and assign
            
        Raises:
            EmptyMobNameError: If name is empty
            DuplicateMobNameError: If name already exists
        """
        if len(name) == 0:
            raise EmptyMobNameError("Mob name must not be empty")
        
        if name in self._existing_names:
            raise DuplicateMobNameError("Mob name must be unique")
        
        mob.name = name
    
    def validate_name(self, name: str) -> bool:
        """
        Validate mob name without assigning.
        
        Args:
            name: Name to validate
            
        Returns:
            True if name is valid and unique
            
        Raises:
            EmptyMobNameError: If name is empty
            DuplicateMobNameError: If name already exists
        """
        if len(name) == 0:
            raise EmptyMobNameError("Mob name must not be empty")
        
        if name in self._existing_names:
            raise DuplicateMobNameError("Mob name must be unique")
        
        return True
    
    def add_existing_name(self, name: str) -> None:
        """Add a name to the existing names set."""
        self._existing_names.add(name)
    
    def remove_existing_name(self, name: str) -> None:
        """Remove a name from the existing names set."""
        self._existing_names.discard(name)

