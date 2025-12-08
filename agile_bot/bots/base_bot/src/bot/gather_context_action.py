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
        
        # If clarification data is provided, save it to context folder
        if parameters and (parameters.get('key_questions_answered') or parameters.get('evidence_provided')):
            self.save_clarification(parameters)
        
        return {'instructions': instructions}
    
    def save_clarification(self, parameters: Dict[str, Any]):
        """Save clarification data to docs/stories folder (generated file, not original context)."""
        try:
            # Get project area from current_project.json
            project_area = self.current_project
            
            # If current_project returns workspace_root (fallback), 
            # we need to get the actual project from current_project.json
            if project_area == self.workspace_root and self.current_project_file.exists():
                try:
                    project_data = json.loads(self.current_project_file.read_text(encoding='utf-8'))
                    project_path = project_data.get('current_project', '')
                    if project_path:
                        project_area = Path(project_path)
                except Exception as e:
                    # If we can't read the file, use workspace_root as fallback
                    pass
            
            # Generated files go to docs/stories/, not context folder
            docs_folder = project_area / 'docs'
            stories_folder = docs_folder / 'stories'
            
            # Ensure docs/stories folder exists
            stories_folder.mkdir(parents=True, exist_ok=True)
            
            # Build clarification data structure
            clarification_data = {
                self.behavior: {
                    'key_questions': parameters.get('key_questions_answered', {}),
                    'evidence': parameters.get('evidence_provided', {})
                }
            }
            
            # Save to docs/stories/ (generated file location)
            clarification_file = stories_folder / 'clarification.json'
            clarification_file.write_text(
                json.dumps(clarification_data, indent=2),
                encoding='utf-8'
            )
        except Exception as e:
            # Log error but don't fail - this allows the action to continue
            # In production, this would be logged properly
            import logging
            logging.warning(f"Failed to save clarification: {e}")
            raise
    
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
