from pathlib import Path
from typing import List, Dict
import json
from datetime import datetime
from transitions import Machine
import logging

from agile_bot.bots.base_bot.src.state.workspace import get_workspace_directory

logger = logging.getLogger(__name__)


class Workflow:
    
    def __init__(self, bot_name: str, behavior: str, bot_directory: Path,
                 states: List[str], transitions: List[Dict], bot_instance=None):
        """Initialize Workflow.
        
        Args:
            bot_name: Name of the bot
            behavior: Name of the behavior
            bot_directory: Directory where bot code lives
            states: List of workflow states
            transitions: List of workflow transitions
            bot_instance: Reference to parent Bot instance
            
        Note:
            workspace_directory is auto-detected from get_workspace_directory()
        """
        self.bot_name = bot_name
        self.behavior = behavior
        self.bot_directory = Path(bot_directory)
        self.states = states
        self.transitions = transitions  # Store transitions for lookup
        self.bot = bot_instance  # Reference to parent Bot instance
        
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
    def workspace_directory(self) -> Path:
        """Get workspace directory (auto-detected from environment/agent.json)."""
        return get_workspace_directory()
    
    @property
    def dir(self) -> Path:
        """Get workflow's bot directory path."""
        return self.bot_directory
    
    @property
    def working_dir(self) -> Path:
        """Authoritative working directory for workflow operations.
        
        This is where content files are created (workflow_state.json, etc.)
        """
        return get_workspace_directory()
    
    @property
    def file(self) -> Path:
        """Get workflow state file path (always derived from workspace helper)."""
        return self.working_dir / 'workflow_state.json'
    
    @property
    def workflow_states(self) -> List[str]:
        """Get workflow states list (for backward compatibility)."""
        return self.states
    
    @property
    def current_state(self) -> str:
        """Get current state from state machine (self.state set by transitions library)."""
        return self.state
    
    def transition_to_next(self):
        # Reload state to ensure we have latest completed_actions before transitioning
        self.load_state()
        try:
            self.proceed()  # Trigger transition
            self.save_state()
        except Exception as e:
            # Already at final state or invalid transition - this is expected at workflow end
            logger.debug(f'Transition failed (expected at workflow end): {e}')
    
    def load_state(self):
        # If no workflow file, start at first action
        if not self.file.exists():
            # No file - reset to first action
            first_action = self.states[0] if self.states else None
            if first_action:
                self.machine.set_state(first_action)
                logger.info(f'No workflow state found, reset to first action: {first_action}')
            return
        
        try:
            state_data = json.loads(self.file.read_text(encoding='utf-8'))
            current_behavior = state_data.get('current_behavior', '')
            current_action = state_data.get('current_action', '')
            
            if current_behavior == f'{self.bot_name}.{self.behavior}':
                # Use current_action from file as source of truth
                # Extract action name from format: 'bot.behavior.action' -> 'action'
                if current_action:
                    action_name = current_action.split('.')[-1]
                    if action_name in self.states:
                        self.machine.set_state(action_name)
                        return
                
                # Fallback: if current_action not found or invalid, determine from completed_actions
                completed_actions = state_data.get('completed_actions', [])
                next_action = self._determine_next_action_from_completed(completed_actions)
                
                if next_action and next_action in self.states:
                    self.machine.set_state(next_action)
            else:
                # Behavior/bot doesn't match - reset to first action
                first_action = self.states[0] if self.states else None
                if first_action:
                    self.machine.set_state(first_action)
                    logger.info(f'Bot/behavior mismatch ({current_behavior} != {self.bot_name}.{self.behavior}), reset to first action: {first_action}')
        except Exception as e:
            logger.warning(f'Failed to load workflow state from {self.file}: {e}', exc_info=True)
            # On error, reset to first action
            first_action = self.states[0] if self.states else None
            if first_action:
                self.machine.set_state(first_action)
    
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
        for transition in self.transitions:
            if transition.get('source') == last_completed and transition.get('trigger') == 'proceed':
                return transition.get('dest')
        
        # If no transition found or at end, return last completed
        # (workflow will handle being at end)
        return last_completed
    
    def save_state(self):
        self.working_dir.mkdir(parents=True, exist_ok=True)
        
        existing_state = {}
        if self.file.exists():
            try:
                existing_state = json.loads(self.file.read_text(encoding='utf-8'))
            except Exception as e:
                logger.warning(f'Failed to load existing workflow state from {self.file}, starting fresh: {e}')
        
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
        # Don't write if working_dir not set
        # Workflow state is in {working_dir}/workflow_state.json
        self.working_dir.mkdir(parents=True, exist_ok=True)
        
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
    
    def navigate_to_action(self, target_action: str, out_of_order: bool = False):
        """
        Navigate to a specific action, handling out-of-order navigation if needed.
        
        This is the authoritative method for workflow state management.
        When navigating out of order, removes completed actions that come after
        the target action in the sequence.
        
        Args:
            target_action: Action name to navigate to (e.g., 'build_knowledge')
            out_of_order: Whether this is out-of-order navigation (default: False)
            
        Raises:
            ValueError: If target_action is not a valid state
        """
        # Validate action exists
        if target_action not in self.states:
            raise ValueError(f"Action '{target_action}' is not a valid state. Valid states: {self.states}")
        
        # If out-of-order, remove completed actions that come after target
        if out_of_order:
            self._remove_completed_actions_after_target(target_action)
        
        # Set state machine to target action
        self.machine.set_state(target_action)
        
        # Update workflow state file
        self.save_state()
    
    def _remove_completed_actions_after_target(self, target_action: str):
        """
        Remove all completed actions that come after the target action in the sequence.
        
        When navigating out of order to a specific action, we need to remove all
        completed actions that come after it, so the workflow state correctly reflects
        that we're going back to an earlier action.
        
        Args:
            target_action: The action we're navigating to (e.g., 'build_knowledge')
        """
        if not self.file.exists():
            return
        
        try:
            state_data = json.loads(self.file.read_text(encoding='utf-8'))
            completed_actions = state_data.get('completed_actions', [])
            
            if not completed_actions:
                return
            
            # Find the index of the target action
            target_index = self.states.index(target_action)
            
            # Filter out completed actions that:
            # 1. Belong to this behavior AND
            # 2. Come after the target action in the sequence
            behavior_prefix = f'{self.bot_name}.{self.behavior}.'
            filtered_completed = []
            
            for action_entry in completed_actions:
                action_state = action_entry.get('action_state', '')
                
                # Keep actions from other behaviors
                if not action_state.startswith(behavior_prefix):
                    filtered_completed.append(action_entry)
                    continue
                
                # Extract action name from full state (e.g., 'bot.behavior.action' -> 'action')
                action_name = action_state.split('.')[-1]
                
                # Keep this action if it's before or equal to target action in sequence
                if action_name in self.states:
                    action_index = self.states.index(action_name)
                    if action_index <= target_index:
                        filtered_completed.append(action_entry)
                else:
                    # Action not in states - keep it (might be from different workflow version)
                    filtered_completed.append(action_entry)
            
            # Update state with filtered completed actions
            state_data['completed_actions'] = filtered_completed
            
            # Update current_action to point to target action
            state_data['current_behavior'] = f'{self.bot_name}.{self.behavior}'
            state_data['current_action'] = f'{self.bot_name}.{self.behavior}.{target_action}'
            
            # Write updated state
            self.file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
            
        except Exception as e:
            logger.warning(f'Failed to remove completed actions after target {target_action}: {e}', exc_info=True)
    
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

