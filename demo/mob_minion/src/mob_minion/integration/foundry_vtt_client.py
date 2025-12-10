"""
Foundry VTT Client

Integration client for Foundry VTT API.
"""
from typing import List, Dict, Optional


class FoundryVTTConnectionError(Exception):
    """Raised when Foundry VTT API is unavailable."""
    pass


class FoundryVTTInvalidDataError(Exception):
    """Raised when Foundry VTT API returns invalid token data."""
    pass


class FoundryVTTClient:
    """
    Client for interacting with Foundry VTT API.
    
    Handles queries for token actor data, including actor ID, name, and position.
    """
    
    def __init__(self, foundry_vtt_api: Optional[object] = None):
        """
        Initialize Foundry VTT client.
        
        Args:
            foundry_vtt_api: Foundry VTT API instance (injected dependency)
        """
        self._foundry_vtt_api = foundry_vtt_api
        self._is_available = foundry_vtt_api is not None
    
    def is_available(self) -> bool:
        """Check if Foundry VTT API is available."""
        if self._foundry_vtt_api is None:
            return False
        return getattr(self._foundry_vtt_api, 'is_available', False)
    
    def get_token_data(self, token_ids: List[str]) -> List[Dict]:
        """
        Query Foundry VTT API for token actor data.
        
        Args:
            token_ids: List of token IDs to query
            
        Returns:
            List of actor data dictionaries with actor_id, name, and position
            
        Raises:
            FoundryVTTConnectionError: If API is unavailable
            FoundryVTTInvalidDataError: If API returns invalid data
        """
        if not self.is_available():
            raise FoundryVTTConnectionError(
                "Connection failure: Foundry VTT API is unavailable"
            )
        
        if self._foundry_vtt_api is None:
            raise FoundryVTTConnectionError(
                "Connection failure: Foundry VTT API is unavailable"
            )
        
        actor_data = self._foundry_vtt_api.get_token_data(token_ids)
        
        if not self._validate_token_data(actor_data):
            raise FoundryVTTInvalidDataError("Invalid token data received")
        
        return actor_data
    
    def _validate_token_data(self, actor_data: List[Dict]) -> bool:
        """
        Validate that token data contains required fields.
        
        Args:
            actor_data: List of actor data dictionaries
            
        Returns:
            True if all entries have required fields, False otherwise
        """
        if not isinstance(actor_data, list):
            return False
        
        required_fields = ["actor_id", "name", "position"]
        return all(
            isinstance(item, dict) and
            all(field in item for field in required_fields)
            for item in actor_data
        )

