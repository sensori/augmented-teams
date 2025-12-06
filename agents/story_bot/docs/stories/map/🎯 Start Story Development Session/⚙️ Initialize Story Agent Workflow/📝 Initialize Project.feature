# Epic: Start Story Development Session
# Feature: Initialize Story Agent Workflow
# Story: Initialize Project
#
# Story Description:
#Agent creates Project instance and delegates project area determination to
# Project. Project determines project_area for new project, presents to user for
# confirmation, saves to agent_state.json, and completes initialization

Feature: Initialize Project
  As a developer
  I want to test the story scenarios
  So that the requirements are verified

  Background:
    Given Agent is initialized with agent_name='story_bot'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:404:given_agent_initialized (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:404:given_agent_initialized (partial match)
    And current working directory has a folder name
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:414:given_cwd_has_folder_name
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:414:given_cwd_has_folder_name
    And no agent_state.json files exist in current directory or subdirectories
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:421:given_no_state_files
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:421:given_no_state_files

  Scenario: Project initializes with default project area
    When Agent creates Project for new project
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:430:when_agent_creates_project
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:430:when_agent_creates_project
    Then Agent instantiates Project with agent_name='story_bot'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:438:then_agent_instantiates_project (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:438:then_agent_instantiates_project (partial match)
    And Agent delegates project area determination to Project
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:445:then_agent_delegates_to_project
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:445:then_agent_delegates_to_project
    When Project initializes for new project
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:452:when_project_initializes
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:452:when_project_initializes
    Then Project determines project_area defaults to current folder name
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:458:then_project_determines_default
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:458:then_project_determines_default
    And Project presents determined project_area to user for confirmation
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:464:then_project_presents_to_user
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:464:then_project_presents_to_user
    When user confirms project area
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:470:when_user_confirms_project_area
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:470:when_user_confirms_project_area
    Then Project saves project_area to agent_state.json in project area
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:476:then_project_saves_to_state
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:476:then_project_saves_to_state
    And Project creates necessary directory structure
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:485:then_project_creates_directories
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:485:then_project_creates_directories
    And Project completes initialization
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:493:then_project_completes_init
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:493:then_project_completes_init

  Scenario: User suggests different project area
    Given Agent is initialized with agent_name='story_bot'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:404:given_agent_initialized (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:404:given_agent_initialized (partial match)
    And current working directory has a folder name
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:414:given_cwd_has_folder_name
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:414:given_cwd_has_folder_name
    And no agent_state.json files exist
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:500:given_no_state_files_short
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:500:given_no_state_files_short
    And Project has determined project_area as current folder name
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:506:given_project_determined_area
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:506:given_project_determined_area
    And Project has presented project_area to user
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:512:given_project_presented_area
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:512:given_project_presented_area
    When user suggests different project area
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:518:when_user_suggests_different
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:518:when_user_suggests_different
    Then Project updates project_area to user-suggested value
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:524:then_project_updates_area
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:524:then_project_updates_area
    And Project saves project_area to agent_state.json
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:531:then_project_saves_state
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:531:then_project_saves_state
    And Project creates necessary directory structure in new project area
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:537:then_project_creates_new_directories
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:537:then_project_creates_new_directories
    And Project completes initialization
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:493:then_project_completes_init
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:493:then_project_completes_init

  Scenario: Project area determination with invalid folder name
    Given Agent is initialized with agent_name='story_bot'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:404:given_agent_initialized (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:404:given_agent_initialized (partial match)
    And current working directory has invalid characters or is empty
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:543:given_invalid_cwd
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:543:given_invalid_cwd
    And no agent_state.json files exist
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:500:given_no_state_files_short
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:500:given_no_state_files_short
    When Project initializes for new project
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:452:when_project_initializes
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:452:when_project_initializes
    And Project attempts to determine project_area from current folder name
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:549:when_project_attempts_determine
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:549:when_project_attempts_determine
    Then Project handles invalid folder name gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:555:then_project_handles_invalid
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:555:then_project_handles_invalid
    And Project does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:561:then_project_no_crash
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:561:then_project_no_crash
    And Project presents error to user or uses safe default
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:567:then_project_presents_error_or_default
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:567:then_project_presents_error_or_default
    And user can provide valid project area
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:573:then_user_can_provide_valid
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:573:then_user_can_provide_valid

  Scenario: Project fails to save agent_state.json due to permissions
    Given Agent is initialized with agent_name='story_bot'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:404:given_agent_initialized (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:404:given_agent_initialized (partial match)
    And Project has determined project_area
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:579:given_project_determined
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:579:given_project_determined
    And user has confirmed project area
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:585:given_user_confirmed
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:585:given_user_confirmed
    And project area directory has read-only permissions
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:591:given_readonly_permissions
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:591:given_readonly_permissions
    When Project attempts to save project_area to agent_state.json
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:598:when_project_attempts_save
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:598:when_project_attempts_save
    Then Project handles file write permission error gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:610:then_project_handles_permission_error
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:610:then_project_handles_permission_error
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And appropriate error is presented to user in chat
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1186:then_error_presented_to_user_chat
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1186:then_error_presented_to_user_chat
    And Project does not complete initialization until file can be written
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:622:then_project_wait_for_write
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:622:then_project_wait_for_write

  Scenario: Project fails to create directory structure
    Given Agent is initialized with agent_name='story_bot'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:404:given_agent_initialized (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:404:given_agent_initialized (partial match)
    And Project has determined project_area
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:579:given_project_determined
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:579:given_project_determined
    And user has confirmed project area
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:585:given_user_confirmed
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:585:given_user_confirmed
    And project area path is on read-only filesystem
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:628:given_readonly_filesystem
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:628:given_readonly_filesystem
    When Project attempts to create necessary directory structure
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:634:when_project_attempts_create_dirs
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:634:when_project_attempts_create_dirs
    Then Project handles directory creation error gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:644:then_project_handles_dir_error
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:644:then_project_handles_dir_error
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And appropriate error is presented to user in chat
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:1186:then_error_presented_to_user_chat
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:1186:then_error_presented_to_user_chat
    And Project does not complete initialization until directories can be created
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:650:then_project_wait_for_dirs
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:650:then_project_wait_for_dirs

  Scenario: Project area already exists with conflicting state
    Given Agent is initialized with agent_name='story_bot'
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:404:given_agent_initialized (partial match)
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:404:given_agent_initialized (partial match)
    And Project has determined project_area
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:579:given_project_determined
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:579:given_project_determined
    And project area directory already exists
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:656:given_project_area_exists
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:656:given_project_area_exists
    And project area contains agent_state.json with different agent_name
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:662:given_conflicting_state
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:662:given_conflicting_state
    When Project attempts to save project_area to agent_state.json
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:598:when_project_attempts_save
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:598:when_project_attempts_save
    Then Project detects conflicting state file
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:671:then_project_detects_conflict
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:671:then_project_detects_conflict
    And Project handles conflict gracefully
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:677:then_project_handles_conflict
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:677:then_project_handles_conflict
    And system does not crash
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:301:then_system_no_crash_generic
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:301:then_system_no_crash_generic
    And Project presents conflict to user for resolution
      # 🔗 → augmented-teams\agents\story_bot\src\stories_acceptance_tests.py:683:then_project_presents_conflict
      # 🔗 → ../../../../../../src/stories_acceptance_tests.py:683:then_project_presents_conflict
