# Exploration: Continue Existing Project

**Increment:** Continue Existing Project  
**Priority:** 2  
**Relative Size:** Medium  
**Approach:** User-System Behavioral  
**Focus:** Component-to-component interactions during workflow state restoration and project resumption

---

## Domain Acceptance Criteria

### Concepts

**Project State Persistence**
- Persisted state in agent_state.json containing project_area, activity_area, and agent_name
- Located in docs/agent_state.json within project area, current directory, or subdirectories (up to 5 levels deep)
- Used to identify existing projects and restore project context
- Project area must be confirmed by user even if found, defaulted, or loaded from state

**Workflow State Persistence**
- Persisted workflow state in workflow_state.json containing current_behavior_name and current_action_name
- Located in project_area/docs/workflow_state.json (note: path is docs/workflow_state.json, not docs/activity/workflow_state.json)
- Used to restore workflow to last action (e.g., clarification, planning, build_structure, render_output, validate)

**State File Search Priority**
- Search order: 1) project_area/docs/agent_state.json (if project_area provided), 2) current_dir/docs/agent_state.json, 3) subdirectories up to 5 levels deep
- First match with matching agent_name wins
- Both Agent._determine_activity_area() and Project._load_activity_area_from_state() perform searches

**Activity Area**
- Determined from agent_state.json if found, otherwise defaults to agent_name.lower()
- Represents the subdirectory within project_area where agent-specific artifacts are stored
- Must match agent_name in state file to be considered valid

### Behaviors

**State Discovery**
- Agent searches for agent_state.json when project_area not explicitly provided
- Project also searches for activity_area in agent_state.json during initialization
- Both components can independently discover state, but Agent's determination takes precedence

**Workflow Restoration**
- Workflow state is loaded automatically during Workflow initialization via _load_state()
- Agent._restore_workflow_state() restores workflow to last action after behaviors are loaded
- Restoration only occurs if workflow_state.json exists and contains valid current_behavior_name and current_action_name

**Workflow Skip Logic**
- Agent._start_workflow_if_needed() checks if workflow already has current_stage and current_action set
- If workflow state was restored, _start_workflow_if_needed() is skipped
- Allows immediate continuation from last action without restarting workflow

**User Confirmation**
- Required for project_area determination (always), even when project_area is discovered from agent_state.json
- MCP Server checks for project area confirmation via agent.check_project_area_confirmation() and returns needs_confirmation: true with message and suggested_project_area
- User must confirm or suggest different project area before workflow can proceed
- Confirmation happens before workflow state restoration

**User Continuation**
- After project area confirmation and workflow state restoration, AI Chat can immediately call agent_get_instructions() to get instructions for current action
- User can continue working from where they left off

### Rules

**State File Location**
- agent_state.json: project_area/docs/agent_state.json, current_dir/docs/agent_state.json, or subdirectories (5 levels deep)
- workflow_state.json: project_area/docs/workflow_state.json (not in activity subdirectory)

**State Validation**
- agent_state.json must contain matching agent_name to be considered valid
- workflow_state.json must contain current_behavior_name that exists in behaviors dictionary
- workflow_state.json must contain current_action_name that exists in behavior's actions

**Restoration Precedence**
- If workflow_state.json exists and is valid, workflow is restored to that state
- If workflow_state.json is missing or invalid, workflow starts from beginning (first behavior, first action)
- Restoration happens after behaviors are loaded but before workflow start

**Project Area Discovery**
- If project_area not provided, Agent searches for agent_state.json to discover project_area
- If found, project_area is loaded from state file
- If not found, defaults to current directory (same as new project flow)
- User must confirm project_area even if discovered from state file (same as new project flow)

**Project Area Confirmation**
- Project.present_project_area_to_user() always presents determined project_area for confirmation
- MCP Server returns needs_confirmation: true with message and suggested_project_area when project area needs confirmation
- User confirms via agent_set_project_area tool or by providing different project area
- Workflow cannot proceed until project area is confirmed

---

## Behavioral Acceptance Criteria

### Story 1: User Requests to Continue Project

1. When user requests to continue working on an existing project in Cursor/VS Code chat (e.g., "continue project", "resume work", "pick up where I left off", or by referencing project area), then AI Chat receives and processes the request

2. When AI Chat processes continue request, then AI Chat identifies continuation keywords (e.g., "continue", "resume", "existing project", project area references) and determines Story Agent is needed

### Story 2: AI Chat Invokes Story Agent MCP

1. When AI Chat determines Story Agent is needed for continuation, then AI Chat selects appropriate MCP tool (agent_get_state for checking current state, agent_get_instructions for getting workflow instructions) and prepares tool call with agent_name='stories'

2. When AI Chat prepares MCP tool call, then AI Chat invokes Story Agent MCP Server via selected tool and MCP Server receives tool call with agent_name parameter

### Story 3: Initialize Agent

1. When MCP Server receives tool call from AI Chat, then MCP Server requests Agent instance from AgentStateManager

2. When AgentStateManager receives request for Agent instance, then AgentStateManager checks if Agent instance already exists in cache, and if not found creates new Agent instance

3. When AgentStateManager creates new Agent instance, then AgentStateManager instantiates Agent with agent_name='stories' and optional project_area parameter (may be None if not explicitly provided), handles any initialization errors, stores instance in cache, and returns the Agent instance

4. When Agent initializes, then Agent sets up configuration file paths: base agent configuration at agents/base/agent.json, agent directory at workspace_root/agents, and agent-specific configuration at agents/{agent_name}/agent.json

### Story 4: Load Project State from agent_state.json

5. When Agent initializes without explicit project_area, then Agent calls _determine_activity_area() which searches for agent_state.json in: 1) project_area/docs/agent_state.json (if project_area provided), 2) current_dir/docs/agent_state.json, 3) subdirectories up to 5 levels deep using pattern "*/" * depth + "docs/agent_state.json"

6. When Agent._determine_activity_area() finds agent_state.json, then Agent reads state file, validates agent_name matches 'stories', extracts activity_area from state if present, and returns activity_area (or defaults to agent_name.lower() if not found)

7. When Agent creates Project instance, then Agent instantiates Project with activity_area (from _determine_activity_area()), agent_name='stories', and optional project_area parameter, and delegates project area determination to Project

8. When Project initializes, then Project calls _load_activity_area_from_state() which also searches for agent_state.json in: 1) project_area/docs/agent_state.json (if project_area provided), 2) current_dir/docs/agent_state.json, 3) subdirectories up to 5 levels deep, and if found loads activity_area and project_area from state file

### Story 5: Confirm Project Area

9. When MCP Server calls agent_get_state() after Project initialization, then MCP Server calls agent.check_project_area_confirmation() which delegates to Project.present_project_area_to_user(), and Project presents determined project_area to user for confirmation (even if loaded from state file)

10. When Project presents project_area to user, then Project loads message template from agents/base/agent.json prompt_templates.project_initialization.project_area_required.template, replaces {{example_project_path}} with determined project_area, and returns confirmation data with needs_confirmation: true, message, and suggested_project_area

11. When MCP Server receives confirmation data from Project, then MCP Server returns response to AI Chat with needs_confirmation: true, message containing suggested project area, and suggested_project_area value

12. When AI Chat receives confirmation response from MCP Server, then AI Chat presents message to user in chat window showing suggested project area and requesting confirmation or alternative project area

13. When user confirms project area (either accepts suggested or provides different value), then AI Chat calls agent_set_project_area tool with confirmed project_area value, MCP Server updates Project with confirmed project_area, Project saves project_area to agent_state.json, and Project creates necessary directory structure

14. When user confirms or suggests different project area, then Project updates project_area if user suggested different value, saves project_area to agent_state.json in project area, creates necessary directory structure, and completes initialization

### Story 6: Restore Workflow State

15. When Agent loads configuration and behaviors after project area confirmation, then Agent calls _initialize_components() which creates Workflow instance, sets workflow._behaviors to behaviors dictionary, calls workflow._derive_stages_from_behaviors() to set up stages, and calls _restore_workflow_state()

16. When Workflow initializes, then Workflow calls _load_state() which checks if project_area/docs/workflow_state.json exists, and if found reads state file and extracts current_behavior_name and current_action_name into workflow._workflow_state dictionary

17. When Agent._restore_workflow_state() is called, then Agent checks if workflow.workflow_state contains current_behavior_name, and if not found returns early (no restoration needed)

18. When workflow state contains current_behavior_name, then Agent validates behavior_name exists in behaviors dictionary, sets workflow._current_stage to behavior_name, gets behavior from behaviors dictionary, and extracts current_action_name from workflow state

19. When Agent has behavior and action_name, then Agent validates action_name exists in behavior.actions, calls behavior.actions.move_to_action(action_name, force=True) to get action object, and if action found sets workflow._current_action to action object

20. When workflow state is successfully restored, then workflow._current_stage and workflow._current_action are set to last saved values, allowing workflow to resume from exact point where user left off

### Story 7: Resume from Last Action

21. When Agent._initialize_components() completes workflow state restoration, then Agent checks if _needs_project_area() (project area not yet confirmed), and if false calls _start_workflow_if_needed()

22. When Agent._start_workflow_if_needed() is called, then Agent checks if workflow._current_stage is already set (from restoration), and if set skips workflow start logic and returns early

23. When workflow state was restored and _start_workflow_if_needed() is skipped, then workflow remains at restored state (current_stage and current_action set), and Agent completes initialization without restarting workflow

24. When AgentStateManager synchronizes workflow, then AgentStateManager checks if Project has workflow attribute, and if missing or None sets Project.workflow to Agent.workflow, and if Project workflow references different object updates Project.workflow to reference Agent.workflow

25. When MCP Server synchronizes project workflow, then MCP Server ensures Project workflow reference matches Agent workflow reference, and updates Project workflow if needed

26. When AI Chat calls agent_get_instructions() after project area confirmation and workflow restoration, then MCP Server calls agent.instructions property which delegates to workflow.current_action.instructions, and AI Chat receives instructions for the current action (e.g., clarification, planning, build_structure, render_output, validate)

27. When user receives instructions for current action, then user can immediately continue working from where they left off, with all workflow context (behavior, action, previous outputs) available and ready for continuation

---

## Source Material

**Shape Phase:**
- Primary source: Story Agent requirements and architecture
- Sections referenced: Continue Existing Project feature
- Date generated: [Current date]
- Context: Initial story shaping for workflow continuation

**Discovery Phase:**
- Source: Inherited from Shape phase
- Discovery Refinements: Detailed breakdown into 7 stories with 27 component interaction points
- Additional sections referenced: agents/base/src/agent.py (Agent._determine_activity_area, Agent._restore_workflow_state, Agent.check_project_area_confirmation, Project._load_activity_area_from_state, Project.present_project_area_to_user, Workflow._load_state), agents/base/src/agent_mcp_server.py
- Areas elaborated: State file search logic, project area confirmation flow, workflow state restoration, continuation flow

**Exploration Phase:**
- Source: Inherited from Discovery phase
- Acceptance Criteria: Domain AC aggregated from all 7 stories, Behavioral AC for 7 stories (User Requests to Continue Project, AI Chat Invokes Story Agent MCP, Initialize Agent, Load Project State from agent_state.json, Confirm Project Area, Restore Workflow State, Resume from Last Action)
- Specific sections: State file search priority, project area confirmation requirement (even when loaded from state), workflow state restoration logic, skip logic for workflow start, continuation flow

