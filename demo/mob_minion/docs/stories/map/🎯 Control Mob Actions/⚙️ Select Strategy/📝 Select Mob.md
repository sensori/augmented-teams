# 📝 Select Mob

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Control Mob Actions
**Feature:** Select Strategy
**User:** Game Master
**Sequential Order:** 1
**Story Type:** user

## Story Description

Select Mob functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

### Scenario: Game Master selects existing mob (happy_path)

**Steps:**
```gherkin
Given one or more mobs exist
And mobs are available for selection
When Game Master selects mob
Then system highlights selected mob
And selected mob is stored in temporary selection state
```


### Scenario: No mobs exist (error_case)

**Steps:**
```gherkin
Given no mobs exist
When Game Master attempts to select mob
Then system shows error message indicating no mobs are available
```

