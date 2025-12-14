# Test File Mapping to Story Graph

This document shows the mapping between test files, classes, and methods to stories in the story graph.

## Epic: Build Agile Bots

### Sub-Epic: Generate MCP Tools

#### Story: Generate Bot Tools
- **Test File**: `test_generate_mcp_tools.py`
  - **Class**: `TestGenerateBotTools`
    - `test_generator_creates_bot_tool_for_test_bot`

#### Story: Generate Behavior Tools
- **Test File**: `test_generate_mcp_tools.py`
  - **Class**: `TestGenerateBehaviorTools`
    - `test_generator_creates_behavior_tools_for_test_bot_with_4_behaviors`

#### Story: Generate MCP Bot Server
- **Test File**: `test_generate_mcp_tools.py`
  - **Class**: `TestGenerateMCPBotServer`
    - `test_generator_creates_mcp_server_for_test_bot`
    - `test_generator_fails_when_bot_config_missing`
    - `test_generator_fails_when_bot_config_malformed`

#### Story: Generate Behavior Action Tools
- **Test File**: `test_generate_mcp_tools.py`
  - **Class**: `TestGenerateBehaviorActionTools`
    - `test_generator_creates_tools_for_test_bot_with_4_behaviors`
    - `test_generator_loads_trigger_words_from_behavior_folder`
    - `test_generator_handles_missing_trigger_words`

#### Story: Deploy MCP Bot Server
- **Test File**: `test_generate_mcp_tools.py`
  - **Class**: `TestDeployMCPBotServer`
    - `test_generator_deploys_server_successfully`
    - `test_server_publishes_tool_catalog_with_metadata`
    - `test_generator_fails_when_protocol_handler_not_running`

#### Story: Handle MCP Generator Exceptions
- **Test File**: `test_generate_mcp_tools.py`
  - **Class**: `TestMCPGeneratorExceptions`
    - `test_mcp_generator_raises_exception_when_base_actions_not_found`

#### Story: Restart MCP Server To Load Code Changes
- **Test File**: `test_generate_mcp_tools.py`
  - **Class**: `TestRestartMCPServerToLoadCodeChanges`
    - `test_clear_python_bytecode_cache`
    - `test_find_mcp_server_processes`

### Sub-Epic: Generate CLI

#### Story: Generate BOT CLI code
- **Test File**: `test_generate_cli.py`
  - **Class**: `TestGenerateBOTCLIcode`

#### Story: Generate Cursor Command Files
- **Test File**: `test_generate_cli.py`
  - **Class**: `TestGenerateCursorCommandFiles`

#### Story: Generate Cursor Awareness Files
- **Test File**: `test_generate_cli.py`
  - **Class**: `TestGenerateCursorAwarenessFiles`
    - `test_generator_creates_workspace_rules_file_with_trigger_patterns`
    - `test_rules_file_includes_bot_goal_and_behavior_descriptions`
    - `test_rules_file_maps_trigger_patterns_to_tool_naming_conventions`

## Epic: Invoke Bot

### Sub-Epic: Init Project

#### Story: Store Context Files
- **[NO TESTS]**

#### Story: Stores Activity for Initialize Project Action
- **[NO TESTS]**

#### Story: Initialize Project Location
- **[NO TESTS]**

### Sub-Epic: Invoke MCP

#### Story: Invoke Bot Tool
- **Test File**: `test_invoke_mcp.py`
  - **Class**: `TestInvokeBotTool`
    - `test_tool_invokes_behavior_action_when_called`
    - `test_tool_routes_to_correct_behavior_action_method`

#### Story: Load And Merge Behavior Action Instructions
- **Test File**: `test_invoke_mcp.py`
  - **Class**: `TestLoadAndMergeBehaviorActionInstructions`
    - `test_action_loads_and_merges_instructions`

#### Story: Forward To Current Behavior and Current Action
- **Test File**: `test_invoke_mcp.py`
  - **Class**: `TestForwardToCurrentBehaviorAndCurrentAction`
    - `test_bot_tool_forwards_to_current_behavior_and_current_action`
    - `test_bot_tool_defaults_to_first_behavior_and_first_action_when_state_missing`

#### Story: Forward To Current Action
- **Test File**: `test_invoke_mcp.py`
  - **Class**: `TestForwardToCurrentAction`
    - `test_behavior_tool_forwards_to_current_action_within_behavior`
    - `test_behavior_tool_sets_workflow_to_current_behavior_when_state_shows_different_behavior`
    - `test_behavior_tool_defaults_to_first_action_when_state_missing`
    - `test_action_called_directly_saves_workflow_state`

#### Story: Save Through MCP
- **[NO TESTS]**

### Sub-Epic: Invoke CLI

#### Story: Invoke Bot CLI
- **[NO TESTS]**

#### Story: Invoke Bot Behavior CLI
- **[NO TESTS]**

#### Story: Invoke Bot Behavior Action CLI
- **[NO TESTS]**

#### Story: Get Help for Command Line Functions
- **[NO TESTS]**

#### Story: Detect Trigger Words Through Extension
- **Test File**: `test_invoke_cli.py`
  - **Class**: `TestDetectTriggerWordsThroughExtension`
    - `test_trigger_bot_only_no_behavior_or_action_specified`
    - `test_trigger_bot_and_behavior_no_action_specified`
    - `test_trigger_bot_behavior_and_action_explicitly`
    - `test_trigger_close_current_action`

#### Story: Save Through CLI
- **[NO TESTS]**

### Sub-Epic: Perform Behavior Action

#### Story: Close Current Action
- **Test File**: `test_perform_behavior_action.py`
  - **Class**: `TestCloseCurrentAction`
    - `test_close_current_action_marks_complete_and_transitions`
    - `test_close_action_at_final_action_stays_at_final`
    - `test_close_final_action_transitions_to_next_behavior`

#### Story: Complete Workflow Integration
- **[NO TESTS]**

#### Story: Find Behavior Folder
- **[NO TESTS]** (Note: `test_utils.py` has `TestFindBehaviorFolder`)

## Epic: Execute Behavior Actions

### Sub-Epic: Gather Context

#### Story: Track Activity for Gather Context Action
- **Test File**: `test_gather_context.py`
  - **Class**: `TestTrackActivityForGatherContextAction`
    - `test_track_activity_when_gather_context_action_starts`
    - `test_track_activity_when_gather_context_action_completes`
    - `test_track_multiple_gather_context_invocations_across_behaviors`
  - **Class**: `TestInjectGuardrailsAsPartOfClarifyRequirements`
    - `test_action_injects_questions_and_evidence`
    - `test_action_uses_base_instructions_when_guardrails_missing`
    - `test_action_handles_malformed_guardrails_json`
  - **Class**: `TestStoreClarificationData`
    - `test_save_clarification_data_when_parameters_provided`
    - `test_preserve_existing_clarification_data_when_saving`
    - `test_skip_saving_when_no_clarification_parameters_provided`

#### Story: Proceed To Decide Planning
- **Test File**: `test_gather_context.py`
  - **Class**: `TestProceedToDecidePlanning`
    - `test_seamless_transition_from_gather_context_to_decide_planning_criteria`
    - `test_workflow_state_captures_gather_context_completion`
    - `test_workflow_resumes_at_decide_planning_criteria_after_interruption`

#### Story: Gather Context Saves To Context Folder
- **[NO TESTS]**

#### Story: Load + Inject Guardrails
- **[NO TESTS]**

#### Story: Gather Context Action Guardrails
- **[NO TESTS]**

#### Story: Saves Answers and Evidence
- **[NO TESTS]**

### Sub-Epic: Decide Planning Criteria Action

#### Story: Inject Planning Criteria Into Instructions
- **Test File**: `test_decide_planning_criteria_action.py`
  - **Class**: `TestInjectPlanningCriteriaIntoInstructions`
    - `test_action_injects_decision_criteria_and_assumptions`
    - `test_action_uses_base_planning_when_guardrails_missing`

#### Story: Track Activity for Planning Action
- **Test File**: `test_decide_planning_criteria_action.py`
  - **Class**: `TestTrackActivityForPlanningAction`
    - `test_track_activity_when_planning_action_starts`
    - `test_track_activity_when_planning_action_completes`

#### Story: Proceed To Build Knowledge
- **Test File**: `test_build_knowledge.py`
  - **Class**: `TestInjectKnowledgeGraphTemplateForBuildKnowledge`
    - `test_action_injects_knowledge_graph_template`
    - `test_action_raises_error_when_template_missing`
    - `test_action_loads_and_merges_instructions`
  - **Class**: `TestUpdateExistingKnowledgeGraph`
    - `test_behavior_updates_existing_story_graph_json`
- **Test File**: `test_decide_planning_criteria_action.py`
  - **Class**: `TestProceedToBuildKnowledge`
    - `test_seamless_transition_from_planning_to_build_knowledge`
    - `test_workflow_state_captures_planning_completion`

#### Story: Save Final Assumptions and Decisions
- **[NO TESTS]**

### Sub-Epic: Build Knowledge

#### Story: Load Story Graph Into Memory
- **Test File**: `test_build_knowledge.py`
  - **Class**: `TestLoadStoryGraphIntoMemory`
    - `test_story_map_loads_epics`
    - `test_epic_has_sub_epics`
    - `test_sub_epic_has_story_groups`
    - (17 more methods)

#### Story: Inject Knowledge Graph Template and Builder Instructions
- **[NO TESTS]**

#### Story: Track Activity for Build Knowledge Action
- **Test File**: `test_build_knowledge.py`
  - **Class**: `TestTrackActivityForBuildKnowledgeAction`
    - `test_track_activity_when_build_knowledge_action_starts`
    - `test_track_activity_when_build_knowledge_action_completes`

#### Story: Proceed To Render Output
- **Test File**: `test_build_knowledge.py`
  - **Class**: `TestProceedToRenderOutput`
    - `test_seamless_transition_from_build_knowledge_to_validate_rules`
    - `test_workflow_state_captures_build_knowledge_completion`
- **Test File**: `test_render_output.py`
  - **Class**: `TestInjectRenderInstructionsAndConfigs`
    - `test_all_template_variables_are_replaced_in_instructions`
    - `test_render_configs_format_includes_all_fields`

#### Story: Load + Inject Knowledge Graph
- **[NO TESTS]**

#### Story: Save Knowledge Graph
- **[NO TESTS]**

### Sub-Epic: Render Output

#### Story: Load Render Configurations
- **[NO TESTS]**

#### Story: Track Activity for Render Output Action
- **Test File**: `test_render_output.py`
  - **Class**: `TestTrackActivityForRenderOutputAction`
    - `test_track_activity_when_render_output_action_starts`
    - `test_track_activity_when_render_output_action_completes`
    - `test_track_multiple_render_output_invocations_across_behaviors`

#### Story: Load+ Inject Content Into Instructions
- **[NO TESTS]**

#### Story: Save Content
- **[NO TESTS]**

#### Story: Proceed To Validate Rules
- **Test File**: `test_render_output.py`
  - **Class**: `TestProceedToValidateRules`
    - `test_seamless_transition_from_validate_rules_to_render_output`
    - `test_workflow_state_captures_render_output_completion`
    - `test_render_output_action_executes_successfully`

### Sub-Epic: Validate Knowledge & Content Against Rules

#### Story: Track Activity for Validate Rules Action
- **Test File**: `test_validate_knowledge_and_content_against_rules.py`
  - **Class**: `TestTrackActivityForValidateRulesAction`
    - `test_track_activity_when_validate_rules_action_starts`
    - `test_track_activity_when_validate_rules_action_completes`
    - `test_track_multiple_validate_rules_invocations_across_behaviors`

#### Story: Inject Validation Rules for Validate Rules Action
- **[NO TESTS]**

#### Story: Discover Scanners
- **[NO TESTS]** (Note: `test_validate_knowledge_and_content_against_rules.py` has `TestDiscoversScanners`)

#### Story: Run Scanners After Build Knowledge
- **[NO TESTS]** (Note: `test_validate_knowledge_and_content_against_rules.py` has `TestRunScannersAgainstKnowledgeGraph`)

#### Story: Detect Violations Using Regex Patterns
- **[NO TESTS]**

#### Story: Collect Violations from All Scanners
- **[NO TESTS]**

#### Story: Load Scanner Classes
- **[NO TESTS]**

#### Story: Run Scanners After Render Output
- **[NO TESTS]** (Note: `test_validate_knowledge_and_content_against_rules.py` has `TestRunScannersAgainstTestCode` and `TestRunScannersAgainstCode`)

#### Story: Detect Violations Using AST Parsing
- **[NO TESTS]**

#### Story: Report Violations with Location Context
- **[NO TESTS]** (Note: `test_validate_knowledge_and_content_against_rules.py` has `TestGenerateViolationReport`)

#### Story: Run Scanners Before AI Validation
- **[NO TESTS]**

#### Story: Detect Violations Using File Structure Analysis
- **[NO TESTS]**

#### Story: Run Diagnostics + inject Results
- **[NO TESTS]**

## Unmapped Test Files

These test files contain classes that couldn't be automatically matched to stories:

- `test_init_project.py` - Contains `TestBootstrapWorkspace`
- `test_perform_behavior_action.py` - Contains additional classes: `TestInjectNextBehaviorReminder`, `TestInvokeBehaviorActionsInWorkflowOrder`, `TestInvokeBehaviorInWorkflowOrder`, `TestExecuteBehavior`, `TestBotBehaviorExceptions`
- `test_invoke_cli.py` - Contains `TestCLIExceptions`, `TestRouterExceptions`
- `test_validate_knowledge_and_content_against_rules.py` - Contains many additional test classes for validation workflow

## Summary

- **Total Stories**: ~60+
- **Stories with Tests**: ~25
- **Stories without Tests**: ~35+
- **Test Files Analyzed**: 14
- **Test Classes Found**: ~50+

