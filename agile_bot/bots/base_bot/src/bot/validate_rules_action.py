from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.bot.base_action import BaseAction


class ValidateRulesAction(BaseAction):
    
    def __init__(self, bot_name: str, behavior: str, workspace_root: Path):
        super().__init__(bot_name, behavior, workspace_root, 'validate_rules')
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validate_rules action logic."""
        rules_data = self.inject_behavior_specific_and_bot_rules()
        action_instructions = rules_data.get('action_instructions', [])
        validation_rules = rules_data.get('validation_rules', [])
        
        # Format instructions properly - action_instructions are primary, rules are context
        instructions = {
            'action': 'validate_rules',
            'behavior': self.behavior,
            'base_instructions': action_instructions,  # Primary instructions from instructions.json
            'validation_rules': validation_rules,  # Rules to validate against (supporting context)
            'content_to_validate': self._identify_content_to_validate()
        }
        
        return {'instructions': instructions}
    
    def inject_common_bot_rules(self) -> Dict[str, Any]:
        # Try both potential paths for common rules
        rules_file = (
            self.workspace_root /
            'agile_bot' / 'bots' / 'base_bot' / 'rules' / 'common_rules.json'
        )
        if not rules_file.exists():
            rules_file = (
                self.workspace_root /
                'base_bot' / 'rules' / 'common_rules.json'
            )
        
        if not rules_file.exists():
            raise FileNotFoundError(
                f'Common bot rules not found at {rules_file}'
            )
        
        rules_data = read_json_file(rules_file)
        
        return {
            'validation_rules': rules_data.get('rules', [])
        }
    
    def inject_behavior_specific_and_bot_rules(self) -> Dict[str, Any]:
        # Load action-specific instructions from base_actions
        action_instructions = []
        base_actions_path = self.workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
        
        # Find the validate_rules action folder (may have number prefix)
        action_folder = None
        if base_actions_path.exists():
            for folder in base_actions_path.iterdir():
                if folder.is_dir() and 'validate_rules' in folder.name:
                    action_folder = folder
                    break
        
        if action_folder:
            instructions_file = action_folder / 'instructions.json'
            if instructions_file.exists():
                instructions_data = read_json_file(instructions_file)
                action_instructions = instructions_data.get('instructions', [])
        
        # Load common rules - try both paths
        common_rules = []
        common_file = (
            self.workspace_root /
            'agile_bot' / 'bots' / 'base_bot' / 'rules' / 'common_rules.json'
        )
        if not common_file.exists():
            common_file = (
                self.workspace_root /
                'base_bot' / 'rules' / 'common_rules.json'
            )
        
        if common_file.exists():
            common_data = read_json_file(common_file)
            common_rules = common_data.get('rules', [])
        
        # Load behavior-specific rules
        behavior_rules = []
        
        # Find behavior folder (handles numbered prefixes)
        try:
            from agile_bot.bots.base_bot.src.bot.bot import Behavior
            behavior_folder = Behavior.find_behavior_folder(
                self.workspace_root,
                self.bot_name,
                self.behavior
            )
            # Try multiple rule folder locations (numbered or not)
            behavior_rules_dir = None
            for rules_folder_name in ['3_rules', 'rules']:
                candidate = behavior_folder / rules_folder_name
                if candidate.exists():
                    behavior_rules_dir = candidate
                    break
        except FileNotFoundError:
            behavior_rules_dir = None
        
        # Check for single validation_rules.json file
        if behavior_rules_dir and behavior_rules_dir.exists():
            behavior_file = behavior_rules_dir / 'validation_rules.json'
            if behavior_file.exists():
                behavior_data = read_json_file(behavior_file)
                behavior_rules = behavior_data.get('rules', [])
            # Otherwise load all .json files from rules directory
            elif behavior_rules_dir.is_dir():
                for rule_file in behavior_rules_dir.glob('*.json'):
                    rule_data = read_json_file(rule_file)
                    # Add the rule file content with filename as identifier
                    behavior_rules.append({
                        'rule_file': rule_file.name,
                        'rule_content': rule_data
                    })
        
        # Merge rules
        all_rules = common_rules + behavior_rules
        
        return {
            'action_instructions': action_instructions,
            'validation_rules': all_rules
        }
    
    def inject_next_action_instructions(self):
        return ""  # Empty string for terminal action
    
    def _identify_content_to_validate(self) -> Dict[str, Any]:
        """Identify what content needs to be validated from the project."""
        project_dir = self.current_project
        content_info = {
            'project_location': str(project_dir),
            'rendered_outputs': [],
            'clarification_file': None,
            'planning_file': None,
            'report_path': None
        }
        
        # Find docs_path from behavior config or default
        try:
            from agile_bot.bots.base_bot.src.bot.bot import Behavior
            behavior_folder = Behavior.find_behavior_folder(
                self.workspace_root,
                self.bot_name,
                self.behavior
            )
            # Try to find config that specifies docs_path
            config_file = behavior_folder / 'instructions.json'
            if config_file.exists():
                config_data = read_json_file(config_file)
                docs_path = config_data.get('docs_path', 'docs/stories')
            else:
                docs_path = 'docs/stories'
        except FileNotFoundError:
            docs_path = 'docs/stories'
        
        docs_dir = project_dir / docs_path
        
        # Find clarification.json and planning.json
        clarification_file = docs_dir / 'clarification.json'
        planning_file = docs_dir / 'planning.json'
        
        if clarification_file.exists():
            content_info['clarification_file'] = str(clarification_file)
        if planning_file.exists():
            content_info['planning_file'] = str(planning_file)
        
        # Set validation report path (where AI should save the report)
        report_file = docs_dir / 'validation-report.md'
        content_info['report_path'] = str(report_file)
        
        # Find rendered outputs (story maps, domain models, etc.)
        if docs_dir.exists():
            # Look for common rendered output files
            rendered_patterns = [
                '*-story-map.md',
                '*-domain-model-description.md',
                '*-domain-model-diagram.md',
                'story-graph.json',
                '*-increments.md'
            ]
            for pattern in rendered_patterns:
                for file_path in docs_dir.glob(pattern):
                    content_info['rendered_outputs'].append(str(file_path))
        
        return content_info


