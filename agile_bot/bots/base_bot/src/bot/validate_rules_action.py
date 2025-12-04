from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.bot.base_action import BaseAction


class ValidateRulesAction(BaseAction):
    
    def __init__(self, bot_name: str, behavior: str, workspace_root: Path):
        super().__init__(bot_name, behavior, workspace_root, 'validate_rules')
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validate_rules action logic."""
        instructions = self.inject_behavior_specific_and_bot_rules()
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


