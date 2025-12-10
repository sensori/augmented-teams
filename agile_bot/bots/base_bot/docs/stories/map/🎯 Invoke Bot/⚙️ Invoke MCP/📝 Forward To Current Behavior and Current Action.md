# 📝 Forward To Current Behavior and Current Action

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Invoke Bot
**Feature:** Invoke MCP
**User:** AI Chat
**Sequential Order:** 3
**Story Type:** user

## Story Description

Forward To Current Behavior and Current Action functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Bot tool receives invocation

  **and** workflow state shows current_behavior and current_action

  **then** Bot tool forwards to correct behavior and action

- **When** workflow state does NOT exist

  **then** Bot tool defaults to first behavior and first action

## Scenarios

### Scenario: Bot tool forwards to current behavior and current action (happy_path)

**Steps:**
```gherkin
Given workflow state shows current_behavior='discovery', current_action='build_knowledge'
When Bot tool receives invocation
Then Bot tool forwards to correct behavior and action
```


### Scenario: Bot tool defaults to first behavior and first action when state missing (happy_path)

**Steps:**
```gherkin
Given workflow state does NOT exist
When Bot tool receives invocation
Then Bot tool defaults to first behavior and first action
```

