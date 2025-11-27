from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
import json


class Agent:

    def __init__(self, agent_name: str, project_area: Optional[str] = None):
        self.agent_name = agent_name
        self._setup_config_paths()
        # Determine activity_area from project state, not hardcoded
        activity_area = self._determine_activity_area(project_area)
        self.project = Project(activity_area=activity_area, agent_name=agent_name, project_area=project_area)
        self._load_configuration()
        self._initialize_components()

    def _setup_config_paths(self):
        self._base_config_path = Path(__file__).parent.parent / "agent.json"
        agents_dir = Path(__file__).parent.parent.parent
        agent_folder_name = self.agent_name.lower()
        self._agent_config_path = agents_dir / agent_folder_name / "agent.json"

    def _determine_activity_area(self, project_area: Optional[str] = None) -> str:
        """Determine activity_area from project state or default to agent_name.lower()
        
        Activity area format: activity/{agent_name}
        Looks for activity_area in:
        1. agent_state.json in the project_area (if provided) - checks docs/activity/{agent_name}/agent_state.json
        2. agent_state.json in current directory - checks docs/activity/{agent_name}/agent_state.json
        3. agent_state.json in subdirectories (up to 5 levels deep) - checks docs/activity/*/agent_state.json
        4. Defaults to agent_name.lower() if not found
        """
        workspace_root = Path(__file__).parent.parent.parent.parent.resolve()
        
        # First, try to load from project_area if provided
        if project_area:
            project_path = Path(project_area).resolve()
            # Check new location: docs/activity/{agent_name}/agent_state.json
            activity_path = project_path / "docs" / "activity" / self.agent_name.lower() / "agent_state.json"
            if activity_path.exists():
                try:
                    with open(activity_path, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                        if state.get("agent_name") == self.agent_name and "activity_area" in state:
                            return state["activity_area"]
                except (json.JSONDecodeError, IOError, OSError):
                    pass
        
        # Try to find agent_state.json in current dir
        current_dir = Path.cwd().resolve()
        # Check new location: docs/activity/{agent_name}/agent_state.json
        activity_path = current_dir / "docs" / "activity" / self.agent_name.lower() / "agent_state.json"
        if activity_path.exists():
            try:
                with open(activity_path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    if state.get("agent_name") == self.agent_name and "activity_area" in state:
                        return state["activity_area"]
            except (json.JSONDecodeError, IOError, OSError):
                pass
        
        # Try to find in subdirectories (up to 5 levels deep) - check activity folders
        max_depth = 5
        for depth in range(max_depth + 1):
            pattern = "*/" * depth + "docs/activity/*/agent_state.json"
            for state_file in workspace_root.glob(pattern):
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                        if state.get("agent_name") == self.agent_name and "activity_area" in state:
                            return state["activity_area"]
                except (json.JSONDecodeError, IOError, OSError):
                    pass
        
        # Default to agent_name.lower() if not found (will be used as activity/{agent_name})
        return self.agent_name.lower()

    def _initialize_components(self):
        self.workflow = self.project.workflow
        self.workflow._behaviors = self.behaviors
        self.workflow.stages = self.workflow._derive_stages_from_behaviors(self.behaviors)

        self._restore_workflow_state()

        if self._needs_project_area():
            self._initialize_without_starting()
        else:
            self._start_workflow_if_needed()

    def _restore_workflow_state(self):
        """Restore workflow state if this is an existing project"""
        if not self.workflow.workflow_state.get("current_behavior_name"):
            return

        behavior_name = self.workflow.workflow_state.get("current_behavior_name")
        if behavior_name not in self.behaviors:
            return

        self.workflow._current_stage = behavior_name
        behavior = self.behaviors[behavior_name]
        action_name = self.workflow.workflow_state.get("current_action_name")

        if not action_name or not hasattr(behavior, 'actions'):
            return

        action = behavior.actions.move_to_action(action_name, force=True)
        if action:
            self.workflow._current_action = action

    def _initialize_without_starting(self):
        """Set first stage without starting workflow"""
        if not self.workflow._current_stage:
            initial_stage = self.workflow.start_next_stage()
            if initial_stage:
                self.workflow._current_stage = initial_stage
                self.workflow._current_action = None
            else:
                self.workflow._current_stage = None
                self.workflow._current_action = None

        if not self.workflow.workflow_state.get("current_behavior_name"):
            self.workflow._workflow_state = {
                "current_behavior_name": None,
                "current_action_name": None
            }

    def _start_workflow_if_needed(self):
        """Start workflow from beginning if state wasn't restored"""
        if not self.workflow._current_stage:
            initial_stage = self.workflow.start_next_stage()
            if initial_stage:
                self.workflow.start(initial_stage)

    def _load_configuration(self):
        self._load_base_agent_config()
        self._load_agent_config()
        self._load_mcp_config()

    def _load_base_agent_config(self):
        """Load base agent config for trigger words and prompt templates"""
        if self._base_config_path.exists():
            with open(self._base_config_path, 'r', encoding='utf-8') as f:
                base_config = json.load(f)
                self._prompt_templates = base_config.get("prompt_templates", {})
                self._base_trigger_words = base_config.get("trigger_words", {})
        else:
            self._prompt_templates = {}
            self._base_trigger_words = {}

    def _load_mcp_config(self):
        """Load and process MCP configuration from agent config, substituting placeholders"""
        agent_config = getattr(self, '_agent_config', {})

        mcp_config = agent_config.get("mcp", {})

        if mcp_config:
            workspace_root = str(Path(__file__).parent.parent.parent.parent)
            mcp_config = self._substitute_mcp_placeholders(mcp_config, workspace_root)

        self.mcp_config = mcp_config

    def _substitute_mcp_placeholders(self, mcp_config: Dict[str, Any], workspace_root: str) -> Dict[str, Any]:
        """Substitute placeholders in MCP config with actual values"""
        import copy
        config = copy.deepcopy(mcp_config)

        def substitute_string(value: Any) -> Any:
            if isinstance(value, str):
                return value.replace("{agent_name}", self.agent_name).replace("{workspace_root}", workspace_root)
            elif isinstance(value, dict):
                return {k: substitute_string(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute_string(item) for item in value]
            return value

        return substitute_string(config)
    def _load_agent_config(self):
        """Load agent-specific configuration from agent.json (not base_agent.json)"""
        if self._agent_config_path.exists():
            agent_config = self._read_agent_config_file()
            self._load_config_from_dict(agent_config)
        else:
            self._load_empty_config()

    def _read_agent_config_file(self) -> Dict[str, Any]:
        """Read agent.json file from agent-specific folder"""
        with open(self._agent_config_path, 'r', encoding='utf-8') as f:
            return json.load(f)  

    def _load_config_from_dict(self, agent_config: Dict[str, Any]):
        """Load configuration from agent.json dict, including behaviors initialization"""
        rules_config = agent_config.get("rules", {})
        self.rules = Rules(rules_config)

        self._agent_config = agent_config
        self._agent_trigger_words = agent_config.get("trigger_words", {})
        self.verbose_mode = agent_config.get("verbose_mode", False)

        behaviors_config = agent_config.get("behaviors", {})
        self.behaviors = {}
        for stage_name, behavior_config in behaviors_config.items():
            behavior_config["_behavior_name"] = stage_name
            behavior_config["_agent_config_path"] = self._agent_config_path
            behavior = Behavior(behavior_config, self.rules, self.project)
            behavior._parent_agent = self
            self.behaviors[stage_name] = behavior

    def _load_empty_config(self):
        self.rules = Rules({})
        self.behaviors = {}
        self._agent_config = {}
        self._agent_trigger_words = {}

    @property
    def current_behavior(self) -> Optional["Behavior"]:
        if not self.workflow.current_stage:
            return None
        return self.behaviors.get(self.workflow.current_stage)

    @property
    def instructions(self) -> Union[str, Dict[str, Any]]:
        """Get instructions from current action"""
        if not hasattr(self, 'workflow') or self.workflow is None:
            return {
                "error": "Workflow not initialized",
                "instructions": "Agent is still initializing. Please wait a moment and try again."
            }

        if not self.project_area or self.project_area == str(Path.cwd()):
            return self._get_project_area_required_instructions()

        if not self.workflow.current_action:
            initial_stage = self.workflow.start_next_stage()
            if initial_stage:
                self.workflow.start(initial_stage)
                if self.workflow.current_action:
                    return self.workflow.current_action.instructions
            return None
        return self.workflow.current_action.instructions

    @property
    def activity_log(self) -> List[Dict[str, Any]]:
        return self.project.activity_log

    @property
    def traceability_links(self) -> List[Dict[str, Any]]:
        return self.project.traceability_links

    @property
    def current_stage(self) -> Optional[str]:
        return self.workflow.current_stage

    @property
    def tools_and_instructions(self) -> "ToolsAndInstructions":
        tools_instructions = ToolsAndInstructions()
        tools_instructions.tools = ["build_structure", "validate_schema", "transform_content"]
        return tools_instructions

    @property
    def project_area(self) -> str:
        """Get the current project_area"""
        if not self.project:
            return str(Path.cwd())
        if hasattr(self.project, 'project_area'):
            return self.project.project_area
        if hasattr(self.project, '_project_area'):
            return self.project._project_area
        return str(Path.cwd())

    def _needs_project_area(self) -> bool:
        """Check if project_area needs to be set (is missing or default)"""
        if not self.project:
            return True
        project_area = self.project_area
        if not project_area:
            return True
        return project_area == str(Path.cwd())

    def check_project_area_confirmation(self) -> Optional[Dict[str, Any]]:
        """Check if project area confirmation is needed and return confirmation data.
        
        Delegates to Project.present_project_area_to_user() to match story flow.
        """
        if not self.project:
            return None
        
        # Matches story: "Project presents determined project_area to user for confirmation"
        return self.project.present_project_area_to_user()

    def _get_project_area_required_instructions(self) -> Dict[str, Any]:
        """Load project area required instructions from base agent.json template"""
        confirmation_data = self.check_project_area_confirmation()
        if confirmation_data:
            return {"instructions": confirmation_data.get("message", "")}
        
        # Fallback if no confirmation needed (shouldn't happen)
        return {
            "instructions": "**Project Area Required**\n\nBefore starting the workflow, you must specify where project files should be saved.\n\nPlease provide the full path to the project location."
        }

    def _collect_trigger_words_for_action(self, action_name: str) -> List[str]:
        """Collect all trigger words for a specific action from all levels (base → agent → behavior → action)"""
        all_patterns = []

        all_patterns.extend(self._get_base_trigger_words(action_name))
        all_patterns.extend(self._get_agent_trigger_words(action_name))

        if self.current_behavior:
            all_patterns.extend(self.current_behavior.get_trigger_words_for_action(action_name))

        return all_patterns

    def _get_base_trigger_words(self, action_name: str) -> List[str]:
        """Get base-level trigger words for an action (Agent owns this data)"""
        base_triggers = getattr(self, '_base_trigger_words', {})
        if action_name in base_triggers:
            return base_triggers[action_name].get("patterns", [])
        return []

    def _get_agent_trigger_words(self, action_name: str) -> List[str]:
        """Get agent-level trigger words for an action (Agent owns this data)"""
        agent_triggers = getattr(self, '_agent_trigger_words', {})
        if not agent_triggers:
            return []

        if "patterns" in agent_triggers:
            return agent_triggers.get("patterns", [])
        elif action_name in agent_triggers:
            return agent_triggers[action_name].get("patterns", [])
        return []

    def deploy_mcp_config(self, target: str = "workspace") -> Dict[str, Any]:
        """
        Deploy MCP configuration to workspace or global location.

        Args:
            target: "workspace" or "global"

        Returns:
            Dict with deployment info (path, created, merged, etc.)
        """
        if not hasattr(self, 'mcp_config') or not self.mcp_config:
            return {"error": "No MCP configuration available"}

        if target == "workspace":
            return self._deploy_to_workspace()
        elif target == "global":
            return self._deploy_to_global()
        else:
            return {"error": f"Unknown target: {target}"}

    def _deploy_to_workspace(self) -> Dict[str, Any]:
        """Deploy MCP config to workspace root mcp.json file"""
        workspace_root = Path(__file__).parent.parent.parent.parent
        config_file = workspace_root / "mcp.json"
        return self._deploy_to_config_file(config_file)

    def _deploy_to_global(self) -> Dict[str, Any]:
        """Deploy MCP config to OS-level global location"""
        import platform
        import os

        if platform.system() == "Windows":
            config_dir = Path(os.getenv("APPDATA", "")) / "Cursor" / "User" / "globalStorage" / "mcp"
        elif platform.system() == "Darwin":
            config_dir = Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage" / "mcp"
        else:
            config_dir = Path.home() / ".config" / "Cursor" / "User" / "globalStorage" / "mcp"

        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "mcp.json"

        result = self._deploy_to_config_file(config_file)

        existing_servers = result.get("existing_servers", {})
        server_name = self.mcp_config["server_name"]
        preserved_count = len([name for name in existing_servers.keys() if name != server_name])
        result["preserved_servers"] = preserved_count

        return result

    def _deploy_to_config_file(self, config_file: Path) -> Dict[str, Any]:
        """Common deployment logic for MCP config"""
        existing_config = {}
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f)
            except (json.JSONDecodeError, IOError):
                existing_config = {}

        merged_config = existing_config.copy()
        if "mcpServers" not in merged_config:
            merged_config["mcpServers"] = {}

        merged_config["mcpServers"][self.mcp_config["server_name"]] = {
            "command": self.mcp_config["command"],
            "args": self.mcp_config.get("args", []),
            "cwd": self.mcp_config.get("cwd", ""),
            "env": self.mcp_config.get("env", {})
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(merged_config, f, indent=2)

        return {
            "path": str(config_file),
            "created": not existing_config,
            "merged": bool(existing_config),
            "server_name": self.mcp_config["server_name"],
            "config": merged_config,
            "existing_servers": existing_config.get("mcpServers", {})
        }

    def store(self, project_area: Optional[str] = None, **kwargs) -> Union[str, Dict[str, Any]]:
        """Store data - routes to current action's store method. Returns formatted string message with file hyperlinks."""
        if project_area is not None:
            self.project.update_project_area(project_area, agent_instance=self)
            self.project._project_area = project_area

        saved_paths = self._store_action_data(**kwargs)

        if self.workflow.current_action:
            return self._format_store_result(saved_paths, project_area)

        return saved_paths

    def _store_action_data(self, **kwargs) -> Dict[str, Any]:
        """Store data via current action's store method"""
        saved_paths = {}
        if self.workflow.current_action:
            action = self.workflow.current_action
            action_saved_paths = action.store(**kwargs)
            if isinstance(action_saved_paths, dict):
                saved_paths.update(action_saved_paths)
        return saved_paths

    def _format_store_result(self, saved_paths: Dict[str, Any], project_area: Optional[str]) -> str:
        """Format store result as string message with file hyperlinks"""
        result_msg = f"Stored output for action: {self.workflow.current_action.name}"
        if project_area is not None:
            result_msg += f"\nUpdated project location to: {project_area}"

        links = self._build_file_hyperlinks(saved_paths)
        if links:
            result_msg += "\n\n**Saved files:**\n" + "\n".join(f"- {link}" for link in links)

        return result_msg

    def _build_file_hyperlinks(self, saved_paths: Dict[str, Any]) -> List[str]:
        """Build markdown hyperlinks for saved file paths"""
        links = []

        if not isinstance(saved_paths, dict):
            return links

        for path_key, link_text in [("clarification_path", "clarification.json"), 
                                     ("planning_path", "planning.json"),
                                     ("structured_path", "structured.json")]:
            if path_key in saved_paths:
                path = saved_paths[path_key]
                file_url = self._path_to_file_url(path)
                links.append(f"[{link_text}]({file_url})")

        if "rendered_paths" in saved_paths:
            rendered_paths = saved_paths["rendered_paths"]
            if isinstance(rendered_paths, dict):
                for name, path in rendered_paths.items():
                    file_url = self._path_to_file_url(path)
                    links.append(f"[{name}]({file_url})")

        return links

    def _path_to_file_url(self, path: str) -> str:
        """Convert file path to file:// URL for proper hyperlink"""
        import os
        if os.name == 'nt':
            return f"file:///{str(path).replace(chr(92), '/')}"
        return f"file://{path}"

class BaseInstructions:
    """Base instructions loaded from guardrails config"""

    def __init__(self, base_instructions_config: Dict[str, Any]):
        """Initialize with only the base_instructions portion of guardrails config"""
        clarification_config = base_instructions_config.get("clarification", {})
        self.clarification_intro = clarification_config.get("intro", "Assess the provided context against the required questions and evidence below.")

        planning_config = base_instructions_config.get("planning", {})
        self.planning_intro = planning_config.get("intro", "Present the following assumptions and decision criteria to the user and ask for their opinion on key decisions.")

class ExampleItem:
    """Single example item with description and content"""

    def __init__(self, example_config: Dict[str, Any]):
        """Initialize with either a string (simple) or object with description/content (complex)"""
        if isinstance(example_config, str):
            self.description = ""
            self.content = example_config
        else:
            self.description = example_config.get("description", "")
            self.content = example_config.get("content", "")


class Examples:
    """Examples (do/dont patterns) - handles both simple (strings) and complex (objects) structures"""

    def __init__(self, examples_config: Dict[str, Any] = None, do: List[Any] = None, dont: List[Any] = None):
        """
        Initialize with examples config.
        Can handle:
        - Simple: do/dont as arrays of strings (agent-level)
        - Complex: do/dont as arrays of objects with description/content (behavior-level)
        """
        if examples_config:
            do_list = examples_config.get("do", [])
            dont_list = examples_config.get("dont", [])
        else:
            do_list = do or []
            dont_list = dont or []

        self.do = [ExampleItem(item) if not isinstance(item, ExampleItem) else item for item in do_list]
        self.dont = [ExampleItem(item) if not isinstance(item, ExampleItem) else item for item in dont_list]

class Rule:
    """Single rule with description and examples"""

    def __init__(self, rule_config: Dict[str, Any]):
        """Initialize with a single rule object"""
        self.description = rule_config.get("description", "")
        examples_config = rule_config.get("examples", [])

        if isinstance(examples_config, dict) and any(key in examples_config for key in ["python", "javascript", "typescript"]):
            self.examples_by_specialization = {}
            for specialization, examples_list in examples_config.items():
                if isinstance(examples_list, list) and examples_list and isinstance(examples_list[0], dict) and ("do" in examples_list[0] or "dont" in examples_list[0]):
                    self.examples_by_specialization[specialization] = []
                    for example_obj in examples_list:
                        do_item = example_obj.get("do", {})
                        dont_item = example_obj.get("dont", {})
                        self.examples_by_specialization[specialization].append({
                            "do": ExampleItem(do_item) if do_item else None,
                            "dont": ExampleItem(dont_item) if dont_item else None
                        })
                else:
                    self.examples_by_specialization[specialization] = Examples(examples_list)
            first_spec = list(self.examples_by_specialization.keys())[0] if self.examples_by_specialization else None
            self.examples = self.examples_by_specialization[first_spec] if first_spec else Examples()
        elif isinstance(examples_config, list) and examples_config and isinstance(examples_config[0], dict) and ("do" in examples_config[0] or "dont" in examples_config[0]):
            self.examples = []
            self.examples_by_specialization = None
            for example_obj in examples_config:
                do_item = example_obj.get("do", {})
                dont_item = example_obj.get("dont", {})
                self.examples.append({
                    "do": ExampleItem(do_item) if do_item else None,
                    "dont": ExampleItem(dont_item) if dont_item else None
                })
        else:
            self.examples = Examples(examples_config)
            self.examples_by_specialization = None
        self.diagnostic = rule_config.get("diagnostic", "")

    def get_examples_for_specialization(self, specialization: str):
        """Get examples for a specific specialization (python, javascript, etc.)"""
        if self.examples_by_specialization:
            spec_lower = specialization.lower()
            if spec_lower in self.examples_by_specialization:
                return self.examples_by_specialization[spec_lower]
            if spec_lower == "js" and "javascript" in self.examples_by_specialization:
                return self.examples_by_specialization["javascript"]
            if spec_lower == "ts" and "typescript" in self.examples_by_specialization:
                return self.examples_by_specialization["typescript"]
            if self.examples_by_specialization:
                return list(self.examples_by_specialization.values())[0]
        return self.examples

class Rules:
    """Agent-level or behavior-level rules - handles both single object and array"""

    def __init__(self, rules_config: Union[Dict[str, Any], List[Dict[str, Any]]]):
        """
        Initialize with rules config.
        Can handle:
        - Agent-level: single object {description, examples: {do: [...], dont: [...]}, diagnostic}
        - Behavior-level: array of rule objects [{description, examples: [{do: {...}, dont: {...}}]}, ...]
        """
        if isinstance(rules_config, list):
            self.rules = [Rule(rule_config_item) for rule_config_item in rules_config]
            if self.rules:
                self.description = self.rules[0].description
                self.examples = self.rules[0].examples
                self.diagnostic = self.rules[0].diagnostic
            else:
                self.description = ""
                self.examples = Examples()
                self.diagnostic = ""
        else:
            self.description = rules_config.get("description", "")
            examples_config = rules_config.get("examples", {})
            self.examples = Examples(examples_config)
            self.diagnostic = rules_config.get("diagnostic", "")
            self.rules = [Rule(rules_config)]

class RequiredClarification:
    """Required context (key questions and evidence)"""

    def __init__(self, required_context_config: Dict[str, Any]):
        """Initialize with only the required_context portion of guardrails config"""
        self.key_questions = required_context_config.get("key_questions", [])
        self.evidence = required_context_config.get("evidence", [])

class DecisionCriterion:
    """Single decision making criterion"""

    def __init__(self, criterion_config: Dict[str, Any]):
        """Initialize with a single decision criterion object from decision_making_criteria array"""
        self.question = criterion_config.get("question", "")
        self.outcome = criterion_config.get("outcome", "")
        self.options = criterion_config.get("options", [])

class Action:
    """Single action with name, outcomes, and output"""

    CLARIFICATION = "clarification"
    PLANNING = "planning"
    BUILD_STRUCTURE = "build_structure"
    RENDER_OUTPUT = "render_output"
    VALIDATE = "validate"
    CORRECT = "correct"

    def __init__(self, name: str, parent_behavior=None, action_config: Optional[Dict[str, Any]] = None):
        self.name = name
        self._parent_behavior = parent_behavior
        self._config = action_config or {}
        self.outcomes: Dict[str, Any] = {}
        self.output: Dict[str, Any] = {}
        self._instructions: Optional[Union[str, Dict[str, Any]]] = None

        self.trigger_words = self._config.get("trigger_words", {})

        self._get_diagnostic_map = None

    def get_trigger_words(self) -> List[str]:
        """Get trigger words for this action (Action owns this data)"""
        action_triggers = getattr(self, 'trigger_words', {})
        if action_triggers:
            return action_triggers.get("patterns", [])
        return []

    @property
    def instructions(self) -> Union[str, Dict[str, Any]]:
        """Get instructions for this action"""
        if self._instructions is not None:
            return self._prepend_common_instruction(self._instructions)

        if self._parent_behavior:
            if self.name == Action.CLARIFICATION:
                instructions = self._parent_behavior.guardrails.requirements_clarification_instructions
                return self._prepend_common_instruction(instructions)
            elif self.name == Action.PLANNING:
                instructions = self._parent_behavior.guardrails.get_planning_instructions
                return self._prepend_common_instruction(instructions)
            elif self.name == Action.BUILD_STRUCTURE:
                instructions = self._parent_behavior.content.build_instructions
                result = {
                    "content_data": self._parent_behavior.content.structured,
                    "instructions": instructions
                }
                return self._prepend_common_instruction(result)
            elif self.name == Action.RENDER_OUTPUT:
                # Automatically execute builders when entering render_output action
                if self._parent_behavior and self._parent_behavior.content:
                    agent = self._parent_behavior._parent_agent if hasattr(self._parent_behavior, '_parent_agent') else None
                    if agent and agent.project:
                        builder_outputs = self._parent_behavior.content.execute_output_builders(agent.project)
                        # Store builder outputs immediately
                        if builder_outputs:
                            # Store builder outputs to rendered content
                            if self._parent_behavior.content._rendered:
                                self._parent_behavior.content._rendered.update(builder_outputs)
                            else:
                                self._parent_behavior.content._rendered = builder_outputs
                            # Save builder outputs to project
                            if agent.project:
                                agent.project.store_output(rendered=builder_outputs)
                
                result = {
                    "content_data": self._parent_behavior.content.structured,
                    "instructions": self._parent_behavior.content.transform_instructions()
                }
                return self._prepend_common_instruction(result)
            elif self.name == Action.VALIDATE:
                instructions = self._generate_validation_instructions()
                return self._prepend_common_instruction(instructions)
            elif self.name == Action.CORRECT:
                instructions = self._generate_correction_instructions()
                return self._prepend_common_instruction(instructions)

        return ""

    def store(self, **kwargs) -> Dict[str, Any]:
        """Store action output - delegates to behavior content or project. Returns dict with file paths."""
        if not self._parent_behavior:
            return {}

        if self.name == Action.CLARIFICATION:
            return self._store_clarification(kwargs)
        elif self.name == Action.PLANNING:
            return self._store_planning(kwargs)
        elif self.name in [Action.BUILD_STRUCTURE, Action.RENDER_OUTPUT, Action.VALIDATE, Action.CORRECT]:
            # For render_output, automatically execute builders before storing
            if self.name == Action.RENDER_OUTPUT and self._parent_behavior and self._parent_behavior.content:
                # Execute builders for outputs that have them
                if self._parent_behavior._parent_agent and self._parent_behavior._parent_agent.project:
                    builder_outputs = self._parent_behavior.content.execute_output_builders(
                        self._parent_behavior._parent_agent.project
                    )
                    
                    # Merge builder outputs with any manually provided rendered content
                    if builder_outputs:
                        if "rendered" in kwargs:
                            if isinstance(kwargs["rendered"], dict):
                                kwargs["rendered"].update(builder_outputs)
                            else:
                                kwargs["rendered"] = builder_outputs
                        else:
                            kwargs["rendered"] = builder_outputs
            
            return self._store_content(kwargs)
        return {}

    def _get_value(self, kwargs: dict, key: str) -> Any:
        """Get value from kwargs or outcomes, preferring kwargs"""
        if key in kwargs:
            return kwargs.get(key)
        return self.outcomes.get(key)

    def _store_clarification(self, kwargs: dict) -> Dict[str, Any]:
        """Store clarification data"""
        if not self._parent_behavior.content._project:
            return {}

        key_questions = self._get_value(kwargs, "key_questions_answered")
        evidence = self._get_value(kwargs, "evidence_provided")
        additional = self._get_value(kwargs, "additional_questions_answered")

        clarification_path = self._parent_behavior.content._project.store_clarification(
            key_questions_answered=key_questions,
            evidence_provided=evidence,
            additional_questions_answered=additional
        )
        return {"clarification_path": str(clarification_path)}

    def _store_planning(self, kwargs: dict) -> Dict[str, Any]:
        """Store planning data"""
        if not self._parent_behavior.content._project:
            return {}

        decisions_made = self._get_value(kwargs, "decisions_made")
        assumptions_made = self._get_value(kwargs, "assumptions_made")
        behavior_name = self._parent_behavior.name if self._parent_behavior else None

        planning_path = self._parent_behavior.content._project.store_planning(
            decisions_made=decisions_made,
            assumptions_made=assumptions_made,
            behavior_name=behavior_name
        )
        return {"planning_path": str(planning_path)}

    def _store_content(self, kwargs: dict) -> Dict[str, Any]:
        """Store structured/rendered content"""
        saved_paths = {}

        if "structured" in kwargs:
            self._parent_behavior.content.structured = kwargs["structured"]
            if self._parent_behavior.content._project:
                saved = self._parent_behavior.content._project.store_output(structured=kwargs["structured"])
                if "structured_path" in saved:
                    saved_paths["structured_path"] = saved["structured_path"]

        if "rendered" in kwargs:
            self._parent_behavior.content.rendered = kwargs["rendered"]
            if self._parent_behavior.content._project:
                saved = self._parent_behavior.content._project.store_output(rendered=kwargs["rendered"])
                if "rendered_paths" in saved:
                    saved_paths["rendered_paths"] = saved["rendered_paths"]

        self.outcomes.update(kwargs)
        if "structured" in kwargs:
            self.output["structured"] = kwargs["structured"]
        if "rendered" in kwargs:
            self.output["rendered"] = kwargs["rendered"]

        return saved_paths

    def _load_base_config(self) -> Dict[str, Any]:
        """Load base agent config for prompt templates"""
        base_config_path = Path(__file__).parent.parent / "agent.json"
        if base_config_path.exists():
            with open(base_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _get_common_instruction(self) -> str:
        """Get the common instruction that applies before all instructions"""
        base_config = self._load_base_config()
        common_instruction_template = base_config.get("common_instruction", "")

        if not common_instruction_template:
            return ""

        agent = self._parent_behavior._parent_agent if hasattr(self._parent_behavior, '_parent_agent') else None
        if not agent:
            return common_instruction_template

        project_area = agent.project_area or "not set"
        agent_name = agent.agent_name or "base"

        common_instruction = common_instruction_template.replace("{{project_area}}", project_area)
        common_instruction = common_instruction.replace("{{agent_name}}", agent_name)

        return common_instruction

    def _prepend_common_instruction(self, instructions: Union[str, Dict[str, Any]]) -> Union[str, Dict[str, Any]]:
        """Prepend common instruction to instructions (string or dict with 'instructions' key)"""
        common_instruction = self._get_common_instruction()

        if not common_instruction:
            return instructions

        if isinstance(instructions, str):
            return common_instruction + "\n\n" + instructions
        elif isinstance(instructions, dict):
            if "instructions" in instructions:
                instructions_copy = instructions.copy()
                instructions_copy["instructions"] = common_instruction + "\n\n" + instructions_copy["instructions"]
                return instructions_copy
            instructions_copy = instructions.copy()
            instructions_copy["common_instruction"] = common_instruction
            return instructions_copy

        return instructions

    def _generate_validation_instructions(self) -> str:
        """Generate comprehensive validation instructions with rules, examples, content, and violations"""
        if not self._parent_behavior:
            return "Validate content against rules"

        instructions_parts = []
        self._add_clarification_and_planning(instructions_parts)
        self._add_content_data(instructions_parts)
        self._add_agent_rules(instructions_parts)
        self._add_behavior_rules(instructions_parts)
        self._add_violations(instructions_parts)
        self._add_validation_template(instructions_parts)

        return "\n".join(instructions_parts)

    def _add_clarification_and_planning(self, instructions_parts: List[str]):
        """Add clarification and planning data to instructions"""
        agent = self._parent_behavior._parent_agent if hasattr(self._parent_behavior, '_parent_agent') else None
        if not agent or not agent.project:
            return

        clarification_data = agent.project._load_clarification()
        if clarification_data:
            formatted_clarification = agent.project._format_clarification_for_prompt(clarification_data)
            if formatted_clarification and formatted_clarification != "No clarification data available.":
                instructions_parts.append(formatted_clarification)
                instructions_parts.append("")

        planning_data = agent.project._load_planning()
        if planning_data:
            current_behavior = agent.workflow.current_behavior.name if agent.workflow.current_behavior else None
            formatted_planning = agent.project._format_planning_for_prompt(planning_data, current_behavior)
            if formatted_planning and formatted_planning != "No planning data available." and not formatted_planning.startswith("No planning data available."):
                instructions_parts.append(formatted_planning)
                instructions_parts.append("")

    def _add_content_data(self, instructions_parts: List[str]):
        """Add structured and rendered content to instructions"""
        content = self._parent_behavior.content

        structured = content.structured
        if structured:
            instructions_parts.append("**Content Data to Validate:**")
            instructions_parts.append("```json")
            instructions_parts.append(json.dumps(structured, indent=2))
            instructions_parts.append("```")
            instructions_parts.append("")

        rendered = content.rendered
        if rendered:
            instructions_parts.append("**Rendered Output to Validate:**")
            instructions_parts.append("```json")
            instructions_parts.append(json.dumps(rendered, indent=2))
            instructions_parts.append("```")
            instructions_parts.append("")

    def _add_agent_rules(self, instructions_parts: List[str]):
        """Add agent-level rules and examples to instructions"""
        agent_rules = self._parent_behavior.agent_rules
        if not agent_rules:
            return

        instructions_parts.append("**Agent-level rules:**")
        if agent_rules.description:
            instructions_parts.append(agent_rules.description)
        instructions_parts.append("")

        if agent_rules.examples.do or agent_rules.examples.dont:
            self._add_examples(instructions_parts, agent_rules.examples)

    def _add_behavior_rules(self, instructions_parts: List[str]):
        """Add behavior-level rules and examples to instructions"""
        behavior_rules = self._parent_behavior.rules
        if not behavior_rules or not hasattr(behavior_rules, 'rules') or not behavior_rules.rules:
            return

        instructions_parts.append("**Behavior-level rules:**")
        for rule in behavior_rules.rules:
            if rule.description:
                instructions_parts.append(f"**{rule.description}**")
                instructions_parts.append("")

            if isinstance(rule.examples, list):
                self._add_example_pairs(instructions_parts, rule.examples)
            elif hasattr(rule.examples, 'do') or hasattr(rule.examples, 'dont'):
                self._add_examples(instructions_parts, rule.examples)

    def _add_examples(self, instructions_parts: List[str], examples):
        """Add DO/DON'T examples to instructions"""
        if examples.do:
            instructions_parts.append("**DO:**")
            for example in examples.do:
                self._add_example_item(instructions_parts, example, prefix="- ")
            instructions_parts.append("")

        if examples.dont:
            instructions_parts.append("**DON'T:**")
            for example in examples.dont:
                self._add_example_item(instructions_parts, example, prefix="- ")
            instructions_parts.append("")

    def _add_example_pairs(self, instructions_parts: List[str], example_pairs: List[Dict]):
        """Add example pairs (complex structure) to instructions"""
        for example_pair in example_pairs:
            if example_pair.get("do"):
                self._add_example_item(instructions_parts, example_pair["do"], prefix="**DO:** ")
            if example_pair.get("dont"):
                self._add_example_item(instructions_parts, example_pair["dont"], prefix="**DON'T:** ")
            instructions_parts.append("")

    def _add_example_item(self, instructions_parts: List[str], example: Any, prefix: str = ""):
        """Add a single example item to instructions"""
        if isinstance(example, ExampleItem):
            if example.description:
                instructions_parts.append(f"{prefix}{example.description}: {example.content}")
            else:
                instructions_parts.append(f"{prefix}{example.content}")
        else:
            instructions_parts.append(f"{prefix}{example}")

    def _add_violations(self, instructions_parts: List[str]):
        """Add violations found by code to instructions"""
        violations = self._scan_for_violations()
        if not violations:
            return

        instructions_parts.append("**Violations Found by Code:**")
        instructions_parts.append("")

        violations_by_rule = {}
        for violation in violations:
            rule_desc = violation.get("rule", "Unknown rule")
            if rule_desc not in violations_by_rule:
                violations_by_rule[rule_desc] = []
            violations_by_rule[rule_desc].append(violation)

        for rule_desc, rule_violations in violations_by_rule.items():
            instructions_parts.append(f"**{rule_desc}**")
            for violation in rule_violations:
                message = violation.get("message", "")
                line_number = violation.get("line_number", 0)
                instructions_parts.append(f"- {message} (line {line_number})")
            instructions_parts.append("")

    def _add_validation_template(self, instructions_parts: List[str]):
        """Add validation instructions template to instructions"""
        base_config = self._load_base_config()
        prompt_templates = base_config.get("prompt_templates", {})
        validation_template = prompt_templates.get("validate", {}).get("validation_instructions", {}).get("template", "")

        if validation_template:
            instructions_parts.append(validation_template)

    def _execute_diagnostic(self, diagnostic_ref: str) -> List[Dict[str, Any]]:
        """Execute a diagnostic function referenced by diagnostic_ref string. Returns list of violations."""
        if not self._parent_behavior or not diagnostic_ref:
            return []

        diagnostic_map_getter = self._get_diagnostic_map if hasattr(self, '_get_diagnostic_map') else None
        return self._parent_behavior.content.execute_diagnostic(diagnostic_ref, diagnostic_map_getter)

    def _scan_for_violations(self) -> List[Dict[str, Any]]:
        """Scan for violations by executing all diagnostics from agent and behavior rules. Returns list of violations."""
        all_violations = []

        if not self._parent_behavior:
            return all_violations

        agent_rules = self._parent_behavior.agent_rules
        behavior_rules = self._parent_behavior.rules

        if agent_rules and agent_rules.diagnostic:
            violations = self._execute_diagnostic(agent_rules.diagnostic)
            rule_desc = agent_rules.description if agent_rules.description else "Agent-level rules"
            for violation in violations:
                if isinstance(violation, dict):
                    violation["rule"] = rule_desc
                else:
                    violation = {"message": str(violation), "rule": rule_desc, "line_number": 0}
                all_violations.append(violation)

        if behavior_rules and hasattr(behavior_rules, 'rules') and behavior_rules.rules:
            for rule in behavior_rules.rules:
                if rule.diagnostic:
                    violations = self._execute_diagnostic(rule.diagnostic)
                    rule_desc = rule.description if rule.description else "Behavior-level rule"
                    for violation in violations:
                        if isinstance(violation, dict):
                            violation["rule"] = rule_desc
                        else:
                            violation = {"message": str(violation), "rule": rule_desc, "line_number": 0}
                        all_violations.append(violation)

        return all_violations

    def _generate_correction_instructions(self) -> str:
        """Generate correction instructions with validation feedback"""
        if not self._parent_behavior:
            return "Correct content based on validation feedback"

        instructions_parts = []

        agent = self._parent_behavior._parent_agent if hasattr(self._parent_behavior, '_parent_agent') else None
        if agent and agent.project:
            clarification_data = agent.project._load_clarification()
            planning_data = agent.project._load_planning()
            current_behavior = agent.workflow.current_behavior.name if agent.workflow.current_behavior else None

            if clarification_data:
                formatted_clarification = agent.project._format_clarification_for_prompt(clarification_data)
                if formatted_clarification and formatted_clarification != "No clarification data available.":
                    instructions_parts.append(formatted_clarification)
                    instructions_parts.append("")

            if planning_data:
                formatted_planning = agent.project._format_planning_for_prompt(planning_data, current_behavior)
                if formatted_planning and formatted_planning != "No planning data available." and not formatted_planning.startswith("No planning data available."):
                    instructions_parts.append(formatted_planning)
                    instructions_parts.append("")

        base_config = self._load_base_config()
        prompt_templates = base_config.get("prompt_templates", {})
        correction_template = prompt_templates.get("correct", {}).get("correction_instructions", {}).get("template", "")

        validate_action = None
        if self._parent_behavior.actions:
            for action in self._parent_behavior.actions.actions:
                if action.name == Action.VALIDATE:
                    validate_action = action
                    break

        if validate_action:
            violations = validate_action._scan_for_violations() if hasattr(validate_action, '_scan_for_violations') else []
            if violations:
                instructions_parts.append("**Validation Errors:**")
                for violation in violations:
                    rule = violation.get("rule", "Unknown rule")
                    message = violation.get("message", "")
                    line_number = violation.get("line_number", 0)
                    instructions_parts.append(f"- **{rule}**: {message} (line {line_number})")
                instructions_parts.append("")

        if validate_action and hasattr(validate_action, '_generate_validation_instructions'):
            validation_instructions = validate_action._generate_validation_instructions()
            instructions_parts.append("**Validation Context:**")
            instructions_parts.append(validation_instructions)
            instructions_parts.append("")

        if correction_template:
            instructions_parts.append(correction_template)

        return "\n".join(instructions_parts) if instructions_parts else "Correct content based on validation feedback"

    def store_output(self, output_data: Dict[str, Any]):
        """Store output data and make it accessible via property"""
        self.output.update(output_data)

    @property
    def validation_report(self) -> str:
        """Get validation report from output"""
        return self.output.get("validation_report", "")


class Actions:
    """Behavior actions configuration"""

    DEFAULT_ACTIONS = ["clarification", "planning", "build_structure", "render_output", "validate", "correct"]
    DEFAULT_MANDATORY_ACTIONS = ["clarification", "planning"]
    ALL_ACTIONS_MANDATORY_BEHAVIORS = ["shape", "exploration"]

    def __init__(self, actions_config: Dict[str, Any], behavior_name: str = None, parent_behavior=None):
        """Initialize with actions config and behavior context"""
        self.description = actions_config.get("description", "")
        self._behavior_name = behavior_name
        self._parent_behavior = parent_behavior

        custom_actions = actions_config.get("actions", [])
        if custom_actions:
            self.actions = [Action(action.get("name", ""), parent_behavior, action_config=action) for action in custom_actions if action.get("name")]
        else:
            self.actions = []
            for action_name in self.DEFAULT_ACTIONS:
                action_config = actions_config.get(action_name, {})
                self.actions.append(Action(action_name, parent_behavior, action_config=action_config))

        self._current_action_index = 0 if self.actions else -1

    def reset(self):
        """Reset actions to first action (used when starting a new behavior)"""
        self._current_action_index = 0 if self.actions else -1

    @property
    def current_action(self) -> Optional[Action]:
        """Get current action"""
        if self._current_action_index >= 0 and self._current_action_index < len(self.actions):
            return self.actions[self._current_action_index]
        return None

    def is_action_mandatory(self, action_name: str) -> bool:
        """Check if an action is mandatory for this behavior"""
        if self._behavior_name in self.ALL_ACTIONS_MANDATORY_BEHAVIORS:
            return True

        return action_name in self.DEFAULT_MANDATORY_ACTIONS

    def can_advance(self) -> bool:
        """Check if current action can advance (is complete)"""
        current = self.current_action
        if not current:
            return False

        if current.name == "clarification":
            return "key_questions_answered" in current.outcomes and "evidence_provided" in current.outcomes
        elif current.name == "planning":
            return "decisions_made" in current.outcomes and "assumptions_made" in current.outcomes
        elif current.name == "build_structure":
            return "structured" in current.output or (current.output.get("structured") is not None)
        elif current.name in ["render_output", "validate", "correct"]:
            return bool(current.output)

        return True

    def next_action(self, force: bool = False) -> Optional[Action]:
        """Move to next action, with optional force to skip validation"""
        if not self.actions:
            return None

        current = self.current_action
        if current:
            if not force and not self.can_advance():
                mandatory = self.is_action_mandatory(current.name)
                if mandatory:
                    raise ValueError(
                        f"Cannot skip mandatory action '{current.name}' without completion. "
                        f"Use force=True to override."
                    )
                else:
                    raise ValueError(f"Cannot advance from incomplete action '{current.name}'")

        if self._current_action_index < len(self.actions) - 1:
            self._current_action_index += 1
            return self.current_action

        return None

    def move_to_action(self, action_name: str, force: bool = False) -> Optional[Action]:
        """Move to a specific action by name"""
        target_index = None
        for i, action in enumerate(self.actions):
            if action.name == action_name:
                target_index = i
                break

        if target_index is None:
            return None

        current_index = self._current_action_index

        if target_index > current_index and not force:
            current_action = self.current_action
            if current_action:
                if self.is_action_mandatory(current_action.name):
                    if not self.can_advance():
                        raise ValueError(
                            f"Cannot skip mandatory action '{current_action.name}' without completion. "
                            f"Use force=True to override."
                        )

            for i in range(current_index + 1, target_index):
                action = self.actions[i]
                if self.is_action_mandatory(action.name):
                    temp_index = self._current_action_index
                    self._current_action_index = i
                    can_advance = self.can_advance()
                    self._current_action_index = temp_index

                    if not can_advance:
                        raise ValueError(
                            f"Cannot skip mandatory action '{action.name}' without completion. "
                            f"Use force=True to override."
                        )

        self._current_action_index = target_index
        return self.current_action

class StructuredContent:
    """Structured content schema configuration"""

    def __init__(self, structured_content_config: Dict[str, Any]):
        """Initialize with only the structured_content portion of content config"""
        self.schema = structured_content_config.get("schema", "")
        self.path = structured_content_config.get("path", "")
        self.description = structured_content_config.get("description", "")
        self.instructions = structured_content_config.get("instructions", "")

class Output:
    """Output configuration (name, transformer, template, instructions, path)"""

    def __init__(self, output_config: Dict[str, Any], agent_config_path: Optional[Path] = None):
        """Initialize with a single output object from outputs array"""
        self.name = output_config.get("name", "")
        self.transformer = output_config.get("transformer", "")
        self.template = output_config.get("template", "")
        self.instructions = output_config.get("instructions", "")
        self.builder = output_config.get("builder", "")
        self.path = output_config.get("path", "")
        self._agent_config_path = agent_config_path
        self._template_content: Optional[str] = None

    def _load_template(self) -> Optional[str]:
        """Load template file content if template path is provided"""
        if not self.template or not self._agent_config_path:
            return None

        template_path = self._agent_config_path.parent / self.template
        if template_path.exists():
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except IOError:
                return None
        return None

    @property
    def template_content(self) -> Optional[str]:
        """Get template file content, loading it if not already loaded"""
        if self._template_content is None:
            self._template_content = self._load_template()
        return self._template_content

class Content:
    """Content configuration and data - defines how to build/transform and holds actual content data"""

    def __init__(self, content_config: Dict[str, Any], agent_rules: Optional[Rules] = None, behavior_rules: Optional[Rules] = None, project=None, agent_config_path: Optional[Path] = None):
        """Initialize with only the content portion of behavior config"""
        structured_config = content_config.get("structured_content", {})
        self.structured_content = StructuredContent(structured_config)
        self.builder = content_config.get("builder", "")
        outputs_config = content_config.get("outputs", [])
        self.outputs = [Output(output_config, agent_config_path=agent_config_path) for output_config in outputs_config]
        self.agent_rules = agent_rules
        self.behavior_rules = behavior_rules

        self._project = project
        self._structured: Optional[Dict[str, Any]] = None
        self._rendered: Optional[Dict[str, Any]] = None
        self._transformations: Dict[str, Any] = {}
        self._last_store_paths: Dict[str, Any] = {}

    @property
    def build_instructions(self) -> str:
        """Generate builder prompt for AI to help generate structured content"""
        instructions_parts = []

        self._add_clarification_and_planning_to_build(instructions_parts)

        self._add_existing_structured_content(instructions_parts)

        self._add_agent_rules_to_build(instructions_parts)
        self._add_behavior_rules_to_build(instructions_parts)

        self._add_base_instructions(instructions_parts)

        return "\n".join(instructions_parts)

    def _add_clarification_and_planning_to_build(self, instructions_parts: List[str]):
        """Add clarification and planning data to build instructions"""
        agent = self._get_parent_agent()
        if not agent or not agent.project:
            return

        clarification_data = agent.project._load_clarification()
        planning_data = agent.project._load_planning()
        current_behavior = agent.workflow.current_behavior.name if agent.workflow.current_behavior else None

        if clarification_data:
            formatted_clarification = agent.project._format_clarification_for_prompt(clarification_data)
            if formatted_clarification and formatted_clarification != "No clarification data available.":
                instructions_parts.append(f"{formatted_clarification}\n\n")

        if planning_data:
            formatted_planning = agent.project._format_planning_for_prompt(planning_data, current_behavior)
            if formatted_planning and formatted_planning != "No planning data available." and not formatted_planning.startswith("No planning data available."):
                instructions_parts.append(f"{formatted_planning}\n\n")

    def _get_parent_agent(self):
        """Get parent agent if available"""
        return self._parent_behavior._parent_agent if hasattr(self, '_parent_behavior') and hasattr(self._parent_behavior, '_parent_agent') else None

    def _add_existing_structured_content(self, instructions_parts: List[str]):
        """Add existing structured content if available"""
        if self._project and hasattr(self._project, '_output_data'):
            existing_structured = self._project._output_data.get("structured")
            if existing_structured:
                instructions_parts.append("**Existing structured content:**")
                instructions_parts.append("")
                instructions_parts.append("```json")
                instructions_parts.append(json.dumps(existing_structured, indent=2))
                instructions_parts.append("```")
                instructions_parts.append("")

    def _add_agent_rules_to_build(self, instructions_parts: List[str]):
        """Add agent-level rules and examples to build instructions"""
        if not self.agent_rules:
            return

        if self.agent_rules.description:
            instructions_parts.append(f"**Agent-level rules:** {self.agent_rules.description}")

        if self.agent_rules.examples.do or self.agent_rules.examples.dont:
            instructions_parts.append("\n**Agent-level examples:**")
            self._add_examples_list(instructions_parts, self.agent_rules.examples.do, "DO:")
            self._add_examples_list(instructions_parts, self.agent_rules.examples.dont, "DON'T:")

    def _add_behavior_rules_to_build(self, instructions_parts: List[str]):
        """Add behavior-level rules and examples to build instructions"""
        if not self.behavior_rules:
            return

        if self.behavior_rules.description:
            instructions_parts.append(f"\n**Behavior-level rules:** {self.behavior_rules.description}")

        if hasattr(self.behavior_rules, 'rules') and self.behavior_rules.rules:
            for rule in self.behavior_rules.rules:
                if rule.description:
                    instructions_parts.append(f"\n**Rule:** {rule.description}")
                self._add_rule_examples(instructions_parts, rule)

    def _add_rule_examples(self, instructions_parts: List[str], rule):
        """Add examples from a rule to instructions"""
        if isinstance(rule.examples, list):
            for example_pair in rule.examples:
                if example_pair.get("do"):
                    self._add_example_item(instructions_parts, example_pair["do"], "  DO: ")
                if example_pair.get("dont"):
                    self._add_example_item(instructions_parts, example_pair["dont"], "  DON'T: ")
        elif hasattr(rule.examples, 'do') or hasattr(rule.examples, 'dont'):
            if rule.examples.do or rule.examples.dont:
                instructions_parts.append("\n**Examples:**")
                self._add_examples_list(instructions_parts, rule.examples.do, "DO:")
                self._add_examples_list(instructions_parts, rule.examples.dont, "DON'T:")

    def _add_examples_list(self, instructions_parts: List[str], examples: List, prefix: str):
        """Add a list of examples with prefix"""
        if not examples:
            return
        instructions_parts.append(prefix)
        for example in examples:
            self._add_example_item(instructions_parts, example, "  - ")

    def _add_example_item(self, instructions_parts: List[str], example: Any, prefix: str):
        """Add a single example item to instructions"""
        if isinstance(example, ExampleItem):
            if example.description:
                instructions_parts.append(f"{prefix}{example.description}: {example.content}")
            else:
                instructions_parts.append(f"{prefix}{example.content}")
        else:
            instructions_parts.append(f"{prefix}{example}")

    def _add_base_instructions(self, instructions_parts: List[str]):
        """Add base instructions or fallback"""
        base_instructions = self.structured_content.instructions if self.structured_content.instructions else ""

        if base_instructions:
            instructions_parts.append(base_instructions)
        else:
            if self.structured_content.schema:
                instructions_parts.append(f"\n**Schema:** Use schema '{self.structured_content.schema}'")

            if self.structured_content.description:
                instructions_parts.append(f"\n**Description:** {self.structured_content.description}")

            if self.builder:
                instructions_parts.append(f"\n**Builder:** Use builder function '{self.builder}'")

    def transform_instructions(self) -> str:
        """Generate transformer prompts from each output's instructions"""
        instructions_parts = []

        agent = self._parent_behavior._parent_agent if hasattr(self, '_parent_behavior') and hasattr(self._parent_behavior, '_parent_agent') else None
        if agent and agent.project:
            clarification_data = agent.project._load_clarification()
            planning_data = agent.project._load_planning()
            current_behavior = agent.workflow.current_behavior.name if agent.workflow.current_behavior else None

            if clarification_data:
                formatted_clarification = agent.project._format_clarification_for_prompt(clarification_data)
                if formatted_clarification and formatted_clarification != "No clarification data available.":
                    instructions_parts.append(formatted_clarification)
                    instructions_parts.append("")

            if planning_data:
                formatted_planning = agent.project._format_planning_for_prompt(planning_data, current_behavior)
                if formatted_planning and formatted_planning != "No planning data available." and not formatted_planning.startswith("No planning data available."):
                    instructions_parts.append("**MANDATORY: You MUST apply ALL planning decisions and assumptions below to guide your generation.**")
                    instructions_parts.append("These decisions contain critical constraints and strategies that override default patterns.")
                    instructions_parts.append("")
                    instructions_parts.append(formatted_planning)
                    instructions_parts.append("")

        has_content = self.structured is not None

        if has_content and self.structured:
            instructions_parts.append("**Structured Content Data:**")
            instructions_parts.append("```json")
            instructions_parts.append(json.dumps(self.structured, indent=2))
            instructions_parts.append("```")
            instructions_parts.append("")

        if not self.outputs:
            instructions_parts.append("Transform the structured content into rendered artifacts using available templates.")
            return "\n".join(instructions_parts)

        for output in self.outputs:
            output_name = output.name if hasattr(output, 'name') else ""
            output_instructions = output.instructions if hasattr(output, 'instructions') and output.instructions else ""
            output_builder = output.builder if hasattr(output, 'builder') and output.builder else ""

            # Skip outputs with builders - they will be executed automatically
            if output_builder:
                continue  # Don't add instructions for builder outputs
            
            if output_instructions:
                instructions_parts.append(f"**{output_name}:**")
                instructions_parts.append(output_instructions)

                if hasattr(output, 'template') and output.template:
                    template_content = output.template_content
                    if template_content:
                        instructions_parts.append(f"\n**Template file content ({output.template}):**")
                        instructions_parts.append("```")
                        instructions_parts.append(template_content)
                        instructions_parts.append("```")
                        instructions_parts.append("\nUse the template file content above as the exact structure and format for the output.")
            else:
                template_name = output.template if hasattr(output, 'template') else ""
                transformer = output.transformer if hasattr(output, 'transformer') else ""
                instructions_parts.append(f"**{output_name}:** Use template '{template_name}' with transformer '{transformer}'")

                if template_name and hasattr(output, 'template_content'):
                    template_content = output.template_content
                    if template_content:
                        instructions_parts.append(f"\n**Template file content:**")
                        instructions_parts.append("```")
                        instructions_parts.append(template_content)
                        instructions_parts.append("```")
            instructions_parts.append("")

        if not has_content:
            instructions_parts.insert(0, "(No structured content available yet.)\n")

        return "\n".join(instructions_parts).strip()

    @property
    def structured(self) -> Optional[Dict[str, Any]]:
        return self._structured

    @structured.setter
    def structured(self, value: Optional[Dict[str, Any]]):
        self._structured = value
        if value is not None and self._project:
            saved_paths = self.store()
            self._last_store_paths = saved_paths
        else:
            self._last_store_paths = {}

    @property
    def rendered(self) -> Optional[Dict[str, Any]]:
        """Get rendered documents"""
        return self._rendered

    @rendered.setter
    def rendered(self, value: Dict[str, Any]):
        """Set rendered documents"""
        if value is None:
            self._rendered = None
            self._last_store_paths = {}
        else:
            self._rendered = value
            if self._project:
                saved_paths = self.store()
                self._last_store_paths = saved_paths
            else:
                self._last_store_paths = {}

    def validate(self) -> bool:
        """Validate Content Data against structured content schema"""
        if self._structured is None:
            return False
        if not isinstance(self._structured, dict):
            return False

        if self.structured_content.schema:
            pass

        return len(self._structured) > 0

    def save(self) -> Dict[str, Any]:
        """Save Content Data including structured JSON and rendered documents. Returns dict with file paths."""
        if not self._project:
            return {}

        saved_paths = self._project.store_output(
            structured=self._structured,
            rendered=self._rendered
        )

        if self._project:
            status_parts = []
            if self._structured is not None:
                status_parts.append("store_structured")
            if self._rendered is not None:
                status_parts.append("store_rendered")
            if status_parts:
                status = "_".join(status_parts) if len(status_parts) > 1 else status_parts[0]
                sanitized_saved_paths = self._project._convert_paths_to_strings(saved_paths) if saved_paths else {}
                self._project.track_activity(status, None, {"saved_paths": sanitized_saved_paths})

            self._project.create_traceability_link(
                structured=self._structured,
                rendered=self._rendered
            )

        self._last_store_paths = saved_paths
        return saved_paths

    def store(self) -> Dict[str, Any]:
        """Store content data - alias for save() for consistency"""
        return self.save()

    def build(self):
        """Build initial structure if not already present"""
        if not self.structured:
            self.structured = {"epics": [], "features": [], "stories": []}

    def build_with_instructions(self) -> Dict[str, Any]:
        """Build structure and return with instructions"""
        self.build()
        return {
            "content_data": self.structured,
            "instructions": "Complete building the structure using the provided content data."
        }

    def transform(self):
        """Track transformation state"""
        self._transformations["last_transform"] = {
            "structured": self.structured is not None,
            "rendered": self.rendered is not None
        }

    def get_completion_instructions(self) -> str:
        """Get completion instructions if structured content exists"""
        if self.structured:
            return "Complete building the structure."
        return ""

    @property
    def transformations(self) -> Dict[str, Any]:
        """Get transformation tracking data"""
        return self._transformations

    def execute_output_builders(self, project) -> Dict[str, Any]:
        """Execute builder functions for outputs that have builders configured.
        
        Also executes behavior-level builders if configured (e.g., arrange behavior).
        """
        rendered_outputs = {}
        
        # Check for behavior-level builder first (e.g., arrange behavior)
        if hasattr(self, 'builder') and self.builder:
            builder_path = self.builder
            try:
                # Dynamically import and execute builder function
                parts = builder_path.split('.')
                if len(parts) > 1:
                    # Full module path provided
                    module_path = '.'.join(parts[:-1])
                    function_name = parts[-1]
                else:
                    # Just function name provided - resolve to agent's src module
                    function_name = builder_path
                    # Get agent name from project
                    agent_name = None
                    if hasattr(project, 'agent_name') and project.agent_name:
                        agent_name = project.agent_name
                    elif hasattr(project, '_parent_agent') and project._parent_agent:
                        agent_name = getattr(project._parent_agent, 'agent_name', None)
                    
                    if agent_name and str(agent_name).strip():
                        agent_module_name = str(agent_name).lower().replace('-', '_')
                        module_path = f"agents.{agent_module_name}.src"
                    else:
                        module_path = "agents.story_bot.src"
                    
                    if not module_path or not str(module_path).strip():
                        module_path = "agents.story_bot.src"
                
                # Add workspace root to sys.path if needed
                import sys
                workspace_root = Path(__file__).parent.parent.parent.parent
                if str(workspace_root) not in sys.path:
                    sys.path.insert(0, str(workspace_root))
                
                import importlib
                module = importlib.import_module(module_path)
                builder_func = getattr(module, function_name)
                
                # Prepare builder parameters
                project_area = str(project.project_area) if project.project_area else None
                if project_area:
                    # Get structured content path
                    structured_content_path = None
                    structured_json_path = Path(project_area) / "docs" / "stories" / "structured.json"
                    if structured_json_path.exists():
                        structured_content_path = str(structured_json_path)
                    
                    # Execute builder (arrange behavior builder doesn't need output_path)
                    result = builder_func(
                        project_path=project_area,
                        structured_content_path=structured_content_path,
                        create_story_files=False  # Default for arrange behavior
                    )
                    
                    # Store result
                    if result:
                        if isinstance(result, dict):
                            # Builder returns dict with status/folders info
                            rendered_outputs["folder_structure"] = {
                                "builder": builder_path,
                                "status": result.get("status", "complete"),
                                "folders_created": result.get("folders_created", 0),
                                "folders_archived": result.get("folders_archived", 0)
                            }
                        else:
                            rendered_outputs["folder_structure"] = {
                                "builder": builder_path,
                                "result": str(result)
                            }
                            
            except Exception as e:
                if project:
                    project.track_activity("error", None, {
                        "builder": builder_path,
                        "error": str(e)
                    })
        
        # Then check output-level builders
        if not self.outputs:
            return rendered_outputs
        
        # Load structured content from file if not in memory
        if not self.structured:
            structured_path = project._path_manager.get_structured_file_path(project.workflow if hasattr(project, 'workflow') else None)
            if structured_path.exists():
                try:
                    import json
                    with open(structured_path, 'r', encoding='utf-8') as f:
                        self._structured = json.load(f)
                except Exception:
                    pass
        
        if not self.structured:
            return rendered_outputs
        
        for output in self.outputs:
            if not hasattr(output, 'builder') or not output.builder:
                continue
            
            builder_path = output.builder
            output_name = output.name if hasattr(output, 'name') else ""
            
            try:
                # Dynamically import and execute builder function
                parts = builder_path.split('.')
                if len(parts) > 1:
                    # Full module path provided (e.g., "agents.story_bot.src.story_agent.story_agent_build_drawio_story_shape")
                    module_path = '.'.join(parts[:-1])
                    function_name = parts[-1]
                else:
                    # Just function name provided - resolve to agent's src module
                    function_name = builder_path
                    # Get agent name from project - try multiple sources
                    agent_name = None
                    if hasattr(project, 'agent_name') and project.agent_name:
                        agent_name = project.agent_name
                    elif hasattr(project, '_parent_agent') and project._parent_agent:
                        agent_name = getattr(project._parent_agent, 'agent_name', None)
                    
                    # Always set a module path - default to story_bot if agent_name not available
                    if agent_name and str(agent_name).strip():
                        # Convert agent name to module path (e.g., "story_bot" -> "story_bot")
                        agent_module_name = str(agent_name).lower().replace('-', '_')
                        module_path = f"agents.{agent_module_name}.src"
                    else:
                        # Fallback: try to import from agents.story_bot.src (most common)
                        module_path = "agents.story_bot.src"
                    
                    # Final safety check - ensure module_path is never empty
                    if not module_path or not str(module_path).strip():
                        module_path = "agents.story_bot.src"
                    
                    # Add workspace root to sys.path if not already there (needed for agent imports)
                    import sys
                    workspace_root = Path(__file__).parent.parent.parent.parent
                    if str(workspace_root) not in sys.path:
                        sys.path.insert(0, str(workspace_root))
                
                import importlib
                module = importlib.import_module(module_path)
                
                builder_func = getattr(module, function_name)
                
                # Prepare builder parameters
                project_area = str(project.project_area) if project.project_area else None
                if not project_area:
                    continue
                
                # Get structured content path - use structured.json as source of truth
                structured_content_path = None
                structured_json_path = Path(project_area) / "docs" / "stories" / "structured.json"
                if structured_json_path.exists():
                    structured_content_path = str(structured_json_path)
                
                # Get output path
                output_path = None
                if hasattr(output, 'path') and output.path:
                    output_dir = Path(project_area) / output.path
                    # Determine file extension from output name or default to .drawio
                    file_ext = ".drawio" if "drawio" in output_name else ".xml"
                    # Special case: drawio.story_shape should be story-map.drawio
                    if output_name == "drawio.story_shape":
                        output_path = str(output_dir / "story-map.drawio")
                    else:
                        output_path = str(output_dir / f"{output_name.replace('.', '_')}{file_ext}")
                else:
                    # Use default rendered output path
                    workflow = project.workflow if hasattr(project, 'workflow') else None
                    output_path = str(project._path_manager.get_rendered_output_path(output_name, workflow))
                
                # Get template path if specified
                template_path = None
                if hasattr(output, 'template') and output.template:
                    if hasattr(self, '_agent_config_path') and self._agent_config_path:
                        template_path = str(self._agent_config_path.parent / output.template)
                    elif hasattr(output, '_agent_config_path') and output._agent_config_path:
                        template_path = str(output._agent_config_path.parent / output.template)
                
                # Execute builder
                result = builder_func(
                    project_path=project_area,
                    structured_content_path=structured_content_path,
                    output_path=output_path,
                    template_path=template_path
                )
                
                # Store result
                if result:
                    # Builder returns dict with output info, extract the actual output
                    if isinstance(result, dict) and "output_path" in result:
                        # Builder already wrote the file, don't save it again
                        # Just track that it was generated
                        generated_path = Path(result["output_path"])
                        if generated_path.exists():
                            # Store the path but don't include content - builder already saved it
                            rendered_outputs[output_name] = {
                                "output_path": str(generated_path),
                                "template": output.template if hasattr(output, 'template') else "",
                                "builder": builder_path,
                                "_builder_wrote_file": True  # Flag to skip saving
                            }
                    elif isinstance(result, dict) and "output" in result:
                        rendered_outputs[output_name] = result
                    else:
                        # Assume result is the output content
                        rendered_outputs[output_name] = {
                            "output": str(result),
                            "template": output.template if hasattr(output, 'template') else "",
                            "builder": builder_path
                        }
                        
            except Exception as e:
                if project:
                    project.track_activity("error", None, {
                        "output": output_name,
                        "builder": builder_path,
                        "error": str(e)
                    })
                continue
        
        return rendered_outputs

    def execute_diagnostic(self, diagnostic_ref: str, diagnostic_map_getter=None) -> List[Dict[str, Any]]:
        """Execute a diagnostic function on structured content. Content owns the structured data."""
        if not diagnostic_ref or not self.structured:
            return []

        if self._project:
            self._project.track_activity("execute_diagnostic", None, {"diagnostic": diagnostic_ref})

        try:
            violations = self._execute_diagnostic_from_map(diagnostic_ref, diagnostic_map_getter)
            if violations is not None:
                return self._track_diagnostic_complete(diagnostic_ref, violations)

            violations = self._execute_diagnostic_from_module(diagnostic_ref)
            if violations is not None:
                return self._track_diagnostic_complete(diagnostic_ref, violations)

            return []
        except (ImportError, AttributeError, Exception) as e:
            return self._track_diagnostic_error(diagnostic_ref, e)

    def _execute_diagnostic_from_map(self, diagnostic_ref: str, diagnostic_map_getter) -> Optional[List[Dict[str, Any]]]:
        """Execute diagnostic from diagnostic map if available"""
        if not diagnostic_map_getter:
            return None

        diagnostic_map = diagnostic_map_getter()
        if diagnostic_ref not in diagnostic_map:
            return None

        diagnostic = diagnostic_map[diagnostic_ref]
        if hasattr(diagnostic, 'validate'):
            return diagnostic.validate(self.structured)
        elif isinstance(diagnostic, type):
            return diagnostic().validate(self.structured)
        else:
            return diagnostic(self.structured) if callable(diagnostic) else None

    def _execute_diagnostic_from_module(self, diagnostic_ref: str) -> Optional[List[Dict[str, Any]]]:
        """Execute diagnostic by importing from module path"""
        if "." not in diagnostic_ref:
            return None

        module_path, function_name = diagnostic_ref.rsplit(".", 1)
        module = __import__(module_path, fromlist=[function_name])
        diagnostic_func = getattr(module, function_name)
        return diagnostic_func(self.structured)

    def _track_diagnostic_complete(self, diagnostic_ref: str, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Track diagnostic completion and return violations"""
        if self._project:
            self._project.track_activity("diagnostic_complete", None, {
                "diagnostic": diagnostic_ref,
                "violations": len(violations) if violations else 0
            })
        return violations if violations else []

    def _track_diagnostic_error(self, diagnostic_ref: str, error: Exception) -> List[Dict[str, Any]]:
        """Track diagnostic error and return empty list"""
        if self._project:
            self._project.track_activity("diagnostic_error", None, {
                "diagnostic": diagnostic_ref,
                "error": str(error)
            })
        return []

class Behavior:
    """Behavior configuration (order, guardrails, rules, actions, content)"""

    def __init__(self, behavior_config: Dict[str, Any], agent_rules: Optional[Rules] = None, project=None):
        """Initialize with only the behavior portion of behaviors config (e.g., behaviors['shape'])"""

        self.order = behavior_config.get("order", 0)

        guardrails_config = behavior_config.get("guardrails", {})
        self.guardrails = GuardRails(guardrails_config)
        self.guardrails._parent_behavior = self

        rules_config = behavior_config.get("rules", {})
        self.rules = Rules(rules_config)

        actions_config = behavior_config.get("actions", {})
        behavior_name = behavior_config.get("_behavior_name")
        self._behavior_name = behavior_name
        self.actions = Actions(actions_config, behavior_name=behavior_name, parent_behavior=self)

        content_config = behavior_config.get("content", {})
        agent_config_path = behavior_config.get("_agent_config_path")
        self.content = Content(content_config, agent_rules, self.rules, project, agent_config_path=agent_config_path)
        self.content._parent_behavior = self

        self.agent_rules = agent_rules

        self.trigger_words = behavior_config.get("trigger_words", {})

        self.pre_actions = behavior_config.get("pre_actions", [])
        self.post_actions = behavior_config.get("post_actions", [])

    @property
    def name(self) -> Optional[str]:
        """Get behavior name"""
        return self._behavior_name

    def get_trigger_words_for_action(self, action_name: str) -> List[str]:
        """Get trigger words for an action from behavior and action levels (Behavior owns this data)"""
        all_patterns = []

        behavior_triggers = getattr(self, 'trigger_words', {})
        if behavior_triggers:
            if "patterns" in behavior_triggers:
                all_patterns.extend(behavior_triggers.get("patterns", []))
            elif action_name in behavior_triggers:
                all_patterns.extend(behavior_triggers[action_name].get("patterns", []))

        try:
            action = self.actions.move_to_action(action_name, force=True)
            if action:
                all_patterns.extend(action.get_trigger_words())
        except (AttributeError, ValueError):
            pass

        return all_patterns

    def initialize_for_workflow(self) -> Optional["Action"]:
        """Initialize behavior for workflow start - reset actions and return first action (Behavior owns actions)"""
        if not hasattr(self, 'actions') or not self.actions:
            return None

        self.actions.reset()
        if self.actions.actions:
            return self.actions.actions[0]
        return None

    def execute_all_actions(self, workflow: "Workflow"):
        """Execute all actions in this behavior (Behavior owns actions and content)"""
        if not hasattr(self, 'actions') or not self.actions.actions:
            return

        for action in self.actions.actions:
            workflow._current_action = action

            if action.name == Action.BUILD_STRUCTURE and hasattr(self.content, 'builder') and self.content.builder:
                workflow._execute_builder_action(self, action)

            next_action = self.actions.next_action(force=True)
            if not next_action:
                break

    def get_guardrails_config(self) -> Dict[str, Any]:
        return {
            "guardrails": {
                "required_context": {
                    "key_questions": self.guardrails.required_context.key_questions,
                    "evidence": self.guardrails.required_context.evidence
                },
                "decision_making_criteria": [
                    {
                        "question": c.question,
                        "outcome": c.outcome,
                        "options": c.options
                    }
                    for c in self.guardrails.decision_making_criteria
                ],
                "typical_assumptions": self.guardrails.typical_assumptions,
                "recommended_human_activity": self.guardrails.recommended_human_activity
            }
        }

    @property
    def build_instructions(self) -> str:
        instructions_parts = []

        if self.agent_rules and self.agent_rules.description:
            instructions_parts.append(f"**Agent-level rules:** {self.agent_rules.description}")

        if self.agent_rules and (self.agent_rules.examples.do or self.agent_rules.examples.dont):
            instructions_parts.append("\n**Agent-level examples:**")
            if self.agent_rules.examples.do:
                instructions_parts.append("DO:")
                for example in self.agent_rules.examples.do:
                    if isinstance(example, ExampleItem):
                        if example.description:
                            instructions_parts.append(f"  - {example.description}: {example.content}")
                        else:
                            instructions_parts.append(f"  - {example.content}")
                    else:
                        instructions_parts.append(f"  - {example}")
            if self.agent_rules.examples.dont:
                instructions_parts.append("DON'T:")
                for example in self.agent_rules.examples.dont:
                    if isinstance(example, ExampleItem):
                        if example.description:
                            instructions_parts.append(f"  - {example.description}: {example.content}")
                        else:
                            instructions_parts.append(f"  - {example.content}")
                    else:
                        instructions_parts.append(f"  - {example}")

        if hasattr(self.rules, 'rules') and self.rules.rules:
            for rule in self.rules.rules:
                if rule.description:
                    instructions_parts.append(f"\n**Rule:** {rule.description}")
                if isinstance(rule.examples, list):
                    for example_pair in rule.examples:
                        if example_pair.get("do"):
                            do_item = example_pair["do"]
                            if isinstance(do_item, ExampleItem):
                                if do_item.description:
                                    instructions_parts.append(f"  DO: {do_item.description}: {do_item.content}")
                                else:
                                    instructions_parts.append(f"  DO: {do_item.content}")
                        if example_pair.get("dont"):
                            dont_item = example_pair["dont"]
                            if isinstance(dont_item, ExampleItem):
                                if dont_item.description:
                                    instructions_parts.append(f"  DON'T: {dont_item.description}: {dont_item.content}")
                                else:
                                    instructions_parts.append(f"  DON'T: {dont_item.content}")
                elif hasattr(rule.examples, 'do') or hasattr(rule.examples, 'dont'):
                    if rule.examples.do or rule.examples.dont:
                        instructions_parts.append("\n**Examples:**")
                        if rule.examples.do:
                            instructions_parts.append("DO:")
                            for example in rule.examples.do:
                                if isinstance(example, ExampleItem):
                                    if example.description:
                                        instructions_parts.append(f"  - {example.description}: {example.content}")
                                    else:
                                        instructions_parts.append(f"  - {example.content}")
                                else:
                                    instructions_parts.append(f"  - {example}")
                        if rule.examples.dont:
                            instructions_parts.append("DON'T:")
                            for example in rule.examples.dont:
                                if isinstance(example, ExampleItem):
                                    if example.description:
                                        instructions_parts.append(f"  - {example.description}: {example.content}")
                                    else:
                                        instructions_parts.append(f"  - {example.content}")
                                else:
                                    instructions_parts.append(f"  - {example}")
        elif self.rules.description:
            instructions_parts.append(f"\n**Behavior-specific rules:** {self.rules.description}")
            if hasattr(self.rules.examples, 'do') or hasattr(self.rules.examples, 'dont'):
                if self.rules.examples.do or self.rules.examples.dont:
                    instructions_parts.append("\n**Behavior-specific examples:**")
                    if self.rules.examples.do:
                        instructions_parts.append("DO:")
                        for example in self.rules.examples.do:
                            if isinstance(example, ExampleItem):
                                if example.description:
                                    instructions_parts.append(f"  - {example.description}: {example.content}")
                                else:
                                    instructions_parts.append(f"  - {example.content}")
                            else:
                                instructions_parts.append(f"  - {example}")
                    if self.rules.examples.dont:
                        instructions_parts.append("DON'T:")
                        for example in self.rules.examples.dont:
                            if isinstance(example, ExampleItem):
                                if example.description:
                                    instructions_parts.append(f"  - {example.description}: {example.content}")
                                else:
                                    instructions_parts.append(f"  - {example.content}")
                            else:
                                instructions_parts.append(f"  - {example}")

        instructions_parts.append("\nComplete building the structure using the provided content data, following all rules and examples above.")

        return "\n".join(instructions_parts)

class ToolsAndInstructions:
    """MCP tool names and usage instructions"""

    def __init__(self):
        self.tools: List[str] = []
        self.usage_instructions = "MCP tools are already registered via MCP server configuration. Use the registered tools for structure building."

    def __str__(self) -> str:
        return self.usage_instructions

class GuardRails:
    def __init__(self, guardrails_config: Dict[str, Any]):
        """Initialize GuardRails with only the guardrails portion of the behavior config"""

        base_instructions_config = guardrails_config.get("base_instructions")
        self.base_instructions = BaseInstructions(base_instructions_config) if base_instructions_config else None
        self.required_context = RequiredClarification(guardrails_config.get("required_context", {}))

        planning_config = guardrails_config.get("planning", {})
        criteria_config = planning_config.get("decision_making_criteria", [])
        self.decision_making_criteria = [
            DecisionCriterion(criterion) for criterion in criteria_config
        ]

        self.typical_assumptions = planning_config.get("typical_assumptions", [])
        self.recommended_human_activity = planning_config.get("recommended_human_activity", [])
        self.decision_instructions = planning_config.get("decision_instructions", None)
        self.assumptions: Dict[str, Any] = {}
        self.decision_criteria: Dict[str, Any] = {}

    @property
    def requirements_clarification_instructions(self) -> Dict[str, Any]:
        """
        Get clarification instructions with requirements.
        AI will handle validation and determine what's missing.
        """
        key_questions = [{'question': q, 'answer': None} for q in self.required_context.key_questions]
        evidence = [{'type': e, 'provided': None} for e in self.required_context.evidence]

        matched = {
            'key_questions': key_questions,
            'evidence': evidence
        }

        intro = self.base_instructions.clarification_intro if self.base_instructions else "Assess the provided context against the required questions and evidence below."
        instructions_parts = [
            intro,
            "",
            "**Required Key Questions:**",
        ]
        for item in matched['key_questions']:
            if item['answer']:
                instructions_parts.append(f"- {item['question']} (Answer: {item['answer']})")
            else:
                instructions_parts.append(f"- {item['question']}")

        instructions_parts.append("")
        instructions_parts.append("**Required Evidence:**")
        for item in matched['evidence']:
            if item['provided']:
                instructions_parts.append(f"- {item['type']} (Provided: {item['provided']})")
            else:
                instructions_parts.append(f"- {item['type']}")

        instructions_parts.append("")
        instructions_parts.append("**MANDATORY WORKFLOW - DO NOT SKIP ANY STEP:**")
        instructions_parts.append("1. Gather information from available documentation, context, or ask the user questions")
        instructions_parts.append("2. **CRITICAL: Present the gathered clarification information to the user in a clear, readable format**")
        instructions_parts.append("3. **WAIT for the user to review and confirm the clarification is correct**")
        instructions_parts.append("4. **ONLY AFTER user confirmation, store the clarification using agent_store_clarification tool**")
        instructions_parts.append("")
        instructions_parts.append("**DO NOT store clarification until the user has reviewed and confirmed it.**")
        instructions_parts.append("**The clarification action is NOT complete until the user has reviewed and confirmed the information.**")

        context_data = {
            "key_questions": matched['key_questions'],
            "evidence": matched['evidence']
        }

        return {
            "content_data": context_data,
            "instructions": "\n".join(instructions_parts)
        }
    def match_clarifications_to_requirements(self, key_questions_answered: Dict[str, str] = None, evidence_provided: Dict[str, str] = None):

        key_questions_answered = key_questions_answered or {}
        evidence_provided = evidence_provided or {}

        questions_dict = {q.strip().lower(): (q, a) for q, a in key_questions_answered.items()}
        evidence_dict = {e.strip().lower(): (e, p) for e, p in evidence_provided.items()}

        key_questions = []
        for question in self.required_context.key_questions:
            question_lower = question.strip().lower()
            answer = None
            if question_lower in questions_dict:
                _, answer = questions_dict[question_lower]
            key_questions.append({
                'question': question,
                'answer': answer
            })

        evidence = []
        for evidence_type in self.required_context.evidence:
            evidence_lower = evidence_type.strip().lower()
            provided = None
            if evidence_lower in evidence_dict:
                _, provided = evidence_dict[evidence_lower]
            evidence.append({
                'type': evidence_type,
                'provided': provided
            })

        return {
            'key_questions': key_questions,
            'evidence': evidence
        }  
    def _evaluate_context_against_requirements(self, context: str) -> Dict[str, Any]:
        """
        Evaluate context string against requirements and populate what was answered/provided.
        Returns validation result with key_questions_answered and evidence_provided populated.
        """
        key_questions_answered = []
        evidence_provided = []
        missing_questions = []
        missing_evidence = []

        for question in self.required_context.key_questions:
            if question.lower() in context.lower() or any(word in context.lower() for word in question.lower().split()[:3]):
                key_questions_answered.append(question)
            else:
                missing_questions.append(question)

        for evidence_type in self.required_context.evidence:
            if evidence_type.lower() in context.lower():
                evidence_provided.append(evidence_type)
            else:
                missing_evidence.append(evidence_type)

        return {
            "might_be_sufficient": len(missing_questions) == 0 and len(missing_evidence) == 0,
            "key_questions_answered": key_questions_answered,
            "evidence_provided": evidence_provided,
            "missing_key_questions": missing_questions,
            "missing_evidence": missing_evidence
        }

    @property
    def get_planning_instructions(self) -> Dict[str, Any]:
        """Get planning instructions - can use behavior-specific decision_instructions or build dynamically"""
        agent = self._parent_agent if hasattr(self, '_parent_agent') else None
        clarification_data = None
        planning_data = None
        current_behavior = None
        if agent and agent.project:
            clarification_data = agent.project._load_clarification()
            planning_data = agent.project._load_planning()
            current_behavior = agent.workflow.current_behavior.name if agent.workflow.current_behavior else None

        instructions_parts = []

        if clarification_data and agent and agent.project:
            instructions_parts.append(agent.project._format_clarification_for_prompt(clarification_data))
            instructions_parts.append("")

        if planning_data and agent and agent.project:
            instructions_parts.append(agent.project._format_planning_for_prompt(planning_data, current_behavior))
            instructions_parts.append("")

        if self.decision_instructions:
            intro = self.decision_instructions
            instructions_parts.append(intro)
        else:
            intro = self.base_instructions.planning_intro if self.base_instructions else "Present the following assumptions and decision criteria to the user and ask for their opinion on key decisions."
            instructions_parts.append(intro)
            instructions_parts.append("")
            instructions_parts.append("**Typical Assumptions:**")
            for assumption in self.typical_assumptions:
                instructions_parts.append(f"- {assumption}")

            instructions_parts.append("")
            instructions_parts.append("**Decision Making Criteria:**")
            for criterion in self.decision_making_criteria:
                instructions_parts.append(f"- {criterion.question}")
                instructions_parts.append(f"  Outcome: {criterion.outcome}")
                instructions_parts.append("  Options:")
                for option in criterion.options:
                    instructions_parts.append(f"    * {option}")
                instructions_parts.append("")

            instructions_parts.append("Present these assumptions and decision criteria to the user. Ask them to review the assumptions and select their preferred criteria/options for each decision point.")

        planning_data_dict = {
            "assumptions": self.typical_assumptions,
            "decision_criteria": [
                {
                    "question": c.question,
                    "outcome": c.outcome,
                    "options": c.options
                }
            for c in self.decision_making_criteria
            ]
        }

        return {
            "content_data": planning_data_dict,
            "instructions": "\n".join(instructions_parts)
        }
    def match_criteria_to_decisions_and_assumptions(self, decisions_made: Dict[str, str] = None, assumptions_made: Dict[str, str] = None):
        decisions_made = decisions_made or {}
        assumptions_made = assumptions_made or {}

        decisions_dict = {q.strip().lower(): (q, d) for q, d in decisions_made.items()}
        assumptions_dict = {a.strip().lower(): (a, m) for a, m in assumptions_made.items()}

        decision_criteria = []
        for criterion in self.decision_making_criteria:
            question_lower = criterion.question.strip().lower()
            decision = None
            if question_lower in decisions_dict:
                _, decision = decisions_dict[question_lower]
            decision_criteria.append({
                'question': criterion.question,
                'outcome': criterion.outcome,
                'options': criterion.options,
                'decision': decision
            })

        assumptions = []
        for assumption in self.typical_assumptions:
            assumption_lower = assumption.strip().lower()
            made = None
            if assumption_lower in assumptions_dict:
                _, made = assumptions_dict[assumption_lower]
            assumptions.append({
                'assumption': assumption,
                'made': made
            })

        return {
            'decision_criteria': decision_criteria,
            'assumptions': assumptions
        }

class ProjectPathManager:
    """Manages all project path resolution - owns path-related data"""

    def __init__(self, workspace_root: Path, project_area: str, activity_area: str, agent_name: Optional[str] = None):
        self._workspace_root = workspace_root
        self._project_area = project_area
        self._activity_area = activity_area
        self._agent_name = agent_name

    def resolve_project_path(self) -> Path:
        """Resolve project_area to an absolute path, always relative to workspace root"""
        if not self._project_area:
            return self._workspace_root
        return self._resolve_project_area_path()

    def _resolve_project_area_path(self) -> Path:
        """Resolve project_area path with error handling"""
        try:
            project_path = Path(self._project_area)
            if not project_path.is_absolute():
                return self._workspace_root / project_path
            return project_path
        except (OSError, ValueError):
            return self._workspace_root

    def get_output_dir(self) -> Path:
        """Get the output directory path based on activity_area"""
        project_path = self.resolve_project_path()
        return project_path / "output" / self._activity_area

    def get_structured_file_path(self, workflow: Optional["Workflow"] = None) -> Path:
        """Get the path for structured output JSON file"""
        project_path = self.resolve_project_path()

        if workflow and hasattr(workflow, 'current_behavior') and workflow.current_behavior:
            behavior = workflow.current_behavior
            if behavior and behavior.content and behavior.content.structured_content:
                structured_path_config = behavior.content.structured_content.path
                if structured_path_config:
                    return project_path / structured_path_config / "structured.json"

        return self.get_output_dir() / "structured.json"

    def get_rendered_file_path(self) -> Path:
        """Get the path for rendered output file (markdown)"""
        return self.get_output_dir() / "rendered.md"

    def get_clarification_file_path(self) -> Path:
        """Get the path for clarification data JSON file"""
        project_path = self.resolve_project_path()
        return project_path / "docs" / "activity" / self._activity_area / "clarification.json"

    def get_planning_file_path(self) -> Path:
        """Get the path for planning data JSON file"""
        project_path = self.resolve_project_path()
        return project_path / "docs" / "activity" / self._activity_area / "planning.json"

    def get_activity_dir(self) -> Path:
        """Get the activity directory path based on project_area and activity_area"""
        project_path = self.resolve_project_path()
        return project_path / "docs" / "activity" / self._activity_area

    def get_agent_state_file_path(self, project_path: Optional[Path] = None) -> Optional[Path]:
        """Get path to agent state file in project area (docs/activity/{activity_area}/agent_state.json)"""
        if not self._agent_name:
            return None

        if project_path is None:
            project_path = self.resolve_project_path()

        return project_path / "docs" / "activity" / self._activity_area / "agent_state.json"

    def get_rendered_output_path(self, output_name: str, workflow: Optional["Workflow"] = None) -> Path:
        """Get the path for a rendered output file based on output name and configuration"""
        project_path = self.resolve_project_path()

        output_config = None
        if workflow and hasattr(workflow, 'current_behavior') and workflow.current_behavior:
            behavior = workflow.current_behavior
            if behavior and behavior.content and behavior.content.outputs:
                for output in behavior.content.outputs:
                    if output.name == output_name:
                        output_config = output
                        break

        # Determine file extension based on output type
        file_ext = ".md"  # default
        if output_config:
            # If output has a builder, determine extension from output name
            if hasattr(output_config, 'builder') and output_config.builder:
                if "drawio" in output_name.lower():
                    file_ext = ".drawio"
                else:
                    file_ext = ".xml"
            # If output has a path, use the same extension logic
            elif output_config.path:
                if "drawio" in output_name.lower():
                    file_ext = ".drawio"
                else:
                    file_ext = ".md"
        elif "drawio" in output_name.lower():
            file_ext = ".drawio"

        if output_config and output_config.path:
            kebab_name = output_name.replace("_", "-").replace(".", "-")
            # If project_path already ends with 'docs', remove it from output_config.path to avoid docs/docs
            output_path = output_config.path
            if str(project_path).endswith('docs') and output_path.startswith('docs/'):
                output_path = output_path[5:]  # Remove 'docs/' prefix
            return project_path / output_path / f"{kebab_name}{file_ext}"

        return self.get_output_dir() / f"{output_name}{file_ext}"

    @property
    def project_area(self) -> str:
        return self._project_area

    @project_area.setter
    def project_area(self, value: str):
        self._project_area = value

    @property
    def workspace_root(self) -> Path:
        return self._workspace_root


class ProjectFileManager:
    """Handles file I/O operations - owns file reading/writing behavior"""

    def __init__(self, path_manager: ProjectPathManager):
        self._path_manager = path_manager

    def load_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load JSON file, return None if file doesn't exist or is invalid"""
        if not file_path.exists():
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if data else None
        except (json.JSONDecodeError, IOError):
            return None

    def save_json_file(self, file_path: Path, data: Dict[str, Any]):
        """Save data to JSON file"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_text_file(self, file_path: Path) -> Optional[str]:
        """Load text file, return None if file doesn't exist"""
        if not file_path.exists():
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError:
            return None

    def save_text_file(self, file_path: Path, content: str):
        """Save content to text file"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)


class ActivityLogger:
    """Manages activity logging - owns activity log data"""

    def __init__(self, path_manager: ProjectPathManager, file_manager: ProjectFileManager):
        self._path_manager = path_manager
        self._file_manager = file_manager
        self._activity_log: List[Dict[str, Any]] = []
        self._traceability_links: List[Dict[str, Any]] = []

    def track_activity(self, status: str, stage: Optional[str] = None, 
                      inputs: Optional[Dict[str, Any]] = None,
                      reasoning: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Track activity and persist to file"""
        if inputs:
            inputs = self._convert_paths_to_strings(inputs)
        if reasoning:
            reasoning = self._convert_paths_to_strings(reasoning)

        activity_entry = self._create_activity_entry(status, stage, inputs, reasoning)
        self._activity_log.append(activity_entry)
        self._save_activity_log()
        return activity_entry

    def _convert_paths_to_strings(self, data: Any) -> Any:
        """Recursively convert Path objects to strings for JSON serialization"""
        if isinstance(data, Path):
            return str(data)
        elif isinstance(data, dict):
            return {k: self._convert_paths_to_strings(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_paths_to_strings(item) for item in data]
        else:
            return data

    def _create_activity_entry(self, status: str, stage: Optional[str], 
                               inputs: Optional[Dict[str, Any]], 
                               reasoning: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "status": status,
            "stage": stage,
            "inputs": inputs or {},
            "reasoning": reasoning or {}
        }

    def _save_activity_log(self):
        """Save activity log to file"""
        activity_path = self._path_manager.get_activity_dir() / "activity.json"
        sanitized_log = self._convert_paths_to_strings(self._activity_log)
        try:
            self._file_manager.save_json_file(activity_path, sanitized_log)
        except IOError:
            pass

    def load_activity_log(self):
        """Load activity log from file"""
        activity_path = self._path_manager.get_activity_dir() / "activity.json"
        loaded_log = self._file_manager.load_json_file(activity_path)
        self._activity_log = loaded_log if loaded_log else []

    def create_traceability_link(self, structured: Optional[Dict[str, Any]] = None,
                                rendered: Optional[Dict[str, Any]] = None):
        """Create traceability link from current activity"""
        if not self._activity_log:
            return

        self._traceability_links.append({
            "activity": self._activity_log[-1],
            "output": {
                "structured": structured,
                "rendered": rendered
            }
        })

    @property
    def activity_log(self) -> List[Dict[str, Any]]:
        return self._activity_log

    @property
    def traceability_links(self) -> List[Dict[str, Any]]:
        return self._traceability_links


class ProjectDataManager:
    """Manages project data storage - owns structured, rendered, clarification, planning data"""

    def __init__(self, path_manager: ProjectPathManager, file_manager: ProjectFileManager):
        self._path_manager = path_manager
        self._file_manager = file_manager
        self._output_data: Dict[str, Any] = {
            "structured": None,
            "rendered": None
        }
        self.clarification: Dict[str, Any] = {
            "key_questions_answered": {},
            "evidence_provided": {},
            "additional_questions_answered": {}
        }
        self.planning: Dict[str, Any] = {}

    def load_output_data(self, workflow: Optional["Workflow"] = None):
        """Load output data from file system if files exist"""
        structured_path = self._path_manager.get_structured_file_path(workflow)
        rendered_path = self._path_manager.get_rendered_file_path()

        structured_data = self._file_manager.load_json_file(structured_path)
        if structured_data:
            self._output_data["structured"] = structured_data

        rendered_content = self._file_manager.load_text_file(rendered_path)
        if rendered_content:
            self._output_data["rendered"] = rendered_content

        planning_data = self.load_planning()
        if planning_data:
            self.planning = planning_data

        clarification_data = self.load_clarification()
        if clarification_data:
            self.clarification = clarification_data

    def store_output(self, structured: Optional[Dict[str, Any]] = None,
                    rendered: Optional[Dict[str, Any]] = None,
                    workflow: Optional["Workflow"] = None) -> Dict[str, Any]:
        """Store output data and persist to file system. Returns dict with file paths (as strings)."""
        saved_paths = {}

        if structured is not None:
            structured_path = self._path_manager.get_structured_file_path(workflow)
            existing_structured = self._file_manager.load_json_file(structured_path) or {}

            if existing_structured:
                merged_structured = self._deep_merge_dict(existing_structured, structured)
            else:
                merged_structured = structured

            self._output_data["structured"] = merged_structured
            self._save_structured(merged_structured, workflow)
            saved_paths["structured_path"] = str(structured_path)

        if rendered is not None:
            self._output_data["rendered"] = rendered
            rendered_paths = {}
            self._save_rendered(rendered, workflow)
            for output_name in rendered.keys():
                rendered_path = self._path_manager.get_rendered_output_path(output_name, workflow)
                if rendered_path.exists():
                    rendered_paths[output_name] = str(rendered_path)
            if rendered_paths:
                saved_paths["rendered_paths"] = rendered_paths

        return saved_paths

    def _deep_merge_dict(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries. Values from update override values in base.

        For nested dictionaries, recursively merges them. For lists, update replaces base.
        For other types, update replaces base.
        Removes keys from base that are not in update, especially empty arrays from initialization.
        """
        result = {}

        all_keys = set(base.keys()) | set(update.keys())

        for key in all_keys:
            if key in update:
                if key in base and isinstance(base[key], dict) and isinstance(update[key], dict):
                    result[key] = self._deep_merge_dict(base[key], update[key])
                else:
                    result[key] = update[key]
            elif key in base:
                base_value = base[key]
                if isinstance(base_value, list) and len(base_value) == 0:
                    continue
                result[key] = base_value

        return result

    def _save_structured(self, structured: Dict[str, Any], workflow: Optional["Workflow"] = None):
        """Save structured data to JSON file"""
        structured_path = self._path_manager.get_structured_file_path(workflow)
        try:
            self._file_manager.save_json_file(structured_path, structured)
        except IOError as e:
            raise IOError(f"Failed to create directory {structured_path.parent}: {e}")

    def _save_rendered(self, rendered: Dict[str, Any], workflow: Optional["Workflow"] = None):
        """Save rendered data to markdown files (one file per rendered output)"""
        if not rendered:
            return

        for output_name, rendered_item in rendered.items():
            # Skip if builder already wrote the file
            if isinstance(rendered_item, dict) and rendered_item.get("_builder_wrote_file"):
                continue
                
            if isinstance(rendered_item, dict) and "output" in rendered_item:
                rendered_path = self._path_manager.get_rendered_output_path(output_name, workflow)
                self._file_manager.save_text_file(rendered_path, rendered_item["output"])
            elif isinstance(rendered_item, str):
                rendered_path = self._path_manager.get_rendered_output_path(output_name, workflow)
                self._file_manager.save_text_file(rendered_path, rendered_item)

    def load_clarification(self) -> Optional[Dict[str, Any]]:
        """Load clarification data from JSON file. Returns None if file doesn't exist."""
        clarification_path = self._path_manager.get_clarification_file_path()
        return self._file_manager.load_json_file(clarification_path)

    def load_planning(self) -> Optional[Dict[str, Any]]:
        """Load planning data from JSON file. Returns None if file doesn't exist."""
        planning_path = self._path_manager.get_planning_file_path()
        return self._file_manager.load_json_file(planning_path)

    def store_clarification(self, key_questions_answered: Optional[Dict[str, str]] = None,
                          evidence_provided: Optional[Dict[str, str]] = None,
                          additional_questions_answered: Optional[Dict[str, str]] = None) -> Path:
        """Store key questions answered, evidence provided, and additional questions answered. Returns path to saved file."""
        if key_questions_answered is not None:
            self.clarification["key_questions_answered"].update(key_questions_answered)
        if evidence_provided is not None:
            self.clarification["evidence_provided"].update(evidence_provided)
        if additional_questions_answered is not None:
            self.clarification["additional_questions_answered"].update(additional_questions_answered)

        clarification_path = self._path_manager.get_clarification_file_path()
        self._file_manager.save_json_file(clarification_path, self.clarification)
        return clarification_path

    def store_planning(self, decisions_made: Optional[Dict[str, str]] = None,
                      assumptions_made: Optional[Dict[str, str]] = None,
                      behavior_name: Optional[str] = None) -> Path:
        """Store decisions made and assumptions made. Returns path to saved file."""
        if not behavior_name:
            raise ValueError("behavior_name is required for new format planning storage")

        if behavior_name not in self.planning:
            self.planning[behavior_name] = {"decisions_made": {}, "assumptions_made": {}}
        if decisions_made is not None:
            self.planning[behavior_name]["decisions_made"].update(decisions_made)
        if assumptions_made is not None:
            self.planning[behavior_name]["assumptions_made"].update(assumptions_made)

        planning_path = self._path_manager.get_planning_file_path()
        self._file_manager.save_json_file(planning_path, self.planning)
        return planning_path

    def _format_clarification_for_prompt(self, clarification_data: Dict[str, Any]) -> str:
        """Format clarification data for inclusion in prompts"""
        if not clarification_data:
            return "No clarification data available."

        parts = ["**Previous Clarification Decisions:**"]
        parts.append("**MANDATORY: You MUST apply ALL clarification decisions provided below to guide your generation. These decisions contain critical constraints and information that MUST be incorporated into your work.**")
        parts.append("**PRIORITY RULE: If there are contradictions between clarification answers from different stages, the clarification answers from LATER stages TRUMP answers from EARLIER stages.**")

        if "key_questions_answered" in clarification_data:
            parts.append("\n**Key Questions Answered:**")
            for key, answer in clarification_data["key_questions_answered"].items():
                parts.append(f"- {key}: {answer}")

        if "evidence_provided" in clarification_data:
            parts.append("\n**Evidence Provided:**")
            for evidence_type, evidence_content in clarification_data["evidence_provided"].items():
                parts.append(f"- {evidence_type}: {evidence_content}")

        if "additional_questions_answered" in clarification_data:
            parts.append("\n**Additional Questions Answered:**")
            for key, answer in clarification_data["additional_questions_answered"].items():
                parts.append(f"- {key}: {answer}")

        return "\n".join(parts)

    @property
    def output_data(self) -> Dict[str, Any]:
        return self._output_data


class Project:
    workflow: Optional["Workflow"] = None

    def __init__(self, activity_area: Optional[str] = None, base_path: Optional[Path] = None, project_area: Optional[str] = None, agent_name: Optional[str] = None, behaviors: Optional[Dict[str, Any]] = None):
        # If activity_area not provided, try to load from state
        if activity_area is None:
            activity_area = self._load_activity_area_from_state(project_area, agent_name) or "default"
        
        self._activity_area = activity_area
        self._base_path = base_path or Path.cwd()
        self._agent_name = agent_name

        self._workspace_root = self._get_workspace_root()

        initial_project_area = self._initialize_project_area(project_area, base_path)

        self._path_manager = ProjectPathManager(self._workspace_root, initial_project_area, self._activity_area, agent_name)
        self._file_manager = ProjectFileManager(self._path_manager)
        self._activity_logger = ActivityLogger(self._path_manager, self._file_manager)
        self._data_manager = ProjectDataManager(self._path_manager, self._file_manager)

        self._initialize_workflow(behaviors)

        self._data_manager.load_output_data(self.workflow)
        self._activity_logger.load_activity_log()


    def _initialize_project_area(self, project_area: Optional[str], base_path: Optional[Path]) -> str:
        """Initialize project_area - searches for existing project_area in state files or defaults to current dir.
        
        For continuing existing projects: searches for project_area in agent_state.json files.
        For new projects: defaults to current directory (will be presented for confirmation).
        """
        if project_area:
            return str(Path(project_area).resolve())
        
        # Try to load project_area from agent_state.json (for continuing existing projects)
        loaded_area = self._load_project_area_from_state()
        if loaded_area:
            return loaded_area
        
        # Default to current folder name (will be presented for confirmation)
        return str(Path.cwd().resolve())
    
    def _load_project_area_from_state(self) -> Optional[str]:
        """Load project_area from agent_state.json in project area or search directories
        
        Matches story: "Project._load_activity_area_from_state() also searches for activity_area in agent_state.json"
        Searches in same order as _load_activity_area_from_state():
        1. project_area/docs/agent_state.json (if project_area provided - not applicable here)
        2. current_dir/docs/agent_state.json
        3. subdirectories up to 5 levels deep
        """
        if not self._agent_name:
            return None
        
        workspace_root = self._get_workspace_root()
        
        # Try to find agent_state.json in current dir - check activity folder
        current_dir = Path.cwd().resolve()
        activity_path = current_dir / "docs" / "activity" / self._agent_name.lower() / "agent_state.json"
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
        if not self._agent_name:
            return None
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                persisted_area = state.get("project_area")
                agent_name = state.get("agent_name")
                if persisted_area and agent_name == self._agent_name:
                    return str(Path(persisted_area).resolve())
        except (json.JSONDecodeError, IOError, OSError):
            pass
        
        return None

    def _load_activity_area_from_state(self, project_area: Optional[str], agent_name: Optional[str]) -> Optional[str]:
        """Load activity_area from agent_state.json in project area or search directories"""
        if not agent_name:
            return None
        
        workspace_root = self._get_workspace_root()
        
        # First, try to load from project_area if provided
        if project_area:
            project_path = Path(project_area).resolve()
            # Check activity folder: docs/activity/{agent_name}/agent_state.json
            activity_path = project_path / "docs" / "activity" / agent_name.lower() / "agent_state.json"
            if activity_path.exists():
                try:
                    with open(activity_path, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                        if state.get("agent_name") == agent_name and "activity_area" in state:
                            return state["activity_area"]
                except (json.JSONDecodeError, IOError, OSError):
                    pass
        
        # Try to find agent_state.json in current dir - check activity folder
        current_dir = Path.cwd().resolve()
        activity_path = current_dir / "docs" / "activity" / agent_name.lower() / "agent_state.json"
        if activity_path.exists():
            try:
                with open(activity_path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    if state.get("agent_name") == agent_name and "activity_area" in state:
                        return state["activity_area"]
            except (json.JSONDecodeError, IOError, OSError):
                pass
        
        # Try to find in subdirectories (up to 5 levels deep) - check activity folders
        max_depth = 5
        for depth in range(max_depth + 1):
            pattern = "*/" * depth + "docs/activity/*/agent_state.json"
            for state_file in workspace_root.glob(pattern):
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                        if state.get("agent_name") == agent_name and "activity_area" in state:
                            return state["activity_area"]
                except (json.JSONDecodeError, IOError, OSError):
                    pass
        
        return None

    def _initialize_data_structures(self):
        """Initialize all data structures - now handled by helper classes"""
        pass

    def _initialize_workflow(self, behaviors: Optional[Dict[str, Any]]):
        """Initialize workflow with error handling"""
        try:
            self.workflow = Workflow(behaviors=behaviors, project=self)
        except Exception as e:
            import traceback
            raise RuntimeError(f"Failed to create Workflow in Project.__init__: {str(e)}\n{traceback.format_exc()}") from e

        if not hasattr(self, 'workflow') or self.workflow is None:
            raise RuntimeError("Workflow was not created in Project.__init__ - this should never happen")

    def set_behaviors(self, behaviors: Dict[str, Any]):
        """Set behaviors on project so workflow can be initialized"""
        pass

    @property
    def activity_area(self) -> str:
        return self._activity_area

    @activity_area.setter
    def activity_area(self, value: str):
        self._activity_area = value

    @property
    def activity_log(self) -> List[Dict[str, Any]]:
        return self._activity_logger.activity_log

    @property
    def traceability_links(self) -> List[Dict[str, Any]]:
        return self._activity_logger.traceability_links

    @property
    def output_data(self) -> Dict[str, Any]:
        return self._data_manager.output_data

    @property
    def project_area(self) -> str:
        """Get project area path"""
        return self._path_manager.project_area


    def _is_project_area_invalid_or_default(self) -> bool:
        """Check if project_area is invalid or set to default (workspace root)"""
        try:
            workspace_root = self._workspace_root.resolve()
            current_area = Path(self._path_manager.project_area).resolve()

            if current_area == workspace_root:
                return True

            if self._is_outside_workspace(workspace_root, current_area):
                return True

            return False
        except (OSError, ValueError):
            return True

    def _is_outside_workspace(self, workspace_root: Path, current_area: Path) -> bool:
        """Check if current_area is outside workspace root"""
        return workspace_root not in current_area.parents and current_area != workspace_root


    def track_activity(self, status: str, stage: Optional[str] = None, 
                      inputs: Optional[Dict[str, Any]] = None,
                      reasoning: Optional[Dict[str, Any]] = None):
        """Track activity - delegates to ActivityLogger"""
        return self._activity_logger.track_activity(status, stage, inputs, reasoning)

    def create_traceability_link(self, structured: Optional[Dict[str, Any]] = None,
                                rendered: Optional[Dict[str, Any]] = None):
        """Create traceability link - delegates to ActivityLogger"""
        self._activity_logger.create_traceability_link(structured, rendered)

    def _convert_paths_to_strings(self, data: Any) -> Any:
        """Convert Path objects to strings - delegates to ActivityLogger"""
        return self._activity_logger._convert_paths_to_strings(data)

    def _get_planning_file_path(self) -> Path:
        """Get planning file path - delegates to path manager"""
        return self._path_manager.get_planning_file_path()

    def _get_clarification_file_path(self) -> Path:
        """Get clarification file path - delegates to path manager"""
        return self._path_manager.get_clarification_file_path()

    def _get_structured_file_path(self) -> Path:
        """Get structured file path - delegates to path manager"""
        return self._path_manager.get_structured_file_path(self.workflow)

    def _get_rendered_file_path(self) -> Path:
        """Get rendered file path - delegates to path manager"""
        return self._path_manager.get_rendered_file_path()

    def _get_workspace_root(self) -> Path:
        """Get the workspace root directory.

        Uses WORKSPACE_ROOT environment variable if set, otherwise detects from agent.py location.
        This ensures the agent always works from the correct workspace root regardless
        of where the MCP server or Python process is running from.
        """
        import os
        workspace_root = os.getenv("WORKSPACE_ROOT")
        if workspace_root:
            return Path(workspace_root)

        agent_file = Path(__file__).resolve()
        return agent_file.parent.parent.parent.parent

    def _resolve_project_path(self) -> Path:
        """Resolve project_area to an absolute path - delegates to path manager"""
        return self._path_manager.resolve_project_path()

    def store_output(self, structured: Optional[Dict[str, Any]] = None,
                    rendered: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store output data and persist to file system - delegates to data manager"""
        return self._data_manager.store_output(structured, rendered, self.workflow)

    def _load_clarification(self) -> Optional[Dict[str, Any]]:
        """Load clarification data - delegates to data manager"""
        return self._data_manager.load_clarification()

    def _load_planning(self) -> Optional[Dict[str, Any]]:
        """Load planning data - delegates to data manager"""
        return self._data_manager.load_planning()

    def _format_clarification_for_prompt(self, clarification_data: Dict[str, Any]) -> str:
        """Format clarification data for inclusion in prompts - delegates to data manager"""
        return self._data_manager._format_clarification_for_prompt(clarification_data)

    def _format_planning_for_prompt(self, planning_data: Dict[str, Any], current_behavior: Optional[str] = None) -> str:
        """Format planning data for inclusion in prompts, including current and previous behaviors.

        Expects new format: {behavior_name: {decisions_made: {...}, assumptions_made: {...}}, ...}
        Only supports new format - behavior names as top-level keys.
        """
        if not planning_data:
            return "No planning data available."

        parts = self._build_planning_header()
        behavior_keys = self._extract_behavior_keys(planning_data)

        if not behavior_keys:
            return "No planning data available. (Expected behavior-based format: {behavior_name: {decisions_made: {...}, assumptions_made: {...}}})"

        self._add_all_behaviors_planning(parts, planning_data, behavior_keys)
        self._add_current_behavior_planning(parts, planning_data, current_behavior)

        return "\n".join(parts)

    def _build_planning_header(self) -> List[str]:
        """Build header for planning prompt"""
        return [
            "**Previous Planning Decisions and Assumptions:**",
            "**MANDATORY: You MUST apply ALL planning decisions and assumptions provided below to guide your generation. These decisions contain critical constraints and strategies that override default patterns.**",
            "**PRIORITY RULE: If there are contradictions between planning decisions from different stages, the decisions from LATER stages (higher order behaviors) TRUMP decisions from EARLIER stages (lower order behaviors).**",
            "**For example: If 'discovery' stage decisions contradict 'shape' stage decisions, use the 'discovery' decisions.**",
            ""
        ]

    def _extract_behavior_keys(self, planning_data: Dict[str, Any]) -> List[str]:
        """Extract behavior keys from planning data"""
        return [k for k in planning_data.keys() 
                if k not in ["decisions_made", "assumptions_made"] and isinstance(planning_data[k], dict)]

    def _add_all_behaviors_planning(self, parts: List[str], planning_data: Dict[str, Any], behavior_keys: List[str]):
        """Add planning data for all behaviors"""
        for behavior_name in behavior_keys:
            behavior_data = planning_data[behavior_name]
            if isinstance(behavior_data, dict):
                parts.append(f"\n**{behavior_name.upper()} Stage:**")
                self._add_decisions_and_assumptions(parts, behavior_data)

    def _add_decisions_and_assumptions(self, parts: List[str], behavior_data: Dict[str, Any]):
        """Add decisions and assumptions to parts list"""
        if "decisions_made" in behavior_data and behavior_data["decisions_made"]:
            parts.append("  **Decisions Made:**")
            for key, value in behavior_data["decisions_made"].items():
                parts.append(f"    - {key}: {value}")

        if "assumptions_made" in behavior_data and behavior_data["assumptions_made"]:
            parts.append("  **Assumptions Made:**")
            for key, value in behavior_data["assumptions_made"].items():
                parts.append(f"    - {key}: {value}")

    def _add_current_behavior_planning(self, parts: List[str], planning_data: Dict[str, Any], current_behavior: Optional[str]):
        """Add current behavior planning with emphasis"""
        if not current_behavior or current_behavior not in planning_data:
            return

        parts.extend([
            f"\n**CRITICAL: Current behavior '{current_behavior}' decisions and assumptions MUST be followed:**",
            "**YOU MUST apply these decisions directly to your generation work. These override any default patterns.**",
            "**PRIORITY RULE: If there are contradictions between planning decisions from different stages, the decisions from LATER stages (higher order behaviors) TRUMP decisions from EARLIER stages (lower order behaviors).**",
            "**For example: If 'discovery' stage decisions contradict 'shape' stage decisions, use the 'discovery' decisions.**"
        ])

        current_data = planning_data[current_behavior]
        if isinstance(current_data, dict):
            if "decisions_made" in current_data and current_data["decisions_made"]:
                parts.append("  **Decisions:**")
                for key, value in current_data["decisions_made"].items():
                    parts.append(f"    - {key}: {value}")
                parts.append("  **ACTION REQUIRED:** Review each decision above. If a decision specifies selective drill-down (e.g., 'focus on 1-2 stories'), you MUST enumerate only those stories and use 'story_count' notation for all others.")

            if "assumptions_made" in current_data and current_data["assumptions_made"]:
                parts.append("  **Assumptions:**")
                for key, value in current_data["assumptions_made"].items():
                    parts.append(f"    - {key}: {value}")

    def store_clarification(self, key_questions_answered: Optional[Dict[str, str]] = None,
                          evidence_provided: Optional[Dict[str, str]] = None,
                          additional_questions_answered: Optional[Dict[str, str]] = None) -> Path:
        """Store clarification data - delegates to data manager"""
        return self._data_manager.store_clarification(key_questions_answered, evidence_provided, additional_questions_answered)

    def store_planning(self, decisions_made: Optional[Dict[str, str]] = None,
                      assumptions_made: Optional[Dict[str, str]] = None,
                      behavior_name: Optional[str] = None) -> Path:
        """Store planning data - delegates to data manager"""
        return self._data_manager.store_planning(decisions_made, assumptions_made, behavior_name)

    def update_project_area(self, new_project_area: str, agent_instance=None):
        """Update project_area and move ONLY known project output files (docs/, structured.json, etc.)

        IMPORTANT: Only moves files if old project area is clearly a test/temp directory.
        Never touches workspace directories like agents/, behaviors/, src/, etc.
        """
        import shutil
        import tempfile

        old_project_path = Path(self._path_manager.project_area)
        new_project_path = Path(new_project_area)

        old_path_str = str(old_project_path).lower()
        temp_dir = tempfile.gettempdir().lower()
        is_test_or_temp = (
            'test' in old_path_str or 
            'temp' in old_path_str or
            old_path_str.startswith(temp_dir)
        )

        workspace_source_dirs = {'agents', 'behaviors', 'src', '.cursor', '.git'}
        is_workspace_dir = any(old_project_path.parts[0] == dir_name for dir_name in workspace_source_dirs if len(old_project_path.parts) > 0)

        PROJECT_OUTPUT_DIRS = {'docs', 'output'}
        PROJECT_OUTPUT_FILES = {'structured.json', 'rendered.md'}

        new_project_path.mkdir(parents=True, exist_ok=True)

        if (old_project_path.exists() and 
            old_project_path != new_project_path and 
            is_test_or_temp and 
            not is_workspace_dir):
            for item in old_project_path.iterdir():
                should_move = False
                if item.is_dir() and item.name in PROJECT_OUTPUT_DIRS:
                    should_move = True
                elif item.is_file() and item.name in PROJECT_OUTPUT_FILES:
                    should_move = True

                if not should_move:
                    continue

                new_item = new_project_path / item.name
                try:
                    if item.is_dir():
                        if new_item.exists():
                            shutil.copytree(item, new_item, dirs_exist_ok=True)
                            shutil.rmtree(item)
                        else:
                            shutil.move(str(item), str(new_item))
                    else:
                        if new_item.exists():
                            new_item.unlink()
                        shutil.move(str(item), str(new_item))
                except (PermissionError, OSError):
                    continue

        self._path_manager.project_area = str(new_project_path)
        self._base_path = new_project_path
        
        # Matches story: "Project saves project_area to agent_state.json"
        self.save_project_area_to_state()
        
        # Matches story: "Project creates necessary directory structure"
        self.create_directory_structure()

        output_data = self._data_manager.output_data
        if output_data.get("structured"):
            self._data_manager.store_output(structured=output_data["structured"], workflow=self.workflow)
        if output_data.get("rendered"):
            self._data_manager.store_output(rendered=output_data["rendered"], workflow=self.workflow)

        if agent_instance:
            agent_instance.project._path_manager.project_area = str(new_project_path)
            agent_instance.project._base_path = new_project_path
            if agent_instance.current_behavior:
                content = agent_instance.current_behavior.content
                if content.structured:
                    agent_instance.project.store_output(structured=content.structured)
                if content.rendered:
                    agent_instance.project.store_output(rendered=content.rendered)

    def _get_agent_state_file_path(self, project_path: Optional[Path] = None) -> Optional[Path]:
        """Get path to agent state file - delegates to path manager"""
        return self._path_manager.get_agent_state_file_path(project_path)

    def _find_project_area_from_state(self) -> Optional[str]:
        """Find project_area by searching for agent_state.json starting from workspace root"""
        if not self._agent_name:
            return None

        workspace_root = self._workspace_root.resolve()

        # First, check the agent's own directory (highest priority)
        agent_dir = workspace_root / "agents" / self._agent_name.lower()
        agent_state_file = agent_dir / "docs" / "agent_state.json"
        if agent_state_file.exists():
            try:
                with open(agent_state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    persisted_area = state.get("project_area")
                    agent_name = state.get("agent_name")
                    if persisted_area and agent_name == self._agent_name:
                        if not Path(persisted_area).is_absolute():
                            persisted_path = workspace_root / persisted_area
                        else:
                            persisted_path = Path(persisted_area)
                        persisted_path = persisted_path.resolve()

                        if "Temp" not in str(persisted_path) and "tmp" not in str(persisted_path).lower():
                            if persisted_path.exists():
                                return str(persisted_path)
            except (json.JSONDecodeError, IOError, OSError):
                pass

        # Then search all other locations - check activity folders
        max_depth = 5
        for depth in range(max_depth + 1):
            pattern = "*/" * depth + "docs/activity/*/agent_state.json"
            for state_file in workspace_root.glob(pattern):
                # Skip if we already checked the agent's own directory
                if state_file == agent_state_file:
                    continue
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                        persisted_area = state.get("project_area")
                        agent_name = state.get("agent_name")
                        if persisted_area and agent_name == self._agent_name:
                            if not Path(persisted_area).is_absolute():
                                persisted_path = workspace_root / persisted_area
                            else:
                                persisted_path = Path(persisted_area)
                            persisted_path = persisted_path.resolve()

                            if "Temp" in str(persisted_path) or "tmp" in str(persisted_path).lower():
                                continue
                            if not persisted_path.exists():
                                continue
                            return str(persisted_path)
                except (json.JSONDecodeError, IOError, OSError):
                    pass

        return None

    def _load_project_area(self) -> Optional[str]:
        """Load persisted project_area from current directory's docs/{activity_area}/agent_state.json
        Simplified to only check current directory per story flow.
        """
        if not self._agent_name:
            return None

        current_dir = Path.cwd().resolve()
        # Check activity folder: docs/activity/{agent_name}/agent_state.json
        activity_path = current_dir / "docs" / "activity" / self._agent_name.lower() / "agent_state.json"
        if activity_path.exists():
            return self._load_project_area_from_file(activity_path)

        return None

    def save_project_area_to_state(self):
        """Save project_area to agent_state.json in project area.
        
        Matches story: "Project saves project_area to agent_state.json in project area"
        """
        if not self._agent_name:
            return

        project_path = self._resolve_project_path()
        state_path = self._get_agent_state_file_path(project_path)
        if state_path:
            state_path.parent.mkdir(parents=True, exist_ok=True)
            state = {
                "project_area": self._path_manager.project_area,
                "agent_name": self._agent_name,
                "activity_area": self._activity_area
            }
            try:
                with open(state_path, 'w', encoding='utf-8') as f:
                    json.dump(state, f, indent=2)
            except IOError:
                pass
    
    def _persist_project_area(self):
        """Legacy method name - delegates to save_project_area_to_state()"""
        self.save_project_area_to_state()
    
    def create_directory_structure(self):
        """Create necessary directory structure in project area.
        
        Matches story: "Project creates necessary directory structure"
        """
        project_path = self._resolve_project_path()
        if project_path:
            # Create main project directory
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create docs directory
            docs_dir = project_path / "docs"
            docs_dir.mkdir(parents=True, exist_ok=True)
            
            # Create activity directory structure
            activity_dir = self._get_activity_dir()
            if activity_dir:
                activity_dir.mkdir(parents=True, exist_ok=True)
    
    def present_project_area_to_user(self) -> Optional[Dict[str, Any]]:
        """Present determined project_area to user for confirmation.
        
        SIMPLIFIED: Always presents for confirmation on new projects.
        Matches story: "Project presents determined project_area to user for confirmation"
        
        Returns:
            Dict with message and suggested_project_area for user confirmation, or None if already confirmed
        """
        determined_area = self._path_manager.project_area
        
        # Check if project_area is already set and confirmed (not default current dir)
        # If project_area is explicitly set (not default), check if it's been persisted
        if determined_area and determined_area != str(Path.cwd().resolve()):
            # Check if there's an agent_state.json with this project_area - means it's been set
            activity_dir = self._get_activity_dir()
            agent_state_path = activity_dir / "agent_state.json"
            if agent_state_path.exists():
                try:
                    with open(agent_state_path, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                        saved_area = state.get("project_area")
                        agent_name_match = state.get("agent_name") == self._agent_name
                        # Compare resolved paths
                        if saved_area and agent_name_match:
                            saved_resolved = str(Path(saved_area).resolve())
                            determined_resolved = str(Path(determined_area).resolve())
                            if saved_resolved == determined_resolved:
                                # Project area is already set and persisted - no confirmation needed
                                return None
                except (json.JSONDecodeError, IOError, OSError):
                    pass
        
        # SIMPLIFIED: Present for confirmation on new projects
        # Load template from agent.json
        base_config_path = Path(__file__).parent.parent / "agent.json"
        message_template = ""
        if base_config_path.exists():
            try:
                with open(base_config_path, 'r', encoding='utf-8') as f:
                    base_config = json.load(f)
                    prompt_templates = base_config.get("prompt_templates", {})
                    project_init = prompt_templates.get("project_initialization", {})
                    message_template = project_init.get("project_area_required", {}).get("template", "")
            except (json.JSONDecodeError, IOError, OSError, KeyError):
                pass
        
        # Fallback if template not found
        if not message_template:
            message_template = "**Project Area Required**\n\nBefore starting the workflow, you must confirm the project location.\n\nSuggested project area: `{{example_project_path}}`\n\nPlease confirm this location or provide a different path using the `agent_set_project_area` tool."
        
        # Replace template variables
        message = message_template.replace("{{example_project_path}}", determined_area)
        
        return {
            "needs_confirmation": True,
            "message": message,
            "suggested_project_area": determined_area
        }


    def _get_activity_dir(self) -> Path:
        """Get the activity directory path - delegates to path manager"""
        return self._path_manager.get_activity_dir()

    def _load_activity_log(self):
        """Load activity log from file system if it exists"""
        activity_path = self._get_activity_dir() / "activity.json"
        if activity_path.exists():
            try:
                with open(activity_path, 'r', encoding='utf-8') as f:
                    self._activity_log = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._activity_log = []
        else:
            self._activity_log = []

class Workflow:

    def __init__(self, config: Dict[str, Any] = None, behaviors: Dict[str, Any] = None, project=None):
        if behaviors:
            self.stages = self._derive_stages_from_behaviors(behaviors)
            self._behaviors = behaviors
        else:
            self.stages = config.get("stages", []) if config else []
            self._behaviors = {}
        self._current_stage: Optional[str] = None
        self._current_action: Optional[Action] = None
        self._stage_data: Dict[str, Any] = {}
        self._context_provided: bool = False
        self._project = project
        self._workflow_state: Dict[str, Any] = {
            "current_behavior_name": None,
            "current_action_name": None
        }
        if project:
            project.workflow = self
            self._load_state()

    @property
    def workflow_state(self) -> Dict[str, Any]:
        """Get current workflow state"""
        return self._workflow_state

    def save_state(self, behavior_name: Optional[str] = None, action_name: Optional[str] = None):
        """Save workflow state to file"""
        if behavior_name is None:
            behavior_name = self._current_stage
        if action_name is None and self._current_action:
            action_name = self._current_action.name

        self._workflow_state = {
            "current_behavior_name": behavior_name,
            "current_action_name": action_name
        }

        # Project should always be set, but check for safety
        if not self._project:
            return

        state_path = self._get_state_path()
        try:
            state_path.parent.mkdir(parents=True, exist_ok=True)
            with open(state_path, 'w', encoding='utf-8') as f:
                json.dump(self._workflow_state, f, indent=2)
        except (IOError, OSError, PermissionError) as e:
            # Log error but don't fail - workflow state save is not critical
            # In debug mode, could log: print(f"Failed to save workflow state to {state_path}: {e}")
            pass

    def _load_state(self):
        """Load workflow state from project_area if it exists"""
        if not self._project:
            return

        state_path = self._get_state_path()
        if state_path.exists():
            try:
                with open(state_path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self._workflow_state = {
                        "current_behavior_name": state.get("current_behavior_name"),
                        "current_action_name": state.get("current_action_name")
                    }
            except (json.JSONDecodeError, IOError, KeyError):
                self._workflow_state = {
                    "current_behavior_name": None,
                    "current_action_name": None
                }

    def _get_state_path(self) -> Path:
        """Get path to workflow state file in project_area"""
        if not self._project:
            # Try to find project area from current directory
            current_dir = Path.cwd()
            activity_path = current_dir / "docs" / "activity" / "story_bot" / "workflow_state.json"
            if activity_path.parent.exists():
                return activity_path
            return Path("docs") / "activity" / "story_bot" / "workflow_state.json"
        try:
            project_path = self._project._resolve_project_path()
            if not project_path:
                # Fallback to current directory if project path can't be resolved
                return Path.cwd() / "docs" / "activity" / "story_bot" / "workflow_state.json"
            activity_area = self._project._activity_area if hasattr(self._project, '_activity_area') else "story_bot"
            return project_path / "docs" / "activity" / activity_area / "workflow_state.json"
        except (AttributeError, Exception):
            # Fallback if project path resolution fails
            return Path.cwd() / "docs" / "activity" / "story_bot" / "workflow_state.json"

    @property
    def current_behavior(self):
        """Get current behavior based on current stage"""
        if not self._current_stage or not self._behaviors:
            return None
        return self._behaviors.get(self._current_stage)

    @property
    def current_action(self):
        """Get current action from current behavior"""
        behavior = self.current_behavior
        if not behavior or not hasattr(behavior, 'actions'):
            return None
        if not hasattr(behavior.actions, 'current_action'):
            return None
        return behavior.actions.current_action

    def _derive_stages_from_behaviors(self, behaviors: Dict[str, Any]) -> List[str]:
        """Derive workflow stages from behaviors sorted by order"""
        if not behaviors:
            return []

        sorted_behaviors = sorted(
            behaviors.items(),
            key=lambda x: (x[1].order, x[0])
        )
        return [stage_name for stage_name, _ in sorted_behaviors]

    @property
    def current_stage(self) -> Optional[str]:
        return self._current_stage

    @property
    def current_behavior_name(self) -> Optional[str]:
        """Get current behavior name (alias for current_stage for compatibility)"""
        return self._current_stage

    @property
    def behavior_names(self) -> List[str]:
        """Get list of behavior names in workflow order"""
        return self.stages

    @property
    def stage_data(self) -> Dict[str, Any]:
        return self._stage_data

    @property
    def context_provided(self) -> bool:
        return self._context_provided

    @context_provided.setter
    def context_provided(self, value: bool):
        self._context_provided = value

    def get_pre_actions_to_execute(self, behavior_name: str) -> List[Dict[str, Any]]:
        """Get list of pre_actions that need to be executed for a behavior.
        Returns list of pre_action configs that should be executed."""
        behavior = self._behaviors.get(behavior_name) if self._behaviors else None
        if not behavior or not hasattr(behavior, 'pre_actions') or not behavior.pre_actions:
            return []

        actions_to_execute = []
        for pre_action_config in behavior.pre_actions:
            if not pre_action_config.get("auto_trigger", False):
                continue

            target_behavior_name = pre_action_config.get("action")

            condition = pre_action_config.get("condition")
            if condition == "not_completed":
                if self._is_behavior_completed(target_behavior_name):
                    pass

            actions_to_execute.append({
                "behavior": target_behavior_name,
                "config": pre_action_config
            })

        return actions_to_execute

    def _is_behavior_completed(self, behavior_name: str) -> bool:
        """Check if a behavior has been completed.
        A behavior is considered completed if it has been started and all its mandatory actions are done."""
        if not self._project:
            return False


        current_behavior = self._workflow_state.get("current_behavior_name")
        if current_behavior and current_behavior != behavior_name:
            if behavior_name in self.stages and current_behavior in self.stages:
                behavior_index = self.stages.index(behavior_name)
                current_index = self.stages.index(current_behavior)
                if current_index > behavior_index:
                    return True

        return False

    def start(self, stage: str, _executing_pre_action: bool = False):
        """Start a behavior, automatically executing any pre_actions first.

        Args:
            stage: Name of the behavior to start
            _executing_pre_action: Internal flag to prevent infinite recursion
        """
        if not _executing_pre_action:
            self._execute_pre_actions(stage)

        self._start_behavior(stage)

    def _execute_pre_actions(self, stage: str):
        """Execute pre_actions for a behavior"""
        pre_actions_to_execute = self.get_pre_actions_to_execute(stage)
        for pre_action_info in pre_actions_to_execute:
            target_behavior_name = pre_action_info["behavior"]
            if target_behavior_name in self._behaviors:
                self.start(target_behavior_name, _executing_pre_action=True)
                self._execute_behavior_workflow(target_behavior_name)

    def _start_behavior(self, stage: str):
        """Start a behavior and initialize its state"""
        self._current_stage = stage
        behavior = self.current_behavior

        if behavior:
            self._current_action = behavior.initialize_for_workflow()
        else:
            self._current_action = None

        self._stage_data = {
            "name": stage,
            "state": "start",
            "order": self._get_stage_order(stage)
        }

        if self._project:
            self._project.track_activity("start", stage)
            action_name = self._current_action.name if self._current_action else None
            self.save_state(stage, action_name)

    def _execute_behavior_workflow(self, behavior_name: str):
        """Execute all actions in a behavior's workflow.
        This is used to fully execute pre_action behaviors."""
        if behavior_name not in self._behaviors:
            return

        target_behavior = self._behaviors[behavior_name]

        original_state = self._save_current_state()
        try:
            self._set_temporary_state(behavior_name, target_behavior)
            target_behavior.execute_all_actions(self)
        finally:
            self._restore_state(original_state)

    def _save_current_state(self) -> Dict[str, Any]:
        """Save current workflow state for restoration"""
        return {
            "stage": self._current_stage,
            "action": self._current_action
        }

    def _set_temporary_state(self, behavior_name: str, behavior: "Behavior"):
        """Set temporary state for behavior execution"""
        self._current_stage = behavior_name
        self._current_action = behavior.initialize_for_workflow()

    def _restore_state(self, original_state: Dict[str, Any]):
        """Restore workflow state from saved state"""
        self._current_stage = original_state.get("stage")
        original_action = original_state.get("action")
        self._current_action = original_action

        if self._current_stage and self._current_stage in self._behaviors:
            original_behavior = self._behaviors[self._current_stage]
            if original_behavior and hasattr(original_behavior, 'actions') and original_action:
                original_behavior.actions.move_to_action(original_action.name, force=True)

    def _execute_builder_action(self, behavior: "Behavior", action: "Action"):
        """Execute a builder action (e.g., build_structure for arrange behavior)."""
        if not hasattr(behavior.content, 'builder') or not behavior.content.builder:
            return

        builder_path = behavior.content.builder
        try:
            parts = builder_path.split('.')
            module_path = '.'.join(parts[:-1])
            function_name = parts[-1]

            import importlib
            module = importlib.import_module(module_path)
            builder_func = getattr(module, function_name)

            if self._project:
                project_area = str(self._project.project_area) if self._project.project_area else None
                structured_content_path = None

                if project_area:
                    project_path = Path(project_area)
                    structured_json_path = project_path / "docs" / "stories" / "structured.json"
                    if structured_json_path.exists():
                        structured_content_path = str(structured_json_path)

                if structured_content_path:
                    result = builder_func(project_area, structured_content_path, create_story_files=False)
                    if result and self._project:
                        behavior.content.structured = result
        except Exception as e:
            if self._project:
                self._project.track_activity("error", f"Pre-action builder execution failed: {str(e)}")

    def next_stage(self):
        if self._current_stage and self.stages:
            current_index = self.stages.index(self._current_stage)
            if current_index < len(self.stages) - 1:
                self._current_stage = self.stages[current_index + 1]
                self._stage_data = {
                    "name": self._current_stage,
                    "state": "next",
                    "order": current_index + 2
                }
                if self._project:
                    self._project.track_activity("next", self._current_stage)

    def approve_current(self):
        if self._current_stage:
            self._stage_data["state"] = "approved"
            if self._project:
                self._project.track_activity("approved", self._current_stage)

    def skip_current(self):
        if self._current_stage:
            self._stage_data["state"] = "skip"
            if self._project:
                self._project.track_activity("skip", self._current_stage)

    def start_next_stage(self) -> Optional[str]:
        if not self.stages:
            return None

        if self._context_provided:
            return self._get_next_stage_for_context()

        return self.stages[0]

    def _get_next_stage_for_context(self) -> str:
        if not self._current_stage:
            return self.stages[0]

        current_index = self.stages.index(self._current_stage)
        if current_index < len(self.stages) - 1:
            return self.stages[current_index + 1]

        return self.stages[0]

    def _get_stage_order(self, stage: str) -> int:
        if stage in self.stages:
            return self.stages.index(stage) + 1
        return 0

    def move_to_action(self, action_name: str, force: bool = False) -> Optional[Action]:
        """Move to a specific action within current behavior"""
        behavior = self.current_behavior
        if not behavior or not hasattr(behavior, 'actions'):
            return None
        action = behavior.actions.move_to_action(action_name, force=force)
        if action:
            self.save_state(self._current_stage, action_name)
        return action

    def next_action(self, force: bool = False) -> Optional[Action]:
        """Move to next action in current behavior"""
        behavior = self.current_behavior
        if not behavior or not hasattr(behavior, 'actions'):
            return None
        action = behavior.actions.next_action(force=force)
        if action:
            self.save_state(self._current_stage, action.name)
        elif not action:
            self.save_state(self._current_stage, None)
        return action

    def next_behavior(self, force: bool = False) -> Optional[str]:
        """Move to next behavior in workflow"""
        if not self._current_stage or not self.stages:
            return None

        if not force:
            behavior = self.current_behavior
            if behavior and hasattr(behavior, 'actions'):
                current_action = behavior.actions.current_action
                if current_action:
                    if not behavior.actions.can_advance():
                        mandatory = behavior.actions.is_action_mandatory(current_action.name)
                        if mandatory:
                            raise ValueError(
                                f"Cannot move to next behavior: mandatory action '{current_action.name}' "
                                f"in behavior '{self._current_stage}' is not complete. Use force=True to override."
                            )

        current_index = self.stages.index(self._current_stage)
        if current_index < len(self.stages) - 1:
            next_stage = self.stages[current_index + 1]
            self.start(next_stage)
            self._stage_data["state"] = "next"
            if self._project:
                self._project.track_activity("next", next_stage)
            return next_stage

        return None

    def start_next_behavior(self) -> Optional[str]:
        """Start the next behavior in workflow sequence"""
        if not self.stages:
            return None

        if self._current_stage:
            current_index = self.stages.index(self._current_stage)
            if current_index < len(self.stages) - 1:
                next_stage = self.stages[current_index + 1]
                self.start(next_stage)
                return next_stage
        else:
            if self.stages:
                self.start(self.stages[0])
                return self.stages[0]

        return None



class Diagnostic(ABC):
    """Base class for diagnostics that validate structured content."""

    @abstractmethod
    def validate(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validate structured content and return list of violations.

        Args:
            content: Structured content dictionary to validate

        Returns:
            List of violation dictionaries, each containing:
            - message: Description of the violation
            - rule: Optional rule description
            - line_number: Optional line number
            - location: Optional location path (e.g., "epics[0].features[0].name")
        """
        pass

    def _create_violation(
        self,
        message: str,
        rule: Optional[str] = None,
        line_number: int = 0,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Helper method to create a violation dictionary."""
        violation = {
            "message": message,
            "line_number": line_number
        }
        if rule:
            violation["rule"] = rule
        if location:
            violation["location"] = location
        return violation


class VerbNounConsistencyDiagnostic(Diagnostic):
    """Validates verb-noun format for story elements."""

    def validate(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for verb-noun consistency in epics, features, and stories."""
        violations = []
        rule = "Use verb-noun format for all story elements (epic names, feature names, story titles)"

        task_words = ["implement", "create", "build", "develop", "design", "set up", "configure", "deploy"]

        epics = content.get("epics", [])
        for epic_idx, epic in enumerate(epics):
            epic_name = epic.get("name", "")
            if any(epic_name.lower().startswith(word) for word in task_words):
                violations.append(self._create_violation(
                    message=f'Epic name "{epic_name}" uses task-oriented language instead of verb-noun format (e.g., "Submit Order" not "Implement Order Submission")',
                    rule=rule,
                    location=f"epics[{epic_idx}].name"
                ))

            features = epic.get("features", [])
            for feature_idx, feature in enumerate(features):
                feature_name = feature.get("name", "")
                if any(feature_name.lower().startswith(word) for word in task_words):
                    violations.append(self._create_violation(
                        message=f'Feature name "{feature_name}" uses task-oriented language instead of verb-noun format',
                        rule=rule,
                        location=f"epics[{epic_idx}].features[{feature_idx}].name"
                    ))

                stories = feature.get("stories", [])
                for story_idx, story in enumerate(stories):
                    story_name = story.get("name", "")
                    if any(story_name.lower().startswith(word) for word in task_words):
                        violations.append(self._create_violation(
                            message=f'Story name "{story_name}" uses task-oriented language instead of verb-noun format',
                            rule=rule,
                            location=f"epics[{epic_idx}].features[{feature_idx}].stories[{story_idx}].name"
                        ))

        return violations


class StoryShapeDiagnostic(Diagnostic):
    """Validates story sizing falls within 3-12 day range."""

    def validate(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check that story sizing is within 3-12 day range."""
        violations = []
        rule = "Size stories to fall within 3-12 day effort range for effective planning and frequent delivery"

        epics = content.get("epics", [])
        for epic_idx, epic in enumerate(epics):
            features = epic.get("features", [])
            for feature_idx, feature in enumerate(features):
                stories = feature.get("stories", [])
                for story_idx, story in enumerate(stories):
                    sizing = story.get("sizing", "")
                    if sizing:
                        import re
                        match = re.search(r'(\d+)', str(sizing))
                        if match:
                            days = int(match.group(1))
                            if days < 3 or days > 12:
                                violations.append(self._create_violation(
                                    message=f'Story "{story.get("name", "")}" has sizing of {days} days, which is outside the 3-12 day range',
                                    rule=rule,
                                    location=f"epics[{epic_idx}].features[{feature_idx}].stories[{story_idx}].sizing"
                                ))

        return violations


class MarketIncrementsDiagnostic(Diagnostic):
    """Validates that marketable increments are defined."""

    def validate(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check that increments are defined with business value."""
        violations = []
        rule = "Identify marketable increments with business priorities and relative sizing"

        increments = content.get("increments", [])
        if not increments or len(increments) == 0:
            violations.append(self._create_violation(
                message="No marketable increments defined. Increments should identify business value and priorities",
                rule=rule,
                location="increments"
            ))

        return violations


class BaseBuilder:
    def __init__(self, project_path: Path, structured_content_path: Optional[Path] = None):
        self.project_path = Path(project_path)
        self.structured_content_path = structured_content_path or self._find_structured_json()
    
    def _find_structured_json(self) -> Optional[Path]:
        structured_path = self.project_path / "docs" / "stories" / "structured.json"
        if structured_path.exists():
            return structured_path
        return None
    
    def _load_story_graph(self) -> Dict[str, Any]:
        if not self.structured_content_path or not self.structured_content_path.exists():
            raise FileNotFoundError(
                f"Structured content file not found: {self.structured_content_path}. "
                "Ensure prioritization phase has been completed."
            )
        
        with open(self.structured_content_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _slugify(self, text: str) -> str:
        return text.lower().replace(' ', '-').replace('_', '-')


class DrawIOBuilder(BaseBuilder):
    def __init__(self, project_path: Path, structured_content_path: Optional[Path] = None, template_path: Optional[Path] = None):
        super().__init__(project_path, structured_content_path)
        self.template_path = template_path or self._find_template()
    
    def _find_template(self) -> Optional[Path]:
        return None
    
    def _load_template(self) -> Optional[str]:
        if self.template_path and self.template_path.exists():
            return self.template_path.read_text(encoding='utf-8')
        return None
