# 📝 Choose Strategy

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Control Mob Actions
**Feature:** Select Strategy
**User:** Game Master
**Sequential Order:** 2
**Story Type:** user

## Story Description

Choose Strategy functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given mob is selected
And available strategies are displayed
```

## Scenarios

### Scenario: Game Master chooses strategy (happy_path)

**Steps:**
```gherkin
When Game Master chooses strategy
Then system assigns strategy to mob
And selected strategy is stored in mob configuration
```


### Scenario: Game Master cancels strategy selection (edge_case)

**Steps:**
```gherkin
When Game Master cancels strategy selection
Then system clears strategy selection
And system returns to mob selection state
```

