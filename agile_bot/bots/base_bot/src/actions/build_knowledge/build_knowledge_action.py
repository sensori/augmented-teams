from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging
import os
from agile_bot.bots.base_bot.src.actions.action import Action
from agile_bot.bots.base_bot.src.actions.build_knowledge.knowledge import Knowledge
from agile_bot.bots.base_bot.src.actions.build_knowledge.knowledge_graph_spec import KnowledgeGraphSpec
from agile_bot.bots.base_bot.src.actions.build_knowledge.knowledge_graph_template import KnowledgeGraphTemplate

logger = logging.getLogger(__name__)


class BuildKnowledgeAction(Action):
    """Build knowledge action for constructing knowledge graphs.
    
    Domain Model:
        Instantiated with: Behavior, BaseActionsConfig, BehaviorConfig
        Properties: knowledge_graph_spec, knowledge_graph_template, rules
    """
    
    def __init__(self, base_action_config=None, behavior=None, activity_tracker=None,
                 bot_name: str = None, action_name: str = 'build_knowledge'):
        """Initialize BuildKnowledgeAction.
        
        Domain Model: Instantiated with: Behavior, BaseActionsConfig, BehaviorConfig
        """
        super().__init__(base_action_config=base_action_config, behavior=behavior,
                        activity_tracker=activity_tracker, bot_name=bot_name, action_name=action_name)
        
        # Instantiate Knowledge from behavior folder
        if self.behavior:
            behavior_folder = self.behavior.folder
            self._knowledge = Knowledge(behavior_folder)
        else:
            self._knowledge = None
    
    @property
    def knowledge(self) -> Optional[Knowledge]:
        """Get Knowledge instance.
        
        Domain Model: Knowledge aggregates KnowledgeGraphSpec and KnowledgeGraphTemplate
        """
        if self._knowledge is None and self.behavior:
            behavior_folder = self.behavior.folder
            self._knowledge = Knowledge(behavior_folder)
        return self._knowledge
    
    @property
    def knowledge_graph_spec(self) -> Optional[KnowledgeGraphSpec]:
        """Get knowledge graph spec.
        
        Domain Model: knowledge_graph_spec
        """
        if self.knowledge and self.knowledge.knowledge_graph_spec:
            return self.knowledge.knowledge_graph_spec
        return None
    
    @property
    def knowledge_graph_template(self) -> Optional[KnowledgeGraphTemplate]:
        """Get knowledge graph template.
        
        Domain Model: knowledge_graph_template
        """
        if self.knowledge and self.knowledge.knowledge_graph_template:
            return self.knowledge.knowledge_graph_template
        return None
    
    @property
    def rules(self):
        """Get rules (ValidateRulesAction instance).
        
        Domain Model: rules
        """
        from agile_bot.bots.base_bot.src.actions.validate_rules.validate_rules_action import ValidateRulesAction
        return ValidateRulesAction(
            base_action_config=None,
            behavior=self.behavior,
            activity_tracker=None,
            bot_name=self.bot_name,
            action_name='validate_rules'
        )
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute build_knowledge action logic."""
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
                    existing_file_info = self._check_existing_output_file(output_path, output_filename)
                    
                    if existing_file_info:
                        instructions['existing_file'] = existing_file_info
                        instructions['update_mode'] = True
                        instructions['update_instructions'] = {
                            'mode': 'update_existing',
                            'message': f"**CRITICAL: Output file '{output_filename}' already exists at '{output_path}/{output_filename}'. You MUST UPDATE this existing file by adding/modifying only the content needed for this behavior. DO NOT create a new file.**",
                            'existing_file_path': existing_file_info['path'],
                            'preserve_existing': [
                                item for item in [
                                    'epics' if existing_file_info.get('has_epics') else None,
                                    'domain_concepts' if existing_file_info.get('has_domain_concepts') else None,
                                ] if item is not None
                            ],
                            'add_or_modify': self._determine_add_or_modify_content()
                        }
        
        # Inject rules (bot-level, behavior-level, and validation rules)
        self.inject_rules(instructions)
        
        return {'instructions': instructions}
    
    def _check_existing_output_file(self, output_path: str, output_filename: str) -> Dict[str, Any]:
        """Check if the output file already exists and return information about it."""
        working_area = os.environ.get('WORKING_AREA')
        if not working_area:
            return None
        
        project_root = Path(working_area)
        output_file_path = project_root / output_path / output_filename
        
        if output_file_path.exists():
            try:
                with open(output_file_path, 'r', encoding='utf-8') as f:
                    existing_content = json.load(f)
                
                return {
                    'path': str(output_file_path),
                    'exists': True,
                    'has_epics': 'epics' in existing_content,
                    'has_increments': 'increments' in existing_content,
                    'has_domain_concepts': any(
                        'domain_concepts' in epic for epic in existing_content.get('epics', [])
                    ),
                    'structure_summary': {
                        'epic_count': len(existing_content.get('epics', [])),
                        'has_increments': 'increments' in existing_content
                    }
                }
            except (json.JSONDecodeError, IOError):
                return {
                    'path': str(output_file_path),
                    'exists': True,
                    'readable': False
                }
        
        return None
    
    def _determine_add_or_modify_content(self) -> list:
        """Determine what content should be added or modified based on the current behavior."""
        behavior_to_content = {
            'prioritization': ['increments'],
            'discovery': ['story refinements', 'increments', 'domain_concepts'],
            'exploration': ['acceptance_criteria', 'domain_concepts'],
            'scenarios': ['scenarios', 'domain_concepts'],
            'tests': ['test_implementations', 'domain_concepts'],
        }
        return behavior_to_content.get(self.behavior.name, ['knowledge_graph'])
    
    def inject_rules(self, instructions: Dict[str, Any]) -> None:
        """Inject all relevant rules (bot-level, behavior-level, and validation rules) into the instructions."""
        validate_action = self.rules
        rules_data = validate_action.inject_behavior_specific_and_bot_rules()
        all_rules = rules_data.get('validation_rules', [])
        
        rules_text = self._format_rules(all_rules)
        
        if 'base_instructions' in instructions:
            new_instructions = []
            for line in instructions['base_instructions']:
                if '{{rules}}' in line:
                    rules_lines = rules_text.split('\n')
                    new_instructions.extend(rules_lines)
                else:
                    new_instructions.append(line)
            instructions['base_instructions'] = new_instructions
        
        instructions['rules'] = all_rules
    
    def _format_rules(self, rules: list) -> str:
        """Format rules list into a readable text string for insertion into instructions."""
        if not rules:
            return "No validation rules found."
        
        formatted_sections = []
        bot_rules = []
        behavior_rules = []
        
        for rule in rules:
            rule_file = rule.get('rule_file', '')
            if 'base_bot/rules' in rule_file or (not 'behaviors' in rule_file and '/rules/' in rule_file):
                bot_rules.append(rule)
            else:
                behavior_rules.append(rule)
        
        if bot_rules:
            formatted_sections.append("**Bot-level rules:**")
            for rule in bot_rules:
                formatted_sections.extend(self._format_rule(rule))
        
        if behavior_rules:
            formatted_sections.append("**Behavior-level rules:**")
            for rule in behavior_rules:
                formatted_sections.extend(self._format_rule(rule))
        
        if not formatted_sections:
            return "No validation rules found."
        
        return "\n".join(formatted_sections)
    
    def _format_rule(self, rule: Dict[str, Any]) -> list:
        """Format a single rule into a list of formatted strings."""
        formatted = []
        rule_file = rule.get('rule_file', 'unknown')
        rule_content = rule.get('rule_content', {})
        rule_description = rule_content.get('description', '')
        
        formatted.append(f"\n**Rule:** {rule_file}")
        if rule_description:
            formatted.append(f"{rule_description}")
        
        if 'do' in rule_content:
            do_examples = rule_content.get('do', {}).get('examples', [])
            if do_examples:
                formatted.append("\n**DO:**")
                for example in do_examples:
                    desc = example.get('description', '')
                    content = example.get('content', '')
                    if isinstance(content, list):
                        content = '\n'.join(content)
                    if desc:
                        formatted.append(f"- {desc}: {content}")
                    else:
                        formatted.append(f"- {content}")
        
        if 'dont' in rule_content:
            dont_examples = rule_content.get('dont', {}).get('examples', [])
            if dont_examples:
                formatted.append("\n**DON'T:**")
                for example in dont_examples:
                    desc = example.get('description', '')
                    content = example.get('content', '')
                    if isinstance(content, list):
                        content = '\n'.join(content)
                    if desc:
                        formatted.append(f"- {desc}: {content}")
                    else:
                        formatted.append(f"- {content}")
        
        if 'examples' in rule_content:
            examples = rule_content.get('examples', [])
            for example in examples:
                if 'do' in example:
                    do_content = example.get('do', {})
                    desc = do_content.get('description', '')
                    content = do_content.get('content', '')
                    if isinstance(content, list):
                        content = '\n'.join(content)
                    formatted.append(f"\n**DO:** {desc}")
                    formatted.append(content)
                if 'dont' in example:
                    dont_content = example.get('dont', {})
                    desc = dont_content.get('description', '')
                    content = dont_content.get('content', '')
                    if isinstance(content, list):
                        content = '\n'.join(content)
                    formatted.append(f"\n**DON'T:** {desc}")
                    formatted.append(content)
        
        formatted.append("")
        return formatted
