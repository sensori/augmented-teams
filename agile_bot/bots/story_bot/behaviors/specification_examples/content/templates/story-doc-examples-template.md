# 📝 {story_name}

**Navigation:** [📋 Story Map]({story_map_filename}) | [⚙️ Feature Overview]({feature_overview_filename})

**Epic:** {epic_name}
**Feature:** {feature_name}

## Story Description

<Actor> <verb> <noun> so that <business_value>

**Example:**
AI Chat processes story shaping request so that users can initiate story mapping workflows

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** <action>, **then** <outcome>
- **When** <action>, **then** <outcome>
- **When** <action>, **then** <outcome>

**Example:**
- **When** Project loads configuration, **then** Agent configuration is loaded from agent.json
- **When** Workflow is created, **then** Workflow State is set to first behavior
- **When** next action is called, **then** shape behavior clarification is presented

## Background

**CRITICAL: Background section is ONLY for common setup steps shared across 3+ scenarios. DO NOT include scenario-specific setup here.**

**What belongs in Background:**
- Setup steps that are TRUE for ALL scenarios in this story (100% of scenarios)
- Common preconditions that every single scenario needs
- Shared system state that applies to all scenarios without exception
- Steps that never vary between scenarios
- Example: "Given Agent is initialized with agent_name='story_bot'" (true for ALL scenarios)
- Example: "Given Cursor/VS Code chat window is open" (true for ALL scenarios)
- Example: "Given Project is finished initializing" (true for ALL scenarios)

**What does NOT belong in Background:**
- Scenario-specific setup (goes in scenario Steps as Given)
- Variable-dependent setup (goes in scenario Steps)
- Setup that only applies to some scenarios (goes in scenario Steps)
- Test data paths or file names (goes in scenario Steps)
- Conditional setup (goes in scenario Steps)
- Example: "Given test project area is set up at \"<test_project_area>\"" (WRONG - scenario-specific with variable, goes in Steps)
- Example: "Given user has attached documents to chat window" (WRONG if not true for ALL scenarios - check if all scenarios need this)

**GOOD Example (from Initialize Behavior and Workflow story):**
```gherkin
Given Agent is initialized with agent_name='story_bot'
And Project is finished initializing
```
These are true for ALL scenarios in that story.

**BAD Example (what NOT to do):**
```gherkin
Given test project area is set up at "<test_project_area>"
And test agent base area is set up at "<test_agent_base_area>"
```
These are scenario-specific with variables and belong in scenario Steps, not Background.

**Common setup steps shared across all scenarios:**

```gherkin
Given <entity> is initialized with <parameter>=<value>
And <system_state_condition>
And <another_common_state>
```

**Example:**
```gherkin
Given Agent is initialized with agent_name='story_bot'
And Project is finished initializing
And Cursor chat window is open
```

## Scenarios

**CRITICAL: Each scenario's Steps section starts with Given steps for scenario-specific setup. Background steps are automatically applied before scenario Steps.**

**What goes in scenario Steps Given section:**
- Setup specific to THIS scenario only
- Variable-dependent setup (even if similar across scenarios)
- Test data setup (paths, file names, etc.)
- Scenario-specific preconditions
- Any setup that is NOT true for ALL scenarios
- Variables for Scenario Outlines (e.g., "<test_project_area>", "<error_condition>")

**GOOD Example structure:**
- Background has: "Given Agent is initialized with agent_name='story_bot'" (common to ALL scenarios)
- Background has: "Given Project is finished initializing" (common to ALL scenarios)
- Scenario Steps start with: "Given test project area is set up at \"<test_project_area>\"" (scenario-specific with variable)
- Scenario Steps continue with: "And valid base agent.json exists at \"<test_agent_base_area>/agent.json>\"" (scenario-specific with variable)

**BAD Example (what NOT to do):**
- Background has: "Given test project area is set up at \"<test_project_area>\"" (WRONG - this is scenario-specific with variable)
- Scenario Steps start with: "Given Agent is initialized" (WRONG - this belongs in Background if true for all scenarios)

### Scenario: {scenario_name}

**Steps:**
```gherkin
Given <scenario_specific_state_condition>
And <scenario_specific_setup>
When <user_action_or_system_event>
Then <expected_outcome>
And <another_expected_outcome>
```

**Example:**
```gherkin
Given test project area is set up at test_data/projects/valid-project
And valid base agent.json exists at test_data/agents/base/agent.json
When Project initializes with project_path='test_data/projects/valid-project'
Then Project loads agent configuration from agent.json
And Project creates Workflow instance
```

### Scenario Outline: {scenario_outline_name}

**CRITICAL: Scenario Outline is used when scenarios need multiple data variations (formulas, calculations, domain entities, parameter variations).**

**Steps:**
```gherkin
Given <scenario_specific_state> at "<variable_path>"
And <entity> exists at "<variable_file_path>"
When <action> with <variable_parameter>="<variable_value>"
Then <expected_outcome> equals "<variable_expected_result>"
And <another_outcome> is "<variable_result>"
```

**Example:**
```gherkin
Given test project area is set up at "<test_project_area>"
And valid base agent.json exists at "<test_agent_base_area>/agent.json"
When Project initializes with project_path="<test_project_area>"
Then Project loads agent configuration from "<test_agent_base_area>/agent.json"
And Agent name equals "<expected_agent_name>"
```

**Examples:**

**CRITICAL Examples Table Requirements:**
- EVERY variable used in Steps MUST have a column in Examples table
- Examples table MUST include BOTH input variables AND output/expected result variables
- Every cell MUST have exact test data values (NO placeholders, NO empty cells, NO vague values like "(same as base)")
- Examples table must have at least 2 rows of test data

| <variable1> | <variable2> | <variable3> | <expected_result> |
|------------|------------|------------|------------------|
| <value1>   | <value2>   | <value3>   | <result1>        |
| <value4>   | <value5>   | <value6>   | <result2>        |

**Example:**
| test_project_area                    | test_agent_base_area                  | expected_agent_name |
|-------------------------------------|--------------------------------------|---------------------|
| test_data/projects/valid-project    | test_data/agents/base                 | story_bot           |
| test_data/projects/another-project  | test_data/agents/custom               | custom_bot          |

## Notes

---

## Source Material

{source_material}

