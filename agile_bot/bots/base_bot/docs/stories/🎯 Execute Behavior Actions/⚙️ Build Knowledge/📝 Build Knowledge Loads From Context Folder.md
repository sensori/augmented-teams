# 📝 Build Knowledge Loads From Context Folder

**Navigation:** [📋 Story Map](story-map-outline.drawio) | [⚙️ Feature Overview](../README.md)

**Epic:** Execute Behavior Actions  
**Feature:** Build Knowledge

**User:** Bot-Behavior  
**Sequential Order:** 2  
**Story Type:** user

**Test File:** test_context_folder_management.py  
**Test Class:** TestBuildKnowledgeLoadsFromContextFolder  
**Test Method:** test_build_knowledge_loads_context_from_context_folder

## Story Description

Build Knowledge action loads context from the correct locations in the project folder structure. It loads clarification.json and planning.json from the docs/stories folder (generated files) and input.txt from the docs/context folder (original input), then incorporates all context into the generated knowledge graph content.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** build_knowledge action executes
- **THEN** build_knowledge loads {project_area}/docs/stories/clarification.json
- **AND** build_knowledge loads {project_area}/docs/stories/planning.json
- **AND** build_knowledge loads {project_area}/docs/context/input.txt
- **AND** build_knowledge incorporates all context into generated content

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given context folder exists with input.txt
And clarification.json and planning.json exist in docs/stories/
And project has been initialized
```

## Scenarios

### Scenario: Build knowledge loads context from correct locations

**Steps:**
```gherkin
Given context folder exists with input.txt
And clarification.json and planning.json exist in docs/stories/
When build_knowledge action executes
Then build_knowledge loads {project_area}/docs/stories/clarification.json
And build_knowledge loads {project_area}/docs/stories/planning.json
And build_knowledge loads {project_area}/docs/context/input.txt
And build_knowledge incorporates all context into generated content
```

## Test Details

- **Test File:** `test_context_folder_management.py`
- **Test Class:** `TestBuildKnowledgeLoadsFromContextFolder`
- **Test Method:** `test_build_knowledge_loads_context_from_context_folder`

The test verifies that build_knowledge correctly loads context files from:
- Generated files location: `{project_area}/docs/stories/` (clarification.json, planning.json)
- Original input location: `{project_area}/docs/context/` (input.txt)
