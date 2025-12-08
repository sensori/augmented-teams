# [Story] Initialize Project Location

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Invoke Bot  
**Sub Epic:** Init Project
**User:** Bot Behavior  
**Sequential Order:** 1  
**Story Type:** user

## Story Description

Initialize Project Location functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN Bot behavior is invoked for the first time (no saved location exists)**
- **THEN Bot detects current directory from context**
- **AND Bot presents location to user for confirmation**
- **AND Bot waits for user to confirm or provide different location**
- **AND Bot saves confirmed location to persistent storage**
- **WHEN Bot behavior is invoked**
- **AND Saved location exists**
- **AND Current directory matches saved location**
- **THEN Bot uses saved location without asking for confirmation**
- **AND Bot proceeds directly to next action**
- **WHEN Bot behavior is invoked**
- **AND Saved location exists**
- **AND Current directory is DIFFERENT from saved location**
- **THEN Bot presents new location to user for confirmation**
- **AND Bot asks if user wants to switch to new location**
- **AND Bot saves confirmed location if user approves change**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: First time initialization with no saved location

**Steps:**
```gherkin
Given: No project location has been saved
When: Bot behavior is invoked
Then: Bot detects current directory and requests confirmation
```


### Scenario: Subsequent invocation with same location (no confirmation bias)

**Steps:**
```gherkin
Given: Project location is saved and current directory matches saved location
When: Bot behavior is invoked
Then: Bot does NOT ask user for confirmation and says 'Resuming in...'
```


### Scenario: Location changed - ask for confirmation

**Steps:**
```gherkin
Given: Project location is saved and current directory is DIFFERENT
When: Bot behavior is invoked
Then: Bot detects mismatch and asks if user wants to switch to current directory
```


### Scenario: Location file persistence when no confirmation needed

**Steps:**
```gherkin
Given: Saved location matches current location
When: Bot behavior is invoked
Then: Bot saves location to current_project.json file
```


### Scenario: User provides different location during initialization via parameters

**Steps:**
```gherkin
Given: No saved location exists
When: Bot behavior is invoked with project_area parameter
Then: Bot uses the provided project_area location
```


### Scenario: User changes project area via initialize_project action with parameters

**Steps:**
```gherkin
Given: Project location is already saved
When: User invokes initialize_project with different project_area parameter
Then: Bot detects change and asks if user wants to switch to current directory
```


### Scenario: First time with project_area parameter as hint

**Steps:**
```gherkin
Given: No saved location exists
When: Bot is invoked with project_area parameter
Then: Bot uses parameter as hint but still requests confirmation
AND: Location is NOT saved until user confirms
```


### Scenario: User confirms proposed location

**Steps:**
```gherkin
Given: Bot proposed a location requiring confirmation
When: User responds with confirm=True and same location
Then: Bot saves the confirmed location
```


### Scenario: User provides different location as response to confirmation

**Steps:**
```gherkin
Given: Bot proposed a location requiring confirmation
When: User responds with confirm=True and DIFFERENT location
Then: Bot saves the user's choice (not the proposed location)
```


### Scenario: Workflow state not created when confirmation required

**Steps:**
```gherkin
Given Bot proposes location requiring confirmation
When initialize_project is called and requires_confirmation is True
Then workflow_state.json is NOT created
And close_current_action cannot proceed without workflow state
```


### Scenario: Workflow state created after confirmation

**Steps:**
```gherkin
Given Bot proposed location requiring confirmation
When User confirms location with confirm=True
Then workflow_state.json IS created
And workflow_state.json contains current_behavior, current_action, and completed_actions
And close_current_action can proceed
```


