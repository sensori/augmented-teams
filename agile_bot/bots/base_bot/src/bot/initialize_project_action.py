from pathlib import Path
import json
from typing import Dict, Any
from agile_bot.bots.base_bot.src.bot.base_action import BaseAction


class InitializeProjectAction(BaseAction):
    
    def __init__(self, bot_name: str, behavior: str, workspace_root: Path):
        super().__init__(bot_name, behavior, workspace_root, 'initialize_project')
    
    def initialize_location(self, project_area: str = None) -> Dict[str, Any]:
        # Determine current location from project_area or default to bot directory
        if project_area:
            if not Path(project_area).is_absolute():
                current_location = self.workspace_root / project_area
            else:
                current_location = Path(project_area)
        else:
            # Default to bot directory (agile_bot/bots/{bot_name})
            current_location = self.workspace_root / 'agile_bot' / 'bots' / self.bot_name
        
        # Check for saved location at bot directory
        bot_dir = self.workspace_root / 'agile_bot' / 'bots' / self.bot_name
        location_file = bot_dir / 'project_area' / 'project_location.json'
        saved_location = None
        
        if location_file.exists():
            try:
                location_data = json.loads(location_file.read_text(encoding='utf-8'))
                saved_location = Path(location_data.get('project_location', ''))
            except Exception:
                pass
        
        # Determine if confirmation needed
        requires_confirmation = False
        data = {}
        
        if not saved_location:
            # First time - need confirmation
            requires_confirmation = True
            data = {
                'proposed_location': str(current_location),
                'requires_confirmation': True,
                'message': f'Project location will be: {current_location}. Confirm?'
            }
        elif saved_location != current_location:
            # Location changed - need confirmation
            requires_confirmation = True
            data = {
                'saved_location': str(saved_location),
                'current_location': str(current_location),
                'requires_confirmation': True,
                'message': f'Saved location: {saved_location}. Current: {current_location}. Switch to new location?'
            }
        else:
            # Same location - skip confirmation
            data = {
                'project_location': str(current_location),
                'requires_confirmation': False
            }
        
        # Save location if confirmed (in real usage, this would be called after user confirms)
        if not requires_confirmation:
            bot_dir = self.workspace_root / 'agile_bot' / 'bots' / self.bot_name
            save_location_file = bot_dir / 'project_area' / 'project_location.json'
            save_location_file.parent.mkdir(parents=True, exist_ok=True)
            save_location_file.write_text(
                json.dumps({'project_location': str(current_location)}),
                encoding='utf-8'
            )
        
        return data
    
    def confirm_location(self, project_location: str) -> Dict[str, Any]:
        # Parse location
        if not Path(project_location).is_absolute():
            location = self.workspace_root / project_location
        else:
            location = Path(project_location)
        
        # Save location to bot's project_area
        bot_dir = self.workspace_root / 'agile_bot' / 'bots' / self.bot_name
        location_file = bot_dir / 'project_area' / 'project_location.json'
        location_file.parent.mkdir(parents=True, exist_ok=True)
        location_file.write_text(
            json.dumps({'project_location': str(location)}),
            encoding='utf-8'
        )
        
        return {
            'project_location': str(location),
            'saved': True,
            'message': f'Project location saved: {location}'
        }


