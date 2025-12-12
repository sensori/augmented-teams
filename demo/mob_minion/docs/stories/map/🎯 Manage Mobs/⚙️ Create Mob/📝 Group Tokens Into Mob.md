# 📝 Group Tokens Into Mob

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Create Mob
**User:** Game Master
**Sequential Order:** 2
**Story Type:** user

## Story Description

Group Tokens Into Mob functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Game Master selects multiple tokens and initiates mob creation

  **then** system creates new Mob entity containing selected tokens

- **When** Mob is created

  **then** all tokens in mob are linked to mob entity via Foundry Token API

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Foundry VTT session is active
And Game Master has selected <token_count> minion tokens
And tokens are not already part of another mob
```

## Scenarios

### Scenario: Game Master groups tokens into mob successfully (happy_path)

**Steps:**
```gherkin
When Game Master initiates mob creation
Then system creates new Mob entity containing selected tokens
And mob entity is assigned unique ID
When Mob is created
Then all "<token_count>" tokens in mob are linked to mob entity via Foundry Token API
And mob entity stores references to all token IDs and actor IDs
```

**Examples:**
| token_count |
| --- |
| 2 |
| 5 |
| 10 |

