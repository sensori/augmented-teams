# 📝 Display Available Strategies

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Manage Mobs
**Feature:** Select Strategy
**User:** Game Master
**Sequential Order:** 1
**Story Type:** user

## Story Description

Display Available Strategies functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Game Master selects mob token

  **then** system displays strategy selection menu with available strategies

- **When** strategies are displayed

  **then** system shows: Attack Most Powerful Target, Attack Weakest Target, Defend Leader, Attack Most Damaged Person

## Scenarios

### Scenario: Display Available Strategies (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
