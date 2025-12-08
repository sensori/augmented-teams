# [Story] Forward To Current Action

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Invoke Bot  
**Sub Epic:** Invoke MCP
**User:** AI Chat  
**Sequential Order:** 4  
**Story Type:** user

## Story Description

Forward To Current Action functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN Behavior tool receives invocation**
- **AND workflow state shows current_action within behavior**
- **THEN Behavior tool forwards to current action**
- **WHEN workflow state shows different behavior**
- **THEN Behavior tool updates workflow to current behavior**
- **WHEN workflow state does NOT exist**
- **THEN Behavior tool defaults to first action**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Behavior tool forwards to current action within behavior

**Steps:**
```gherkin
Given a behavior tool for 'discovery' behavior
And workflow state shows current_action='build_knowledge'
When Behavior tool receives invocation
Then Behavior tool forwards to build_knowledge action
```


### Scenario: Behavior tool sets workflow to current behavior when state shows different behavior

**Steps:**
```gherkin
Given a behavior tool for 'exploration' behavior
And workflow state shows current_behavior='discovery'
When Behavior tool receives invocation
Then workflow state updated to current_behavior='exploration'
```


### Scenario: Behavior tool defaults to first action when state missing

**Steps:**
```gherkin
Given a behavior tool for 'shape' behavior
And workflow state does NOT exist
When Behavior tool receives invocation
Then Behavior tool defaults to first action
```


### Scenario: Action called directly saves workflow state

**Steps:**
```gherkin
Given Bot is initialized with current_project set
And No workflow state exists yet
When Action is called directly (e.g., bot.shape.gather_context())
Then workflow_state.json is created with current_behavior and current_action
```


