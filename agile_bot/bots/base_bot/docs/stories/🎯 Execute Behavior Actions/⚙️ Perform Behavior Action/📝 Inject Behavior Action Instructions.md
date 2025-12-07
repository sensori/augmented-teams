# 📝 Inject Behavior Action Instructions

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Execute Behavior Actions  
**Feature:** Perform Behavior Action

**User:** Bot Behavior  
**Sequential Order:** 1  
**Story Type:** system

**Test File:** test_invoke_bot_tool.py  
**Test Class:** TestBehaviorActionInstructions  
**Test Methods:** 
- test_action_loads_and_merges_instructions

## Story Description

When a tool invokes a Bot.Behavior.Action method, the Behavior Action loads instructions from both the behavior-specific location and the base_actions location, then merges them together. The merged instructions are returned for injection into AI Chat.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** Tool invokes Bot.Behavior.Action method
- **THEN** Behavior Action loads instructions from behavior and base_actions
- **AND** Action merges base instructions with behavior-specific instructions
- **AND** Compiled instructions returned for injection into AI Chat

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Bot is initialized with bot_name and behavior
And Base action instructions exist in base_actions folder
And Behavior-specific action instructions exist in behavior folder
```

## Scenarios

### Scenario: Action loads and merges instructions

**Steps:**
```gherkin
Given Base and behavior-specific instructions exist
When Action method is invoked
Then Instructions are loaded from both locations and merged
And base_instructions field is present in merged instructions
And action field matches the action name
And Merged instructions contain content from both sources
```

**Test Method:** `test_action_loads_and_merges_instructions`

**Test Details:**
- Creates bot config file
- Creates behavior-specific action instructions
- Creates base action instructions
- Instantiates action object (e.g., GatherContextAction)
- Calls load_and_merge_instructions() method
- Verifies base_instructions field is present
- Verifies action field matches action name
- Verifies instructions are merged from both sources

## Test Details

- **Test File:** `test_invoke_bot_tool.py`
- **Test Class:** `TestBehaviorActionInstructions`
- **Test Methods:**
  - `test_action_loads_and_merges_instructions` - Tests loading and merging of instructions from both base and behavior-specific locations

## Implementation Notes

The Behavior Action instruction loading process:
1. Loads base instructions from `base_bot/base_actions/{action_name}/instructions.json`
2. Loads behavior-specific instructions from `{bot_name}/behaviors/{behavior}/{action_name}/instructions.json` (if exists)
3. Merges base instructions with behavior-specific instructions
4. Behavior-specific instructions override/extend base instructions
5. Returns merged instructions dictionary with:
   - `base_instructions` - Base instructions from base_actions
   - `action` - Action name
   - Additional fields from behavior-specific instructions

The merged instructions are then used to provide context and guidance to the AI when executing the behavior action.
