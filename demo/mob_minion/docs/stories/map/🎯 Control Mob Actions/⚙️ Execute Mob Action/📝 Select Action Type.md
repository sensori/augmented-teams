# 📝 Select Action Type

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Control Mob Actions
**Feature:** Execute Mob Action
**User:** Game Master
**Sequential Order:** 1
**Story Type:** user

## Story Description

Select Action Type functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Game Master selects action type from available actions
  **then** system displays available action types
  **and** selected action type is stored in temporary action state

- **When** Game Master selects invalid action type
  **then** system shows error message indicating action type is not available

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given mob is selected
And mob has minions available
```

## Scenarios

### Scenario: Game Master selects valid action type (happy_path)

**Steps:**
```gherkin
When Game Master selects action type from available actions
Then system displays available action types
And selected action type is stored in temporary action state
```


### Scenario: Game Master selects invalid action type (error_case)

**Steps:**
```gherkin
When Game Master selects invalid action type
Then system shows error message indicating action type is not available
```

