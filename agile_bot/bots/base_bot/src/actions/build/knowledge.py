from pathlib import Path
from typing import Dict, Any, TYPE_CHECKING
from agile_bot.bots.base_bot.src.actions.build.knowledge_graph_spec import KnowledgeGraphSpec

if TYPE_CHECKING:
    from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
    from agile_bot.bots.base_bot.src.bot.behavior import Behavior


class Knowledge:
    def __init__(self, behavior: 'Behavior'):
        self._behavior = behavior
        kg_dir = behavior.folder / 'content' / 'knowledge_graph'
        self._kg_dir = kg_dir
        self.knowledge_graph_spec = KnowledgeGraphSpec(self._kg_dir, behavior.bot_paths)
        self.knowledge_graph_template = self.knowledge_graph_spec.template
    
    @property
    def instructions(self) -> Dict[str, Any]:
        return {
            'knowledge_graph_template': self.knowledge_graph_template.template_content,
            'knowledge_graph_config': self.knowledge_graph_spec.config_data,
            'template_path': str(self.knowledge_graph_template.template_path),
            'config_path': str(self.knowledge_graph_spec.config_path)
        }

