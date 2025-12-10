# 📝 Add Minion To Mob

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Edit Mob
**User:** Game Master
**Sequential Order:** 2
**Story Type:** user

## Story Description

Add Minion To Mob functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

### Scenario: Game Master adds minion to mob (happy_path)

**Steps:**
```gherkin
Given mob is selected for editing
And minion tokens are available on scene
When Game Master selects minion token to add
Then system adds minion to mob
And system updates mob configuration with new minion
```


### Scenario: Game Master adds duplicate minion (edge_case)

**Steps:**
```gherkin
Given mob is selected for editing
And minion token is already in mob
When Game Master selects minion token that is already in mob
Then system shows notification that minion is already in mob
And system does not add duplicate minion
```

