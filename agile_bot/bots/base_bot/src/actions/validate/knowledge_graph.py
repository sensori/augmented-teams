from pathlib import Path
from typing import Dict, Any, Optional
from agile_bot.bots.base_bot.src.utils import read_json_file


class KnowledgeGraph:
    def __init__(self, docs_dir: Path):
        self._docs_dir = docs_dir
        self._content: Dict[str, Any] = {}
        self._path: Optional[Path] = None
        self._load()
    
    def _load(self):
        knowledge_graph_path = self._docs_dir / 'story-graph.json'
        self._content = read_json_file(knowledge_graph_path)
        self._path = knowledge_graph_path
    
    @property
    def content(self) -> Dict[str, Any]:
        return self._content
    
    @property
    def path(self) -> Path:
        return self._path
