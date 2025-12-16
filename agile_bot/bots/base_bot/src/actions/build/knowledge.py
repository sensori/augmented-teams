from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.actions.build.knowledge_graph_spec import KnowledgeGraphSpec


class Knowledge:
    def __init__(self, behavior_folder: Path):
        self._behavior_folder = behavior_folder
        kg_dir = behavior_folder / 'content' / 'knowledge_graph'
        
        # If knowledge graph folder doesn't exist, set to None (optional for some behaviors)
        if not kg_dir.exists():
            self._kg_dir = None
            self.knowledge_graph_spec = None
            self.knowledge_graph_template = None
        else:
            self._kg_dir = kg_dir
            # Instantiate KnowledgeGraphSpec (which lazily loads KnowledgeGraphTemplate via template property)
            self.knowledge_graph_spec = KnowledgeGraphSpec(self._kg_dir)
            # Access template through KnowledgeGraphSpec
            self.knowledge_graph_template = self.knowledge_graph_spec.template
    
    @property
    def instructions(self) -> Dict[str, Any]:
        if not self._kg_dir or not self.knowledge_graph_spec or not self.knowledge_graph_template:
            return {}
        
        return {
            'knowledge_graph_template': self.knowledge_graph_template.template_content,
            'knowledge_graph_config': self.knowledge_graph_spec.config_data,
            'template_path': str(self.knowledge_graph_template.template_path),
            'config_path': str(self.knowledge_graph_spec.config_path)
        }

