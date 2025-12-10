"""
Minion Domain Entity

Represents an individual token/actor in Foundry VTT that can be grouped into a mob.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Minion:
    """
    Minion domain entity.
    
    Represents an individual token/actor in Foundry VTT that belongs to a mob
    for coordinated control.
    """
    actor_id: str
    name: str
    
    def __post_init__(self):
        """Validate minion data."""
        if not self.actor_id:
            raise ValueError("Minion actor_id cannot be empty")
        if not self.name:
            raise ValueError("Minion name cannot be empty")

