from pathlib import Path
from typing import Dict, Any, Optional
from agile_bot.bots.base_bot.src.utils import read_json_file


class KnowledgeGraphSpec:
    def __init__(self, kg_dir: Path):
        self._kg_dir = kg_dir
        self._config_data: Dict[str, Any] = {}
        self._template: Optional['KnowledgeGraphTemplate'] = None
        self._load_config()
    
    def _load_config(self):
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
        return self._config_data.get('path', 'docs/stories')
    
    @property
    def output_filename(self) -> str:
        return self._config_data.get('output', 'story-graph.json')
    
    @property
    def template_filename(self) -> str:
        template_filename = self._config_data.get('template')
        if not template_filename:
            raise ValueError(
                f'No template specified in {self._config_path}'
            )
        return template_filename
    
    @property
    def template(self) -> 'KnowledgeGraphTemplate':
        if self._template is None:
            from agile_bot.bots.base_bot.src.actions.build.knowledge_graph_template import KnowledgeGraphTemplate
            self._template = KnowledgeGraphTemplate(
                self._kg_dir,
                self.template_filename
            )
        return self._template
    
    @property
    def config_data(self) -> Dict[str, Any]:
        return self._config_data
    
    @property
    def config_path(self) -> Path:
        return self._config_path

