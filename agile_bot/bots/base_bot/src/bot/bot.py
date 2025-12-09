from pathlib import Path
from typing import Dict, Any, List, Tuple
import json
 
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.state.workspace import get_workspace_directory
import logging

logger = logging.getLogger(__name__)


def load_workflow_states_and_transitions(bot_directory: Path) -> Tuple[List[str], List[Dict]]:
    from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root
    
    # Try to find base_actions in bot directory first
    base_actions_dir = bot_directory / 'base_actions'
    
    # Fallback to base_bot if bot doesn't have its own base_actions
    if not base_actions_dir.exists():
        # Use centralized repository root
        repo_root = get_python_workspace_root()
        base_actions_dir = repo_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
    
    # Fallback if path doesn't exist (for tests with temp workspaces)
    if not base_actions_dir.exists():
        # Use hardcoded defaults
        states = ['gather_context', 'decide_planning_criteria', 'build_knowledge', 
                  'render_output', 'validate_rules']
        transitions = [
            {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
            {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
            {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
            {'trigger': 'proceed', 'source': 'render_output', 'dest': 'validate_rules'},
        ]
        return states, transitions
    
    # Load workflow actions from action_config.json files
    workflow_actions = []
    for action_folder in base_actions_dir.iterdir():
        if not action_folder.is_dir():
            continue
        
        action_config_file = action_folder / 'action_config.json'
        if not action_config_file.exists():
            continue
        
        try:
            config_data = read_json_file(action_config_file)
            if config_data.get('workflow', False):
                workflow_actions.append({
                    'name': config_data.get('name', action_folder.name),
                    'order': config_data.get('order', 999),
                    'next_action': config_data.get('next_action')
                })
        except Exception as e:
            logger.warning(f'Failed to load action config from {action_config_file}: {e}')
            continue
    
    # Sort by order
    workflow_actions.sort(key=lambda x: x['order'])
    
    # Build states list
    states = [action['name'] for action in workflow_actions]
    
    # Build transitions list
    transitions = []
    for action in workflow_actions:
        if action['next_action']:
            transitions.append({
                'trigger': 'proceed',
                'source': action['name'],
                'dest': action['next_action']
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
        
        # Load workflow configuration
        states, transitions = load_workflow_states_and_transitions(self.bot_directory)
        
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
    
    def validate_rules(self, parameters: Dict[str, Any] = None) -> BotResult:
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        return self.execute_action('validate_rules', ValidateRulesAction, parameters)
    
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
        
        # Make it absolute if relative (relative to workspace_directory)
        if not path.is_absolute():
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