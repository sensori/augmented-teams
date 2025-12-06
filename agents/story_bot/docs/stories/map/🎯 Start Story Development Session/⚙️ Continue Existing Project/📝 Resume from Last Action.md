# 📝 Resume from Last Action

**Navigation:** [📋 Story Map](../../story-agent-story-map.md) | [⚙️ Feature Overview](../../continue-existing-project-exploration.md)

**Epic:** Start Story Development Session
**Feature:** Continue Existing Project

## Story Description

After workflow state is restored, Agent._initialize_components() skips _start_workflow_if_needed() since workflow already has current_stage and current_action set. AI Chat can immediately call agent_get_instructions() to get instructions for the current action, allowing user to continue from where they left off

## Acceptance Criteria

### Behavioral Acceptance Criteria

- When Agent._initialize_components() completes workflow state restoration, then Agent checks if _needs_project_area() (project area not yet confirmed), and if false calls _start_workflow_if_needed()
- When Agent._start_workflow_if_needed() is called, then Agent checks if workflow._current_stage is already set (from restoration), and if set skips workflow start logic and returns early
- When workflow state was restored and _start_workflow_if_needed() is skipped, then workflow remains at restored state (current_stage and current_action set), and Agent completes initialization without restarting workflow
- When AgentStateManager synchronizes workflow, then AgentStateManager checks if Project has workflow attribute, and if missing or None sets Project.workflow to Agent.workflow, and if Project workflow references different object updates Project.workflow to reference Agent.workflow
- When MCP Server synchronizes project workflow, then MCP Server ensures Project workflow reference matches Agent workflow reference, and updates Project workflow if needed
- When AI Chat calls agent_get_instructions() after project area confirmation and workflow restoration, then MCP Server calls agent.instructions property which delegates to workflow.current_action.instructions, and AI Chat receives instructions for the current action (e.g., clarification, planning, build_structure, render_output, validate)
- When user receives instructions for current action, then user can immediately continue working from where they left off, with all workflow context (behavior, action, previous outputs) available and ready for continuation

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Agent is initialized with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L404)
And Project has been initialized and project area has been confirmed
  [🔗](../../../../../../src/stories_acceptance_tests.py#L585)
And Workflow state has been successfully restored with current_behavior_name and current_action_name
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

## Scenarios

### Scenario Outline: Agent skips workflow start when state is restored

**Steps:**
```gherkin
Given workflow._current_stage is set to '<restored_behavior_name>' from restoration
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And workflow._current_action is set to '<restored_action_name>' from restoration
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Agent._initialize_components() completes workflow state restoration
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then Agent checks if _needs_project_area()
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent finds project area is confirmed (returns false)
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent calls _start_workflow_if_needed()
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Agent._start_workflow_if_needed() is called
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then Agent checks if workflow._current_stage is already set
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent finds workflow._current_stage is set to '<restored_behavior_name>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent skips workflow start logic and returns early
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When workflow state was restored and _start_workflow_if_needed() is skipped
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then workflow remains at restored state with current_stage '<restored_behavior_name>' and current_action '<restored_action_name>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent completes initialization without restarting workflow
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

**Examples:**
| restored_behavior_name | restored_action_name |
|----------------------|-------------------|
| shape | clarification |
| shape | planning |
| shape | build_structure |
| shape | render_output |
| shape | validate |

### Scenario: AgentStateManager synchronizes workflow

**Steps:**
```gherkin
Given Agent.workflow is set to Workflow instance
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When AgentStateManager synchronizes workflow
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then AgentStateManager checks if Project has workflow attribute
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And AgentStateManager finds Project has workflow attribute
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And AgentStateManager checks if Project.workflow references same object as Agent.workflow
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And AgentStateManager finds Project.workflow references different object
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And AgentStateManager updates Project.workflow to reference Agent.workflow
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

### Scenario: MCP Server synchronizes project workflow

**Steps:**
```gherkin
Given Agent.workflow is set to Workflow instance
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Project.workflow may reference different object
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When MCP Server synchronizes project workflow
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then MCP Server ensures Project workflow reference matches Agent workflow reference
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And MCP Server checks if Project.workflow references same object as Agent.workflow
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And MCP Server finds Project.workflow references different object
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And MCP Server updates Project.workflow to reference Agent.workflow
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

### Scenario Outline: AI Chat gets instructions for restored action

**Steps:**
```gherkin
Given workflow has been restored with current_behavior_name '<restored_behavior_name>' and current_action_name '<restored_action_name>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When AI Chat calls agent_get_instructions() after project area confirmation and workflow restoration
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then MCP Server calls agent.instructions property
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And agent.instructions property delegates to workflow.current_action.instructions
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And workflow.current_action.instructions returns instructions for '<restored_action_name>' action
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And AI Chat receives instructions for the current action '<restored_action_name>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When user receives instructions for current action
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then user can immediately continue working from where they left off
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And all workflow context (behavior '<restored_behavior_name>', action '<restored_action_name>', previous outputs) is available and ready for continuation
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

**Examples:**
| restored_behavior_name | restored_action_name |
|----------------------|-------------------|
| shape | clarification |
| shape | planning |
| shape | build_structure |
| shape | render_output |
| shape | validate |

### Scenario: Agent starts workflow when state is not restored

**Steps:**
```gherkin
Given workflow._current_stage is not set (no restoration occurred)
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Agent._initialize_components() completes (no workflow state restoration)
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then Agent checks if _needs_project_area()
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent finds project area is confirmed (returns false)
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent calls _start_workflow_if_needed()
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Agent._start_workflow_if_needed() is called
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then Agent checks if workflow._current_stage is already set
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent finds workflow._current_stage is not set
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent starts workflow from beginning (first behavior, first action)
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

