# 📝 Apply Strategy To Select Target

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Control Mob Actions
**Feature:** Choose Target
**User:** Game Master
**Sequential Order:** 2
**Story Type:** user

## Story Description

Apply Strategy To Select Target functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

### Scenario: System applies strategy to select target (happy_path)

**Steps:**
```gherkin
Given available targets are evaluated
And strategy is assigned to mob
When system applies strategy to select target
Then system evaluates targets according to strategy rules
And system selects target based on strategy
And selected target is stored in temporary selection state
```


### Scenario: Strategy cannot select valid target (edge_case)

**Steps:**
```gherkin
Given available targets are evaluated
And strategy is assigned to mob
And no targets meet strategy criteria
When system applies strategy to select target
Then system shows message indicating no targets meet strategy criteria
```

