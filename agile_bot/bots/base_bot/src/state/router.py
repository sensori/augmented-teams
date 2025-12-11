from pathlib import Path
import json


class Router:
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
    
    def determine_next_action_from_state(self, state_file: Path) -> str:
        if not state_file.exists():
            raise FileNotFoundError(
                f"Workflow state file not found at {state_file}. "
                f"Cannot determine next action without workflow state. "
                f"This indicates workflow has not been initialized."
            )
        
        state = json.loads(state_file.read_text(encoding='utf-8'))
        completed = state.get('completed_actions', [])
        
        if not completed:
            raise ValueError(
                f"Workflow state file exists but has no completed actions. "
                f"Cannot determine next action. "
                f"State file: {state_file}"
            )
        
        # Get last completed action
        last_action = completed[-1]['action_state'].split('.')[-1]
        
        # Map to next action
        action_map = {
            'gather_context': 'decide_planning_criteria',
            'decide_planning_criteria': 'build_knowledge',
            'build_knowledge': 'validate_rules',
            'validate_rules': 'render_output',
            'render_output': None
        }
        
        next_action = action_map.get(last_action)
        if next_action is None and last_action not in action_map:
            raise ValueError(
                f"Unknown last action '{last_action}' in workflow state. "
                f"Cannot determine next action. "
                f"Known actions: {', '.join(action_map.keys())}"
            )
        
        return next_action

