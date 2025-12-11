from pathlib import Path
import json
from fastmcp import FastMCP
from typing import Dict, Any
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.state.workspace import get_python_workspace_root


class MCPServerGenerator:
    
    def __init__(self, bot_directory: Path):
        """Initialize MCP Server Generator.
        
        Args:
            bot_directory: Directory where bot code lives (e.g., agile_bot/bots/story_bot)
                          Contains: agent.json, config/, behaviors/, src/
                          
        Note:
            workspace_directory is auto-detected from agent.json WORKING_AREA field
        """
        self.bot_directory = Path(bot_directory)
        
        # Derive bot_name from last folder in bot_directory
        self.bot_name = self.bot_directory.name
        
        # Config path follows convention: {bot_directory}/config/bot_config.json
        self.config_path = self.bot_directory / 'config' / 'bot_config.json'
        
        self.bot = None
        self.registered_tools = []
        
        # Discover actions from base_actions folder
        self.workflow_actions = self._discover_workflow_actions()
        self.independent_actions = self._discover_independent_actions()
    
    def _discover_workflow_actions(self) -> list:
        base_actions_path = self.bot_directory / 'base_actions'
        
        # Fallback to base_bot if bot doesn't have its own base_actions
        if not base_actions_path.exists():
            # Use centralized repository root
            repo_root = get_python_workspace_root()
            base_actions_path = repo_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
        
        if not base_actions_path.exists():
            return []
        
        workflow_actions = []
        for item in base_actions_path.iterdir():
            if item.is_dir() and item.name[0].isdigit() and '_' in item.name:
                # Extract action name without number prefix (e.g., '1_gather_context' -> 'gather_context')
                action_name = item.name.split('_', 1)[1]
                workflow_actions.append((int(item.name.split('_')[0]), action_name))
        
        # Sort by number prefix and return just the action names
        workflow_actions.sort(key=lambda x: x[0])
        return [action for _, action in workflow_actions]
    
    def _discover_independent_actions(self) -> list:
        base_actions_path = self.bot_directory / 'base_actions'
        
        # Fallback to base_bot if bot doesn't have its own base_actions
        if not base_actions_path.exists():
            repo_root = get_python_workspace_root()
            base_actions_path = repo_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
        
        if not base_actions_path.exists():
            return []
        
        independent_actions = []
        for item in base_actions_path.iterdir():
            if item.is_dir() and not (item.name[0].isdigit() and '_' in item.name):
                independent_actions.append(item.name)
        
        return independent_actions
    
    def create_server_instance(self) -> FastMCP:
        if not self.config_path.exists():
            raise FileNotFoundError(
                f'Bot Config not found at {self.config_path}'
            )
        
        try:
            bot_config = read_json_file(self.config_path)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f'Malformed Bot Config at {self.config_path}: {e.msg}',
                e.doc,
                e.pos
            )
        
        server_name = self.bot_name
        mcp_server = FastMCP(server_name)
        
        mcp_server.bot_config = bot_config
        
        # Initialize bot instance
        from agile_bot.bots.base_bot.src.bot.bot import Bot
        self.bot = Bot(
            bot_name=self.bot_name,
            bot_directory=self.bot_directory,
            config_path=self.config_path
        )
        
        return mcp_server
    
    def _get_bot_behaviors(self) -> list:
        """Safely get behaviors list from bot, handling mocks and properties."""
        bot_behaviors = getattr(self.bot, 'behaviors', [])
        if not isinstance(bot_behaviors, list):
            # Handle case where bot.behaviors might be a property or mock
            bot_config = self.bot.config if hasattr(self.bot, 'config') else None
            if bot_config and isinstance(bot_config, dict):
                bot_behaviors = bot_config.get('behaviors', [])
            else:
                bot_behaviors = []
        return bot_behaviors if isinstance(bot_behaviors, list) else []
    
    def register_all_behavior_action_tools(self, mcp_server: FastMCP):
        bot_config = mcp_server.bot_config
        behaviors = bot_config.get('behaviors', [])
        
        # Register bot tool (routes to current behavior and current action)
        self.register_bot_tool(mcp_server)
        
        # Register get_working_dir tool (shows current working directory)
        self.register_get_working_dir_tool(mcp_server)
        
        # Register close current action tool (marks action complete and transitions)
        self.register_close_current_action_tool(mcp_server)
        
        # Register confirm out-of-order tool (explicit human confirmation for skipping workflow sequence)
        self.register_confirm_out_of_order_tool(mcp_server)
        
        # Register restart server tool (terminates processes, clears cache, restarts)
        self.register_restart_server_tool(mcp_server)
        
        # Register behavior tools (routes to current action within behavior, or specific action if provided)
        for behavior in behaviors:
            self.register_behavior_tool(mcp_server, behavior)
    
    def _normalize_name_for_tool(self, name: str) -> str:
        """Normalize behavior name using centralized utility."""
        from agile_bot.bots.base_bot.src.bot.behavior_folder_finder import normalize_behavior_name
        return normalize_behavior_name(name)
    
    def register_bot_tool(self, mcp_server: FastMCP):
        tool_name = 'tool'
        
        @mcp_server.tool(name=tool_name, description=f'Bot tool for {self.bot_name} - routes to current behavior and action.')
        async def bot_tool(parameters: dict = None):
            if parameters is None:
                parameters = {}
            
            if self.bot is None:
                return {"error": "Bot not initialized"}
            
            result = self.bot.forward_to_current_behavior_and_current_action(parameters=parameters)
            
            return {
                "status": result.status,
                "behavior": result.behavior,
                "action": result.action,
                "data": result.data
            }
        
        self.registered_tools.append({
            'name': tool_name,
            'type': 'bot_tool',
            'description': f'Routes to current behavior and action'
        })
    
    def register_get_working_dir_tool(self, mcp_server: FastMCP):
        tool_name = 'get_working_dir'
        
        @mcp_server.tool(name=tool_name, description=f'Get the current working directory from WORKING_AREA. Triggers: where are we working, what\'s my location, show working directory')
        async def get_working_dir(input_file: str = None, project_dir: str = None):
            """Get the working directory from WORKING_AREA environment variable.

            Always returns the workspace directory from WORKING_AREA (no inference).
            """
            if self.bot is None:
                return {"error": "Bot not initialized"}

            # Always use workspace_directory from WORKING_AREA
            from agile_bot.bots.base_bot.src.state.workspace import get_workspace_directory
            working_dir = get_workspace_directory()
            return {
                'working_dir': str(working_dir),
                'message': f'Working directory from WORKING_AREA: {working_dir}'
            }
        
        self.registered_tools.append({
            'name': tool_name,
            'type': 'get_working_dir_tool',
            'description': f'Get current working directory'
        })
    
    def register_close_current_action_tool(self, mcp_server: FastMCP):
        tool_name = 'close_current_action'
        
        @mcp_server.tool(name=tool_name, description=f'Close current action tool for {self.bot_name} - marks current action complete and transitions to next')
        async def close_current_action(parameters: dict = None):
            """Mark the current action as complete and transition to the next action.

            The server derives the working directory from the workflow (via the
            centralized workspace helper). Callers do not need to provide a
            `working_dir`.
            """
            if parameters is None:
                parameters = {}

            if self.bot is None:
                return {"error": "Bot not initialized"}

            # Locate an active workflow_state.json from any behavior's workflow file
            state_file = None
            for behavior in self._get_bot_behaviors():
                behavior_obj = getattr(self.bot, behavior, None)
                if behavior_obj is None:
                    continue
                wf_file = behavior_obj.workflow.file
                if wf_file.exists():
                    state_file = wf_file
                    break

            if state_file is None:
                return {
                    "error": "No active workflow found",
                    "message": "No workflow_state.json exists for any behavior. Start a workflow first."
                }
            
            try:
                import json
                state_data = json.loads(state_file.read_text(encoding='utf-8'))
                current_behavior_path = state_data.get('current_behavior', '')
                current_action_path = state_data.get('current_action', '')
                
                if not current_behavior_path or not current_action_path:
                    return {
                        "error": "Cannot determine current action",
                        "message": "workflow_state.json is missing current_behavior or current_action"
                    }
                
                # Extract behavior and action names
                # 'story_bot.shape' -> 'shape'
                # 'story_bot.shape.gather_context' -> 'gather_context'
                behavior_name = current_behavior_path.split('.')[-1]
                action_name = current_action_path.split('.')[-1]
                
                # Get behavior object
                behavior_obj = getattr(self.bot, behavior_name, None)
                if behavior_obj is None:
                    bot_behaviors = self._get_bot_behaviors()
                    return {
                        "error": f"Behavior {behavior_name} not found",
                        "message": f"Available behaviors: {', '.join(bot_behaviors)}"
                    }
                
                # Workflow computes its own working_dir via the workspace helper;
                # no explicit set is required here.
                
                # Mark action as complete and transition
                # (idempotent - safe to call multiple times)
                behavior_obj.workflow.save_completed_action(action_name)
                
                # Action is complete - check if this is the final action in behavior
                is_final_action = (action_name == behavior_obj.workflow.states[-1] if behavior_obj.workflow.states else False)
                
                # Transition to next action within behavior
                previous_state = behavior_obj.workflow.current_state
                behavior_obj.workflow.transition_to_next()
                new_state = behavior_obj.workflow.current_state
                
                # Check if behavior is complete (stayed at same state = end of behavior)
                behavior_complete = (previous_state == new_state and is_final_action)
                
                if behavior_complete:
                    # Final action - check for next behavior
                    bot_behaviors = self._get_bot_behaviors()
                    if behavior_name in bot_behaviors:
                        current_behavior_index = bot_behaviors.index(behavior_name)
                        if current_behavior_index + 1 < len(bot_behaviors):
                            # Transition to next behavior
                            next_behavior_name = bot_behaviors[current_behavior_index + 1]
                        
                        # Update workflow state to next behavior, first action
                        next_behavior_obj = getattr(self.bot, next_behavior_name)
                        first_action = next_behavior_obj.workflow.states[0] if next_behavior_obj.workflow.states else 'gather_context'
                        
                        # Update state file with new behavior
                        state_data['current_behavior'] = f'{self.bot_name}.{next_behavior_name}'
                        state_data['current_action'] = f'{self.bot_name}.{next_behavior_name}.{first_action}'
                        state_file.write_text(json.dumps(state_data), encoding='utf-8')
                        
                        message = f"Behavior '{behavior_name}' complete. Transitioned to behavior '{next_behavior_name}', action '{first_action}'."
                        
                        return {
                            "status": "completed",
                            "completed_action": action_name,
                            "completed_behavior": behavior_name,
                            "next_behavior": next_behavior_name,
                            "next_action": first_action,
                            "message": message
                        }
                    else:
                        # No more behaviors - workflow complete
                        message = f"Action '{action_name}' marked complete. All behaviors complete."
                        return {
                            "status": "completed",
                            "completed_action": action_name,
                            "completed_behavior": behavior_name,
                            "message": message
                        }
                else:
                    # Not final - normal transition within behavior
                    message = f"Action '{action_name}' marked complete. Transitioned to '{new_state}'."
                    
                    return {
                        "status": "completed",
                        "completed_action": action_name,
                        "next_action": new_state,
                        "message": message
                    }
                
            except Exception as e:
                return {
                    "error": "Failed to close current action",
                    "message": str(e)
                }
        
        self.registered_tools.append({
            'name': tool_name,
            'type': 'close_action_tool',
            'description': f'Marks current action complete and transitions to next'
        })
    
    def register_confirm_out_of_order_tool(self, mcp_server: FastMCP):
        tool_name = 'confirm_out_of_order'
        
        @mcp_server.tool(name=tool_name, description=f'Confirm out-of-order behavior execution for {self.bot_name} - MUST be called explicitly by HUMAN USER, NOT by AI assistant. AI must ask user to call this tool, never call it directly.')
        async def confirm_out_of_order(behavior: str):
            """Confirm that user wants to execute a behavior out of sequence.
            
            CRITICAL: This tool MUST be called by a HUMAN USER, NOT by the AI assistant.
            When workflow order check requires confirmation, the AI must ask the user
            to call this tool explicitly. The AI must never call this tool directly.
            
            Args:
                behavior: The behavior name to confirm execution for (e.g., 'code', 'shape')
            
            Returns:
                dict with status and confirmation details
            """
            if self.bot is None:
                return {"error": "Bot not initialized"}
            
            from agile_bot.bots.base_bot.src.state.workspace import get_workspace_directory
            working_dir = get_workspace_directory()
            workflow_state_file = working_dir / 'workflow_state.json'
            
            if not workflow_state_file.exists():
                return {
                    "error": "No workflow state found",
                    "message": "Cannot confirm out-of-order execution without an active workflow. Start a workflow first."
                }
            
            try:
                import json
                from datetime import datetime
                
                state_data = json.loads(workflow_state_file.read_text(encoding='utf-8'))
                
                # Normalize behavior name for consistent storage/retrieval using centralized utility
                from agile_bot.bots.base_bot.src.bot.behavior_folder_finder import normalize_behavior_name
                normalized_behavior = normalize_behavior_name(behavior)
                
                # Store confirmation in workflow state (using normalized name)
                if 'out_of_order_confirmations' not in state_data:
                    state_data['out_of_order_confirmations'] = {}
                
                state_data['out_of_order_confirmations'][normalized_behavior] = {
                    'confirmed_at': datetime.now().isoformat(),
                    'confirmed_by': 'human',
                    'original_behavior': behavior  # Store original for reference
                }
                
                workflow_state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
                
                return {
                    "status": "confirmed",
                    "behavior": normalized_behavior,
                    "original_behavior": behavior,
                    "message": f"Out-of-order execution confirmed for behavior '{normalized_behavior}'. You may now execute this behavior.",
                    "confirmed_at": state_data['out_of_order_confirmations'][normalized_behavior]['confirmed_at']
                }
                
            except Exception as e:
                return {
                    "error": "Failed to confirm out-of-order execution",
                    "message": str(e)
                }
        
        self.registered_tools.append({
            'name': tool_name,
            'type': 'confirm_out_of_order_tool',
            'description': f'Confirm out-of-order behavior execution (must be called explicitly by human)'
        })
    
    def register_restart_server_tool(self, mcp_server: FastMCP):
        tool_name = 'restart_server'
        
        @mcp_server.tool(name=tool_name, description=f'Restart MCP server for {self.bot_name} - terminates processes, clears cache, and restarts to load code changes')
        async def restart_server(parameters: dict = None):
            """
            Restart the MCP server to load code changes.
            
            This will:
            1. Find and terminate existing MCP server processes
            2. Clear Python bytecode cache (__pycache__)
            3. Allow Cursor to restart the server automatically with fresh code
            
            Call this after making code changes to bot/workflow/action files.
            
            Returns:
                status: "restarted" or "ready_to_start"
                previous_pids: List of terminated process IDs
                cache_cleared: true/false
                message: Human-readable status
            """
            if parameters is None:
                parameters = {}
            
            try:
                from agile_bot.bots.base_bot.src.mcp.server_restart import restart_mcp_server
                
                # Get workspace root
                workspace_root = get_python_workspace_root()
                
                # Get bot_location as relative path from workspace root
                bot_location = str(self.bot_directory.relative_to(workspace_root))
                
                result = restart_mcp_server(
                    workspace_root=workspace_root,
                    bot_name=self.bot_name,
                    bot_location=bot_location
                )
                
                return result
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Failed to restart MCP server: {e}', exc_info=True)
                return {
                    "status": "error",
                    "error": "Failed to restart server",
                    "message": str(e)
                }
        
        self.registered_tools.append({
            'name': tool_name,
            'type': 'restart_server_tool',
            'description': f'Restarts MCP server to load code changes'
        })
    
    def register_behavior_tool(self, mcp_server: FastMCP, behavior: str):
        normalized_behavior = self._normalize_name_for_tool(behavior)
        tool_name = normalized_behavior
        
        # Load trigger patterns from behavior folder
        trigger_patterns = self._load_trigger_words_from_behavior_folder(behavior=behavior)
        
        description = f'{behavior} behavior for {self.bot_name}. Accepts optional action parameter and parameters dict.'
        if trigger_patterns:
            description += f'\nTrigger patterns: {", ".join(trigger_patterns[:5])}'  # Show first 5
        
        @mcp_server.tool(name=tool_name, description=description)
        async def behavior_tool(action: str = None, parameters: dict = None):
            if parameters is None:
                parameters = {}
            
            if self.bot is None:
                return {"error": "Bot not initialized"}
            
            # WORKFLOW STATE ENFORCEMENT: Check if workflow_state.json exists
            # Use workspace_directory directly from WORKING_AREA (no inference)
            from agile_bot.bots.base_bot.src.state.workspace import get_workspace_directory
            working_dir = get_workspace_directory()
            
            workflow_state_file = working_dir / 'workflow_state.json'
            
            if not workflow_state_file.exists():
                # Check if user provided confirmation
                if 'confirmed_behavior' in parameters:
                    confirmed = parameters['confirmed_behavior']
                    # Initialize workflow state with confirmed behavior
                    self._initialize_workflow_state(working_dir, confirmed)
                    # Continue to execute the behavior
                else:
                    # No workflow state - must execute entry workflow first
                    return self._execute_entry_workflow(working_dir, parameters)
            
            # WORKFLOW ORDER ENFORCEMENT: Check if proceeding out of order
            matches, current_behavior, expected_next = self.bot.does_requested_behavior_match_current(behavior)
            if not matches and expected_next:
                # Check if user has explicitly confirmed out-of-order execution via confirm_out_of_order tool
                import json
                state_data = {}
                if workflow_state_file.exists():
                    try:
                        state_data = json.loads(workflow_state_file.read_text(encoding='utf-8'))
                    except Exception:
                        pass
                
                confirmations = state_data.get('out_of_order_confirmations', {})
                # Normalize behavior name to match how confirmations are stored using centralized utility
                is_confirmed = False
                if behavior:
                    try:
                        from agile_bot.bots.base_bot.src.bot.behavior_folder_finder import normalize_behavior_name
                        normalized_behavior = normalize_behavior_name(behavior)
                        is_confirmed = normalized_behavior in confirmations
                    except Exception:
                        # If normalization fails, fall back to direct comparison
                        is_confirmed = behavior in confirmations
                
                if not is_confirmed:
                    # Out of order - ask for explicit confirmation via confirm_out_of_order tool
                    return {
                        "status": "requires_confirmation",
                        "message": (
                            f"**WORKFLOW ORDER CHECK**\n\n"
                            f"Current behavior: `{current_behavior}`\n"
                            f"Expected next behavior: `{expected_next}`\n"
                            f"Requested behavior: `{behavior}`\n\n"
                            f"You are attempting to execute `{behavior}` out of sequence. "
                            f"The next behavior in sequence should be `{expected_next}`.\n\n"
                            f"**To proceed, you must explicitly call the `confirm_out_of_order` tool with behavior `{behavior}`.**\n"
                            f"This confirmation must be sent by a human explicitly."
                        ),
                        "current_behavior": current_behavior,
                        "expected_next": expected_next,
                        "requested_behavior": behavior,
                        "confirmation_required": True,
                        "confirmation_tool": "confirm_out_of_order"
                    }
            
            behavior_obj = getattr(self.bot, behavior, None)
            if behavior_obj is None:
                return {"error": f"Behavior {behavior} not found"}
            
            # ACTION ORDER ENFORCEMENT: Check if proceeding out of order
            if action:  # Only check if specific action was requested
                matches, current_action, expected_next = behavior_obj.does_requested_action_match_current(action)
                if not matches and expected_next:
                    # Check if user has explicitly confirmed out-of-order execution via confirm_out_of_order tool
                    import json
                    state_data = {}
                    if workflow_state_file.exists():
                        try:
                            state_data = json.loads(workflow_state_file.read_text(encoding='utf-8'))
                        except Exception:
                            pass
                    
                    confirmations = state_data.get('out_of_order_confirmations', {})
                    # For action-level confirmation, check if behavior is confirmed (actions inherit behavior confirmation)
                    # Normalize behavior name to match how confirmations are stored using centralized utility
                    from agile_bot.bots.base_bot.src.bot.behavior_folder_finder import normalize_behavior_name
                    normalized_behavior = normalize_behavior_name(behavior)
                    is_confirmed = normalized_behavior in confirmations
                    
                    if not is_confirmed:
                        # Out of order - ask for explicit confirmation via confirm_out_of_order tool
                        return {
                            "status": "requires_confirmation",
                            "message": (
                                f"**ACTION ORDER CHECK**\n\n"
                                f"Current action: `{current_action}`\n"
                                f"Expected next action: `{expected_next}`\n"
                                f"Requested action: `{action}`\n\n"
                                f"You are attempting to execute `{action}` out of sequence. "
                                f"The next action in sequence should be `{expected_next}`.\n\n"
                                f"**To proceed, you must explicitly call the `confirm_out_of_order` tool with behavior `{behavior}`.**\n"
                                f"This confirmation must be sent by a human explicitly."
                            ),
                            "current_action": current_action,
                            "expected_next": expected_next,
                            "requested_action": action,
                            "requested_behavior": behavior,
                            "confirmation_required": True,
                            "confirmation_tool": "confirm_out_of_order"
                        }
            
            # If action is specified, route to that action, otherwise use current action
            if action:
                action_method = getattr(behavior_obj, action, None)
                if action_method is None:
                    return {"error": f"Action {action} not found in {behavior}"}
                result = action_method(parameters=parameters)
            else:
                result = behavior_obj.forward_to_current_action(parameters=parameters)
            
            return {
                "status": result.status,
                "behavior": result.behavior,
                "action": result.action,
                "data": result.data
            }
        
        self.registered_tools.append({
            'name': tool_name,
            'behavior': behavior,
            'type': 'behavior_tool',
            'trigger_patterns': trigger_patterns,
            'description': description
        })
    
    def _infer_working_dir_from_parameters(self, parameters: dict) -> Path:
        """
        Get working directory from WORKING_AREA (no inference).
        
        Always returns workspace_directory from WORKING_AREA environment variable.
        """
        from agile_bot.bots.base_bot.src.state.workspace import get_workspace_directory
        return get_workspace_directory()
    
    def _execute_entry_workflow(self, working_dir: Path, parameters: dict) -> dict:
        """
        Execute the bot's entry workflow to determine which behavior to start with.
        
        This follows the ENTRY WORKFLOW defined in the bot's instructions.json:
        1. Check {{project_area}}/docs/stories/ for artifacts
        2. Suggest earliest missing stage
        3. WAIT for user to confirm stage
        4. Read behavior instructions and execute
        
        Returns a message prompting the user to confirm which stage to start with.
        """
        import json
        
        # Check for existing artifacts in docs/stories/
        stories_dir = working_dir / 'docs' / 'stories'
        existing_artifacts = []
        
        if stories_dir.exists():
            bot_behaviors = self._get_bot_behaviors()
            for behavior in bot_behaviors:
                # Check for common artifact patterns per behavior
                behavior_artifacts = self._check_behavior_artifacts(stories_dir, behavior)
                if behavior_artifacts:
                    existing_artifacts.append({
                        'behavior': behavior,
                        'artifacts': behavior_artifacts
                    })
        
        # Determine earliest missing stage
        earliest_missing = None
        bot_behaviors = self._get_bot_behaviors()
        for behavior in bot_behaviors:
            # Check if this behavior has artifacts
            has_artifacts = any(a['behavior'] == behavior for a in existing_artifacts)
            if not has_artifacts:
                earliest_missing = behavior
                break
        
        # If no missing stages, suggest the last behavior
        if earliest_missing is None:
            earliest_missing = bot_behaviors[-1] if bot_behaviors else None
        
        # Build suggestion message
        message = f"**ENTRY WORKFLOW - No workflow_state.json found**\n\n"
        message += f"Checking for existing artifacts in `{stories_dir}`...\n\n"
        
        if existing_artifacts:
            message += "**Found existing artifacts:**\n"
            for artifact in existing_artifacts:
                message += f"- {artifact['behavior']}: {', '.join(artifact['artifacts'])}\n"
            message += "\n"
        else:
            message += "No existing artifacts found.\n\n"
        
        message += f"**Suggested starting behavior:** `{earliest_missing}`\n\n"
        message += "**Available behaviors:**\n"
        bot_behaviors = self._get_bot_behaviors()
        for i, behavior in enumerate(bot_behaviors, 1):
            status = "✓" if any(a['behavior'] == behavior for a in existing_artifacts) else " "
            message += f"{i}. [{status}] {behavior}\n"
        
        message += "\n**Please confirm which behavior to start with.**\n"
        if earliest_missing and earliest_missing in bot_behaviors:
            message += f"Reply with the behavior name (e.g., '{earliest_missing}') or number (e.g., '{bot_behaviors.index(earliest_missing) + 1}')."
        else:
            message += f"Reply with the behavior name (e.g., '{earliest_missing}')."
        
        return {
            "status": "requires_confirmation",
            "message": message,
            "suggested_behavior": earliest_missing,
            "available_behaviors": bot_behaviors,
            "existing_artifacts": existing_artifacts,
            "working_dir": str(working_dir)
        }
    
    def _check_behavior_artifacts(self, stories_dir: Path, behavior: str) -> list:
        """
        Check for common artifact patterns for a given behavior.
        
        Returns list of found artifact filenames.
        """
        artifacts = []
        
        # Common patterns per behavior
        patterns = {
            'shape': ['*story_map*', '*epic*', '*feature*'],
            'prioritization': ['*increment*', '*priority*', '*backlog*'],
            'arrange': ['*arrangement*', '*execution_order*'],
            'discovery': ['*discovery*', '*flow*', '*rules*'],
            'exploration': ['*exploration*', '*criteria*'],
            'scenarios': ['*.feature', '*scenario*'],
            'tests': ['*test*.py', '*_test.py', 'test_*.py']
        }
        
        behavior_patterns = patterns.get(behavior, [])
        
        for pattern in behavior_patterns:
            matches = list(stories_dir.rglob(pattern))
            for match in matches:
                if match.is_file():
                    artifacts.append(match.name)
        
        return artifacts
    
    def _initialize_workflow_state(self, working_dir: Path, behavior: str):
        """
        Initialize workflow_state.json for a new workflow starting with the specified behavior.
        """
        import json
        
        # Create docs/stories directory if it doesn't exist
        stories_dir = working_dir / 'docs' / 'stories'
        stories_dir.mkdir(parents=True, exist_ok=True)
        
        # Get the behavior object to find its first action
        behavior_obj = getattr(self.bot, behavior, None)
        if behavior_obj is None:
            raise ValueError(f"Behavior {behavior} not found")
        
        first_action = behavior_obj.workflow.states[0] if behavior_obj.workflow.states else 'gather_context'
        
        # Create initial workflow state
        workflow_state_file = working_dir / 'workflow_state.json'
        state_data = {
            'current_behavior': f'{self.bot_name}.{behavior}',
            'current_action': f'{self.bot_name}.{behavior}.{first_action}',
            'completed_actions': [],
            'started_at': None  # Will be set by workflow when it saves
        }
        
        workflow_state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')

    
    def _load_trigger_words_from_behavior_folder(
        self,
        behavior: str,
        action: str = None
    ) -> list:
        # Find behavior folder (handles numbered prefixes)
        from agile_bot.bots.base_bot.src.bot.bot import Behavior
        
        try:
            behavior_folder = Behavior.find_behavior_folder(
                self.bot_directory,
                self.bot_name,
                behavior
            )
        except FileNotFoundError:
            return []
        
        # Determine trigger words path
        if action:
            # Action-level trigger words
            trigger_path = behavior_folder / action / 'trigger_words.json'
        else:
            # Behavior-level trigger words
            trigger_path = behavior_folder / 'trigger_words.json'
        
        if not trigger_path.exists():
            return []
        
        try:
            trigger_data = read_json_file(trigger_path)
            return trigger_data.get('patterns', [])
        except Exception:
            return []
    
    def generate_bot_config_file(self, behaviors: list) -> Path:
        config_dir = self.bot_directory / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_path = config_dir / 'bot_config.json'
        config_data = {
            'name': self.bot_name,
            'behaviors': behaviors
        }
        
        config_path.write_text(json.dumps(config_data, indent=2))
        return config_path
    
    def generate_server_entry_point(self) -> Path:
        src_dir = self.bot_directory / 'src'
        src_dir.mkdir(parents=True, exist_ok=True)
        
        server_file = src_dir / f'{self.bot_name}_mcp_server.py'
        
        server_code = f'''"""
{self.bot_name.title().replace('_', ' ')} MCP Server Entry Point

Runnable MCP server for {self.bot_name} using FastMCP and base generator.
"""
from pathlib import Path
import sys
import os
import json

# Setup Python import path for package imports
python_workspace_root = Path(__file__).parent.parent.parent.parent.parent
if str(python_workspace_root) not in sys.path:
    sys.path.insert(0, str(python_workspace_root))

# ============================================================================
# BOOTSTRAP: Set environment variables before importing other modules
# ============================================================================

# 1. Self-detect bot directory from this script's location
bot_directory = Path(__file__).parent.parent  # src/ -> {self.bot_name}/
os.environ['BOT_DIRECTORY'] = str(bot_directory)

# 2. Read agent.json and set workspace directory (if not already set by mcp.json)
if 'WORKING_AREA' not in os.environ:
    agent_json_path = bot_directory / 'agent.json'
    if agent_json_path.exists():
        agent_config = json.loads(agent_json_path.read_text(encoding='utf-8'))
        if 'WORKING_AREA' in agent_config:
            os.environ['WORKING_AREA'] = agent_config['WORKING_AREA']

# ============================================================================
# Now import - everything will read from environment variables
# ============================================================================

from agile_bot.bots.base_bot.src.state.workspace import (
    get_bot_directory,
    get_workspace_directory
)
from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator


def main():
    """Main entry point for {self.bot_name} MCP server.

    Environment variables are bootstrapped before import:
    - BOT_DIRECTORY: Self-detected from script location
    - WORKING_AREA: Read from agent.json (or overridden by mcp.json env)
    
    All subsequent code reads from these environment variables.
    """
    # Get directories (these now just read from env vars we set above)
    bot_directory = get_bot_directory()
    workspace_directory = get_workspace_directory()
    
    # Create MCP server
    generator = MCPServerGenerator(
        bot_directory=bot_directory
    )

    mcp_server = generator.create_server_instance()
    generator.register_all_behavior_action_tools(mcp_server)

    mcp_server.run()


if __name__ == '__main__':
    main()
'''
        
        server_file.write_text(server_code)
        return server_file
    
    def generate_cursor_mcp_config(self) -> Dict:
        server_path = str(self.bot_directory / 'src' / f'{self.bot_name}_mcp_server.py')
        # Use centralized repository root
        repo_root = str(get_python_workspace_root())
        
        mcp_config = {
            'mcpServers': {
                f'{self.bot_name.replace("_", "-")}': {
                    'command': 'python',
                    'args': [server_path],
                    'cwd': repo_root
                    # Note: BOT_DIRECTORY and WORKING_AREA are now self-detected by the script
                    # You can add 'env': {'WORKING_AREA': 'path'} here to override agent.json
                }
            }
        }
        
        return mcp_config
    
    def discover_behaviors_from_folders(self) -> list:
        behaviors_dir = self.bot_directory / 'behaviors'
        
        if not behaviors_dir.exists():
            return []
        
        behaviors = []
        for item in behaviors_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                behaviors.append(item.name)
        
        return sorted(behaviors)
    
    def generate_server(self, behaviors: list = None) -> Dict[str, Path]:
        if behaviors is None:
            behaviors = self.discover_behaviors_from_folders()
        
        bot_config_path = self.generate_bot_config_file(behaviors)
        server_entry_path = self.generate_server_entry_point()
        mcp_config = self.generate_cursor_mcp_config()
        
        return {
            'bot_config': bot_config_path,
            'server_entry': server_entry_path,
            'mcp_config': mcp_config
        }
    
    def generate_awareness_files(self) -> Dict[str, Path]:
        # Generate workspace rules file
        rules_path = self._generate_workspace_rules_file()
        
        return {
            'rules_file': rules_path
        }
    
    def _generate_workspace_rules_file(self) -> Path:
        # Use centralized repository root
        repo_root = get_python_workspace_root()
        rules_dir = repo_root / '.cursor' / 'rules'
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        # Use bot-specific filename with hyphens
        bot_name_with_hyphens = self.bot_name.replace('_', '-')
        rules_file = rules_dir / f'mcp-{bot_name_with_hyphens}-awareness.mdc'
        
        # Load bot config to get behaviors
        bot_config = read_json_file(self.config_path)
        behaviors = bot_config.get('behaviors', [])
        
        # Load instructions.json for goal and behavior descriptions
        instructions_path = self.bot_directory / 'instructions.json'
        bot_goal = ''
        bot_description = ''
        behavior_descriptions = {}
        
        if instructions_path.exists():
            instructions = read_json_file(instructions_path)
            bot_goal = instructions.get('goal', '')
            bot_description = instructions.get('description', '')
            behavior_descriptions = instructions.get('behaviors', {})
        
        # Collect trigger words from all behaviors
        behavior_trigger_words = {}
        for behavior in behaviors:
            trigger_words = self._load_trigger_words_from_behavior_folder(
                behavior=behavior,
                action=None  # Get behavior-level trigger words
            )
            if trigger_words:
                behavior_trigger_words[behavior] = trigger_words
        
        # Build behavior sections (one section per behavior)
        behavior_sections = []
        for behavior in behaviors:
            behavior_display_name = behavior.replace('_', ' ').title()
            trigger_words = behavior_trigger_words.get(behavior, [])
            
            # Get behavior description from instructions.json
            # Handle numbered keys (1_shape) and non-numbered keys (shape)
            behavior_desc = behavior_descriptions.get(behavior, '')
            if not behavior_desc and behavior in behaviors:
                # Try with number prefix
                for key in behavior_descriptions.keys():
                    if key.endswith(behavior) or key.endswith(f'_{behavior}'):
                        behavior_desc = behavior_descriptions[key]
                        break
            
            if trigger_words:
                trigger_words_str = ', '.join(trigger_words)
                
                # Build explicit section with "When...as indicated by...Then check for"
                if behavior_desc:
                    section = f'''### {behavior_display_name} Behavior

**When user is trying to:** {behavior_desc}  
**as indicated by Trigger words:** {trigger_words_str}

**Then check for:** `{self.bot_name}_{behavior}_<action>` tool

**Example:** "{trigger_words[0]}" → use `{self.bot_name}_{behavior}_gather_context`

'''
                else:
                    section = f'''### {behavior_display_name} Behavior
**Trigger words:** {trigger_words_str}
**Tool pattern:** `{self.bot_name}_{behavior}_<action>`
**Example:** "{trigger_words[0]}" → use `{self.bot_name}_{behavior}_gather_context`

'''
                behavior_sections.append(section)
        
        behavior_sections_str = '\n'.join(behavior_sections)
        
        # Generate content dynamically with bot goal and behavior sections
        goal_line = f"\n**Bot Goal:** {bot_goal}\n" if bot_goal else ""
        desc_line = f"**Bot Description:** {bot_description}\n" if bot_description else ""
        
        critical_rule = f"**CRITICAL RULE:** When user is trying to {bot_goal.lower()}, ALWAYS check for and use MCP {self.bot_name} tools FIRST before falling back to manual file operations." if bot_goal else f"**CRITICAL RULE:** When user mentions workflow operations with trigger words, ALWAYS check for and use MCP {self.bot_name} tools FIRST before falling back to manual file operations."
        
        rules_content = f'''# MCP Tool Awareness

## Bot: {self.bot_name}
{goal_line}{desc_line}
## Priority: Check MCP Tools First

{critical_rule}

## Behaviors and Trigger Words

{behavior_sections_str}

## Error Handling

**CRITICAL:** If a registered tool is broken or returns an error:

1. **DO NOT automatically attempt a workaround**
2. **Inform user of the exact error details** (include full error message, tool name, parameters used)
3. **Ask user:** "The tool returned an error. Should I attempt to repair the tool, or proceed manually?"
4. **Wait for user decision** before taking any action

## Workflow Pattern

When you recognize a trigger word:

1. **Check if MCP tools are available** (ask mode vs agent mode)
2. **If in ask mode:** Inform user to switch to agent mode for MCP tool access
3. **If in agent mode:** Look for matching MCP tool and invoke it
4. **If tool returns error:** Follow error handling above (do NOT workaround)
5. **If no matching tool found:** Fall back to manual operations with explanation

## Example Usage

**User says:** "{behavior_trigger_words.get(behaviors[0], [behaviors[0]])[0] if behaviors and behavior_trigger_words else 'trigger word'}"

**AI should:**
1. Recognize trigger word from behavior section above
2. Check: Am I in agent mode?
3. Check: Is `{self.bot_name}_{behaviors[0] if behaviors else 'behavior'}_gather_context` available?
4. If yes → Invoke the tool
5. If no → Explain and ask how to proceed

**DO NOT** immediately start reading files manually without checking for tools first.
'''
        
        rules_file.write_text(rules_content, encoding='utf-8')
        return rules_file
