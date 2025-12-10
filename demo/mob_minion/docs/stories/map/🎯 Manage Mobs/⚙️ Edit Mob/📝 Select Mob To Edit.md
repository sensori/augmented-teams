# 📝 Select Mob To Edit

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Edit Mob
**User:** Game Master
**Sequential Order:** 1
**Story Type:** user

## Story Description

Select Mob To Edit functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

### Scenario: Game Master selects mob to edit (happy_path)

**Steps:**
```gherkin
Given one or more mobs exist
And mobs are available for selection
When Game Master selects mob to edit
Then system highlights selected mob
And system displays mob details for editing
```


### Scenario: No mobs exist to edit (error_case)

**Steps:**
```gherkin
Given no mobs exist
When Game Master attempts to select mob to edit
Then system shows error message indicating no mobs are available
```

