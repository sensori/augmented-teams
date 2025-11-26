import sys
import os
import re
import json
import traceback
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from mcp.server.fastmcp import FastMCP

workspace_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(workspace_root))

from agents.base.src.agent import Agent


# Constants
WINDOWS_PATH_SEPARATOR = chr(92)
BACKSLASH_REPLACEMENT = '/'
OVERRIDE_PATTERNS = [
    r"skip\s+(?:the\s+)?(?:stage|step|action|phase)",
    r"skip\s+\w+",
    r"forget\s+about\s+(?:the\s+)?(?:stage|step|action|phase|\w+)",
    r"override\s+(?:the\s+)?(?:stage|step|action|phase)",
    r"skip\s+to\s+\w+",
    r"go\s+directly\s+to",
    r"jump\s+to",
]


class ProjectAreaRequired(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Project area required: {message}")


class ResponseFormatter:
    """Handles consistent JSON response formatting."""
    
    @staticmethod
    def success(data: Dict[str, Any]) -> str:
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    @staticmethod
    def error(error_type: str, message: str, **kwargs) -> str:
        response = {
            "error": error_type,
            "message": message
        }
        response.update(kwargs)
        return json.dumps(response, indent=2, ensure_ascii=False)
    
    @staticmethod
    def project_area_required(message: str = "Project area must be specified. Please provide the project location path.") -> str:
        return ResponseFormatter.error("Project area required", message)
    
    @staticmethod
    def attribute_error(error: AttributeError, agent_name: str, hint: Optional[str] = None) -> str:
        response = {
            "error": f"AttributeError: {str(error)}",
            "traceback": traceback.format_exc(),
            "agent_name": agent_name
        }
        if hint:
            response["hint"] = hint
        return json.dumps(response, indent=2)
    
    @staticmethod
    def unexpected_error(error: Exception, agent_name: str) -> str:
        return json.dumps({
            "error": f"Unexpected error: {str(error)}",
            "traceback": traceback.format_exc(),
            "agent_name": agent_name
        }, indent=2)


class ProjectAreaValidator:
    """Validates project area requirements."""
    
    @staticmethod
    def check(agent: Agent) -> None:
        if not agent.project_area or agent.project_area == str(Path.cwd()):
            raise ProjectAreaRequired("Project area must be specified. Please provide the project location path.")


class AgentStateManager:
    """Manages agent initialization and state synchronization."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self._agent_instance: Optional[Agent] = None
    
    def get_agent(self) -> Agent:
        """Get agent instance - discovers project area from state files if available.
        
        Matches story: "When AgentStateManager receives request for Agent instance, 
        then AgentStateManager checks if Agent instance already exists in cache, 
        and if not found creates new Agent instance"
        
        Matches story: "When AgentStateManager creates new Agent instance, 
        then AgentStateManager instantiates Agent with agent_name and optional 
        project_area parameter (may be None if not explicitly provided)"
        
        Handles all initialization errors and formats them for user presentation.
        """
        # Check if cached agent's project area matches discovered project area
        # If not, invalidate cache and re-initialize
        discovered_project_area = self._discover_project_area_from_state()
        
        if self._agent_instance is not None:
            # Check if project area has changed
            current_project_area = self._agent_instance.project_area
            if discovered_project_area and current_project_area:
                # Resolve both paths to compare
                current_path = Path(current_project_area).resolve()
                discovered_path = Path(discovered_project_area).resolve()
                if current_path != discovered_path:
                    # Project area changed - invalidate cache
                    self._agent_instance = None
            elif discovered_project_area and not current_project_area:
                # Project area was discovered but agent doesn't have one - invalidate
                self._agent_instance = None
            elif not discovered_project_area and current_project_area:
                # Project area was lost - invalidate
                self._agent_instance = None
        
        if self._agent_instance is None:
            # Try to discover project_area from state files
            if discovered_project_area is None:
                discovered_project_area = self._discover_project_area_from_state()
            
            # Create agent with discovered project_area (or None if not found)
            # Agent will then check for confirmation via check_project_area_confirmation()
            try:
                agent = Agent(agent_name=self.agent_name, project_area=discovered_project_area)
                self._agent_instance = agent
                self._sync_workflow()
            except FileNotFoundError as e:
                # Missing config file
                error_path = str(e).split("'")[1] if "'" in str(e) else str(e)
                if "base" in error_path.lower() or "agent.json" in error_path:
                    if "base" in error_path.lower():
                        raise RuntimeError(
                            f"Error: Could not load base agent configuration from {error_path}: File not found"
                        )
                    else:
                        agent_name_display = self.agent_name.replace('-', ' ').title()
                        raise RuntimeError(
                            f"Error: Could not load {agent_name_display} Agent configuration from {error_path}: File not found"
                        )
                raise RuntimeError(f"Error: File not found: {error_path}")
            except json.JSONDecodeError as e:
                # Corrupted JSON config
                error_path = getattr(e, 'filename', 'configuration file')
                line_info = f" at line {e.lineno}" if hasattr(e, 'lineno') else ""
                raise RuntimeError(
                    f"Error: Could not parse agent configuration from {error_path}: Invalid JSON syntax{line_info}"
                )
            except ValueError as e:
                # Invalid agent_name or other validation errors
                error_msg = str(e)
                if "not found" in error_msg.lower() or "invalid" in error_msg.lower():
                    # Try to get available agents
                    agents_dir = Path(__file__).parent.parent.parent
                    available_agents = []
                    if agents_dir.exists():
                        for agent_dir in agents_dir.iterdir():
                            if agent_dir.is_dir() and (agent_dir / "agent.json").exists():
                                available_agents.append(agent_dir.name)
                    
                    if available_agents:
                        agents_list = ", ".join(available_agents)
                        raise RuntimeError(
                            f"Error: Agent '{self.agent_name}' not found. Available agents: {agents_list}"
                        )
                    raise RuntimeError(f"Error: {error_msg}")
                raise RuntimeError(f"Error: {error_msg}")
            except Exception as e:
                # Any other initialization error
                raise RuntimeError(
                    f"Error: Failed to initialize agent '{self.agent_name}': {str(e)}"
                )
        
        return self._agent_instance
    
    def _discover_project_area_from_state(self) -> Optional[str]:
        """Discover project_area from agent_state.json files.
        
        Matches story: "When Agent initializes without explicit project_area, 
        then Agent calls _determine_activity_area() which searches for agent_state.json in: 
        1) project_area/docs/agent_state.json (if project_area provided), 
        2) current_dir/docs/agent_state.json, 
        3) subdirectories up to 5 levels deep using pattern '*/' * depth + 'docs/agent_state.json'"
        
        Search order matches Project._load_project_area_from_state():
        1. current_dir/docs/agent_state.json
        2. subdirectories up to 5 levels deep
        """
        if not self.agent_name:
            return None
        
        workspace_root = Path(__file__).parent.parent.parent.parent.resolve()
        
        # Try to find agent_state.json in current dir - check activity folder
        current_dir = Path.cwd().resolve()
        activity_path = current_dir / "docs" / "activity" / self.agent_name.lower() / "agent_state.json"
        if activity_path.exists():
            loaded_area = self._load_project_area_from_file(activity_path)
            if loaded_area:
                return loaded_area
        
        # Try to find in subdirectories (up to 5 levels deep) - check activity folders
        max_depth = 5
        for depth in range(max_depth + 1):
            pattern = "*/" * depth + "docs/activity/*/agent_state.json"
            for state_file in workspace_root.glob(pattern):
                loaded_area = self._load_project_area_from_file(state_file)
                if loaded_area:
                    return loaded_area
        
        return None
    
    def _load_project_area_from_file(self, state_file: Path) -> Optional[str]:
        """Load project_area from a specific agent_state.json file"""
        if not self.agent_name:
            return None
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                persisted_area = state.get("project_area")
                agent_name = state.get("agent_name")
                if persisted_area and agent_name == self.agent_name:
                    return str(Path(persisted_area).resolve())
        except (json.JSONDecodeError, IOError, OSError):
            pass
        
        return None
    
    def create_agent_with_project_area(self, project_area: str) -> Agent:
        """Create agent instance with project area - handles all initialization errors."""
        try:
            agent = Agent(agent_name=self.agent_name, project_area=project_area)
            self._agent_instance = agent
            self._sync_workflow()
            return agent
        except FileNotFoundError as e:
            # Missing config file
            error_path = str(e).split("'")[1] if "'" in str(e) else str(e)
            if "base" in error_path.lower() or "agent.json" in error_path:
                if "base" in error_path.lower():
                    raise RuntimeError(
                        f"Error: Could not load base agent configuration from {error_path}: File not found"
                    )
                else:
                    agent_name_display = self.agent_name.replace('-', ' ').title()
                    raise RuntimeError(
                        f"Error: Could not load {agent_name_display} Agent configuration from {error_path}: File not found"
                    )
            raise RuntimeError(f"Error: File not found: {error_path}")
        except json.JSONDecodeError as e:
            # Corrupted JSON config
            error_path = getattr(e, 'filename', 'configuration file')
            line_info = f" at line {e.lineno}" if hasattr(e, 'lineno') else ""
            raise RuntimeError(
                f"Error: Could not parse agent configuration from {error_path}: Invalid JSON syntax{line_info}"
            )
        except ValueError as e:
            # Invalid agent_name or other validation errors
            error_msg = str(e)
            if "not found" in error_msg.lower() or "invalid" in error_msg.lower():
                # Try to get available agents
                agents_dir = Path(__file__).parent.parent.parent
                available_agents = []
                if agents_dir.exists():
                    for agent_dir in agents_dir.iterdir():
                        if agent_dir.is_dir() and (agent_dir / "agent.json").exists():
                            available_agents.append(agent_dir.name)
                
                if available_agents:
                    agents_list = ", ".join(available_agents)
                    raise RuntimeError(
                        f"Error: Agent '{self.agent_name}' not found. Available agents: {agents_list}"
                    )
                raise RuntimeError(f"Error: {error_msg}")
            raise RuntimeError(f"Error: {error_msg}")
        except Exception as e:
            # Any other initialization error
            raise RuntimeError(
                f"Error: Failed to initialize agent '{self.agent_name}': {str(e)}"
            )
    
    def _sync_workflow(self) -> None:
        """Synchronize workflow between agent and project."""
        if not self._agent_instance.project:
            return
        
        if not hasattr(self._agent_instance.project, 'workflow'):
            raise RuntimeError("Project.workflow attribute missing after initialization - this is a bug")
        
        if hasattr(self._agent_instance, 'workflow') and self._agent_instance.workflow:
            if self._agent_instance.project.workflow is not self._agent_instance.workflow:
                self._agent_instance.project.workflow = self._agent_instance.workflow
    
    def set_agent(self, agent: Agent) -> None:
        self._agent_instance = agent
        self.agent_name = agent.agent_name
    
    def reset(self) -> None:
        self._agent_instance = None


class PathExtractor:
    """Extracts project paths from user input."""
    
    @staticmethod
    def extract(user_input: str) -> Optional[str]:
        user_lower = user_input.lower()
        
        if not PathExtractor._is_project_location_mentioned(user_lower):
            return None
        
        path_patterns = [
            r"(?:project\s+)?location[:\s]+([a-zA-Z]:[\\/][^\s]+)",
            r"to\s+([a-zA-Z]:[\\/][^\s]+)",
            r"to\s+([/][^\s]+)",
            r"location\s+to\s+([^\s]+)",
            r"project\s+location\s+to\s+([^\s]+)",
            r"moved.*to\s+([^\s]+)",
            r"(?:root\s+of\s+repo|repo)\s+([a-zA-Z0-9_\\/-]+)",
            r"in\s+root.*?([a-zA-Z0-9_\\/-]+)",
            r"to\s+([a-zA-Z0-9_-]+)",
        ]
        
        for pattern in path_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                path = match.group(1).strip()
                if path:
                    return PathExtractor._resolve_path(path)
        
        return None
    
    @staticmethod
    def _is_project_location_mentioned(user_lower: str) -> bool:
        return any([
            "moved" in user_lower and "project" in user_lower,
            "move" in user_lower and "project" in user_lower,
            "project" in user_lower and "location" in user_lower,
            "update" in user_lower and "project" in user_lower,
            "change" in user_lower and "project" in user_lower,
            "set" in user_lower and "project" in user_lower,
            "put" in user_lower and ("root" in user_lower or "repo" in user_lower),
            bool(re.search(r"in\s+root", user_lower)),
        ])
    
    @staticmethod
    def _resolve_path(path: str) -> str:
        if os.path.isabs(path) or path.startswith(('\\', '/')):
            return str(Path(path).resolve())
        full_path = workspace_root / path
        return str(full_path.resolve())


class OverrideDetector:
    """Detects override intent from user input."""
    
    @staticmethod
    def detect(user_input: str) -> bool:
        user_lower = user_input.lower()
        return any(re.search(pattern, user_lower) for pattern in OVERRIDE_PATTERNS)


class InstructionsFileWriter:
    """Handles writing instructions to files in verbose mode."""
    
    @staticmethod
    def write_if_verbose(agent: Agent, instructions: Any) -> None:
        if not getattr(agent, 'verbose_mode', False):
            return
        
        try:
            instruction_text = InstructionsFileWriter._extract_instruction_text(instructions)
            InstructionsFileWriter._write_to_file(agent, instruction_text)
        except Exception:
            pass
    
    @staticmethod
    def _extract_instruction_text(instructions: Any) -> str:
        if isinstance(instructions, dict):
            instruction_text = instructions.get("instructions", "")
            if not instruction_text:
                instruction_text = json.dumps(instructions, indent=2, ensure_ascii=False)
            return instruction_text
        return str(instructions)
    
    @staticmethod
    def _write_to_file(agent: Agent, instruction_text: str) -> None:
        from datetime import datetime
        project_path = Path(agent.project_area) if agent.project_area else Path.cwd()
        instructions_log_dir = project_path / "docs" / "instructions_log"
        instructions_log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        instructions_file = instructions_log_dir / f"instructions_{timestamp}.txt"
        instructions_file.write_text(instruction_text, encoding='utf-8')


class FileURLFormatter:
    """Formats file paths as URLs for markdown links."""
    
    @staticmethod
    def format(path: Path) -> str:
        if os.name == 'nt':
            return f"file:///{str(path).replace(WINDOWS_PATH_SEPARATOR, BACKSLASH_REPLACEMENT)}"
        return f"file://{path}"


class ToolRegistry:
    """Registers MCP tools organized by category."""
    
    def __init__(self, mcp: FastMCP, server: 'AgentMCPServer'):
        self.mcp = mcp
        self.server = server
    
    def register_all(self) -> None:
        """Register all tool categories."""
        self._register_state_tools()
        self._register_navigation_tools()
        self._register_instruction_tools()
        self._register_storage_tools()
        self._register_query_tools()
    
    def _register_state_tools(self) -> None:
        """Register state management tools."""
        
        @self.mcp.tool()
        def agent_get_state() -> str:
            return self.server._handle_tool_call(
                self.server._get_state_impl,
                handle_project_area=False
            )
        
        @self.mcp.tool()
        def agent_list_behaviors() -> str:
            return self.server._handle_tool_call(
                self.server._list_behaviors_impl
            )
    
    def _register_navigation_tools(self) -> None:
        """Register workflow navigation tools."""
        
        @self.mcp.tool()
        def agent_move_to_behavior(behavior_name: str) -> str:
            return self.server._handle_tool_call(
                lambda: self.server._move_to_behavior_impl(behavior_name)
            )
        
        def agent_move_to_action(action_name: str, override_mandatory: bool = False, user_input: str = "") -> str:
            return self.server._handle_tool_call(
                lambda: self.server._move_to_action_impl(action_name, override_mandatory, user_input)
            )
        
        try:
            agent_move_to_action.__doc__ = self.server._build_move_to_action_description()
        except Exception:
            pass
        
        self.mcp.tool()(agent_move_to_action)
        
        @self.mcp.tool()
        def agent_next_action(
            user_input: str = "",
            override_mandatory: bool = False,
            skip_to_action: str = ""
        ) -> str:
            return self.server._handle_tool_call(
                lambda: self.server._next_action_impl(user_input, override_mandatory, skip_to_action)
            )
        
        @self.mcp.tool()
        def agent_next_behavior(override_mandatory: bool = False, user_input: str = "") -> str:
            return self.server._handle_tool_call(
                lambda: self.server._next_behavior_impl(override_mandatory, user_input)
            )
    
    def _register_instruction_tools(self) -> None:
        """Register instruction retrieval tools."""
        
        @self.mcp.tool()
        def agent_get_instructions(user_input: str = "") -> str:
            return self.server._handle_tool_call(
                lambda: self.server._get_instructions_impl(user_input),
                handle_project_area=False
            )
        
        @self.mcp.tool()
        def agent_get_action_instructions(
            behavior_name: str,
            action_name: str
        ) -> str:
            return self.server._handle_tool_call(
                lambda: self.server._get_action_instructions_impl(behavior_name, action_name)
            )
    
    def _register_storage_tools(self) -> None:
        """Register content storage tools."""
        
        @self.mcp.tool()
        def agent_store_clarification(
            key_questions_answered: Dict[str, Any],
            evidence_provided: Dict[str, Any],
            additional_questions_answered: Dict[str, Any]
        ) -> str:
            return self.server._handle_tool_call(
                lambda: self.server._store_clarification_impl(
                    key_questions_answered, evidence_provided, additional_questions_answered
                )
            )
        
        @self.mcp.tool()
        def agent_store_planning(
            decisions_made: Dict[str, Any],
            assumptions_made: Dict[str, Any]
        ) -> str:
            return self.server._handle_tool_call(
                lambda: self.server._store_planning_impl(decisions_made, assumptions_made)
            )
        
        @self.mcp.tool()
        def agent_store_action_output(
            action_name: str = "",
            kwargs: Dict[str, Any] = {}
        ) -> str:
            return self.server._handle_tool_call(
                lambda: self.server._store_action_output_impl(action_name, kwargs)
            )
    
    def _register_query_tools(self) -> None:
        """Register query/retrieval tools."""
        
        @self.mcp.tool()
        def agent_get_activity_log() -> str:
            return self.server._handle_tool_call(
                lambda: self.server._get_activity_log_impl()
            )
        
        @self.mcp.tool()
        def agent_get_traceability_links() -> str:
            return self.server._handle_tool_call(
                lambda: self.server._get_traceability_links_impl()
            )
        
        @self.mcp.tool()
        def agent_get_content(
            behavior_name: str = ""
        ) -> str:
            return self.server._handle_tool_call(
                lambda: self.server._get_content_impl(behavior_name)
            )
        
        @self.mcp.tool()
        def agent_set_project_area(project_area: str) -> str:
            return self.server._handle_tool_call(
                lambda: self.server._set_project_area_impl(project_area),
                handle_project_area=False
            )


class AgentMCPServer:
    """MCP server for agent workflow management."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.state_manager = AgentStateManager(agent_name)
        self.mcp = FastMCP(f"agent-{agent_name}")
        self.tool_registry = ToolRegistry(self.mcp, self)
        self.tool_registry.register_all()
    
    def _get_agent(self) -> Agent:
        return self.state_manager.get_agent()
    
    def _check_project_area_required(self) -> None:
        agent = self._get_agent()
        ProjectAreaValidator.check(agent)
    
    def _handle_tool_call(
        self,
        tool_impl: Callable[[], str],
        handle_project_area: bool = True
    ) -> str:
        """Centralized error handling wrapper for tool calls.
        
        Handles all exceptions and formats them for user presentation.
        """
        try:
            if handle_project_area:
                self._check_project_area_required()
            return tool_impl()
        except ProjectAreaRequired as e:
            return ResponseFormatter.project_area_required(str(e))
        except RuntimeError as e:
            # Agent initialization errors, project errors, etc.
            return ResponseFormatter.error("RuntimeError", str(e))
        except FileNotFoundError as e:
            error_path = str(e).split("'")[1] if "'" in str(e) else str(e)
            return ResponseFormatter.error(
                "FileNotFoundError",
                f"Error: File not found: {error_path}"
            )
        except PermissionError as e:
            return ResponseFormatter.error(
                "PermissionError",
                f"Error: Permission denied: {str(e)}"
            )
        except OSError as e:
            if e.errno == 13:  # Permission denied
                return ResponseFormatter.error(
                    "PermissionError",
                    f"Error: Permission denied: {str(e)}"
                )
            return ResponseFormatter.error(
                "OSError",
                f"Error: System error: {str(e)}"
            )
        except json.JSONDecodeError as e:
            error_path = getattr(e, 'filename', 'configuration file')
            line_info = f" at line {e.lineno}" if hasattr(e, 'lineno') else ""
            return ResponseFormatter.error(
                "JSONDecodeError",
                f"Error: Invalid JSON in {error_path}{line_info}: {str(e)}"
            )
        except ValueError as e:
            return ResponseFormatter.error(
                "ValueError",
                f"Error: Invalid value: {str(e)}"
            )
        except AttributeError as e:
            return ResponseFormatter.attribute_error(e, self.agent_name)
        except Exception as e:
            return ResponseFormatter.unexpected_error(e, self.agent_name)
    
    def _get_state_impl(self) -> str:
        """Implementation of agent_get_state tool.
        
        Handles all exceptions and formats them for user presentation.
        """
        try:
            agent = self._get_agent()
        except ProjectAreaRequired as e:
            # Project area not set - return confirmation request
            return ResponseFormatter.success({
                "needs_confirmation": True,
                "error": "Project area required",
                "message": str(e)
            })
        except RuntimeError as e:
            # Agent initialization errors
            return ResponseFormatter.error("AgentInitializationError", str(e))
        except Exception as e:
            return ResponseFormatter.error("UnexpectedError", f"Error getting agent state: {str(e)}")
        
        # Force reload project area from persisted state if it seems wrong
        try:
            if agent.project_area and Path(agent.project_area).resolve() != Path(agent.project._path_manager.project_area).resolve():
                # Project area mismatch - reload from persisted state
                persisted_area = agent.project._load_project_area()
                if persisted_area:
                    agent.project.update_project_area(persisted_area, agent_instance=agent)
        except Exception:
            # If reload fails, continue with current state
            pass
        
        if not hasattr(agent, 'workflow') or agent.workflow is None:
            return ResponseFormatter.success({
                "agent_name": agent.agent_name,
                "current_behavior": None,
                "current_action": None,
                "project_area": agent.project_area,
                "error": "Workflow not initialized"
            })
        
        self._sync_project_workflow(agent)
        
        # Check if project area confirmation is needed
        try:
            confirmation_data = agent.check_project_area_confirmation()
            if confirmation_data and confirmation_data.get("needs_confirmation"):
                return ResponseFormatter.success({
                    "needs_confirmation": True,
                    "message": confirmation_data.get("message", ""),
                    "suggested_project_area": confirmation_data.get("suggested_project_area", "")
                })
        except Exception:
            # If confirmation check fails, continue with state return
            pass
        
        return ResponseFormatter.success({
            "agent_name": agent.agent_name,
            "current_behavior": agent.current_behavior.name if agent.current_behavior else None,
            "current_action": agent.workflow.current_action.name if agent.workflow.current_action else None,
            "project_area": agent.project_area
        })
    
    def _sync_project_workflow(self, agent: Agent) -> None:
        """Synchronize project workflow attribute."""
        if not hasattr(agent, 'project') or not agent.project:
            return
        
        try:
            workflow = agent.project.workflow
            if workflow is None and hasattr(agent, 'workflow') and agent.workflow:
                agent.project.workflow = agent.workflow
        except AttributeError:
            if hasattr(agent, 'workflow') and agent.workflow:
                agent.project.workflow = agent.workflow
            else:
                agent.project.workflow = None
    
    def _list_behaviors_impl(self) -> str:
        """Implementation of agent_list_behaviors tool."""
        agent = self._get_agent()
        self._sync_project_workflow(agent)
        
        behaviors_info = {}
        for behavior_name, behavior in agent.behaviors.items():
            behaviors_info[behavior_name] = {
                "order": behavior.order,
                "actions": [action.name for action in behavior.actions.actions]
            }
        return ResponseFormatter.success(behaviors_info)
    
    def _move_to_behavior_impl(self, behavior_name: str) -> str:
        """Implementation of agent_move_to_behavior tool."""
        agent = self._get_agent()
        
        if behavior_name not in agent.behaviors:
            return f"Error: Behavior '{behavior_name}' not found"
        
        agent.workflow.start(behavior_name)
        return f"Moved to behavior: {behavior_name}"
    
    def _move_to_action_impl(self, action_name: str, override_mandatory: bool, user_input: str) -> str:
        """Implementation of agent_move_to_action tool."""
        if user_input and OverrideDetector.detect(user_input):
            override_mandatory = True
        
        agent = self._get_agent()
        
        try:
            action = agent.workflow.move_to_action(action_name, force=override_mandatory)
            if not action:
                return f"Error: Action '{action_name}' not found in current behavior"
            
            if override_mandatory:
                return f"Override: Moved to action: {action_name}"
            return f"Moved to action: {action_name}"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def _next_action_impl(self, user_input: str, override_mandatory: bool, skip_to_action: str) -> str:
        """Implementation of agent_next_action tool."""
        if user_input and OverrideDetector.detect(user_input):
            override_mandatory = True
        
        agent = self._get_agent()
        
        try:
            if skip_to_action:
                return self._handle_skip_to_action(agent, skip_to_action, override_mandatory)
            
            action = self._get_next_action(agent, override_mandatory)
            if not action:
                return "No next action available"
            
            prefix = "Override: " if override_mandatory else ""
            return f"{prefix}Moved to next action: {action.name}"
        except ValueError as e:
            return self._format_workflow_error(e)
    
    def _handle_skip_to_action(self, agent: Agent, skip_to_action: str, override_mandatory: bool) -> str:
        """Handle skip_to_action parameter."""
        if not override_mandatory:
            return "Error: Cannot skip to action without override_mandatory=True. Use explicit override to skip stages."
        
        behavior = agent.workflow.current_behavior
        if not behavior:
            return "Error: No current behavior"
        
        action = behavior.actions.move_to_action(skip_to_action, force=True)
        if not action:
            return f"Error: Action '{skip_to_action}' not found"
        
        return f"Override: Moved directly to action: {action.name}"
    
    def _get_next_action(self, agent: Agent, override_mandatory: bool):
        """Get next action with optional override."""
        if override_mandatory:
            action = agent.workflow.next_action()
            if not action:
                behavior = agent.workflow.current_behavior
                if behavior:
                    action = behavior.actions.next_action(force=True)
            return action
        return agent.workflow.next_action()
    
    def _format_workflow_error(self, error: ValueError) -> str:
        """Format workflow-related errors."""
        error_msg = str(error)
        if "mandatory" in error_msg.lower() and "force=True" not in error_msg:
            return f"Error: {error_msg}. Use override_mandatory=True or force=True to override."
        return f"Error: {error_msg}"
    
    def _next_behavior_impl(self, override_mandatory: bool, user_input: str) -> str:
        """Implementation of agent_next_behavior tool."""
        if user_input and OverrideDetector.detect(user_input):
            override_mandatory = True
        
        agent = self._get_agent()
        
        try:
            next_behavior_name = agent.workflow.next_behavior(force=override_mandatory)
            if not next_behavior_name:
                return "No next behavior available"
            
            prefix = "Override: " if override_mandatory else ""
            return f"{prefix}Moved to next behavior: {next_behavior_name}"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def _get_instructions_impl(self, user_input: str) -> str:
        """Implementation of agent_get_instructions tool."""
        agent = self._get_agent()
        
        if not hasattr(agent, 'workflow') or agent.workflow is None:
            return ResponseFormatter.error(
                "Workflow not initialized",
                "Workflow not initialized. Agent may still be initializing.",
                agent_name=agent.agent_name
            )
        
        if not agent.workflow.current_action:
            return "No current action"
        
        instructions = agent.instructions
        verbose_mode = getattr(agent, 'verbose_mode', False)
        
        InstructionsFileWriter.write_if_verbose(agent, instructions)
        
        return self._format_instructions_response(instructions, verbose_mode)
    
    def _format_instructions_response(self, instructions: Any, verbose_mode: bool) -> str:
        """Format instructions response consistently."""
        if verbose_mode:
            if isinstance(instructions, dict):
                instructions["verbose_mode"] = True
                return ResponseFormatter.success(instructions)
            return ResponseFormatter.success({
                "instructions": instructions,
                "verbose_mode": True
            })
        
        if isinstance(instructions, dict):
            return ResponseFormatter.success(instructions)
        return instructions
    
    def _get_action_instructions_impl(self, behavior_name: str, action_name: str) -> str:
        """Implementation of agent_get_action_instructions tool."""
        agent = self._get_agent()
        
        if behavior_name not in agent.behaviors:
            return f"Error: Behavior '{behavior_name}' not found"
        
        behavior = agent.behaviors[behavior_name]
        action = behavior.actions.move_to_action(action_name, force=True)
        if not action:
            return f"Error: Action '{action_name}' not found in behavior '{behavior_name}'"
        
        instructions = action.instructions
        if isinstance(instructions, dict):
            return ResponseFormatter.success(instructions)
        return instructions
    
    def _prepare_store_context(self) -> tuple[Agent, Dict[str, Any]]:
        """Prepare context for store operations."""
        agent = self._get_agent()
        return agent, {}
    
    def _format_store_result(self, saved_paths: dict, action_name: str) -> str:
        """Format store operation results with file links."""
        result_msg = f"Stored output for action: {action_name}"
        links = self._extract_file_links(saved_paths)
        
        if links:
            result_msg += "\n\n**Saved files:**\n" + "\n".join(f"- {link}" for link in links)
        
        return result_msg
    
    def _extract_file_links(self, saved_paths: dict) -> list[str]:
        """Extract file links from saved paths."""
        links = []
        if not isinstance(saved_paths, dict):
            return links
        
        link_mappings = [
            ("clarification_path", "clarification.json"),
            ("planning_path", "planning.json"),
            ("structured_path", "structured.json")
        ]
        
        for key, link_name in link_mappings:
            if key in saved_paths:
                path = Path(saved_paths[key])
                file_url = FileURLFormatter.format(path)
                links.append(f"[{link_name}]({file_url})")
        
        if "rendered_paths" in saved_paths:
            rendered_paths = saved_paths["rendered_paths"]
            if isinstance(rendered_paths, dict):
                for name, path in rendered_paths.items():
                    file_url = FileURLFormatter.format(Path(path))
                    links.append(f"[{name}]({file_url})")
        
        return links
    
    def _store_clarification_impl(
        self,
        key_questions_answered: Dict[str, Any],
        evidence_provided: Dict[str, Any],
        additional_questions_answered: Dict[str, Any]
    ) -> str:
        """Implementation of agent_store_clarification tool."""
        agent, parsed_kwargs = self._prepare_store_context()
        
        action = agent.workflow.current_action
        if not action or action.name != "clarification":
            action = agent.workflow.move_to_action("clarification", force=True)
            if not action:
                return "Error: Clarification action not found"
        
        parsed_kwargs["key_questions_answered"] = key_questions_answered
        parsed_kwargs["evidence_provided"] = evidence_provided
        if additional_questions_answered:
            parsed_kwargs["additional_questions_answered"] = additional_questions_answered
        
        saved_paths = agent.store(**parsed_kwargs)
        return self._format_store_result(saved_paths, action.name)
    
    def _store_planning_impl(
        self,
        decisions_made: Dict[str, Any],
        assumptions_made: Dict[str, Any]
    ) -> str:
        """Implementation of agent_store_planning tool."""
        agent, parsed_kwargs = self._prepare_store_context()
        
        action = agent.workflow.current_action
        if not action or action.name != "planning":
            action = agent.workflow.move_to_action("planning", force=True)
            if not action:
                return "Error: Planning action not found"
        
        parsed_kwargs["decisions_made"] = decisions_made
        parsed_kwargs["assumptions_made"] = assumptions_made
        saved_paths = agent.store(**parsed_kwargs)
        return self._format_store_result(saved_paths, action.name)
    
    def _store_action_output_impl(self, action_name: str, kwargs: Dict[str, Any]) -> str:
        """Implementation of agent_store_action_output tool."""
        agent, parsed_kwargs = self._prepare_store_context()
        
        if action_name:
            action = agent.workflow.move_to_action(action_name, force=True)
            if not action:
                return f"Error: Action '{action_name}' not found in current behavior"
        else:
            action = agent.workflow.current_action
            if not action:
                return "Error: No current action"
        
        if kwargs:
            parsed_kwargs.update(kwargs)
        
        saved_paths = agent.store(**parsed_kwargs)
        return self._format_store_result(saved_paths, action.name)
    
    def _get_activity_log_impl(self) -> str:
        """Implementation of agent_get_activity_log tool."""
        agent = self._get_agent()
        return ResponseFormatter.success(agent.activity_log)
    
    def _get_traceability_links_impl(self) -> str:
        """Implementation of agent_get_traceability_links tool."""
        agent = self._get_agent()
        return ResponseFormatter.success(agent.traceability_links)
    
    def _get_content_impl(self, behavior_name: str) -> str:
        """Implementation of agent_get_content tool."""
        agent = self._get_agent()
        
        if behavior_name:
            if behavior_name not in agent.behaviors:
                return f"Error: Behavior '{behavior_name}' not found"
            behavior = agent.behaviors[behavior_name]
        else:
            behavior = agent.current_behavior
            if not behavior:
                return "Error: No current behavior"
        
        return ResponseFormatter.success({
            "structured": behavior.content.structured,
            "rendered": behavior.content.rendered
        })
    
    def _set_project_area_impl(self, project_area: str) -> str:
        """Implementation of agent_set_project_area tool.
        
        Handles all failure conditions from Initialize Project scenarios:
        - Invalid folder names (invalid characters, empty, too long)
        - File write permission errors
        - Directory creation errors (read-only filesystem)
        - Conflicting state files
        """
        try:
            # Validate project area path
            try:
                resolved_area = str(Path(project_area).resolve())
            except (OSError, ValueError) as e:
                return ResponseFormatter.error(
                    "InvalidProjectArea",
                    f"Error: Invalid project area path '{project_area}': {str(e)}"
                )
            
            # Check for invalid folder name conditions
            project_path = Path(resolved_area)
            folder_name = project_path.name if project_path.name else project_path.parent.name
            
            # Check for invalid characters
            invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
            if any(char in folder_name for char in invalid_chars):
                return ResponseFormatter.error(
                    "InvalidFolderName",
                    f"Error: Project area folder name contains invalid characters: {folder_name}\n"
                    f"Invalid characters: {', '.join(invalid_chars)}\n"
                    f"Please provide a valid project area path."
                )
            
            # Check for empty folder name
            if not folder_name or folder_name.strip() == '':
                return ResponseFormatter.error(
                    "InvalidFolderName",
                    f"Error: Project area folder name cannot be empty.\n"
                    f"Please provide a valid project area path."
                )
            
            # Check for too long path (Windows limit is ~260 chars, but we'll be conservative)
            if len(resolved_area) > 200:
                return ResponseFormatter.error(
                    "PathTooLong",
                    f"Error: Project area path is too long ({len(resolved_area)} characters).\n"
                    f"Maximum recommended length is 200 characters.\n"
                    f"Please provide a shorter path."
                )
            
            # Check for conflicting state file - check activity folder
            activity_path = project_path / "docs" / "activity" / self.agent_name.lower() / "agent_state.json"
            if activity_path.exists():
                try:
                    with open(activity_path, 'r', encoding='utf-8') as f:
                        existing_state = json.load(f)
                        existing_agent = existing_state.get("agent_name")
                        if existing_agent and existing_agent != self.agent_name:
                            return ResponseFormatter.error(
                                "ConflictingState",
                                f"Error: Project area already contains agent_state.json for different agent '{existing_agent}'.\n"
                                f"Current agent: '{self.agent_name}'\n"
                                f"Please choose a different project area or resolve the conflict."
                            )
                except (json.JSONDecodeError, IOError, OSError):
                    # If we can't read it, we'll try to overwrite it
                    pass
            
            # Create agent instance - handles config loading errors
            try:
                temp_agent = self.state_manager.create_agent_with_project_area(resolved_area)
            except RuntimeError as e:
                # Agent initialization errors (missing config, JSON errors, etc.)
                return ResponseFormatter.error("AgentInitializationError", str(e))
            
            # Update project area - handles save and directory creation errors
            try:
                temp_agent.project.update_project_area(resolved_area, agent_instance=temp_agent)
            except PermissionError as e:
                # File write permission error
                return ResponseFormatter.error(
                    "PermissionError",
                    f"Error: Cannot save project area to {resolved_area}/docs/{{activity_area}}/agent_state.json: Permission denied.\n"
                    f"Please check file permissions or choose a different location."
                )
            except OSError as e:
                # Directory creation error (read-only filesystem, etc.)
                if e.errno == 13:  # Permission denied
                    return ResponseFormatter.error(
                        "PermissionError",
                        f"Error: Cannot create directory structure at {resolved_area}: Permission denied.\n"
                        f"Please check directory permissions or choose a different location."
                    )
                return ResponseFormatter.error(
                    "DirectoryCreationError",
                    f"Error: Cannot create directory structure at {resolved_area}: {str(e)}"
                )
            except Exception as e:
                return ResponseFormatter.error(
                    "ProjectUpdateError",
                    f"Error: Failed to update project area: {str(e)}"
                )
            
            # Now reset the state manager so next get_agent() call will create fresh agent with correct project area
            self.state_manager.reset()
            
            return ResponseFormatter.success({
                "message": f"Project area confirmed and set to: {resolved_area}",
                "project_area": resolved_area,
                "note": "This will be automatically loaded from persisted state in future calls."
            })
        except Exception as e:
            # Catch-all for any unexpected errors
            return ResponseFormatter.error(
                "SetProjectAreaError",
                f"Error: Unexpected error setting project area: {str(e)}"
            )
    
    def _build_move_to_action_description(self) -> str:
        """Build dynamic description for move_to_action tool."""
        base_desc = """Move to a specific action within current behavior.
    
    This tool navigates the workflow to the specified action, allowing you
    to jump directly to clarification, planning, build_structure, render_output,
    validate, or correct actions as needed."""
        
        try:
            agent = self._get_agent()
            all_triggers = {}
            for action_name in ["correct", "validate", "build_structure", "render_output", "clarification", "planning"]:
                if hasattr(agent, '_collect_trigger_words_for_action'):
                    triggers = agent._collect_trigger_words_for_action(action_name)
                    if triggers:
                        all_triggers[action_name] = triggers
            
            if all_triggers:
                trigger_section = "\n\nTRIGGER WORDS:\nThis tool should be called when user input contains phrases that suggest specific actions:\n"
                for action, patterns in all_triggers.items():
                    pattern_list = ", ".join([f'"{p}"' for p in patterns])
                    trigger_section += f"- For '{action}' action: {pattern_list}\n"
                trigger_section += "\nWhen you detect these phrases in user messages, automatically call this tool with the appropriate action_name."
                return base_desc + trigger_section
        except (ProjectAreaRequired, Exception):
            pass
        
        return base_desc


# Module-level initialization
_agent_name = os.getenv("AGENT_NAME") or (sys.argv[1] if len(sys.argv) > 1 else "base")
_server = AgentMCPServer(_agent_name)
mcp = _server.mcp


def get_server() -> AgentMCPServer:
    return _server


def agent_get_state() -> dict:
    """Get agent state - SIMPLIFIED: Always checks for project area confirmation on new projects.
    
    Handles all exceptions and formats them for user presentation.
    """
    try:
        agent = _server._get_agent()
    except ProjectAreaRequired as e:
        # Project area not set - return confirmation request
        return {
            "needs_confirmation": True,
            "error": "Project area required",
            "message": str(e)
        }
    except RuntimeError as e:
        # Agent initialization errors (missing config, JSON errors, etc.)
        return {
            "error": "Agent initialization failed",
            "message": str(e)
        }
    except Exception as e:
        # Any other unexpected error
        return {
            "error": "Unexpected error",
            "message": f"Error getting agent state: {str(e)}"
        }
    
    # SIMPLIFIED: Always check if project area confirmation is needed
    try:
        confirmation_data = agent.check_project_area_confirmation()
        if confirmation_data and confirmation_data.get("needs_confirmation"):
            return {
                "needs_confirmation": True,
                "message": confirmation_data.get("message", ""),
                "suggested_project_area": confirmation_data.get("suggested_project_area", "")
            }
    except Exception as e:
        # If confirmation check fails, still return state if we have agent
        pass
    
    return {
        "agent_name": agent.agent_name,
        "current_behavior": agent.current_behavior.name if agent.current_behavior else None,
        "current_action": agent.workflow.current_action.name if agent.workflow.current_action else None,
        "project_area": agent.project_area
    }


def agent_next_action(user_input: Optional[str] = None, override_mandatory: bool = False, skip_to_action: Optional[str] = None) -> str:
    agent = _server._get_agent()
    
    if user_input and OverrideDetector.detect(user_input):
        override_mandatory = True
    
    try:
        if skip_to_action:
            if not override_mandatory:
                return "Error: Cannot skip to action without override_mandatory=True. Use explicit override to skip stages."
            behavior = agent.workflow.current_behavior
            if behavior:
                action = behavior.actions.move_to_action(skip_to_action, force=True)
                if action:
                    return f"Override: Moved directly to action: {action.name}"
                return f"Error: Action '{skip_to_action}' not found"
            return "Error: No current behavior"
        
        if override_mandatory:
            behavior = agent.workflow.current_behavior
            if behavior:
                action = behavior.actions.next_action(force=True)
            else:
                action = None
        else:
            action = agent.workflow.next_action()
        
        if action:
            if override_mandatory:
                return f"Override: Moved to next action: {action.name}"
            return f"Moved to next action: {action.name}"
        return "No next action available"
    except ValueError as e:
        error_msg = str(e)
        if "mandatory" in error_msg.lower() and "force=True" not in error_msg:
            return f"Error: {error_msg}. Use override_mandatory=True or force=True to override."
        return f"Error: {error_msg}"


def agent_move_to_action(action_name: str, override_mandatory: bool = False, user_input: Optional[str] = None) -> str:
    agent = _server._get_agent()
    
    if user_input and OverrideDetector.detect(user_input):
        override_mandatory = True
    
    try:
        action = agent.workflow.move_to_action(action_name, force=override_mandatory)
        if action:
            if override_mandatory:
                return f"Override: Moved to action: {action_name}"
            return f"Moved to action: {action_name}"
        return f"Error: Action '{action_name}' not found in current behavior"
    except ValueError as e:
        return f"Error: {str(e)}"


def agent_next_behavior(override_mandatory: bool = False, user_input: Optional[str] = None) -> str:
    agent = _server._get_agent()
    
    if user_input and OverrideDetector.detect(user_input):
        override_mandatory = True
    
    try:
        next_behavior_name = agent.workflow.next_behavior(force=override_mandatory)
        if next_behavior_name:
            if override_mandatory:
                return f"Override: Moved to next behavior: {next_behavior_name}"
            return f"Moved to next behavior: {next_behavior_name}"
        return "No next behavior available"
    except ValueError as e:
        return f"Error: {str(e)}"


try:
    if _server and hasattr(_server, '_build_move_to_action_description'):
        base_desc = agent_move_to_action.__doc__
        enhanced = _server._build_move_to_action_description()
        if enhanced and enhanced != base_desc and base_desc:
            agent_move_to_action.__doc__ = enhanced
except (AttributeError, Exception):
    pass


if __name__ == "__main__":
    mcp.run()
