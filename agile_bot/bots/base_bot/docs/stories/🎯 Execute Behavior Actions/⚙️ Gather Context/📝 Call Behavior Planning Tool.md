# 📝 Call Behavior Planning Tool

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Execute Behavior Actions  
**Feature:** Gather Context

**User:** Bot Behavior  
**Sequential Order:** 3  
**Story Type:** user

## Story Description

After saving answers and evidence, Bot Behavior calls the behavior planning tool to proceed to the next action in the workflow, which is the Decide Planning Criteria action.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** Gather Context action completes and saves answers and evidence
- **THEN** Bot Behavior calls behavior planning tool
- **AND** Planning tool is invoked with appropriate context
- **WHEN** planning tool is called
- **THEN** workflow proceeds to Decide Planning Criteria action

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Gather Context action has completed
And answers and evidence have been saved
And behavior planning tool is available
```

## Scenarios

### Scenario: Call behavior planning tool after gather context

**Steps:**
```gherkin
Given Gather Context action has completed
And answers and evidence have been saved to docs/stories folder
When Bot Behavior calls behavior planning tool
Then Planning tool is invoked with current workflow state
And Planning tool receives context from clarification.json
And Workflow transitions to Decide Planning Criteria action
```
