# [Story] Input File Copied To Context Folder

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Invoke Bot  
**Sub Epic:** Init Project
**User:** Bot Behavior  
**Sequential Order:** 1.6  
**Story Type:** user

## Story Description

Input File Copied To Context Folder functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** GIVEN: User provides input file via @input.txt command
- **AND: input file exists at original location**
- **WHEN: initialize_project action executes**
- **THEN: initialize_project copies input file to {project_area}/docs/context/input.txt**
- **AND: original input file remains at original location (copy, not move)**
- **AND: {project_area}/docs/context/input.txt exists and contains original content**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Initialize project copies input file to context folder

**Steps:**
```gherkin
GIVEN: User provides input file via @input.txt command
AND: input file exists at original location
WHEN: initialize_project action executes
THEN: initialize_project copies input file to {project_area}/docs/context/input.txt
AND: original input file remains at original location (copy, not move)
AND: {project_area}/docs/context/input.txt exists and contains original content
```


