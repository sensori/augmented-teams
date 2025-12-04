from pathlib import Path
import json


class Router:
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
    
    def determine_next_action_from_state(self, state_file: Path) -> str:
        if not state_file.exists():
            return 'gather_context'
        
        state = json.loads(state_file.read_text(encoding='utf-8'))
        completed = state.get('completed_actions', [])
        
        if not completed:
            return 'gather_context'
        
        # Get last completed action
        last_action = completed[-1]['action_state'].split('.')[-1]
        
        # Map to next action
        action_map = {
            'gather_context': 'decide_planning_criteria',
            'decide_planning_criteria': 'build_knowledge',
            'build_knowledge': 'render_output',
            'render_output': 'validate_rules',
            'validate_rules': None
        }
        
        return action_map.get(last_action, 'gather_context')

