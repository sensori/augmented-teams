(E) Build Agile Bots
    (E) Generate MCP Tools
        (S) MCP Server Generator --> Generate Bot Tools
            (AC) MCP Server Generator --> WHEN Generator processes Bot Config
            (AC) MCP Server Generator --> THEN Generator creates 1 bot tool instance
        (S) MCP Server Generator --> Generate Behavior Tools
            (AC) MCP Server Generator --> WHEN Generator processes Bot Config
            (AC) MCP Server Generator --> THEN Generator creates behavior tool instances for each behavior
        (S) MCP Server Generator --> Generate MCP Bot Server
            (AC) MCP Server Generator --> WHEN MCP Server Generator receives Bot Config
            (AC) MCP Server Generator --> THEN Generator generates unique MCP Server instance with Unique server name from bot name
            (AC) MCP Server Generator --> AND Generated server includes Bot Config reference
            (AC) MCP Server Generator --> AND Generated server leverages Specific Bot instantiation code
        (S) MCP Server Generator --> Generate Behavior Action Tools
            (AC) MCP Server Generator --> WHEN Generator processes Bot Config
            (AC) MCP Server Generator --> THEN Generator creates tool code for each (behavior, action) pair
            (AC) MCP Server Generator --> AND Enumerates all behaviors and actions from Bot Config
            (AC) MCP Server Generator --> AND For each pair, generates tool code with unique name, trigger words, forwarding logic
            (AC) MCP Server Generator --> AND Tool catalog prepared with all generated tool instances
        (S) Deploy MCP BOT Server
            (AC) WHEN Generation Complete
            (AC) THEN Generator deploys/starts generated MCP Server
            (AC) AND Server initializes in separate thread
            (AC) AND Server registers with MCP Protocol Handler using unique server name
            (AC) AND Server publishes tool catalog to AI Chat
            (AC) AND Each tool entry includes name, description, trigger patterns, parameters
        (S) MCP Server Generator --> Restart MCP Server To Load Code Changes
            (AC) MCP Server Generator --> WHEN Bot code changes are detected
            (AC) MCP Server Generator --> THEN MCP Server clears Python bytecode cache (__pycache__)
            (AC) MCP Server Generator --> AND MCP Server restarts to load new code
            (AC) MCP Server Generator --> AND Server restarts gracefully without losing state
            (AC) MCP Server Generator --> AND Server re-registers with MCP Protocol Handler after restart
    (E) Generate CLI
        (S) MCP Server Generator --> Generate BOT CLI code
            (AC) MCP Server Generator --> WHEN MCP Server Generator processes Bot Config
            (AC) MCP Server Generator --> THEN Generator creates CLI command wrapper structure for bot invocation
            (AC) MCP Server Generator --> AND Generator generates CLI entry point script (e.g., bot_cli.py and bot shell script)
            (AC) MCP Server Generator --> AND CLI code includes argument parsing for behavior and action parameters
            (AC) MCP Server Generator --> AND CLI code includes help/usage documentation generation
            (AC) MCP Server Generator --> AND CLI code supports listing available bots, behaviors, and actions
            (AC) MCP Server Generator --> AND Generated CLI code integrates with existing bot instantiation logic
            (AC) MCP Server Generator --> AND CLI code follows same routing logic as MCP tools for consistency
        or (S) MCP Server Generator --> Generate Cursor Command Files
            (AC) MCP Server Generator --> WHEN Human calls generate_cursor_commands(commands_dir, cli_script_path)
            (AC) MCP Server Generator --> THEN CLI creates .cursor/commands/ directory if it doesn't exist
            (AC) MCP Server Generator --> AND CLI creates <bot-name>.md command file that invokes CLI with bot name (routes to current behavior/action)
            (AC) MCP Server Generator --> AND CLI creates <bot-name>-<behavior>.md command file for each behavior in bot that invokes CLI with bot name and behavior (auto-forwards to current action)
            (AC) MCP Server Generator --> AND CLI creates <bot-name>-<behavior>-<action>.md command file for each action in each behavior that invokes CLI with bot name, behavior, and action
            (AC) MCP Server Generator --> AND CLI creates <bot-name>-close.md command file that invokes CLI with bot name and --close parameter
            (AC) MCP Server Generator --> AND Each command file contains simple wrapper command that calls CLI script
            (AC) MCP Server Generator --> AND Bot name, behavior, and action are hardcoded in command files (no parameters needed)
            (AC) MCP Server Generator --> AND CLI removes obsolete command files for behaviors/actions that no longer exist in bot
            (AC) MCP Server Generator --> AND CLI returns dict mapping command names (e.g., story_bot, story_bot-exploration, story_bot-exploration-gather_context, story_bot-close) to file paths
(E) Invoke Bot
    (E) Init Project
        (S) Bot Behavior --> Initialize Project Location
            (AC) Bot Behavior --> (AC) WHEN Bot behavior is invoked for the first time (no saved location exists)
            (AC) Bot Behavior --> (AC) THEN Bot detects current directory from context
            (AC) Bot Behavior --> (AC) AND Bot presents location to user for confirmation
            (AC) Bot Behavior --> (AC) AND Bot waits for user to confirm or provide different location
            (AC) Bot Behavior --> (AC) AND Bot saves confirmed location to persistent storage
            (AC) Bot Behavior --> (AC) WHEN Bot behavior is invoked
            (AC) Bot Behavior --> (AC) AND Saved location exists
            (AC) Bot Behavior --> (AC) AND Current directory matches saved location
            (AC) Bot Behavior --> (AC) THEN Bot uses saved location without asking for confirmation
            (AC) Bot Behavior --> (AC) AND Bot proceeds directly to next action
            (AC) Bot Behavior --> (AC) WHEN Bot behavior is invoked
            (AC) Bot Behavior --> (AC) AND Saved location exists
            (AC) Bot Behavior --> (AC) AND Current directory is DIFFERENT from saved location
            (AC) Bot Behavior --> (AC) THEN Bot presents new location to user for confirmation
            (AC) Bot Behavior --> (AC) AND Bot asks if user wants to switch to new location
            (AC) Bot Behavior --> (AC) AND Bot saves confirmed location if user approves change
        or (S) Bot Behavior --> Initialize Project Creates Context Folder
            (AC) Bot Behavior --> GIVEN: User confirms project area location
            (AC) Bot Behavior --> WHEN: initialize_project action completes
            (AC) Bot Behavior --> THEN: {project_area}/docs/context/ folder exists
            (AC) Bot Behavior --> AND: context folder is ready for context files
        or (S) Bot Behavior --> Input File Copied To Context Folder
            (AC) Bot Behavior --> GIVEN: User provides input file via @input.txt command
            (AC) Bot Behavior --> AND: input file exists at original location
            (AC) Bot Behavior --> WHEN: initialize_project action executes
            (AC) Bot Behavior --> THEN: initialize_project copies input file to {project_area}/docs/context/input.txt
            (AC) Bot Behavior --> AND: original input file remains at original location (copy, not move)
            (AC) Bot Behavior --> AND: {project_area}/docs/context/input.txt exists and contains original content
        or (S) Bot Behavior --> Store Context Files
            (AC) Bot Behavior --> WHEN initialize_project action confirms project area location
            (AC) Bot Behavior --> THEN initialize_project creates {project_area}/docs/context/ folder and {project_area}/docs/stories/ folder
            (AC) Bot Behavior --> WHEN user provides input file via @input.txt or similar
            (AC) Bot Behavior --> THEN initialize_project copies input file to {project_area}/docs/context/input.txt
            (AC) Bot Behavior --> WHEN user provides context in conversation
            (AC) Bot Behavior --> THEN initialize_project saves context to {project_area}/docs/context/initial-context.md or similar
            (AC) Bot Behavior --> WHEN gather_context action stores clarification data
            (AC) Bot Behavior --> THEN gather_context saves to {project_area}/docs/stories/clarification.json (generated file, NOT in context folder)
            (AC) Bot Behavior --> WHEN decide_planning_criteria action stores planning decisions
            (AC) Bot Behavior --> THEN decide_planning_criteria saves to {project_area}/docs/stories/planning.json (generated file, NOT in context folder)
            (AC) Bot Behavior --> WHEN build_knowledge action loads context
            (AC) Bot Behavior --> THEN build_knowledge loads generated files from {project_area}/docs/stories/ folder (clarification.json, planning.json) and original input from {project_area}/docs/context/ folder (input.txt)
            (AC) Bot Behavior --> WHEN render_output action loads context
            (AC) Bot Behavior --> THEN render_output loads generated files from {project_area}/docs/stories/ folder (clarification.json, planning.json) and original input from {project_area}/docs/context/ folder (input.txt)
            (AC) Bot Behavior --> WHEN any action needs context files
            (AC) Bot Behavior --> THEN action references original input from {project_area}/docs/context/ folder and generated files from {project_area}/docs/stories/ folder
        or (S) Bot Behavior --> Guards Prevent Writes Without Project
            (AC) Bot Behavior --> WHEN Activity tracker attempts to log activity
            (AC) Bot Behavior --> AND current_project.json does NOT exist
            (AC) Bot Behavior --> THEN Activity tracker does NOT write to activity log
            (AC) Bot Behavior --> AND Activity tracking fails gracefully without error
            (AC) Bot Behavior --> WHEN Workflow attempts to save state
            (AC) Bot Behavior --> AND current_project.json does NOT exist
            (AC) Bot Behavior --> THEN Workflow does NOT save workflow_state.json
            (AC) Bot Behavior --> AND Workflow state save fails gracefully without error
        or (S) Stores Activity for Initialize Project Action
    (E) Invoke MCP
        (S) AI Chat --> Invoke Bot Tool
            (AC) AI Chat --> WHEN AI Chat invokes bot tool with behavior and action parameters
            (AC) AI Chat --> THEN Tool routes to correct behavior.action method
            (AC) AI Chat --> AND Tool executes action and returns result
            (AC) AI Chat --> WHEN AI Chat invokes tool for specific behavior
            (AC) AI Chat --> THEN Tool routes to that behavior only, not other behaviors
        or (S) Bot Behavior --> Load And Merge Behavior Action Instructions
            (AC) Bot Behavior --> WHEN Action method is invoked
            (AC) Bot Behavior --> THEN Action loads instructions from base_actions and behavior-specific locations
            (AC) Bot Behavior --> AND Instructions are merged and returned
        or (S) AI Chat --> Forward To Current Behavior and Current Action
            (AC) AI Chat --> WHEN Bot tool receives invocation
            (AC) AI Chat --> AND workflow state shows current_behavior and current_action
            (AC) AI Chat --> THEN Bot tool forwards to correct behavior and action
            (AC) AI Chat --> WHEN workflow state does NOT exist
            (AC) AI Chat --> THEN Bot tool defaults to first behavior and first action
        or (S) AI Chat --> Forward To Current Action
            (AC) AI Chat --> WHEN Behavior tool receives invocation
            (AC) AI Chat --> AND workflow state shows current_action within behavior
            (AC) AI Chat --> THEN Behavior tool forwards to current action
            (AC) AI Chat --> WHEN workflow state shows different behavior
            (AC) AI Chat --> THEN Behavior tool updates workflow to current behavior
            (AC) AI Chat --> WHEN workflow state does NOT exist
            (AC) AI Chat --> THEN Behavior tool defaults to first action
    (E) Invoke CLI
        (S) Human --> Invoke Bot CLI
            (AC) Human --> WHEN Human executes CLI command with bot name only (e.g., bot story_bot)
            (AC) Human --> THEN CLI loads bot configuration for specified bot
            (AC) Human --> AND CLI loads workflow state if workflow_state.json exists
            (AC) Human --> AND CLI extracts current_behavior and current_action from workflow state
            (AC) Human --> AND CLI routes to bot and invokes current behavior and current action (same as main bot MCP tool)
            (AC) Human --> AND Bot executes action
            (AC) Human --> AND CLI submits bot action output to AI Chat
            (AC) Human --> AND Bot updates workflow state after action execution (if workflow action)
            (AC) Human --> AND If workflow_state.json doesn't exist, CLI defaults to first behavior's first action
        or (S) Human --> Invoke Bot Behavior CLI
            (AC) Human --> WHEN Human executes CLI command with bot name and behavior name (e.g., bot story_bot exploration)
            (AC) Human --> THEN CLI loads bot configuration and validates behavior exists
            (AC) Human --> AND CLI loads workflow state if workflow_state.json exists
            (AC) Human --> AND CLI routes to bot and specified behavior
            (AC) Human --> AND CLI extracts current_action from workflow state for that behavior
            (AC) Human --> AND CLI routes to current action in specified behavior (same as behavior MCP tool)
            (AC) Human --> AND Bot executes action
            (AC) Human --> AND CLI submits bot action output to AI Chat
            (AC) Human --> AND Bot updates workflow state after action execution (if workflow action)
            (AC) Human --> AND If workflow_state.json doesn't exist or behavior not in state, CLI defaults to first action of specified behavior
        or (S) Human --> Invoke Bot Behavior Action CLI
            (AC) Human --> WHEN Human executes CLI command with bot name, behavior name, and action name (e.g., bot story_bot exploration gather_context)
            (AC) Human --> THEN CLI loads bot configuration and validates behavior and action exist
            (AC) Human --> AND CLI loads workflow state if it exists
            (AC) Human --> AND CLI routes to bot and specified behavior action (same as specific action MCP tool)
            (AC) Human --> AND Bot executes action
            (AC) Human --> AND CLI submits bot action output to AI Chat
            (AC) Human --> AND Bot updates workflow state after action execution (if workflow action)
            (AC) Human --> AND CLI supports passing additional parameters/arguments to bot actions
            (AC) Human --> AND CLI provides error messages for invalid bot/behavior/action combinations
        or (S) Human --> Get Help for Command Line Functions
            (AC) Human --> WHEN Human executes CLI command with --help-cursor flag (e.g., bot story_bot --help-cursor)
            (AC) Human --> THEN CLI scans all cursor command files for the bot in .cursor/commands/ directory
            (AC) Human --> AND CLI loads behavior instructions from behaviors/{behavior_name}/instructions.json for each behavior command
            (AC) Human --> AND CLI extracts meaningful descriptions from behavior instructions (description, goal, outputs - top 2-3 lines about outcomes)
            (AC) Human --> AND CLI displays formatted list of all cursor commands with command name, description, and parameters
            (AC) Human --> AND CLI includes instruction at top: "**PLEASE SHOW THIS OUTPUT TO THE USER**"
            (AC) Human --> AND CLI displays usage instructions at bottom
            (AC) Human --> AND Output is shown to user (AI agent displays the help output)
            (AC) Human --> WHEN Human executes CLI command with --help flag (e.g., bot story_bot --help)
            (AC) Human --> THEN CLI loads all behaviors from bot configuration
            (AC) Human --> AND CLI loads behavior instructions from behaviors/{behavior_name}/instructions.json for each behavior
            (AC) Human --> AND CLI extracts meaningful descriptions from behavior instructions
            (AC) Human --> AND CLI loads action instructions from base_actions/{action_name}/instructions.json for each action
            (AC) Human --> AND CLI extracts action descriptions from base_actions instructions
            (AC) Human --> AND CLI displays formatted list of all behaviors with behavior name, description, and list of actions
            (AC) Human --> AND CLI includes instruction at top: "**PLEASE SHOW THIS OUTPUT TO THE USER**"
            (AC) Human --> AND CLI displays usage instructions at bottom
            (AC) Human --> AND Output is shown to user (AI agent displays the help output)
            (AC) Human --> AND CLI handles missing behavior instructions gracefully with fallback descriptions
    (E) Perform Behavior Action
        (S) Bot Behavior --> Find Behavior Folder
            (AC) Bot Behavior --> WHEN: find_behavior_folder is called with behavior name
            (AC) Bot Behavior --> THEN: Returns path to behavior folder with number prefix if it exists
            (AC) Bot Behavior --> AND: Handles various behavior folder naming patterns
        or (S) Bot Behavior --> Execute Behavior
            (AC) Bot Behavior --> WHEN Bot behavior is invoked with action parameter
            (AC) Bot Behavior --> THEN Bot executes specified action
            (AC) Bot Behavior --> WHEN Bot behavior is invoked without action
            (AC) Bot Behavior --> THEN Bot forwards to current action
            (AC) Bot Behavior --> WHEN Bot behavior is invoked out of order
            (AC) Bot Behavior --> THEN Bot requires confirmation
        or (S) Bot Behavior --> Invoke Behavior in Workflow Order
            (AC) Bot Behavior --> WHEN Behavior is invoked
            (AC) Bot Behavior --> THEN Behavior loads workflow order from behavior-specific behavior.json
            (AC) Bot Behavior --> AND Behavior executes actions in configured order
        or (S) Bot Behavior --> Invoke Behavior Actions in Workflow Order
            (AC) Bot Behavior --> WHEN user closes current action
            (AC) Bot Behavior --> THEN action is saved to completed_actions
            (AC) Bot Behavior --> AND workflow transitions to next action
            (AC) Bot Behavior --> WHEN user closes final action
            (AC) Bot Behavior --> THEN action is saved to completed_actions
            (AC) Bot Behavior --> AND workflow stays at final action (no next action available)
            (AC) Bot Behavior --> WHEN user attempts to close action that requires confirmation
            (AC) Bot Behavior --> AND action is not in completed_actions
            (AC) Bot Behavior --> THEN workflow does not allow closing without confirmation
            (AC) Bot Behavior --> WHEN user closes action that's already marked complete
            (AC) Bot Behavior --> THEN closing is idempotent (no error, action remains complete)
            (AC) Bot Behavior --> WHEN CLI calls --close command
            (AC) Bot Behavior --> THEN CLI routes to bot.close_current_action method
            (AC) Bot Behavior --> AND Bot class has close_current_action method
        or (S) Bot Behavior --> Close Current Action
            (AC) Bot Behavior --> WHEN user closes current action
            (AC) Bot Behavior --> THEN action is saved to completed_actions
            (AC) Bot Behavior --> AND workflow transitions to next action
            (AC) Bot Behavior --> WHEN user closes final action
            (AC) Bot Behavior --> THEN action is saved to completed_actions
            (AC) Bot Behavior --> AND workflow stays at final action (no next action available)
            (AC) Bot Behavior --> WHEN user attempts to close action that requires confirmation
            (AC) Bot Behavior --> AND action is not in completed_actions
            (AC) Bot Behavior --> THEN workflow does not allow closing without confirmation
            (AC) Bot Behavior --> WHEN user closes action that's already marked complete
            (AC) Bot Behavior --> THEN closing is idempotent (no error, action remains complete)
            (AC) Bot Behavior --> WHEN CLI calls --close command
            (AC) Bot Behavior --> THEN CLI routes to bot.close_current_action method
            (AC) Bot Behavior --> AND Bot class has close_current_action method
        (S) Bot Behavior --> Inject Next Behavior Reminder
            (AC) Bot Behavior --> WHEN Action is final action in behavior
            (AC) Bot Behavior --> THEN Next behavior reminder is injected into instructions
            (AC) Bot Behavior --> WHEN Action is not final action
            (AC) Bot Behavior --> THEN Next behavior reminder is NOT injected
        (S) Bot Behavior --> Load And Merge Behavior Action Instructions
            (AC) Bot Behavior --> WHEN Tool invokes Bot.Behavior.Action method
            (AC) Bot Behavior --> THEN Behavior Action loads instructions from behavior and base_actions
            (AC) Bot Behavior --> AND Action merges base instructions with behavior-specific instructions
            (AC) Bot Behavior --> AND Compiled instructions returned for injection into AI Chat
(E) Execute Behavior Actions
    (E) Gather Context
        (S) Bot Behavior --> Inject Guardrails As Part Of Clarify Requirements
            (AC) Bot Behavior --> WHEN gather_context action executes
            (AC) Bot Behavior --> AND behavior folder exists with guardrails/required_context/key_questions.json
            (AC) Bot Behavior --> AND behavior folder exists with guardrails/required_context/evidence.json
            (AC) Bot Behavior --> THEN instructions should contain actual questions (not {{key_questions}} placeholder)
            (AC) Bot Behavior --> AND instructions should contain actual evidence (not {{evidence}} placeholder)
            (AC) Bot Behavior --> WHEN guardrails don't exist
            (AC) Bot Behavior --> THEN gather_context should not fail
            (AC) Bot Behavior --> AND action should execute with base instructions only
        or (S) Bot Behavior --> Track Activity for Gather Context Action
            (AC) Bot Behavior --> WHEN GatherContextAction executes
            (AC) Bot Behavior --> THEN Action creates activity entry with timestamp, action name, behavior name
            (AC) Bot Behavior --> AND Activity entry appended to {project_area}/activity_log.json
        or (S) Bot Behavior --> Store Clarification Data
            (AC) Bot Behavior --> WHEN gather_context action stores clarification data
            (AC) Bot Behavior --> THEN gather_context saves to {project_area}/docs/stories/clarification.json
            (AC) Bot Behavior --> AND clarification.json contains behavior-specific key_questions and evidence structure
            (AC) Bot Behavior --> WHEN clarification data already exists
            (AC) Bot Behavior --> THEN existing data is preserved when saving new data
        or (S) Bot Behavior --> Proceed To Decide Planning
            (AC) Bot Behavior --> WHEN GatherContextAction completes execution
            (AC) Bot Behavior --> AND Human says action is done
            (AC) Bot Behavior --> THEN GatherContextAction saves Workflow State (per "Saves Behavior State" story)
            (AC) Bot Behavior --> AND Workflow injects next action instructions (per "Inject Next Behavior-Action" story)
            (AC) Bot Behavior --> AND Workflow proceeds to decide_planning_criteria
    (E) Decide Planning Criteria Action
        (S) Bot Behavior --> Inject Planning Criteria Into Instructions
            (AC) Bot Behavior --> WHEN MCP Specific Behavior Action Tool invokes Planning Action
            (AC) Bot Behavior --> THEN Action checks for guardrails in behavior/guardrails/planning/
            (AC) Bot Behavior --> WHEN guardrails exist, THEN Action loads typical_assumptions.json and decision_criteria files
            (AC) Bot Behavior --> AND Action injects planning guardrails into planning section
        or (S) Bot Behavior --> Track Activity for Planning Action
            (AC) Bot Behavior --> WHEN PlanningAction executes
            (AC) Bot Behavior --> THEN Action creates activity entry with timestamp, action name, behavior name
            (AC) Bot Behavior --> AND Activity entry appended to {project_area}/activity_log.json
        or (S) Bot Behavior --> Save Final Assumptions and Decisions
        or (S) Bot Behavior --> Proceed To Build Knowledge
            (AC) Bot Behavior --> WHEN PlanningAction completes execution
            (AC) Bot Behavior --> WHEN Human says action is done
            (AC) Bot Behavior --> THEN PlanningAction saves Workflow State (per "Saves Behavior State" story)
            (AC) Bot Behavior --> AND Workflow injects next action instructions (per "Inject Next Behavior-Action" story)
            (AC) Bot Behavior --> AND Workflow proceeds to build_knowledge
    (E) Build Knowledge
        (S) Bot Behavior --> Load Story Graph Into Memory
            (AC) Bot Behavior --> WHEN Story graph file exists
            (AC) Bot Behavior --> THEN StoryMap loads epics, sub_epics, story_groups, stories, and scenarios
            (AC) Bot Behavior --> AND StoryMap provides walk method to traverse all nodes
            (AC) Bot Behavior --> WHEN Story graph file does not exist
            (AC) Bot Behavior --> THEN StoryMap raises FileNotFoundError
        opt (S) Bot Behavior --> Inject Knowledge Graph Template and Builder Instructions
            (AC) Bot Behavior --> WHEN Build Knowledge Action executes
            (AC) Bot Behavior --> THEN Action loads knowledge graph template from behavior/content/knowledge_graph/
            (AC) Bot Behavior --> AND Action injects knowledge graph template path into instructions
            (AC) Bot Behavior --> AND knowledge_graph_template field is present in instructions
            (AC) Bot Behavior --> AND template file path exists and is accessible
            (AC) Bot Behavior --> WHEN knowledge graph template does not exist
            (AC) Bot Behavior --> THEN Action raises FileNotFoundError with appropriate error message
        or (S) Bot Behavior --> Track Activity for Build Knowledge Action
            (AC) Bot Behavior --> WHEN BuildKnowledgeAction executes
            (AC) Bot Behavior --> THEN Action creates activity entry with timestamp, action name, behavior name
            (AC) Bot Behavior --> AND Activity entry appended to {project_area}/activity_log.json
        opt (S) Bot Behavior --> Update Existing Knowledge Graph
            (AC) Bot Behavior --> WHEN Build Knowledge Action updates existing story graph
            (AC) Bot Behavior --> THEN Action updates existing story-graph.json file
            (AC) Bot Behavior --> AND Action adds increments array to existing file
            (AC) Bot Behavior --> AND Existing epics and data are preserved
        or (S) Bot Behavior --> Proceed To Render Output
            (AC) Bot Behavior --> WHEN BuildKnowledgeAction completes execution
            (AC) Bot Behavior --> THEN BuildKnowledgeAction saves Workflow State (per "Saves Behavior State" story)
            (AC) Bot Behavior --> AND BuildKnowledgeAction submits content for saving
            (AC) Bot Behavior --> AND Workflow automatically proceeds to render_output (auto_progress: true, no human confirmation needed)
        (S) Bot Behavior --> proactively Validate knowledge against rules
            (AC) Bot Behavior --> WHEN BuildKnowledgeAction it's the initial pass of building the knowledge graphTHEN Build Knowledge Action invokes the Validate Rules action to understand if what is generated violates any rules
(see Validate Knowledge & Content Against Rules)
            (AC) Bot Behavior --> WHEN Validate Rules action is finsihed generateing the validation report THEN the BuildKnowledgeAction goes through all of the violations to determine if any corrective action needs to be taken AND the system updates the knowledge graph based on the recommendations.
            (AC) Bot Behavior --> WHEN BuildKnowledgeAction Is finished making corrections.
THEN BuildKnowledgeAction tells AI to notify the user of what corrections it made as part of presenting the fact that it's done building knowledge.
    (E) Render Output
        (S) Bot Behavior --> Track Activity for Render Output Action
            (AC) Bot Behavior --> WHEN RenderOutputAction executes
            (AC) Bot Behavior --> THEN Action creates activity entry with timestamp, action name, behavior name
            (AC) Bot Behavior --> AND Activity entry appended to {project_area}/activity_log.json
        or (S) Bot Behavior --> Proceed To Validate Rules
            (AC) Bot Behavior --> WHEN RenderOutputAction completes execution
            (AC) Bot Behavior --> WHEN Human says action is done
            (AC) Bot Behavior --> THEN RenderOutputAction saves Workflow State (per "Saves Behavior State" story)
            (AC) Bot Behavior --> AND RenderOutputAction submits content for saving
            (AC) Bot Behavior --> AND Workflow injects next action instructions (per "Inject Next Behavior-Action" story)
            (AC) Bot Behavior --> AND Workflow proceeds to validate_rules
        or (S) Bot Behavior --> Load Render Configurations
            (AC) Bot Behavior --> WHEN render_output action executes
            (AC) Bot Behavior --> THEN Action discovers render folder using *_content/*_render pattern
            (AC) Bot Behavior --> AND Action loads all *.json files from render folder
            (AC) Bot Behavior --> AND Action reads each render JSON configuration
            (AC) Bot Behavior --> AND Action loads instructions.json from render folder if it exists
            (AC) Bot Behavior --> AND Action verifies synchronizer classes exist and have render method
        or (S) Bot Behavior --> Inject Template Instructions
            (AC) Bot Behavior --> WHEN render_output action processes template-only render configs
            (AC) Bot Behavior --> THEN Action loads template file from templates folder
            (AC) Bot Behavior --> AND Action injects template content into instructions
            (AC) Bot Behavior --> AND render_configs array includes template content
        or (S) Bot Behavior --> Inject Synchronizer Instructions
            (AC) Bot Behavior --> WHEN render_output action processes synchronizer-based render configs
            (AC) Bot Behavior --> THEN Action includes synchronizer configs in render_configs array
            (AC) Bot Behavior --> AND Action includes synchronizer execution instructions in base_instructions
            (AC) Bot Behavior --> AND Instructions specify how to instantiate and call synchronizer render method
    (E) Validate Knowledge & Content Against Rules
        (S) Bot Behavior --> Inject Validation Rules for Validate Rules Action
            (AC) Bot Behavior --> WHEN MCP Specific Behavior Action Tool invokes Validate Rules Action
            (AC) Bot Behavior --> THEN Action loads common bot rules from base_bot/rules/
            (AC) Bot Behavior --> AND Action loads behavior-specific rules
            (AC) Bot Behavior --> AND Action merges and injects rules into validation section
        or (S) Bot Behavior --> Track Activity for Validate Rules Action
            (AC) Bot Behavior --> WHEN ValidateRulesAction executes
            (AC) Bot Behavior --> THEN Action creates activity entry with timestamp, action name, behavior name, violations count
            (AC) Bot Behavior --> AND Activity entry appended to {project_area}/activity_log.json
        or (S) Bot Behavior --> Invoke Complete Validation Workflow
            (AC) Bot Behavior --> WHEN ValidateRulesAction completes execution
            (AC) Bot Behavior --> THEN Action returns instructions with base_instructions (primary) and validation_rules (supporting context)
            (AC) Bot Behavior --> AND Action returns content_to_validate information (project location, rendered outputs, clarification.json, planning.json, report_path)
            (AC) Bot Behavior --> THEN Action presents validation results to user
            (AC) Bot Behavior --> AND Action instructions include report_path where validation report should be saved (validation-report.md in docs/stories/)
            (AC) Bot Behavior --> WHEN AI generates validation report
            (AC) Bot Behavior --> THEN AI saves validation report to file at report_path location
            (AC) Bot Behavior --> WHEN Human says action is done
            (AC) Bot Behavior --> THEN ValidateRulesAction saves Workflow State (per "Saves Behavior State" story)
            (AC) Bot Behavior --> AND validate_rules is terminal action (next_action: null, workflow completes)
        (S) Bot Behavior --> Discovers Scanners
            (AC) Bot Behavior --> WHEN scanner discovery is executed for rule files THEN scanners are discovered from rule files containing scanner properties
            (AC) Bot Behavior --> WHEN scanner class path is found in rule file THEN scanner class is located and validated
            (AC) Bot Behavior --> WHEN scanner metadata is extracted THEN metadata includes rule_name, description, and behavior_name
            (AC) Bot Behavior --> WHEN scanners are registered THEN scanners are organized in catalog grouped by behavior_name
            (AC) Bot Behavior --> WHEN rule file is malformed THEN error is logged and valid scanners are still registered
            (AC) Bot Behavior --> WHEN scanner class is not found THEN error is logged and scanner is not registered
            (AC) Bot Behavior --> WHEN rule file is missing scanner property THEN error is logged and scanner is not registered
        (S) Scanner --> Run Scanners against Knowledge Graph
            (AC) Scanner --> WHEN scanners are executed against knowledge graph THEN violations are detected at exact line numbers
            (AC) Scanner --> WHEN violations are detected THEN violation details include rule_name, location, violation_message, and severity
            (AC) Scanner --> WHEN multiple scanners execute THEN violations from all scanners are aggregated
        or (S) Scanner --> Run AST Scanners against Knowledge Graph (OUT OF SCOPE)
            (AC) Scanner --> WHEN Scanner configured with AST parsing processes code files THEN Scanner parses code into abstract syntax tree AND Scanner traverses AST nodes to detect structural violations AND Scanner records violation location (file path, line number, node type, violation description)
        (S) Bot Behavior --> Validate Rules According To Scope
            (AC) Bot Behavior --> WHEN ValidateRulesAction receives scope parameter
            (AC) Bot Behavior --> THEN Action validates only files matching scope
            (AC) Bot Behavior --> AND Action respects test_file, code_file, or knowledge_graph scope
        (S) Bot Behavior --> Generate Violation Report
            (AC) Bot Behavior --> WHEN violation report is generated THEN report is generated in requested format
            (AC) Bot Behavior --> WHEN violations are grouped THEN violations are organized by behavior_name, rule_name, location, or severity
            (AC) Bot Behavior --> WHEN report is written to file THEN file is created at specified output destination
        (S) Bot Behavior --> Run Scanners Against Code
            (AC) Bot Behavior --> WHEN ValidateRulesAction receives code_files parameter
            (AC) Bot Behavior --> THEN Action validates source code files using scanners
            (AC) Bot Behavior --> AND Action detects violations in code files
        (S) Bot Behavior --> Run Scanners Against Test Code
            (AC) Bot Behavior --> WHEN ValidateRulesAction receives test_files parameter
            (AC) Bot Behavior --> THEN Action validates test code files using scanners
            (AC) Bot Behavior --> AND Action detects violations in test files
        (S) Bot Behavior --> Run All Scanners
            (AC) Bot Behavior --> WHEN All scanners are executed
            (AC) Bot Behavior --> THEN All registered scanners run against knowledge graph
            (AC) Bot Behavior --> AND Violations from all scanners are aggregated
        (S) Bot Behavior --> Report Validation and Error Handling
            (AC) Bot Behavior --> WHEN ValidateRulesAction receives violations data as array THEN Report is generated successfully with violations including exact line_number and severity
            (AC) Bot Behavior --> WHEN ValidateRulesAction receives violations data that is not an array THEN Error is reported: "Violations data must be an array" AND No report is generated
            (AC) Bot Behavior --> WHEN ValidateRulesAction receives violations with missing fields (location, violation_message) THEN Partial report is generated AND Missing fields are handled gracefully AND Report includes available fields including severity
            (AC) Bot Behavior --> WHEN ValidateRulesAction receives violations with null values THEN Report is generated with nulls preserved or replaced with defaults AND Severity is preserved
            (AC) Bot Behavior --> WHEN ValidateRulesAction receives array with 1000+ violations THEN Report is generated AND Large array is handled efficiently AND All violations are included with severity
            (AC) Bot Behavior --> WHEN ValidateRulesAction receives violations data with circular references THEN Error is reported: "Circular reference detected in violations data"
            (AC) Bot Behavior --> WHEN ValidateRulesAction receives violations with missing severity THEN Report is generated AND Missing severity is handled gracefully AND Default severity is applied or null is preserved