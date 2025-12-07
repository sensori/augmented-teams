# 📝 Save Answers and Evidence

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Execute Behavior Actions  
**Feature:** Gather Context

**User:** Bot Behavior  
**Sequential Order:** 2  
**Story Type:** user

## Story Description

Bot Behavior saves the answers and evidence collected during the Gather Context action to the project's docs/stories folder (generated file), storing them in a structured format for use in subsequent actions.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** Gather Context action collects answers and evidence
- **THEN** Bot Behavior saves answers and evidence to docs/stories folder (generated file)
- **AND** Answers and evidence are stored in structured format (clarification.json)
- **AND** clarification.json is saved to {project_area}/docs/stories/clarification.json (NOT in context folder)
- **WHEN** answers and evidence are saved
- **THEN** subsequent actions can load and use this context from docs/stories folder

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Gather Context action has collected answers and evidence
And project docs/stories folder exists
```

## Scenarios

### Scenario: Save answers and evidence to docs/stories folder

**Steps:**
```gherkin
Given Gather Context action has collected answers and evidence
When Bot Behavior saves answers and evidence
Then Bot Behavior saves to {project_area}/docs/stories/clarification.json
And clarification.json contains structured answers and evidence
And clarification.json follows behavior-specific format
And clarification.json is NOT saved to {project_area}/docs/context/ folder
And subsequent actions can load clarification.json from docs/stories folder
```
