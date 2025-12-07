# 📝 Call Build Knowledge Tool

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Execute Behavior Actions  
**Feature:** Decide Planning Criteria

**User:** Bot Behavior  
**Sequential Order:** 3  
**Story Type:** user

## Story Description

After saving assumptions and decisions, Bot Behavior calls the build knowledge tool to proceed to the next action in the workflow, which is the Build Knowledge action.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** Decide Planning Criteria action completes and saves assumptions and decisions
- **THEN** Bot Behavior calls build knowledge tool
- **AND** Build knowledge tool is invoked with appropriate context
- **WHEN** build knowledge tool is called
- **THEN** workflow proceeds to Build Knowledge action

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Decide Planning Criteria action has completed
And assumptions and decisions have been saved
And build knowledge tool is available
```

## Scenarios

### Scenario: Call build knowledge tool after planning

**Steps:**
```gherkin
Given Decide Planning Criteria action has completed
And assumptions and decisions have been saved to docs/stories folder
When Bot Behavior calls build knowledge tool
Then Build knowledge tool is invoked with current workflow state
And Build knowledge tool receives context from planning.json and clarification.json
And Workflow transitions to Build Knowledge action
```
