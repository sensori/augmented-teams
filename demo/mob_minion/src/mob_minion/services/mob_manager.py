"""
Mob Manager Service

Creates and manages Mob domain objects.
"""
from typing import List, Dict, Optional

from ..domain.mob import Mob
from ..domain.minion import Minion


class MobManager:
    """
    Service for creating and managing Mob domain objects.
    
    Creates Mob objects from selected tokens and actor data, handling
    validation and duplicate removal.
    """
    
    def __init__(self):
        """Initialize mob manager."""
        pass
    
    def create_mob_from_tokens(
        self,
        tokens: List[str],
        actor_data: List[Dict]
    ) -> Mob:
        """
        Create Mob domain object from tokens and actor data.
        
        Args:
            tokens: List of token IDs
            actor_data: List of actor data dictionaries with actor_id, name, position
            
        Returns:
            Mob domain object with Minion objects
            
        Raises:
            ValueError: If mob group contains less than one minion
        """
        if len(tokens) < 1:
            raise ValueError("Mob must contain at least one minion")
        
        unique_tokens = list(set(tokens))
        notification = None
        if len(unique_tokens) < len(tokens):
            notification = "Duplicate tokens removed"
        
        # Create a mapping from token index to actor data
        # Since actor_data is created based on tokens, we match by index
        minions = []
        seen_actor_ids = set()
        for i, token in enumerate(unique_tokens):
            if i < len(actor_data):
                actor = actor_data[i]
                # Skip duplicates based on actor_id
                if actor["actor_id"] not in seen_actor_ids:
                    minions.append(Minion(actor_id=actor["actor_id"], name=actor["name"]))
                    seen_actor_ids.add(actor["actor_id"])
        
        mob = Mob(name="", minions=minions)
        
        if notification:
            pass
        
        return mob
    
    def create_temporary_mob_group(
        self,
        tokens: List[str],
        actor_data: List[Dict]
    ) -> Dict:
        """
        Create temporary mob group structure.
        
        Args:
            tokens: List of token IDs
            actor_data: List of actor data dictionaries
            
        Returns:
            Dictionary with tokens, actor_data, and minion_names
        """
        return {
            "tokens": tokens,
            "actor_data": actor_data,
            "minion_names": [actor["name"] for actor in actor_data]
        }

