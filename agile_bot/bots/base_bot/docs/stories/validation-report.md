# Validation Report - 8 Code

**Generated:** 2025-12-14 04:44:47
**Project:** base_bot
**Behavior:** 8_code
**Action:** validate_rules

## Summary

Validated story map and domain model against **41 validation rules**.

## Content Validated

- **Planning:** `planning.json`
- **Rendered Outputs:**
  - `build-bot-domain-model-description.md`
  - `build-bot-domain-model-diagram.md`
  - `story-graph.json`
  - `story-map-increments.md`
- **Test Files Scanned:**
  - `test\test_build_agile_bots.py`
  - `test\test_build_knowledge.py`
  - `test\test_decide_planning_criteria_action.py`
  - `test\test_execute_behavior_actions.py`
  - `test\test_gather_context.py`
  - `test\test_generate_cli.py`
  - `test\test_generate_mcp_tools.py`
  - `test\test_helpers.py`
  - `test\test_init_project.py`
  - `test\test_invoke_bot.py`
  - `test\test_invoke_cli.py`
  - `test\test_invoke_mcp.py`
  - `test\test_perform_behavior_action.py`
  - `test\test_render_output.py`
  - `test\test_validate_knowledge_and_content_against_rules.py`
  - **Total:** 15 test file(s)
- **Code Files Scanned:**
  - `src\bot\__init__.py`
  - `src\bot\base_action.py`
  - `src\bot\behavior_folder_finder.py`
  - `src\bot\bot.py`
  - `src\bot\build_knowledge_action.py`
  - `src\bot\code_quality_action.py`
  - `src\bot\gather_context_action.py`
  - `src\bot\planning_action.py`
  - `src\bot\render_output_action.py`
  - `src\bot\validate_rules_action.py`
  - `src\cli\__init__.py`
  - `src\cli\base_bot_cli.py`
  - `src\cli\cli_generator.py`
  - `src\cli\trigger_router.py`
  - `src\cli\trigger_router_entry.py`
  - `src\mcp\behavior_tool_generator.py`
  - `src\mcp\bot_tool_generator.py`
  - `src\mcp\mcp_server.py`
  - `src\mcp\mcp_server_generator.py`
  - `src\mcp\server_deployer.py`
  - `src\mcp\server_restart.py`
  - `src\state\activity_tracker.py`
  - `src\state\router.py`
  - `src\state\workflow.py`
  - `src\state\workspace.py`
  - `src\utils.py`
  - **Total:** 26 code file(s)

## Validation Rules Checked

### Rule: Maintain Verb Noun Consistency
**Description:** Maintain verb-noun consistency from epic to feature to story to scenario

### Rule: Map Sequential Spine Vs Optional Paths
**Description:** When mapping stories, carefully distinguish between sequential spine (essential path) and optional paths, alternate routes, or additional functionality that is not strictly essential. Sequential stories form the mandatory flow; optional stories are alternatives, enhancements, or non-essential features.

### Rule: Stories Developed And Tested In Days
**Description:** Write stories that can be developed and tested in a matter of days

### Rule: Story Names Must Follow Verb Noun Format
**Description:** CRITICAL: Story names MUST follow Verb-Noun format (e.g., 'Move To Mob Leaders Turn', 'Determines Target from Strategy', 'Initiate Mob Attack'), and include italicized description showing component interactions (e.g., '*Combat Tracker moves to any mob member's turn, auto moves to mob leader's turn*'). The story name should be concise and action-oriented, while the description shows the component-to-component interactions.

### Rule: Use Active Behavioral Language
**Description:** Use active behavioral language with action verbs. Describe behaviors, not tasks or capabilities.

### Rule: Use Verb Noun Format For Story Elements
**Description:** Use verb-noun format for all story elements (epic names, feature names, story titles)

### Rule: Classify Exceptions By Caller Needs
**Description:** Design exceptions based on how callers will handle them. Create exception types based on caller's needs, use special case objects for predictable failures, and wrap third-party exceptions at boundaries.

### Rule: Eliminate Duplication
**Description:** CRITICAL: Every piece of knowledge should have a single, authoritative representation (DRY principle). Extract repeated logic into reusable functions and use abstraction to capture common patterns.

### Rule: Enforce Encapsulation
**Description:** CRITICAL: Hide implementation details and expose minimal interface. Make fields private by default, expose behavior not data, and follow Law of Demeter (principle of least knowledge).

### Rule: Enforce Team Formatting Consensus
**Description:** Formatting should be consistent and automated. Agree on formatting rules as a team, use automated formatters (prettier, black, gofmt), and enforce formatting in CI/CD pipeline.

### Rule: Follow Open Closed Principle
**Description:** Open for extension, closed for modification. Design for extension without modification, depend on interfaces/abstractions not concrete types, and use composition over inheritance.

### Rule: Handle Backward Compatibility
**Description:** When refactoring public interfaces, provide migration paths to avoid breaking existing code. Maintain backward compatibility during transitions and deprecate old interfaces gracefully.

### Rule: Isolate Error Handling
**Description:** Keep error handling separate from business logic. Extract try/catch blocks into dedicated functions and handle errors at appropriate abstraction levels.

### Rule: Isolate Third Party Code
**Description:** CRITICAL: Don't let external APIs spread through your codebase. Wrap third-party APIs behind your interfaces, create learning tests for external dependencies, and isolate boundary code from business logic.

### Rule: Keep Classes Single Responsibility
**Description:** CRITICAL: Each class should have one reason to change. Keep classes cohesive (methods/data interdependent), focus on single responsibility, and extract multi-responsibility classes.

### Rule: Keep Classes Small Compact
**Description:** Classes should be small and free of dead code. Keep classes under 200-300 lines, eliminate dead/unused code, and favor many small classes over few large ones.

### Rule: Keep Functions Single Responsibility
**Description:** CRITICAL: Functions should do one thing and do it well, with no hidden side effects. Each function must have a single, well-defined responsibility.

### Rule: Keep Functions Small Focused
**Description:** Functions should be small enough to understand at a glance. Keep functions under 20 lines when possible and extract complex logic into named helper functions.

### Rule: Maintain Abstraction Levels
**Description:** Code should flow from high-level concepts down to details. Follow 'newspaper metaphor' (high-level first), keep related functions close together, and step down one abstraction level at a time.

### Rule: Maintain Test Quality
**Description:** CRITICAL: Tests should be as clean as production code. Keep tests readable and maintainable, use descriptive test names, and follow FIRST principles (Fast, Independent, Repeatable, Self-validating, Timely).

*... and 21 more rules*

## Violations Found

**Total Violations:** 642
- **File-by-File Violations:** 642
- **Cross-File Violations:** 0

### File-by-File Violations (Pass 1)

These violations were detected by scanning each file individually.

#### Map Sequential Spine Vs Optional Paths: 13 violation(s)

- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements
- 🟡 **WARNING** - ``: All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements

#### Stories Developed And Tested In Days: 4 violation(s)

- 🟡 **WARNING** - [`epics[0].sub_epics[1].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[0].sub_epics[1].name): Sub-epic "Generate CLI" has 3 3 stories (should be 4-10)
- 🔴 **ERROR** - [`epics[1].sub_epics[0].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].sub_epics[0].name): Sub-epic "Init Project" has 1 1 stories (should be 4-10)
- 🟡 **WARNING** - [`epics[1].sub_epics[3].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[1].sub_epics[3].name): Sub-epic "Perform Behavior Action" has 3 3 stories (should be 4-10)
- 🔴 **ERROR** - [`epics[2].sub_epics[4].name`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/epics[2].sub_epics[4].name): Sub-epic "Validate Knowledge & Content Against Rules" has 14 14 stories (should be 4-10)

#### Classify Exceptions By Caller Needs: 2 violation(s)

- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:886): Line 886 defines component-based exception - exceptions should be classified by how caller handles them, not by component
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:888): Line 888 defines component-based exception - exceptions should be classified by how caller handles them, not by component

#### Eliminate Duplication: 1 violation(s)

- 🔴 **ERROR** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:129): Duplicate code detected: functions workspace_directory, workspace_directory have identical bodies - extract to shared function

#### Follow Open Closed Principle: 9 violation(s)

- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:847): Line 847 uses type-based conditional - use polymorphism instead to follow open-closed principle
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:849): Line 849 uses type-based conditional - use polymorphism instead to follow open-closed principle
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:860): Line 860 uses type-based conditional - use polymorphism instead to follow open-closed principle
- 🟡 **WARNING** - [`test_invoke_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_cli.py:663): Line 663 uses type-based conditional - use polymorphism instead to follow open-closed principle
- 🟡 **WARNING** - [`test_invoke_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_cli.py:669): Line 669 uses type-based conditional - use polymorphism instead to follow open-closed principle
- 🟡 **WARNING** - [`test_invoke_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_cli.py:675): Line 675 uses type-based conditional - use polymorphism instead to follow open-closed principle
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:907): Line 907 uses type-based conditional - use polymorphism instead to follow open-closed principle
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:909): Line 909 uses type-based conditional - use polymorphism instead to follow open-closed principle
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:911): Line 911 uses type-based conditional - use polymorphism instead to follow open-closed principle

#### Isolate Error Handling: 3 violation(s)

- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:809): Function "_write_validation_report" has 5 try-except blocks - extract error handling to separate functions
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:1080): Function "_create_file_link" has 3 try-except blocks - extract error handling to separate functions
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:635): Function "_load_trigger_words_from_behavior_folder" has 3 try-except blocks - extract error handling to separate functions

#### Isolate Third Party Code: 3 violation(s)

- 🔵 **INFO** - [`server_deployer.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/server_deployer.py:65): Line 65 imports third-party library directly - wrap third-party APIs behind your own interfaces
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:898): Line 898 imports third-party library directly - wrap third-party APIs behind your own interfaces
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:899): Line 899 imports third-party library directly - wrap third-party APIs behind your own interfaces

#### Keep Classes Single Responsibility: 5 violation(s)

- 🔵 **INFO** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:95): Class "Behavior" has 27 methods - consider if it has multiple responsibilities
- 🔵 **INFO** - [`render_output_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/render_output_action.py:12): Class "RenderOutputAction" has 16 methods - consider if it has multiple responsibilities
- 🔵 **INFO** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:13): Class "BaseBotCli" has 29 methods - consider if it has multiple responsibilities
- 🔵 **INFO** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:9): Class "MCPServerGenerator" has 25 methods - consider if it has multiple responsibilities
- 🔵 **INFO** - [`workflow.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/workflow.py:13): Class "Workflow" has 18 methods - consider if it has multiple responsibilities

#### Keep Classes Small Compact: 13 violation(s)

- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:95): Class "Behavior" is 412 lines - should be under 300 lines (extract related methods into separate classes)
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:509): Class "Bot" is 466 lines - should be under 300 lines (extract related methods into separate classes)
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:14): Class "BuildKnowledgeAction" is 649 lines - should be under 300 lines (extract related methods into separate classes)
- 🟡 **WARNING** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:10): Class "CodeQualityAction" is 313 lines - should be under 300 lines (extract related methods into separate classes)
- 🟡 **WARNING** - [`render_output_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/render_output_action.py:12): Class "RenderOutputAction" is 314 lines - should be under 300 lines (extract related methods into separate classes)
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:135): Class "ValidateRulesAction" is 1178 lines - should be under 300 lines (extract related methods into separate classes)
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:13): Class "BaseBotCli" is 667 lines - should be under 300 lines (extract related methods into separate classes)
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:10): Class "CliGenerator" is 349 lines - should be under 300 lines (extract related methods into separate classes)
- 🟡 **WARNING** - [`trigger_router.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/trigger_router.py:15): Class "TriggerRouter" is 366 lines - should be under 300 lines (extract related methods into separate classes)
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:9): Class "MCPServerGenerator" is 965 lines - should be under 300 lines (extract related methods into separate classes)
- 🟡 **WARNING** - [`workflow.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/workflow.py:13): Class "Workflow" is 344 lines - should be under 300 lines (extract related methods into separate classes)
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:286): Class "TestBootstrapWorkspace" is 327 lines - should be under 300 lines (extract related methods into separate classes)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2417): Class "TestValidateRulesAccordingToScope" is 717 lines - should be under 300 lines (extract related methods into separate classes)

#### Keep Functions Single Responsibility: 5 violation(s)

- 🔵 **INFO** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:95): Class "Behavior" has 27 methods - consider if it has multiple responsibilities
- 🔵 **INFO** - [`render_output_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/render_output_action.py:12): Class "RenderOutputAction" has 16 methods - consider if it has multiple responsibilities
- 🔵 **INFO** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:13): Class "BaseBotCli" has 29 methods - consider if it has multiple responsibilities
- 🔵 **INFO** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:9): Class "MCPServerGenerator" has 25 methods - consider if it has multiple responsibilities
- 🔵 **INFO** - [`workflow.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/workflow.py:13): Class "Workflow" has 18 methods - consider if it has multiple responsibilities

#### Keep Functions Small Focused: 40 violation(s)

- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:14): Function "load_workflow_states_and_transitions" is 35 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:160): Function "rules" is 22 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:369): Function "does_requested_action_match_current" is 24 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:451): Function "forward_to_current_action" is 21 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:584): Function "infer_working_dir_from_path" is 27 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:628): Function "forward_to_current_behavior_and_current_action" is 22 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:653): Function "does_requested_behavior_match_current" is 51 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:730): Function "execute_behavior" is 85 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:940): Function "close_current_action" is 28 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:19): Function "do_execute" is 38 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:78): Function "load_and_merge_instructions" is 50 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:161): Function "inject_knowledge_graph_template" is 45 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:277): Function "inject_rules" is 30 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:321): Function "inject_schema_description_instructions" is 30 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:21): Function "do_execute" is 105 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:169): Function "injectValidationInstructions" is 100 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`gather_context_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/gather_context_action.py:33): Function "save_clarification" is 29 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`gather_context_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/gather_context_action.py:76): Function "load_and_merge_instructions" is 50 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`gather_context_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/gather_context_action.py:143): Function "inject_questions_and_evidence" is 27 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`planning_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/planning_action.py:34): Function "inject_decision_criteria_and_assumptions" is 35 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`planning_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/planning_action.py:76): Function "save_planning" is 39 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:141): Function "do_execute" is 201 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:402): Function "inject_behavior_specific_and_bot_rules" is 56 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:620): Function "injectValidationInstructions" is 128 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:1252): Function "generate_report" is 27 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:109): Function "help_behaviors_and_actions" is 31 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:189): Function "help_cursor_commands" is 44 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:373): Function "parse_arguments" is 27 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:571): Function "generate_cursor_commands" is 33 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:34): Function "generate_cli_code" is 23 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`trigger_router.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/trigger_router.py:40): Function "match_trigger" is 32 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`mcp_server.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server.py:32): Function "invoke_tool" is 23 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:184): Function "register_close_current_action_tool" is 75 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:323): Function "register_confirm_out_of_order_tool" is 31 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:395): Function "register_restart_server_tool" is 35 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`server_deployer.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/server_deployer.py:54): Function "deploy_server" is 23 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`server_restart.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/server_restart.py:48): Function "terminate_processes" is 30 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`server_restart.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/server_restart.py:132): Function "restart_mcp_server" is 29 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`router.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/router.py:10): Function "determine_next_action_from_state" is 24 lines - should be under 20 lines (extract complex logic to helper functions)
- 🟡 **WARNING** - [`workflow.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/workflow.py:92): Function "load_state" is 38 lines - should be under 20 lines (extract complex logic to helper functions)

#### Maintain Abstraction Levels: 48 violation(s)

- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:511): Function "__init__" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:653): Function "does_requested_behavior_match_current" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:730): Function "execute_behavior" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:78): Function "load_and_merge_instructions" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:161): Function "inject_knowledge_graph_template" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:441): Function "_load_behavior_specific_instructions" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:470): Function "_format_rules" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:169): Function "injectValidationInstructions" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`gather_context_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/gather_context_action.py:33): Function "save_clarification" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`gather_context_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/gather_context_action.py:143): Function "inject_questions_and_evidence" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`planning_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/planning_action.py:34): Function "inject_decision_criteria_and_assumptions" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`planning_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/planning_action.py:76): Function "save_planning" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:141): Function "do_execute" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:402): Function "inject_behavior_specific_and_bot_rules" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:620): Function "injectValidationInstructions" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:809): Function "_write_validation_report" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:373): Function "parse_arguments" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:425): Function "_parse_action_parameters" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:565): Function "_handle_error" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:258): Function "_generate_cursor_commands" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:104): Function "register_all_behavior_action_tools" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:395): Function "register_restart_server_tool" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:635): Function "_load_trigger_words_from_behavior_folder" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`server_deployer.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/server_deployer.py:54): Function "deploy_server" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`server_restart.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/server_restart.py:132): Function "restart_mcp_server" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`workflow.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/workflow.py:135): Function "_determine_next_action_from_completed" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`workflow.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/workflow.py:252): Function "navigate_to_action" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_generate_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:188): Function "test_generator_handles_file_write_errors_gracefully_creates_directory" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_generate_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:202): Function "test_generator_handles_file_write_errors_with_clear_error_message" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:401): Function "when_deployer_attempts_deployment_with_invalid_url" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:894): Function "test_generator_creates_bot_tool_for_test_bot" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:920): Function "test_generator_creates_behavior_tools_for_test_bot_with_4_behaviors" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1011): Function "test_generator_creates_tools_for_test_bot_with_4_behaviors" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1067): Function "test_generator_handles_missing_trigger_words" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1184): Function "test_generator_fails_when_protocol_handler_not_running" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1204): Function "test_server_handles_initialization_failure" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:485): Function "test_close_handles_action_already_completed_gracefully" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:678): Function "given_story_graph_for_multiple_test_files" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:788): Function "_create_test_file_for_test_quality_scanner" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:800): Function "_create_test_file_for_specification_match_scanner" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:824): Function "_create_code_file_for_scanner_type" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1014): Function "when_test_scope_extraction_with_increment_priorities" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1026): Function "when_test_scope_extraction_with_epic_names" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1038): Function "when_test_scope_extraction_with_multiple_epics" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1049): Function "when_test_scope_extraction_with_story_names" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1653): Function "when_extract_violations_from_validation_rules" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2421): Function "create_comprehensive_story_graph" mixes high-level operations with low-level details - extract low-level details to separate functions
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2710): Function "_handle_story_names_scope" mixes high-level operations with low-level details - extract low-level details to separate functions

#### Maintain Test Quality: 1 violation(s)

- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:791): Line 791 uses global state - tests should be independent, not share state

#### Maintain Vertical Density: 37 violation(s)

- 🔵 **INFO** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:14): Function "load_workflow_states_and_transitions" is 66 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:653): Function "does_requested_behavior_match_current" is 76 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:730): Function "execute_behavior" is 165 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:19): Function "do_execute" is 58 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:78): Function "load_and_merge_instructions" is 65 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:161): Function "inject_knowledge_graph_template" is 68 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:470): Function "_format_rules" is 163 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:21): Function "do_execute" is 147 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:169): Function "injectValidationInstructions" is 154 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`gather_context_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/gather_context_action.py:76): Function "load_and_merge_instructions" is 66 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:141): Function "do_execute" is 243 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:402): Function "inject_behavior_specific_and_bot_rules" is 83 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:489): Function "_identify_content_to_validate" is 66 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:620): Function "injectValidationInstructions" is 188 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:809): Function "_write_validation_report" is 270 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:1125): Function "_extract_test_info" is 77 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:1252): Function "generate_report" is 61 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:189): Function "help_cursor_commands" is 57 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:247): Function "_get_behavior_description" is 94 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:425): Function "_parse_action_parameters" is 90 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:571): Function "generate_cursor_commands" is 62 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:34): Function "generate_cli_code" is 51 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:86): Function "_generate_python_cli_script" is 98 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`trigger_router.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/trigger_router.py:40): Function "match_trigger" is 60 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:184): Function "register_close_current_action_tool" is 138 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:323): Function "register_confirm_out_of_order_tool" is 71 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:395): Function "register_restart_server_tool" is 56 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:500): Function "_execute_entry_workflow" is 76 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:698): Function "generate_server_entry_point" is 78 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:831): Function "_generate_workspace_rules_file" is 143 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`server_restart.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/server_restart.py:48): Function "terminate_processes" is 51 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`server_restart.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/server_restart.py:132): Function "restart_mcp_server" is 54 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`workflow.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/workflow.py:281): Function "_remove_completed_actions_after_target" is 62 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:89): Function "simple_story_graph" is 71 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:200): Function "create_actions_workflow_json" is 92 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:824): Function "_create_code_file_for_scanner_type" is 105 lines - consider improving vertical density by declaring variables near usage
- 🔵 **INFO** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2421): Function "create_comprehensive_story_graph" is 272 lines - consider improving vertical density by declaring variables near usage

#### Minimize Mutable State: 2 violation(s)

- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:95): Line 95 mutates state - prefer immutable data structures (create new objects instead of mutating)
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:870): Line 870 mutates state - prefer immutable data structures (create new objects instead of mutating)

#### Never Swallow Exceptions: 18 violation(s)

- 🔴 **ERROR** - [`base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/base_action.py:164): Except block only contains pass at line 164 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/base_action.py:160): Except block only contains pass at line 160 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:957): Except block only contains pass at line 957 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:782): Except block only contains pass at line 782 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:856): Except block only contains pass at line 856 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:129): Except block only contains pass at line 129 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:436): Except block only contains pass at line 436 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:465): Except block only contains pass at line 465 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`gather_context_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/gather_context_action.py:119): Except block only contains pass at line 119 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:183): Except block only contains pass at line 183 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:289): Except block only contains pass at line 289 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:336): Except block only contains pass at line 336 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`trigger_router.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/trigger_router.py:291): Except block only contains pass at line 291 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:667): Except block only contains pass at line 667 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:680): Except block only contains pass at line 680 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:877): Except block only contains pass at line 877 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:443): Except block only contains pass at line 443 - exceptions must be logged or rethrown, never swallowed
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1948): Except block only contains pass at line 1948 - exceptions must be logged or rethrown, never swallowed

#### Prefer Code Over Comments: 1 violation(s)

- 🔴 **ERROR** - [`behavior_tool_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/behavior_tool_generator.py:36): Useless comment: "# Load bot config to get behaviors" - delete it or improve the code instead

#### Provide Meaningful Context: 114 violation(s)

- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:932): Line 932 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:103): Line 103 uses numbered variable "100" - use meaningful descriptive name
- 🟡 **WARNING** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:113): Line 113 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`render_output_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/render_output_action.py:192): Line 192 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:276): Line 276 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:930): Line 930 uses numbered variable "20" - use meaningful descriptive name
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:939): Line 939 uses numbered variable "20" - use meaningful descriptive name
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:940): Line 940 uses numbered variable "20" - use meaningful descriptive name
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:1051): Line 1051 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:1053): Line 1053 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:1054): Line 1054 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:1211): Line 1211 uses numbered variable "123" - use meaningful descriptive name
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:1226): Line 1226 uses numbered variable "123" - use meaningful descriptive name
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:1): Line 1 uses numbered variable "python3" - use meaningful descriptive name
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:2): Line 2 uses numbered variable "90" - use meaningful descriptive name
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:14): Line 14 uses numbered variable "90" - use meaningful descriptive name
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:113): Line 113 uses numbered variable "70" - use meaningful descriptive name
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:138): Line 138 uses numbered variable "70" - use meaningful descriptive name
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:177): Line 177 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:180): Line 180 uses numbered variable "80" - use meaningful descriptive name
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:181): Line 181 uses numbered variable "77" - use meaningful descriptive name
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:209): Line 209 uses numbered variable "70" - use meaningful descriptive name
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:242): Line 242 uses numbered variable "70" - use meaningful descriptive name
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:451): Line 451 uses numbered variable "file1" - use meaningful descriptive name
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:454): Line 454 uses numbered variable "file1" - use meaningful descriptive name
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:461): Line 461 uses numbered variable "file1" - use meaningful descriptive name
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:97): Line 97 uses numbered variable "python3" - use meaningful descriptive name
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:205): Line 205 uses numbered variable "python3" - use meaningful descriptive name
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:222): Line 222 uses numbered variable "ps1" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_build_agile_bots.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_agile_bots.py:63): Line 63 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:145): Line 145 uses numbered variable "v2" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:173): Line 173 uses numbered variable "12" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:177): Line 177 uses numbered variable "420" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:334): Line 334 uses numbered variable "copy2" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:891): Line 891 uses numbered variable "v2" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_decide_planning_criteria_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria_action.py:222): Line 222 uses numbered variable "240" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:44): Line 44 uses numbered variable "330" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:56): Line 56 uses numbered variable "00" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:99): Line 99 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:291): Line 291 uses numbered variable "197" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:156): Line 156 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:407): Line 407 uses numbered variable "9999" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1296): Line 1296 uses numbered variable "312" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1297): Line 1297 uses numbered variable "312" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:286): Line 286 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:433): Line 433 uses numbered variable "412" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:501): Line 501 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:65): Line 65 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:604): Line 604 uses numbered variable "result1" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:605): Line 605 uses numbered variable "result2" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:606): Line 606 uses numbered variable "result3" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:609): Line 609 uses numbered variable "result1" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:612): Line 612 uses numbered variable "result1" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_invoke_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_cli.py:262): Line 262 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_invoke_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_cli.py:634): Line 634 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_invoke_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_cli.py:647): Line 647 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_invoke_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_cli.py:649): Line 649 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:40): Line 40 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:709): Line 709 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:720): Line 720 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:770): Line 770 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:832): Line 832 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:854): Line 854 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:855): Line 855 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:856): Line 856 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:900): Line 900 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:901): Line 901 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:902): Line 902 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:903): Line 903 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:957): Line 957 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:1023): Line 1023 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:1079): Line 1079 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:1155): Line 1155 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:1388): Line 1388 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:1546): Line 1546 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:41): Line 41 uses numbered variable "copy2" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:151): Line 151 uses numbered variable "09" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:152): Line 152 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:337): Line 337 uses numbered variable "180" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:864): Line 864 contains magic number - replace with named constant
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1512): Line 1512 contains magic number - replace with named constant
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1586): Line 1586 contains magic number - replace with named constant
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:790): Line 790 uses numbered variable "test_1" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:795): Line 795 uses numbered variable "test_2" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:864): Line 864 uses numbered variable "200" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:866): Line 866 uses numbered variable "data1" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:867): Line 867 uses numbered variable "data1" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:899): Line 899 uses numbered variable "boto3" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:903): Line 903 uses numbered variable "s3" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:904): Line 904 uses numbered variable "s3" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:920): Line 920 uses numbered variable "50" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1323): Line 1323 uses numbered variable "source_file1" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1328): Line 1328 uses numbered variable "source_file2" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1333): Line 1333 uses numbered variable "source_file1" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1512): Line 1512 uses numbered variable "500" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1586): Line 1586 uses numbered variable "500" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1994): Line 1994 uses numbered variable "240" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2005): Line 2005 uses numbered variable "240" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2019): Line 2019 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2024): Line 2024 uses numbered variable "2025" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2042): Line 2042 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2046): Line 2046 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2049): Line 2049 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2050): Line 2050 uses numbered variable "10" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2060): Line 2060 uses numbered variable "11" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2122): Line 2122 uses numbered variable "180" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2143): Line 2143 uses numbered variable "180" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2341): Line 2341 uses numbered variable "12" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2342): Line 2342 uses numbered variable "15" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2728): Line 2728 uses numbered variable "999" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2731): Line 2731 uses numbered variable "999" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:3286): Line 3286 uses numbered variable "15" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:3542): Line 3542 uses numbered variable "source_file1" - use meaningful descriptive name
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:3546): Line 3546 uses numbered variable "source_file1" - use meaningful descriptive name

#### Refactor Completely Not Partially: 8 violation(s)

- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:351): Commented-out old code found (lines 351-351) - complete refactoring by deleting old code
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:358): Commented-out old code found (lines 358-358) - complete refactoring by deleting old code
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:365): Commented-out old code found (lines 365-365) - complete refactoring by deleting old code
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:1149): Commented-out old code found (lines 1149-1149) - complete refactoring by deleting old code
- 🟡 **WARNING** - [`server_restart.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/server_restart.py:175): Commented-out old code found (lines 175-175) - complete refactoring by deleting old code
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:857): Commented-out old code found (lines 857-858) - complete refactoring by deleting old code
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:3454): Commented-out old code found (lines 3454-3454) - complete refactoring by deleting old code
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:856): Line 856 supports both old and new patterns - complete refactoring by removing old pattern support

#### Remove Bad Comments: 159 violation(s)

- 🟡 **WARNING** - [`base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/base_action.py:165): Line 165 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`behavior_folder_finder.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/behavior_folder_finder.py:94): Line 94 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:255): Line 255 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:400): Line 400 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:403): Line 403 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:706): Line 706 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:709): Line 709 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:24): Line 24 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:80): Line 80 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:112): Line 112 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:285): Line 285 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:334): Line 334 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:485): Line 485 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:641): Line 641 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:648): Line 648 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:147): Line 147 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:228): Line 228 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:284): Line 284 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`gather_context_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/gather_context_action.py:19): Line 19 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`gather_context_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/gather_context_action.py:40): Line 40 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`gather_context_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/gather_context_action.py:77): Line 77 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`gather_context_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/gather_context_action.py:109): Line 109 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`planning_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/planning_action.py:83): Line 83 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:151): Line 151 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:176): Line 176 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:266): Line 266 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:272): Line 272 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:286): Line 286 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:377): Line 377 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:403): Line 403 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:421): Line 421 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:434): Line 434 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:445): Line 445 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:491): Line 491 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:509): Line 509 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:639): Line 639 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:720): Line 720 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:723): Line 723 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:759): Line 759 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:943): Line 943 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:960): Line 960 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:1242): Line 1242 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:1): Line 1 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:152): Line 152 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:212): Line 212 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:262): Line 262 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:317): Line 317 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:411): Line 411 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:414): Line 414 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:479): Line 479 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:485): Line 485 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:501): Line 501 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:616): Line 616 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:622): Line 622 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:31): Line 31 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:66): Line 66 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:69): Line 69 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:143): Line 143 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:159): Line 159 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:195): Line 195 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:200): Line 200 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:204): Line 204 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:235): Line 235 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:284): Line 284 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:320): Line 320 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`trigger_router.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/trigger_router.py:35): Line 35 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`trigger_router.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/trigger_router.py:111): Line 111 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:26): Line 26 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:232): Line 232 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:260): Line 260 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:301): Line 301 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:514): Line 514 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:736): Line 736 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:755): Line 755 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:788): Line 788 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:837): Line 837 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:845): Line 845 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:855): Line 855 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:929): Line 929 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`workflow.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/workflow.py:319): Line 319 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:27): Line 27 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:61): Line 61 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_build_knowledge.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_build_knowledge.py:168): Line 168 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_decide_planning_criteria_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria_action.py:25): Line 25 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_decide_planning_criteria_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria_action.py:28): Line 28 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_decide_planning_criteria_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria_action.py:36): Line 36 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_decide_planning_criteria_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria_action.py:215): Line 215 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_execute_behavior_actions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_execute_behavior_actions.py:34): Line 34 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_execute_behavior_actions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_execute_behavior_actions.py:57): Line 57 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_execute_behavior_actions.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_execute_behavior_actions.py:141): Line 141 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:37): Line 37 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:258): Line 258 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:262): Line 262 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:289): Line 289 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:378): Line 378 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:22): Line 22 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:199): Line 199 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:230): Line 230 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:24): Line 24 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:27): Line 27 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:30): Line 30 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:284): Line 284 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:442): Line 442 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:802): Line 802 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:841): Line 841 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:860): Line 860 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:866): Line 866 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1005): Line 1005 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1040): Line 1040 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1120): Line 1120 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:1198): Line 1198 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:24): Line 24 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:71): Line 71 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:81): Line 81 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:140): Line 140 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:219): Line 219 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:341): Line 341 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:345): Line 345 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:355): Line 355 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:412): Line 412 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:415): Line 415 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:431): Line 431 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:433): Line 433 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:437): Line 437 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:458): Line 458 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:23): Line 23 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:26): Line 26 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_init_project.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_init_project.py:74): Line 74 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_cli.py:208): Line 208 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_cli.py:453): Line 453 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_cli.py:467): Line 467 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_mcp.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_mcp.py:28): Line 28 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_mcp.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_mcp.py:31): Line 31 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_mcp.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_mcp.py:53): Line 53 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_mcp.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_mcp.py:75): Line 75 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_invoke_mcp.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_mcp.py:464): Line 464 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:33): Line 33 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:62): Line 62 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:95): Line 95 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:404): Line 404 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:445): Line 445 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:699): Line 699 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:1258): Line 1258 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:1366): Line 1366 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:1683): Line 1683 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:24): Line 24 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_render_output.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_render_output.py:329): Line 329 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:49): Line 49 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:857): Line 857 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1533): Line 1533 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1716): Line 1716 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1932): Line 1932 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2310): Line 2310 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2317): Line 2317 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2324): Line 2324 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2331): Line 2331 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2345): Line 2345 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:3310): Line 3310 has commented-out code - call production code directly, even if API doesn't exist yet
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:3318): Line 3318 has commented-out code - call production code directly, even if API doesn't exist yet

#### Separate Concerns: 20 violation(s)

- 🔴 **ERROR** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:230): Function "_check_existing_output_file" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:654): Function "_estimate_tokens" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:169): Function "injectValidationInstructions" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`planning_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/planning_action.py:14): Function "do_execute" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`planning_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/planning_action.py:34): Function "inject_decision_criteria_and_assumptions" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`planning_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/planning_action.py:76): Function "save_planning" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:620): Function "injectValidationInstructions" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:809): Function "_write_validation_report" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:299): Function "_update_bot_registry" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:184): Function "register_close_current_action_tool" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`test_decide_planning_criteria_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria_action.py:85): Function "given_planning_json_exists_with_data" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`test_decide_planning_criteria_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria_action.py:135): Function "then_planning_json_contains_behavior_data" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`test_decide_planning_criteria_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria_action.py:182): Function "given_environment_with_existing_planning_and_action" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`test_decide_planning_criteria_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria_action.py:287): Function "test_save_planning_data_when_parameters_provided" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`test_decide_planning_criteria_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_decide_planning_criteria_action.py:327): Function "test_skip_saving_when_no_planning_parameters_provided" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:179): Function "given_environment_bootstrapped_for_workflow_resume" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`test_gather_context.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_gather_context.py:474): Function "test_workflow_resumes_at_decide_planning_criteria_after_interruption" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`test_helpers.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_helpers.py:97): Function "create_planning_guardrails" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:824): Function "_create_code_file_for_scanner_type" mixes calculations with I/O/infrastructure - separate pure logic from side effects
- 🔴 **ERROR** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:3230): Function "test_violation_report_generation_in_different_formats" mixes calculations with I/O/infrastructure - separate pure logic from side effects

#### Simplify Control Flow: 43 violation(s)

- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:160): Function "rules" has nesting depth of 5 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:311): Function "_get_action_class" has nesting depth of 5 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:628): Function "forward_to_current_behavior_and_current_action" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:653): Function "does_requested_behavior_match_current" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:730): Function "execute_behavior" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:321): Function "inject_schema_description_instructions" has nesting depth of 6 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:441): Function "_load_behavior_specific_instructions" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:470): Function "_format_rules" has nesting depth of 6 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:21): Function "do_execute" has nesting depth of 5 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:169): Function "injectValidationInstructions" has nesting depth of 11 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`render_output_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/render_output_action.py:75): Function "_find_render_folder" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`render_output_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/render_output_action.py:146): Function "_verify_synchronizer_class" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`render_output_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/render_output_action.py:241): Function "_inject_render_instructions" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`render_output_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/render_output_action.py:272): Function "_format_render_configs" has nesting depth of 5 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:90): Function "_load_scanner_class" has nesting depth of 6 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:141): Function "do_execute" has nesting depth of 6 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:402): Function "inject_behavior_specific_and_bot_rules" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:556): Function "discover_scanners" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:584): Function "_load_scanner_class" has nesting depth of 5 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:620): Function "injectValidationInstructions" has nesting depth of 10 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:809): Function "_write_validation_report" has nesting depth of 7 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:1252): Function "generate_report" has nesting depth of 6 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:109): Function "help_behaviors_and_actions" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:147): Function "_get_action_description" has nesting depth of 8 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:189): Function "help_cursor_commands" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:247): Function "_get_behavior_description" has nesting depth of 6 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:425): Function "_parse_action_parameters" has nesting depth of 8 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:516): Function "main" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`trigger_router.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/trigger_router.py:259): Function "_load_behavior_triggers" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:184): Function "register_close_current_action_tool" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:635): Function "_load_trigger_words_from_behavior_folder" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:831): Function "_generate_workspace_rules_file" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`server_restart.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/server_restart.py:16): Function "find_mcp_server_processes" has nesting depth of 5 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`workflow.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/workflow.py:92): Function "load_state" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`workflow.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/workflow.py:281): Function "_remove_completed_actions_after_target" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`test_generate_mcp_tools.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_mcp_tools.py:603): Function "then_trigger_words_in_behavior_section" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`test_perform_behavior_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_perform_behavior_action.py:231): Function "then_base_instructions_include_next_behavior_reminder" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:618): Function "when_convert_expected_violations_to_set" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:824): Function "_create_code_file_for_scanner_type" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:1653): Function "when_extract_violations_from_validation_rules" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2720): Function "_handle_increment_priorities_scope" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2736): Function "_handle_epic_names_scope" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:2771): Function "_extract_story_names_from_epic" has nesting depth of 4 - use guard clauses and extract nested blocks to reduce nesting

#### Stop Writing Useless Comments: 1 violation(s)

- 🔴 **ERROR** - [`behavior_tool_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/behavior_tool_generator.py:36): Useless comment: "# Load bot config to get behaviors" - delete it or improve the code instead

#### Test One Concept Per Test: 5 violation(s)

- 🟡 **WARNING** - [`test_generate_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:107): Test method [test_rules_file_includes_bot_goal_and_behavior_descriptions](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_generate_cli.py:107) appears to test multiple concepts - split into separate tests, one concept per test
- 🟡 **WARNING** - [`test_invoke_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_cli.py:473): Test method [test_trigger_bot_only_no_behavior_or_action_specified](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_cli.py:473) appears to test multiple concepts - split into separate tests, one concept per test
- 🟡 **WARNING** - [`test_invoke_mcp.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_mcp.py:335): Test method [test_bot_tool_forwards_to_current_behavior_and_current_action](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_mcp.py:335) appears to test multiple concepts - split into separate tests, one concept per test
- 🟡 **WARNING** - [`test_invoke_mcp.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_mcp.py:356): Test method [test_bot_tool_defaults_to_first_behavior_and_first_action_when_state_missing](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_invoke_mcp.py:356) appears to test multiple concepts - split into separate tests, one concept per test
- 🟡 **WARNING** - [`test_validate_knowledge_and_content_against_rules.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:3502): Test method [test_validate_code_files_action_merges_violations_from_knowledge_graph_and_files](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py:3502) appears to test multiple concepts - split into separate tests, one concept per test

#### Use Clear Function Parameters: 1 violation(s)

- 🟡 **WARNING** - [`activity_tracker.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/activity_tracker.py:40): Function "track_completion" has 6 parameters - consider using parameter object or reducing parameters

#### Use Intention Revealing Names: 86 violation(s)

- 🔴 **ERROR** - [`base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/base_action.py:119): Variable "_" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`base_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/base_action.py:126): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:60): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:63): Variable "x" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:58): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:344): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:727): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:932): Variable "b" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`bot.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/bot.py:932): Variable "b" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:187): Variable "f" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:204): Variable "f" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:188): Variable "f" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:205): Variable "f" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:251): Variable "f" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:252): Variable "f" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`build_knowledge_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/build_knowledge_action.py:75): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:99): Variable "f" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:99): Variable "f" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:165): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:282): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:282): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:100): Variable "f" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:278): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`code_quality_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/code_quality_action.py:100): Variable "f" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`gather_context_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/gather_context_action.py:74): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`gather_context_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/gather_context_action.py:74): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`planning_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/planning_action.py:122): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`planning_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/planning_action.py:122): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`render_output_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/render_output_action.py:111): Variable "f" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`render_output_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/render_output_action.py:111): Variable "f" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`render_output_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/render_output_action.py:111): Variable "f" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`render_output_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/render_output_action.py:128): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`render_output_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/render_output_action.py:181): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`render_output_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/render_output_action.py:203): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`render_output_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/render_output_action.py:100): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`render_output_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/render_output_action.py:119): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:383): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:379): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:132): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:374): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:618): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:1075): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:1198): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:762): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:373): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:762): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:1074): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:892): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:921): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`validate_rules_action.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/bot/validate_rules_action.py:757): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:533): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:136): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:240): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:452): Variable "f" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:452): Variable "f" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`base_bot_cli.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/base_bot_cli.py:516): Function "main" uses generic name - use intention-revealing name that explains purpose
- 🔴 **ERROR** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:59): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:60): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`cli_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/cli_generator.py:58): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`trigger_router_entry.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/cli/trigger_router_entry.py:20): Function "main" uses generic name - use intention-revealing name that explains purpose
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:49): Variable "_" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:48): Variable "x" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:73): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:74): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:534): Variable "a" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:314): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:386): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:443): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:534): Variable "a" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:559): Variable "a" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:72): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:439): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:481): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`mcp_server_generator.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/mcp_server_generator.py:559): Variable "a" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`server_restart.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/server_restart.py:183): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`server_restart.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/server_restart.py:43): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`server_restart.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/server_restart.py:182): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`server_restart.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/server_restart.py:77): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`server_restart.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/server_restart.py:95): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`server_restart.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/mcp/server_restart.py:127): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`workflow.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/workflow.py:90): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`workflow.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/workflow.py:129): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`workflow.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/workflow.py:246): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`workflow.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/workflow.py:342): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`workflow.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/workflow.py:192): Variable "e" uses single-letter name - use intention-revealing name
- 🔴 **ERROR** - [`workflow.py`](vscode://file/C:/dev/augmented-teams/agile_bot/bots/base_bot/src/state/workflow.py:217): Variable "e" uses single-letter name - use intention-revealing name

## Validation Instructions

The following validation steps were performed:

1. **MANDATORY: Before validating any content, you MUST load and review the project's context files:**
2. 1. Load `{project_area}/docs/stories/clarification.json` - Contains key questions and evidence (generated file)
3. 2. Load `{project_area}/docs/stories/planning.json` - Contains assumptions and decisions (generated file)
4. 3. Load `{project_area}/docs/context/input.txt` (or similar) - Original input/source material if needed for validation (original context)
5. 
6. **CRITICAL: File locations:**
7. - **Generated files:** `{project_area}/docs/stories/clarification.json`, `{project_area}/docs/stories/planning.json`
8. - **Original input:** `{project_area}/docs/context/input.txt` and other original context files
9. 
10. These files contain critical requirements, decisions, and context that MUST be checked against during validation.
*... and 241 more instructions*

## Report Location

This report was automatically generated and saved to:
`C:\dev\augmented-teams\agile_bot\bots\base_bot\docs\stories\validation-report.md`
