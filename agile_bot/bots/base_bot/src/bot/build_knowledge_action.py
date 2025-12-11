from pathlib import Path
from typing import Dict, Any
import json
import logging
from agile_bot.bots.base_bot.src.bot.base_action import BaseAction
from agile_bot.bots.base_bot.src.bot.behavior_folder_finder import find_nested_subfolder, find_behavior_subfolder
from agile_bot.bots.base_bot.src.utils import read_json_file

# Note: All file reads in this module use UTF-8 encoding for Windows compatibility

logger = logging.getLogger(__name__)


class BuildKnowledgeAction(BaseAction):
    
    def __init__(self, bot_name: str, behavior: str, bot_directory: Path):
        super().__init__(bot_name, behavior, bot_directory, 'build_knowledge')
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute build_knowledge action logic."""
        logger.info(f"Starting build_knowledge action for behavior {self.behavior}")
        
        try:
            # Load and merge base instructions with behavior-specific instructions
            logger.debug("Loading and merging instructions...")
            instructions = self.load_and_merge_instructions()
            logger.debug(f"Loaded {len(instructions.get('base_instructions', []))} base instruction lines")
            
            # Inject knowledge graph template and config
            logger.debug("Injecting knowledge graph template...")
            kg_data = self.inject_knowledge_graph_template()
            instructions.update(kg_data)
            logger.debug("Knowledge graph template injected")
            
            # Inject schema, description, and instructions template variables
            logger.debug("Injecting schema and description...")
            self.inject_schema_description_instructions(instructions)
            logger.debug("Schema and description injected")
            
            # Add explicit update instructions if existing file was found
            if instructions.get('existing_file') and instructions.get('update_mode'):
                existing_file = instructions['existing_file']
                config = instructions['knowledge_graph_config']
                output_path = config.get('path', 'docs/stories')
                output_filename = config.get('output', 'story-graph.json')
                
                instructions['update_instructions'] = {
                    'mode': 'update_existing',
                    'message': f"**CRITICAL: Output file '{output_filename}' already exists at '{output_path}/{output_filename}'. You MUST UPDATE this existing file by adding/modifying only the content needed for this behavior. DO NOT create a new file.**",
                    'existing_file_path': existing_file['path'],
                    'preserve_existing': [
                        'epics' if existing_file.get('has_epics') else None,
                        'domain_concepts' if existing_file.get('has_domain_concepts') else None,
                    ],
                    'add_or_modify': self._determine_add_or_modify_content()
                }
                # Remove None values
                instructions['update_instructions']['preserve_existing'] = [
                    item for item in instructions['update_instructions']['preserve_existing'] if item is not None
                ]
                logger.debug("Update instructions added for existing file")

            # Inject all rules (bot-level, behavior-level, and validation rules) into instructions
            logger.debug("Injecting rules (this may take a moment)...")
            self.inject_rules(instructions)
            rules_count = len(instructions.get('rules', []))
            logger.debug(f"Injected {rules_count} rules")
            
            # Update token estimate after all injections
            instructions['token_estimate'] = self._estimate_tokens(instructions)
            logger.info(f"build_knowledge action completed. Token estimate: {instructions['token_estimate']}")
            
            return {'instructions': instructions}
        except Exception as e:
            logger.error(f"Error in build_knowledge action: {e}", exc_info=True)
            raise
    
    def load_and_merge_instructions(self) -> Dict[str, Any]:
        """Load and merge base instructions with behavior-specific instructions."""
        # Load base instructions - check for numbered prefix folders
        base_actions_dir = self.base_actions_dir
        
        # Try with and without number prefix - prefer numbered folders
        base_path = None
        matching_folders = sorted(base_actions_dir.glob('*build_knowledge'))
        # Prioritize folders that start with a digit
        for folder in matching_folders:
            if folder.name[0].isdigit():
                instructions_file = folder / 'instructions.json'
                if instructions_file.exists():
                    base_path = instructions_file
                    break
        
        # Fall back to non-numbered folder if no numbered folder found
        if not base_path:
            for folder in matching_folders:
                instructions_file = folder / 'instructions.json'
                if instructions_file.exists():
                    base_path = instructions_file
                    break
        
        if not base_path:
            base_path = base_actions_dir / 'build_knowledge' / 'instructions.json'
        
        if not base_path.exists():
            raise FileNotFoundError(
                f'Base instructions not found for action build_knowledge at {base_path}'
            )
        
        base_instructions = read_json_file(base_path)
        
        # Load behavior-specific instructions (optional)
        # For build_knowledge, behavior-specific instructions are in:
        # behaviors/{behavior}/2_content/1_knowledge_graph/instructions.json
        behavior_instructions = None
        try:
            from agile_bot.bots.base_bot.src.bot.bot import Behavior
            behavior_folder = Behavior.find_behavior_folder(
                self.bot_directory,
                self.bot_name,
                self.behavior
            )
            # Find content/knowledge_graph folder (handles numbered prefixes)
            kg_dir = find_nested_subfolder(behavior_folder, 'content', 'knowledge_graph')
            if kg_dir:
                behavior_path = kg_dir / 'instructions.json'
                if behavior_path.exists():
                    behavior_instructions = read_json_file(behavior_path)
        except FileNotFoundError:
            pass
        
        # Merge instructions
        merged = {
            'action': 'build_knowledge',
            'behavior': self.behavior,
            'base_instructions': base_instructions.get('instructions', []),
        }
        
        if behavior_instructions:
            merged['behavior_instructions'] = behavior_instructions.get('instructions', [])
        
        return merged
    
    def _determine_add_or_modify_content(self) -> list:
        """
        Determine what content should be added or modified based on the current behavior.
        
        Returns:
            List of content types to add/modify
        """
        behavior_to_content = {
            'prioritization': ['increments'],
            'discovery': ['story refinements', 'increments', 'domain_concepts'],
            'exploration': ['acceptance_criteria', 'domain_concepts'],
            'scenarios': ['scenarios', 'domain_concepts'],
            'tests': ['test_implementations', 'domain_concepts'],
        }
        
        return behavior_to_content.get(self.behavior, ['knowledge_graph'])
    
    def inject_knowledge_graph_template(self) -> Dict[str, Any]:
        # Find behavior folder (handles numbered prefixes)
        from agile_bot.bots.base_bot.src.bot.bot import Behavior
        behavior_folder = Behavior.find_behavior_folder(
            self.bot_directory,
            self.bot_name,
            self.behavior
        )
        
        # Find content/knowledge_graph folder (handles numbered prefixes)
        kg_dir = find_nested_subfolder(behavior_folder, 'content', 'knowledge_graph')
        
        if not kg_dir:
            raise FileNotFoundError(
                f'Knowledge graph folder not found under {behavior_folder}'
            )
        
        # Find config files (e.g., build_story_graph_outline.json)
        config_files = list(kg_dir.glob('*.json'))
        if not config_files:
            raise FileNotFoundError(
                f'Knowledge graph config not found in {kg_dir}'
            )
        
        # Load the first config file to get template reference
        config_path = config_files[0]
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Get the template filename from config
        template_filename = config_data.get('template')
        if not template_filename:
            raise ValueError(
                f'No template specified in {config_path}'
            )
        
        # Load the actual template file
        template_path = kg_dir / template_filename
        if not template_path.exists():
            raise FileNotFoundError(
                f'Template file not found: {template_path}'
            )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = json.load(f)
        
        # Extract schema from template (includes _explanation + full template structure)
        schema_text = self._extract_schema_from_template(template_content)
        
        # Check if output file exists and add update instructions
        output_path = config_data.get('path', 'docs/stories')
        output_filename = config_data.get('output', 'story-graph.json')
        existing_file_info = self._check_existing_output_file(output_path, output_filename)
        
        result = {
            'knowledge_graph_template': template_content,
            'knowledge_graph_config': config_data,
            'template_path': str(template_path),
            'config_path': str(config_path),
            'schema': schema_text
        }
        
        # Add existing file information if file exists
        if existing_file_info:
            result['existing_file'] = existing_file_info
            result['update_mode'] = True
        
        return result
    
    def _check_existing_output_file(self, output_path: str, output_filename: str) -> Dict[str, Any]:
        """
        Check if the output file already exists and return information about it.
        
        Args:
            output_path: Relative path from project root (e.g., 'docs/stories')
            output_filename: Output filename (e.g., 'story-graph.json')
            
        Returns:
            Dict with existing file info if file exists, None otherwise
        """
        import os
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
                # File exists but can't be read - return basic info
                return {
                    'path': str(output_file_path),
                    'exists': True,
                    'readable': False
                }
        
        return None

    def inject_rules(self, instructions: Dict[str, Any]) -> None:
        """
        Inject all relevant rules (bot-level, behavior-level, and validation rules) 
        into the instructions, replacing the {{rules}} placeholder.
        """
        logger.debug("Creating ValidateRulesAction instance...")
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        
        # Create ValidateRulesAction instance to reuse its rule-loading logic
        validate_action = ValidateRulesAction(
            bot_name=self.bot_name,
            behavior=self.behavior,
            bot_directory=self.bot_directory
        )
        
        # Load all rules (common/bot-level + behavior-specific)
        logger.debug("Loading rules from ValidateRulesAction...")
        rules_data = validate_action.inject_behavior_specific_and_bot_rules()
        all_rules = rules_data.get('validation_rules', [])
        logger.debug(f"Loaded {len(all_rules)} rules")
        
        # Format rules for insertion into instructions
        logger.debug("Formatting rules for instructions...")
        rules_text = self._format_rules(all_rules)
        logger.debug(f"Formatted rules text length: {len(rules_text)} characters")
        
        # Replace {{rules}} placeholder in base_instructions
        # Split rules_text into lines and insert them where {{rules}} appears
        if 'base_instructions' in instructions:
            new_instructions = []
            for line in instructions['base_instructions']:
                if '{{rules}}' in line:
                    # Replace the placeholder line with the formatted rules (split into lines)
                    rules_lines = rules_text.split('\n')
                    new_instructions.extend(rules_lines)
                    logger.debug(f"Replaced {{rules}} placeholder with {len(rules_lines)} lines")
                else:
                    new_instructions.append(line)
            instructions['base_instructions'] = new_instructions
        
        # Also store rules in the instructions dict for reference
        instructions['rules'] = all_rules
        logger.debug("Rules injection completed")
    
    def inject_schema_description_instructions(self, instructions: Dict[str, Any]) -> None:
        """
        Inject schema, description, and instructions template variables into base_instructions.
        - {{schema}} - extracted from knowledge graph template's _explanation section
        - {{description}} - from behavior instructions.json (description + goal)
        - {{instructions}} - from behavior-specific knowledge_graph instructions.json
        """
        # Get schema from injected knowledge graph template
        schema_text = instructions.get('schema', '')
        
        # Load behavior description and goal
        description_text = self._load_behavior_description()
        
        # Load behavior-specific instructions
        instructions_text = self._load_behavior_specific_instructions()
        
        # Replace template variables in base_instructions
        if 'base_instructions' in instructions:
            new_instructions = []
            for line in instructions['base_instructions']:
                if '{{schema}}' in line:
                    # Replace with schema text
                    new_line = line.replace('{{schema}}', schema_text if schema_text else 'story-graph.json structure')
                    new_instructions.append(new_line)
                elif '{{description}}' in line:
                    # Replace with description + goal
                    new_line = line.replace('{{description}}', description_text if description_text else 'Build knowledge graph')
                    new_instructions.append(new_line)
                elif '{{instructions}}' in line:
                    # Replace with behavior-specific instructions
                    if instructions_text:
                        # Split instructions into lines and insert them
                        instructions_lines = instructions_text.split('\n')
                        new_instructions.extend(instructions_lines)
                    else:
                        new_instructions.append(line.replace('{{instructions}}', 'Follow behavior-specific instructions'))
                else:
                    new_instructions.append(line)
            instructions['base_instructions'] = new_instructions
    
    def _extract_schema_from_template(self, template_content: Dict[str, Any]) -> str:
        """
        Extract schema description from template including _explanation and full template structure.
        
        Args:
            template_content: The loaded template JSON content
            
        Returns:
            Formatted schema description string with explanation and template JSON
        """
        schema_parts = []
        
        # First include the _explanation section
        explanation = template_content.get('_explanation', {})
        if explanation:
            schema_parts.append("**Schema Rules:**")
            for key, value in explanation.items():
                schema_parts.append(f"- **{key.replace('_', ' ').title()}**: {value}")
            schema_parts.append("")
        
        # Then include the full template structure as JSON
        schema_parts.append("**Template Structure (JSON Schema):**")
        schema_parts.append("```json")
        # Format the template as pretty JSON
        import json
        template_json = json.dumps(template_content, indent=2, ensure_ascii=False)
        schema_parts.append(template_json)
        schema_parts.append("```")
        
        return '\n'.join(schema_parts)
    
    def _load_behavior_description(self) -> str:
        """
        Load behavior description and goal from behavior instructions.json.
        
        Returns:
            Combined description + goal text
        """
        try:
            from agile_bot.bots.base_bot.src.bot.bot import Behavior
            behavior_folder = Behavior.find_behavior_folder(
                self.bot_directory,
                self.bot_name,
                self.behavior
            )
            
            # Load behavior-level instructions.json
            behavior_instructions_file = behavior_folder / 'instructions.json'
            if behavior_instructions_file.exists():
                behavior_data = read_json_file(behavior_instructions_file)
                description = behavior_data.get('description', '')
                goal = behavior_data.get('goal', '')
                
                parts = []
                if description:
                    parts.append(description)
                if goal:
                    parts.append(f"Goal: {goal}")
                
                return ' '.join(parts) if parts else ''
        except (FileNotFoundError, KeyError):
            pass
        
        return ''
    
    def _load_behavior_specific_instructions(self) -> str:
        """
        Load behavior-specific instructions from knowledge_graph/instructions.json.
        
        Returns:
            Combined instructions text
        """
        try:
            from agile_bot.bots.base_bot.src.bot.bot import Behavior
            behavior_folder = Behavior.find_behavior_folder(
                self.bot_directory,
                self.bot_name,
                self.behavior
            )
            
            # Find content/knowledge_graph folder (handles numbered prefixes)
            kg_dir = find_nested_subfolder(behavior_folder, 'content', 'knowledge_graph')
            if kg_dir:
                kg_instructions_file = kg_dir / 'instructions.json'
                if kg_instructions_file.exists():
                    kg_data = read_json_file(kg_instructions_file)
                    instructions_list = kg_data.get('instructions', [])
                    if instructions_list:
                        return '\n'.join(instructions_list)
        except (FileNotFoundError, KeyError):
            pass
        
        return ''
    
    def _format_rules(self, rules: list) -> str:
        """
        Format rules list into a readable text string for insertion into instructions.
        
        Args:
            rules: List of rule dictionaries with 'rule_file' and 'rule_content' keys
            
        Returns:
            Formatted string with all rules
        """
        if not rules:
            return "No validation rules found."
        
        formatted_sections = []
        
        # Separate bot-level and behavior-level rules
        bot_rules = []
        behavior_rules = []
        
        for rule in rules:
            rule_file = rule.get('rule_file', '')
            # Bot-level rules are in base_bot/rules or bot's own rules directory
            if 'base_bot/rules' in rule_file or (not 'behaviors' in rule_file and '/rules/' in rule_file):
                bot_rules.append(rule)
            else:
                behavior_rules.append(rule)
        
        # Format bot-level rules
        if bot_rules:
            formatted_sections.append("**Bot-level rules:**")
            for rule in bot_rules:
                rule_file = rule.get('rule_file', 'unknown')
                rule_content = rule.get('rule_content', {})
                
                # Extract rule description
                rule_description = rule_content.get('description', '')
                
                formatted_sections.append(f"\n**Rule:** {rule_file}")
                if rule_description:
                    formatted_sections.append(f"{rule_description}")
                
                # Format do/dont examples if present
                if 'do' in rule_content:
                    do_examples = rule_content.get('do', {}).get('examples', [])
                    if do_examples:
                        formatted_sections.append("\n**DO:**")
                        for example in do_examples:
                            desc = example.get('description', '')
                            content = example.get('content', '')
                            if isinstance(content, list):
                                content = '\n'.join(content)
                            if desc:
                                formatted_sections.append(f"- {desc}: {content}")
                            else:
                                formatted_sections.append(f"- {content}")
                
                if 'dont' in rule_content:
                    dont_examples = rule_content.get('dont', {}).get('examples', [])
                    if dont_examples:
                        formatted_sections.append("\n**DON'T:**")
                        for example in dont_examples:
                            desc = example.get('description', '')
                            content = example.get('content', '')
                            if isinstance(content, list):
                                content = '\n'.join(content)
                            if desc:
                                formatted_sections.append(f"- {desc}: {content}")
                            else:
                                formatted_sections.append(f"- {content}")
                
                # Handle examples array format (alternative structure)
                if 'examples' in rule_content:
                    examples = rule_content.get('examples', [])
                    for example in examples:
                        if 'do' in example:
                            do_content = example.get('do', {})
                            desc = do_content.get('description', '')
                            content = do_content.get('content', '')
                            if isinstance(content, list):
                                content = '\n'.join(content)
                            formatted_sections.append(f"\n**DO:** {desc}")
                            formatted_sections.append(content)
                        if 'dont' in example:
                            dont_content = example.get('dont', {})
                            desc = dont_content.get('description', '')
                            content = dont_content.get('content', '')
                            if isinstance(content, list):
                                content = '\n'.join(content)
                            formatted_sections.append(f"\n**DON'T:** {desc}")
                            formatted_sections.append(content)
                
                formatted_sections.append("")
        
        # Format behavior-level rules
        if behavior_rules:
            formatted_sections.append("**Behavior-level rules:**")
            for rule in behavior_rules:
                rule_file = rule.get('rule_file', 'unknown')
                rule_content = rule.get('rule_content', {})
                
                # Extract rule description
                rule_description = rule_content.get('description', '')
                
                formatted_sections.append(f"\n**Rule:** {rule_file}")
                if rule_description:
                    formatted_sections.append(f"{rule_description}")
                
                # Format do/dont examples if present
                if 'do' in rule_content:
                    do_examples = rule_content.get('do', {}).get('examples', [])
                    if do_examples:
                        formatted_sections.append("\n**DO:**")
                        for example in do_examples:
                            desc = example.get('description', '')
                            content = example.get('content', '')
                            if isinstance(content, list):
                                content = '\n'.join(content)
                            if desc:
                                formatted_sections.append(f"- {desc}: {content}")
                            else:
                                formatted_sections.append(f"- {content}")
                
                if 'dont' in rule_content:
                    dont_examples = rule_content.get('dont', {}).get('examples', [])
                    if dont_examples:
                        formatted_sections.append("\n**DON'T:**")
                        for example in dont_examples:
                            desc = example.get('description', '')
                            content = example.get('content', '')
                            if isinstance(content, list):
                                content = '\n'.join(content)
                            if desc:
                                formatted_sections.append(f"- {desc}: {content}")
                            else:
                                formatted_sections.append(f"- {content}")
                
                # Handle examples array format (alternative structure)
                if 'examples' in rule_content:
                    examples = rule_content.get('examples', [])
                    for example in examples:
                        if 'do' in example:
                            do_content = example.get('do', {})
                            desc = do_content.get('description', '')
                            content = do_content.get('content', '')
                            if isinstance(content, list):
                                content = '\n'.join(content)
                            formatted_sections.append(f"\n**DO:** {desc}")
                            formatted_sections.append(content)
                        if 'dont' in example:
                            dont_content = example.get('dont', {})
                            desc = dont_content.get('description', '')
                            content = dont_content.get('content', '')
                            if isinstance(content, list):
                                content = '\n'.join(content)
                            formatted_sections.append(f"\n**DON'T:** {desc}")
                            formatted_sections.append(content)
                
                formatted_sections.append("")
        
        if not formatted_sections:
            return "No validation rules found."
        
        return "\n".join(formatted_sections)
    
    def inject_validation_rules(self) -> Dict[str, Any]:
        """
        Load validation rules by delegating to ValidateRulesAction to avoid code duplication.
        Rules are injected into the LLM prompt so it can follow them during generation.
        """
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        
        # Create ValidateRulesAction instance to reuse its rule-loading logic
        validate_action = ValidateRulesAction(
            bot_name=self.bot_name,
            behavior=self.behavior,
            bot_directory=self.bot_directory
        )
        
        # Use existing method to load both common and behavior-specific rules
        rules_data = validate_action.inject_behavior_specific_and_bot_rules()
        
        # Return the validation_rules portion
        return rules_data.get('validation_rules', [])
    
    def _estimate_tokens(self, instructions: Dict[str, Any]) -> int:
        """
        Estimate token count for the full instructions payload.
        Uses rough approximation: word count * 1.3
        """
        total_chars = len(json.dumps(instructions, indent=2))
        # Approximate: 1 token ~= 4 characters for JSON
        estimated_tokens = total_chars // 4
        return estimated_tokens



