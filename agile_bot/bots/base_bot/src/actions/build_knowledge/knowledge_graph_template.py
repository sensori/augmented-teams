"""
KnowledgeGraphTemplate class.

Loads knowledge graph template from template file.
"""
from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.utils import read_json_file


class KnowledgeGraphTemplate:
    """Knowledge graph template.
    
    Domain Model:
        Property: schema
    """
    
    def __init__(self, kg_dir: Path, template_filename: str):
        """Initialize KnowledgeGraphTemplate.
        
        Args:
            kg_dir: Path to content/knowledge_graph directory
            template_filename: Name of template file
        """
        self._kg_dir = kg_dir
        self._template_filename = template_filename
        self._template_content: Dict[str, Any] = {}
        self._load_template()
    
    def _load_template(self):
        """Load template from template file."""
        template_path = self._kg_dir / self._template_filename
        if not template_path.exists():
            raise FileNotFoundError(
                f'Template file not found: {template_path}'
            )
        
        self._template_content = read_json_file(template_path)
        self._template_path = template_path
    
    @property
    def schema(self) -> Dict[str, Any]:
        """Get schema from template.
        
        Domain Model: schema
        """
        return self._template_content
    
    @property
    def template_content(self) -> Dict[str, Any]:
        """Get full template content."""
        return self._template_content
    
    @property
    def template_path(self) -> Path:
        """Get path to template file."""
        return self._template_path



