# Epic: Start Story Development Session
# Feature: Initialize Story Agent Workflow
# Story: Initialize Agent
#
# Story Description:
#MCP Server receives tool call from AI Chat and requests Agent instance from
# AgentStateManager, which creates and initializes Agent with
# agent_name='story_bot', sets up configuration file paths

Feature: Initialize Agent
  As a developer
  I want to test the story scenarios
  So that the requirements are verified

  Background:
    Given MCP Server is initialized and running
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:145:given_mcp_server_initialized
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:145:given_mcp_server_initialized
    And MCP Server has received tool call from AI Chat with agent_name='story_bot'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:152:given_mcp_received_tool_call (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:152:given_mcp_received_tool_call (partial match)
    And AgentStateManager cache is empty
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:159:given_empty_cache
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:159:given_empty_cache

  Scenario: MCP Server requests new Agent instance
    When MCP Server requests Agent instance from AgentStateManager
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:167:when_mcp_requests_agent
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:167:when_mcp_requests_agent
    Then AgentStateManager checks if Agent instance exists in cache
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:173:then_manager_checks_cache
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:173:then_manager_checks_cache
    And AgentStateManager finds no cached instance
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:180:then_no_cached_instance
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:180:then_no_cached_instance
    When AgentStateManager creates new Agent instance
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:186:when_manager_creates_agent
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:186:when_manager_creates_agent
    Then AgentStateManager instantiates Agent with agent_name='story_bot'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:192:then_manager_instantiates_agent (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:192:then_manager_instantiates_agent (partial match)
    And AgentStateManager handles any initialization errors
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:199:then_manager_handles_errors
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:199:then_manager_handles_errors
    And AgentStateManager stores instance in cache
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:205:then_manager_stores_in_cache
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:205:then_manager_stores_in_cache
    And AgentStateManager returns the Agent instance
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:212:then_manager_returns_agent
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:212:then_manager_returns_agent
    When Agent initializes
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:218:when_agent_initializes
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:218:when_agent_initializes
    Then Agent sets up base agent configuration path at agents/base/agent.json
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:224:then_agent_sets_base_config_path
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:224:then_agent_sets_base_config_path
    And Agent sets up agent directory at workspace_root/agents
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:231:then_agent_sets_agent_directory
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:231:then_agent_sets_agent_directory
    And Agent sets up agent-specific configuration at agents/story_bot/agent.json
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:238:then_agent_sets_agent_config_path
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:238:then_agent_sets_agent_config_path

  Scenario: AgentStateManager reuses cached Agent instance
    Given MCP Server is initialized and running
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:145:given_mcp_server_initialized
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:145:given_mcp_server_initialized
    And AgentStateManager has cached Agent instance with agent_name='story_bot'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:245:given_cached_agent_instance (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:245:given_cached_agent_instance (partial match)
    And MCP Server has received tool call from AI Chat with agent_name='story_bot'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:152:given_mcp_received_tool_call (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:152:given_mcp_received_tool_call (partial match)
    When MCP Server requests Agent instance from AgentStateManager
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:167:when_mcp_requests_agent
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:167:when_mcp_requests_agent
    Then AgentStateManager checks if Agent instance exists in cache
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:173:then_manager_checks_cache
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:173:then_manager_checks_cache
    And AgentStateManager finds cached instance
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:252:then_manager_finds_cached
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:252:then_manager_finds_cached
    Then AgentStateManager returns cached Agent instance
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:258:then_manager_returns_cached
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:258:then_manager_returns_cached
    And AgentStateManager does not create new instance
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:264:then_manager_no_new_instance
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:264:then_manager_no_new_instance
    And system does not crash from duplicate initialization
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:270:then_system_no_crash
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:270:then_system_no_crash

  Scenario: Agent initialization fails due to missing base config
    Given MCP Server is initialized and running
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:145:given_mcp_server_initialized
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:145:given_mcp_server_initialized
    And agents/base/agent.json file does not exist
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:276:given_base_config_missing
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:276:given_base_config_missing
    And AgentStateManager cache is empty
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:159:given_empty_cache
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:159:given_empty_cache
    When MCP Server requests Agent instance from AgentStateManager
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:167:when_mcp_requests_agent
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:167:when_mcp_requests_agent
    And AgentStateManager attempts to create new Agent instance
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:284:when_manager_attempts_create
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:284:when_manager_attempts_create
    Then AgentStateManager handles initialization error gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:295:then_manager_handles_init_error
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:295:then_manager_handles_init_error
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And appropriate error is returned to MCP Server
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:307:then_error_returned_to_mcp
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:307:then_error_returned_to_mcp
    And error is presented to user in chat
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:313:then_error_presented_to_user
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:313:then_error_presented_to_user
    And error is presented to user in chat
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:313:then_error_presented_to_user
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:313:then_error_presented_to_user
    And AgentStateManager does not store invalid instance in cache
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:319:then_manager_no_invalid_cache
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:319:then_manager_no_invalid_cache

  Scenario: Agent initialization fails due to missing agent-specific config
    Given MCP Server is initialized and running
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:145:given_mcp_server_initialized
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:145:given_mcp_server_initialized
    And agents/base/agent.json exists
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:326:given_base_config_exists
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:326:given_base_config_exists
    And agents/story_bot/agent.json file does not exist
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:332:given_agent_config_missing
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:332:given_agent_config_missing
    And AgentStateManager cache is empty
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:159:given_empty_cache
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:159:given_empty_cache
    When MCP Server requests Agent instance from AgentStateManager
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:167:when_mcp_requests_agent
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:167:when_mcp_requests_agent
    And AgentStateManager attempts to create new Agent instance
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:284:when_manager_attempts_create
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:284:when_manager_attempts_create
    Then Agent sets up base agent configuration path successfully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:340:then_agent_sets_base_config_success
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:340:then_agent_sets_base_config_success
    And Agent attempts to set up agent-specific configuration path
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:347:then_agent_attempts_agent_config
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:347:then_agent_attempts_agent_config
    Then AgentStateManager handles missing agent config error gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:353:then_manager_handles_missing_config
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:353:then_manager_handles_missing_config
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And appropriate error is returned to MCP Server
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:307:then_error_returned_to_mcp
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:307:then_error_returned_to_mcp
    And error is presented to user in chat
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:313:then_error_presented_to_user
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:313:then_error_presented_to_user

  Scenario: Agent initialization with invalid agent_name
    Given MCP Server is initialized and running
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:145:given_mcp_server_initialized
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:145:given_mcp_server_initialized
    And MCP Server has received tool call with invalid agent_name
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:359:given_invalid_agent_name_tool_call
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:359:given_invalid_agent_name_tool_call
    And AgentStateManager cache is empty
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:159:given_empty_cache
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:159:given_empty_cache
    When MCP Server requests Agent instance with invalid agent_name
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:365:when_mcp_requests_invalid_agent
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:365:when_mcp_requests_invalid_agent
    And AgentStateManager attempts to create new Agent instance
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:284:when_manager_attempts_create
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:284:when_manager_attempts_create
    Then AgentStateManager handles invalid agent_name error gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:377:then_manager_handles_invalid_name
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:377:then_manager_handles_invalid_name
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And appropriate error is returned to MCP Server
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:307:then_error_returned_to_mcp
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:307:then_error_returned_to_mcp
    And error is presented to user in chat
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:313:then_error_presented_to_user
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:313:then_error_presented_to_user

  Scenario: Agent initialization with corrupted config file
    Given MCP Server is initialized and running
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:145:given_mcp_server_initialized
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:145:given_mcp_server_initialized
    And agents/base/agent.json exists but is corrupted or invalid JSON
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:383:given_corrupted_base_config
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:383:given_corrupted_base_config
    And AgentStateManager cache is empty
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:159:given_empty_cache
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:159:given_empty_cache
    When MCP Server requests Agent instance from AgentStateManager
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:167:when_mcp_requests_agent
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:167:when_mcp_requests_agent
    And AgentStateManager attempts to create new Agent instance
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:284:when_manager_attempts_create
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:284:when_manager_attempts_create
    And Agent attempts to load base configuration
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1165:when_agent_attempts_load_base_config
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1165:when_agent_attempts_load_base_config
    Then Agent handles JSON parsing error gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:397:then_agent_handles_json_error
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:397:then_agent_handles_json_error
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And appropriate error is returned to MCP Server
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:307:then_error_returned_to_mcp
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:307:then_error_returned_to_mcp
    And error is presented to user in chat
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:313:then_error_presented_to_user
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:313:then_error_presented_to_user
