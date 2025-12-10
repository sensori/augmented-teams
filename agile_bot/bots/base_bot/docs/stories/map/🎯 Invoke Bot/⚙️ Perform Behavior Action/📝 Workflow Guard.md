# 📝 Workflow Guard

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Invoke Bot
**Feature:** Perform Behavior Action
**User:** Bot Behavior
**Sequential Order:** 5
**Story Type:** user

## Story Description

Workflow Guard functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** : Workflow.save_state() is called

  **then** : workflow_state.json is NOT created

- **When** : Workflow.save_state() is called

  **then** : workflow_state.json IS created

## Scenarios

### Scenario: Workflow state not saved when current_project missing (happy_path)

**Steps:**
```gherkin
GIVEN: current_project.json does NOT exist
WHEN: Workflow.save_state() is called
THEN: workflow_state.json is NOT created
```


### Scenario: Workflow state saved when current_project exists (happy_path)

**Steps:**
```gherkin
GIVEN: current_project.json exists
WHEN: Workflow.save_state() is called
THEN: workflow_state.json IS created
```

