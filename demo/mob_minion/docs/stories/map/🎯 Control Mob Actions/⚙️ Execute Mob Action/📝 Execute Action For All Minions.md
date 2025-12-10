# 📝 Execute Action For All Minions

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Control Mob Actions
**Feature:** Execute Mob Action
**User:** Game Master
**Sequential Order:** 3
**Story Type:** user

## Story Description

Execute Action For All Minions functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Game Master confirms action execution
  **then** system prepares to execute action for all minions in mob
  **and** system displays confirmation message showing action will be applied to all minions

- **When** Game Master cancels action execution
  **then** system clears action selection and returns to action type selection state

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given action type is selected and validated
And mob has minions available
```

## Scenarios

### Scenario: Game Master confirms action execution (happy_path)

**Steps:**
```gherkin
When Game Master confirms action execution
Then system prepares to execute action for all minions in mob
And system displays confirmation message showing action will be applied to all minions
```


### Scenario: Game Master cancels action execution (edge_case)

**Steps:**
```gherkin
When Game Master cancels action execution
Then system clears action selection
And system returns to action type selection state
```

