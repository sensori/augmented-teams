# 📝 Initialize Project Location

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Init Project

**User:** Bot Behavior  
**Sequential Order:** 1  
**Story Type:** system

**Test File:** test_init_project.py  
**Test Class:** TestInitializeProjectLocation

## Story Description

Bot behavior initializes project location by detecting the current directory from context, presenting it to the user for confirmation, and saving the confirmed location to persistent storage. If a saved location exists and matches the current directory, the bot uses it without asking for confirmation.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** Bot behavior is invoked for the first time (no saved location exists)
- **THEN** Bot detects current directory from context
- **AND** Bot presents location to user for confirmation
- **AND** Bot waits for user to confirm or provide different location
- **AND** Bot saves confirmed location to persistent storage
- **WHEN** Bot behavior is invoked
- **AND** Saved location exists
- **AND** Current directory matches saved location
- **THEN** Bot uses saved location without asking for confirmation
- **AND** Bot proceeds directly to next action
- **WHEN** Bot behavior is invoked
- **AND** Saved location exists
- **AND** Current directory is DIFFERENT from saved location
- **THEN** Bot presents new location to user for confirmation
- **AND** Bot asks if user wants to switch to new location
- **AND** Bot saves confirmed location if user approves change

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given bot behavior is invoked
```

## Scenarios

### Scenario: Initialize project location for first time

**Test Method:** `test_first_time_initialization_detects_and_requests_confirmation`

**Steps:**
```gherkin
Given bot behavior is invoked for the first time
And no saved location exists
When bot initializes project location
Then bot detects current directory from context
And bot presents location to user for confirmation
And bot waits for user to confirm or provide different location
And bot saves confirmed location to persistent storage
```

### Scenario: Use existing saved location when it matches

**Test Method:** `test_subsequent_invocation_same_location_skips_confirmation`

**Steps:**
```gherkin
Given bot behavior is invoked
And saved location exists
And current directory matches saved location
When bot initializes project location
Then bot uses saved location without asking for confirmation
And bot proceeds directly to next action
```

### Scenario: Prompt user when current directory differs from saved location

**Test Method:** `test_location_changed_requests_confirmation`

**Steps:**
```gherkin
Given bot behavior is invoked
And saved location exists
And current directory is DIFFERENT from saved location
When bot initializes project location
Then bot presents new location to user for confirmation
And bot asks if user wants to switch to new location
And bot saves confirmed location if user approves change
```

### Scenario: Location file saved when no confirmation needed

**Test Method:** `test_location_file_saved_when_no_confirmation_needed`

**Steps:**
```gherkin
Given saved location matches current location
When bot behavior is invoked
Then bot saves location to current_project.json file
```

### Scenario: User provides custom project area via parameters

**Test Method:** `test_user_provides_custom_project_area_via_parameters`

**Steps:**
```gherkin
Given no saved location exists
When bot behavior is invoked with project_area parameter
Then bot uses the provided project_area location
```

### Scenario: User changes project area with initialize_project action

**Test Method:** `test_user_changes_project_area_with_initialize_project_action`

**Steps:**
```gherkin
Given project location is already saved
When user invokes initialize_project with different project_area parameter
Then bot detects change and asks if user wants to switch to current directory
```

### Scenario: Project area parameter as hint still requests confirmation

**Test Method:** `test_project_area_parameter_as_hint_still_requests_confirmation`

**Steps:**
```gherkin
Given no saved location exists
When bot is invoked with project_area parameter
Then bot uses parameter as hint but still requests confirmation
And location is NOT saved until user confirms
```

### Scenario: User confirms proposed location

**Test Method:** `test_user_confirms_proposed_location`

**Steps:**
```gherkin
Given bot proposed a location requiring confirmation
When user responds with confirm=True and same location
Then bot saves the confirmed location
```

### Scenario: User provides different location as confirmation response

**Test Method:** `test_user_provides_different_location_as_confirmation_response`

**Steps:**
```gherkin
Given bot proposed a location requiring confirmation
When user responds with confirm=True and DIFFERENT location
Then bot saves the user's choice (not the proposed location)
```

### Scenario: Workflow state not created when confirmation required

**Test Method:** `test_workflow_state_not_created_when_confirmation_required`

**Steps:**
```gherkin
Given bot proposes location requiring confirmation
When initialize_project is called and requires_confirmation is True
Then workflow_state.json is NOT created
And close_current_action cannot proceed without workflow state
```

### Scenario: Workflow state created after confirmation

**Test Method:** `test_workflow_state_created_after_confirmation`

**Steps:**
```gherkin
Given bot proposed location requiring confirmation
When user confirms location with confirm=True
Then workflow_state.json IS created
And workflow_state.json contains current_behavior, current_action, and completed_actions
And close_current_action can proceed
```

