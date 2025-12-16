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
        self.name = bot_name
        self.bot_name = bot_name
        self.config_path = Path(config_path)
        
        self.bot_paths = BotPaths(bot_directory=bot_directory)
        self.bot_config = BotConfig(bot_name, self.bot_paths)
        self._behaviors_collection = Behaviors(self.bot_config, self.bot_paths)
        
        self._behaviors_collection._bot_instance = self
        for behavior in self._behaviors_collection:
            behavior.bot = self
    
    def find_behavior_by_name(self, behavior_name: str) -> Optional[str]:
        behavior = self.behaviors.find_by_name(behavior_name)
        if behavior:
            return behavior.name
        return None
    
    def infer_working_dir_from_path(self, path: str | Path) -> Path:
        path = Path(path)
        
        if path.is_file():
            path = path.parent
        
        if not path.is_absolute():
            from agile_bot.bots.base_bot.src.bot.workspace import get_python_workspace_root
            workspace_root = get_python_workspace_root()
            workspace_dir_name = self.bot_paths.workspace_directory.name
            
            if str(path).startswith(workspace_dir_name):
                path = workspace_root / path
            else:
                path = self.bot_paths.workspace_directory / path
        
        path = path.resolve()
        
        current = path
        while current != current.parent:
            workflow_state = current / 'workflow_state.json'
            if workflow_state.exists():
                return current
            current = current.parent
        
        return path
    
    def forward_to_current_behavior_and_current_action(self, parameters: Dict[str, Any] = None) -> BotResult:
        current_behavior_obj = self.behaviors.current
        if current_behavior_obj is None:
            if self.behaviors.check_exists(self.bot_config.behaviors_list[0]):
                current_behavior_obj = self.behaviors.find_by_name(self.bot_config.behaviors_list[0])
            else:
                raise ValueError("No behaviors available")
        
        return current_behavior_obj.forward_to_current_action(parameters=parameters)
    
    def does_requested_behavior_match_current(self, requested_behavior: str) -> Tuple[bool, Optional[str], Optional[str]]:
        if not self.behaviors.current:
            return (True, None, None)
        
        current_behavior_obj = self.behaviors.current
        current_behavior = current_behavior_obj.name
        
        requested_behavior_obj = self.behaviors.find_by_name(requested_behavior)
        requested_matched = requested_behavior_obj.name if requested_behavior_obj else None
        
        next_behavior_obj = self.behaviors.next()
        expected_next = next_behavior_obj.name if next_behavior_obj else None
        
        if requested_matched is None:
            matches = False
        elif requested_matched == current_behavior:
            matches = True
        elif expected_next is None:
            matches = True
        else:
            matches = (requested_matched == expected_next)
        
        logger.debug(
            f"Behavior order check: requested={requested_behavior} ({requested_matched}), "
            f"current={current_behavior}, "
            f"expected_next={expected_next}, matches={matches}"
        )
        
        return (matches, current_behavior, expected_next)
    
    def execute_behavior(self, behavior_name: str, action: str = None, parameters: Dict[str, Any] = None) -> BotResult:
        if parameters is None:
            parameters = {}
        
        if not self.behaviors.current:
            if not self.bot_config.behaviors_list:
                raise ValueError("No behaviors configured")
            first_behavior_name = self.bot_config.behaviors_list[0]
            self.behaviors.navigate_to(first_behavior_name)
        
        current_behavior_obj = self.behaviors.current
        if current_behavior_obj is None:
            raise ValueError("No current behavior")
        
        state_file = current_behavior_obj.bot.bot_paths.workspace_directory / 'behavior_action_state.json'
        
        if not state_file.exists():
            if 'confirmed_behavior' in parameters:
                confirmed = parameters['confirmed_behavior']
                self._initialize_workflow_state(state_file.parent, confirmed)
            else:
                return self._execute_entry_workflow(state_file.parent, parameters)
        
        matches, current_behavior, expected_next = self.does_requested_behavior_match_current(behavior_name)
        if not matches and expected_next:
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
        
        behavior_obj = self.behaviors.find_by_name(behavior_name)
        if behavior_obj is None:
            raise ValueError(f"Behavior {behavior_name} not found")
        
        if action:
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
                            f"When starting a new behavior, use: `{self.bot_name}_{behavior_name}_clarify`\n"
                            f"Example: `{self.bot_name}_{behavior_name}_clarify`"
                        ),
                        'requested_action': action,
                        'valid_actions': action_names,
                        'behavior': behavior_name
                    }
                )
            
            matches, current_action, expected_next = behavior_obj.does_requested_action_match_current(action)
            if not matches and expected_next:
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
            
            return behavior_obj.navigate_to_action(action, parameters=parameters, out_of_order=not matches)
        else:
            return behavior_obj.forward_to_current_action(parameters=parameters)
    
    def _initialize_workflow_state(self, working_dir: Path, confirmed_behavior: str):
        state_file = working_dir / 'behavior_action_state.json'
        
        behavior_obj = self.behaviors.find_by_name(confirmed_behavior)
        if behavior_obj is None:
            raise ValueError(
                f"Behavior '{confirmed_behavior}' not found in bot '{self.name}'. "
                f"Available behaviors: {', '.join(self.bot_config.behaviors_list)}. "
                f"Cannot initialize state with invalid behavior."
            )
        
        action_names = behavior_obj.actions.names
        first_action = action_names[0] if action_names else 'clarify'
        
        state_data = {
            'current_behavior': f'{self.name}.{behavior_obj.name}',
            'current_action': f'{self.name}.{behavior_obj.name}.{first_action}',
            'completed_actions': [],
            'timestamp': datetime.now().isoformat()
        }
        
        state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
    
    def _execute_entry_workflow(self, working_dir: Path, parameters: dict) -> BotResult:
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
        current_behavior_obj = self.behaviors.current
        if current_behavior_obj is None:
            if not self.bot_config.behaviors_list:
                raise ValueError("No behaviors configured")
            first_behavior_name = self.bot_config.behaviors_list[0]
            self.behaviors.navigate_to(first_behavior_name)
            current_behavior_obj = self.behaviors.current
        
        current_behavior_obj.actions.load_state()
        current_action_obj = current_behavior_obj.actions.current
        if current_action_obj:
            current_behavior_obj.actions.close_current()
        
        return current_behavior_obj.forward_to_current_action()
    
    @property
    def behaviors(self):
        """Access behaviors collection."""
        return self._behaviors_collection
    

    
    def __getattr__(self, name: str):
        """Allow accessing behaviors as attributes (e.g., bot.code, bot.shape)."""
        # Check if it's a behavior name
        behavior = self._behaviors_collection.find_by_name(name)
        if behavior:
            return behavior
        
        # Default behavior for unknown attributes
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")