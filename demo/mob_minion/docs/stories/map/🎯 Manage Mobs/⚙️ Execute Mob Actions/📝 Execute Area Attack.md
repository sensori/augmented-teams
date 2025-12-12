# 📝 Execute Area Attack

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Execute Mob Actions
**User:** Game Master
**Sequential Order:** 2
**Story Type:** user

## Story Description

Execute Area Attack functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** area attack action is selected

  **then** system executes area attack affecting multiple targets in range

- **When** area attack is executed

  **then** all targets within area of effect are affected by attack using Foundry combat system

## Scenarios

### Scenario: Execute Area Attack (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
