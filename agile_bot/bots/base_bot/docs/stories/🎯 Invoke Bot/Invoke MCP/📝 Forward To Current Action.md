# 📝 Forward To Current Action

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json)

**Epic:** Invoke MCP Bot Server  
**Feature:** Invoke Bot Tool

**User:** AI Chat  
**Sequential Order:** 4  
**Story Type:** system

## Story Description

Behavior tool forwards to current action when workflow state shows current_action within behavior. When workflow state shows different behavior, behavior tool updates workflow to current behavior. When workflow state does NOT exist, behavior tool defaults to first action.

## Acceptance Criteria

- **WHEN** Behavior tool receives invocation
- **AND** workflow state shows current_action within behavior
- **THEN** Behavior tool forwards to current action
- **WHEN** workflow state shows different behavior
- **THEN** Behavior tool updates workflow to current behavior
- **WHEN** workflow state does NOT exist
- **THEN** Behavior tool defaults to first action

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given bot configuration exists
And behavior exists in bot configuration
```

## Scenarios

### Scenario: Behavior tool forwards to current action within behavior

**Steps:**
```gherkin
Given a behavior tool for 'discovery' behavior
And workflow state shows current_action='build_knowledge'
When Behavior tool receives invocation
Then Behavior tool forwards to build_knowledge action
```

### Scenario: Behavior tool sets workflow to current behavior when state shows different behavior

**Steps:**
```gherkin
Given a behavior tool for 'exploration' behavior
And workflow state shows current_behavior='discovery'
When Behavior tool receives invocation
Then workflow state updated to current_behavior='exploration'
```

### Scenario: Behavior tool defaults to first action when state missing

**Steps:**
```gherkin
Given a behavior tool for 'shape' behavior
And workflow state does NOT exist
When Behavior tool receives invocation
Then Behavior tool defaults to first action
```

### Scenario: Action called directly saves workflow state

**Steps:**
```gherkin
Given Bot is initialized with current_project set
And No workflow state exists yet
When Action is called directly (e.g., bot.shape.gather_context())
Then workflow_state.json is created with current_behavior and current_action
```

## Source Material

**Generated from:** Story "Forward To Current Action" in story graph  
**Date:** 2025-12-05  
**Context:** Story for behavior tool forwarding to current action from workflow state

