# 📝 Select Attack Most Damaged Person Strategy

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Select Strategy
**User:** Game Master
**Sequential Order:** 4
**Story Type:** user

## Story Description

Select Attack Most Damaged Person Strategy functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Game Master selects Attack Most Damaged Person strategy

  **then** system configures mob to target enemy with lowest health/damage

- **When** mob executes action

  **then** target selection algorithm identifies most damaged enemy using Foundry combat system

## Scenarios

### Scenario: Select Attack Most Damaged Person Strategy (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
