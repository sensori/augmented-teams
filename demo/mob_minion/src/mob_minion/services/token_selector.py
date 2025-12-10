"""
Token Selector Service

Handles token selection, highlighting, and validation.
"""
from typing import List, Optional


class TokenSelector:
    """
    Service for selecting and managing minion tokens.
    
    Handles token selection, highlighting, and validation according to
    business rules.
    """
    
    def __init__(self):
        """Initialize token selector."""
        self._selected_tokens: List[str] = []
        self._highlighted: bool = False
    
    def select_tokens(self, tokens: List[str]) -> None:
        """
        Select tokens and highlight them.
        
        Args:
            tokens: List of token IDs to select
            
        Raises:
            ValueError: If no tokens are provided
        """
        if len(tokens) == 0:
            raise ValueError("At least one token must be selected")
        
        self._selected_tokens = tokens
        self._highlighted = True
    
    def clear_selection(self) -> None:
        """Clear current selection and return to initial state."""
        self._selected_tokens = []
        self._highlighted = False
    
    @property
    def selected_tokens(self) -> List[str]:
        """Get list of currently selected tokens."""
        return self._selected_tokens.copy()
    
    @property
    def is_highlighted(self) -> bool:
        """Check if tokens are currently highlighted."""
        return self._highlighted
    
    @property
    def has_selection(self) -> bool:
        """Check if any tokens are selected."""
        return len(self._selected_tokens) > 0

