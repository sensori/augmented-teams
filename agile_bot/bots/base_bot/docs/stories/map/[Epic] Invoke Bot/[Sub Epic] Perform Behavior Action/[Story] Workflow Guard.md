# [Story] Workflow Guard

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Invoke Bot  
**Sub Epic:** Perform Behavior Action
**User:** Bot Behavior  
**Sequential Order:** 5  
**Story Type:** user

## Story Description

Workflow Guard functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** GIVEN: current_project.json does NOT exist
- **WHEN: Workflow.save_state() is called**
- **THEN: workflow_state.json is NOT created**
- **WHEN** GIVEN: current_project.json exists
- **WHEN: Workflow.save_state() is called**
- **THEN: workflow_state.json IS created**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Workflow state not saved when current_project missing

**Steps:**
```gherkin
GIVEN: current_project.json does NOT exist
WHEN: Workflow.save_state() is called
THEN: workflow_state.json is NOT created
```


### Scenario: Workflow state saved when current_project exists

**Steps:**
```gherkin
GIVEN: current_project.json exists
WHEN: Workflow.save_state() is called
THEN: workflow_state.json IS created
```


