# 📝 Inject Validation Rules for Validate Rules Action

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [Increment 2 AC](../../increment-2-acceptance-criteria-DRAFT.md)

**Epic:** Invoke MCP Bot Server  
**Feature:** Perform Behavior Action

**User:** Bot Behavior  
**Sequential Order:** 14  
**Story Type:** system

## Story Description

Bot Behavior injects validation rules so that AI Chat can validate generated content against common and behavior-specific rules.

## Acceptance Criteria

- **WHEN** MCP Specific Behavior Action Tool invokes Validate Rules Action (7_validate_rules)
- **THEN** Action loads common bot rules from `base_bot/rules/`
- **AND** Action loads behavior-specific rules from `{bot}/behaviors/{behavior}/rules/`
- **AND** Action merges common and behavior-specific rules
- **AND** Action injects rules into validation section of compiled instructions
- **AND** Rules define validation criteria for generated content

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given a bot with name 'test_bot'
And bot instance is preloaded in MCP Server
And generated content exists to validate
```

## Scenarios

### Scenario: Action loads and injects validation rules for exploration

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'exploration'
And behavior has action 'validate_rules'
And action has behavior-specific rules configured
And common bot rules exist
When Tool invokes test_bot.Exploration.ValidateRules() method
Then Action loads common rules from exact path: base_bot/rules/story_structure_rules.json
And Action loads behavior-specific rules from exact path: agile_bot/bots/test_bot/behaviors/exploration/rules/acceptance_criteria_rules.json
And Action merges common rules with behavior-specific rules
And Action injects merged rules into validation section of compiled instructions
And Instructions guide AI Chat to validate acceptance criteria against all rules
And Instructions specify validation criteria: format, coverage, testability
```

### Scenario: Action uses common rules when behavior-specific rules do not exist

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'exploration'
And behavior has action 'validate_rules'
And action does NOT have behavior-specific rules configured
And common bot rules exist
When Tool invokes test_bot.Exploration.ValidateRules() method
Then Action loads common rules from exact path: base_bot/rules/story_structure_rules.json
And Action checks for behavior-specific rules at exact path: agile_bot/bots/test_bot/behaviors/exploration/rules/
And Action injects common rules only into validation section
And Action logs info 'No behavior-specific rules found for exploration, using common rules only'
```

### Scenario: Action handles missing common rules

**Steps:**
```gherkin
Given a bot with name 'test_bot'
And bot has a behavior configured as 'exploration'
And behavior has action 'validate_rules'
And common bot rules do NOT exist
When Tool invokes test_bot.Exploration.ValidateRules() method
Then Action attempts to load from exact path: base_bot/rules/
And Action raises FileNotFoundError with message 'Common bot rules not found at base_bot/rules/'
And Action does not return compiled instructions
And Tool returns error to AI Chat
```

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/increment-2-acceptance-criteria-DRAFT.md  
**Phase**: Specification - Detailed scenario writing from acceptance criteria  
**Date Generated**: 2025-12-03  
**Context**: System-centric scenarios focusing on validation rule loading, merging, and injection.

