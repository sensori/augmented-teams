# 📝 Close Current Action

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Perform Behavior Action

**User:** Human  
**Sequential Order:** 2  
**Story Type:** user  
**Test File:** test_close_current_action.py

## Story Description

Users can explicitly mark an action as complete and transition to the next action. This allows users to control workflow progression and explicitly close actions when they're satisfied with the results.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** user closes current action
- **THEN** action is saved to completed_actions
- **AND** workflow transitions to next action
- **WHEN** user closes final action
- **THEN** action is saved to completed_actions
- **AND** workflow stays at final action (no next action available)
- **WHEN** user attempts to close action that requires confirmation
- **AND** action is not in completed_actions
- **THEN** workflow does not allow closing without confirmation
- **WHEN** user closes action that's already marked complete
- **THEN** closing is idempotent (no error, action remains complete)
- **WHEN** CLI calls --close command
- **THEN** CLI routes to bot.close_current_action method
- **AND** Bot class has close_current_action method

## Scenarios

### Scenario: Close current action and transition to next

**Test Method:** `test_close_current_action_marks_complete_and_transitions`

```gherkin
GIVEN: workflow is at action "gather_context"
AND: action has NOT been marked complete yet
WHEN: user closes current action
THEN: action "gather_context" is saved to completed_actions
AND: workflow transitions to "decide_planning_criteria" (next action)
```

### Scenario: Close action when already at final action

**Test Method:** `test_close_action_at_final_action_stays_at_final`

```gherkin
GIVEN: workflow is at action "validate_rules" (final action)
WHEN: user closes current action
THEN: action "validate_rules" is saved to completed_actions
AND: workflow stays at "validate_rules" (no next action available)
```

### Scenario: Close final action and transition to next behavior

**Test Method:** `test_close_final_action_transitions_to_next_behavior`

```gherkin
GIVEN: workflow is at final action "validate_rules" of behavior "shape"
WHEN: user closes current action
THEN: "validate_rules" is saved to completed_actions
AND: workflow stays at "validate_rules" (end of behavior)
```

### Scenario: Close action that requires confirmation but wasn't confirmed

**Test Method:** `test_error_when_closing_action_that_requires_confirmation`

```gherkin
GIVEN: workflow is at "initialize_project"
AND: action has NOT been saved to completed_actions (requires confirmation)
THEN: is_action_completed returns False
```

### Scenario: Close action that's already marked complete (idempotent)

**Test Method:** `test_close_handles_action_already_completed_gracefully`

```gherkin
GIVEN: action already complete
WHEN: close again (should be idempotent)
THEN: should still work fine
AND: action remains marked as complete
```

### Scenario: Bot class has close_current_action method (CLI routes to bot.close_current_action)

**Test Method:** `test_bot_class_has_close_current_action_method`

```gherkin
GIVEN: bot is configured with behavior "shape"
WHEN: Bot instance is created
THEN: Bot class has close_current_action method
AND: close_current_action is callable
WHEN: close_current_action is called
THEN: action "gather_context" is marked complete
AND: workflow transitions to next action "decide_planning_criteria"
```
