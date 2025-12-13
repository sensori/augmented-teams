from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import json
import importlib
from datetime import datetime
 
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.state.workspace import get_workspace_directory, get_base_actions_directory
import logging

logger = logging.getLogger(__name__)


def load_workflow_states_and_transitions(bot_directory: Path, behavior_name: str) -> Tuple[List[str], List[Dict]]:
    """Load workflow states and transitions from behavior.json file.
    
    Args:
        bot_directory: Directory where bot code lives
        behavior_name: REQUIRED behavior name. Each behavior MUST have its own behavior.json file.
    
    Returns:
        Tuple of (states list, transitions list)
    
    Raises:
        FileNotFoundError: If behavior.json is missing for the behavior
        ValueError: If actions_workflow.actions array is empty or missing
        RuntimeError: If file cannot be loaded or parsed
    """
    if not behavior_name:
        raise ValueError(
            "behavior_name is REQUIRED. Every behavior must have its own behavior.json file. "
            "No fallback to base workflow exists."
        )
    
    # Find behavior folder and load behavior.json (REQUIRED, no fallback)
    behavior_folder = Behavior.find_behavior_folder(bot_directory, '', behavior_name)
    behavior_file = behavior_folder / 'behavior.json'
    
    if not behavior_file.exists():
        raise FileNotFoundError(
            f"behavior.json is REQUIRED for behavior '{behavior_name}' but not found at: {behavior_file}\n"
            f"Every behavior must define its own workflow. Create {behavior_file} with an 'actions_workflow' section containing an 'actions' array."
        )
    
    # Load from behavior-specific behavior.json (REQUIRED)
    try:
        behavior_config = read_json_file(behavior_file)
        actions_workflow = behavior_config.get('actions_workflow', {})
        workflow_actions = actions_workflow.get('actions', [])
        
        if not workflow_actions:
            raise ValueError(
                f"behavior.json for behavior '{behavior_name}' is missing 'actions_workflow.actions' array. "
                f"File: {behavior_file}"
            )
    except Exception as e:
        raise RuntimeError(
            f"Failed to load behavior.json for behavior '{behavior_name}': {e}\n"
            f"File: {behavior_file}"
        ) from e
    
    # Sort by order
    workflow_actions.sort(key=lambda x: x['order'])
    
    # Build states list
    states = [action['name'] for action in workflow_actions]
    
    # Build transitions list
    transitions = []
    for action in workflow_actions:
        next_action = action.get('next_action')
        if next_action:
            transitions.append({
                'trigger': 'proceed',
                'source': action['name'],
                'dest': next_action
            })
    
    return states, transitions





class BotResult:
    
    def __init__(self, status: str, behavior: str, action: str, data: Dict[str, Any] = None):
        self.status = status
        self.behavior = behavior
        self.action = action
        self.data = data or {}
        self.executed_instructions_from = f'{behavior}/{action}'


class Behavior:
    
    def __init__(self, name: str, bot_name: str, bot_directory: Path, bot_instance=None):
        """Initialize Behavior.
        
        Args:
            name: Behavior name (e.g., 'shape', '1_shape')
            bot_name: Bot name (e.g., 'story_bot')
            bot_directory: Directory where bot code lives
            bot_instance: Reference to parent Bot instance
            
        Note:
            workspace_directory is auto-detected from get_workspace_directory()
        """
        self.name = name
        self.bot_name = bot_name
        self.bot_directory = Path(bot_directory)
        self.bot = bot_instance  # Reference to parent Bot instance
        
        # Load workflow configuration (behavior-specific if available)
        states, transitions = load_workflow_states_and_transitions(self.bot_directory, behavior_name=self.name)
        
        # Initialize workflow (contains state machine)
        from agile_bot.bots.base_bot.src.state.workflow import Workflow
        self.workflow = Workflow(
            bot_name=bot_name,
            behavior=name,
            bot_directory=bot_directory,
            states=states,
            transitions=transitions,
            bot_instance=bot_instance
        )
    
    @property
    def workspace_directory(self) -> Path:
        """Get workspace directory (auto-detected from environment/agent.json)."""
        return get_workspace_directory()
    
    @property
    def bot_dir(self) -> Path:
        """Get behavior's bot directory path."""
        return self.bot_directory
    
    @property
    def working_dir(self) -> Path:
        """Get workspace directory where content files are created."""
        return self.workspace_directory
    
   
    @property
    def workflow_state_file(self) -> Path:
        """Get workflow_state.json path."""
        return self.working_dir / 'workflow_state.json'
    
    @property
    def activity_log_file(self) -> Path:
        """Get activity_log.json path."""
        return self.working_dir / 'activity_log.json'
    
    @property
    def folder(self) -> Path:
        """Get behavior's folder path in behaviors directory."""
        return self.bot_directory / 'behaviors' / self.name
    
    @property
    def rules(self) -> List['Rule']:
        """Get all rules for this behavior (common + behavior-specific).
        
        Returns:
            List of Rule objects, each with 0 or 1 scanner (accessed via rule.scanner).
        """
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction, Rule
        action = ValidateRulesAction(
            bot_name=self.bot_name,
            behavior=self.name,
            bot_directory=self.bot_directory
        )
        rules_data = action.inject_behavior_specific_and_bot_rules()
        validation_rules = rules_data.get('validation_rules', [])
        
        # Convert rule dicts to Rule objects
        rule_objects = []
        for rule_dict in validation_rules:
            if isinstance(rule_dict, dict):
                rule_file = rule_dict.get('rule_file', 'unknown.json')
                rule_content = rule_dict.get('rule_content', rule_dict)
                
                # Determine behavior name from rule file path
                behavior_name = 'common'
                if '/behaviors/' in rule_file:
                    parts = rule_file.split('/behaviors/')
                    if len(parts) > 1:
                        behavior_part = parts[1].split('/')[0]
                        if '_' in behavior_part:
                            behavior_name = behavior_part.split('_', 1)[1]
                
                rule_obj = Rule(rule_file, rule_content, behavior_name)
                rule_objects.append(rule_obj)
        
        return rule_objects
    
    @property
    def scanners(self) -> List[type]:
        """Get all scanners across all rules for this behavior.
        
        Returns:
            List of scanner classes (all scanners from behavior.rules[x].scanner).
            Wrapper for behavior.rules[x].scanner - collects scanners from all rules.
        """
        scanners = []
        for rule in self.rules:
            scanner = rule.scanner  # Each rule has 0 or 1 scanner
            if scanner is not None:
                scanners.append(scanner)
        return scanners
    
    @staticmethod
    def find_behavior_folder(bot_directory: Path, bot_name: str, behavior_name: str) -> Path:
        """Find behavior folder within bot directory.
        
        Args:
            bot_directory: Directory where bot code lives
            bot_name: Bot name (for compatibility, not used since bot_directory is already specific)
            behavior_name: Name of behavior to find
            
        Returns:
            Path to behavior folder
        """
        behaviors_dir = bot_directory / 'behaviors'
        
        # Try to find folder with or without number prefix
        for folder in behaviors_dir.glob(f'*{behavior_name}'):
            if folder.is_dir():
                return folder
        
        # Fall back to exact name
        behavior_folder = behaviors_dir / behavior_name
        if behavior_folder.exists():
            return behavior_folder
        
        raise FileNotFoundError(
            f'Behavior folder not found for {behavior_name} in {behaviors_dir}'
        )
    
    @property
    def state(self):
        """Get current state from workflow."""
        return self.workflow.current_state
    
    @property
    def workflow_states(self):
        return self.workflow.workflow_states
    
    def proceed(self):
        self.workflow.machine.proceed()
    
    def execute_action(self, action_name: str, action_class, parameters: Dict[str, Any] = None) -> BotResult:
        if self.workflow.current_state != action_name:
            self.workflow.machine.set_state(action_name)
        
        # Use authoritative working_dir from workspace helper (environment-driven)
        working_dir = self.working_dir

        # Workflow uses the centralized workspace helper for its working_dir;
        # no need to set it here.
        
        self.workflow.save_state()
        
        action = action_class(
            bot_name=self.bot_name,
            behavior=self.name,
            bot_directory=self.bot_directory
        )
        
        
        data = action.execute(parameters)
        
        # Ensure data is a dict (action.execute should return a dict)
        if data is None:
            data = {}
  
        
        # Add working_dir to response so user knows where files are being created
        if working_dir:
            data['working_dir'] = str(working_dir)
        
        return BotResult(
            status='completed',
            behavior=self.name,
            action=action_name,
            data=data
        )
    
    
    def initialize_workspace(self, parameters: Dict[str, Any] = None) -> BotResult:
        """Initialize workspace - currently just forwards to gather_context."""
        # For now, initialize_workspace just forwards to gather_context
        # In the future, this could have its own InitializeWorkspaceAction
        return self.gather_context(parameters)
    
    def gather_context(self, parameters: Dict[str, Any] = None) -> BotResult:
        from agile_bot.bots.base_bot.src.bot.gather_context_action import GatherContextAction
        return self.execute_action('gather_context', GatherContextAction, parameters)
    
    def decide_planning_criteria(self, parameters: Dict[str, Any] = None) -> BotResult:
        from agile_bot.bots.base_bot.src.bot.planning_action import PlanningAction
        return self.execute_action('decide_planning_criteria', PlanningAction, parameters)
    
    def build_knowledge(self, parameters: Dict[str, Any] = None) -> BotResult:
        from agile_bot.bots.base_bot.src.bot.build_knowledge_action import BuildKnowledgeAction
        return self.execute_action('build_knowledge', BuildKnowledgeAction, parameters)
    
    def render_output(self, parameters: Dict[str, Any] = None) -> BotResult:
        from agile_bot.bots.base_bot.src.bot.render_output_action import RenderOutputAction
        return self.execute_action('render_output', RenderOutputAction, parameters)
    
    def _get_action_class(self, action_name: str, default_action_class):
        """Get action class for a given action, checking for custom override in actions-workflow.json.
        
        Args:
            action_name: Name of the action (e.g., 'validate_rules')
            default_action_class: Default action class to use if no override is found
        
        Returns:
            Action class to use (either custom override or default)
        """
        try:
            # Check behavior-specific behavior.json (at behavior root)
            behavior_folder = self.find_behavior_folder(self.bot_directory, self.bot_name, self.name)
            behavior_file = behavior_folder / 'behavior.json'
            
            if behavior_file.exists():
                behavior_config = read_json_file(behavior_file)
                actions_workflow = behavior_config.get('actions_workflow', {})
                actions = actions_workflow.get('actions', [])
                
                # Find the action with matching name
                for action_config in actions:
                    if action_config.get('name') == action_name:
                        # Check for custom action_class override
                        action_class_path = action_config.get('action_class')
                        if action_class_path:
                            # Load custom action class
                            module_path, class_name = action_class_path.rsplit('.', 1)
                            module = importlib.import_module(module_path)
                            custom_action_class = getattr(module, class_name)
                            return custom_action_class
        except (FileNotFoundError, Exception) as e:
            # Behavior folder doesn't exist or error loading, use default
            logger.debug(f'Could not load custom action class for {action_name}: {e}')
        
        # No custom override found, use default
        return default_action_class
    
    def validate_rules(self, parameters: Dict[str, Any] = None) -> BotResult:
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        # Check for custom action class override
        action_class = self._get_action_class('validate_rules', ValidateRulesAction)
        return self.execute_action('validate_rules', action_class, parameters)
    
    def test_validate(self, parameters: Dict[str, Any] = None) -> BotResult:
        """Execute test validation action - automatically runs TestScanner instances."""
        from agile_bot.bots.base_bot.src.bot.test_validate_action import TestValidateAction
        # Check for custom action class override
        action_class = self._get_action_class('test_validate', TestValidateAction)
        return self.execute_action('test_validate', action_class, parameters)
    
    def code_quality(self, parameters: Dict[str, Any] = None) -> BotResult:
        """Execute code quality action - automatically runs CodeScanner instances."""
        from agile_bot.bots.base_bot.src.bot.code_quality_action import CodeQualityAction
        # Check for custom action class override
        action_class = self._get_action_class('code_quality', CodeQualityAction)
        return self.execute_action('code_quality', action_class, parameters)
    
    def does_requested_action_match_current(self, requested_action: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if requested action matches current action or expected next action.
        
        Args:
            requested_action: Action name being requested (e.g., 'build_knowledge')
            
        Returns:
            Tuple of (matches: bool, current_action: Optional[str], expected_next: Optional[str])
            - matches: True if requested action is current or expected next, False otherwise
            - current_action: Current action name (None if no current action)
            - expected_next: Expected next action in sequence (None if no next or no state)
        """
        # Load workflow state to get current action
        self.workflow.load_state()
        
        current_action = self.workflow.current_state
        if not current_action:
            # No current action - allow any action (will start from beginning)
            return (True, None, None)
        
        # Get expected next action from workflow states sequence
        if current_action not in self.workflow.states:
            # Current action not in states - allow any
            return (True, current_action, None)
        
        current_index = self.workflow.states.index(current_action)
        expected_next = self.workflow.states[current_index + 1] if current_index + 1 < len(self.workflow.states) else None
        
        # Check if requested matches current OR expected next
        if requested_action == current_action:
            # Requested action is the current action - always allow (re-execution)
            matches = True
        elif expected_next is None:
            # No expected next (at end of sequence) - allow any
            matches = True
        else:
            # Check if requested matches expected next
            matches = (requested_action == expected_next)
        
        return (matches, current_action, expected_next)
    
    def navigate_to_action(self, action_name: str, parameters: Dict[str, Any] = None, out_of_order: bool = False) -> BotResult:
        """
        Navigate to a specific action and execute it.
        
        This delegates workflow state management to the Workflow class.
        
        Args:
            action_name: Action name to navigate to (e.g., 'build_knowledge')
            parameters: Parameters to pass to the action
            out_of_order: Whether this is out-of-order navigation (default: False)
            
        Returns:
            BotResult from executing the action
            
        Raises:
            ValueError: If action_name is not a valid state
            AttributeError: If action method doesn't exist
        """
        # Delegate state management to Workflow
        self.workflow.navigate_to_action(action_name, out_of_order=out_of_order)
        
        # Execute the action
        if not hasattr(self, action_name):
            raise AttributeError(f"Behavior {self.name} does not have action method '{action_name}'")
        
        action_method = getattr(self, action_name)
        result = action_method(parameters=parameters)
        
        if result is None:
            raise RuntimeError(f"Action method '{action_name}' returned None instead of BotResult")
        
        # Save state after action completion
        if not (result.data and result.data.get('requires_confirmation')):
            self.workflow.save_state()
        
        if self.workflow.is_action_completed(action_name):
            self.workflow.transition_to_next()
        
        return result
    
    def forward_to_current_action(self, parameters: Dict[str, Any] = None) -> BotResult:
        # CRITICAL: Workflow derives its working_dir from the workspace helper.
        # Nothing to set here; proceed to load existing state.
        
        self.workflow.load_state()
        
        current_action = self.workflow.current_state
        if not current_action:
            # Default to first action if no current state
            current_action = 'gather_context'
            self.workflow.machine.set_state(current_action)
        
        if not hasattr(self, current_action):
            raise AttributeError(f"Behavior {self.name} does not have action method '{current_action}'")
        
        action_method = getattr(self, current_action)
        result = action_method(parameters=parameters)
        
        if result is None:
            raise RuntimeError(f"Action method '{current_action}' returned None instead of BotResult")
        
        # Save state after action completion
        if not (result.data and result.data.get('requires_confirmation')):
            self.workflow.save_state()
        
        if self.workflow.is_action_completed(current_action):
            self.workflow.transition_to_next()
        
        return result
    
    def execute(self, action_class, action_name: str, 
                execute_fn, parameters: Dict[str, Any] = None) -> BotResult:
        action = action_class(
            bot_name=self.bot_name,
            behavior=self.name,
            bot_directory=self.bot_directory
        )
        
        # Track start
        action.track_activity_on_start()
        
        # Execute business logic
        result = execute_fn(action, parameters)
        
        # Track completion
        action.track_activity_on_completion(outputs=result if isinstance(result, dict) else {})
        
        # Save completed action to workflow state
        self.workflow.save_completed_action(action_name)
        
        return BotResult(
            status='completed',
            behavior=self.name,
            action=action_name,
            data=result if isinstance(result, dict) else {}
        )


class Bot:
    
    def __init__(self, bot_name: str, bot_directory: Path, config_path: Path):
        """Initialize Bot.
        
        Args:
            bot_name: Name of the bot (e.g., 'story_bot')
            bot_directory: Directory where bot code lives (e.g., agile_bot/bots/story_bot)
            config_path: Path to bot_config.json
            
        Note:
            workspace_directory is auto-detected from get_workspace_directory()
        """
        self.name = bot_name
        self.bot_name = bot_name  # Add bot_name attribute for consistency
        self.bot_directory = Path(bot_directory)
        self.config_path = Path(config_path)
        
        # Load config
        if not self.config_path.exists():
            raise FileNotFoundError(f'Bot config not found at {self.config_path}')
        
        # read_json_file already handles UTF-8 and raises appropriate errors
        self.config = read_json_file(self.config_path)
        
        # Initialize behaviors as attributes
        self.behaviors = self.config.get('behaviors', [])
        for behavior_name in self.behaviors:
            behavior_obj = Behavior(
                name=behavior_name,
                bot_name=self.name,
                bot_directory=self.bot_directory,
                bot_instance=self  # Pass bot instance to behavior
            )
            setattr(self, behavior_name, behavior_obj)
    
    @property
    def workspace_directory(self) -> Path:
        """Get workspace directory (auto-detected from environment/agent.json)."""
        return get_workspace_directory()
    
    def find_behavior_by_name(self, behavior_name: str) -> Optional[str]:
        """
        Find behavior in behaviors list by matching base name (handles numbered prefixes).
        
        Args:
            behavior_name: Behavior name to find (e.g., "shape", "1_shape", "discovery", "4_discovery")
            
        Returns:
            Full behavior name from self.behaviors if found, None otherwise
            (e.g., "shape" -> "1_shape", "1_shape" -> "1_shape", "discovery" -> "4_discovery")
        """
        # First try exact match
        if behavior_name in self.behaviors:
            return behavior_name
        
        # Extract base name (e.g., "1_shape" -> "shape")
        # Check if it starts with a digit and has underscore
        if behavior_name and '_' in behavior_name and behavior_name[0].isdigit():
            base_name = behavior_name.split('_', 1)[-1]
        else:
            base_name = behavior_name
        
        # Find behavior that ends with base name
        for behavior in self.behaviors:
            # Extract base name from behavior in list
            if behavior and '_' in behavior and behavior[0].isdigit():
                behavior_base = behavior.split('_', 1)[-1]
            else:
                behavior_base = behavior
            if behavior_base == base_name:
                return behavior
        
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
            from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
            workspace_root = get_python_workspace_root()
            workspace_dir_name = self.workspace_directory.name
            
            # If the relative path starts with the workspace directory name, it's already relative to workspace root
            if str(path).startswith(workspace_dir_name):
                path = workspace_root / path
            else:
                # Otherwise, resolve relative to workspace_directory
                path = self.workspace_directory / path
        
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
        # Determine current behavior by checking each behavior's workflow state file
        current_behavior = None
        for behavior_name in self.behaviors:
            behavior_instance = getattr(self, behavior_name)
            state_file = behavior_instance.workflow.file
            if state_file.exists():
                try:
                    state_data = json.loads(state_file.read_text(encoding='utf-8'))
                    current_behavior_path = state_data.get('current_behavior', '')
                    if current_behavior_path:
                        current_behavior = current_behavior_path.split('.')[-1]
                        break
                except Exception:
                    # Ignore malformed state files and continue searching
                    continue
        
        if not current_behavior or current_behavior not in self.behaviors:
            # Default to FIRST behavior in bot config
            current_behavior = self.behaviors[0]
        
        # Forward to behavior
        behavior_instance = getattr(self, current_behavior)
        return behavior_instance.forward_to_current_action(parameters=parameters)
    
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
        # Get workflow state file from first behavior (all behaviors share same file)
        if not self.behaviors:
            return (True, None, None)  # No behaviors configured, allow any
        
        first_behavior = self.behaviors[0]
        behavior_instance = getattr(self, first_behavior)
        state_file = behavior_instance.workflow.file
        
        if not state_file.exists():
            # No workflow state - allow any behavior (entry workflow handles this)
            return (True, None, None)
        
        try:
            state_data = json.loads(state_file.read_text(encoding='utf-8'))
            current_behavior_full = state_data.get('current_behavior', '')
            
            if not current_behavior_full:
                return (True, None, None)  # No current behavior, allow any
            
            # Extract behavior name from full name (e.g., "story_bot.shape" -> "shape")
            current_behavior = current_behavior_full.split('.')[-1] if '.' in current_behavior_full else current_behavior_full
            
            # Find matching behavior in self.behaviors using helper method (handles numbered prefixes)
            current_behavior_matched = self.find_behavior_by_name(current_behavior)
            
            # Determine expected next behavior based on sequence
            if current_behavior_matched is None:
                return (True, current_behavior, None)  # Current not in sequence, allow any
            
            current_index = self.behaviors.index(current_behavior_matched)
            expected_next = self.behaviors[current_index + 1] if current_index + 1 < len(self.behaviors) else None
            
            # Find matching behavior for requested (handles numbered prefixes)
            requested_matched = self.find_behavior_by_name(requested_behavior)
            
            # Check if requested matches expected next OR if requested matches current behavior
            # (allow executing current behavior - that's not "out of order")
            if requested_matched is None:
                matches = False
            elif requested_matched == current_behavior_matched:
                # Requested behavior is the current behavior - always allow (re-execution)
                matches = True
            elif expected_next is None:
                # No expected next (at end of sequence) - allow
                matches = True
            else:
                # Check if requested matches expected next
                matches = (requested_matched == expected_next)
            
            # Log for debugging (can be removed later)
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(
                f"Behavior order check: requested={requested_behavior} ({requested_matched}), "
                f"current={current_behavior} ({current_behavior_matched}), "
                f"expected_next={expected_next}, matches={matches}"
            )
            
            return (matches, current_behavior, expected_next)
            
        except Exception as e:
            logger.warning(f'Failed to check behavior order: {e}')
            return (True, None, None)  # On error, allow (fail open)
    
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
        if not self.behaviors:
            raise ValueError("No behaviors configured")
        
        first_behavior = self.behaviors[0]
        behavior_instance = getattr(self, first_behavior)
        workflow_state_file = behavior_instance.workflow.file
        
        # Check if workflow state exists (entry workflow)
        if not workflow_state_file.exists():
            # Check if user provided confirmation
            if 'confirmed_behavior' in parameters:
                confirmed = parameters['confirmed_behavior']
                # Initialize workflow state with confirmed behavior
                self._initialize_workflow_state(workflow_state_file.parent, confirmed)
            else:
                # No workflow state - must execute entry workflow first
                return self._execute_entry_workflow(workflow_state_file.parent, parameters)
        
        # Check behavior order
        matches, current_behavior, expected_next = self.does_requested_behavior_match_current(behavior_name)
        if not matches and expected_next:
            # Check if user has explicitly confirmed out-of-order execution
            import json
            state_data = {}
            if workflow_state_file.exists():
                try:
                    state_data = json.loads(workflow_state_file.read_text(encoding='utf-8'))
                except Exception:
                    pass
            
            confirmations = state_data.get('out_of_order_confirmations', {})
            from agile_bot.bots.base_bot.src.bot.behavior_folder_finder import normalize_behavior_name
            normalized_behavior = normalize_behavior_name(behavior_name)
            is_confirmed = normalized_behavior in confirmations
            
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
        
        # Find the actual behavior name (handles numbered prefixes)
        actual_behavior_name = self.find_behavior_by_name(behavior_name)
        if actual_behavior_name is None:
            raise ValueError(f"Behavior {behavior_name} not found")
        
        behavior_obj = getattr(self, actual_behavior_name, None)
        if behavior_obj is None:
            raise ValueError(f"Behavior {behavior_name} ({actual_behavior_name}) not found on bot")
        
        # Route to behavior - it handles action order checking
        if action:
            # FIRST: Validate that the action exists before checking sequence
            if action not in behavior_obj.workflow.states:
                valid_actions = ', '.join(behavior_obj.workflow.states)
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
                        'valid_actions': behavior_obj.workflow.states,
                        'behavior': behavior_name
                    }
                )
            
            # Check if out-of-order navigation requires confirmation
            matches, current_action, expected_next = behavior_obj.does_requested_action_match_current(action)
            if not matches and expected_next:
                # Check if user has explicitly confirmed out-of-order execution
                import json
                state_data = {}
                if workflow_state_file.exists():
                    try:
                        state_data = json.loads(workflow_state_file.read_text(encoding='utf-8'))
                    except Exception:
                        pass
                
                confirmations = state_data.get('out_of_order_confirmations', {})
                from agile_bot.bots.base_bot.src.bot.behavior_folder_finder import normalize_behavior_name
                normalized_behavior = normalize_behavior_name(behavior_name)
                is_confirmed = normalized_behavior in confirmations
                
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
        """Initialize workflow state with confirmed behavior."""
        workflow_state_file = working_dir / 'workflow_state.json'
        
        # Find actual behavior name - REQUIRED, no fallback
        actual_behavior_name = self.find_behavior_by_name(confirmed_behavior)
        if actual_behavior_name is None:
            raise ValueError(
                f"Behavior '{confirmed_behavior}' not found in bot '{self.name}'. "
                f"Available behaviors: {', '.join(self.behaviors)}. "
                f"Cannot initialize workflow with invalid behavior."
            )
        
        behavior_obj = getattr(self, actual_behavior_name)
        first_action = behavior_obj.workflow.states[0] if behavior_obj.workflow.states else 'gather_context'
        
        state_data = {
            'current_behavior': f'{self.name}.{actual_behavior_name}',
            'current_action': f'{self.name}.{actual_behavior_name}.{first_action}',
            'completed_actions': [],
            'timestamp': datetime.now().isoformat()
        }
        
        workflow_state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
    
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
                    f"{chr(10).join(f'- {b}' for b in self.behaviors)}\n\n"
                    "Provide 'confirmed_behavior' in parameters to proceed."
                ),
                'behaviors': self.behaviors,
                'requires_confirmation': True
            }
        )
    
    def close_current_action(self) -> BotResult:
        """Mark current action as complete and transition to next action."""
        # Get current behavior from workflow state using the correct workflow file path
        # Use the first behavior's workflow to get the correct state file path
        first_behavior = self.behaviors[0]
        behavior_instance = getattr(self, first_behavior)
        
        # Use workflow's file property to get correct path
        state_file = behavior_instance.workflow.file
        
        current_behavior = None
        if state_file.exists():
            try:
                state_data = json.loads(state_file.read_text(encoding='utf-8'))
                current_behavior_path = state_data.get('current_behavior', '')
                if current_behavior_path:
                    current_behavior = current_behavior_path.split('.')[-1]
            except Exception:
                pass
        
        if not current_behavior or current_behavior not in self.behaviors:
            # Default to FIRST behavior in bot config
            current_behavior = self.behaviors[0]
        
        # Get behavior instance
        behavior_instance = getattr(self, current_behavior)
        
        # Mark current action as complete and transition to next
        behavior_instance.workflow.load_state()
        current_action = behavior_instance.workflow.current_state
        behavior_instance.workflow.save_completed_action(current_action)
        behavior_instance.workflow.transition_to_next()
        
        # Forward to the next action
        return behavior_instance.forward_to_current_action()