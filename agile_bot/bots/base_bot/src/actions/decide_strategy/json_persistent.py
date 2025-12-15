"""
Base class for JSON persistence.

Handles loading, merging, and saving JSON files in a consistent way.
"""
from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths

logger = logging.getLogger(__name__)


class JsonPersistent:
    """Base class for objects that persist data as JSON files.
    
    Handles:
    - Finding the file path
    - Loading existing data
    - Merging new data
    - Saving to file
    """
    
    def __init__(self, bot_paths: BotPaths, filename: str):
        """Initialize JsonPersistent.
        
        Args:
            bot_paths: BotPaths instance for accessing paths
            filename: Name of the JSON file (e.g., 'clarification.json', 'planning.json')
        """
        self.bot_paths = bot_paths
        self.filename = filename
    
    @property
    def file_path(self) -> Path:
        """Get the full path to the JSON file.
        
        Returns:
            Path to the JSON file in the documentation directory.
        """
        workspace_directory = self.bot_paths.workspace_directory
        documentation_path = self.bot_paths.documentation_path
        docs_dir = workspace_directory / documentation_path
        return docs_dir / self.filename
    
    def load(self) -> Dict[str, Any]:
        """Load existing data from JSON file.
        
        Returns:
            Dictionary with existing data, or empty dict if file doesn't exist.
        """
        file_path = self.file_path
        if file_path.exists():
            try:
                return json.loads(file_path.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Failed to load {file_path}: {e}. Starting fresh.")
                return {}
        return {}
    
    def merge(self, existing_data: Dict[str, Any], new_data: Dict[str, Any], 
              key: str) -> Dict[str, Any]:
        """Merge new data into existing data under a key.
        
        Args:
            existing_data: Existing data dictionary
            new_data: New data to merge
            key: Key under which to store the new data
            
        Returns:
            Merged data dictionary
        """
        merged = existing_data.copy()
        merged[key] = new_data
        return merged
    
    def save(self, data: Dict[str, Any]):
        """Save data to JSON file.
        
        Args:
            data: Data dictionary to save
        """
        try:
            file_path = self.file_path
            
            # Ensure documentation folder exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            file_path.write_text(
                json.dumps(data, indent=2),
                encoding='utf-8'
            )
        except Exception as e:
            logger.exception(f"Failed to save {self.filename}")
            raise RuntimeError(f"Failed to save {self.filename}: {e}") from e

