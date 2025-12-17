from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths

logger = logging.getLogger(__name__)


class JsonPersistent:
    def __init__(self, bot_paths: BotPaths, filename: str):
        self.bot_paths = bot_paths
        self.filename = filename
    
    @property
    def file_path(self) -> Path:
        workspace_directory = self.bot_paths.workspace_directory
        documentation_path = self.bot_paths.documentation_path
        docs_dir = workspace_directory / documentation_path
        return docs_dir / self.filename
    
    def load(self) -> Dict[str, Any]:
        file_path = self.file_path
        if not file_path.exists():
            return {}
        return json.loads(file_path.read_text(encoding='utf-8'))
    
    def merge(self, existing_data: Dict[str, Any], new_data: Dict[str, Any], 
              key: str) -> Dict[str, Any]:
        merged = existing_data.copy()
        merged[key] = new_data
        return merged
    
    def save(self, data: Dict[str, Any]):
        try:
            file_path = self.file_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(
                json.dumps(data, indent=2),
                encoding='utf-8'
            )
        except Exception as e:
            logger.exception(f"Failed to save {self.filename}")
            raise RuntimeError(f"Failed to save {self.filename}: {e}") from e

