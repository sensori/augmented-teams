"""
Base Bot Class

Provides core bot functionality including:
- Loading bot configuration
- Managing behaviors
- Routing tool invocations to behavior actions
- Workflow state management using transitions state machine
"""
from pathlib import Path
from typing import Dict, Any, List, Tuple
import json
from transitions import Machine
from agile_bot.bots.base_bot.src.utils import read_json_file


def load_workflow_states_and_transitions(workspace_root: Path) -> Tuple[List[str], List[Dict]]:
    """
    Load workflow states and transitions from action_config.json files.
    
    Reads all action configurations from base_actions/, sorts by order,
    and builds state list and transition list.
    
    Returns:
        Tuple of (states_list, transitions_list)
    """
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
                except Exception:
                    pass
    
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
    """Result from bot tool invocation."""
    
    def __init__(self, status: str, behavior: str, action: str, data: Dict[str, Any] = None):
        self.status = status
        self.behavior = behavior
        self.action = action
        self.data = data or {}
        self.executed_instructions_from = f'{behavior}/{action}'


class Behavior:
    """Behavior container for action execution."""
    
    def __init__(self, name: str, bot_name: str, workspace_root: Path):
        self.name = name
        self.bot_name = bot_name
        self.workspace_root = Path(workspace_root)
        
        # Load workflow configuration
        states, transitions = load_workflow_states_and_transitions(self.workspace_root)
        
        # Initialize workflow (contains state machine)
        from agile_bot.bots.base_bot.src.workflow import Workflow
        self.workflow = Workflow(
            bot_name=bot_name,
            behavior=name,
            workspace_root=workspace_root,
            states=states,
            transitions=transitions
        )
    
    @property
    def state(self):
        """Delegate to workflow current state."""
        return self.workflow.current_state
    
    @property
    def workflow_states(self):
        """Delegate to workflow states list."""
        return self.workflow.workflow_states
    
    def proceed(self):
        """Delegate to workflow transition."""
        self.workflow.machine.proceed()
    
    def initialize_project(self, parameters: Dict[str, Any] = None) -> BotResult:
        """Execute initialize project action with activity tracking and workflow state."""
        from agile_bot.bots.base_bot.src.actions.initialize_project_action import InitializeProjectAction
        
        if parameters is None:
            parameters = {}
        
        action = InitializeProjectAction(
            bot_name=self.bot_name,
            behavior=self.name,
            workspace_root=self.workspace_root
        )
        
        # Track activity start
        action.track_activity_on_start()
        
        # Initialize location
        project_area = parameters.get('project_area')
        data = action.initialize_location(project_area=project_area)
        
        # Track activity completion
        action.track_activity_on_completion(outputs=data)
        
        # Save workflow state
        action.save_state_on_completion()
        
        return BotResult(
            status='completed',
            behavior=self.name,
            action='initialize_project',
            data=data
        )
    
    def gather_context(self, parameters: Dict[str, Any] = None) -> BotResult:
        """Execute gather context action as Prefect task."""
        from agile_bot.bots.base_bot.src.actions.gather_context_action import GatherContextAction
        
        action = GatherContextAction(
            bot_name=self.bot_name,
            behavior=self.name,
            workspace_root=self.workspace_root
        )
        instructions = action.load_and_merge_instructions()
        
        return BotResult(
            status='completed',
            behavior=self.name,
            action='gather_context',
            data={'instructions': instructions}
        )
    
    def decide_planning_criteria(self, parameters: Dict[str, Any] = None) -> BotResult:
        """Execute decide planning criteria action as Prefect task."""
        from agile_bot.bots.base_bot.src.actions.planning_action import PlanningAction
        
        action = PlanningAction(
            bot_name=self.bot_name,
            behavior=self.name,
            workspace_root=self.workspace_root
        )
        instructions = action.inject_decision_criteria_and_assumptions()
        
        return BotResult(
            status='completed',
            behavior=self.name,
            action='decide_planning_criteria',
            data={'instructions': instructions}
        )
    
    def build_knowledge(self, parameters: Dict[str, Any] = None) -> BotResult:
        """Execute build knowledge action as Prefect task."""
        from agile_bot.bots.base_bot.src.actions.build_knowledge_action import BuildKnowledgeAction
        
        action = BuildKnowledgeAction(
            bot_name=self.bot_name,
            behavior=self.name,
            workspace_root=self.workspace_root
        )
        
        try:
            instructions = action.inject_knowledge_graph_template()
        except FileNotFoundError:
            # Template not required for all behaviors
            instructions = {}
        
        return BotResult(
            status='completed',
            behavior=self.name,
            action='build_knowledge',
            data={'instructions': instructions}
        )
    
    def render_output(self, parameters: Dict[str, Any] = None) -> BotResult:
        """Execute render output action as Prefect task."""
        return BotResult(
            status='completed',
            behavior=self.name,
            action='render_output'
        )
    
    def validate_rules(self, parameters: Dict[str, Any] = None) -> BotResult:
        """Execute validate rules action as Prefect task."""
        from agile_bot.bots.base_bot.src.actions.validate_rules_action import ValidateRulesAction
        
        action = ValidateRulesAction(
            bot_name=self.bot_name,
            behavior=self.name,
            workspace_root=self.workspace_root
        )
        instructions = action.inject_behavior_specific_and_bot_rules()
        
        return BotResult(
            status='completed',
            behavior=self.name,
            action='validate_rules',
            data={'instructions': instructions}
        )
    
    def correct_bot(self, parameters: Dict[str, Any] = None) -> BotResult:
        """Execute correct bot action."""
        return BotResult(
            status='completed',
            behavior=self.name,
            action='correct_bot'
        )
    
    def forward_to_current_action(self) -> BotResult:
        """Forward to current action using workflow state machine."""
        # Workflow knows current state (action)
        current_action = self.workflow.current_state
        
        # Execute that action
        action_method = getattr(self, current_action)
        result = action_method()
        
        # Transition to next state and save
        self.workflow.transition_to_next()
        
        return result
    
    def execute(self, action_class, action_name: str, 
                execute_fn, parameters: Dict[str, Any] = None) -> BotResult:
        """Template method: wraps action execution with activity tracking.
        
        Args:
            action_class: Action class to instantiate
            action_name: Name of the action
            execute_fn: Function to execute on action instance
            parameters: Optional parameters for execution
            
        Returns:
            BotResult with execution details
        """
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
        
        # Save workflow state
        action.save_state_on_completion()
        
        return BotResult(
            status='completed',
            behavior=self.name,
            action=action_name,
            data=result if isinstance(result, dict) else {}
        )


class Bot:
    """Base Bot class that manages behaviors and routes actions."""
    
    def __init__(self, bot_name: str, workspace_root: Path, config_path: Path):
        """Initialize Bot.
        
        Args:
            bot_name: Name of the bot
            workspace_root: Root workspace directory
            config_path: Path to bot_config.json
        """
        self.name = bot_name
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
        """Invoke a tool by routing to the correct behavior action.
        
        Args:
            tool_name: Name of the tool (e.g., 'test_bot_shape_gather_context')
            parameters: Parameters including 'behavior' and 'action'
            
        Returns:
            BotResult with execution details
            
        Raises:
            AttributeError: If behavior not found
            FileNotFoundError: If action not found in base actions
        """
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
        """
        Forward to current behavior and current action.
        
        Reads workflow state from file to determine current behavior.
        Defaults to first behavior in config if no state exists.
        
        Returns:
            BotResult from executed action
        """
        # Read workflow state
        state_file = self.workspace_root / 'project_area' / 'workflow_state.json'
        
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

