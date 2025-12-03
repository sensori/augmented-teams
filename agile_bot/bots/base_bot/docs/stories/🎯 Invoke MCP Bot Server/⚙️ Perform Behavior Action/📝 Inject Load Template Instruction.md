# 📝 Inject Load Template Instruction

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [Increment 2 AC](../../increment-2-acceptance-criteria-DRAFT.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Perform Behavior Action

**User:** System  
**Sequential Order:** 11  
**Story Type:** system

## Story Description

System injects template loading instructions so that AI Chat can use templates to structure rendered output.

## Acceptance Criteria

- **WHEN** Render Output Action needs templates
- **THEN** Action injects load template instructions into compiled instructions
- **AND** Instructions specify template file paths
- **AND** Instructions guide AI Chat on how to use templates for rendering

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given a bot with name 'test_bot'
And bot instance is preloaded in MCP Server
```

## Scenarios

### Scenario: Action injects template loading instructions for exploration render

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'exploration'
And behavior has action 'render_output'
And action has template 'story-acceptance-criteria-template.md'
When Tool invokes test_bot.Exploration.RenderOutput() method
Then Action injects load template instructions into compiled instructions
And Instructions specify template file at exact path: agile_bot/bots/test_bot/behaviors/exploration/content/render/templates/story-acceptance-criteria-template.md
And Instructions guide AI Chat to read template file
And Instructions guide AI Chat to use template structure for rendering acceptance criteria
And Instructions describe template placeholders and how to fill them
```

### Scenario: Action handles missing template file

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'exploration'
And behavior has action 'render_output'
And action does NOT have template file
When Tool invokes test_bot.Exploration.RenderOutput() method
Then Action attempts to load from exact path: agile_bot/bots/test_bot/behaviors/exploration/content/render/templates/
And Action raises FileNotFoundError with message 'Template not found for exploration render at agile_bot/bots/test_bot/behaviors/exploration/content/render/templates/'
And Action does not return compiled instructions
And Tool returns error to AI Chat
```

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/increment-2-acceptance-criteria-DRAFT.md  
**Phase**: Specification - Detailed scenario writing from acceptance criteria  
**Date Generated**: 2025-12-03  
**Context**: System-centric scenarios focusing on template loading and usage guidance for rendering structured output.

