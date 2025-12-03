# 📝 Inject Load Transformer Methods Instruction

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [Increment 2 AC](../../increment-2-acceptance-criteria-DRAFT.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Perform Behavior Action

**User:** Bot Behavior  
**Sequential Order:** 10  
**Story Type:** system

## Story Description

Bot Behavior injects transformer method loading instructions so that AI Chat can apply transformations to structured content before rendering.

## Acceptance Criteria

- **WHEN** Render Output Action needs transformer methods
- **THEN** Action injects load transformer methods instructions into compiled instructions
- **AND** Instructions specify transformer file paths
- **AND** Instructions guide AI Chat on how to apply transformations

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given a bot with name 'test_bot'
And bot instance is preloaded in MCP Server
```

## Scenarios

### Scenario: Action injects transformer loading instructions for exploration render

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'exploration'
And behavior has action 'render_output'
And action has transformer methods 'story_graph_transformers.py'
When Tool invokes test_bot.Exploration.RenderOutput() method
Then Action injects load transformer methods instructions into compiled instructions
And Instructions specify transformer file at exact path: agile_bot/bots/test_bot/behaviors/exploration/content/render/transformers/story_graph_transformers.py
And Instructions guide AI Chat to import transformer functions
And Instructions guide AI Chat to apply transformers to knowledge graph before rendering
And Instructions describe available transformer methods and their purposes
```

### Scenario: Action handles missing transformer methods

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'exploration'
And behavior has action 'render_output'
And action does NOT have transformer methods
When Tool invokes test_bot.Exploration.RenderOutput() method
Then Action checks for transformers at exact path: agile_bot/bots/test_bot/behaviors/exploration/content/render/transformers/
And Action injects load transformer instructions with fallback guidance
And Instructions guide AI Chat to proceed with rendering without transformations
And Action logs warning 'No transformer methods found for exploration render'
```

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/increment-2-acceptance-criteria-DRAFT.md  
**Phase**: Specification - Detailed scenario writing from acceptance criteria  
**Date Generated**: 2025-12-03  
**Context**: System-centric scenarios focusing on transformer method loading for content transformation before rendering.

