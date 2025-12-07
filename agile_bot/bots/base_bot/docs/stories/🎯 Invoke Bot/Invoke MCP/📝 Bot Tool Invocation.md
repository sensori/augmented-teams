# 📝 Bot Tool Invocation

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json)

**Epic:** Invoke MCP Bot Server  
**Feature:** Invoke Bot Tool

**User:** AI Chat  
**Sequential Order:** 1  
**Story Type:** system

## Story Description

AI Chat invokes bot tool with behavior and action parameters so that the tool routes to the correct behavior.action method, executes the action, and returns the result. When AI Chat invokes a tool for a specific behavior, the tool routes to that behavior only, not other behaviors.

## Acceptance Criteria

- **WHEN** AI Chat invokes bot tool with behavior and action parameters
- **THEN** Tool routes to correct behavior.action method
- **AND** Tool executes action and returns result
- **WHEN** AI Chat invokes tool for specific behavior
- **THEN** Tool routes to that behavior only, not other behaviors

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given bot configuration exists
And behavior and action exist in bot configuration
```

## Scenarios

### Scenario: Tool invokes behavior action when called

**Steps:**
```gherkin
Given Bot has behavior 'shape' with action 'gather_context'
When AI Chat invokes tool with parameters
Then Tool routes to test_bot.Shape.GatherContext() method
And Tool executed and returned result
```

### Scenario: Tool routes to correct behavior action method

**Steps:**
```gherkin
Given Bot has multiple behaviors with build_knowledge action
When AI Chat invokes 'test_bot_exploration_build_knowledge'
Then Tool routes to test_bot.Exploration.BuildKnowledge() not other behaviors
And Routes to exploration behavior only
```

## Source Material

**Generated from:** Story "Bot Tool Invocation" in story graph  
**Date:** 2025-12-05  
**Context:** Foundational MCP tool invocation story for routing to behavior.action methods

