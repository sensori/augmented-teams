# 📝 Respect Range Constraints

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Control Mob Actions
**Feature:** Execute Mob Action
**User:** Game Master
**Sequential Order:** 6
**Story Type:** user

## Story Description

Respect Range Constraints functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Game Master selects target for action
  **then** system checks target is within range for action type
  **and** system displays range validation status

- **When** target is out of range
  **then** system shows error message indicating target is out of range
  **and** system prevents action execution

- **When** target is within range
  **then** system allows action execution to proceed

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given action type is selected
And mob has minions available
```

## Scenarios

### Scenario: Game Master selects target within range (happy_path)

**Steps:**
```gherkin
When Game Master selects target for action
Then system checks target is within range for action type
And system displays range validation status
And system allows action execution to proceed
```


### Scenario: Game Master selects target out of range (error_case)

**Steps:**
```gherkin
When Game Master selects target for action
And target is out of range
Then system shows error message indicating target is out of range
And system prevents action execution
```

