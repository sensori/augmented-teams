"""
KnowledgeGraph class.

Loads the built knowledge graph from story-graph.json file.
"""
from pathlib import Path
from typing import Dict, Any, Optional
from agile_bot.bots.base_bot.src.utils import read_json_file


class KnowledgeGraph:
    """Built knowledge graph loaded from story-graph.json.
    
    Domain Model:
        Properties: content, path
    """
    
    def __init__(self, docs_dir: Path):
        """Initialize KnowledgeGraph.
        
        Args:
            docs_dir: Path to docs directory containing story-graph.json
        """
        self._docs_dir = docs_dir
        self._content: Dict[str, Any] = {}
        self._path: Optional[Path] = None
        self._load()
    
    def _load(self):
        """Load knowledge graph from story-graph.json file."""
        # Find story-graph.json in docs directory
        knowledge_graph_path = self._docs_dir / 'story-graph.json'
        
        if not knowledge_graph_path.exists():
            raise FileNotFoundError(
                f"Knowledge graph file not found at {knowledge_graph_path}. "
                f"Cannot validate rules without knowledge graph. "
                f"Expected knowledge graph to be created by build_knowledge action before validate_rules."
            )
        
        self._content = read_json_file(knowledge_graph_path)
        self._path = knowledge_graph_path
    
    @property
    def content(self) -> Dict[str, Any]:
        """Get knowledge graph content.
        
        Domain Model: content
        """
        return self._content
    
    @property
    def path(self) -> Path:
        """Get path to knowledge graph file.
        
        Domain Model: path
        """
        return self._path

