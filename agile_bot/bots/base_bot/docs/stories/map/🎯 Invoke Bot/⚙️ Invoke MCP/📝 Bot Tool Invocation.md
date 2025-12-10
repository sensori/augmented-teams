# 📝 Bot Tool Invocation

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Invoke Bot
**Feature:** Invoke MCP
**User:** AI Chat
**Sequential Order:** 1
**Story Type:** user

## Story Description

Bot Tool Invocation functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** AI Chat invokes bot tool with behavior and action parameters

  **then** Tool routes to correct behavior.action method

  **and** Tool executes action and returns result

- **When** AI Chat invokes tool for specific behavior

  **then** Tool routes to that behavior only, not other behaviors

## Scenarios

### Scenario: Bot Tool Invocation (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
