# 📝 Execute Attack Action

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Execute Mob Actions
**User:** Game Master
**Sequential Order:** 3
**Story Type:** user

## Story Description

Execute Attack Action functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** target is determined and attack action is selected

  **then** system executes attack for all minions in mob via Foundry combat system

- **When** attack is executed

  **then** all minions perform attack action against selected target

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Foundry VTT session is active
And mob exists with <token_count> minion tokens
And target has been determined
And attack action is selected
And Foundry combat system is active
```

## Scenarios

### Scenario: System executes attack for all minions in mob (happy_path)

**Steps:**
```gherkin
When target is determined and attack action is selected
Then system executes attack for all "<token_count>" minions in mob via Foundry combat system
When attack is executed
Then all "<token_count>" minions perform attack action against selected target
And system updates combat tracker with results for all minions in mob
```

**Examples:**
| token_count |
| --- |
| 2 |
| 5 |
| 10 |

