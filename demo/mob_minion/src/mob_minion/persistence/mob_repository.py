"""
Mob Repository

Persists and loads mob configurations.
"""
import json
from pathlib import Path
from typing import Optional, Dict, List

from ..domain.mob import Mob


class MobRepositoryError(Exception):
    """Base exception for mob repository errors."""
    pass


class MobRepository:
    """
    Repository for persisting and loading mob configurations.
    
    Saves mob configurations to persistent storage and loads them back,
    including mob name, minion actor IDs, and creation timestamp.
    """
    
    def __init__(self, storage_path: Path):
        """
        Initialize mob repository.
        
        Args:
            storage_path: Path to persistent storage directory
        """
        self._storage_path = Path(storage_path)
        self._storage_path.mkdir(parents=True, exist_ok=True)
    
    def save(self, mob: Mob) -> str:
        """
        Save mob configuration to persistent storage.
        
        Args:
            mob: Mob domain object to save
            
        Returns:
            Success message
            
        Raises:
            MobRepositoryError: If persistence operation fails
        """
        try:
            config_file = self._storage_path / f"{mob.name}.json"
            config_data = {
                "name": mob.name,
                "minion_actor_ids": mob.get_minion_actor_ids(),
                "created_at": mob.created_at
            }
            config_file.write_text(json.dumps(config_data, indent=2))
            return "Mob configuration saved successfully"
        except Exception as e:
            raise MobRepositoryError(
                f"Failed to save mob configuration: {e}"
            )
    
    def load(self, mob_name: str) -> Optional[Dict]:
        """
        Load mob configuration from persistent storage.
        
        Args:
            mob_name: Name of mob to load
            
        Returns:
            Configuration dictionary or None if not found
        """
        config_file = self._storage_path / f"{mob_name}.json"
        if not config_file.exists():
            return None
        
        try:
            config_data = json.loads(config_file.read_text())
            return config_data
        except Exception:
            return None
    
    def is_available(self) -> bool:
        """Check if persistent storage is available."""
        try:
            return self._storage_path.exists() and self._storage_path.is_dir()
        except Exception:
            return False

