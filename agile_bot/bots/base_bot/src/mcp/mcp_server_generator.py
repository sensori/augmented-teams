from pathlib import Path
import json
from fastmcp import FastMCP
from typing import Dict, Any
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.bot.workspace import get_python_workspace_root, get_base_actions_directory


class MCPServerGenerator:
    
    def __init__(self, bot_directory: Path):
        self.bot_directory = Path(bot_directory)
        
        # Derive bot_name from last folder in bot_directory
        self.bot_name = self.bot_directory.name
        
        # Config path follows convention: {bot_directory}/bot_config.json
        self.config_path = self.bot_directory / 'bot_config.json'
        
        self.bot = None
        self.registered_tools = []
        
        # Discover actions from base_actions folder
        self.workflow_actions = self._discover_workflow_actions()
        self.independent_actions = self._discover_independent_actions()
    
    def _discover_workflow_actions(self) -> list:
        # Use centralized workspace utility to get base_actions directory
        base_actions_path = get_base_actions_directory(bot_directory=self.bot_directory)
        
        workflow_actions = []
        for item in base_actions_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Action folders no longer have number prefixes
                action_name = item.name
                workflow_actions.append(action_name)
        
        # Return action names (sorted alphabetically for consistency)
        return sorted(workflow_actions)
    
    def _discover_independent_actions(self) -> list:
        # Use centralized workspace utility to get base_actions directory
        base_actions_path = get_base_actions_directory(bot_directory=self.bot_directory)
        
        independent_actions = []
        for item in base_actions_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
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
        """Get behavior names from bot instance or discover from folders."""
        # Try to get from bot.behaviors.names (Behaviors collection)
        if self.bot and hasattr(self.bot, 'behaviors'):
            behaviors_collection = self.bot.behaviors
            if hasattr(behaviors_collection, 'names'):
                return behaviors_collection.names
        # Fallback to folder discovery
        return self.discover_behaviors_from_folders()
    
    def register_all_tools(self, mcp_server: FastMCP):
        # Discover behaviors from folder structure
        behaviors = self._get_bot_behaviors()
        
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
    
    def register_bot_tool(self, mcp_server: FastMCP):
        tool_name = 'tool'
        
        @mcp_server.tool(name=tool_name, description=f'Bot tool for {self.bot_name} - routes to current behavior and action.')
        async def bot_tool(parameters: dict = None):
            if parameters is None:
                parameters = {}
            
            if self.bot is None:
                return {"error": "Bot not initialized"}
            
            current_behavior = self.bot.behaviors.current
            if current_behavior is None:
                if self.bot.behaviors.first:
                    self.bot.behaviors.navigate_to(self.bot.behaviors.first.name)
                    current_behavior = self.bot.behaviors.current
                else:
                    raise ValueError("No behaviors available")
            if current_behavior is None:
                raise ValueError("No current behavior")
            
            action = current_behavior.actions.forward_to_current()
            if action is None:
                return {"error": f"No current action found for behavior {current_behavior.name}"}
            
            result_data = action.execute(parameters or {})
            from agile_bot.bots.base_bot.src.bot.bot import BotResult
            result = BotResult(
                status='completed',
                behavior=current_behavior.name,
                action=action.action_name,
                data=result_data
            )
            
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
            if self.bot is None:
                return {"error": "Bot not initialized"}

            # Always use workspace_directory from WORKING_AREA
            from agile_bot.bots.base_bot.src.bot.workspace import get_workspace_directory
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
            if parameters is None:
                parameters = {}

            if self.bot is None:
                return {"error": "Bot not initialized"}

            # Locate an active behavior_action_state.json from workspace directory
            state_file = self.bot.bot_paths.workspace_directory / 'behavior_action_state.json'
            
            if not state_file.exists():
                return {
                    "error": "No active state found",
                    "message": "No behavior_action_state.json exists. Start a behavior first."
                }
            
            try:
                # Use behaviors collection to close current action
                current_behavior = self.bot.behaviors.current
                if current_behavior is None:
                    return {
                        "error": "No current behavior",
                        "message": "No current behavior found. Initialize a behavior first."
                    }
                
                # Load state to sync
                current_behavior.actions.load_state()
                current_action = current_behavior.actions.current
                if current_action is None:
                    return {
                        "error": "No current action",
                        "message": "No current action found."
                    }
                
                action_name = current_action.action_name
                action_names = current_behavior.actions.names
                is_final_action = (action_name == action_names[-1] if action_names else False)
                
                # Close current action (this transitions to next action)
                current_behavior.actions.close_current()
                
                # Check if behavior is complete
                new_action = current_behavior.actions.current
                behavior_complete = (new_action is None or (is_final_action and new_action.action_name == action_name))
                
                if behavior_complete:
                    # Transition to next behavior
                    next_behavior = self.bot.behaviors.next()
                    if next_behavior:
                        self.bot.behaviors.navigate_to(next_behavior.name)
                        next_behavior.actions.load_state()
                        first_action = next_behavior.actions.current.action_name if next_behavior.actions.current else 'clarify'
                        
                        message = f"Behavior '{current_behavior.name}' complete. Transitioned to behavior '{next_behavior.name}', action '{first_action}'."
                        
                        return {
                            "status": "completed",
                            "completed_action": action_name,
                            "completed_behavior": current_behavior.name,
                            "next_behavior": next_behavior.name,
                            "next_action": first_action,
                            "message": message
                        }
                    else:
                        # No more behaviors
                        message = f"Action '{action_name}' marked complete. All behaviors complete."
                        return {
                            "status": "completed",
                            "completed_action": action_name,
                            "completed_behavior": current_behavior.name,
                            "message": message
                        }
                else:
                    # Normal transition within behavior
                    new_action_name = current_behavior.actions.current.action_name if current_behavior.actions.current else None
                    message = f"Action '{action_name}' marked complete. Transitioned to '{new_action_name}'."
                    
                    return {
                        "status": "completed",
                        "completed_action": action_name,
                        "next_action": new_action_name,
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
            if self.bot is None:
                return {"error": "Bot not initialized"}
            
            from agile_bot.bots.base_bot.src.bot.workspace import get_workspace_directory
            working_dir = get_workspace_directory()
            state_file = working_dir / 'behavior_action_state.json'
            
            if not state_file.exists():
                return {
                    "error": "No behavior state found",
                    "message": "Cannot confirm out-of-order execution without an active behavior state. Start a behavior first."
                }
            
            try:
                import json
                from datetime import datetime
                
                state_data = json.loads(state_file.read_text(encoding='utf-8'))
                
                # Store confirmation in workflow state
                if 'out_of_order_confirmations' not in state_data:
                    state_data['out_of_order_confirmations'] = {}
                
                state_data['out_of_order_confirmations'][behavior] = {
                    'confirmed_at': datetime.now().isoformat(),
                    'confirmed_by': 'human'
                }
                
                state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
                
                return {
                    "status": "confirmed",
                    "behavior": behavior,
                    "message": f"Out-of-order execution confirmed for behavior '{behavior}'. You may now execute this behavior.",
                    "confirmed_at": state_data['out_of_order_confirmations'][behavior]['confirmed_at']
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
        tool_name = behavior
        
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
            
            # MCP Server forwards requests using explicit object hierarchy to lowest level:
            # 1. Find behavior from behaviors collection
            # 2. Find action from behavior's actions collection (if specified)
            # 3. Execute the action directly
            try:
                behavior_obj = self.bot.behaviors.find_by_name(behavior)
                if behavior_obj is None:
                    return {"error": f"Behavior '{behavior}' not found"}
                
                if action:
                    # Find action and execute directly at lowest level
                    action_obj = behavior_obj.actions.find_by_name(action)
                    if action_obj is None:
                        return {"error": f"Action '{action}' not found in behavior '{behavior}'"}
                    result_data = action_obj.execute(parameters)
                    from agile_bot.bots.base_bot.src.bot.bot import BotResult
                    result = BotResult(
                        status='completed',
                        behavior=behavior,
                        action=action,
                        data=result_data
                    )
                else:
                    # Get current action and execute directly
                    behavior_obj.actions.load_state()
                    current_action = behavior_obj.actions.current
                    if current_action is None:
                        return {"error": f"No current action in behavior '{behavior}'"}
                    result_data = current_action.execute(parameters)
                    from agile_bot.bots.base_bot.src.bot.bot import BotResult
                    result = BotResult(
                        status='completed',
                        behavior=behavior,
                        action=current_action.action_name,
                        data=result_data
                    )
                
                return {
                    "status": result.status,
                    "behavior": result.behavior,
                    "action": result.action,
                    "data": result.data
                }
            except Exception as e:
                return {"error": f"Failed to execute behavior: {e}"}
        
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
        from agile_bot.bots.base_bot.src.bot.workspace import get_workspace_directory
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
        message = f"**ENTRY STATE - No behavior_action_state.json found**\n\n"
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
    

    
    def _load_trigger_words_from_behavior_folder(
        self,
        behavior: str,
        action: str = None
    ) -> list:
        # Find behavior folder
        from agile_bot.bots.base_bot.src.bot.bot import Behavior
        
        # Behavior folder is directly named (no numbered prefixes)
        behavior_folder = self.bot_directory / 'behaviors' / behavior
        if not behavior_folder.exists():
            return []
        
        # Load from behavior.json
        behavior_file = behavior_folder / 'behavior.json'
        if behavior_file.exists():
            try:
                behavior_data = read_json_file(behavior_file)
                # Behavior-level trigger words from behavior.json
                trigger_words = behavior_data.get('trigger_words', {})
                return trigger_words.get('patterns', [])
            except Exception:
                pass
        
        return []
    
    def generate_bot_config_file(self, behaviors: list) -> Path:
        """Ensure bot_config.json exists but don't modify behaviors list.
        
        Behaviors are discovered from folder structure at runtime by Behaviors.names.
        This method only creates a minimal config if none exists; otherwise leaves it untouched.
        """
        config_path = self.bot_directory / 'bot_config.json'
        
        # If config exists, don't touch it - behaviors are discovered from folders
        if config_path.exists():
            return config_path
        
        # Only create minimal config if none exists
        config_data = {
            'name': self.bot_name
        }
        config_path.write_text(json.dumps(config_data, indent=2), encoding='utf-8')
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

# 2. Read bot_config.json and set workspace directory (if not already set by mcp.json env)
if 'WORKING_AREA' not in os.environ:
    config_path = bot_directory / 'bot_config.json'
    if config_path.exists():
        bot_config = json.loads(config_path.read_text(encoding='utf-8'))
        # Check mcp.env.WORKING_AREA (standard location)
        if 'mcp' in bot_config and 'env' in bot_config['mcp']:
            mcp_env = bot_config['mcp']['env']
            if 'WORKING_AREA' in mcp_env:
                os.environ['WORKING_AREA'] = mcp_env['WORKING_AREA']

# ============================================================================
# Now import - everything will read from environment variables
# ============================================================================

from agile_bot.bots.base_bot.src.bot.workspace import (
    get_bot_directory,
    get_workspace_directory
)
from agile_bot.bots.base_bot.src.mcp.mcp_server_generator import MCPServerGenerator


def main():
    """Main entry point for {self.bot_name} MCP server.

    Environment variables are bootstrapped before import:
    - BOT_DIRECTORY: Self-detected from script location
    - WORKING_AREA: Read from bot_config.json (or overridden by mcp.json env)
    
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
    generator.register_all_tools(mcp_server)

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
                    # You can add 'env': {'WORKING_AREA': 'path'} here to override bot_config.json
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
        # Initialize bot if not already initialized (needed for behavior discovery)
        if self.bot is None:
            self.create_server_instance()
        
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
        
        # Discover behaviors from folder structure
        behaviors = self.discover_behaviors_from_folders()
        
        # Load bot-level goal and description from bot_config.json
        bot_config = read_json_file(self.config_path)
        bot_goal = bot_config.get('goal', '')
        bot_description = bot_config.get('description', '')
        
        # Collect trigger words and descriptions from all behaviors (from behavior.json)
        behavior_trigger_words = {}
        behavior_descriptions = {}
        for behavior in behaviors:
            # Load from behavior.json (new format)
            # Behavior folder is directly named (no numbered prefixes)
            behavior_folder = self.bot_directory / 'behaviors' / behavior
            behavior_file = behavior_folder / 'behavior.json'
            try:
                if behavior_file.exists():
                    behavior_data = read_json_file(behavior_file)
                    behavior_descriptions[behavior] = behavior_data.get('description', '')
                    # Load trigger words directly from behavior_data
                    trigger_words_data = behavior_data.get('trigger_words', {})
                    if isinstance(trigger_words_data, dict):
                        trigger_words = trigger_words_data.get('patterns', [])
                    elif isinstance(trigger_words_data, list):
                        trigger_words = trigger_words_data
                    else:
                        trigger_words = []
                    # If not found in behavior_data, try loading via method
                    if not trigger_words:
                        trigger_words = self._load_trigger_words_from_behavior_folder(
                            behavior=behavior,
                            action=None  # Get behavior-level trigger words
                        )
                    if trigger_words:
                        behavior_trigger_words[behavior] = trigger_words
            except (FileNotFoundError, Exception) as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"Failed to load trigger words for {behavior}: {e}")
                pass
        
        # Build behavior sections (one section per behavior)
        behavior_sections = []
        for behavior in behaviors:
            behavior_display_name = behavior.replace('_', ' ').title()
            trigger_words = behavior_trigger_words.get(behavior, [])
            
            # Get behavior description from behavior.json (already loaded above)
            behavior_desc = behavior_descriptions.get(behavior, '')
            if not behavior_desc:
                # Try exact match lookup
                for key in behavior_descriptions.keys():
                    if key == behavior:
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

**Example:** "{trigger_words[0]}" → use `{self.bot_name}_{behavior}_clarify`

'''
                else:
                    section = f'''### {behavior_display_name} Behavior
**Trigger words:** {trigger_words_str}
**Tool pattern:** `{self.bot_name}_{behavior}_<action>`
**Example:** "{trigger_words[0]}" → use `{self.bot_name}_{behavior}_clarify`

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
3. Check: Is `{self.bot_name}_{behaviors[0] if behaviors else 'behavior'}_clarify` available?
4. If yes → Invoke the tool
5. If no → Explain and ask how to proceed

**DO NOT** immediately start reading files manually without checking for tools first.
'''
        
        rules_file.write_text(rules_content, encoding='utf-8')
        return rules_file
