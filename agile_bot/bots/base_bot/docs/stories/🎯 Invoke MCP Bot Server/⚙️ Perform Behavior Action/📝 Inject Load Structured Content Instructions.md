# 📝 Inject Load Structured Content Instructions

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [Increment 2 AC](../../increment-2-acceptance-criteria-DRAFT.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Perform Behavior Action

**User:** Bot Behavior  
**Sequential Order:** 9  
**Story Type:** system

## Story Description

Bot Behavior injects load structured content instructions so that AI Chat can read and process previously built knowledge graphs.

## Acceptance Criteria

- **WHEN** Build Knowledge Action needs to load structured content (knowledge graph)
- **THEN** Action injects load structured content instructions into compiled instructions
- **AND** Instructions specify knowledge graph file path to load
- **AND** Instructions guide AI Chat on how to read and process structured content

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given a bot with name 'test_bot'
And bot instance is preloaded in MCP Server
And previously built knowledge graph exists in project
```

## Scenarios

### Scenario: Action injects instructions to load knowledge graph template for shape behavior

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as '1_shape'
And behavior has knowledge graph template 'story-graph-outline.json'
And behavior has build instructions 'instructions.json'
When BuildKnowledge tool is invoked for behavior '1_shape'
Then Action injects load structured content instructions into compiled instructions
And Instructions specify knowledge graph template at exact path: agile_bot/bots/test_bot/behaviors/1_shape/2_content/1_knowlege_graph/story-graph-outline.json
And Instructions specify build instructions at exact path: agile_bot/bots/test_bot/behaviors/1_shape/2_content/1_knowlege_graph/instructions.json
And Instructions guide AI Chat to read story-graph-outline.json using file read tool
And Instructions guide AI Chat to parse JSON structure and use as template for building knowledge graph
And Instructions guide AI Chat to construct new knowledge graph following template structure
```

### Scenario: Action handles missing structured content file

**Steps:**
```gherkin
Given Tool has invoked test_bot.Exploration.BuildKnowledge() method
And expected story graph does NOT exist at agile_bot/bots/base_bot/docs/stories/story-graph.json
When BuildKnowledgeAction injects load instructions
Then Action injects load instructions with file path
And Instructions include fallback guidance if file is missing
And Instructions guide AI Chat to proceed without loaded content or ask user for source material
```

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/increment-2-acceptance-criteria-DRAFT.md  
**Phase**: Specification - Detailed scenario writing from acceptance criteria  
**Date Generated**: 2025-12-03  
**Context**: System-centric scenarios focusing on loading and processing previously built knowledge graphs.

