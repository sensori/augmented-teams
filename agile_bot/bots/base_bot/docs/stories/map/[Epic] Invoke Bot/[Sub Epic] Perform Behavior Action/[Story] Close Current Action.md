# [Story] Close Current Action

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Invoke Bot  
**Sub Epic:** Perform Behavior Action
**User:** Bot Behavior  
**Sequential Order:** 1  
**Story Type:** user

## Story Description

Close Current Action functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN user closes current action**
- **THEN action is saved to completed_actions**
- **AND workflow transitions to next action**
- **WHEN user closes final action**
- **THEN action is saved to completed_actions**
- **AND workflow stays at final action (no next action available)**
- **WHEN user attempts to close action that requires confirmation**
- **AND action is not in completed_actions**
- **THEN workflow does not allow closing without confirmation**
- **WHEN user closes action that's already marked complete**
- **THEN closing is idempotent (no error, action remains complete)**
- **WHEN CLI calls --close command**
- **THEN CLI routes to bot.close_current_action method**
- **AND Bot class has close_current_action method**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Close current action and transition to next

**Steps:**
```gherkin
Given workflow is at action "gather_context"
And action has NOT been marked complete yet
When user closes current action
Then action "gather_context" is saved to completed_actions
And workflow transitions to "decide_planning_criteria" (next action)
```


### Scenario: Close action when already at final action

**Steps:**
```gherkin
Given workflow is at action "validate_rules" (final action)
When user closes current action
Then action "validate_rules" is saved to completed_actions
And workflow stays at "validate_rules" (no next action available)
```


### Scenario: Close final action and transition to next behavior

**Steps:**
```gherkin
Given workflow is at final action "validate_rules" of behavior "shape"
When user closes current action
Then "validate_rules" is saved to completed_actions
And workflow stays at "validate_rules" (end of behavior)
```


### Scenario: Close action that requires confirmation but wasn't confirmed

**Steps:**
```gherkin
Given workflow is at "initialize_project"
And action has NOT been saved to completed_actions (requires confirmation)
Then is_action_completed returns False
```


### Scenario: Close action that's already marked complete (idempotent)

**Steps:**
```gherkin
Given action already complete
When close again (should be idempotent)
Then should still work fine
```


### Scenario: Bot class has close_current_action method (CLI routes to bot.close_current_action)

**Steps:**
```gherkin
Given bot is configured with behavior "shape"
When Bot instance is created
Then Bot class has close_current_action method
And When close_current_action is called
Then action "gather_context" is marked complete
And workflow transitions to next action "decide_planning_criteria"
```


