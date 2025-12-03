# 📝 Invoke MCP BOT Tool

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [Increment 2 AC](../../increment-2-acceptance-criteria-DRAFT.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Invoke Bot Tool

**User:** AI Chat  
**Sequential Order:** 4  
**Story Type:** system

## Story Description

AI Chat invokes MCP BOT Tool so that bot behavior actions can be executed and instructions can be injected into chat context.

## Acceptance Criteria

### AC 3: Generated Server Self-Initialization

- **WHEN** Generated MCP Server starts up
- **THEN** Server initializes itself in separate thread
- **AND** Server instantiates Specific Bot class from Bot Config
- **AND** Specific Bot loads Behavior configuration from Bot Config

- **WHEN** Generated MCP Server initializes
- **THEN** Server preloads Specific Bot class from Bot Config
- **AND** Bot class remains in memory for duration of server lifecycle
- **AND** All tool invocations use same preloaded bot instance
- **Technical Constraint:** Preload bot once, reuse across all tool invocations

- **WHEN** AI Chat invokes any generated tool
- **THEN** Tool invoke correct behavior action on preloaded bot
- **AND** Invocation completes in < 50ms (lookup + forward to bot)
- **AND** Instructions loaded and injected into AI Chat context
- **AND** Total round-trip time < 200ms
- **Technical Constraint:** Cache instructions in memory, minimize I/O

- **WHEN** MCP tool is called for a (behavior, action) pair
- **THEN** tool directly routes to behavior action method of preloaded Bot class
- **AND** Calls Bot.Behavior.Action with correct parameters
- **AND** Bot.Behavior compiles and returns instructions
- **AND** MCP tool Injects instructions into AI Chat context

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given test_bot MCP Server is deployed and running
And Server has preloaded test_bot Bot class at startup
And Bot class has loaded all behavior configurations
And AI Chat is connected to MCP Protocol Handler
```

## Scenarios

### Scenario: AI Chat invokes test_bot_shape_gather_context tool

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'shape'
And behavior has action 'gather_context'
And action has trigger pattern 'start.*mapping'
And AI Chat receives user input 'start story mapping for my project'
And AI Chat matches input against trigger pattern
When AI Chat invokes tool 'test_bot_shape_gather_context' with parameters: behavior='shape', action='gather_context'
Then Tool uses BaseTool logic to route invocation to preloaded test_bot instance
And Tool calls test_bot.Shape.GatherContext() method
And Shape.GatherContext compiles instructions from exact paths: agile_bot/bots/test_bot/behaviors/shape/gather_context/instructions.json and base_bot/base_actions/gather_context/instructions.json
And Tool receives compiled instructions from Shape.GatherContext
And Tool injects instructions into AI Chat context
And Invocation completes in less than 50ms
And Total round-trip time is less than 200ms
```

### Scenario: Server preloads bot once and reuses across invocations

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has behaviors configured as ['shape', 'discovery', 'exploration', 'specification']
And MCP Server has started up
When Server initializes in separate thread
Then Server reads Bot Config from exact path: agile_bot/bots/test_bot/config/bot_config.json
And Server instantiates test_bot Bot class once
And Bot class loads all behavior configurations: ['shape', 'discovery', 'exploration', 'specification']
And Bot instance remains in memory for server lifecycle
And subsequent tool invocations reuse the same preloaded bot instance
And Server does not re-instantiate Bot class on each tool invocation
```

### Scenario: Tool routes to correct behavior action method

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has behaviors configured as ['shape', 'discovery', 'exploration']
And behavior 'exploration' has action 'build_knowledge'
And preloaded test_bot Bot instance is in memory
When AI Chat invokes tool 'test_bot_exploration_build_knowledge' with parameters: behavior='exploration', action='build_knowledge'
Then Tool directly routes to test_bot.Exploration.BuildKnowledge() method
And Tool does NOT route to test_bot.Shape.BuildKnowledge()
And Tool does NOT route to test_bot.Discovery.BuildKnowledge()
And Correct behavior action method is invoked based on parameters
```

### Scenario: Tool handles missing behavior gracefully

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has behaviors configured as ['shape', 'discovery', 'exploration']
And behavior 'invalid_behavior' does NOT exist in bot configuration
When AI Chat invokes tool 'test_bot_invalid_behavior_gather_context' with parameters: behavior='invalid_behavior', action='gather_context'
Then Tool attempts to route to invalid_behavior
And Tool raises AttributeError with message 'Behavior invalid_behavior not found in test_bot'
And Tool returns error to AI Chat with message 'Invalid behavior requested'
And Instructions are not injected into AI Chat context
```

### Scenario: Tool handles missing action gracefully

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'shape'
And action 'invalid_action' does NOT exist in base actions
When AI Chat invokes tool 'test_bot_shape_invalid_action' with parameters: behavior='shape', action='invalid_action'
Then Tool attempts to route to shape.invalid_action
And Tool raises AttributeError with message 'Action invalid_action not found in base actions'
And Tool returns error to AI Chat with message 'Invalid action requested'
And Instructions are not injected into AI Chat context
```

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/increment-2-acceptance-criteria-DRAFT.md  
**Phase**: Specification - Detailed scenario writing from acceptance criteria  
**Date Generated**: 2025-12-03  
**Context**: System-centric scenarios focusing on tool invocation, bot preloading, and routing to correct behavior action methods.

