# 📝 {story_name}

**Navigation:** [📋 Story Map]({story_map_filename}) | [⚙️ Feature Overview]({feature_overview_filename})

**Epic:** {epic_name}
**Feature:** {feature_name}

## Story Description

{story_description}

## Acceptance Criteria

### Behavioral Acceptance Criteria

{behavioral_acceptance_criteria}

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
{background_steps}
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
{scenario_steps}
```

### Scenario Outline: {scenario_outline_name}

**CRITICAL: Scenario Outline is used when scenarios need multiple data variations (formulas, calculations, domain entities, parameter variations).**

**Steps:**
```gherkin
{scenario_outline_steps}
```

**Examples:**

**CRITICAL Examples Table Requirements:**
- EVERY variable used in Steps MUST have a column in Examples table
- Examples table MUST include BOTH input variables AND output/expected result variables
- Every cell MUST have exact test data values (NO placeholders, NO empty cells, NO vague values like "(same as base)")
- Examples table must have at least 2 rows of test data

| {example_column_headers} |
|{example_column_separators}|
| {example_data_rows} |

## Notes

---

## Source Material

{source_material}

