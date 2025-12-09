from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.bot.base_action import BaseAction

# Note: All file reads in this module use UTF-8 encoding for Windows compatibility


class BuildKnowledgeAction(BaseAction):
    
    def __init__(self, bot_name: str, behavior: str, workspace_root: Path):
        super().__init__(bot_name, behavior, workspace_root, 'build_knowledge')
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute build_knowledge action logic."""
        try:
            instructions = self.inject_knowledge_graph_template()
        except FileNotFoundError:
            # Fallback for behaviors without knowledge_graph: check for behavior-specific templates
            instructions = self.inject_behavior_specific_templates()
        return {'instructions': instructions}
    
    def inject_knowledge_graph_template(self) -> Dict[str, Any]:
        # Find behavior folder (handles numbered prefixes)
        from agile_bot.bots.base_bot.src.bot.bot import Behavior
        behavior_folder = Behavior.find_behavior_folder(
            self.workspace_root,
            self.bot_name,
            self.behavior
        )
        kg_dir = behavior_folder / 'content' / 'knowledge_graph'
        
        if not kg_dir.exists():
            raise FileNotFoundError(
                f'Knowledge graph template not found at {kg_dir}'
            )
        
        # Find any JSON template in the directory
        templates = list(kg_dir.glob('*.json'))
        if not templates:
            raise FileNotFoundError(
                f'Knowledge graph template not found in {kg_dir}'
            )
        
        template_path = templates[0]
        
        return {
            'knowledge_graph_template': str(template_path)
        }

    def inject_behavior_specific_templates(self) -> Dict[str, Any]:
        """
        For behaviors that don't use knowledge_graph, optionally load behavior-specific templates.
        Example: tests behavior uses story-graph-tests.json and test_file.json under 2_content/.
        """
        from agile_bot.bots.base_bot.src.bot.bot import Behavior
        try:
            behavior_folder = Behavior.find_behavior_folder(
                self.workspace_root,
                self.bot_name,
                self.behavior
            )
        except FileNotFoundError:
            return {}

        instructions: Dict[str, Any] = {}

        # Look for 2_content/test_file.json
        test_file_cfg = behavior_folder / '2_content' / 'test_file.json'
        if test_file_cfg.exists():
            instructions['test_file_config'] = str(test_file_cfg)

        # Look for 2_content/templates/story-graph-tests.json
        tests_template = behavior_folder / '2_content' / 'templates' / 'story-graph-tests.json'
        if tests_template.exists():
            instructions['tests_template'] = str(tests_template)

        return instructions



