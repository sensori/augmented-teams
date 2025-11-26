# 📝 Load Project State from agent_state.json

**Navigation:** [📋 Story Map](../../story-agent-story-map.md) | [⚙️ Feature Overview](../../continue-existing-project-exploration.md)

**Epic:** Start Story Development Session
**Feature:** Continue Existing Project

## Story Description

When Agent initializes without explicit project_area, Agent searches for agent_state.json in current directory and subdirectories (up to 5 levels deep), loads activity_area and project_area from state file, and creates Project instance with discovered state

## Acceptance Criteria

### Behavioral Acceptance Criteria

- When Agent initializes without explicit project_area, then Agent calls _determine_activity_area() which searches for agent_state.json in: 1) project_area/docs/agent_state.json (if project_area provided), 2) current_dir/docs/agent_state.json, 3) subdirectories up to 5 levels deep using pattern "*/" * depth + "docs/agent_state.json"
- When Agent._determine_activity_area() finds agent_state.json, then Agent reads state file, validates agent_name matches 'stories', extracts activity_area from state if present, and returns activity_area (or defaults to agent_name.lower() if not found)
- When Agent creates Project instance, then Agent instantiates Project with activity_area (from _determine_activity_area()), agent_name='stories', and optional project_area parameter, and delegates project area determination to Project
- When Project initializes, then Project calls _load_activity_area_from_state() which also searches for agent_state.json in: 1) project_area/docs/agent_state.json (if project_area provided), 2) current_dir/docs/agent_state.json, 3) subdirectories up to 5 levels deep, and if found loads activity_area and project_area from state file

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Agent is initialized with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L404)
And Agent has no explicit project_area parameter
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

## Scenarios

### Scenario Outline: Agent finds agent_state.json in current directory

**Steps:**
```gherkin
Given test working directory is set up at "<test_working_dir>"
And current working directory is "<test_working_dir>"
And agent_state.json exists at "<test_working_dir>/docs/agent_state.json" with agent_name='stories' and activity_area='<expected_activity_area>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Agent initializes without explicit project_area
  [🔗](../../../../../../src/stories_acceptance_tests.py#L218)
Then Agent calls _determine_activity_area() which searches for agent_state.json
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent finds agent_state.json at "<test_working_dir>/docs/agent_state.json"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent reads state file and validates agent_name matches 'stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent extracts activity_area '<expected_activity_area>' from state
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent returns activity_area '<expected_activity_area>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Agent creates Project instance
  [🔗](../../../../../../src/stories_acceptance_tests.py#L430)
Then Agent instantiates Project with activity_area='<expected_activity_area>' and agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L438)
When Project initializes
  [🔗](../../../../../../src/stories_acceptance_tests.py#L452)
Then Project calls _load_activity_area_from_state() which searches for agent_state.json
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Project finds agent_state.json at "<test_working_dir>/docs/agent_state.json"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Project loads activity_area '<expected_activity_area>' and project_area '<expected_project_area>' from state file
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

**Examples:**
| test_working_dir | expected_activity_area | expected_project_area |
|-----------------|----------------------|---------------------|
| test_data/projects/my-story-project | stories | test_data/projects/my-story-project |
| test_data/projects/story-dev | stories | test_data/projects/story-dev |

### Scenario Outline: Agent finds agent_state.json in subdirectory

**Steps:**
```gherkin
Given test working directory is set up at "<test_working_dir>"
And current working directory is "<test_working_dir>"
And agent_state.json exists at "<subdirectory_path>/docs/agent_state.json" with agent_name='stories' and activity_area='<expected_activity_area>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Agent initializes without explicit project_area
  [🔗](../../../../../../src/stories_acceptance_tests.py#L218)
Then Agent calls _determine_activity_area() which searches subdirectories up to 5 levels deep
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent finds agent_state.json at "<subdirectory_path>/docs/agent_state.json"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent reads state file and validates agent_name matches 'stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent extracts activity_area '<expected_activity_area>' from state
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent returns activity_area '<expected_activity_area>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

**Examples:**
| test_working_dir | subdirectory_path | expected_activity_area |
|-----------------|------------------|----------------------|
| test_data | test_data/projects/my-story-project | stories |
| test_data | test_data/projects/story-dev | stories |
| test_data | test_data/workspace/projects/my-story | stories |

### Scenario: Agent does not find agent_state.json

**Steps:**
```gherkin
Given test working directory is set up at "<test_working_dir>"
And current working directory is "<test_working_dir>"
And no agent_state.json files exist in current directory or subdirectories
  [🔗](../../../../../../src/stories_acceptance_tests.py#L421)
When Agent initializes without explicit project_area
  [🔗](../../../../../../src/stories_acceptance_tests.py#L218)
Then Agent calls _determine_activity_area() which searches for agent_state.json
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent does not find agent_state.json
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent returns default activity_area 'stories' (agent_name.lower())
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

### Scenario: Agent finds agent_state.json with mismatched agent_name

**Steps:**
```gherkin
Given test working directory is set up at "<test_working_dir>"
And current working directory is "<test_working_dir>"
And agent_state.json exists at "<test_working_dir>/docs/agent_state.json" with agent_name='clean_code' (not 'stories')
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Agent initializes without explicit project_area
  [🔗](../../../../../../src/stories_acceptance_tests.py#L218)
Then Agent calls _determine_activity_area() which searches for agent_state.json
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent finds agent_state.json at "<test_working_dir>/docs/agent_state.json"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent reads state file and validates agent_name
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent finds agent_name 'clean_code' does not match 'stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent skips this state file and continues searching
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent returns default activity_area 'stories' (agent_name.lower())
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

