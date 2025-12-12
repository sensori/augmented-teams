# 📝 Select Attack Weakest Target Strategy

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Select Strategy
**User:** Game Master
**Sequential Order:** 2
**Story Type:** user

## Story Description

Select Attack Weakest Target Strategy functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Game Master selects Attack Weakest Target strategy

  **then** system configures mob to target enemy with lowest power/level

- **When** mob executes action

  **then** target selection algorithm identifies weakest enemy using Foundry combat system

## Scenarios

### Scenario: Select Attack Weakest Target Strategy (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
