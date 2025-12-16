"""
StoryGraph class.

Loads the story graph from story-graph.json file.
Follows the same pattern as other classes - instantiated with bot_paths and loads itself.
"""
from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
from agile_bot.bots.base_bot.src.utils import read_json_file

logger = logging.getLogger(__name__)


class StoryGraph:
    """Story graph loaded from story-graph.json.
    
    Follows the pattern: instantiated with bot_paths, loads itself from file.
    """
    
    def __init__(self, bot_paths: BotPaths, workspace_directory: Path, require_file: bool = True):
        """Initialize StoryGraph.
        
        Args:
            bot_paths: BotPaths instance for accessing documentation path
            workspace_directory: Workspace directory path
            require_file: If True, raise FileNotFoundError if file doesn't exist. If False, allow missing file.
        """
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
                    f"Expected story graph to be created by build_knowledge action before validate_rules."
                )
            self._content = {}
            return
        
        self._content = read_json_file(story_graph_path)
    
    @property
    def content(self) -> Dict[str, Any]:
        """Get story graph content."""
        return self._content
    
    @property
    def path(self) -> Path:
        """Get path to story graph file."""
        return self._path
    
    @property
    def has_epics(self) -> bool:
        """Check if story graph has epics."""
        return 'epics' in self._content
    
    @property
    def has_increments(self) -> bool:
        """Check if story graph has increments."""
        return 'increments' in self._content
    
    @property
    def has_domain_concepts(self) -> bool:
        """Check if story graph has domain concepts in any epic."""
        return any(
            'domain_concepts' in epic for epic in self._content.get('epics', [])
        )
    
    @property
    def epic_count(self) -> int:
        """Get number of epics in story graph."""
        return len(self._content.get('epics', []))
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access to story graph content."""
        return self._content[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dict-like assignment to story graph content."""
        self._content[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from story graph content with default."""
        return self._content.get(key, default)

