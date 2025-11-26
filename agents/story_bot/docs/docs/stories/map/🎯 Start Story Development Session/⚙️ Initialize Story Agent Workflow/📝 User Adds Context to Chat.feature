# Epic: Start Story Development Session
# Feature: Initialize Story Agent Workflow
# Story: User Adds Context to Chat
#
# Story Description:
#User adds documents, models, text descriptions, diagrams to Cursor/VS Code chat
# window and requests to start shaping/planning/building a new project

Feature: User Adds Context to Chat
  As a developer
  I want to test the story scenarios
  So that the requirements are verified

  Scenario: User attaches documents and requests story shaping
    Given Cursor/VS Code chat window is open
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1405:given_chat_window_open
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1405:given_chat_window_open
    And user has documents, models, text descriptions, or diagrams available
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1411:given_user_has_documents
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1411:given_user_has_documents
    When user selects and attaches documents to chat window
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1417:when_user_attaches_documents
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1417:when_user_attaches_documents
    And user types request message 'start shaping'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1535:when_user_types_without_docs (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1535:when_user_types_without_docs (partial match)
    Then system receives context and stores location/path and purpose of each context item to docs/provide_context.json
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1429:then_system_stores_context
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1429:then_system_stores_context
    And AI Chat receives and processes the request
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1436:then_ai_receives_request
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1436:then_ai_receives_request

  Scenario: User attaches multiple document types
    Given Cursor/VS Code chat window is open
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1405:given_chat_window_open
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1405:given_chat_window_open
    When user attaches markdown document
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1442:when_user_attaches_markdown
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1442:when_user_attaches_markdown
    And user attaches JSON model file
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1450:when_user_attaches_json
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1450:when_user_attaches_json
    And user types request message 'plan new project'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1535:when_user_types_without_docs (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1535:when_user_types_without_docs (partial match)
    Then system stores location/path and purpose of each attached file to docs/provide_context.json
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1464:then_system_stores_files
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1464:then_system_stores_files
    And AI Chat receives and processes the request with all context
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1471:then_ai_receives_with_context
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1471:then_ai_receives_with_context

  Scenario: User provides textual description as context
    Given Cursor/VS Code chat window is open
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1405:given_chat_window_open
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1405:given_chat_window_open
    When user types textual description as context in chat window
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1478:when_user_types_textual
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1478:when_user_types_textual
    And user types request message 'start shaping'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1535:when_user_types_without_docs (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1535:when_user_types_without_docs (partial match)
    Then system stores actual text content and purpose of textual description to docs/provide_context.json
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1484:then_system_stores_textual
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1484:then_system_stores_textual
    And AI Chat receives and processes the request with textual context
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1491:then_ai_receives_textual
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1491:then_ai_receives_textual

  Scenario: User attaches empty or invalid files
    Given Cursor/VS Code chat window is open
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1405:given_chat_window_open
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1405:given_chat_window_open
    When user attempts to attach empty file
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1498:when_user_attempts_empty_file
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1498:when_user_attempts_empty_file
    Or user attempts to attach corrupted file
    And user types request message 'build story map'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1535:when_user_types_without_docs (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1535:when_user_types_without_docs (partial match)
    Then system handles file attachment error gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1516:then_system_handles_attachment_error
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1516:then_system_handles_attachment_error
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And system stores only valid context items (location/path for files, actual content for textual descriptions, and purpose) to docs/provide_context.json
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1522:then_system_stores_valid_only
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1522:then_system_stores_valid_only
    And AI Chat receives request with available valid context only
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1529:then_ai_receives_valid_only
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1529:then_ai_receives_valid_only

  Scenario: User types request without attaching documents
    Given Cursor/VS Code chat window is open
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1405:given_chat_window_open
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1405:given_chat_window_open
    When user types request message 'start shaping' without attaching any documents
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1535:when_user_types_without_docs (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1535:when_user_types_without_docs (partial match)
    Then system creates docs/provide_context.json with empty context list
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1542:then_system_creates_empty_context
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1542:then_system_creates_empty_context
    And AI Chat receives and processes the request
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1436:then_ai_receives_request
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1436:then_ai_receives_request
    And system proceeds with story shaping workflow using empty context
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1549:then_system_proceeds_empty_context
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1549:then_system_proceeds_empty_context
