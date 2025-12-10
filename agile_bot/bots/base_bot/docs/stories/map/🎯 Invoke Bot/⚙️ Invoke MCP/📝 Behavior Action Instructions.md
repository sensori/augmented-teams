# 📝 Behavior Action Instructions

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Invoke Bot
**Feature:** Invoke MCP
**User:** Bot Behavior
**Sequential Order:** 2
**Story Type:** user

## Story Description

Behavior Action Instructions functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Action method is invoked

  **then** Action loads instructions from base_actions and behavior-specific locations

  **and** Instructions are merged and returned

## Scenarios

### Scenario: Behavior Action Instructions (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
