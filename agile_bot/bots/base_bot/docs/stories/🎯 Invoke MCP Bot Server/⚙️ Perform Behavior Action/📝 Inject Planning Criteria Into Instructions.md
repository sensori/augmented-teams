# 📝 Inject Planning Criteria Into Instructions

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [Increment 2 AC](../../increment-2-acceptance-criteria-DRAFT.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Perform Behavior Action

**User:** Bot Behavior  
**Sequential Order:** 7  
**Story Type:** system

## Story Description

Bot Behavior injects planning criteria (assumptions and decision criteria) so that AI Chat can guide user through planning decisions.

## Acceptance Criteria

- **WHEN** MCP Specific Behavior Action Tool invokes Planning Action (3_decide_planning_criteria)
- **THEN** Action checks for guardrails in `{bot}/behaviors/{behavior}/guardrails/planning/`
- **WHEN** guardrails exist
- **THEN** Action loads typical_assumptions.json and decision_criteria/*.json files
- **AND** Action injects planning guardrails into planning section of compiled instructions
- **WHEN** no guardrails exist
- **THEN** Action injects base planning instructions only

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given a bot with name 'test_bot'
And bot instance is preloaded in MCP Server
```

## Scenarios

### Scenario: Action loads and injects planning criteria for exploration

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'exploration'
And behavior has action 'decide_planning_criteria'
And action has planning guardrails configured with typical_assumptions.json and decision_criteria files
When Tool invokes test_bot.Exploration.DecidePlanningCriteria() method
Then Action loads typical_assumptions.json from exact path: agile_bot/bots/test_bot/behaviors/exploration/guardrails/planning/typical_assumptions.json
And Action loads decision_criteria files from exact path: agile_bot/bots/test_bot/behaviors/exploration/guardrails/planning/decision_criteria/
And Action injects assumptions into planning section of compiled instructions
And Action injects decision criteria options into planning section
And Compiled instructions include both base planning and behavior-specific guardrails
```

### Scenario: Action uses base planning instructions when guardrails do not exist

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'exploration'
And behavior has action 'decide_planning_criteria'
And action does NOT have planning guardrails configured
When Tool invokes test_bot.Exploration.DecidePlanningCriteria() method
Then Action checks for guardrails at exact path: agile_bot/bots/test_bot/behaviors/exploration/guardrails/planning/
And Action does not find guardrails folder
And Action injects base planning instructions only
And Compiled instructions do not include behavior-specific assumptions or decision criteria
And Action logs info 'No planning guardrails found for exploration, using base instructions only'
```

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/increment-2-acceptance-criteria-DRAFT.md  
**Phase**: Specification - Detailed scenario writing from acceptance criteria  
**Date Generated**: 2025-12-03  
**Context**: System-centric scenarios focusing on planning criteria and assumption injection.

