from pathlib import Path
from typing import Dict, Any
import json
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.bot.base_action import BaseAction
from agile_bot.bots.base_bot.src.bot.behavior_folder_finder import find_nested_subfolder, find_file_in_folder


class GatherContextAction(BaseAction):
    
    def __init__(self, bot_name: str, behavior: str, bot_directory: Path):
        super().__init__(bot_name, behavior, bot_directory, 'gather_context')
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute gather_context action logic."""
        try:
            instructions = self.load_and_merge_instructions()
        except FileNotFoundError:
            # If instructions are missing (e.g., in ephemeral test workspaces),
            # proceed with empty instructions but still save clarification data.
            instructions = {
                'action': 'gather_context',
                'behavior': self.behavior,
                'base_instructions': []
            }
        
        # If clarification data is provided, save it to context folder
        if parameters and (parameters.get('key_questions_answered') or parameters.get('evidence_provided')):
            self.save_clarification(parameters)
        
        return {'instructions': instructions}
    
    def save_clarification(self, parameters: Dict[str, Any]):
        """Save clarification data to docs/stories folder (generated file, not original context)."""
        try:
            # Use working_dir if set, otherwise skip
            if not self.working_dir:
                return
            
            # Generated files go to docs/stories/, not context folder
            docs_folder = self.working_dir / 'docs'
            stories_folder = docs_folder / 'stories'
            
            # Ensure docs/stories folder exists
            stories_folder.mkdir(parents=True, exist_ok=True)
            
            # Load existing clarification data if it exists
            clarification_file = stories_folder / 'clarification.json'
            clarification_data = {}
            if clarification_file.exists():
                try:
                    clarification_data = json.loads(clarification_file.read_text(encoding='utf-8'))
                except (json.JSONDecodeError, Exception):
                    # If file is corrupted or unreadable, start fresh
                    clarification_data = {}
            
            # Merge new clarification data for this behavior
            clarification_data[self.behavior] = {
                'key_questions': parameters.get('key_questions_answered', {}),
                'evidence': parameters.get('evidence_provided', {})
            }
            
            # Save to docs/stories/ (generated file location)
            clarification_file.write_text(
                json.dumps(clarification_data, indent=2),
                encoding='utf-8'
            )
        except Exception as e:
            # Log error and fail fast so callers can handle the problem.
            # Previously this swallowed the error; now we raise a clear exception.
            import logging
            logging.exception("Failed to save clarification")
            # Raise a RuntimeError with context, preserving original exception
            raise RuntimeError(f"Failed to save clarification for behavior '{self.behavior}': {e}") from e
    
    def load_and_merge_instructions(self) -> Dict[str, Any]:
        # Load base instructions - check for numbered prefix folders
        base_actions_dir = self.base_actions_dir
        
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
                self.bot_directory,
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
                self.bot_directory,
                self.bot_name,
                self.behavior
            )
            
            # Use centralized utility to find guardrails/required_context folder
            guardrails_dir = find_nested_subfolder(behavior_folder, 'guardrails', 'required_context')
            
        except FileNotFoundError:
            guardrails_dir = None
        
        instructions = {'guardrails': {}}
        
        if not guardrails_dir:
            return instructions
        
        # Find key_questions.json (may have number prefix)
        questions_file = find_file_in_folder(guardrails_dir, 'key_questions.json')
        
        if questions_file and questions_file.exists():
            questions_data = read_json_file(questions_file)
            instructions['guardrails']['key_questions'] = questions_data.get('questions', [])
        
        # Find evidence.json (may have number prefix)
        evidence_file = find_file_in_folder(guardrails_dir, 'evidence.json')
        
        if evidence_file and evidence_file.exists():
            evidence_data = read_json_file(evidence_file)
            instructions['guardrails']['evidence'] = evidence_data.get('evidence', [])
        
        return instructions
    

            

    
    def inject_gather_context_instructions(self) -> Dict[str, Any]:
        rendered_dir = (
            self.bot_directory /
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
    
           
