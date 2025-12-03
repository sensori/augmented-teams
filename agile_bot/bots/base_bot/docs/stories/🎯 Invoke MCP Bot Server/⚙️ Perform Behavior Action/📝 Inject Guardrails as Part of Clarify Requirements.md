# 📝 Inject Guardrails as Part of Clarify Requirements

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [Increment 2 AC](../../increment-2-acceptance-criteria-DRAFT.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Perform Behavior Action

**User:** Bot Behavior  
**Sequential Order:** 6  
**Story Type:** system

## Story Description

Bot Behavior injects guardrails (key questions and evidence) so that AI Chat knows what context to gather from the user.

## Acceptance Criteria

- **WHEN** MCP Specific Behavior Action Tool invokes Gather Context Action (2_gather_context)
- **THEN** Action checks for guardrails in `{bot}/behaviors/{behavior}/guardrails/required_context/`
- **WHEN** guardrails exist
- **THEN** Action loads key_questions.json and evidence.json
- **AND** Action injects guardrails into clarify requirements section of compiled instructions
- **WHEN** no guardrails exist
- **THEN** Action injects base clarification instructions only

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given a bot with name 'test_bot'
And bot instance is preloaded in MCP Server
```

## Scenarios

### Scenario: Action loads and injects guardrails for shape gather_context

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'shape'
And behavior has action 'gather_context'
And action has guardrails configured with key_questions.json and evidence.json
When Tool invokes test_bot.Shape.GatherContext() method
Then Action loads key_questions.json from exact path: agile_bot/bots/test_bot/behaviors/shape/guardrails/required_context/key_questions.json
And Action loads evidence.json from exact path: agile_bot/bots/test_bot/behaviors/shape/guardrails/required_context/evidence.json
And Action injects key questions into clarify requirements section of compiled instructions
And Action injects required evidence into clarify requirements section
And Compiled instructions include both base clarification and behavior-specific guardrails
```

### Scenario: Action uses base instructions when guardrails do not exist

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'shape'
And behavior has action 'gather_context'
And action does NOT have guardrails configured
When Tool invokes test_bot.Shape.GatherContext() method
Then Action checks for guardrails at exact path: agile_bot/bots/test_bot/behaviors/shape/guardrails/required_context/
And Action does not find guardrails folder
And Action injects base clarification instructions only
And Compiled instructions do not include behavior-specific key questions or evidence
And Action logs info 'No guardrails found for shape/gather_context, using base instructions only'
```

### Scenario: Action handles malformed guardrails JSON

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'shape'
And behavior has action 'gather_context'
And action has guardrails configured but key_questions.json has invalid JSON syntax
When Tool invokes test_bot.Shape.GatherContext() method
Then Action attempts to load from exact path: agile_bot/bots/test_bot/behaviors/shape/guardrails/required_context/key_questions.json
And Action raises JSONDecodeError with message 'Malformed key_questions.json for shape/gather_context at agile_bot/bots/test_bot/behaviors/shape/guardrails/required_context/key_questions.json'
And Action does not inject guardrails
And Action falls back to base clarification instructions only
```

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/increment-2-acceptance-criteria-DRAFT.md  
**Phase**: Specification - Detailed scenario writing from acceptance criteria  
**Date Generated**: 2025-12-03  
**Context**: System-centric scenarios focusing on guardrail loading and injection for context gathering.

