"""
Workflow

Manages behavior workflow execution using transitions state machine.
Handles state persistence, transitions, and workflow state management.
"""
from pathlib import Path
from typing import List, Dict
import json
from datetime import datetime
from transitions import Machine


class Workflow:
    """Workflow manager for behavior execution with state machine."""
    
    def __init__(self, bot_name: str, behavior: str, workspace_root: Path, 
                 states: List[str], transitions: List[Dict]):
        """Initialize workflow with state machine.
        
        Args:
            bot_name: Name of the bot
            behavior: Name of the behavior
            workspace_root: Root workspace directory
            states: List of workflow states (action names)
            transitions: List of transition definitions
        """
        self.bot_name = bot_name
        self.behavior = behavior
        self.workspace_root = Path(workspace_root)
        self.workflow_states = states
        
        # Initialize state machine
        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial=states[0] if states else 'gather_context',
            auto_transitions=False
        )
        
        # Load saved state if exists
        self.load_state()
    
    @property
    def current_state(self) -> str:
        """Get current state from state machine."""
        return self.state
    
    def transition_to_next(self):
        """Transition to next state in workflow."""
        try:
            self.proceed()  # Trigger transition
            self.save_state()
        except Exception:
            # Already at final state or invalid transition
            pass
    
    def load_state(self):
        """Load workflow state from file - sets state machine to correct state."""
        state_file = self.workspace_root / 'project_area' / 'workflow_state.json'
        
        if state_file.exists():
            try:
                state_data = json.loads(state_file.read_text(encoding='utf-8'))
                current_behavior = state_data.get('current_behavior', '')
                current_action = state_data.get('current_action', '')
                
                # Check if this is the current behavior
                if current_behavior == f'{self.bot_name}.{self.behavior}':
                    # Extract action name from 'bot_name.behavior.action_name'
                    action_name = current_action.split('.')[-1]
                    if action_name in self.workflow_states:
                        self.state = action_name
            except Exception:
                pass
    
    def save_state(self):
        """Save current workflow state to file."""
        state_dir = self.workspace_root / 'project_area'
        state_dir.mkdir(parents=True, exist_ok=True)
        state_file = state_dir / 'workflow_state.json'
        
        state_file.write_text(json.dumps({
            'current_behavior': f'{self.bot_name}.{self.behavior}',
            'current_action': f'{self.bot_name}.{self.behavior}.{self.state}',
            'timestamp': datetime.now().isoformat()
        }), encoding='utf-8')
    
    def is_terminal_action(self, action_name: str) -> bool:
        """Check if action is terminal (last) action."""
        return action_name == 'validate_rules'
    
    @staticmethod
    def is_behavior_complete(behavior: str, state_file: Path) -> bool:
        """Check if behavior workflow is complete (static utility method)."""
        if not state_file.exists():
            return False
        
        state = json.loads(state_file.read_text(encoding='utf-8'))
        completed = state.get('completed_actions', [])
        
        # Check if validate_rules is in completed actions for this behavior
        return any(
            f'.{behavior}.validate_rules' in action['action_state']
            for action in completed
        )

