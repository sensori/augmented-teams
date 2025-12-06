# Exploration: Initialize Story Agent Workflow

**Increment:** Initialize Story Agent Workflow  
**Priority:** 1  
**Relative Size:** Medium  
**Approach:** User-System Behavioral  
**Focus:** Component-to-component interactions during workflow initialization

---

## Domain Acceptance Criteria

### Concepts

**Project Area**
- Root directory for project files where agent artifacts are stored
- For new projects: defaults to current folder name (no state files exist)
- For existing projects: searched in agent_state.json files with priority: project_area → current_dir → subdirs (5 levels deep)
- Can be explicitly set or discovered from agent_state.json
- Must be confirmed by user even if found, defaulted, or loaded from state

**Agent State**
- Persisted state in agent_state.json containing project_area and agent_name
- Located in docs/agent_state.json within project area, current directory, or subdirectories

**Workflow State**
- Persisted workflow state in workflow_state.json containing current_behavior_name and current_action_name
- Used to restore workflow to last action

**Configuration Hierarchy**
- Base agent.json (shared) → Agent-specific agent.json (behaviors, rules, guardrails)

### Behaviors

**Agent Instance**
- Cached per AgentStateManager
- Created on first access, reused on subsequent calls
- Synchronized with Project workflow

**Workflow**
- Derived from behaviors dictionary sorted by order property
- Stages determined from behavior order
- Can be restored from state or started fresh

**User Confirmation**
- Required at 3 points: project_area determination (always), configuration loaded, workflow state (always)
- Even when values found in state files

### Rules

**State File Search Priority**
- Search order: 1) project_area/docs/agent_state.json, 2) current_dir/docs/agent_state.json, 3) subdirectories up to 5 levels deep
- First match with matching agent_name wins

**Project Area Default**
- For new projects (no state files exist), defaults to current folder name
- User must confirm even if defaulted

**Workflow Synchronization**
- Agent.workflow and Project.workflow must reference same object
- AgentStateManager and MCP Server ensure synchronization

**Configuration Path Resolution**
- Agent config path is set to agents/{agent_name}/agent.json

---

## Behavioral Acceptance Criteria

### Story 1: User Adds Context to Chat

1. When user selects and attaches documents, models, text descriptions, or diagrams to Cursor/VS Code chat window, then system receives and stores context for story shaping

2. When user types request message in chat window (e.g., 'start shaping', 'plan new project', 'build story map'), then AI Chat receives and processes the request

### Story 2: AI Chat Invokes Story Agent MCP

1. When AI Chat processes user message and attached documents, then AI Chat identifies story shaping keywords (e.g., 'shaping', 'planning', 'story map', 'new project') and determines Story Agent is needed

2. When AI Chat determines Story Agent is needed, then AI Chat selects appropriate MCP tool (agent_get_state for checking current state, agent_get_instructions for getting workflow instructions) and prepares tool call with agent_name='stories'

3. When AI Chat prepares MCP tool call, then AI Chat invokes Story Agent MCP Server via selected tool and MCP Server receives tool call with agent_name parameter

### Story 3: Initialize Agent

1. When MCP Server receives tool call from AI Chat, then MCP Server requests Agent instance from AgentStateManager

2. When AgentStateManager receives request for Agent instance, then AgentStateManager checks if Agent instance already exists in cache, and if not found creates new Agent instance

3. When AgentStateManager creates new Agent instance, then AgentStateManager instantiates Agent with agent_name='stories', handles any initialization errors, stores instance in cache, and returns the Agent instance

4. When Agent initializes, then Agent sets up configuration file paths: base agent configuration at agents/base/agent.json, agent directory at workspace_root/agents, and agent-specific configuration at agents/{agent_name}/agent.json

### Story 4: Initialize Project

5. When Agent creates Project for new project, then Agent instantiates Project with agent_name='stories' and optional project_area parameter, and delegates project area determination to Project

6. When Project initializes for new project, then Project determines project_area (defaults to current folder name since no state files exist), and presents determined project_area to user for confirmation

7. When user confirms or suggests new project area, then Project updates project_area if user suggested different value, saves project_area to agent_state.json in project area, creates necessary directory structure, and completes initialization

### Story 5: Initialize Behavior and Workflow

8. When Project is finished initializing, then Agent loads base configuration by reading agents/base/agent.json, extracts base instruction templates and base trigger words, stores them for use in future instruction generation

9. When Agent has loaded base configuration, then Agent loads Story Agent configuration by reading agents/stories/agent.json, extracts agent-specific instruction templates and agent-specific trigger words, creates Rules objects from rules configuration, creates Behavior objects for each workflow behavior (shape, prioritization, discovery, exploration, specification) with their order, guardrails, rules, actions, and content configurations, stores behaviors in dictionary, and presents configuration summary to user for confirmation

10. When Agent connects Workflow to Project, then Agent links Workflow instance (created during Project initialization) to Agent, and passes behaviors dictionary to Workflow

11. When Workflow receives behaviors dictionary, then Workflow sorts behaviors by their order property (shape=1, prioritization=2, discovery=4, etc.), creates ordered list of stage names, and sets up workflow stages

12. When Agent starts workflow for new project, then Agent calls Workflow to start, Workflow gets first behavior from sorted stages (shape behavior with order=1), initializes first action of that behavior (clarification action), sets workflow current_stage and current_action, and Agent presents workflow state to user for confirmation

13. When AgentStateManager synchronizes workflow, then AgentStateManager checks if Project has workflow attribute, and if missing or None sets Project.workflow to Agent.workflow, and if Project workflow references different object updates Project.workflow to reference Agent.workflow

14. When MCP Server synchronizes project workflow, then MCP Server ensures Project workflow reference matches Agent workflow reference, and updates Project workflow if needed

---

## Source Material

**Shape Phase:**
- Primary source: Story Agent requirements and architecture
- Sections referenced: Initialize Story Agent Workflow feature
- Date generated: [Current date]
- Context: Initial story shaping for workflow initialization

**Discovery Phase:**
- Source: Inherited from Shape phase
- Discovery Refinements: Detailed breakdown into 10 features with 26 component interaction points
- Additional sections referenced: agents/base/src/agent.py, agents/base/src/agent_mcp_server.py
- Areas elaborated: Component-to-component interactions, method calls, file loading, state management

**Exploration Phase:**
- Source: Inherited from Discovery phase
- Acceptance Criteria: Domain AC aggregated from all 10 features, Behavioral AC for 5 stories (Initialize Agent, Initialize Project, Initialize Behavior and Workflow)
- Specific sections: User confirmation requirements, state file search priority, workflow synchronization rules

