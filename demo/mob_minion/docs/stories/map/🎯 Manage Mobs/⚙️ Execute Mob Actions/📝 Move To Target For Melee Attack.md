# 📝 Move To Target For Melee Attack

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Execute Mob Actions
**User:** Game Master
**Sequential Order:** 1
**Story Type:** user

## Story Description

Move To Target For Melee Attack functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** target is out of range for melee attack

  **then** system moves minions to target location using Foundry movement system

- **When** minions reach target

  **then** system executes melee attack against target

## Scenarios

### Scenario: Move To Target For Melee Attack (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
