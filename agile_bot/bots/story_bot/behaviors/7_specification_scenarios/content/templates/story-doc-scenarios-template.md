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

## Notes

---

## Source Material

{source_material}

