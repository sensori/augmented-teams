# 📝 Confirm Project Area

**Navigation:** [📋 Story Map](../../story-agent-story-map.md) | [⚙️ Feature Overview](../../continue-existing-project-exploration.md)

**Epic:** Start Story Development Session
**Feature:** Continue Existing Project

## Story Description

MCP Server calls agent_get_state() after Project initialization, Project presents determined project_area to user for confirmation (even if loaded from state file), user confirms or suggests different project area, and Project saves confirmed project_area to agent_state.json

## Acceptance Criteria

### Behavioral Acceptance Criteria

- When MCP Server calls agent_get_state() after Project initialization, then MCP Server calls agent.check_project_area_confirmation() which delegates to Project.present_project_area_to_user(), and Project presents determined project_area to user for confirmation (even if loaded from state file)
- When Project presents project_area to user, then Project loads message template from agents/base/agent.json prompt_templates.project_initialization.project_area_required.template, replaces {{example_project_path}} with determined project_area, and returns confirmation data with needs_confirmation: true, message, and suggested_project_area
- When MCP Server receives confirmation data from Project, then MCP Server returns response to AI Chat with needs_confirmation: true, message containing suggested project area, and suggested_project_area value
- When AI Chat receives confirmation response from MCP Server, then AI Chat presents message to user in chat window showing suggested project area and requesting confirmation or alternative project area
- When user confirms project area (either accepts suggested or provides different value), then AI Chat calls agent_set_project_area tool with confirmed project_area value, MCP Server updates Project with confirmed project_area, Project saves project_area to agent_state.json, and Project creates necessary directory structure
- When user confirms or suggests different project area, then Project updates project_area if user suggested different value, saves project_area to agent_state.json in project area, creates necessary directory structure, and completes initialization

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Agent is initialized with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L404)
And Project has been initialized and has determined project_area
  [🔗](../../../../../../src/stories_acceptance_tests.py#L579)
```

## Scenarios

### Scenario Outline: Project presents project area for confirmation (loaded from state)

**Steps:**
```gherkin
Given Project has loaded project_area '<suggested_project_area>' from agent_state.json
  [🔗](../../../../../../src/stories_acceptance_tests.py#L579)
When MCP Server calls agent_get_state() after Project initialization
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then MCP Server calls agent.check_project_area_confirmation()
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And agent.check_project_area_confirmation() delegates to Project.present_project_area_to_user()
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Project presents determined project_area '<suggested_project_area>' to user for confirmation
  [🔗](../../../../../../src/stories_acceptance_tests.py#L464)
When Project presents project_area to user
  [🔗](../../../../../../src/stories_acceptance_tests.py#L464)
Then Project loads message template from agents/base/agent.json prompt_templates.project_initialization.project_area_required.template
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Project replaces {{example_project_path}} with determined project_area '<suggested_project_area>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Project returns confirmation data with needs_confirmation: true, message, and suggested_project_area '<suggested_project_area>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When MCP Server receives confirmation data from Project
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then MCP Server returns response to AI Chat with needs_confirmation: true, message containing suggested project area, and suggested_project_area '<suggested_project_area>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When AI Chat receives confirmation response from MCP Server
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then AI Chat presents message to user in chat window showing suggested project area '<suggested_project_area>' and requesting confirmation or alternative project area
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

**Examples:**
| suggested_project_area |
|----------------------|
| test_data/projects/my-story-project |
| test_data/projects/story-dev |
| C:\dev\my-story-project |

### Scenario Outline: User confirms suggested project area

**Steps:**
```gherkin
Given Project has presented project_area '<suggested_project_area>' to user
  [🔗](../../../../../../src/stories_acceptance_tests.py#L512)
And AI Chat has presented confirmation message to user
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When user confirms project area (accepts suggested)
  [🔗](../../../../../../src/stories_acceptance_tests.py#L470)
Then AI Chat calls agent_set_project_area tool with confirmed project_area '<suggested_project_area>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And MCP Server updates Project with confirmed project_area '<suggested_project_area>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Project saves project_area to '<suggested_project_area>/docs/agent_state.json'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L476)
And Project creates necessary directory structure
  [🔗](../../../../../../src/stories_acceptance_tests.py#L485)
And Project completes initialization
  [🔗](../../../../../../src/stories_acceptance_tests.py#L493)
```

**Examples:**
| suggested_project_area |
|----------------------|
| test_data/projects/my-story-project |
| test_data/projects/story-dev |

### Scenario Outline: User suggests different project area

**Steps:**
```gherkin
Given Project has presented project_area '<suggested_project_area>' to user
  [🔗](../../../../../../src/stories_acceptance_tests.py#L512)
And AI Chat has presented confirmation message to user
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When user suggests different project area '<user_suggested_area>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L518)
Then Project updates project_area to '<user_suggested_area>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L524)
And Project saves project_area to '<user_suggested_area>/docs/agent_state.json'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L531)
And Project creates necessary directory structure in new project area '<user_suggested_area>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L537)
And Project completes initialization
  [🔗](../../../../../../src/stories_acceptance_tests.py#L493)
```

**Examples:**
| suggested_project_area | user_suggested_area |
|----------------------|-------------------|
| test_data/projects/my-story-project | test_data/projects/my-story-project-v2 |
| test_data/projects/story-dev | test_data/projects/story-dev-main |

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

