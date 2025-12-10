# 📝 Generate Behavior Action Tools

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Build Agile Bots
**Feature:** Generate MCP Tools
**User:** MCP Server Generator
**Sequential Order:** 2
**Story Type:** user

## Story Description

Generate Behavior Action Tools functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Generator processes Bot Config

  **then** Generator creates tool code for each (behavior, action) pair

  **and** Enumerates all behaviors and actions from Bot Config

  **and** For each pair, generates tool code with unique name, trigger words, forwarding logic

  **and** Tool catalog prepared with all generated tool instances

## Scenarios

### Scenario: Generate Behavior Action Tools (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
