# 📝 Select Attack Most Powerful Target Strategy

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Select Strategy
**User:** Game Master
**Sequential Order:** 1
**Story Type:** user

## Story Description

Select Attack Most Powerful Target Strategy functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Game Master selects Attack Most Powerful Target strategy

  **then** system configures mob to target enemy with highest power/level

- **When** mob executes action

  **then** target selection algorithm identifies most powerful enemy using Foundry combat system

## Scenarios

### Scenario: Select Attack Most Powerful Target Strategy (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
