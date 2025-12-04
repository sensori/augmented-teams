from pathlib import Path
from typing import Dict, Any
import json
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.bot.base_action import BaseAction


class GatherContextAction(BaseAction):
    
    def __init__(self, bot_name: str, behavior: str, workspace_root: Path):
        super().__init__(bot_name, behavior, workspace_root, 'gather_context')
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute gather_context action logic."""
        instructions = self.load_and_merge_instructions()
        return {'instructions': instructions}
    
    def load_and_merge_instructions(self) -> Dict[str, Any]:
        # Load base instructions - check for numbered prefix folders
        base_actions_dir = self.workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
        
        # Try with and without number prefix - prefer numbered folders
        base_path = None
        matching_folders = sorted(base_actions_dir.glob('*gather_context'))
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
            base_path = base_actions_dir / 'gather_context' / 'instructions.json'
        
        if not base_path.exists():
            raise FileNotFoundError(
                f'Base instructions not found for action gather_context at {base_path}'
            )
        
        base_instructions = read_json_file(base_path)
        
        # Load behavior-specific instructions (optional)
        behavior_path = None
        try:
            from agile_bot.bots.base_bot.src.bot.bot import Behavior
            behavior_folder = Behavior.find_behavior_folder(
                self.workspace_root,
                self.bot_name,
                self.behavior
            )
            behavior_path = behavior_folder / 'gather_context' / 'instructions.json'
        except FileNotFoundError:
            pass
        
        behavior_instructions = None
        if behavior_path and behavior_path.exists():
            behavior_instructions = read_json_file(behavior_path)
        
        # Merge instructions
        merged = {
            'action': 'gather_context',
            'behavior': self.behavior,
            'base_instructions': base_instructions.get('instructions', []),
        }
        
        if behavior_instructions:
            merged['behavior_instructions'] = behavior_instructions.get('instructions', [])
        
        # Inject guardrails (key_questions and evidence) from behavior folder
        guardrails = self.inject_questions_and_evidence()
        if guardrails and guardrails.get('guardrails'):
            merged['guardrails'] = guardrails['guardrails']
        
        return merged
    
    def inject_questions_and_evidence(self) -> Dict[str, Any]:
        # Find behavior folder (handles numbered prefixes)
        try:
            from agile_bot.bots.base_bot.src.bot.bot import Behavior
            behavior_folder = Behavior.find_behavior_folder(
                self.workspace_root,
                self.bot_name,
                self.behavior
            )
            
            # Find guardrails folder (may have number prefix like 1_guardrails)
            guardrails_folder = None
            for folder in behavior_folder.glob('*guardrails'):
                if folder.is_dir():
                    guardrails_folder = folder
                    break
            
            if not guardrails_folder:
                return {'guardrails': {}}
            
            # Find required_context folder (may have number prefix like 1_required_context)
            guardrails_dir = None
            for folder in guardrails_folder.glob('*required_context'):
                if folder.is_dir():
                    guardrails_dir = folder
                    break
            
        except FileNotFoundError:
            guardrails_dir = None
        
        instructions = {'guardrails': {}}
        
        if not guardrails_dir:
            return instructions
        
        # Load questions (may have number prefix like 1_key_questions.json or just key_questions.json)
        questions_file = None
        for file in guardrails_dir.glob('*key_questions.json'):
            if file.is_file():
                questions_file = file
                break
        
        if questions_file and questions_file.exists():
            questions_data = read_json_file(questions_file)
            instructions['guardrails']['key_questions'] = questions_data.get('questions', [])
        
        # Load evidence (may have number prefix like 1_evidence.json or just evidence.json)
        evidence_file = None
        for file in guardrails_dir.glob('*evidence.json'):
            if file.is_file():
                evidence_file = file
                break
        
        if evidence_file and evidence_file.exists():
            evidence_data = read_json_file(evidence_file)
            instructions['guardrails']['evidence'] = evidence_data.get('evidence', [])
        
        return instructions
    
    def inject_gather_context_instructions(self) -> Dict[str, Any]:
        rendered_dir = (
            self.workspace_root /
            'agile_bot' / 'bots' / self.bot_name / 'docs' / 'stories'
        )
        
        rendered_paths = []
        if rendered_dir.exists():
            # Look for acceptance criteria files
            for file_path in rendered_dir.rglob('acceptance-criteria.md'):
                rendered_paths.append(str(file_path))
        
        return {
            'rendered_content_paths': rendered_paths
        }


