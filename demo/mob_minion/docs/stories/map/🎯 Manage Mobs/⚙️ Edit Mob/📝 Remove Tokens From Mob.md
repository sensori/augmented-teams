# 📝 Remove Tokens From Mob

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Edit Mob
**User:** Game Master
**Sequential Order:** 2
**Story Type:** user

## Story Description

Remove Tokens From Mob functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Game Master selects tokens within mob and initiates removal

  **then** system removes tokens from mob collection

- **When** last token is removed from mob

  **then** mob entity is deleted from Foundry actor system

## Scenarios

### Scenario: Remove Tokens From Mob (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
     vfg   