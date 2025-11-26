# 📝 Restore Workflow State

**Navigation:** [📋 Story Map](../../story-agent-story-map.md) | [⚙️ Feature Overview](../../continue-existing-project-exploration.md)

**Epic:** Start Story Development Session
**Feature:** Continue Existing Project

## Story Description

Agent loads configuration and behaviors after project area confirmation, Workflow loads workflow_state.json from project_area/docs/workflow_state.json, and Agent restores workflow to last action (current_behavior_name and current_action_name) from saved state

## Acceptance Criteria

### Behavioral Acceptance Criteria

- When Agent loads configuration and behaviors after project area confirmation, then Agent calls _initialize_components() which creates Workflow instance, sets workflow._behaviors to behaviors dictionary, calls workflow._derive_stages_from_behaviors() to set up stages, and calls _restore_workflow_state()
- When Workflow initializes, then Workflow calls _load_state() which checks if project_area/docs/workflow_state.json exists, and if found reads state file and extracts current_behavior_name and current_action_name into workflow._workflow_state dictionary
- When Agent._restore_workflow_state() is called, then Agent checks if workflow.workflow_state contains current_behavior_name, and if not found returns early (no restoration needed)
- When workflow state contains current_behavior_name, then Agent validates behavior_name exists in behaviors dictionary, sets workflow._current_stage to behavior_name, gets behavior from behaviors dictionary, and extracts current_action_name from workflow state
- When Agent has behavior and action_name, then Agent validates action_name exists in behavior.actions, calls behavior.actions.move_to_action(action_name, force=True) to get action object, and if action found sets workflow._current_action to action object
- When workflow state is successfully restored, then workflow._current_stage and workflow._current_action are set to last saved values, allowing workflow to resume from exact point where user left off

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Agent is initialized with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L404)
And Project has been initialized and project area has been confirmed
  [🔗](../../../../../../src/stories_acceptance_tests.py#L585)
And Agent has loaded base and Story Agent configurations
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

## Scenarios

### Scenario Outline: Workflow state is successfully restored

**Steps:**
```gherkin
Given workflow_state.json exists at '<project_area>/docs/workflow_state.json' with current_behavior_name='<saved_behavior_name>' and current_action_name='<saved_action_name>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Agent loads configuration and behaviors after project area confirmation
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then Agent calls _initialize_components()
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent creates Workflow instance
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent sets workflow._behaviors to behaviors dictionary
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent calls workflow._derive_stages_from_behaviors() to set up stages
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent calls _restore_workflow_state()
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Workflow initializes
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then Workflow calls _load_state()
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Workflow checks if '<project_area>/docs/workflow_state.json' exists
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Workflow finds workflow_state.json exists
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Workflow reads state file and extracts current_behavior_name '<saved_behavior_name>' and current_action_name '<saved_action_name>' into workflow._workflow_state dictionary
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Agent._restore_workflow_state() is called
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then Agent checks if workflow.workflow_state contains current_behavior_name
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent finds current_behavior_name '<saved_behavior_name>' in workflow state
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent validates behavior_name '<saved_behavior_name>' exists in behaviors dictionary
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent sets workflow._current_stage to '<saved_behavior_name>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent gets behavior '<saved_behavior_name>' from behaviors dictionary
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent extracts current_action_name '<saved_action_name>' from workflow state
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Agent has behavior and action_name
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then Agent validates action_name '<saved_action_name>' exists in behavior.actions
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent calls behavior.actions.move_to_action('<saved_action_name>', force=True) to get action object
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent finds action object
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent sets workflow._current_action to action object
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When workflow state is successfully restored
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then workflow._current_stage is set to '<saved_behavior_name>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And workflow._current_action is set to '<saved_action_name>'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And workflow can resume from exact point where user left off
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

**Examples:**
| project_area | saved_behavior_name | saved_action_name |
|-------------|-------------------|------------------|
| test_data/projects/my-story-project | shape | clarification |
| test_data/projects/my-story-project | shape | planning |
| test_data/projects/my-story-project | shape | build_structure |
| test_data/projects/my-story-project | shape | render_output |
| test_data/projects/my-story-project | shape | validate |

### Scenario: Workflow state file does not exist

**Steps:**
```gherkin
Given workflow_state.json does not exist at '<project_area>/docs/workflow_state.json'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Workflow initializes
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then Workflow calls _load_state()
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Workflow checks if '<project_area>/docs/workflow_state.json' exists
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Workflow finds workflow_state.json does not exist
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Workflow sets workflow._workflow_state to empty dictionary
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Agent._restore_workflow_state() is called
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then Agent checks if workflow.workflow_state contains current_behavior_name
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent finds no current_behavior_name in workflow state
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent returns early (no restoration needed)
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
```

### Scenario: Workflow state contains invalid behavior_name

**Steps:**
```gherkin
Given workflow_state.json exists at '<project_area>/docs/workflow_state.json' with current_behavior_name='invalid_behavior' and current_action_name='clarification'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Agent._restore_workflow_state() is called
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then Agent checks if workflow.workflow_state contains current_behavior_name
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent finds current_behavior_name 'invalid_behavior' in workflow state
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent validates behavior_name 'invalid_behavior' exists in behaviors dictionary
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent finds behavior_name 'invalid_behavior' does not exist in behaviors dictionary
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent returns early (no restoration needed)
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
```

### Scenario: Workflow state contains invalid action_name

**Steps:**
```gherkin
Given workflow_state.json exists at '<project_area>/docs/workflow_state.json' with current_behavior_name='shape' and current_action_name='invalid_action'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Agent._restore_workflow_state() is called
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then Agent validates behavior_name 'shape' exists in behaviors dictionary
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent sets workflow._current_stage to 'shape'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent gets behavior 'shape' from behaviors dictionary
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent extracts current_action_name 'invalid_action' from workflow state
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
When Agent has behavior and action_name
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
Then Agent validates action_name 'invalid_action' exists in behavior.actions
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent finds action_name 'invalid_action' does not exist in behavior.actions
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And Agent returns early (no restoration needed)
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1405)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
```

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

