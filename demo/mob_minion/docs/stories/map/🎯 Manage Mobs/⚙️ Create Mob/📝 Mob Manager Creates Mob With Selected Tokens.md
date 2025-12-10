# 📝 Mob Manager Creates Mob With Selected Tokens

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Create Mob
**User:** System
**Sequential Order:** 4
**Story Type:** system

## Story Description

Mob Manager Creates Mob With Selected Tokens functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** temporary mob group is confirmed
  **then** Mob Manager creates new Mob domain object
  **and** Mob object contains collection of Minion objects from selected tokens
  **and** each Minion object references its Foundry VTT actor ID

- **When** mob group contains less than one minion
  **then** system shows error message indicating mob must contain at least one minion

- **When** duplicate tokens are detected
  **then** system removes duplicates and shows notification

## Scenarios

### Scenario: Mob Manager creates mob with valid tokens (happy_path)

**Steps:**
```gherkin
Given temporary mob group is confirmed
And mob group contains one or more valid minion tokens
When Mob Manager creates new Mob domain object
Then Mob object contains collection of Minion objects from selected tokens
And each Minion object references its Foundry VTT actor ID
```


### Scenario: Mob group contains less than one minion (error_case)

**Steps:**
```gherkin
Given temporary mob group is confirmed
And mob group contains less than one minion
When system attempts to create Mob domain object
Then system shows error message indicating mob must contain at least one minion
```


### Scenario: Duplicate tokens are detected (edge_case)

**Steps:**
```gherkin
Given temporary mob group is confirmed
And mob group contains duplicate tokens
When Mob Manager creates new Mob domain object
Then system removes duplicates
And system shows notification
```

