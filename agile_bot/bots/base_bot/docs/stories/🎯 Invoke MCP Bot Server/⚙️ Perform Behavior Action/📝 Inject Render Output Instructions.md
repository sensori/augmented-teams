# 📝 Inject Render Output Instructions

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [Increment 2 AC](../../increment-2-acceptance-criteria-DRAFT.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Perform Behavior Action

**User:** Bot Behavior  
**Sequential Order:** 12  
**Story Type:** system

## Story Description

Bot Behavior injects render output instructions so that AI Chat can generate final formatted output from knowledge graph.

## Acceptance Criteria

- **WHEN** Render Output Action (5_render_output) compiles instructions
- **THEN** Action injects render output instructions into compiled instructions
- **AND** Action includes templates from `{bot}/behaviors/{behavior}/content/render/templates/`
- **AND** Action includes transformer methods from `{bot}/behaviors/{behavior}/content/render/transformers/`
- **AND** Action includes render spec paths
- **AND** Instructions guide how to render final output

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given a bot with name 'test_bot'
And bot instance is preloaded in MCP Server
And templates, transformers, and knowledge graph are available
```

## Scenarios

### Scenario: Action compiles complete render instructions for exploration

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'exploration'
And behavior has action 'render_output'
And action has template 'story-acceptance-criteria-template.md'
And action has render spec 'render_spec.json'
And knowledge graph exists in project
When Tool invokes test_bot.Exploration.RenderOutput() method
Then Action injects render output instructions into compiled instructions
And Instructions include template at exact path: agile_bot/bots/test_bot/behaviors/exploration/content/render/templates/story-acceptance-criteria-template.md
And Instructions include render spec at exact path: agile_bot/bots/test_bot/behaviors/exploration/content/render/render_spec.json
And Instructions guide AI Chat to: load knowledge graph, apply transformers, use template, generate output
And Compiled instructions provide complete rendering workflow guidance
```

### Scenario: Action handles incomplete render components

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'exploration'
And behavior has action 'render_output'
And action has template but does NOT have transformers
When Tool invokes test_bot.Exploration.RenderOutput() method
Then Action injects render instructions with available components only
And Instructions include template at exact path: agile_bot/bots/test_bot/behaviors/exploration/content/render/templates/story-acceptance-criteria-template.md
And Instructions guide AI Chat to render using template without transformations
And Action logs warning 'Rendering without transformers for exploration'
```

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/increment-2-acceptance-criteria-DRAFT.md  
**Phase**: Specification - Detailed scenario writing from acceptance criteria  
**Date Generated**: 2025-12-03  
**Context**: System-centric scenarios focusing on complete render workflow including templates, transformers, and specs.

