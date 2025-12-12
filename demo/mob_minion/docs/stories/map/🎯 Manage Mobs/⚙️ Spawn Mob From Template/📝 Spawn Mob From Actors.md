# 📝 Spawn Mob From Actors

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Spawn Mob From Template
**User:** Game Master
**Sequential Order:** 2
**Story Type:** user

## Story Description

Spawn Mob From Actors functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Game Master selects template and spawn location

  **then** system creates tokens from specified actors using Foundry actor system

- **When** tokens are created

  **then** system groups spawned tokens into new mob entity

## Scenarios

### Scenario: Spawn Mob From Actors (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
