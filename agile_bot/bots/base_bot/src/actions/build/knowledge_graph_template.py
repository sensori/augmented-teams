from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.utils import read_json_file


class KnowledgeGraphTemplate:
    def __init__(self, kg_dir: Path, template_filename: str):
        self._kg_dir = kg_dir
        self._template_filename = template_filename
        self._template_content: Dict[str, Any] = {}
        self._load_template()
    
    def _load_template(self):
        template_path = self._kg_dir / self._template_filename
        
        self._template_content = read_json_file(template_path)
        self._template_path = template_path
    
    @property
    def schema(self) -> Dict[str, Any]:
        return self._template_content
    
    @property
    def template_content(self) -> Dict[str, Any]:
        return self._template_content
    
    @property
    def template_path(self) -> Path:
        return self._template_path




