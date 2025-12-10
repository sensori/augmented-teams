# 📝 Confirm Target Selection

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Control Mob Actions
**Feature:** Choose Target
**User:** Game Master
**Sequential Order:** 3
**Story Type:** user

## Story Description

Confirm Target Selection functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given target is selected by strategy
And target is displayed to Game Master
```

## Scenarios

### Scenario: Game Master confirms target selection (happy_path)

**Steps:**
```gherkin
When Game Master confirms target selection
Then system stores confirmed target for action execution
And system proceeds to action execution
```


### Scenario: Game Master rejects target selection (edge_case)

**Steps:**
```gherkin
When Game Master rejects target selection
Then system clears target selection
And system returns to target evaluation state
```

