# 📝 Load Correct Bot Instructions

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [Increment 2 AC](../../increment-2-acceptance-criteria-DRAFT.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Perform Behavior Action

**User:** Bot Behavior  
**Sequential Order:** 15  
**Story Type:** system

## Story Description

Bot Behavior loads and injects correction instructions so that AI Chat can review validation results and suggest corrections to generated content.

## Acceptance Criteria

- **WHEN** MCP Specific Behavior Action Tool invokes Correct Bot Action (6_correct_bot)
- **THEN** Action loads correct bot instructions from `base_bot/base_actions/6_correct_bot/instructions.json`
- **AND** Action injects correction instructions into compiled instructions
- **AND** Instructions guide how to review and correct generated content

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given a bot with name 'test_bot'
And bot instance is preloaded in MCP Server
And validation has been performed with diagnostic results available
```

## Scenarios

### Scenario: Action loads and injects correction instructions after validation

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'exploration'
And behavior has action 'correct_bot'
And validation has produced diagnostic results showing 3 rule violations
When Tool invokes test_bot.Exploration.CorrectBot() method
Then Action loads correct bot instructions from exact path: base_bot/base_actions/6_correct_bot/instructions.json
And Action injects correction instructions into compiled instructions
And Action injects diagnostic results showing 3 violations
And Instructions guide AI Chat to review violations and suggest corrections
And Instructions guide AI Chat to present corrections to user for approval
And Instructions guide AI Chat to apply approved corrections to content
```

### Scenario: Action handles missing correction instructions

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'exploration'
And behavior has action 'correct_bot'
And correct bot instructions do NOT exist
When Tool invokes test_bot.Exploration.CorrectBot() method
Then Action attempts to load from exact path: base_bot/base_actions/6_correct_bot/instructions.json
And Action raises FileNotFoundError with message 'Correct bot instructions not found at base_bot/base_actions/6_correct_bot/instructions.json'
And Action does not return compiled instructions
And Tool returns error to AI Chat
```

### Scenario: Action injects diagnostic results with correction instructions

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'exploration'
And behavior has action 'correct_bot'
And validation has identified 3 violations: ["AC format incorrect", "Missing edge cases", "Ambiguous wording"]
When Tool invokes test_bot.Exploration.CorrectBot() method
Then Action loads diagnostic results from validation
And Action loads correct bot instructions from exact path: base_bot/base_actions/6_correct_bot/instructions.json
And Action injects diagnostic results into compiled instructions
And Instructions include specific violation details for each of the 3 issues
And Instructions guide AI Chat to address each violation systematically
And Instructions guide AI Chat to suggest specific corrections for each violation
```

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/increment-2-acceptance-criteria-DRAFT.md  
**Phase**: Specification - Detailed scenario writing from acceptance criteria  
**Date Generated**: 2025-12-03  
**Context**: System-centric scenarios focusing on correction instruction loading and diagnostic result injection.

