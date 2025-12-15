from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import json
from datetime import datetime

from agile_bot.bots.base_bot.src.bot.bot_config import BotConfig
from agile_bot.bots.base_bot.src.bot.behaviors import Behaviors
from agile_bot.bots.base_bot.src.bot.behavior import Behavior
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths
import logging

logger = logging.getLogger(__name__)
__all__ = ["Bot", "BotResult", "Behavior"]


class BotResult:
    def __init__(self, status: str, behavior: str, action: str, data: Dict[str, Any] = None):
        self.status = status
        self.behavior = behavior
        self.action = action
        self.data = data or {}
        self.executed_instructions_from = f'{behavior}/{action}'


class Bot:
    
    def __init__(self, bot_name: str, bot_directory: Path, config_path: Path):
        """Initialize Bot.
        
        Args:
            bot_name: Name of the bot (e.g., 'story_bot')
            bot_directory: Directory where bot code lives (e.g., agile_bot/bots/story_bot)
            config_path: Path to bot_config.json
            
        Note:
            BotPaths is initialized automatically for accessing bot-related paths.
            Access paths via self.bot_paths (e.g., self.bot_paths.workspace_directory, self.bot_paths.bot_directory).
        """
        self.name = bot_name
        self.bot_name = bot_name  # Add bot_name attribute for consistency
        self.config_path = Path(config_path)
        
        # Initialize BotPaths for accessing bot-related paths
        self.bot_paths = BotPaths(bot_directory=bot_directory)
        
        # Load config using BotConfig (takes bot_name and bot_paths)
        self.bot_config = BotConfig(bot_name, self.bot_paths)
        
        # Initialize behaviors collection (pass bot_paths so it can manage state)
        self._behaviors_collection = Behaviors(self.bot_config, self.bot_paths)
        
        # Set bot_instance on behaviors collection and all behavior objects
        self._behaviors_collection._bot_instance = self
        for behavior in self._behaviors_collection.iterate():
            behavior.bot = self
    
    def find_behavior_by_name(self, behavior_name: str) -> Optional[str]:
        """
        Find behavior in behaviors list by matching name.
        
        Args:
            behavior_name: Behavior name to find (e.g., "shape", "1_shape", "discovery", "4_discovery")
            
        Returns:
            Full behavior name from behaviors collection if found, None otherwise
            (e.g., "shape" -> "1_shape", "1_shape" -> "1_shape", "discovery" -> "4_discovery")
        """
        # Use Behaviors collection's find_by_name method
        behavior = self.behaviors.find_by_name(behavior_name)
        if behavior:
            return behavior.name
        return None
    
    def infer_working_dir_from_path(self, path: str | Path) -> Path:
        """
        Infer working directory from a context file or folder path.
        Walks up the directory tree until finding workflow_state.json, or uses the folder itself.
        
        Args:
            path: File or folder path from context
            
        Returns:
            Path object representing the working directory
        """
        path = Path(path)
        
        # If it's a file, start from its parent directory
        if path.is_file():
            path = path.parent
        
        # Make it absolute if relative
        if not path.is_absolute():
            # Check if path already contains workspace_directory name to avoid double nesting
            from agile_bot.bots.base_bot.src.bot.workspace import get_python_workspace_root
            workspace_root = get_python_workspace_root()
            workspace_dir_name = self.bot_paths.workspace_directory.name
            
            # If the relative path starts with the workspace directory name, it's already relative to workspace root
            if str(path).startswith(workspace_dir_name):
                path = workspace_root / path
            else:
                # Otherwise, resolve relative to workspace_directory
                path = self.bot_paths.workspace_directory / path
        
        path = path.resolve()
        
        # Walk up looking for workflow_state.json
        current = path
        while current != current.parent:  # Stop at filesystem root
            workflow_state = current / 'workflow_state.json'
            if workflow_state.exists():
                return current
            current = current.parent
        
        # No workflow_state.json found, use the original folder
        return path
    
    def forward_to_current_behavior_and_current_action(self, parameters: Dict[str, Any] = None) -> BotResult:
        # Use Behaviors collection's current property
        current_behavior_obj = self.behaviors.current
        if current_behavior_obj is None:
            # Default to first behavior if no current
            if self.behaviors.check_exists(self.bot_config.behaviors_list[0]):
                current_behavior_obj = self.behaviors.find_by_name(self.bot_config.behaviors_list[0])
            else:
                raise ValueError("No behaviors available")
        
        # Forward to behavior
        return current_behavior_obj.forward_to_current_action(parameters=parameters)
    
    def does_requested_behavior_match_current(self, requested_behavior: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if requested behavior matches the current/expected behavior in workflow sequence.
        
        Args:
            requested_behavior: The behavior name being requested
            
        Returns:
            Tuple of (matches: bool, current_behavior: Optional[str], expected_next: Optional[str])
            - matches: True if requested behavior matches expected next, False otherwise
            - current_behavior: Current behavior from workflow state (None if no state)
            - expected_next: Expected next behavior in sequence (None if no next or no state)
        """
        # Use Behaviors collection
        if not self.behaviors.current:
            return (True, None, None)  # No current behavior, allow any
        
        current_behavior_obj = self.behaviors.current
        current_behavior = current_behavior_obj.name
        
            # Find matching behavior for requested
        requested_behavior_obj = self.behaviors.find_by_name(requested_behavior)
        requested_matched = requested_behavior_obj.name if requested_behavior_obj else None
        
        # Get next behavior
        next_behavior_obj = self.behaviors.next()
        expected_next = next_behavior_obj.name if next_behavior_obj else None
        
        # Check if requested matches expected next OR if requested matches current behavior
        # (allow executing current behavior - that's not "out of order")
        if requested_matched is None:
            matches = False
        elif requested_matched == current_behavior:
            # Requested behavior is the current behavior - always allow (re-execution)
            matches = True
        elif expected_next is None:
            # No expected next (at end of sequence) - allow
            matches = True
        else:
            # Check if requested matches expected next
            matches = (requested_matched == expected_next)
        
        # Log for debugging (can be removed later)
        logger.debug(
            f"Behavior order check: requested={requested_behavior} ({requested_matched}), "
            f"current={current_behavior}, "
            f"expected_next={expected_next}, matches={matches}"
        )
        
        return (matches, current_behavior, expected_next)
    
    def execute_behavior(self, behavior_name: str, action: str = None, parameters: Dict[str, Any] = None) -> BotResult:
        """
        Execute a behavior with optional action. Handles all workflow state management.
        
        This is the main entry point for behavior execution. It handles:
        - Workflow state initialization (entry workflow)
        - Behavior order checking and confirmations
        - Routing to the behavior
        - The behavior handles action order checking
        
        Args:
            behavior_name: Behavior name (e.g., "shape", "1_shape")
            action: Optional action name (e.g., "build_knowledge")
            parameters: Optional parameters dict
            
        Returns:
            BotResult from executing the behavior/action
            
        Raises:
            ValueError: If behavior not found or requires confirmation
        """
        if parameters is None:
            parameters = {}
        
        # Get workflow state file (all behaviors share same file)
        # Use current behavior or first behavior if none set
        if not self.behaviors.current:
            if not self.bot_config.behaviors_list:
                raise ValueError("No behaviors configured")
            first_behavior_name = self.bot_config.behaviors_list[0]
            self.behaviors.navigate_to(first_behavior_name)
        
        current_behavior_obj = self.behaviors.current
        if current_behavior_obj is None:
            raise ValueError("No current behavior")
        
        # Get state file path
        state_file = current_behavior_obj.bot.bot_paths.workspace_directory / 'behavior_action_state.json'
        
        # Check if state exists (entry workflow)
        if not state_file.exists():
            # Check if user provided confirmation
            if 'confirmed_behavior' in parameters:
                confirmed = parameters['confirmed_behavior']
                # Initialize state with confirmed behavior
                self._initialize_workflow_state(state_file.parent, confirmed)
            else:
                # No state - must execute entry workflow first
                return self._execute_entry_workflow(state_file.parent, parameters)
        
        # Check behavior order
        matches, current_behavior, expected_next = self.does_requested_behavior_match_current(behavior_name)
        if not matches and expected_next:
            # Check if user has explicitly confirmed out-of-order execution
            import json
            state_data = {}
            if state_file.exists():
                try:
                    state_data = json.loads(state_file.read_text(encoding='utf-8'))
                except Exception:
                    pass
            
            confirmations = state_data.get('out_of_order_confirmations', {})
            is_confirmed = behavior_name in confirmations
            
            if not is_confirmed:
                # Out of order - return confirmation requirement
                return BotResult(
                    status='requires_confirmation',
                    behavior=behavior_name,
                    action='',
                    data={
                        'message': (
                            f"**WORKFLOW ORDER CHECK**\n\n"
                            f"Current behavior: `{current_behavior}`\n"
                            f"Expected next behavior: `{expected_next}`\n"
                            f"Requested behavior: `{behavior_name}`\n\n"
                            f"You are attempting to execute `{behavior_name}` out of sequence. "
                            f"The next behavior in sequence should be `{expected_next}`.\n\n"
                            f"**To proceed, you must explicitly call the `confirm_out_of_order` tool with behavior `{behavior_name}`.**\n"
                            f"This confirmation must be sent by a human explicitly."
                        ),
                        'current_behavior': current_behavior,
                        'expected_next': expected_next,
                        'requested_behavior': behavior_name,
                        'requires_confirmation': True,
                        'confirmation_tool': 'confirm_out_of_order'
                    }
                )
        
        # Find the actual behavior using Behaviors collection
        behavior_obj = self.behaviors.find_by_name(behavior_name)
        if behavior_obj is None:
            raise ValueError(f"Behavior {behavior_name} not found")
        
        # Route to behavior - it handles action order checking
        if action:
            # FIRST: Validate that the action exists before checking sequence
            action_names = behavior_obj.actions.names
            if action not in action_names:
                valid_actions = ', '.join(action_names)
                return BotResult(
                    status='error',
                    behavior=behavior_name,
                    action=action,
                    data={
                        'message': (
                            f"**INVALID ACTION**\n\n"
                            f"Action `{action}` is not valid for behavior `{behavior_name}`.\n\n"
                            f"Valid actions are: {valid_actions}\n\n"
                            f"When starting a new behavior, use: `{self.bot_name}_{behavior_name}_gather_context`\n"
                            f"Example: `{self.bot_name}_{behavior_name}_gather_context`"
                        ),
                        'requested_action': action,
                        'valid_actions': action_names,
                        'behavior': behavior_name
                    }
                )
            
            # Check if out-of-order navigation requires confirmation
            matches, current_action, expected_next = behavior_obj.does_requested_action_match_current(action)
            if not matches and expected_next:
                # Check if user has explicitly confirmed out-of-order execution
                import json
                state_data = {}
                if state_file.exists():
                    try:
                        state_data = json.loads(state_file.read_text(encoding='utf-8'))
                    except Exception:
                        pass
                
                confirmations = state_data.get('out_of_order_confirmations', {})
                is_confirmed = behavior_name in confirmations
                
                if not is_confirmed:
                    # Out of order - return confirmation requirement
                    return BotResult(
                        status='requires_confirmation',
                        behavior=behavior_name,
                        action=action,
                        data={
                            'message': (
                                f"**ACTION ORDER CHECK**\n\n"
                                f"Current action: `{current_action}`\n"
                                f"Expected next action: `{expected_next}`\n"
                                f"Requested action: `{action}`\n\n"
                                f"You are attempting to execute `{action}` out of sequence. "
                                f"The next action in sequence should be `{expected_next}`.\n\n"
                                f"**To proceed, you must explicitly call the `confirm_out_of_order` tool with behavior `{behavior_name}`.**\n"
                                f"This confirmation must be sent by a human explicitly."
                            ),
                            'current_action': current_action,
                            'expected_next': expected_next,
                            'requested_action': action,
                            'requested_behavior': behavior_name,
                            'requires_confirmation': True,
                            'confirmation_tool': 'confirm_out_of_order'
                        }
                    )
            
            # Forward to Behavior - it handles all workflow state management
            return behavior_obj.navigate_to_action(action, parameters=parameters, out_of_order=not matches)
        else:
            # No action specified - forward to current action
            return behavior_obj.forward_to_current_action(parameters=parameters)
    
    def _initialize_workflow_state(self, working_dir: Path, confirmed_behavior: str):
        """Initialize state with confirmed behavior."""
        state_file = working_dir / 'behavior_action_state.json'
        
        # Find actual behavior name - REQUIRED, no fallback
        actual_behavior_name = self.find_behavior_by_name(confirmed_behavior)
        if actual_behavior_name is None:
            raise ValueError(
                f"Behavior '{confirmed_behavior}' not found in bot '{self.name}'. "
                f"Available behaviors: {', '.join(self.bot_config.behaviors_list)}. "
                f"Cannot initialize state with invalid behavior."
            )
        
        behavior_obj = self.behaviors.find_by_name(actual_behavior_name)
        if behavior_obj is None:
            raise ValueError(f"Behavior {actual_behavior_name} not found")
        action_names = behavior_obj.actions.names
        first_action = action_names[0] if action_names else 'gather_context'
        
        state_data = {
            'current_behavior': f'{self.name}.{actual_behavior_name}',
            'current_action': f'{self.name}.{actual_behavior_name}.{first_action}',
            'completed_actions': [],
            'timestamp': datetime.now().isoformat()
        }
        
        state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
    
    def _execute_entry_workflow(self, working_dir: Path, parameters: dict) -> BotResult:
        """Execute entry workflow when no workflow state exists."""
        # Return a result that indicates entry workflow is needed
        return BotResult(
            status='requires_confirmation',
            behavior='',
            action='',
            data={
                'message': (
                    "**ENTRY WORKFLOW**\n\n"
                    "No workflow state found. Please select a behavior to start:\n\n"
                    f"{chr(10).join(f'- {b}' for b in self.bot_config.behaviors_list)}\n\n"
                    "Provide 'confirmed_behavior' in parameters to proceed."
                ),
                'behaviors': self.bot_config.behaviors_list,
                'requires_confirmation': True
            }
        )
    
    def close_current_action(self) -> BotResult:
        """Mark current action as complete and transition to next action."""
        # Use Behaviors collection's current property
        current_behavior_obj = self.behaviors.current
        if current_behavior_obj is None:
            # Default to first behavior if no current
            if not self.bot_config.behaviors_list:
                raise ValueError("No behaviors configured")
            first_behavior_name = self.bot_config.behaviors_list[0]
            self.behaviors.navigate_to(first_behavior_name)
            current_behavior_obj = self.behaviors.current
        
        # Mark current action as complete and transition to next
        current_behavior_obj.actions.load_state()
        current_action_obj = current_behavior_obj.actions.current
        if current_action_obj:
            current_behavior_obj.actions.close_current()
        
        # Forward to the next action
        return current_behavior_obj.forward_to_current_action()