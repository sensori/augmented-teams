# 📝 Forward To Current Behavior and Current Action

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json)

**Epic:** Invoke MCP Bot Server  
**Feature:** Invoke Bot Tool

**User:** AI Chat  
**Sequential Order:** 3  
**Story Type:** system

## Story Description

Bot tool forwards to current behavior and current action when workflow state shows current_behavior and current_action. When workflow state does NOT exist, bot tool defaults to first behavior and first action.

## Acceptance Criteria

- **WHEN** Bot tool receives invocation
- **AND** workflow state shows current_behavior and current_action
- **THEN** Bot tool forwards to correct behavior and action
- **WHEN** workflow state does NOT exist
- **THEN** Bot tool defaults to first behavior and first action

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given bot configuration exists
```

## Scenarios

### Scenario: Bot tool forwards to current behavior and current action

**Steps:**
```gherkin
Given workflow state shows current_behavior='discovery', current_action='build_knowledge'
When Bot tool receives invocation
Then Bot tool forwards to correct behavior and action
```

### Scenario: Bot tool defaults to first behavior and first action when state missing

**Steps:**
```gherkin
Given workflow state does NOT exist
When Bot tool receives invocation
Then Bot tool defaults to first behavior and first action
```

## Source Material

**Generated from:** Story "Forward To Current Behavior and Current Action" in story graph  
**Date:** 2025-12-05  
**Context:** Story for bot tool forwarding to current behavior and action from workflow state

