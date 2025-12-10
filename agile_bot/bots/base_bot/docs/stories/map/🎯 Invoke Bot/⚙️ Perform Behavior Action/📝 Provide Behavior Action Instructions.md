# 📝 Provide Behavior Action Instructions

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Invoke Bot
**Feature:** Perform Behavior Action
**User:** Bot Behavior
**Sequential Order:** 3
**Story Type:** user

## Story Description

Provide Behavior Action Instructions functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Tool invokes Bot.Behavior.Action method

  **then** Behavior Action loads instructions from behavior and base_actions

  **and** Action merges base instructions with behavior-specific instructions

  **and** Compiled instructions returned for injection into AI Chat

## Scenarios

### Scenario: Provide Behavior Action Instructions (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
