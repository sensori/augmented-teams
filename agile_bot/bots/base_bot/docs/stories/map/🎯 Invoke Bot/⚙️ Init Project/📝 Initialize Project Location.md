# 📝 Initialize Project Location

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Invoke Bot
**Feature:** Init Project
**User:** Bot Behavior
**Sequential Order:** 1
**Story Type:** user

## Story Description

Initialize Project Location functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

### Scenario: First time initialization with no saved location (happy_path)

**Steps:**
```gherkin
Given: No project location has been saved
When: Bot behavior is invoked
Then: Bot detects current directory and requests confirmation
```


### Scenario: Subsequent invocation with same location (no confirmation bias) (happy_path)

**Steps:**
```gherkin
Given: Project location is saved and current directory matches saved location
When: Bot behavior is invoked
Then: Bot does NOT ask user for confirmation and says 'Resuming in...'
```


### Scenario: Location changed - ask for confirmation (happy_path)

**Steps:**
```gherkin
Given: Project location is saved and current directory is DIFFERENT
When: Bot behavior is invoked
Then: Bot detects mismatch and asks if user wants to switch to current directory
```


### Scenario: Location file persistence when no confirmation needed (happy_path)

**Steps:**
```gherkin
Given: Saved location matches current location
When: Bot behavior is invoked
Then: Bot saves location to current_project.json file
```


### Scenario: User provides different location during initialization via parameters (happy_path)

**Steps:**
```gherkin
Given: No saved location exists
When: Bot behavior is invoked with project_area parameter
Then: Bot uses the provided project_area location
```


### Scenario: User changes project area via initialize_project action with parameters (happy_path)

**Steps:**
```gherkin
Given: Project location is already saved
When: User invokes initialize_project with different project_area parameter
Then: Bot detects change and asks if user wants to switch to current directory
```


### Scenario: First time with project_area parameter as hint (happy_path)

**Steps:**
```gherkin
Given: No saved location exists
When: Bot is invoked with project_area parameter
Then: Bot uses parameter as hint but still requests confirmation
AND: Location is NOT saved until user confirms
```


### Scenario: User confirms proposed location (happy_path)

**Steps:**
```gherkin
Given: Bot proposed a location requiring confirmation
When: User responds with confirm=True and same location
Then: Bot saves the confirmed location
```


### Scenario: User provides different location as response to confirmation (happy_path)

**Steps:**
```gherkin
Given: Bot proposed a location requiring confirmation
When: User responds with confirm=True and DIFFERENT location
Then: Bot saves the user's choice (not the proposed location)
```


### Scenario: Workflow state not created when confirmation required (happy_path)

**Steps:**
```gherkin
Given Bot proposes location requiring confirmation
When initialize_project is called and requires_confirmation is True
Then workflow_state.json is NOT created
And close_current_action cannot proceed without workflow state
```


### Scenario: Workflow state created after confirmation (happy_path)

**Steps:**
```gherkin
Given Bot proposed location requiring confirmation
When User confirms location with confirm=True
Then workflow_state.json IS created
And workflow_state.json contains current_behavior, current_action, and completed_actions
And close_current_action can proceed
```

