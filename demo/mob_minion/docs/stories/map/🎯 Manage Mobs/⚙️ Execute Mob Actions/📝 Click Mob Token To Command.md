# 📝 Click Mob Token To Command

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Execute Mob Actions
**User:** Game Master
**Sequential Order:** 1
**Story Type:** user

## Story Description

Click Mob Token To Command functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Game Master clicks any token belonging to mob

  **then** system identifies mob associated with clicked token

- **When** mob is identified

  **then** system prepares to execute action for all minions in mob

## Scenarios

### Scenario: Game Master clicks mob token to command mob (happy_path)

**Steps:**
```gherkin
Given Foundry VTT session is active
And mob exists with <token_count> minion tokens
And mob is persisted in Foundry actor system
When Game Master clicks any token belonging to mob
Then system identifies mob associated with clicked token
When mob is identified
Then system prepares to execute action for all "<token_count>" minions in mob
```

**Examples:**
| token_count |
| --- |
| 2 |
| 5 |
| 10 |


### Scenario: Game Master clicks token not belonging to mob (edge_case)

**Steps:**
```gherkin
Given Foundry VTT session is active
And individual minion tokens exist that are not part of any mob
When Game Master clicks token that does not belong to any mob
Then system treats it as individual minion
And no mob action is prepared
```

