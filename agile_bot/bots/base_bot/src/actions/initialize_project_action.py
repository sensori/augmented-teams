"""
Initialize Project Action

Handles initialize_project action including:
- Project location confirmation
- Activity tracking
- Workflow state initialization
"""
from pathlib import Path
import json
from typing import Dict, Any
from agile_bot.bots.base_bot.src.actions.activity_tracker import ActivityTracker


class InitializeProjectAction:
    """Initialize Project action implementation."""
    
    def __init__(self, bot_name: str, behavior: str, workspace_root: Path):
        self.bot_name = bot_name
        self.behavior = behavior
        self.workspace_root = Path(workspace_root)
        self.tracker = ActivityTracker(workspace_root)
    
    def initialize_location(self, project_area: str = None) -> Dict[str, Any]:
        """Initialize and confirm project location for workflow state persistence.
        
        Args:
            project_area: Optional project area path (relative or absolute)
            
        Returns:
            Dictionary with location info and confirmation requirement
        """
        # Determine current location from project_area or default to workspace_root
        if project_area:
            if not Path(project_area).is_absolute():
                current_location = self.workspace_root / project_area
            else:
                current_location = Path(project_area)
        else:
            current_location = self.workspace_root
        
        # Check for saved location
        location_file = self.workspace_root / 'project_area' / 'project_location.json'
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
            location_file.parent.mkdir(parents=True, exist_ok=True)
            location_file.write_text(
                json.dumps({'project_location': str(current_location)}),
                encoding='utf-8'
            )
        
        return data
    
    def track_activity_on_start(self):
        """Track activity when action starts."""
        self.tracker.track_start(self.bot_name, self.behavior, 'initialize_project')
    
    def track_activity_on_completion(self, outputs: dict = None, duration: int = None):
        """Track activity when action completes."""
        self.tracker.track_completion(self.bot_name, self.behavior, 'initialize_project', outputs, duration)
    
    def save_state_on_completion(self):
        """Save workflow state on completion."""
        state_file = self.workspace_root / 'project_area' / 'workflow_state.json'
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state = json.loads(state_file.read_text(encoding='utf-8')) if state_file.exists() else {}
        
        if 'completed_actions' not in state:
            state['completed_actions'] = []
        
        state['completed_actions'].append({
            'action_state': f'{self.bot_name}.{self.behavior}.initialize_project',
            'timestamp': '2025-12-04T10:00:00Z'
        })
        
        state_file.write_text(json.dumps(state), encoding='utf-8')
    
    def finalize_and_transition(self):
        """Finalize action and return next action."""
        class TransitionResult:
            next_action = 'gather_context'
        return TransitionResult()

