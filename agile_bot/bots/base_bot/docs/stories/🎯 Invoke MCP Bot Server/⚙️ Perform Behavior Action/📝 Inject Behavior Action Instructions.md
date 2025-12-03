# 📝 Inject Behavior Action Instructions

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [Increment 2 AC](../../increment-2-acceptance-criteria-DRAFT.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Perform Behavior Action

**User:** Bot Behavior  
**Sequential Order:** 5  
**Story Type:** system

## Story Description

Bot Behavior injects compiled behavior action instructions so that AI Chat receives guidance on how to execute the requested action.

## Acceptance Criteria

- **WHEN** Tool invokes Bot.Behavior.Action method
- **THEN** Behavior Action loads instructions from `{bot}/behaviors/{behavior}/{action}/instructions.json`
- **AND** Behavior Action loads instructions from `base_bot/base_actions/{action}/instructions.json`
- **AND** Action merges base instructions with behavior-specific instructions
- **AND** Compiled instructions returned for injection into AI Chat
- **AND** Behavior Action compiles instructions with behavior-specific context
- **AND** Behavior Action returns compiled instructions to tool

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given a bot with name 'test_bot'
And bot instance is preloaded in MCP Server
And base action instructions exist in base_bot/base_actions/
And behavior-specific instructions exist for the bot
```

## Scenarios

### Scenario: Action loads and merges instructions for shape gather_context

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'shape'
And behavior has action 'gather_context'
And action has instructions.json
When Tool invokes test_bot.Shape.GatherContext() method
Then Action loads base instructions from exact path: base_bot/base_actions/2_gather_context/instructions.json
And Action loads behavior instructions from exact path: agile_bot/bots/test_bot/behaviors/shape/2_gather_context/instructions.json
And Action merges base instructions with behavior-specific instructions
And Merged instructions include base action steps and shape-specific context
And Action returns compiled instructions to Tool
And Tool injects compiled instructions into AI Chat context
```

### Scenario: Action handles missing behavior-specific instructions

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'shape'
And behavior has action 'gather_context'
And action does NOT have instructions.json
When Tool invokes test_bot.Shape.GatherContext() method
Then Action loads base instructions from exact path: base_bot/base_actions/2_gather_context/instructions.json
And Action attempts to load behavior instructions from exact path: agile_bot/bots/test_bot/behaviors/shape/2_gather_context/instructions.json
And Action logs warning 'Missing behavior-specific instructions for shape/gather_context'
And Action returns base instructions only (no behavior-specific merge)
And Tool injects base instructions into AI Chat context
```

### Scenario: Action handles missing base instructions

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'shape'
And behavior has action 'gather_context'
And base action instructions do NOT exist
When Tool invokes test_bot.Shape.GatherContext() method
Then Action attempts to load from exact path: base_bot/base_actions/2_gather_context/instructions.json
And Action raises FileNotFoundError with message 'Base instructions not found for action gather_context at base_bot/base_actions/2_gather_context/instructions.json'
And Action does not return compiled instructions
And Tool returns error to AI Chat
```

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/increment-2-acceptance-criteria-DRAFT.md  
**Phase**: Specification - Detailed scenario writing from acceptance criteria  
**Date Generated**: 2025-12-03  
**Context**: System-centric scenarios focusing on instruction loading, merging base and behavior-specific instructions.

