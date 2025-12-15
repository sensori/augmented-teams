"""
KnowledgeGraphSpec class.

Loads knowledge graph specification from config file.
"""
from pathlib import Path
from typing import Dict, Any, Optional
from agile_bot.bots.base_bot.src.utils import read_json_file


class KnowledgeGraphSpec:
    """Knowledge graph specification.
    
    Domain Model:
        Properties: output_path, output_filename, template_filename, template
    """
    
    def __init__(self, kg_dir: Path):
        """Initialize KnowledgeGraphSpec.
        
        Args:
            kg_dir: Path to content/knowledge_graph directory
        """
        self._kg_dir = kg_dir
        self._config_data: Dict[str, Any] = {}
        self._template: Optional['KnowledgeGraphTemplate'] = None
        self._load_config()
    
    def _load_config(self):
        """Load config from first JSON file in knowledge_graph directory."""
        config_files = list(self._kg_dir.glob('*.json'))
        if not config_files:
            raise FileNotFoundError(
                f'Knowledge graph config not found in {self._kg_dir}'
            )
        
        config_path = config_files[0]
        self._config_data = read_json_file(config_path)
        self._config_path = config_path
    
    @property
    def output_path(self) -> str:
        """Get output path.
        
        Domain Model: output_path
        """
        return self._config_data.get('path', 'docs/stories')
    
    @property
    def output_filename(self) -> str:
        """Get output filename.
        
        Domain Model: output_filename
        """
        return self._config_data.get('output', 'story-graph.json')
    
    @property
    def template_filename(self) -> str:
        """Get template filename.
        
        Domain Model: template_filename
        """
        template_filename = self._config_data.get('template')
        if not template_filename:
            raise ValueError(
                f'No template specified in {self._config_path}'
            )
        return template_filename
    
    @property
    def template(self) -> 'KnowledgeGraphTemplate':
        """Get KnowledgeGraphTemplate instance.
        
        Domain Model: template (points to KnowledgeGraphTemplate)
        """
        if self._template is None:
            from agile_bot.bots.base_bot.src.actions.build_knowledge.knowledge_graph_template import KnowledgeGraphTemplate
            self._template = KnowledgeGraphTemplate(
                self._kg_dir,
                self.template_filename
            )
        return self._template
    
    @property
    def config_data(self) -> Dict[str, Any]:
        """Get full config data."""
        return self._config_data
    
    @property
    def config_path(self) -> Path:
        """Get path to config file."""
        return self._config_path

