from pathlib import Path
import json
from fastmcp import FastMCP
from typing import Dict, Any
from agile_bot.bots.base_bot.src.utils import read_json_file


class MCPServerGenerator:
    
    def __init__(self, workspace_root: Path, bot_location: str = None):
        self.workspace_root = Path(workspace_root)
        
        if bot_location is None:
            bot_location = 'agile_bot/bots/base_bot'
        
        self.bot_location = Path(bot_location)
        
        # Derive bot_name from last folder in bot_location
        self.bot_name = self.bot_location.name
        
        # Config path follows convention: {bot_location}/config/bot_config.json
        self.config_path = self.workspace_root / self.bot_location / 'config' / 'bot_config.json'
        
        self.bot = None
        self.registered_tools = []
        
        # Discover actions from base_actions folder
        self.workflow_actions = self._discover_workflow_actions()
        self.independent_actions = self._discover_independent_actions()
    
    def _discover_workflow_actions(self) -> list:
        base_actions_path = self.workspace_root / self.bot_location / 'base_actions'
        
        # Fallback to base_bot if bot doesn't have its own base_actions
        if not base_actions_path.exists():
            base_actions_path = self.workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
        
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
        base_actions_path = self.workspace_root / self.bot_location / 'base_actions'
        
        # Fallback to base_bot if bot doesn't have its own base_actions
        if not base_actions_path.exists():
            base_actions_path = self.workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'base_actions'
        
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
        
        server_name = f'{self.bot_name}_server'
        mcp_server = FastMCP(server_name)
        
        mcp_server.bot_config = bot_config
        
        # Initialize bot instance
        from agile_bot.bots.base_bot.src.bot.bot import Bot
        self.bot = Bot(
            bot_name=self.bot_name,
            workspace_root=self.workspace_root,
            config_path=self.config_path
        )
        
        return mcp_server
    
    def register_all_behavior_action_tools(self, mcp_server: FastMCP):
        bot_config = mcp_server.bot_config
        behaviors = bot_config.get('behaviors', [])
        
        # Register bot tool (routes to current behavior and current action)
        self.register_bot_tool(mcp_server)
        
        # Register close current action tool (marks action complete and transitions)
        self.register_close_current_action_tool(mcp_server)
        
        # Register behavior tools (routes to current action within behavior)
        for behavior in behaviors:
            self.register_behavior_tool(mcp_server, behavior)
        
        # Register all behavior-action tools
        all_actions = self.workflow_actions + self.independent_actions
        
        for behavior in behaviors:
            for action in all_actions:
                self.register_behavior_action_tool(
                    mcp_server=mcp_server,
                    behavior=behavior,
                    action=action
                )
    
    def _normalize_name_for_tool(self, name: str) -> str:
        # Strip number prefix (e.g., '1_shape' -> 'shape')
        if name and name[0].isdigit() and '_' in name:
            name = name.split('_', 1)[1]
        
        # Abbreviate common long words
        abbreviations = {
            'specification': 'spec',
            'decide_planning_criteria': 'decide_planning',
        }
        
        for full, abbrev in abbreviations.items():
            name = name.replace(full, abbrev)
        
        return name
    
    def register_bot_tool(self, mcp_server: FastMCP):
        tool_name = f'{self.bot_name}_tool'
        
        @mcp_server.tool(name=tool_name, description=f'Bot tool for {self.bot_name} - routes to current behavior and action')
        async def bot_tool(parameters: dict = None):
            if parameters is None:
                parameters = {}
            
            if self.bot is None:
                return {"error": "Bot not initialized"}
            
            result = self.bot.forward_to_current_behavior_and_current_action()
            
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
    
    def register_close_current_action_tool(self, mcp_server: FastMCP):
        tool_name = f'{self.bot_name}_close_current_action'
        
        @mcp_server.tool(name=tool_name, description=f'Close current action tool for {self.bot_name} - marks current action complete and transitions to next')
        async def close_current_action(parameters: dict = None):
            """
            Mark the current action as complete and transition to next action.
            
            Call this after:
            1. Action tool returned instructions
            2. AI followed the instructions
            3. Human reviewed and confirmed completion
            
            Returns:
                status: "completed"
                completed_action: Name of action that was closed
                next_action: Name of next action (or same if at end)
                message: Human-readable status message
            """
            if parameters is None:
                parameters = {}
            
            if self.bot is None:
                return {"error": "Bot not initialized"}
            
            # Get first behavior to access workflow properties
            # (all behaviors share same current_project configuration)
            first_behavior = self.bot.behaviors[0] if self.bot.behaviors else None
            if not first_behavior:
                return {
                    "error": "No behaviors configured",
                    "message": "Bot has no behaviors configured."
                }
            
            behavior_obj = getattr(self.bot, first_behavior)
            
            # Use workflow properties instead of manually constructing paths
            if not behavior_obj.workflow.current_project_file.exists():
                return {
                    "error": "No project initialized",
                    "message": "No current_project.json found. Initialize project first."
                }
            
            # Workflow state file path from workflow object
            state_file = behavior_obj.workflow.file
            
            if not state_file.exists():
                return {
                    "error": "No active workflow found",
                    "message": f"No workflow_state.json exists at {state_file}. Start a workflow first."
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
                    return {
                        "error": f"Behavior {behavior_name} not found",
                        "message": f"Available behaviors: {', '.join(self.bot.behaviors)}"
                    }
                
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
                    current_behavior_index = self.bot.behaviors.index(behavior_name)
                    if current_behavior_index + 1 < len(self.bot.behaviors):
                        # Transition to next behavior
                        next_behavior_name = self.bot.behaviors[current_behavior_index + 1]
                        
                        # Update workflow state to next behavior, first action
                        next_behavior_obj = getattr(self.bot, next_behavior_name)
                        first_action = next_behavior_obj.workflow.states[0] if next_behavior_obj.workflow.states else 'initialize_project'
                        
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
    
    def register_behavior_tool(self, mcp_server: FastMCP, behavior: str):
        normalized_behavior = self._normalize_name_for_tool(behavior)
        tool_name = f'{self.bot_name}_{normalized_behavior}_tool'
        
        @mcp_server.tool(name=tool_name, description=f'{behavior} behavior tool for {self.bot_name} - routes to current action')
        async def behavior_tool(parameters: dict = None):
            if parameters is None:
                parameters = {}
            
            if self.bot is None:
                return {"error": "Bot not initialized"}
            
            behavior_obj = getattr(self.bot, behavior, None)
            if behavior_obj is None:
                return {"error": f"Behavior {behavior} not found"}
            
            result = behavior_obj.forward_to_current_action()
            
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
            'description': f'Routes to current action in {behavior}'
        })
    
    def register_behavior_action_tool(
        self,
        mcp_server: FastMCP,
        behavior: str,
        action: str
    ):
        # Normalize names to keep tool names under 60 chars
        normalized_behavior = self._normalize_name_for_tool(behavior)
        normalized_action = self._normalize_name_for_tool(action)
        
        tool_name = f'{self.bot_name}_{normalized_behavior}_{normalized_action}'
        
        trigger_patterns = self._load_trigger_words_from_behavior_folder(
            behavior=behavior,
            action=action
        )
        
        description = f'{behavior} {action} for {self.bot_name}'
        if trigger_patterns:
            description += f'\nTrigger patterns: {", ".join(trigger_patterns)}'
        
        @mcp_server.tool(name=tool_name, description=description)
        async def behavior_action_tool(parameters: dict = None):
            if parameters is None:
                parameters = {}
            
            if self.bot is None:
                return {"error": "Bot not initialized"}
            
            behavior_obj = getattr(self.bot, behavior, None)
            if behavior_obj is None:
                return {"error": f"Behavior {behavior} not found"}
            
            action_method = getattr(behavior_obj, action, None)
            if action_method is None:
                return {"error": f"Action {action} not found in {behavior}"}
            
            result = action_method(parameters=parameters)
            
            # Return serializable dict instead of BotResult object
            return {
                "status": result.status,
                "behavior": result.behavior,
                "action": result.action,
                "data": result.data
            }
        
        self.registered_tools.append({
            'name': tool_name,
            'behavior': behavior,
            'action': action,
            'trigger_patterns': trigger_patterns,
            'description': description
        })
    
    def _load_trigger_words_from_behavior_folder(
        self,
        behavior: str,
        action: str = None
    ) -> list:
        # Find behavior folder (handles numbered prefixes)
        from agile_bot.bots.base_bot.src.bot.bot import Behavior
        
        try:
            behavior_folder = Behavior.find_behavior_folder(
                self.workspace_root,
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
        config_dir = self.workspace_root / 'agile_bot' / 'bots' / self.bot_name / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_path = config_dir / 'bot_config.json'
        config_data = {
            'name': self.bot_name,
            'behaviors': behaviors
        }
        
        config_path.write_text(json.dumps(config_data, indent=2))
        return config_path
    
    def generate_server_entry_point(self) -> Path:
        src_dir = self.workspace_root / 'agile_bot' / 'bots' / self.bot_name / 'src'
        src_dir.mkdir(parents=True, exist_ok=True)
        
        server_file = src_dir / f'{self.bot_name}_mcp_server.py'
        
        server_code = f'''"""
{self.bot_name.title().replace('_', ' ')} MCP Server Entry Point

Runnable MCP server for {self.bot_name} using FastMCP and base generator.
"""
from pathlib import Path
import sys

workspace_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(workspace_root))

from agile_bot.bots.base_bot.src.mcp_server_generator import MCPServerGenerator


def main():
    generator = MCPServerGenerator(
        workspace_root=workspace_root,
        bot_location='agile_bot/bots/{self.bot_name}'
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
        server_path = f'C:/dev/augmented-teams/agile_bot/bots/{self.bot_name}/src/{self.bot_name}_mcp_server.py'
        
        mcp_config = {
            'mcpServers': {
                f'{self.bot_name.replace("_", "-")}': {
                    'command': 'python',
                    'args': [server_path],
                    'cwd': 'C:/dev/augmented-teams',
                    'env': {
                        'PYTHONPATH': 'C:/dev/augmented-teams'
                    }
                }
            }
        }
        
        return mcp_config
    
    def discover_behaviors_from_folders(self) -> list:
        behaviors_dir = (
            self.workspace_root / 
            'agile_bot' / 'bots' / self.bot_name / 'behaviors'
        )
        
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
        rules_dir = self.workspace_root / '.cursor' / 'rules'
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        # Use bot-specific filename with hyphens
        bot_name_with_hyphens = self.bot_name.replace('_', '-')
        rules_file = rules_dir / f'mcp-{bot_name_with_hyphens}-awareness.mdc'
        
        # Load bot config to get behaviors
        bot_config = read_json_file(self.config_path)
        behaviors = bot_config.get('behaviors', [])
        
        # Load instructions.json for goal and behavior descriptions
        instructions_path = self.workspace_root / 'agile_bot' / 'bots' / self.bot_name / 'instructions.json'
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
