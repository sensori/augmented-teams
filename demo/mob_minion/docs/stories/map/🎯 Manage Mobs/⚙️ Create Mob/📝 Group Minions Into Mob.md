# 📝 Group Minions Into Mob

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Create Mob
**User:** Game Master
**Sequential Order:** 3
**Story Type:** user

## Story Description

Group Minions Into Mob functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Game Master confirms grouping of selected tokens
  **then** system creates temporary mob group with selected tokens
  **and** mob group displays list of included minion names

- **When** Game Master cancels grouping
  **then** system clears selection and returns to token selection state

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given tokens are selected
And system has retrieved actor data for selected tokens
```

## Scenarios

### Scenario: Game Master confirms grouping (happy_path)

**Steps:**
```gherkin
When Game Master confirms grouping of selected tokens
Then system creates temporary mob group with selected tokens
And mob group displays list of included minion names
```


### Scenario: Game Master cancels grouping (edge_case)

**Steps:**
```gherkin
When Game Master cancels grouping
Then system clears selection
And system returns to token selection state
```

