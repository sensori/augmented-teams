from pathlib import Path
from typing import List, Dict
import json
from datetime import datetime
from transitions import Machine
import logging

logger = logging.getLogger(__name__)


class Workflow:
    
    def __init__(self, bot_name: str, behavior: str, workspace_root: Path, 
                 states: List[str], transitions: List[Dict]):
        self.bot_name = bot_name
        self.behavior = behavior
        self.workspace_root = Path(workspace_root)
        self.states = states
        
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
    def dir(self) -> Path:
        """Get workflow's bot directory path."""
        return self.workspace_root / 'agile_bot' / 'bots' / self.bot_name
    
    @property
    def current_project_file(self) -> Path:
        """Get current_project.json file path."""
        return self.dir / 'current_project.json'
    
    @property
    def current_project(self) -> Path:
        """Get current project directory."""
        if self.current_project_file.exists():
            try:
                project_data = json.loads(self.current_project_file.read_text(encoding='utf-8'))
                return Path(project_data.get('current_project', ''))
            except Exception:
                pass
        return self.workspace_root
    
    @property
    def project_location(self) -> Path:
        """Get project location (same as current_project for clarity)."""
        return self.current_project
    
    @property
    def file(self) -> Path:
        """Get workflow state file path."""
        return self.project_location / 'workflow_state.json'
    
    @property
    def workflow_states(self) -> List[str]:
        """Get workflow states list (for backward compatibility)."""
        return self.states
    
    @property
    def current_state(self) -> str:
        """Get current state from state machine (self.state set by transitions library)."""
        return self.state
    
    def transition_to_next(self):
        try:
            self.proceed()  # Trigger transition
            self.save_state()
        except Exception as e:
            # Already at final state or invalid transition - this is expected at workflow end
            logger.debug(f'Transition failed (expected at workflow end): {e}')
    
    def load_state(self):
        # Workflow state is in {current_project}/project_area/workflow_state.json
        if self.file.exists():
            try:
                state_data = json.loads(self.file.read_text(encoding='utf-8'))
                current_behavior = state_data.get('current_behavior', '')
                completed_actions = state_data.get('completed_actions', [])
                
                # Check if this is the current behavior
                if current_behavior == f'{self.bot_name}.{self.behavior}':
                    # Determine next action from completed_actions (source of truth)
                    # NOT from current_action (which may be stale/corrupted)
                    next_action = self._determine_next_action_from_completed(completed_actions)
                    
                    if next_action and next_action in self.states:
                        self.machine.set_state(next_action)
            except Exception as e:
                logger.warning(f'Failed to load workflow state from {self.file}: {e}', exc_info=True)
    
    def _determine_next_action_from_completed(self, completed_actions: list) -> str:
        """
        Determine the next action to execute based on completed_actions.
        
        This is the SOURCE OF TRUTH for workflow state.
        We don't trust current_action from file - it may be stale/corrupted.
        
        Logic:
        1. If no completed actions → return first action in states
        2. Find last completed action for this behavior
        3. Look up what comes next in transitions
        4. Return that next action
        
        Args:
            completed_actions: List of completed action states
            
        Returns:
            Next action name, or first action if none completed
        """
        if not completed_actions:
            # No completed actions - start at beginning
            return self.states[0] if self.states else None
        
        # Find last completed action for this behavior
        last_completed = None
        for action_entry in reversed(completed_actions):
            action_state = action_entry.get('action_state', '')
            # Check if it's for this behavior
            if action_state.startswith(f'{self.bot_name}.{self.behavior}.'):
                # Extract action name: 'bot.behavior.action' -> 'action'
                action_name = action_state.split('.')[-1]
                if action_name in self.states:
                    last_completed = action_name
                    break
        
        if not last_completed:
            # No completed actions for this behavior - start at beginning
            return self.states[0] if self.states else None
        
        # Find what comes next after last_completed
        # Look through transitions to find where source=last_completed
        for transition in self.machine.get_triggers(last_completed):
            if transition == 'proceed':
                # Get the next state by simulating proceed
                current_index = self.states.index(last_completed)
                if current_index + 1 < len(self.states):
                    return self.states[current_index + 1]
        
        # If no transition found or at end, return last completed
        # (workflow will handle being at end)
        return last_completed
    
    def save_state(self):
        # Don't write if current_project not set
        if not self.current_project_file.exists():
            # Silently skip - project not initialized yet
            return
        
        # Workflow state is in {project_location}/workflow_state.json
        self.project_location.mkdir(parents=True, exist_ok=True)
        
        # Load existing state to preserve completed_actions
        existing_state = {}
        if self.file.exists():
            try:
                existing_state = json.loads(self.file.read_text(encoding='utf-8'))
            except Exception as e:
                logger.warning(f'Failed to load existing workflow state from {self.file}, starting fresh: {e}')
        
        # Update current state
        existing_state.update({
            'current_behavior': f'{self.bot_name}.{self.behavior}',
            'current_action': f'{self.bot_name}.{self.behavior}.{self.current_state}',
            'timestamp': datetime.now().isoformat()
        })
        
        self.file.write_text(json.dumps(existing_state), encoding='utf-8')
    
    def save_current_action(self):
        """Convenience method to save current action as complete."""
        self.save_completed_action(self.current_state)
    
    def save_completed_action(self, action_name: str):
        # Don't write if current_project not set
        if not self.current_project_file.exists():
            # Silently skip - project not initialized yet
            return
        
        # Workflow state is in {project_location}/workflow_state.json
        self.project_location.mkdir(parents=True, exist_ok=True)
        
        # Load existing state
        state_data = {}
        if self.file.exists():
            try:
                state_data = json.loads(self.file.read_text(encoding='utf-8'))
            except Exception as e:
                logger.warning(f'Failed to load workflow state for save_completed_action from {self.file}, starting fresh: {e}')
        
        # Add completed action
        if 'completed_actions' not in state_data:
            state_data['completed_actions'] = []
        
        state_data['completed_actions'].append({
            'action_state': f'{self.bot_name}.{self.behavior}.{action_name}',
            'timestamp': datetime.now().isoformat()
        })
        
        self.file.write_text(json.dumps(state_data), encoding='utf-8')
    
    def is_action_completed(self, action_name: str) -> bool:
        """Check if an action has been marked as completed."""
        if not self.file.exists():
            return False
        
        try:
            state_data = json.loads(self.file.read_text(encoding='utf-8'))
            completed_actions = state_data.get('completed_actions', [])
            
            # Check if this action is in completed_actions for this behavior
            action_state = f'{self.bot_name}.{self.behavior}.{action_name}'
            return any(
                action.get('action_state') == action_state
                for action in completed_actions
            )
        except Exception as e:
            logger.warning(f'Failed to check if action {action_name} is completed: {e}')
            return False
    
    def is_terminal_action(self, action_name: str) -> bool:
        return action_name == 'validate_rules'
    
    @staticmethod
    def is_behavior_complete(behavior: str, workflow_state_file: Path) -> bool:
        if not workflow_state_file.exists():
            return False
        
        state = json.loads(workflow_state_file.read_text(encoding='utf-8'))
        completed = state.get('completed_actions', [])
        
        # Check if validate_rules is in completed actions for this behavior
        return any(
            f'.{behavior}.validate_rules' in action['action_state']
            for action in completed
        )

