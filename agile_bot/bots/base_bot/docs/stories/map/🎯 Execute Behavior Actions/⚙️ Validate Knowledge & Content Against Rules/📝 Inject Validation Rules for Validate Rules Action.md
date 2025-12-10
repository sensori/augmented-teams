# 📝 Inject Validation Rules for Validate Rules Action

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Execute Behavior Actions
**Feature:** Validate Knowledge & Content Against Rules
**User:** Bot Behavior
**Sequential Order:** 1
**Story Type:** user

## Story Description

Inject Validation Rules for Validate Rules Action functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** MCP Specific Behavior Action Tool invokes Validate Rules Action

  **then** Action loads common bot rules from base_bot/rules/

  **and** Action loads behavior-specific rules

  **and** Action merges and injects rules into validation section

## Scenarios

### Scenario: Inject Validation Rules for Validate Rules Action (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
