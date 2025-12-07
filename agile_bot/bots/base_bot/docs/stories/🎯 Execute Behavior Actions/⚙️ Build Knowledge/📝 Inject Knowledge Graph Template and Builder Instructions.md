# 📝 Inject Knowledge Graph Template and Builder Instructions

**Navigation:** [📋 Story Map](story-map-outline.drawio) | [⚙️ Feature Overview](../README.md)

**Epic:** Execute Behavior Actions  
**Feature:** Build Knowledge

**User:** Bot-Behavior  
**Sequential Order:** 1  
**Story Type:** user

**Test File:** test_build_knowledge.py  
**Test Class:** TestInjectKnowledgeGraphTemplateForBuildKnowledge  
**Test Methods:** 
- test_action_injects_knowledge_graph_template
- test_action_raises_error_when_template_missing

## Story Description

Build Knowledge Action loads the knowledge graph template from the behavior's content folder and injects it into the instructions provided to the AI. The template is located at `behavior/content/knowledge_graph/` and contains the structure for building the knowledge graph. If the template does not exist, the action raises an appropriate error.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** Build Knowledge Action executes
- **THEN** Action loads knowledge graph template from behavior/content/knowledge_graph/
- **AND** Action injects knowledge graph template path into instructions
- **AND** knowledge_graph_template field is present in instructions
- **AND** template file path exists and is accessible
- **WHEN** knowledge graph template does not exist
- **THEN** Action raises FileNotFoundError with appropriate error message

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Build Knowledge Action is initialized with bot_name and behavior
And behavior folder structure exists
```

## Scenarios

### Scenario: Action injects knowledge graph template

**Steps:**
```gherkin
Given behavior folder exists with knowledge graph template
When Build Knowledge Action executes inject_knowledge_graph_template
Then Action loads template from behavior/content/knowledge_graph/
And Action injects template path into instructions
And instructions contain knowledge_graph_template field
And template file path exists
```

**Test Method:** `test_action_injects_knowledge_graph_template`

**Test Details:**
- Creates a knowledge graph template file in the behavior's content folder
- Executes `inject_knowledge_graph_template()` method
- Verifies that `knowledge_graph_template` field is present in returned instructions
- Verifies that the template name is included in the instructions
- Verifies that the template file path exists

### Scenario: Action raises error when template missing

**Steps:**
```gherkin
Given behavior folder exists without knowledge graph template
When Build Knowledge Action executes inject_knowledge_graph_template
Then Action raises FileNotFoundError
And error message indicates template not found
```

**Test Method:** `test_action_raises_error_when_template_missing`

**Test Details:**
- Creates behavior folder structure without knowledge graph template
- Executes `inject_knowledge_graph_template()` method
- Verifies that FileNotFoundError is raised
- Verifies that error message contains "Knowledge graph template not found" or similar text

## Test Details

- **Test File:** `test_build_knowledge.py`
- **Test Class:** `TestInjectKnowledgeGraphTemplateForBuildKnowledge`
- **Test Methods:**
  - `test_action_injects_knowledge_graph_template` - Tests successful template injection
  - `test_action_raises_error_when_template_missing` - Tests error handling when template is missing

## Implementation Notes

The Build Knowledge Action uses the `inject_knowledge_graph_template()` method to:
1. Locate the knowledge graph template in `{behavior}/content/knowledge_graph/` folder
2. Load the template file path
3. Inject the template path into the instructions dictionary under the `knowledge_graph_template` key
4. Return the instructions with the template reference for use by the AI

The template file is expected to be a JSON file that defines the structure for the knowledge graph to be built.

