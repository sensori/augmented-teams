# 📝 Remove Minion From Mob

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Edit Mob
**User:** Game Master
**Sequential Order:** 3
**Story Type:** user

## Story Description

Remove Minion From Mob functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

### Scenario: Game Master removes minion from mob (happy_path)

**Steps:**
```gherkin
Given mob is selected for editing
And mob contains one or more minions
When Game Master selects minion to remove from mob
Then system removes minion from mob
And system updates mob configuration
```


### Scenario: Game Master attempts to remove last minion (error_case)

**Steps:**
```gherkin
Given mob is selected for editing
And mob contains only one minion
When Game Master attempts to remove last minion from mob
Then system shows error message indicating mob must contain at least one minion
And system does not remove minion
```

