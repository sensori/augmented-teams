# 📝 Inject Strategy Criteria Into Instructions

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Execute Behavior Actions
**Feature:** Decide Strategy Criteria Action
**User:** Bot Behavior
**Sequential Order:** 1
**Story Type:** user

## Story Description

Inject Strategy Criteria Into Instructions functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** MCP Specific Behavior Action Tool invokes Strategy Action

  **then** Action checks for guardrails in behavior/guardrails/strategy/

- **When** guardrails exist,
  **then** Action loads typical_assumptions.json and decision_criteria files

  **and** Action injects strategy guardrails into strategy section

## Scenarios

### Scenario: Inject Strategy Criteria Into Instructions (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
