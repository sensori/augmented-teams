# 📝 Save Final Assumptions and Decisions

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Execute Behavior Actions  
**Feature:** Decide Planning Criteria

**User:** Bot Behavior  
**Sequential Order:** 2  
**Story Type:** user

## Story Description

Bot Behavior saves the final assumptions and decisions made during the Decide Planning Criteria action to the project's docs/stories folder (generated file), storing them in a structured format for use in subsequent actions.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** Decide Planning Criteria action collects assumptions and decisions
- **THEN** Bot Behavior saves assumptions and decisions to docs/stories folder (generated file)
- **AND** Assumptions and decisions are stored in structured format (planning.json)
- **AND** planning.json is saved to {project_area}/docs/stories/planning.json (NOT in context folder)
- **WHEN** assumptions and decisions are saved
- **THEN** subsequent actions can load and use this context from docs/stories folder

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Decide Planning Criteria action has collected assumptions and decisions
And project docs/stories folder exists
```

## Scenarios

### Scenario: Save assumptions and decisions to docs/stories folder

**Steps:**
```gherkin
Given Decide Planning Criteria action has collected assumptions and decisions
When Bot Behavior saves assumptions and decisions
Then Bot Behavior saves to {project_area}/docs/stories/planning.json
And planning.json contains structured assumptions and decisions
And planning.json follows behavior-specific format
And planning.json is NOT saved to {project_area}/docs/context/ folder
And subsequent actions can load planning.json from docs/stories folder
```
