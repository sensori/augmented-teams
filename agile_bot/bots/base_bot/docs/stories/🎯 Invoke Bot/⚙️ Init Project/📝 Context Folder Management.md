# 📝 Context Folder Management

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Init Project

**User:** Bot-Behavior  
**Sequential Order:** 1.5  
**Story Type:** system  
**Test File:** test_context_folder_management.py

## Story Description

Tests verify that initialize_project creates context folder at `{project_area}/docs/context/` and all actions reference context files from correct locations:
- Original input files: `{project_area}/docs/context/`
- Generated files (clarification.json, planning.json): `{project_area}/docs/stories/`

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** initialize_project action completes with confirmation
- **THEN** `{project_area}/docs/context/` folder exists
- **AND** context folder is ready for context files
- **WHEN** user provides input file via `@input.txt` command
- **AND** input file exists at original location
- **WHEN** initialize_project action executes
- **THEN** initialize_project copies input file to `{project_area}/docs/context/input.txt`
- **AND** original input file remains at original location (copy, not move)
- **AND** `{project_area}/docs/context/input.txt` exists and contains original content
- **WHEN** context folder exists at `{project_area}/docs/context/`
- **AND** gather_context action has collected key questions and evidence
- **WHEN** gather_context action stores clarification data
- **THEN** gather_context saves to `{project_area}/docs/stories/clarification.json`
- **AND** clarification.json is NOT saved to `{project_area}/docs/context/clarification.json`
- **AND** clarification.json contains behavior-specific key_questions and evidence structure
- **WHEN** context folder exists with input.txt
- **AND** clarification.json and planning.json exist in docs/stories/
- **WHEN** build_knowledge action executes
- **THEN** build_knowledge loads `{project_area}/docs/stories/clarification.json`
- **AND** build_knowledge loads `{project_area}/docs/stories/planning.json`
- **AND** build_knowledge loads `{project_area}/docs/context/input.txt`
- **AND** build_knowledge incorporates all context into generated content

## Scenarios

### Scenario: Initialize project creates context folder

**Test Class:** `TestInitializeProjectCreatesContextFolder`  
**Test Method:** `test_context_folder_created_after_project_confirmation`

```gherkin
GIVEN: User confirms project area location
WHEN: initialize_project action completes
THEN: {project_area}/docs/context/ folder exists
AND: context folder is ready for context files
```

### Scenario: Initialize project copies input file to context folder

**Test Class:** `TestInputFileCopiedToContextFolder`  
**Test Method:** `test_input_file_copied_to_context_folder`

```gherkin
GIVEN: User provides input file via @input.txt command
AND: input file exists at original location
WHEN: initialize_project action executes
THEN: initialize_project copies input file to {project_area}/docs/context/input.txt
AND: original input file remains at original location (copy, not move)
AND: {project_area}/docs/context/input.txt exists and contains original content
```

### Scenario: Gather context saves clarification to docs/stories folder

**Test Class:** `TestGatherContextSavesToContextFolder`  
**Test Method:** `test_gather_context_saves_clarification_to_context_folder`

```gherkin
GIVEN: context folder exists at {project_area}/docs/context/
AND: gather_context action has collected key questions and evidence
WHEN: gather_context action stores clarification data
THEN: gather_context saves to {project_area}/docs/stories/clarification.json
AND: clarification.json is NOT saved to {project_area}/docs/context/clarification.json
AND: clarification.json contains behavior-specific key_questions and evidence structure
```

### Scenario: Build knowledge loads context from correct locations

**Test Class:** `TestBuildKnowledgeLoadsFromContextFolder`  
**Test Method:** `test_build_knowledge_loads_context_from_context_folder`

```gherkin
GIVEN: context folder exists with input.txt
AND: clarification.json and planning.json exist in docs/stories/
WHEN: build_knowledge action executes
THEN: build_knowledge loads {project_area}/docs/stories/clarification.json
AND: build_knowledge loads {project_area}/docs/stories/planning.json
AND: build_knowledge loads {project_area}/docs/context/input.txt
AND: build_knowledge incorporates all context into generated content
```
