# 📝 Evaluate Available Targets

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Control Mob Actions
**Feature:** Choose Target
**User:** Game Master
**Sequential Order:** 1
**Story Type:** user

## Story Description

Evaluate Available Targets functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

### Scenario: System evaluates available targets (happy_path)

**Steps:**
```gherkin
Given mob is selected
And strategy is assigned to mob
And Foundry VTT scene has enemy tokens
When system evaluates available targets
Then system queries Foundry VTT for enemy tokens
And system displays list of available targets
```


### Scenario: No targets available (edge_case)

**Steps:**
```gherkin
Given mob is selected
And strategy is assigned to mob
And Foundry VTT scene has no enemy tokens
When system evaluates available targets
Then system shows message indicating no targets are available
```

