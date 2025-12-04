from pathlib import Path
from typing import Dict, Any, List, Tuple
import json
from transitions import Machine
from agile_bot.bots.base_bot.src.utils import read_json_file
import logging

logger = logging.getLogger(__name__)


def load_workflow_states_and_transitions(workspace_root: Path) -> Tuple[List[str], List[Dict]]:

    base_actions_dir = workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
    
    # Fallback if path doesn't exist (for tests with temp workspaces)
    if not base_actions_dir.exists():
        # Use hardcoded defaults
        states = ['initialize_project', 'gather_context', 'decide_planning_criteria', 'build_knowledge', 
                  'render_output', 'validate_rules', 'correct_bot']
        transitions = [
            {'trigger': 'proceed', 'source': 'initialize_project', 'dest': 'gather_context'},
            {'trigger': 'proceed', 'source': 'gather_context', 'dest': 'decide_planning_criteria'},
            {'trigger': 'proceed', 'source': 'decide_planning_criteria', 'dest': 'build_knowledge'},
            {'trigger': 'proceed', 'source': 'build_knowledge', 'dest': 'render_output'},
            {'trigger': 'proceed', 'source': 'render_output', 'dest': 'validate_rules'},
            {'trigger': 'proceed', 'source': 'validate_rules', 'dest': 'correct_bot'},
        ]
        return states, transitions
    
    # Load all action configs
    actions = []
    for action_dir in base_actions_dir.iterdir():
        if action_dir.is_dir():
            config_file = action_dir / 'action_config.json'
            if config_file.exists():
                try:
                    config = json.loads(config_file.read_text(encoding='utf-8'))
                    if config.get('workflow'):  # Only workflow actions
                        actions.append(config)
                except Exception as e:
                    # Skip malformed action config files
                    logger.warning(f'Failed to load action config from {config_file}: {e}')
    
    # Sort by order
    actions.sort(key=lambda x: x.get('order', 999))
    
    # Build states list
    states = [action['name'] for action in actions]
    
    # Build transitions list
    transitions = []
    for action in actions:
        if 'next_action' in action:
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
    
    def __init__(self, name: str, bot_name: str, workspace_root: Path):
        self.name = name
        self.bot_name = bot_name
        self.workspace_root = Path(workspace_root)
        
        # Load workflow configuration
        states, transitions = load_workflow_states_and_transitions(self.workspace_root)
        
        # Initialize workflow (contains state machine)
        from agile_bot.bots.base_bot.src.state.workflow import Workflow
        self.workflow = Workflow(
            bot_name=bot_name,
            behavior=name,
            workspace_root=workspace_root,
            states=states,
            transitions=transitions
        )
    
    @property
    def dir(self) -> Path:
        """Get behavior's bot directory path."""
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
    def project_area(self) -> Path:
        """Get project_area directory for current project."""
        return self.current_project / 'project_area'
    
    @property
    def workflow_state_file(self) -> Path:
        """Get workflow_state.json path."""
        return self.project_area / 'workflow_state.json'
    
    @property
    def activity_log_file(self) -> Path:
        """Get activity_log.json path."""
        return self.project_area / 'activity_log.json'
    
    @property
    def folder(self) -> Path:
        """Get behavior's folder path in behaviors directory."""
        return self.dir / 'behaviors' / self.name
    
    @staticmethod
    def find_behavior_folder(workspace_root: Path, bot_name: str, behavior_name: str) -> Path:
        behaviors_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors'
        
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
    
    
    def initialize_project(self, parameters: Dict[str, Any] = None) -> BotResult:
        from agile_bot.bots.base_bot.src.bot.initialize_project_action import InitializeProjectAction
        
        if parameters is None:
            parameters = {}
        
        action = InitializeProjectAction(
            bot_name=self.bot_name,
            behavior=self.name,
            workspace_root=self.workspace_root
        )
        
        # Track activity start
        action.track_activity_on_start()
        
        # Check if this is a confirmation response from user
        if parameters.get('confirm') and parameters.get('project_area'):
            # User is responding with their location choice (confirmation response)
            data = action.confirm_location(project_location=parameters['project_area'])
        else:
            # Initial call - propose location and ask for confirmation
            # (project_area here is just a hint, we still ask for confirmation)
            project_area = parameters.get('project_area')
            data = action.initialize_location(project_area=project_area)
        
        # Track activity completion
        action.track_activity_on_completion(outputs=data)
        
        # Save completed action to workflow state only if confirmed
        if not data.get('requires_confirmation'):
            self.workflow.save_completed_action('initialize_project')
        
        return BotResult(
            status='completed',
            behavior=self.name,
            action='initialize_project',
            data=data
        )
    
    def gather_context(self, parameters: Dict[str, Any] = None) -> BotResult:
        from agile_bot.bots.base_bot.src.bot.gather_context_action import GatherContextAction
        
        # Save workflow state when action is invoked (sets current_behavior and current_action)
        self.workflow.save_state()
        
        action = GatherContextAction(
            bot_name=self.bot_name,
            behavior=self.name,
            workspace_root=self.workspace_root
        )
        # Use template method that automatically tracks activity
        data = action.execute(parameters)
        
        return BotResult(
            status='completed',
            behavior=self.name,
            action='gather_context',
            data=data
        )
    
    def decide_planning_criteria(self, parameters: Dict[str, Any] = None) -> BotResult:
        from agile_bot.bots.base_bot.src.bot.planning_action import PlanningAction
        
        # Save workflow state when action is invoked (sets current_behavior and current_action)
        self.workflow.save_state()
        
        action = PlanningAction(
            bot_name=self.bot_name,
            behavior=self.name,
            workspace_root=self.workspace_root
        )
        # Use template method that automatically tracks activity
        data = action.execute(parameters)
        
        return BotResult(
            status='completed',
            behavior=self.name,
            action='decide_planning_criteria',
            data=data
        )
    
    def build_knowledge(self, parameters: Dict[str, Any] = None) -> BotResult:
        from agile_bot.bots.base_bot.src.bot.build_knowledge_action import BuildKnowledgeAction
        
        # Save workflow state when action is invoked (sets current_behavior and current_action)
        self.workflow.save_state()
        
        action = BuildKnowledgeAction(
            bot_name=self.bot_name,
            behavior=self.name,
            workspace_root=self.workspace_root
        )
        
        try:
            # Use template method that automatically tracks activity
            data = action.execute(parameters)
        except FileNotFoundError:
            # Template not required for all behaviors
            data = {'instructions': {}}
        
        return BotResult(
            status='completed',
            behavior=self.name,
            action='build_knowledge',
            data=data
        )
    
    def render_output(self, parameters: Dict[str, Any] = None) -> BotResult:
        from agile_bot.bots.base_bot.src.bot.render_output_action import RenderOutputAction
        
        # Save workflow state when action is invoked (sets current_behavior and current_action)
        self.workflow.save_state()
        
        action = RenderOutputAction(
            bot_name=self.bot_name,
            behavior=self.name,
            workspace_root=self.workspace_root
        )
        # Use template method that automatically tracks activity
        data = action.execute(parameters)
        
        return BotResult(
            status='completed',
            behavior=self.name,
            action='render_output',
            data=data
        )
    
    def validate_rules(self, parameters: Dict[str, Any] = None) -> BotResult:
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction
        
        # Save workflow state when action is invoked (sets current_behavior and current_action)
        self.workflow.save_state()
        
        action = ValidateRulesAction(
            bot_name=self.bot_name,
            behavior=self.name,
            workspace_root=self.workspace_root
        )
        # Use template method that automatically tracks activity
        data = action.execute(parameters)
        
        return BotResult(
            status='completed',
            behavior=self.name,
            action='validate_rules',
            data=data
        )
    
    def correct_bot(self, parameters: Dict[str, Any] = None) -> BotResult:
        # Save workflow state when action is invoked (sets current_behavior and current_action)
        self.workflow.save_state()
        
        return BotResult(
            status='completed',
            behavior=self.name,
            action='correct_bot'
        )
    
    def forward_to_current_action(self) -> BotResult:
        # Workflow knows current state (action)
        current_action = self.workflow.current_state
        
        # Execute that action
        action_method = getattr(self, current_action)
        result = action_method()
        
        # Check if action marked itself as complete (saved to completed_actions)
        # Actions call save_completed_action() when they're truly done
        if self.workflow.is_action_completed(current_action):
            # Action is complete - transition to next action
            self.workflow.transition_to_next()
        
        return result
    
    def execute(self, action_class, action_name: str, 
                execute_fn, parameters: Dict[str, Any] = None) -> BotResult:
        action = action_class(
            bot_name=self.bot_name,
            behavior=self.name,
            workspace_root=self.workspace_root
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
    
    def __init__(self, bot_name: str, workspace_root: Path, config_path: Path):
        self.name = bot_name
        self.bot_name = bot_name  # Add bot_name attribute for consistency
        self.workspace_root = Path(workspace_root)
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
                workspace_root=self.workspace_root
            )
            setattr(self, behavior_name, behavior_obj)
    
    def invoke_tool(self, tool_name: str, parameters: Dict[str, Any]) -> BotResult:
        behavior = parameters.get('behavior')
        action = parameters.get('action')
        
        # Get behavior object
        behavior_obj = getattr(self, behavior, None)
        if behavior_obj is None:
            raise AttributeError(
                f'Behavior {behavior} not found in bot {self.name}. '
                f'Available behaviors: {", ".join(self.behaviors)}'
            )
        
        # Get action method
        action_method = getattr(behavior_obj, action, None)
        if action_method is None:
            raise FileNotFoundError(
                f'Action {action} not found in base actions'
            )
        
        # Execute action
        return action_method(parameters)
    
    def forward_to_current_behavior_and_current_action(self) -> BotResult:
        # Read workflow state from bot directory
        bot_dir = self.workspace_root / 'agile_bot' / 'bots' / self.name
        state_file = bot_dir / 'project_area' / 'workflow_state.json'
        
        current_behavior = None
        if state_file.exists():
            try:
                state_data = json.loads(state_file.read_text(encoding='utf-8'))
                current_behavior_path = state_data.get('current_behavior', '')
                # Extract: 'story_bot.discovery' -> 'discovery'
                if current_behavior_path:
                    current_behavior = current_behavior_path.split('.')[-1]
            except Exception:
                pass
        
        if not current_behavior or current_behavior not in self.behaviors:
            # Default to FIRST behavior in bot config
            current_behavior = self.behaviors[0]
        
        # Forward to behavior
        behavior_instance = getattr(self, current_behavior)
        return behavior_instance.forward_to_current_action()

