# 📝 Inject Knowledge Graph Template for Build Knowledge

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [Increment 2 AC](../../increment-2-acceptance-criteria-DRAFT.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Perform Behavior Action

**User:** Bot Behavior  
**Sequential Order:** 8  
**Story Type:** system

## Story Description

Bot Behavior injects knowledge graph template and build instructions so that AI Chat can construct structured knowledge from context.

## Acceptance Criteria

- **WHEN** MCP Specific Behavior Action Tool invokes Build Knowledge Action (4_build_knowledge)
- **THEN** Action loads knowledge graph template from `{bot}/behaviors/{behavior}/content/knowledge_graph/`
- **AND** Action loads build instructions from knowledge graph spec files
- **AND** Action injects knowledge graph template path and build instructions into compiled instructions
- **AND** Action injects validation rules reference (see Story 10: Inject Validation Rules)

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given a bot with name 'test_bot'
And bot instance is preloaded in MCP Server
```

## Scenarios

### Scenario: Action loads and injects knowledge graph template for exploration

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'exploration'
And behavior has action 'build_knowledge'
And action has knowledge graph template 'story-graph-explored-outline.json'
And action has build instructions 'build_instructions.md'
When Tool invokes test_bot.Exploration.BuildKnowledge() method
Then Action loads knowledge graph template from exact path: agile_bot/bots/test_bot/behaviors/exploration/content/knowledge_graph/story-graph-explored-outline.json
And Action loads build instructions from exact path: agile_bot/bots/test_bot/behaviors/exploration/content/knowledge_graph/build_instructions.md
And Action injects knowledge graph template path into compiled instructions
And Action injects build instructions into compiled instructions
And Action injects validation rules reference for exploration knowledge graph
And Compiled instructions guide AI Chat to construct story graph following template structure
```

### Scenario: Action handles missing knowledge graph template

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'exploration'
And behavior has action 'build_knowledge'
And action does NOT have knowledge graph template
When Tool invokes test_bot.Exploration.BuildKnowledge() method
Then Action attempts to load from exact path: agile_bot/bots/test_bot/behaviors/exploration/content/knowledge_graph/
And Action raises FileNotFoundError with message 'Knowledge graph template not found for exploration at agile_bot/bots/test_bot/behaviors/exploration/content/knowledge_graph/'
And Action does not return compiled instructions
And Tool returns error to AI Chat
```

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/increment-2-acceptance-criteria-DRAFT.md  
**Phase**: Specification - Detailed scenario writing from acceptance criteria  
**Date Generated**: 2025-12-03  
**Context**: System-centric scenarios focusing on knowledge graph template injection and build instruction loading.

