# Epic: Start Story Development Session
# Feature: Initialize Story Agent Workflow
# Story: Initialize Behavior and Workflow
#
# Story Description:
#After Project initialization, Agent loads base and Story Agent configurations
# (instruction templates, trigger words, Rules, Behaviors), connects Workflow to
# Project, Workflow sets up stages, and Agent starts workflow at first behavior
# and action

Feature: Initialize Behavior and Workflow
  As a developer
  I want to test the story scenarios
  So that the requirements are verified

  Background:
    Given Project is finished initializing
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:921:when_project_finished_init
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:921:when_project_finished_init
    And agents/base/agent.json exists and is valid
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:902:given_base_config_valid
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:902:given_base_config_valid
    And agents/stories/agent.json exists and is valid
    And Workflow instance exists in Project
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:914:given_workflow_exists
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:914:given_workflow_exists

  Scenario: Agent loads configurations and initializes workflow successfully
    When Project is finished initializing
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:921:when_project_finished_init
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:921:when_project_finished_init
    Then Agent loads base configuration by reading agents/base/agent.json
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:927:then_agent_loads_base_config
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:927:then_agent_loads_base_config
    And Agent extracts base instruction templates and base trigger words
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:934:then_agent_extracts_base
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:934:then_agent_extracts_base
    And Agent stores them for use in future instruction generation
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:940:then_agent_stores_base
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:940:then_agent_stores_base
    When Agent has loaded base configuration
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:946:when_agent_loaded_base
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:946:when_agent_loaded_base
    Then Agent loads Story Agent configuration by reading agents/stories/agent.json
    And Agent extracts agent-specific instruction templates and agent-specific trigger words
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:958:then_agent_extracts_story
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:958:then_agent_extracts_story
    And Agent creates Rules objects from rules configuration
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:964:then_agent_creates_rules
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:964:then_agent_creates_rules
    And Agent creates Behavior objects for each workflow behavior
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:970:then_agent_creates_behaviors
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:970:then_agent_creates_behaviors
    And Agent stores behaviors in dictionary
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:977:then_agent_stores_behaviors
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:977:then_agent_stores_behaviors
    And Agent presents configuration summary to user for confirmation
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:983:then_agent_presents_config_summary
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:983:then_agent_presents_config_summary
    When Agent connects Workflow to Project
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:992:when_agent_connects_workflow
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:992:when_agent_connects_workflow
    Then Agent links Workflow instance to Agent
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:998:then_agent_links_workflow
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:998:then_agent_links_workflow
    And Agent passes behaviors dictionary to Workflow
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1240:when_agent_passes_behaviors_dict
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1240:when_agent_passes_behaviors_dict
    When Workflow receives behaviors dictionary
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1011:when_workflow_receives_behaviors
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1011:when_workflow_receives_behaviors
    Then Workflow sorts behaviors by their order property
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1017:then_workflow_sorts_behaviors
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1017:then_workflow_sorts_behaviors
    And Workflow creates ordered list of stage names
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1023:then_workflow_creates_stages
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1023:then_workflow_creates_stages
    And Workflow sets up workflow stages
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1030:then_workflow_sets_up_stages
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1030:then_workflow_sets_up_stages
    When Agent starts workflow for new project
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1036:when_agent_starts_workflow
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1036:when_agent_starts_workflow
    Then Agent calls Workflow to start
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1308:when_agent_calls_workflow_start
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1308:when_agent_calls_workflow_start
    And Workflow gets first behavior from sorted stages (shape behavior with order=1)
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1048:then_workflow_gets_first_behavior
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1048:then_workflow_gets_first_behavior
    And Workflow initializes first action of that behavior (clarification action)
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1058:then_workflow_initializes_first_action
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1058:then_workflow_initializes_first_action
    And Workflow sets current_stage and current_action
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1065:then_workflow_sets_current
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1065:then_workflow_sets_current
    And Agent presents workflow state to user for confirmation
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1072:then_agent_presents_workflow_state
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1072:then_agent_presents_workflow_state

  Scenario: Workflow synchronization ensures consistency
    Given Project is finished initializing
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:921:when_project_finished_init
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:921:when_project_finished_init
    And Agent has loaded configurations
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1082:given_agent_loaded_configs
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1082:given_agent_loaded_configs
    And Workflow has been set up
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1088:given_workflow_set_up
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1088:given_workflow_set_up
    And Agent workflow and Project workflow may reference different objects
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1094:given_workflows_may_differ
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1094:given_workflows_may_differ
    When AgentStateManager synchronizes workflow
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1100:when_manager_synchronizes
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1100:when_manager_synchronizes
    Then AgentStateManager verifies Project has workflow attribute
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1108:then_manager_verifies_project_workflow
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1108:then_manager_verifies_project_workflow
    And AgentStateManager checks if Agent workflow and Project workflow reference the same object
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1114:then_manager_checks_same_object
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1114:then_manager_checks_same_object
    When Agent workflow and Project workflow reference different objects
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1121:when_workflows_reference_different
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1121:when_workflows_reference_different
    Then AgentStateManager updates Project workflow to reference Agent workflow
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1127:then_manager_updates_project_workflow
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1127:then_manager_updates_project_workflow
    When MCP Server synchronizes project workflow
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1133:when_mcp_synchronizes
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1133:when_mcp_synchronizes
    Then MCP Server ensures Project workflow reference matches Agent workflow reference
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1139:then_mcp_ensures_match
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1139:then_mcp_ensures_match
    And MCP Server updates Project workflow if needed
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1145:then_mcp_updates_if_needed
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1145:then_mcp_updates_if_needed
    And system does not crash from workflow reference mismatch
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1151:then_system_no_crash_workflow
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1151:then_system_no_crash_workflow

  Scenario: Agent fails to load base configuration
    Given Project is finished initializing
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:921:when_project_finished_init
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:921:when_project_finished_init
    And agents/base/agent.json does not exist or is corrupted
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1157:given_base_config_missing_or_corrupted
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1157:given_base_config_missing_or_corrupted
    When Project is finished initializing
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:921:when_project_finished_init
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:921:when_project_finished_init
    And Agent attempts to load base configuration
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1165:when_agent_attempts_load_base_config
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1165:when_agent_attempts_load_base_config
    Then Agent handles missing or corrupted base config error gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1180:then_agent_handles_base_config_error
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1180:then_agent_handles_base_config_error
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And appropriate error is presented to user in chat
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1186:then_error_presented_to_user_chat
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1186:then_error_presented_to_user_chat
    And Agent does not proceed to load agent-specific configuration
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1192:then_agent_no_proceed_agent_config
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1192:then_agent_no_proceed_agent_config

  Scenario: Agent fails to load agent-specific configuration
    Given Project is finished initializing
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:921:when_project_finished_init
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:921:when_project_finished_init
    And agents/base/agent.json exists and is valid
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:902:given_base_config_valid
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:902:given_base_config_valid
    And agents/stories/agent.json does not exist or is corrupted
    When Project is finished initializing
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:921:when_project_finished_init
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:921:when_project_finished_init
    Then Agent loads base configuration successfully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1207:then_agent_loads_base_success
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1207:then_agent_loads_base_success
    When Agent attempts to load Story Agent configuration
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1213:when_agent_attempts_load_story_config
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1213:when_agent_attempts_load_story_config
    Then Agent handles missing or corrupted agent config error gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1219:then_agent_handles_agent_config_error
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1219:then_agent_handles_agent_config_error
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And appropriate error is presented to user in chat
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1186:then_error_presented_to_user_chat
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1186:then_error_presented_to_user_chat
    And Agent does not proceed to create behaviors or initialize workflow
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1225:then_agent_no_proceed_behaviors
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1225:then_agent_no_proceed_behaviors

  Scenario: Workflow receives behaviors dictionary with missing order property
    Given Project is finished initializing
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:921:when_project_finished_init
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:921:when_project_finished_init
    And Agent has loaded configurations
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1082:given_agent_loaded_configs
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1082:given_agent_loaded_configs
    And behaviors dictionary contains behavior without order property
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1232:given_behaviors_missing_order
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1232:given_behaviors_missing_order
    When Agent passes behaviors dictionary to Workflow
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1240:when_agent_passes_behaviors_dict
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1240:when_agent_passes_behaviors_dict
    And Workflow attempts to sort behaviors by order property
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1246:when_workflow_attempts_sort
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1246:when_workflow_attempts_sort
    Then Workflow handles missing order property gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1252:then_workflow_handles_missing_order
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1252:then_workflow_handles_missing_order
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And Workflow uses default ordering or skips invalid behaviors
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1258:then_workflow_uses_default
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1258:then_workflow_uses_default
    And appropriate error is logged
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1264:then_error_logged
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1264:then_error_logged

  Scenario: Workflow receives behaviors dictionary with duplicate order values
    Given Project is finished initializing
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:921:when_project_finished_init
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:921:when_project_finished_init
    And Agent has loaded configurations
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1082:given_agent_loaded_configs
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1082:given_agent_loaded_configs
    And behaviors dictionary contains multiple behaviors with same order value
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1270:given_behaviors_duplicate_order
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1270:given_behaviors_duplicate_order
    When Agent passes behaviors dictionary to Workflow
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1240:when_agent_passes_behaviors_dict
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1240:when_agent_passes_behaviors_dict
    And Workflow attempts to sort behaviors by order property
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1246:when_workflow_attempts_sort
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1246:when_workflow_attempts_sort
    Then Workflow handles duplicate order values gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1276:then_workflow_handles_duplicate
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1276:then_workflow_handles_duplicate
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And Workflow uses secondary sorting criteria or maintains insertion order
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1282:then_workflow_uses_secondary
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1282:then_workflow_uses_secondary
    And workflow stages are set up correctly
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1288:then_workflow_stages_correct
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1288:then_workflow_stages_correct

  Scenario: Workflow fails to get first behavior from sorted stages
    Given Project is finished initializing
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:921:when_project_finished_init
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:921:when_project_finished_init
    And Agent has loaded configurations
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1082:given_agent_loaded_configs
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1082:given_agent_loaded_configs
    And Workflow has set up stages
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1295:given_workflow_set_up_stages
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1295:given_workflow_set_up_stages
    And sorted stages list is empty
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1301:given_empty_stages_list
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1301:given_empty_stages_list
    When Agent calls Workflow to start
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1308:when_agent_calls_workflow_start
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1308:when_agent_calls_workflow_start
    And Workflow attempts to get first behavior from sorted stages
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1314:when_workflow_attempts_get_first
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1314:when_workflow_attempts_get_first
    Then Workflow handles empty stages list gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1320:then_workflow_handles_empty
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1320:then_workflow_handles_empty
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And appropriate error is returned to Agent
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1326:then_error_returned_to_agent
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1326:then_error_returned_to_agent
    And Agent presents error to user in chat
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1332:then_agent_presents_error
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1332:then_agent_presents_error
    And Agent does not present invalid workflow state to user
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1338:then_agent_no_invalid_state
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1338:then_agent_no_invalid_state

  Scenario: Workflow fails to initialize first action
    Given Project is finished initializing
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:921:when_project_finished_init
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:921:when_project_finished_init
    And Agent has loaded configurations
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1082:given_agent_loaded_configs
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1082:given_agent_loaded_configs
    And Workflow has set up stages
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1295:given_workflow_set_up_stages
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1295:given_workflow_set_up_stages
    And first behavior (shape) exists but has no actions
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1344:given_behavior_no_actions
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1344:given_behavior_no_actions
    When Agent calls Workflow to start
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1308:when_agent_calls_workflow_start
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1308:when_agent_calls_workflow_start
    And Workflow gets first behavior from sorted stages
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1351:when_workflow_gets_first_behavior
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1351:when_workflow_gets_first_behavior
    And Workflow attempts to initialize first action
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1357:when_workflow_attempts_init_action
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1357:when_workflow_attempts_init_action
    Then Workflow handles missing actions gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1363:then_workflow_handles_missing_actions
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1363:then_workflow_handles_missing_actions
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And appropriate error is returned to Agent
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1326:then_error_returned_to_agent
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1326:then_error_returned_to_agent
    And Agent presents error to user in chat
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1332:then_agent_presents_error
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1332:then_agent_presents_error
    And Agent does not present invalid workflow state to user
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1338:then_agent_no_invalid_state
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1338:then_agent_no_invalid_state

  Scenario: Project workflow attribute missing during synchronization
    Given Project is finished initializing
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:921:when_project_finished_init
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:921:when_project_finished_init
    And Agent has loaded configurations
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1082:given_agent_loaded_configs
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1082:given_agent_loaded_configs
    And Workflow has been initialized
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1369:given_workflow_initialized
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1369:given_workflow_initialized
    And Project does not have workflow attribute
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1375:given_project_no_workflow
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1375:given_project_no_workflow
    When AgentStateManager attempts to synchronize workflow
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1382:when_manager_attempts_sync
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1382:when_manager_attempts_sync
    And AgentStateManager verifies Project has workflow attribute
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1108:then_manager_verifies_project_workflow
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1108:then_manager_verifies_project_workflow
    Then AgentStateManager handles missing workflow attribute gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1392:then_manager_handles_missing_workflow
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1392:then_manager_handles_missing_workflow
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And AgentStateManager creates workflow attribute or returns appropriate error
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1398:then_manager_creates_or_returns_error
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1398:then_manager_creates_or_returns_error
