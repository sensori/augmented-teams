# 📝 Guards Prevent Writes Without Project

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Invoke Bot
**Feature:** Init Project
**User:** Bot Behavior
**Sequential Order:** 4
**Story Type:** user

## Story Description

Guards Prevent Writes Without Project functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Activity tracker attempts to log activity

  **and** current_project.json does NOT exist

  **then** Activity tracker does NOT write to activity log

  **and** Activity tracking fails gracefully without error

- **When** Workflow attempts to save state

  **and** current_project.json does NOT exist

  **then** Workflow does NOT save workflow_state.json

  **and** Workflow state save fails gracefully without error

## Scenarios

### Scenario: Activity not tracked when current_project missing (happy_path)

**Steps:**
```gherkin
Given current_project.json does NOT exist
When Action attempts to track activity
Then Activity tracker detects missing current_project
And Activity tracker does NOT write to activity log
And Action continues execution (non-blocking)
```


### Scenario: Activity tracked when current_project exists (happy_path)

**Steps:**
```gherkin
Given current_project.json exists with valid project_area
When Action attempts to track activity
Then Activity tracker writes to project_area/activity_log.json
And Activity entry is successfully logged
```


### Scenario: Initialize project action not tracked without current_project (happy_path)

**Steps:**
```gherkin
Given current_project.json does NOT exist
When initialize_project action executes
Then Activity tracker does NOT log initialize_project activity
And initialize_project can still execute (it creates current_project)
```


### Scenario: Workflow state not saved when current_project missing (happy_path)

**Steps:**
```gherkin
Given current_project.json does NOT exist
When Action attempts to save workflow state
Then Workflow guard detects missing current_project
And Workflow does NOT write workflow_state.json
And Action continues execution (non-blocking)
```


### Scenario: Workflow state saved when current_project exists (happy_path)

**Steps:**
```gherkin
Given current_project.json exists
When Action attempts to save workflow state
Then Workflow writes to project_area/workflow_state.json
And Workflow state is successfully persisted
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


### Scenario: Completed actions not saved when current_project missing (happy_path)

**Steps:**
```gherkin
Given current_project.json does NOT exist
When Action attempts to save completed_actions
Then Workflow guard prevents write
And completed_actions are NOT persisted
And Action continues execution
```

