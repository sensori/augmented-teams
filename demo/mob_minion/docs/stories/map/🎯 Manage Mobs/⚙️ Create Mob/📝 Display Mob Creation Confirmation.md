# 📝 Display Mob Creation Confirmation

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Create Mob
**User:** Game Master
**Sequential Order:** 3
**Story Type:** user

## Story Description

Display Mob Creation Confirmation functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Mob is successfully created

  **then** system displays confirmation dialog showing mob name and token count

- **When** Game Master confirms mob creation

  **then** mob is persisted in Foundry actor system

## Scenarios

### Scenario: Game Master confirms mob creation (happy_path)

**Steps:**
```gherkin
Given Foundry VTT session is active
And mob entity has been successfully created
And mob contains <token_count> tokens
When Mob is successfully created
Then system displays confirmation dialog showing mob name and token count of "<token_count>"
When Game Master confirms mob creation
Then mob is persisted in Foundry actor system
And mob entity is accessible for future operations
```

**Examples:**
| token_count |
| --- |
| 2 |
| 5 |
| 10 |


### Scenario: Game Master cancels mob creation (edge_case)

**Steps:**
```gherkin
Given Foundry VTT session is active
And mob entity has been successfully created
When Mob is successfully created
Then system displays confirmation dialog showing mob name and token count
When Game Master cancels mob creation
Then mob entity is discarded
And tokens remain ungrouped
```

