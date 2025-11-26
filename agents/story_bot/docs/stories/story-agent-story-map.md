# Story Map: Story Agent

**Navigation:** [📊 Increments](../increments/story-agent-story-map-increments.md)

**File Name**: `story-agent-story-map.md`
**Location**: `{solution_folder}/docs/stories/map/story-agent-story-map.md`

> **CRITICAL MARKDOWN FORMATTING**: All tree structure lines MUST end with TWO SPACES (  ) for proper line breaks. Without two spaces, markdown will wrap lines together into one long line, breaking the visual tree structure.

> **CRITICAL HIERARCHY FORMATTING**: The 🎯 **Start Story Development Session** (9 features, ~40 stories)  

├─ ⚙️ **Initialize Story Agent Workflow** (~5 stories)  
│  ├─ 📝 Story: User Adds Context to Chat  
│  │  *User adds documents, models, text descriptions, diagrams to Cursor/VS Code chat window and requests to start shaping/planning/building a new project*  
│  ├─ 📝 Story: AI Chat Invokes Story Agent MCP  
│  │  *AI Chat detects story shaping request and calls Story Agent MCP Server via agent_get_state or agent_get_instructions tool*  
│  ├─ 📝 Story: Initialize Agent  
│  │  *MCP Server receives tool call from AI Chat and requests Agent instance from AgentStateManager, which creates and initializes Agent with agent_name='stories', sets up configuration file paths*  
│  ├─ 📝 Story: Initialize Project  
│  │  *Agent creates Project instance and delegates project area determination to Project. Project determines project_area for new project, presents to user for confirmation, saves to agent_state.json, and completes initialization*  
│  └─ 📝 Story: Initialize Behavior and Workflow  
│     *After Project initialization, Agent loads base and Story Agent configurations (instruction templates, trigger words, Rules, Behaviors), connects Workflow to Project, Workflow sets up stages, and Agent starts workflow at first behavior and action*  
│  
├─ ⚙️ **Continue Existing Project** (~4 stories)  
│  ├─ 📝 Story: User Requests to Continue Project  
│  │  *User requests to continue working on an existing project in Cursor/VS Code chat, either by explicitly asking to continue or by referencing the project area*  
│  ├─ 📝 Story: Load Project State from agent_state.json  
│  │  *When Agent.__init__ is called without explicit project_area, Agent._determine_activity_area() searches for agent_state.json in current directory, then subdirectories (up to 5 levels deep). Project._load_activity_area_from_state() also searches for activity_area in agent_state.json. If found, loads project_area and activity_area from state file*  
│  ├─ 📝 Story: Restore Workflow State  
│  │  *Agent._restore_workflow_state() loads workflow_state.json from project_area/docs/activity/workflow_state.json, extracts current_behavior_name and current_action_name, calls workflow.move_to_behavior() and workflow.move_to_action() to restore workflow to last action (e.g., clarification, planning, build_structure, render_output, validate)*  
│  └─ 📝 Story: Resume from Last Action  
│     *After workflow state is restored, Agent._initialize_components() skips _start_workflow_if_needed() since workflow already has current_stage and current_action set. AI Chat can immediately call agent_get_instructions() to get instructions for the current action, allowing user to continue from where they left off*  
│  
├─ ⚙️ **Load Configuration from JSON** (~4 stories)  
│  ├─ 📝 Story: Load Base Agent Config  
│  │  *Agent._load_base_agent_config() loads agents/base/agent.json and retrieves prompt_templates and trigger_words into Agent._prompt_templates and Agent._base_trigger_words*  
│  ├─ 📝 Story: Load Story Agent Config  
│  │  *Agent._load_agent_config() loads agents/stories/agent.json, creates Rules from rules config, initializes behaviors dictionary by creating Behavior objects for each behavior (shape, prioritization, discovery, exploration, specification) with order, guardrails, rules, actions, content configs*  
│  ├─ 📝 Story: Initialize Workflow from Behaviors  
│  │  *Agent._initialize_components() creates Workflow instance, sets workflow._behaviors to behaviors dictionary, calls workflow._derive_stages_from_behaviors() which sorts behaviors by order property and returns stage names list, sets workflow.stages to derived stages*  
│  └─ 📝 Story: Start Workflow at Shape Behavior  
│     *Agent._start_workflow_if_needed() calls workflow.start_next_stage() to get first behavior (shape: order=1), then workflow.start(shape) which calls behavior.initialize_for_workflow() to reset actions and return first action (clarification), sets workflow._current_stage="shape" and workflow._current_action to clarification action*  
│  
├─ ⚙️ **Clarify Context Requirements** (~6 stories)  
│  ├─ 📝 Story: Load Clarification Questions from JSON  
│  │  *When AI Chat calls agent_get_instructions(), MCP Server calls agent.instructions property which delegates to workflow.current_action.instructions. Clarification action generates instructions by calling behavior.guardrails.requirements_clarification_instructions which loads key_questions and evidence lists from agents/stories/agent.json behaviors.shape.guardrails.required_context*  
│  ├─ 📝 Story: AI Attempts to Answer Questions  
│  │  *AI Chat receives instructions with key_questions array and evidence array, AI analyzes provided context (documents, models, text) and attempts to answer each question based on available information*  
│  ├─ 📝 Story: Present Questions and Answers to User  
│  │  *AI Chat presents questions asked, answers provided, gap analysis, and requests corrections in chat window for user review*  
│  ├─ 📝 Story: User Provides Feedback  
│  │  *User reviews presented questions/answers, provides corrections or additional detail for incomplete answers, confirms answers are complete*  
│  ├─ 📝 Story: MCP Saves Clarification Answers  
│  │  *AI Chat calls agent_store_clarification(key_questions_answered, evidence_provided, additional_questions_answered). MCP Server calls agent.store() which delegates to current action (clarification).store() which calls Project.store_clarification() to update Project.clarification dict and save to project_area/docs/clarification.json*  
│  └─ 📝 Story: Track Clarification Activity  
│     *Project.store_clarification() calls Project.track_activity("store_clarification", behavior_name, data) which creates activity entry and appends to activity_log, saves activity_log to project_area/docs/activity/activity.json*  
│  
├─ ⚙️ **Plan Story Development Approach** (~5 stories)  
│  ├─ 📝 Story: Load Planning Assumptions from JSON  
│  │  *When moving to planning action, behavior.guardrails.get_planning_instructions() loads typical_assumptions and decision_making_criteria from agents/stories/agent.json behaviors.shape.guardrails.planning, formats instructions with BaseInstructions.planning_intro*  
│  ├─ 📝 Story: Present Assumptions and Decision Criteria  
│  │  *AI Chat receives planning instructions with assumptions list and decision_criteria array (each with question, outcome, options), presents to user in chat window*  
│  ├─ 📝 Story: User Selects Decision Options  
│  │  *User reviews assumptions, selects preferred options from decision criteria (e.g., story_drill_down: "Dig deep on system interactions", flow_scope: "Journey level with component detail"), confirms approach*  
│  ├─ 📝 Story: MCP Saves Planning Decisions  
│  │  *AI Chat calls agent_store_planning(decisions_made, assumptions_made). MCP Server calls agent.store() which delegates to planning action.store() which calls Project.store_planning() to update Project.planning dict with shape section containing decisions_made and assumptions_made, saves to project_area/docs/planning.json*  
│  └─ 📝 Story: Track Planning Activity  
│     *Project.store_planning() calls Project.track_activity("store_planning", behavior_name, data) which creates activity entry and appends to activity_log, saves to project_area/docs/activity/activity.json*  
│  
├─ ⚙️ **Build Structured Story Map Content** (~4 stories)  
│  ├─ 📝 Story: Load Story Graph Schema  
│  │  *When moving to build_structure action, Content.build_instructions includes instructions to load story_graph.json schema from agents/stories/story_graph.json to understand required structure (solution, epics, features, stories, increments)*  
│  ├─ 📝 Story: Generate Structured JSON Content  
│  │  *AI Chat follows build_instructions which include agent-level rules, behavior-level rules, and structured_content instructions from agents/stories/agent.json. AI generates structured JSON following story_graph.json schema with solution, epics array, features array, stories array, increments array*  
│  ├─ 📝 Story: MCP Saves Structured Content  
│  │  *AI Chat calls agent_store_structured(structured). MCP Server calls agent.store(structured=structured) which sets current_behavior.content.structured, triggering Content.structured setter which calls Content.store(). Content.store() calls Project.store_output(structured=structured) which saves JSON to project_area/docs/stories/structured.json via Project._save_structured()*  
│  └─ 📝 Story: Create Traceability Link  
│     *Project.store_output() calls Project.create_traceability_link(structured, rendered) which links last activity entry in activity_log to output data (structured.json path), updates activity_log and saves to project_area/docs/activity/activity.json*  
│  
├─ ⚙️ **Render Story Map to Markdown** (~5 stories)  
│  ├─ 📝 Story: Load Story Map Template  
│  │  *When moving to render_output action, Content.transform_instructions includes output instructions specifying template: "templates/story-map-decomposition-template.md" from agents/stories/templates/, transformer: "story_agent_transform_story_map_to_markdown"*  
│  ├─ 📝 Story: Transform Structured JSON to Markdown  
│  │  *AI Chat follows transform_instructions, loads structured JSON from project_area/docs/stories/structured.json, loads template from agents/stories/templates/story-map-decomposition-template.md, applies structured content data to template variables (solution, epic_hierarchy, source_material), generates markdown document*  
│  ├─ 📝 Story: MCP Saves Rendered Markdown  
│  │  *AI Chat calls agent_store_rendered(rendered). MCP Server calls agent.store(rendered=rendered) which sets current_behavior.content.rendered["story_map"], triggering Content.rendered setter which calls Content.store(). Content.store() calls Project.store_output(rendered={"story_map": {"output": rendered, "template": "templates/story-map-decomposition-template.md"}}) which saves markdown to project_area/docs/stories/map/{product_name}-story-map.md via Project._save_rendered()*  
│  ├─ 📝 Story: Track Rendering Activity  
│  │  *Project.store_output() calls Project.track_activity("store_rendered", behavior_name, {"output": "story_map"}) which creates activity entry and appends to activity_log, saves to project_area/docs/activity/activity.json*  
│  └─ 📝 Story: Create Output Traceability Link  
│     *Project.create_traceability_link() links last activity entry to rendered output data (story_map markdown file path), updates activity_log and saves to project_area/docs/activity/activity.json*  
│  
├─ ⚙️ **Validate Story Map Content** (~4 stories)  
│  ├─ 📝 Story: Execute Code Diagnostics  
│  │  *When moving to validate action, Content.execute_diagnostic() is called with diagnostic_ref from rule config (e.g., "story_agent_validate_verb_noun_consistency"). Content loads diagnostic from agents/stories/src/story_agent.py (VerbNounConsistencyDiagnostic, StoryShapeDiagnostic, MarketIncrementsDiagnostic), calls diagnostic.validate(structured) which scans structured JSON for violations*  
│  ├─ 📝 Story: Assemble Validation Prompt  
│  │  *Content generates validation_instructions by assembling prompt from agents/base/agent.json prompt_templates.validate.validation_instructions template, includes Content Data, examples from rules, violations found by code diagnostics, rules from agent-level and behavior-level configs*  
│  ├─ 📝 Story: AI Evaluates and Generates Report  
│  │  *AI Chat receives validation prompt, evaluates structured content against all rules, generates validation report with violations list, specific examples, recommendations for fixing violations*  
│  └─ 📝 Story: Track Validation Activity  
│     *Content.execute_diagnostic() calls Project.track_activity("execute_diagnostic", None, {"diagnostic": diagnostic_ref, "violations": len(violations)}) which creates activity entry and appends to activity_log, saves to project_area/docs/activity/activity.json*  
│  
└─ ⚙️ **Build Folder Structure from Story Graph** (~3 stories)  
│  ├─ 📝 Story: Load Structured Story Graph  
│  │  *StoryFolderStructureBuilder.build() loads structured JSON from project_area/docs/stories/structured.json via _load_story_graph(), parses epics array and features array*  
│  ├─ 📝 Story: Create Epic and Feature Folders  
│  │  *StoryFolderStructureBuilder iterates epics, creates folder "🎯 {epic_name}" in project_area/docs/stories/map/, iterates features, creates folder "⚙️ {feature_name}" in epic folder, handles sub_epics recursively*  
│  └─ 📝 Story: Archive Obsolete Folders  
│     *StoryFolderStructureBuilder compares existing epic folders with epics in structured JSON, moves obsolete folders to project_area/docs/stories/map/z_archive/{timestamp}/, never deletes folders*   section MUST use tree structure characters to show hierarchy:
> - Use `│` (vertical line) for continuing branches
> - Use `├─` (branch) for items that have siblings below them
> - Use `└─` (end branch) for the last item in a group
> - Epic format: `🎯 **Epic Name** (X features, ~Y stories)  `
> - Feature format: `├─ ⚙️ **Feature Name** (~Z stories)  ` or `└─ ⚙️ **Feature Name** (~Z stories)  ` for last feature
> - Story format (when present): `│  ├─ 📝 Story: [Verb-Noun Name]  ` followed by `│  │  *[Component interaction description]*  ` on the next line, or `│  └─ 📝 Story: [Verb-Noun Name]  ` for last story
> - **MANDATORY STORY NAMING FORMAT**: All story names MUST follow Actor-Verb-Noun format:
>   - Story name: Concise Verb-Noun format (e.g., "Create Mob from Selected Tokens", "Display Mob Grouping in Combat Tracker", "Execute Mob Attack with Strategy")
>   - Description: Italicized component interaction description showing component-to-component interactions (e.g., "*GM selects multiple minion tokens on canvas and Mob manager creates mob with selected tokens and assigns random leader*")
> - Example structure:
>   ```
>   🎯 **Epic Name** (2 features, ~8 stories)  
>   │  
>   ├─ ⚙️ **Feature 1** (~5 stories)  
>   │  ├─ 📝 Story: Create Mob from Selected Tokens  
>   │  │  *GM selects multiple minion tokens on canvas and Mob manager creates mob*  
>   │  └─ 📝 Story: Display Mob Grouping  
>   │     *Combat Tracker receives mob creation notification and updates display*  
>   │  
>   └─ ⚙️ **Feature 2** (~3 stories)  
>      └─ 📝 Story: Execute Mob Attack  
>         *Combat Tracker moves to mob leader's turn and Mob manager forwards action*  
>   ```

## System Purpose
Enable product owners, business analysts, and developers to use AI in a structured way for story shaping, discovery, exploration, and specification following Agile by Design practices. Accelerate story development from weeks/months to hours by providing structured AI assistance integrated into Cursor/VS Code environment.

---

## Legend
- 🎯 **Epic** - High-level capability
- 📂 **Sub-Epic** - Sub-capability (when epic has > 9 features)
- ⚙️ **Feature** - Cohesive set of functionality
- 📝 **Story** - Small increment of behavior (3-12d)

---

## Story Map Structure

🎯 **Start Story Development Session** (9 features, ~38 stories)  

├─ ⚙️ **Initialize Story Agent Workflow** (~3 stories)  
│  ├─ 📝 Story: User Adds Context to Chat  
│  │  *User adds documents, models, text descriptions, diagrams to Cursor/VS Code chat window and requests to start shaping/planning/building a new project*  
│  ├─ 📝 Story: AI Chat Invokes Story Agent MCP  
│  │  *AI Chat detects story shaping request and calls Story Agent MCP Server via agent_get_state or agent_get_instructions tool*  
│  └─ 📝 Story: MCP Server Initializes Agent  
│     *Story Agent MCP Server (agent_mcp_server.py) calls AgentStateManager.get_agent() which creates Agent instance with agent_name="stories", loads agent.json from agents/stories/agent.json. Agent._determine_activity_area() searches for activity_area in agent_state.json (current dir, subdirs, or project_area), defaults to "stories" if not found. Creates Project with determined activity_area, initializes Workflow with behaviors dictionary from agent.json*  
│  
├─ ⚙️ **Continue Existing Project** (~4 stories)  
│  ├─ 📝 Story: User Requests to Continue Project  
│  │  *User requests to continue working on an existing project in Cursor/VS Code chat, either by explicitly asking to continue or by referencing the project area*  
│  ├─ 📝 Story: Load Project State from agent_state.json  
│  │  *When Agent.__init__ is called without explicit project_area, Agent._determine_activity_area() searches for agent_state.json in current directory, then subdirectories (up to 5 levels deep). Project._load_activity_area_from_state() also searches for activity_area in agent_state.json. If found, loads project_area and activity_area from state file*  
│  ├─ 📝 Story: Restore Workflow State  
│  │  *Agent._restore_workflow_state() loads workflow_state.json from project_area/docs/activity/workflow_state.json, extracts current_behavior_name and current_action_name, calls workflow.move_to_behavior() and workflow.move_to_action() to restore workflow to last action (e.g., clarification, planning, build_structure, render_output, validate)*  
│  └─ 📝 Story: Resume from Last Action  
│     *After workflow state is restored, Agent._initialize_components() skips _start_workflow_if_needed() since workflow already has current_stage and current_action set. AI Chat can immediately call agent_get_instructions() to get instructions for the current action, allowing user to continue from where they left off*  
│  
├─ ⚙️ **Load Configuration from JSON** (~4 stories)  
│  ├─ 📝 Story: Load Base Agent Config  
│  │  *Agent._load_base_agent_config() loads agents/base/agent.json and retrieves prompt_templates and trigger_words into Agent._prompt_templates and Agent._base_trigger_words*  
│  ├─ 📝 Story: Load Story Agent Config  
│  │  *Agent._load_agent_config() loads agents/stories/agent.json, creates Rules from rules config, initializes behaviors dictionary by creating Behavior objects for each behavior (shape, prioritization, discovery, exploration, specification) with order, guardrails, rules, actions, content configs*  
│  ├─ 📝 Story: Initialize Workflow from Behaviors  
│  │  *Agent._initialize_components() creates Workflow instance, sets workflow._behaviors to behaviors dictionary, calls workflow._derive_stages_from_behaviors() which sorts behaviors by order property and returns stage names list, sets workflow.stages to derived stages*  
│  └─ 📝 Story: Start Workflow at Shape Behavior  
│     *Agent._start_workflow_if_needed() calls workflow.start_next_stage() to get first behavior (shape: order=1), then workflow.start(shape) which calls behavior.initialize_for_workflow() to reset actions and return first action (clarification), sets workflow._current_stage="shape" and workflow._current_action to clarification action*  
│  
├─ ⚙️ **Clarify Context Requirements** (~6 stories)  
│  ├─ 📝 Story: Load Clarification Questions from JSON  
│  │  *When AI Chat calls agent_get_instructions(), MCP Server calls agent.instructions property which delegates to workflow.current_action.instructions. Clarification action generates instructions by calling behavior.guardrails.requirements_clarification_instructions which loads key_questions and evidence lists from agents/stories/agent.json behaviors.shape.guardrails.required_context*  
│  ├─ 📝 Story: AI Attempts to Answer Questions  
│  │  *AI Chat receives instructions with key_questions array and evidence array, AI analyzes provided context (documents, models, text) and attempts to answer each question based on available information*  
│  ├─ 📝 Story: Present Questions and Answers to User  
│  │  *AI Chat presents questions asked, answers provided, gap analysis, and requests corrections in chat window for user review*  
│  ├─ 📝 Story: User Provides Feedback  
│  │  *User reviews presented questions/answers, provides corrections or additional detail for incomplete answers, confirms answers are complete*  
│  ├─ 📝 Story: MCP Saves Clarification Answers  
│  │  *AI Chat calls agent_store_clarification(key_questions_answered, evidence_provided, additional_questions_answered). MCP Server calls agent.store() which delegates to current action (clarification).store() which calls Project.store_clarification() to update Project.clarification dict and save to project_area/docs/clarification.json*  
│  └─ 📝 Story: Track Clarification Activity  
│     *Project.store_clarification() calls Project.track_activity("store_clarification", behavior_name, data) which creates activity entry and appends to activity_log, saves activity_log to project_area/docs/activity/activity.json*  
│  
├─ ⚙️ **Plan Story Development Approach** (~5 stories)  
│  ├─ 📝 Story: Load Planning Assumptions from JSON  
│  │  *When moving to planning action, behavior.guardrails.get_planning_instructions() loads typical_assumptions and decision_making_criteria from agents/stories/agent.json behaviors.shape.guardrails.planning, formats instructions with BaseInstructions.planning_intro*  
│  ├─ 📝 Story: Present Assumptions and Decision Criteria  
│  │  *AI Chat receives planning instructions with assumptions list and decision_criteria array (each with question, outcome, options), presents to user in chat window*  
│  ├─ 📝 Story: User Selects Decision Options  
│  │  *User reviews assumptions, selects preferred options from decision criteria (e.g., story_drill_down: "Dig deep on system interactions", flow_scope: "Journey level with component detail"), confirms approach*  
│  ├─ 📝 Story: MCP Saves Planning Decisions  
│  │  *AI Chat calls agent_store_planning(decisions_made, assumptions_made). MCP Server calls agent.store() which delegates to planning action.store() which calls Project.store_planning() to update Project.planning dict with shape section containing decisions_made and assumptions_made, saves to project_area/docs/planning.json*  
│  └─ 📝 Story: Track Planning Activity  
│     *Project.store_planning() calls Project.track_activity("store_planning", behavior_name, data) which creates activity entry and appends to activity_log, saves to project_area/docs/activity/activity.json*  
│  
├─ ⚙️ **Build Structured Story Map Content** (~4 stories)  
│  ├─ 📝 Story: Load Story Graph Schema  
│  │  *When moving to build_structure action, Content.build_instructions includes instructions to load story_graph.json schema from agents/stories/story_graph.json to understand required structure (solution, epics, features, stories, increments)*  
│  ├─ 📝 Story: Generate Structured JSON Content  
│  │  *AI Chat follows build_instructions which include agent-level rules, behavior-level rules, and structured_content instructions from agents/stories/agent.json. AI generates structured JSON following story_graph.json schema with solution, epics array, features array, stories array, increments array*  
│  ├─ 📝 Story: MCP Saves Structured Content  
│  │  *AI Chat calls agent_store_structured(structured). MCP Server calls agent.store(structured=structured) which sets current_behavior.content.structured, triggering Content.structured setter which calls Content.store(). Content.store() calls Project.store_output(structured=structured) which saves JSON to project_area/docs/stories/structured.json via Project._save_structured()*  
│  └─ 📝 Story: Create Traceability Link  
│     *Project.store_output() calls Project.create_traceability_link(structured, rendered) which links last activity entry in activity_log to output data (structured.json path), updates activity_log and saves to project_area/docs/activity/activity.json*  
│  
├─ ⚙️ **Render Story Map to Markdown** (~5 stories)  
│  ├─ 📝 Story: Load Story Map Template  
│  │  *When moving to render_output action, Content.transform_instructions includes output instructions specifying template: "templates/story-map-decomposition-template.md" from agents/stories/templates/, transformer: "story_agent_transform_story_map_to_markdown"*  
│  ├─ 📝 Story: Transform Structured JSON to Markdown  
│  │  *AI Chat follows transform_instructions, loads structured JSON from project_area/docs/stories/structured.json, loads template from agents/stories/templates/story-map-decomposition-template.md, applies structured content data to template variables (solution, epic_hierarchy, source_material), generates markdown document*  
│  ├─ 📝 Story: MCP Saves Rendered Markdown  
│  │  *AI Chat calls agent_store_rendered(rendered). MCP Server calls agent.store(rendered=rendered) which sets current_behavior.content.rendered["story_map"], triggering Content.rendered setter which calls Content.store(). Content.store() calls Project.store_output(rendered={"story_map": {"output": rendered, "template": "templates/story-map-decomposition-template.md"}}) which saves markdown to project_area/docs/stories/map/{product_name}-story-map.md via Project._save_rendered()*  
│  ├─ 📝 Story: Track Rendering Activity  
│  │  *Project.store_output() calls Project.track_activity("store_rendered", behavior_name, {"output": "story_map"}) which creates activity entry and appends to activity_log, saves to project_area/docs/activity/activity.json*  
│  └─ 📝 Story: Create Output Traceability Link  
│     *Project.create_traceability_link() links last activity entry to rendered output data (story_map markdown file path), updates activity_log and saves to project_area/docs/activity/activity.json*  
│  
├─ ⚙️ **Validate Story Map Content** (~4 stories)  
│  ├─ 📝 Story: Execute Code Diagnostics  
│  │  *When moving to validate action, Content.execute_diagnostic() is called with diagnostic_ref from rule config (e.g., "story_agent_validate_verb_noun_consistency"). Content loads diagnostic from agents/stories/src/story_agent.py (VerbNounConsistencyDiagnostic, StoryShapeDiagnostic, MarketIncrementsDiagnostic), calls diagnostic.validate(structured) which scans structured JSON for violations*  
│  ├─ 📝 Story: Assemble Validation Prompt  
│  │  *Content generates validation_instructions by assembling prompt from agents/base/agent.json prompt_templates.validate.validation_instructions template, includes Content Data, examples from rules, violations found by code diagnostics, rules from agent-level and behavior-level configs*  
│  ├─ 📝 Story: AI Evaluates and Generates Report  
│  │  *AI Chat receives validation prompt, evaluates structured content against all rules, generates validation report with violations list, specific examples, recommendations for fixing violations*  
│  └─ 📝 Story: Track Validation Activity  
│     *Content.execute_diagnostic() calls Project.track_activity("execute_diagnostic", None, {"diagnostic": diagnostic_ref, "violations": len(violations)}) which creates activity entry and appends to activity_log, saves to project_area/docs/activity/activity.json*  
│  
└─ ⚙️ **Build Folder Structure from Story Graph** (~3 stories)  
│  ├─ 📝 Story: Load Structured Story Graph  
│  │  *StoryFolderStructureBuilder.build() loads structured JSON from project_area/docs/stories/structured.json via _load_story_graph(), parses epics array and features array*  
│  ├─ 📝 Story: Create Epic and Feature Folders  
│  │  *StoryFolderStructureBuilder iterates epics, creates folder "🎯 {epic_name}" in project_area/docs/stories/map/, iterates features, creates folder "⚙️ {feature_name}" in epic folder, handles sub_epics recursively*  
│  └─ 📝 Story: Archive Obsolete Folders  
│     *StoryFolderStructureBuilder compares existing epic folders with epics in structured JSON, moves obsolete folders to project_area/docs/stories/map/z_archive/{timestamp}/, never deletes folders*  

---

## Source Material

**Shape Phase:**
- **Primary Source**: `agents/base/src/agent.py` - Base Agent implementation showing Agent, Workflow, Behavior, Content, Project classes with workflow orchestration, guidance application, and content generation
- **Primary Source**: `agents/base/src/agent_mcp_server.py` - MCP server implementation showing how AI Chat invokes Story Agent via MCP tools (agent_get_instructions, agent_store_clarification, agent_store_planning, agent_store_structured, agent_store_rendered)
- **Primary Source**: `agents/base/src/agent_test.py` - Comprehensive tests showing the flow of code and how Base Agent works (extremely important for understanding implementation)
- **Primary Source**: `agents/stories/agent.json` - Story Agent configuration with behaviors (shape, prioritization, discovery, exploration, specification), guardrails with key_questions and evidence, planning decision_criteria, rules, and content configs
- **Primary Source**: `agents/stories/src/story_agent.py` - Story Agent specific builders (StoryFolderStructureBuilder, DrawIOStoryBuilder, DrawIOStoryShapeBuilder) and diagnostic implementations
- **Primary Source**: `agents/stories/src/story_agent_test.py` - Tests showing how Story Agent builders work
- **Primary Source**: `agents/stories/templates/story-map-decomposition-template.md` - Template used for rendering story map markdown
- **Primary Source**: `agents/stories/story_graph.json` - Schema for structured story content
- **Primary Source**: `agents/base/docs/agent-story-map.md` - Existing Base Agent story map (referenced and extended, not created from scratch)
- **Date Generated**: 2025-01-21
- **Context Note**: Story map generated to document Story Agent user experience with component-level detail showing interactions between User, AI Chat, Story Agent MCP Server, and Base Agent. Focuses on JSON loading, MCP tool calls, method invocations, template rendering, file saving, and activity tracking. Includes new "Continue Existing Project" feature documenting activity_area persistence and workflow state restoration.
