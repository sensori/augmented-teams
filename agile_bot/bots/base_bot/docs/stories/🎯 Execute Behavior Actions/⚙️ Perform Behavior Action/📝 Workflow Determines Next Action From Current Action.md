# 📝 Workflow Determines Next Action From Current Action

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json)

**Epic:** Execute Behavior Actions  
**Feature:** Perform Behavior Action

**User:** Bot Behavior  
**Sequential Order:** 9  
**Story Type:** system  
**Test File:** test_workflow_action_sequence.py

## Story Description

Bot Behavior determines next action from workflow state so that workflow can resume from the correct action after interruption or restart, using current_action as the source of truth.

## Acceptance Criteria

- **WHEN** Workflow loads state from workflow_state.json
- **THEN** Workflow uses current_action as source of truth
- **AND** Workflow extracts action name from current_action field (format: bot.behavior.action)
- **AND** Workflow falls back to completed_actions if current_action is missing or invalid
- **AND** Workflow determines next uncompleted action from completed_actions when current_action unavailable
- **AND** Workflow starts at first action when no workflow_state.json file exists
- **AND** Workflow handles missing workflow_state.json file gracefully

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given bot configuration exists at "<bot_config_path>"
And workspace root is set to "<workspace_root>"
And workflow state machine has states: [initialize_project, gather_context, decide_planning_criteria, build_knowledge, render_output, validate_rules]
```

## Scenario Outlines

### Scenario Outline: Workflow determines next action from current_action (source of truth)

**Steps:**
```gherkin
Given workflow_state.json shows: current_action='<current_action>'
And current_action format is '<bot_name>.<behavior>.<action_name>'
When Workflow loads state
Then Workflow uses current_action='<current_action>' as source of truth
And Workflow extracts action name '<action_name>' from current_action field
And Workflow sets current_state='<action_name>'
And Workflow does NOT use completed_actions to override current_action
```

**Examples:**
- current_action='story_bot.shape.build_knowledge', action_name='build_knowledge'
- current_action='story_bot.discovery.render_output', action_name='render_output'
- current_action='story_bot.exploration.validate_rules', action_name='validate_rules'

**Test Method:** test_workflow_determines_next_action_from_current_action

### Scenario Outline: Workflow starts at first action when current_action missing and no completed_actions

**Steps:**
```gherkin
Given workflow_state.json has empty current_action=''
And workflow_state.json has empty completed_actions=[]
When Workflow loads state
Then Workflow determines current_state is first action in sequence
And Workflow sets current_state='initialize_project'
```

**Test Method:** test_workflow_starts_at_first_action_when_no_completed_actions

### Scenario Outline: Workflow falls back to completed_actions when current_action missing

**Steps:**
```gherkin
Given workflow_state.json has empty current_action=''
And completed_actions=[<completed_action_1>, <completed_action_2>]
When Workflow loads state
Then Workflow uses completed_actions as fallback
And Workflow determines next uncompleted action
And Workflow sets current_state='<next_action>'
```

**Examples:**
- completed_action_1='initialize_project', completed_action_2='gather_context', next_action='decide_planning_criteria'
- completed_action_1='gather_context', completed_action_2='decide_planning_criteria', next_action='build_knowledge'

**Test Method:** test_workflow_falls_back_to_completed_actions_when_current_action_missing

### Scenario Outline: Workflow uses current_action when provided (ignores completed_actions)

**Steps:**
```gherkin
Given workflow_state.json shows current_action='<current_action>'
And completed_actions=[<completed_action>] (behind)
When Workflow loads state
Then Workflow uses current_action='<current_action>' as source of truth
And Workflow sets current_state='<action_name>'
And Workflow does NOT use completed_actions to override
```

**Examples:**
- current_action='story_bot.shape.decide_planning_criteria', completed_action='initialize_project', action_name='decide_planning_criteria'
- current_action='story_bot.discovery.render_output', completed_action='gather_context', action_name='render_output'

**Test Method:** test_workflow_uses_current_action_when_provided

### Scenario Outline: Workflow starts at first action when workflow_state.json missing

**Steps:**
```gherkin
Given workflow_state.json file does NOT exist
And current_project.json exists
When Workflow is created
Then Workflow creates new workflow state
And Workflow sets current_state to first action
And Workflow initializes empty completed_actions list
```

**Test Method:** test_workflow_starts_at_first_action_when_no_workflow_state_file_exists

## Source Material

**Primary Source:** Workflow state management requirements  
**Date Generated:** 2025-12-06  
**Context:** Updated to use current_action as source of truth instead of completed_actions




