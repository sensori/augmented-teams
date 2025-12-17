from pathlib import Path
from typing import Dict, Any, Optional
import logging
from agile_bot.bots.base_bot.src.actions.action import Action
from agile_bot.bots.base_bot.src.actions.build.knowledge import Knowledge
from agile_bot.bots.base_bot.src.actions.build.knowledge_graph_spec import KnowledgeGraphSpec
from agile_bot.bots.base_bot.src.actions.build.knowledge_graph_template import KnowledgeGraphTemplate
from agile_bot.bots.base_bot.src.actions.validate.validate_action import ValidateRulesAction

logger = logging.getLogger(__name__)


class BuildKnowledgeAction(Action):
    def __init__(self, behavior=None, action_config=None):
        super().__init__(behavior=behavior, action_config=action_config)
        self._knowledge = Knowledge(self.behavior)
    
    @property
    def action_name(self) -> str:
        """Action name is always 'build' for BuildKnowledgeAction."""
        return 'build'
    
    @action_name.setter
    def action_name(self, value: str):
        raise AttributeError("action_name is read-only for BuildKnowledgeAction")
       
    
    @property
    def knowledge(self) -> Optional[Knowledge]:
        self._knowledge = Knowledge(self.behavior)
        return self._knowledge
    
    @property
    def knowledge_graph_spec(self) -> Optional[KnowledgeGraphSpec]:
        return self.knowledge.knowledge_graph_spec
    
    @property
    def knowledge_graph_template(self) -> Optional[KnowledgeGraphTemplate]:
        return self.knowledge.knowledge_graph_template
    
    @property
    def rules(self):
        return ValidateRulesAction(behavior=self.behavior, action_config=None)
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # Get instructions from base class (already merged from BaseActionConfig and Behavior)
        instructions = self.instructions.copy()
        
        # Inject knowledge graph data (knowledge_graph_spec, knowledge_graph_template) from Knowledge
        kg_instructions = self.knowledge.instructions
        instructions.update(kg_instructions)
        
        # Check if output file exists and add update instructions
        story_graph = self.knowledge_graph_spec.knowledge_graph
        instructions['existing_file'] = {
            'path': str(story_graph.path),
            'exists': True
        }
        instructions['update_mode'] = True
        instructions['update_instructions'] = {
            'mode': 'update_existing',
            'message': f"**CRITICAL: Output file '{story_graph.path.name}' already exists. You MUST UPDATE this existing file by adding/modifying only the content needed for this behavior. DO NOT create a new file.**",
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
        validate_action = self.rules
        rules_obj = validate_action.rules
        rules_text = rules_obj.formatted_rules()
        rules_data = validate_action.inject_behavior_specific_and_bot_rules()
        all_rules = rules_data.get('validation_rules', [])
        
        # Replace {{rules}} placeholder in base_instructions
        new_instructions = []
        for line in instructions['base_instructions']:
            if isinstance(line, str) and '{{rules}}' in line:
                # Replace {{rules}} placeholder with actual rules text
                if rules_text != "No validation rules found.":
                    rules_lines = rules_text.split('\n')
                    new_instructions.extend(rules_lines)
                # If no rules found, remove the placeholder line entirely (don't add it)
            else:
                new_instructions.append(line)
        instructions['base_instructions'] = new_instructions
        
        instructions['rules'] = all_rules
