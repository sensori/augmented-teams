# Epic: Start Story Development Session
# Feature: Initialize Story Agent Workflow
# Story: AI Chat Invokes Story Agent MCP
#
# Story Description:
#AI Chat detects story shaping request and calls Story Agent MCP Server via
# agent_get_state or agent_get_instructions tool

Feature: AI Chat Invokes Story Agent MCP
  As a developer
  I want to test the story scenarios
  So that the requirements are verified

  Background:
    Given user has attached documents to chat window
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:690:given_user_attached_documents
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:690:given_user_attached_documents
    And user has typed request message with story shaping keywords
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:696:given_user_typed_keywords
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:696:given_user_typed_keywords

  Scenario: AI Chat detects story shaping keywords and invokes MCP
    When AI Chat processes user message and attached documents
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:703:when_ai_chat_processes
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:703:when_ai_chat_processes
    Then AI Chat identifies story shaping keywords
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:709:then_ai_identifies_keywords
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:709:then_ai_identifies_keywords
    And AI Chat determines Story Agent is needed
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:721:when_ai_determines_agent_needed
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:721:when_ai_determines_agent_needed
    When AI Chat determines Story Agent is needed
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:721:when_ai_determines_agent_needed
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:721:when_ai_determines_agent_needed
    Then AI Chat selects appropriate MCP tool
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:727:then_ai_selects_tool
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:727:then_ai_selects_tool
    And AI Chat prepares tool call with agent_name='story_bot'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:733:then_ai_prepares_tool_call (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:733:then_ai_prepares_tool_call (partial match)
    When AI Chat invokes Story Agent MCP Server via selected tool
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:739:when_ai_invokes_mcp
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:739:when_ai_invokes_mcp
    Then MCP Server receives tool call with agent_name parameter
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:745:then_mcp_receives_tool_call
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:745:then_mcp_receives_tool_call

  Scenario: AI Chat selects agent_get_state tool
    Given user has attached documents to chat window
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:690:given_user_attached_documents
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:690:given_user_attached_documents
    And user has typed request message 'start shaping'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:851:given_user_typed_build_map (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:851:given_user_typed_build_map (partial match)
    When AI Chat processes request
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:758:when_ai_processes_request
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:758:when_ai_processes_request
    And AI Chat determines Story Agent is needed
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:721:when_ai_determines_agent_needed
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:721:when_ai_determines_agent_needed
    And AI Chat needs to check current agent state
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:764:then_ai_needs_check_state
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:764:then_ai_needs_check_state
    Then AI Chat selects agent_get_state tool
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:770:then_ai_selects_get_state
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:770:then_ai_selects_get_state
    And AI Chat prepares tool call with agent_name='story_bot'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:733:then_ai_prepares_tool_call (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:733:then_ai_prepares_tool_call (partial match)
    When AI Chat invokes agent_get_state
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:776:when_ai_invokes_get_state
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:776:when_ai_invokes_get_state
    Then MCP Server receives agent_get_state tool call
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:783:then_mcp_receives_get_state
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:783:then_mcp_receives_get_state

  Scenario: AI Chat selects agent_get_instructions tool
    Given user has attached documents to chat window
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:690:given_user_attached_documents
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:690:given_user_attached_documents
    And user has typed request message 'plan new project'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:851:given_user_typed_build_map (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:851:given_user_typed_build_map (partial match)
    When AI Chat processes request
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:758:when_ai_processes_request
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:758:when_ai_processes_request
    And AI Chat determines Story Agent is needed
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:721:when_ai_determines_agent_needed
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:721:when_ai_determines_agent_needed
    And AI Chat needs to get workflow instructions
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:795:then_ai_needs_instructions
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:795:then_ai_needs_instructions
    Then AI Chat selects agent_get_instructions tool
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:801:then_ai_selects_get_instructions
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:801:then_ai_selects_get_instructions
    And AI Chat prepares tool call with agent_name='story_bot'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:733:then_ai_prepares_tool_call (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:733:then_ai_prepares_tool_call (partial match)
    When AI Chat invokes agent_get_instructions
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:807:when_ai_invokes_get_instructions
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:807:when_ai_invokes_get_instructions
    Then MCP Server receives agent_get_instructions tool call
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:814:then_mcp_receives_get_instructions
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:814:then_mcp_receives_get_instructions

  Scenario: AI Chat handles ambiguous request without keywords
    Given user has attached documents to chat window
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:690:given_user_attached_documents
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:690:given_user_attached_documents
    And user has typed request message without clear story shaping keywords
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:820:given_user_typed_ambiguous
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:820:given_user_typed_ambiguous
    When AI Chat processes user message
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:826:when_ai_processes_user_message
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:826:when_ai_processes_user_message
    Then AI Chat does not identify story shaping keywords
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:832:then_ai_no_keywords
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:832:then_ai_no_keywords
    And AI Chat does not determine Story Agent is needed
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:839:then_ai_no_agent_needed
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:839:then_ai_no_agent_needed
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And AI Chat handles request through default flow
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:845:then_ai_handles_default
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:845:then_ai_handles_default

  Scenario: AI Chat handles MCP Server unavailable
    Given user has attached documents to chat window
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:690:given_user_attached_documents
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:690:given_user_attached_documents
    And user has typed request message 'build story map'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:851:given_user_typed_build_map (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:851:given_user_typed_build_map (partial match)
    And MCP Server is not available or not responding
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:857:given_mcp_unavailable
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:857:given_mcp_unavailable
    When AI Chat determines Story Agent is needed
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:721:when_ai_determines_agent_needed
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:721:when_ai_determines_agent_needed
    And AI Chat attempts to invoke MCP Server
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:863:when_ai_attempts_invoke
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:863:when_ai_attempts_invoke
    Then system handles MCP Server unavailability gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:878:then_system_handles_unavailable
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:878:then_system_handles_unavailable
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And user receives appropriate error message
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:884:then_user_receives_error
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:884:then_user_receives_error
