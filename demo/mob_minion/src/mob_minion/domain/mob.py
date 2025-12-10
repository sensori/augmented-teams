"""
Mob Domain Entity

A collection of minions that act together as a coordinated unit.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .minion import Minion


@dataclass
class Mob:
    """
    Mob domain entity.
    
    Groups minions together for coordinated action, allowing a Game Master
    to control all minions in the mob by selecting any single minion token.
    """
    name: str
    minions: List[Minion] = field(default_factory=list)
    created_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize mob with creation timestamp if not provided."""
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat() + "Z"
    
    def add_minion(self, minion: Minion) -> None:
        """Add a minion to the mob."""
        if minion in self.minions:
            return
        self.minions.append(minion)
    
    def remove_minion(self, minion: Minion) -> None:
        """Remove a minion from the mob."""
        if minion in self.minions:
            self.minions.remove(minion)
    
    def has_minions(self) -> bool:
        """Check if mob has any minions."""
        return len(self.minions) > 0
    
    def get_minion_actor_ids(self) -> List[str]:
        """Get list of actor IDs for all minions in the mob."""
        return [minion.actor_id for minion in self.minions]
    
    def get_minion_names(self) -> List[str]:
        """Get list of names for all minions in the mob."""
        return [minion.name for minion in self.minions]

