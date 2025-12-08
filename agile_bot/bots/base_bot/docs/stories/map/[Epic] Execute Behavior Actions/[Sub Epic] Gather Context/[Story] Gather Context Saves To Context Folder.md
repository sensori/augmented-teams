# [Story] Gather Context Saves To Context Folder

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Execute Behavior Actions  
**Sub Epic:** Gather Context
**User:** Bot Behavior  
**Sequential Order:** 4  
**Story Type:** user

## Story Description

Gather Context Saves To Context Folder functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** GIVEN: context folder exists at {project_area}/docs/context/
- **AND: gather_context action has collected key questions and evidence**
- **WHEN: gather_context action stores clarification data**
- **THEN: gather_context saves to {project_area}/docs/stories/clarification.json**
- **AND: clarification.json is NOT saved to {project_area}/docs/context/clarification.json**
- **AND: clarification.json contains behavior-specific key_questions and evidence structure**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Gather context saves clarification to docs/stories folder

**Steps:**
```gherkin
GIVEN: context folder exists at {project_area}/docs/context/
AND: gather_context action has collected key questions and evidence
WHEN: gather_context action stores clarification data
THEN: gather_context saves to {project_area}/docs/stories/clarification.json
AND: clarification.json is NOT saved to {project_area}/docs/context/clarification.json
AND: clarification.json contains behavior-specific key_questions and evidence structure
```


