# [Story] Detect Trigger Words Through Extension

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Invoke Bot  
**Sub Epic:** Invoke CLI
**User:** Human  
**Sequential Order:** 5  
**Story Type:** user

## Story Description

Detect Trigger Words Through Extension functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN Cursor extension detects trigger words in user input**
- **THEN Extension identifies trigger patterns from bot configuration**
- **AND Extension matches trigger words to corresponding bot behaviors and actions**
- **AND Extension provides trigger word context to CLI**
- **AND CLI receives trigger word information from extension**
- **AND CLI routes to appropriate bot behavior and action based on trigger words**
- **AND Bot executes action with trigger word context**
- **AND Extension handles multiple trigger word matches gracefully**
- **AND Extension provides feedback when no trigger words are detected**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Trigger bot only (no behavior or action specified)

**Steps:**
```gherkin
Given user types message containing trigger words "<trigger_message>" and bot is at behavior "<current_behavior>" and action "<current_action>"
When Cursor extension intercepts user message
Then Extension identifies target bot "<bot_name>" from trigger patterns
And Extension translates trigger words to CLI command for bot "<bot_name>"
And Extension executes CLI command
And CLI routes to bot "<bot_name>" using behavior "<current_behavior>" and action "<current_action>"
And Bot executes behavior "<current_behavior>" action "<current_action>"
```

**Examples:**
| trigger_message | bot_name | current_behavior | current_action | cli_command |
| --- | --- | --- | --- | --- |
| run story bot shape initialize_project | story_bot | shape | initialize_project | story_bot |
| run story bot shape gather_context | story_bot | shape | gather_context | story_bot |
| run story bot shape decide_planning_criteria | story_bot | shape | decide_planning_criteria | story_bot |
| run story bot shape build_knowledge | story_bot | shape | build_knowledge | story_bot |
| run story bot shape render_output | story_bot | shape | render_output | story_bot |
| run story bot shape validate_rules | story_bot | shape | validate_rules | story_bot |
| run story bot shape correct_bot | story_bot | shape | correct_bot | story_bot |
| run story bot prioritization initialize_project | story_bot | prioritization | initialize_project | story_bot |
| run story bot prioritization gather_context | story_bot | prioritization | gather_context | story_bot |
| run story bot prioritization decide_planning_criteria | story_bot | prioritization | decide_planning_criteria | story_bot |
| run story bot prioritization build_knowledge | story_bot | prioritization | build_knowledge | story_bot |
| run story bot prioritization render_output | story_bot | prioritization | render_output | story_bot |
| run story bot prioritization validate_rules | story_bot | prioritization | validate_rules | story_bot |
| run story bot prioritization correct_bot | story_bot | prioritization | correct_bot | story_bot |
| run story bot arrange initialize_project | story_bot | arrange | initialize_project | story_bot |
| run story bot arrange gather_context | story_bot | arrange | gather_context | story_bot |
| run story bot arrange decide_planning_criteria | story_bot | arrange | decide_planning_criteria | story_bot |
| run story bot arrange build_knowledge | story_bot | arrange | build_knowledge | story_bot |
| run story bot arrange render_output | story_bot | arrange | render_output | story_bot |
| run story bot arrange validate_rules | story_bot | arrange | validate_rules | story_bot |
| run story bot arrange correct_bot | story_bot | arrange | correct_bot | story_bot |
| run story bot discovery initialize_project | story_bot | discovery | initialize_project | story_bot |
| run story bot discovery gather_context | story_bot | discovery | gather_context | story_bot |
| run story bot discovery decide_planning_criteria | story_bot | discovery | decide_planning_criteria | story_bot |
| run story bot discovery build_knowledge | story_bot | discovery | build_knowledge | story_bot |
| run story bot discovery render_output | story_bot | discovery | render_output | story_bot |
| run story bot discovery validate_rules | story_bot | discovery | validate_rules | story_bot |
| run story bot discovery correct_bot | story_bot | discovery | correct_bot | story_bot |
| run story bot exploration initialize_project | story_bot | exploration | initialize_project | story_bot |
| run story bot exploration gather_context | story_bot | exploration | gather_context | story_bot |
| run story bot exploration decide_planning_criteria | story_bot | exploration | decide_planning_criteria | story_bot |
| run story bot exploration build_knowledge | story_bot | exploration | build_knowledge | story_bot |
| run story bot exploration render_output | story_bot | exploration | render_output | story_bot |
| run story bot exploration validate_rules | story_bot | exploration | validate_rules | story_bot |
| run story bot exploration correct_bot | story_bot | exploration | correct_bot | story_bot |
| run story bot scenarios initialize_project | story_bot | scenarios | initialize_project | story_bot |
| run story bot scenarios gather_context | story_bot | scenarios | gather_context | story_bot |
| run story bot scenarios decide_planning_criteria | story_bot | scenarios | decide_planning_criteria | story_bot |
| run story bot scenarios build_knowledge | story_bot | scenarios | build_knowledge | story_bot |
| run story bot scenarios render_output | story_bot | scenarios | render_output | story_bot |
| run story bot scenarios validate_rules | story_bot | scenarios | validate_rules | story_bot |
| run story bot scenarios correct_bot | story_bot | scenarios | correct_bot | story_bot |
| run story bot examples initialize_project | story_bot | examples | initialize_project | story_bot |
| run story bot examples gather_context | story_bot | examples | gather_context | story_bot |
| run story bot examples decide_planning_criteria | story_bot | examples | decide_planning_criteria | story_bot |
| run story bot examples build_knowledge | story_bot | examples | build_knowledge | story_bot |
| run story bot examples render_output | story_bot | examples | render_output | story_bot |
| run story bot examples validate_rules | story_bot | examples | validate_rules | story_bot |
| run story bot examples correct_bot | story_bot | examples | correct_bot | story_bot |
| run story bot tests initialize_project | story_bot | tests | initialize_project | story_bot |
| run story bot tests gather_context | story_bot | tests | gather_context | story_bot |
| run story bot tests decide_planning_criteria | story_bot | tests | decide_planning_criteria | story_bot |
| run story bot tests build_knowledge | story_bot | tests | build_knowledge | story_bot |
| run story bot tests render_output | story_bot | tests | render_output | story_bot |
| run story bot tests validate_rules | story_bot | tests | validate_rules | story_bot |
| run story bot tests correct_bot | story_bot | tests | correct_bot | story_bot |


### Scenario: Trigger bot and behavior (no action specified)

**Steps:**
```gherkin
Given user types message containing trigger words "<trigger_message>" for bot and behavior and behavior is at action "<current_action>"
When Cursor extension intercepts user message
Then Extension identifies bot "<bot_name>" and behavior "<behavior_name>" from trigger patterns
And Extension translates trigger words to CLI command for bot "<bot_name>" behavior "<behavior_name>"
And Extension executes CLI command
And CLI routes to bot "<bot_name>" behavior "<behavior_name>" using action "<current_action>"
And Bot executes action "<current_action>"
```

**Examples:**
| trigger_message | bot_name | behavior_name | current_action | cli_command |
| --- | --- | --- | --- | --- |
| story bot shape initialize_project | story_bot | shape | initialize_project | story_bot shape |
| story bot shape gather_context | story_bot | shape | gather_context | story_bot shape |
| story bot shape decide_planning_criteria | story_bot | shape | decide_planning_criteria | story_bot shape |
| story bot shape build_knowledge | story_bot | shape | build_knowledge | story_bot shape |
| story bot shape render_output | story_bot | shape | render_output | story_bot shape |
| story bot shape validate_rules | story_bot | shape | validate_rules | story_bot shape |
| story bot shape correct_bot | story_bot | shape | correct_bot | story_bot shape |
| story bot prioritization initialize_project | story_bot | prioritization | initialize_project | story_bot prioritization |
| story bot prioritization gather_context | story_bot | prioritization | gather_context | story_bot prioritization |
| story bot prioritization decide_planning_criteria | story_bot | prioritization | decide_planning_criteria | story_bot prioritization |
| story bot prioritization build_knowledge | story_bot | prioritization | build_knowledge | story_bot prioritization |
| story bot prioritization render_output | story_bot | prioritization | render_output | story_bot prioritization |
| story bot prioritization validate_rules | story_bot | prioritization | validate_rules | story_bot prioritization |
| story bot prioritization correct_bot | story_bot | prioritization | correct_bot | story_bot prioritization |
| story bot arrange initialize_project | story_bot | arrange | initialize_project | story_bot arrange |
| story bot arrange gather_context | story_bot | arrange | gather_context | story_bot arrange |
| story bot arrange decide_planning_criteria | story_bot | arrange | decide_planning_criteria | story_bot arrange |
| story bot arrange build_knowledge | story_bot | arrange | build_knowledge | story_bot arrange |
| story bot arrange render_output | story_bot | arrange | render_output | story_bot arrange |
| story bot arrange validate_rules | story_bot | arrange | validate_rules | story_bot arrange |
| story bot arrange correct_bot | story_bot | arrange | correct_bot | story_bot arrange |
| story bot discovery initialize_project | story_bot | discovery | initialize_project | story_bot discovery |
| story bot discovery gather_context | story_bot | discovery | gather_context | story_bot discovery |
| story bot discovery decide_planning_criteria | story_bot | discovery | decide_planning_criteria | story_bot discovery |
| story bot discovery build_knowledge | story_bot | discovery | build_knowledge | story_bot discovery |
| story bot discovery render_output | story_bot | discovery | render_output | story_bot discovery |
| story bot discovery validate_rules | story_bot | discovery | validate_rules | story_bot discovery |
| story bot discovery correct_bot | story_bot | discovery | correct_bot | story_bot discovery |
| story bot exploration initialize_project | story_bot | exploration | initialize_project | story_bot exploration |
| story bot exploration gather_context | story_bot | exploration | gather_context | story_bot exploration |
| story bot exploration decide_planning_criteria | story_bot | exploration | decide_planning_criteria | story_bot exploration |
| story bot exploration build_knowledge | story_bot | exploration | build_knowledge | story_bot exploration |
| story bot exploration render_output | story_bot | exploration | render_output | story_bot exploration |
| story bot exploration validate_rules | story_bot | exploration | validate_rules | story_bot exploration |
| story bot exploration correct_bot | story_bot | exploration | correct_bot | story_bot exploration |
| story bot scenarios initialize_project | story_bot | scenarios | initialize_project | story_bot scenarios |
| story bot scenarios gather_context | story_bot | scenarios | gather_context | story_bot scenarios |
| story bot scenarios decide_planning_criteria | story_bot | scenarios | decide_planning_criteria | story_bot scenarios |
| story bot scenarios build_knowledge | story_bot | scenarios | build_knowledge | story_bot scenarios |
| story bot scenarios render_output | story_bot | scenarios | render_output | story_bot scenarios |
| story bot scenarios validate_rules | story_bot | scenarios | validate_rules | story_bot scenarios |
| story bot scenarios correct_bot | story_bot | scenarios | correct_bot | story_bot scenarios |
| story bot examples initialize_project | story_bot | examples | initialize_project | story_bot examples |
| story bot examples gather_context | story_bot | examples | gather_context | story_bot examples |
| story bot examples decide_planning_criteria | story_bot | examples | decide_planning_criteria | story_bot examples |
| story bot examples build_knowledge | story_bot | examples | build_knowledge | story_bot examples |
| story bot examples render_output | story_bot | examples | render_output | story_bot examples |
| story bot examples validate_rules | story_bot | examples | validate_rules | story_bot examples |
| story bot examples correct_bot | story_bot | examples | correct_bot | story_bot examples |
| story bot tests initialize_project | story_bot | tests | initialize_project | story_bot tests |
| story bot tests gather_context | story_bot | tests | gather_context | story_bot tests |
| story bot tests decide_planning_criteria | story_bot | tests | decide_planning_criteria | story_bot tests |
| story bot tests build_knowledge | story_bot | tests | build_knowledge | story_bot tests |
| story bot tests render_output | story_bot | tests | render_output | story_bot tests |
| story bot tests validate_rules | story_bot | tests | validate_rules | story_bot tests |
| story bot tests correct_bot | story_bot | tests | correct_bot | story_bot tests |


### Scenario: Trigger bot, behavior, and action explicitly

**Steps:**
```gherkin
Given user types message containing trigger words "<trigger_message>" specifying bot, behavior, and action
When Cursor extension intercepts user message
Then Extension identifies bot "<bot_name>", behavior "<behavior_name>", and action "<action_name>" from trigger patterns
And Extension translates trigger words to CLI command for bot "<bot_name>" behavior "<behavior_name>" action "<action_name>"
And Extension executes CLI command
And CLI routes to bot "<bot_name>" and behavior "<behavior_name>" and action "<action_name>"
And Bot executes action "<action_name>"
```

**Examples:**
| trigger_message | bot_name | behavior_name | action_name | cli_command |
| --- | --- | --- | --- | --- |
| story bot shape initialize_project | story_bot | shape | initialize_project | story_bot shape initialize_project |
| story bot shape gather_context | story_bot | shape | gather_context | story_bot shape gather_context |
| story bot shape decide_planning_criteria | story_bot | shape | decide_planning_criteria | story_bot shape decide_planning_criteria |
| story bot shape build_knowledge | story_bot | shape | build_knowledge | story_bot shape build_knowledge |
| story bot shape render_output | story_bot | shape | render_output | story_bot shape render_output |
| story bot shape validate_rules | story_bot | shape | validate_rules | story_bot shape validate_rules |
| story bot shape correct_bot | story_bot | shape | correct_bot | story_bot shape correct_bot |
| story bot prioritization initialize_project | story_bot | prioritization | initialize_project | story_bot prioritization initialize_project |
| story bot prioritization gather_context | story_bot | prioritization | gather_context | story_bot prioritization gather_context |
| story bot prioritization decide_planning_criteria | story_bot | prioritization | decide_planning_criteria | story_bot prioritization decide_planning_criteria |
| story bot prioritization build_knowledge | story_bot | prioritization | build_knowledge | story_bot prioritization build_knowledge |
| story bot prioritization render_output | story_bot | prioritization | render_output | story_bot prioritization render_output |
| story bot prioritization validate_rules | story_bot | prioritization | validate_rules | story_bot prioritization validate_rules |
| story bot prioritization correct_bot | story_bot | prioritization | correct_bot | story_bot prioritization correct_bot |
| story bot arrange initialize_project | story_bot | arrange | initialize_project | story_bot arrange initialize_project |
| story bot arrange gather_context | story_bot | arrange | gather_context | story_bot arrange gather_context |
| story bot arrange decide_planning_criteria | story_bot | arrange | decide_planning_criteria | story_bot arrange decide_planning_criteria |
| story bot arrange build_knowledge | story_bot | arrange | build_knowledge | story_bot arrange build_knowledge |
| story bot arrange render_output | story_bot | arrange | render_output | story_bot arrange render_output |
| story bot arrange validate_rules | story_bot | arrange | validate_rules | story_bot arrange validate_rules |
| story bot arrange correct_bot | story_bot | arrange | correct_bot | story_bot arrange correct_bot |
| story bot discovery initialize_project | story_bot | discovery | initialize_project | story_bot discovery initialize_project |
| story bot discovery gather_context | story_bot | discovery | gather_context | story_bot discovery gather_context |
| story bot discovery decide_planning_criteria | story_bot | discovery | decide_planning_criteria | story_bot discovery decide_planning_criteria |
| story bot discovery build_knowledge | story_bot | discovery | build_knowledge | story_bot discovery build_knowledge |
| story bot discovery render_output | story_bot | discovery | render_output | story_bot discovery render_output |
| story bot discovery validate_rules | story_bot | discovery | validate_rules | story_bot discovery validate_rules |
| story bot discovery correct_bot | story_bot | discovery | correct_bot | story_bot discovery correct_bot |
| story bot exploration initialize_project | story_bot | exploration | initialize_project | story_bot exploration initialize_project |
| story bot exploration gather_context | story_bot | exploration | gather_context | story_bot exploration gather_context |
| story bot exploration decide_planning_criteria | story_bot | exploration | decide_planning_criteria | story_bot exploration decide_planning_criteria |
| story bot exploration build_knowledge | story_bot | exploration | build_knowledge | story_bot exploration build_knowledge |
| story bot exploration render_output | story_bot | exploration | render_output | story_bot exploration render_output |
| story bot exploration validate_rules | story_bot | exploration | validate_rules | story_bot exploration validate_rules |
| story bot exploration correct_bot | story_bot | exploration | correct_bot | story_bot exploration correct_bot |
| story bot scenarios initialize_project | story_bot | scenarios | initialize_project | story_bot scenarios initialize_project |
| story bot scenarios gather_context | story_bot | scenarios | gather_context | story_bot scenarios gather_context |
| story bot scenarios decide_planning_criteria | story_bot | scenarios | decide_planning_criteria | story_bot scenarios decide_planning_criteria |
| story bot scenarios build_knowledge | story_bot | scenarios | build_knowledge | story_bot scenarios build_knowledge |
| story bot scenarios render_output | story_bot | scenarios | render_output | story_bot scenarios render_output |
| story bot scenarios validate_rules | story_bot | scenarios | validate_rules | story_bot scenarios validate_rules |
| story bot scenarios correct_bot | story_bot | scenarios | correct_bot | story_bot scenarios correct_bot |
| story bot examples initialize_project | story_bot | examples | initialize_project | story_bot examples initialize_project |
| story bot examples gather_context | story_bot | examples | gather_context | story_bot examples gather_context |
| story bot examples decide_planning_criteria | story_bot | examples | decide_planning_criteria | story_bot examples decide_planning_criteria |
| story bot examples build_knowledge | story_bot | examples | build_knowledge | story_bot examples build_knowledge |
| story bot examples render_output | story_bot | examples | render_output | story_bot examples render_output |
| story bot examples validate_rules | story_bot | examples | validate_rules | story_bot examples validate_rules |
| story bot examples correct_bot | story_bot | examples | correct_bot | story_bot examples correct_bot |
| story bot tests initialize_project | story_bot | tests | initialize_project | story_bot tests initialize_project |
| story bot tests gather_context | story_bot | tests | gather_context | story_bot tests gather_context |
| story bot tests decide_planning_criteria | story_bot | tests | decide_planning_criteria | story_bot tests decide_planning_criteria |
| story bot tests build_knowledge | story_bot | tests | build_knowledge | story_bot tests build_knowledge |
| story bot tests render_output | story_bot | tests | render_output | story_bot tests render_output |
| story bot tests validate_rules | story_bot | tests | validate_rules | story_bot tests validate_rules |
| story bot tests correct_bot | story_bot | tests | correct_bot | story_bot tests correct_bot |


