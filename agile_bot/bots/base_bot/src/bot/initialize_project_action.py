from pathlib import Path
import json
from typing import Dict, Any
from agile_bot.bots.base_bot.src.bot.base_action import BaseAction


class InitializeProjectAction(BaseAction):
    
    def __init__(self, bot_name: str, behavior: str, workspace_root: Path):
        super().__init__(bot_name, behavior, workspace_root, 'initialize_project')
    
    @property
    def dir(self) -> Path:
        """Get action's bot directory path."""
        return self.workspace_root / 'agile_bot' / 'bots' / self.bot_name
    
    @property
    def current_project_file(self) -> Path:
        """Get current_project.json file path."""
        return self.dir / 'current_project.json'
    
    def initialize_location(self, project_area: str = None) -> Dict[str, Any]:
        # Determine current directory (project being worked on)
        if project_area:
            if not Path(project_area).is_absolute():
                current_dir = self.workspace_root / project_area
            else:
                current_dir = Path(project_area)
        else:
            # No explicit parameter - use current working directory
            current_dir = Path.cwd()
        
        # Check for saved current_project in bot root
        saved_project = None
        
        if self.current_project_file.exists():
            try:
                project_data = json.loads(self.current_project_file.read_text(encoding='utf-8'))
                saved_project = Path(project_data.get('current_project', ''))
            except Exception:
                pass
        
        # Determine action based on saved_project vs current_dir
        data = {}
        
        if not saved_project:
            # First time - need confirmation (even if project_area provided)
            data = {
                'proposed_location': str(current_dir),
                'requires_confirmation': True,
                'message': f'Project location will be: {current_dir}. Confirm?'
            }
        elif saved_project == current_dir:
            # Same location - skip init, just resume
            data = {
                'project_location': str(current_dir),
                'requires_confirmation': False,
                'message': f'Resuming in {current_dir}'
            }
        else:
            # Location changed - ask if user wants to switch
            data = {
                'saved_location': str(saved_project),
                'current_location': str(current_dir),
                'requires_confirmation': True,
                'message': f'Current project: {saved_project}. Current directory: {current_dir}. Switch to current directory?'
            }
        
        # Save if no confirmation needed (resuming case)
        if not data.get('requires_confirmation'):
            self.current_project_file.parent.mkdir(parents=True, exist_ok=True)
            self.current_project_file.write_text(
                json.dumps({'current_project': str(current_dir)}),
                encoding='utf-8'
            )
            # Also create context folder inside docs when resuming (no confirmation needed)
            docs_folder = current_dir / 'docs'
            docs_folder.mkdir(parents=True, exist_ok=True)
            context_folder = docs_folder / 'context'
            context_folder.mkdir(parents=True, exist_ok=True)
            stories_folder = docs_folder / 'stories'
            stories_folder.mkdir(parents=True, exist_ok=True)
        
        return data
    
    def confirm_location(self, project_location: str, input_file: str = None) -> Dict[str, Any]:
        # Parse location
        if not Path(project_location).is_absolute():
            location = self.workspace_root / project_location
        else:
            location = Path(project_location)
        
        # Save to bot root as current_project.json
        self.current_project_file.parent.mkdir(parents=True, exist_ok=True)
        self.current_project_file.write_text(
            json.dumps({'current_project': str(location)}),
            encoding='utf-8'
        )
        
        # MANDATORY: Create context folder inside docs folder immediately after project confirmation
        docs_folder = location / 'docs'
        docs_folder.mkdir(parents=True, exist_ok=True)
        context_folder = docs_folder / 'context'
        context_folder.mkdir(parents=True, exist_ok=True)
        
        # Also ensure docs/stories folder exists for generated files
        stories_folder = docs_folder / 'stories'
        stories_folder.mkdir(parents=True, exist_ok=True)
        
        # If input file provided, copy it to context folder
        if input_file:
            input_path = Path(input_file)
            if input_path.exists():
                context_input = context_folder / 'input.txt'
                # Copy file (don't move - preserve original)
                import shutil
                shutil.copy2(input_path, context_input)
        
        return {
            'project_location': str(location),
            'saved': True,
            'context_folder_created': True,
            'message': f'Project location saved: {location}'
        }

        docs_folder = location / 'docs'
        docs_folder.mkdir(parents=True, exist_ok=True)
        context_folder = docs_folder / 'context'
        context_folder.mkdir(parents=True, exist_ok=True)
        
        # Also ensure docs/stories folder exists for generated files
        stories_folder = docs_folder / 'stories'
        stories_folder.mkdir(parents=True, exist_ok=True)
        
        # If input file provided, copy it to context folder
        if input_file:
            input_path = Path(input_file)
            if input_path.exists():
                context_input = context_folder / 'input.txt'
                # Copy file (don't move - preserve original)
                import shutil
                shutil.copy2(input_path, context_input)
        
        return {
            'project_location': str(location),
            'saved': True,
            'context_folder_created': True,
            'message': f'Project location saved: {location}'
        }

        docs_folder = location / 'docs'
        docs_folder.mkdir(parents=True, exist_ok=True)
        context_folder = docs_folder / 'context'
        context_folder.mkdir(parents=True, exist_ok=True)
        
        # Also ensure docs/stories folder exists for generated files
        stories_folder = docs_folder / 'stories'
        stories_folder.mkdir(parents=True, exist_ok=True)
        
        # If input file provided, copy it to context folder
        if input_file:
            input_path = Path(input_file)
            if input_path.exists():
                context_input = context_folder / 'input.txt'
                # Copy file (don't move - preserve original)
                import shutil
                shutil.copy2(input_path, context_input)
        
        return {
            'project_location': str(location),
            'saved': True,
            'context_folder_created': True,
            'message': f'Project location saved: {location}'
        }
