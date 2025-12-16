from pathlib import Path
from typing import Dict, Any, Optional
import logging
from agile_bot.bots.base_bot.src.actions.action import Action
from agile_bot.bots.base_bot.src.actions.base_action_config import BaseActionConfig
from agile_bot.bots.base_bot.src.actions.build.knowledge import Knowledge
from agile_bot.bots.base_bot.src.actions.build.knowledge_graph_spec import KnowledgeGraphSpec
from agile_bot.bots.base_bot.src.actions.build.knowledge_graph_template import KnowledgeGraphTemplate
from agile_bot.bots.base_bot.src.actions.validate.story_graph import StoryGraph
from agile_bot.bots.base_bot.src.actions.validate.validate_action import ValidateRulesAction

logger = logging.getLogger(__name__)


class BuildKnowledgeAction(Action):
    def __init__(self, base_action_config=None, behavior=None, activity_tracker=None,
                 bot_name: str = None, action_name: str = None):
      
        if base_action_config is not None:
            super().__init__(base_action_config=base_action_config, behavior=behavior,
                            activity_tracker=activity_tracker)
        else:
            if action_name is None:
                action_name = 'build_knowledge'
            # Pass action_name to super to use the bot_name/action_name path
            super().__init__(base_action_config=None, behavior=behavior,
                            activity_tracker=activity_tracker, bot_name=bot_name, action_name=action_name)
        
        # Instantiate Knowledge from behavior folder
        if self.behavior:
            behavior_folder = self.behavior.folder
            self._knowledge = Knowledge(behavior_folder)
        else:
            self._knowledge = None
    
    @property
    def knowledge(self) -> Optional[Knowledge]:
        if self._knowledge is None and self.behavior:
            behavior_folder = self.behavior.folder
            self._knowledge = Knowledge(behavior_folder)
        return self._knowledge
    
    @property
    def knowledge_graph_spec(self) -> Optional[KnowledgeGraphSpec]:
        if self.knowledge and self.knowledge.knowledge_graph_spec:
            return self.knowledge.knowledge_graph_spec
        return None
    
    @property
    def knowledge_graph_template(self) -> Optional[KnowledgeGraphTemplate]:
        if self.knowledge and self.knowledge.knowledge_graph_template:
            return self.knowledge.knowledge_graph_template
        return None
    
    @property
    def rules(self):
        if not self.behavior:
            return None
        base_action_config = BaseActionConfig('validate', self.behavior.bot_paths)
        return ValidateRulesAction(
            base_action_config=base_action_config,
            behavior=self.behavior,
            activity_tracker=None
        )
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # Get instructions from base class (already merged from BaseActionConfig and Behavior)
        instructions = self.instructions.copy()
        
        # Inject knowledge graph data (knowledge_graph_spec, knowledge_graph_template) from Knowledge
        # Only inject if there are actual knowledge graph components
        if self.knowledge and self.knowledge.instructions:
            kg_instructions = self.knowledge.instructions
            if kg_instructions:
                instructions.update(kg_instructions)
                
                # Check if output file exists and add update instructions
                if self.knowledge_graph_spec:
                    output_path = self.knowledge_graph_spec.output_path
                    output_filename = self.knowledge_graph_spec.output_filename
                    
                    try:
                        story_graph = StoryGraph(self.behavior.bot_paths, self.working_dir)
                        instructions['existing_file'] = {
                            'path': str(story_graph.path),
                            'exists': True
                        }
                        instructions['update_mode'] = True
                        instructions['update_instructions'] = {
                            'mode': 'update_existing',
                            'message': f"**CRITICAL: Output file '{output_filename}' already exists at '{output_path}/{output_filename}'. You MUST UPDATE this existing file by adding/modifying only the content needed for this behavior. DO NOT create a new file.**",
                            'existing_file_path': str(story_graph.path),
                            'preserve_existing': [
                                item for item in [
                                    'epics' if story_graph.has_epics else None,
                                    'increments' if story_graph.has_increments else None,
                                    'domain_concepts' if story_graph.has_domain_concepts else None,
                                ] if item is not None
                            ],
                            'add_or_modify': self._determine_add_or_modify_content()
                        }
                    except FileNotFoundError:
                        pass
        
        # Inject rules (bot-level, behavior-level, and validation rules)
        self.inject_rules(instructions)
        
        return {'instructions': instructions}
    
    def _determine_add_or_modify_content(self) -> list:
        behavior_to_content = {
            'shape': [],
            'prioritization': ['increments'],
            'discovery': ['story refinements', 'increments', 'domain_concepts'],
            'exploration': ['acceptance_criteria', 'domain_concepts'],
            'scenarios': ['scenarios', 'domain_concepts'],
            'tests': ['test_implementations', 'domain_concepts'],
        }
        return behavior_to_content.get(self.behavior.name, [])
    
    def inject_rules(self, instructions: Dict[str, Any]) -> None:
        # Always try to replace {{rules}} placeholder, even if no rules are found
        if 'base_instructions' not in instructions:
            return
        
        validate_action = self.rules
        rules_text = ""
        all_rules = []
        
        if validate_action:
            rules_obj = validate_action.rules
            if rules_obj:
                rules_text = rules_obj.formatted_rules()
                rules_data = validate_action.inject_behavior_specific_and_bot_rules()
                all_rules = rules_data.get('validation_rules', [])
        
        # Replace {{rules}} placeholder in base_instructions
        new_instructions = []
        for line in instructions['base_instructions']:
            if isinstance(line, str) and '{{rules}}' in line:
                # Replace {{rules}} placeholder with actual rules text
                if rules_text and rules_text != "No validation rules found.":
                    rules_lines = rules_text.split('\n')
                    new_instructions.extend(rules_lines)
                # If no rules found, remove the placeholder line entirely (don't add it)
            else:
                new_instructions.append(line)
        instructions['base_instructions'] = new_instructions
        
        instructions['rules'] = all_rules
