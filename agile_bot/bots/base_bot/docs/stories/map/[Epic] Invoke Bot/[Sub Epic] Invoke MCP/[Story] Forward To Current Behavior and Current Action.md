# [Story] Forward To Current Behavior and Current Action

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Invoke Bot  
**Sub Epic:** Invoke MCP
**User:** AI Chat  
**Sequential Order:** 3  
**Story Type:** user

## Story Description

Forward To Current Behavior and Current Action functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN Bot tool receives invocation**
- **AND workflow state shows current_behavior and current_action**
- **THEN Bot tool forwards to correct behavior and action**
- **WHEN workflow state does NOT exist**
- **THEN Bot tool defaults to first behavior and first action**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Bot tool forwards to current behavior and current action

**Steps:**
```gherkin
Given workflow state shows current_behavior='discovery', current_action='build_knowledge'
When Bot tool receives invocation
Then Bot tool forwards to correct behavior and action
```


### Scenario: Bot tool defaults to first behavior and first action when state missing

**Steps:**
```gherkin
Given workflow state does NOT exist
When Bot tool receives invocation
Then Bot tool defaults to first behavior and first action
```


