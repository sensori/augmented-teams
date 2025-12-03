# 📝 Generate Behavior Action Tools

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [Increment 2 AC](../../increment-2-acceptance-criteria-DRAFT.md)

**Epic:** Build Agile Bots  
**Feature:** Generate Bot Server And Tools

**User:** MCP Server Generator  
**Sequential Order:** 2  
**Story Type:** system

## Story Description

MCP Server Generator generates Behavior Action Tools for each (behavior, action) pair so that AI Chat can invoke specific bot actions.

## Acceptance Criteria

- **WHEN** Generator processes Bot Config
- **THEN** Generator creates tool code for each (behavior, action) pair:
  - **AND** Enumerates all behaviors and actions from Bot Config (2_gather_context, 3_decide_planning_criteria, 4_build_knowledge, 5_render_output, 6_correct_bot, 7_validate_rules)
  - **AND** For each pair, generates tool code that:
    - **AND** Has unique name: `{bot_name}_{behavior}_{action}`
    - **AND** Loads trigger words from `{bot}/behaviors/{behavior}/{action}/trigger_words.json`
    - **Example:** story_bot with 4 behaviors × 6 base actions = 24 tool instances to generate
    - **AND** Annotates tool with trigger words for lookup
    - **AND** Forwards invocation to Bot + Behavior + Action
    - **AND** Loads instructions and injects into AI Chat
- **Tool catalog** prepared with all generated tool instances

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given MCP Bot Server Generator is initialized
And base tool template code exists in base_bot/src/base_tool.py
And base action definitions exist in base_bot/base_actions/
```

## Scenarios

### Scenario: Generator creates tools for test_bot with 4 behaviors

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has 4 behaviors configured as ['shape', 'discovery', 'exploration', 'specification']
And each behavior has 6 base actions configured
When Generator processes Bot Config
Then Generator enumerates 24 (behavior, action) pairs (4 behaviors × 6 actions)
And Generator creates 24 tool instances with unique names
And tool 'test_bot_shape_gather_context' is created with trigger words from exact path: agile_bot/bots/test_bot/behaviors/shape/gather_context/trigger_words.json
And tool 'test_bot_discovery_build_knowledge' is created with trigger words from exact path: agile_bot/bots/test_bot/behaviors/discovery/build_knowledge/trigger_words.json
And each tool includes forwarding logic to invoke Bot.Behavior.Action
And Tool catalog contains all 24 generated tool instances
```

### Scenario: Generator loads trigger words from behavior folder

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'shape'
And behavior has action 'gather_context'
And action has trigger_words.json with patterns: ["shape.*story", "start.*mapping", "story.*discovery"]
When Generator creates tool for (shape, gather_context) pair
Then Generator loads trigger words from exact path: agile_bot/bots/test_bot/behaviors/shape/gather_context/trigger_words.json
And Generated tool is annotated with trigger patterns: ["shape.*story", "start.*mapping", "story.*discovery"]
And AI Chat can match user input against these patterns to discover the tool
```

### Scenario: Generator handles missing trigger words file

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'shape'
And behavior has action 'gather_context'
And action does NOT have trigger_words.json
When Generator creates tool for (shape, gather_context) pair
Then Generator attempts to load from exact path: agile_bot/bots/test_bot/behaviors/shape/gather_context/trigger_words.json
And Generator uses empty trigger word list for that tool
And Generator logs warning 'Missing trigger words for test_bot_shape_gather_context'
And Tool is still created with forwarding logic but no trigger patterns
```

### Scenario: Generator creates tool with forwarding logic

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'shape'
And behavior has action 'gather_context'
When Generator creates tool 'test_bot_shape_gather_context'
Then Generated tool includes method to forward invocation to Bot.Shape.GatherContext
And Generated tool includes method to load instructions from exact path: agile_bot/bots/test_bot/behaviors/shape/gather_context/instructions.json
And Generated tool includes method to inject instructions into AI Chat context
```

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/increment-2-acceptance-criteria-DRAFT.md  
**Phase**: Specification - Detailed scenario writing from acceptance criteria  
**Date Generated**: 2025-12-03  
**Context**: System-centric scenarios focusing on Behavior Action Tool generation with trigger word loading and forwarding logic.

