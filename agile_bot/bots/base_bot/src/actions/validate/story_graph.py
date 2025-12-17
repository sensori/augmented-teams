from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
from agile_bot.bots.base_bot.src.utils import read_json_file

logger = logging.getLogger(__name__)


class StoryGraph:
    def __init__(self, bot_paths: BotPaths, workspace_directory: Path, require_file: bool = True):
        self._bot_paths = bot_paths
        self._workspace_directory = workspace_directory
        docs_path = self._bot_paths.documentation_path
        docs_dir = self._workspace_directory / docs_path
        story_graph_path = docs_dir / 'story-graph.json'
        self._path = story_graph_path
        
        if not story_graph_path.exists():
            if require_file:
                logger.error(f"Story graph file not found at {story_graph_path}")
                raise FileNotFoundError(
                    f"Story graph file (story-graph.json) not found in {docs_dir}. "
                    f"Cannot validate rules without story graph. "
                    f"Expected story graph to be created by build action before validate."
                )
            self._content = {}
            return
        
        self._content = read_json_file(story_graph_path)
    
    @property
    def content(self) -> Dict[str, Any]:
        return self._content
    
    @property
    def path(self) -> Path:
        return self._path
    
    @property
    def has_epics(self) -> bool:
        return 'epics' in self._content
    
    @property
    def has_increments(self) -> bool:
        return 'increments' in self._content
    
    @property
    def has_domain_concepts(self) -> bool:
        return any(
            'domain_concepts' in epic for epic in self._content.get('epics', [])
        )
    
    @property
    def epic_count(self) -> int:
        return len(self._content.get('epics', []))
    
    def __getitem__(self, key: str) -> Any:
        return self._content[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        self._content[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._content.get(key, default)
