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
- **THEN Extension loads bot registry to discover available bots**
- **AND Extension performs two-stage routing: first match bot, then match behavior/action**
- **AND Extension identifies target bot from bot-level trigger patterns**
- **AND Extension loads target bot's behavior/action trigger patterns**
- **AND Extension matches trigger words to corresponding behavior and action**
- **AND Extension provides trigger word context and route to CLI**
- **AND CLI receives bot, behavior, action, and context from extension**
- **AND CLI routes to appropriate bot behavior and action based on trigger route**
- **AND Bot executes action with trigger word context**
- **AND Extension handles multiple trigger word matches gracefully**
- **AND Extension provides feedback when no trigger words are detected**
- **AND CliGenerator maintains bot registry when generating CLI**
- **AND Bot registry contains bot name, trigger patterns, and CLI path for each bot**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Two-stage routing - Match bot from registry then match behavior/action

**Steps:**
```gherkin
Given bot registry exists at agile_bot/bots/registry.json
And registry contains multiple bots with trigger patterns
And registry contains story_bot with patterns ["stories", "story map", "requirements"]
And registry contains code_bot with patterns ["write code", "implement", "refactor"]
When user types message "lets work on stories"
Then TriggerRouter loads bot registry
And TriggerRouter matches "stories" to story_bot
And TriggerRouter loads story_bot's behavior/action triggers
And TriggerRouter matches behavior/action within story_bot
And TriggerRouter returns route {bot: story_bot, behavior: shape, action: gather_context}
```

**Examples:**
| message | matched_bot | bot_pattern | behavior | action |
| --- | --- | --- | --- | --- |
| lets work on stories | story_bot | stories | shape | gather_context |
| write code for authentication | code_bot | write code | implementation | generate_code |
| refactor the payment logic | code_bot | refactor | refactoring | refactor_code |
| update story map requirements | story_bot | requirements | discovery | gather_context |


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
| hey lets get going on some stories | story_bot | shape | initialize_project | story_bot |
| lets launch the stories work | story_bot | shape | gather_context | story_bot |
| lets get back into writing stories | story_bot | shape | decide_planning_criteria | story_bot |
| ready to work on stories | story_bot | shape | build_knowledge | story_bot |
| time to kick off stories | story_bot | shape | render_output | story_bot |
| lets do some stories now | story_bot | shape | validate_rules | story_bot |
| lets launch the stories work | story_bot | prioritization | initialize_project | story_bot |
| lets get back into writing stories | story_bot | prioritization | gather_context | story_bot |
| ready to work on stories | story_bot | prioritization | decide_planning_criteria | story_bot |
| time to kick off stories | story_bot | prioritization | build_knowledge | story_bot |
| lets do some stories now | story_bot | prioritization | render_output | story_bot |
| hey lets get going on some stories | story_bot | prioritization | validate_rules | story_bot |
| lets get back into writing stories | story_bot | arrange | initialize_project | story_bot |
| ready to work on stories | story_bot | arrange | gather_context | story_bot |
| time to kick off stories | story_bot | arrange | decide_planning_criteria | story_bot |
| lets do some stories now | story_bot | arrange | build_knowledge | story_bot |
| hey lets get going on some stories | story_bot | arrange | render_output | story_bot |
| lets launch the stories work | story_bot | arrange | validate_rules | story_bot |
| ready to work on stories | story_bot | discovery | initialize_project | story_bot |
| time to kick off stories | story_bot | discovery | gather_context | story_bot |
| lets do some stories now | story_bot | discovery | decide_planning_criteria | story_bot |
| hey lets get going on some stories | story_bot | discovery | build_knowledge | story_bot |
| lets launch the stories work | story_bot | discovery | render_output | story_bot |
| lets get back into writing stories | story_bot | discovery | validate_rules | story_bot |
| time to kick off stories | story_bot | exploration | initialize_project | story_bot |
| lets do some stories now | story_bot | exploration | gather_context | story_bot |
| hey lets get going on some stories | story_bot | exploration | decide_planning_criteria | story_bot |
| lets launch the stories work | story_bot | exploration | build_knowledge | story_bot |
| lets get back into writing stories | story_bot | exploration | render_output | story_bot |
| ready to work on stories | story_bot | exploration | validate_rules | story_bot |
| lets do some stories now | story_bot | scenarios | initialize_project | story_bot |
| hey lets get going on some stories | story_bot | scenarios | gather_context | story_bot |
| lets launch the stories work | story_bot | scenarios | decide_planning_criteria | story_bot |
| lets get back into writing stories | story_bot | scenarios | build_knowledge | story_bot |
| ready to work on stories | story_bot | scenarios | render_output | story_bot |
| time to kick off stories | story_bot | scenarios | validate_rules | story_bot |
| hey lets get going on some stories | story_bot | examples | initialize_project | story_bot |
| lets launch the stories work | story_bot | examples | gather_context | story_bot |
| lets get back into writing stories | story_bot | examples | decide_planning_criteria | story_bot |
| ready to work on stories | story_bot | examples | build_knowledge | story_bot |
| time to kick off stories | story_bot | examples | render_output | story_bot |
| lets do some stories now | story_bot | examples | validate_rules | story_bot |
| lets launch the stories work | story_bot | tests | initialize_project | story_bot |
| lets get back into writing stories | story_bot | tests | gather_context | story_bot |
| ready to work on stories | story_bot | tests | decide_planning_criteria | story_bot |
| time to kick off stories | story_bot | tests | build_knowledge | story_bot |
| lets do some stories now | story_bot | tests | render_output | story_bot |
| hey lets get going on some stories | story_bot | tests | validate_rules | story_bot |


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
| kick off shaping for a new feature | story_bot | shape | initialize_project | story_bot shape |
| define scope for the new capability | story_bot | shape | gather_context | story_bot shape |
| map acceptance requirements | story_bot | shape | decide_planning_criteria | story_bot shape |
| kick off shaping for a new feature | story_bot | shape | build_knowledge | story_bot shape |
| define scope for the new capability | story_bot | shape | render_output | story_bot shape |
| map acceptance requirements | story_bot | shape | validate_rules | story_bot shape |
| rank the backlog for launch | story_bot | prioritization | initialize_project | story_bot prioritization |
| set priorities for upcoming features | story_bot | prioritization | gather_context | story_bot prioritization |
| groom the backlog items | story_bot | prioritization | decide_planning_criteria | story_bot prioritization |
| rank the backlog for launch | story_bot | prioritization | build_knowledge | story_bot prioritization |
| set priorities for upcoming features | story_bot | prioritization | render_output | story_bot prioritization |
| groom the backlog items | story_bot | prioritization | validate_rules | story_bot prioritization |
| arrange the feature map layout | story_bot | arrange | initialize_project | story_bot arrange |
| organize epics and features | story_bot | arrange | gather_context | story_bot arrange |
| restructure the story map | story_bot | arrange | decide_planning_criteria | story_bot arrange |
| arrange the feature map layout | story_bot | arrange | build_knowledge | story_bot arrange |
| organize epics and features | story_bot | arrange | render_output | story_bot arrange |
| restructure the story map | story_bot | arrange | validate_rules | story_bot arrange |
| start discovery for the new product | story_bot | discovery | initialize_project | story_bot discovery |
| collect insights for the domain | story_bot | discovery | gather_context | story_bot discovery |
| explore user needs | story_bot | discovery | decide_planning_criteria | story_bot discovery |
| start discovery for the new product | story_bot | discovery | build_knowledge | story_bot discovery |
| collect insights for the domain | story_bot | discovery | render_output | story_bot discovery |
| explore user needs | story_bot | discovery | validate_rules | story_bot discovery |
| begin the exploration phase | story_bot | exploration | initialize_project | story_bot exploration |
| investigate solution options | story_bot | exploration | gather_context | story_bot exploration |
| clarify exploration scope | story_bot | exploration | decide_planning_criteria | story_bot exploration |
| begin the exploration phase | story_bot | exploration | build_knowledge | story_bot exploration |
| investigate solution options | story_bot | exploration | render_output | story_bot exploration |
| clarify exploration scope | story_bot | exploration | validate_rules | story_bot exploration |
| draft behavior scenarios | story_bot | scenarios | initialize_project | story_bot scenarios |
| write gherkin cases | story_bot | scenarios | gather_context | story_bot scenarios |
| outline test scenarios | story_bot | scenarios | decide_planning_criteria | story_bot scenarios |
| draft behavior scenarios | story_bot | scenarios | build_knowledge | story_bot scenarios |
| write gherkin cases | story_bot | scenarios | render_output | story_bot scenarios |
| outline test scenarios | story_bot | scenarios | validate_rules | story_bot scenarios |
| prepare usage examples | story_bot | examples | initialize_project | story_bot examples |
| draft sample flows | story_bot | examples | gather_context | story_bot examples |
| capture illustrative examples | story_bot | examples | decide_planning_criteria | story_bot examples |
| prepare usage examples | story_bot | examples | build_knowledge | story_bot examples |
| draft sample flows | story_bot | examples | render_output | story_bot examples |
| capture illustrative examples | story_bot | examples | validate_rules | story_bot examples |
| design test coverage | story_bot | tests | initialize_project | story_bot tests |
| plan validation cases | story_bot | tests | gather_context | story_bot tests |
| define acceptance tests | story_bot | tests | decide_planning_criteria | story_bot tests |
| design test coverage | story_bot | tests | build_knowledge | story_bot tests |
| plan validation cases | story_bot | tests | render_output | story_bot tests |
| define acceptance tests | story_bot | tests | validate_rules | story_bot tests |


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
| set up the project area for shape | story_bot | shape | initialize_project | story_bot shape initialize_project |
| gather context for shape | story_bot | shape | gather_context | story_bot shape gather_context |
| decide planning criteria for shape | story_bot | shape | decide_planning_criteria | story_bot shape decide_planning_criteria |
| build the knowledge base for shape | story_bot | shape | build_knowledge | story_bot shape build_knowledge |
| render outputs for shape | story_bot | shape | render_output | story_bot shape render_output |
| validate outputs for shape | story_bot | shape | validate_rules | story_bot shape validate_rules |
| set up the project area for prioritization | story_bot | prioritization | initialize_project | story_bot prioritization initialize_project |
| gather context for prioritization | story_bot | prioritization | gather_context | story_bot prioritization gather_context |
| decide planning criteria for prioritization | story_bot | prioritization | decide_planning_criteria | story_bot prioritization decide_planning_criteria |
| build the knowledge base for prioritization | story_bot | prioritization | build_knowledge | story_bot prioritization build_knowledge |
| render outputs for prioritization | story_bot | prioritization | render_output | story_bot prioritization render_output |
| validate outputs for prioritization | story_bot | prioritization | validate_rules | story_bot prioritization validate_rules |
| set up the project area for arrange | story_bot | arrange | initialize_project | story_bot arrange initialize_project |
| gather context for arrange | story_bot | arrange | gather_context | story_bot arrange gather_context |
| decide planning criteria for arrange | story_bot | arrange | decide_planning_criteria | story_bot arrange decide_planning_criteria |
| build the knowledge base for arrange | story_bot | arrange | build_knowledge | story_bot arrange build_knowledge |
| render outputs for arrange | story_bot | arrange | render_output | story_bot arrange render_output |
| validate outputs for arrange | story_bot | arrange | validate_rules | story_bot arrange validate_rules |
| set up the project area for discovery | story_bot | discovery | initialize_project | story_bot discovery initialize_project |
| gather context for discovery | story_bot | discovery | gather_context | story_bot discovery gather_context |
| decide planning criteria for discovery | story_bot | discovery | decide_planning_criteria | story_bot discovery decide_planning_criteria |
| build the knowledge base for discovery | story_bot | discovery | build_knowledge | story_bot discovery build_knowledge |
| render outputs for discovery | story_bot | discovery | render_output | story_bot discovery render_output |
| validate outputs for discovery | story_bot | discovery | validate_rules | story_bot discovery validate_rules |
| set up the project area for exploration | story_bot | exploration | initialize_project | story_bot exploration initialize_project |
| gather context for exploration | story_bot | exploration | gather_context | story_bot exploration gather_context |
| decide planning criteria for exploration | story_bot | exploration | decide_planning_criteria | story_bot exploration decide_planning_criteria |
| build the knowledge base for exploration | story_bot | exploration | build_knowledge | story_bot exploration build_knowledge |
| render outputs for exploration | story_bot | exploration | render_output | story_bot exploration render_output |
| validate outputs for exploration | story_bot | exploration | validate_rules | story_bot exploration validate_rules |
| set up the project area for scenarios | story_bot | scenarios | initialize_project | story_bot scenarios initialize_project |
| gather context for scenarios | story_bot | scenarios | gather_context | story_bot scenarios gather_context |
| decide planning criteria for scenarios | story_bot | scenarios | decide_planning_criteria | story_bot scenarios decide_planning_criteria |
| build the knowledge base for scenarios | story_bot | scenarios | build_knowledge | story_bot scenarios build_knowledge |
| render outputs for scenarios | story_bot | scenarios | render_output | story_bot scenarios render_output |
| validate outputs for scenarios | story_bot | scenarios | validate_rules | story_bot scenarios validate_rules |
| set up the project area for examples | story_bot | examples | initialize_project | story_bot examples initialize_project |
| gather context for examples | story_bot | examples | gather_context | story_bot examples gather_context |
| decide planning criteria for examples | story_bot | examples | decide_planning_criteria | story_bot examples decide_planning_criteria |
| build the knowledge base for examples | story_bot | examples | build_knowledge | story_bot examples build_knowledge |
| render outputs for examples | story_bot | examples | render_output | story_bot examples render_output |
| validate outputs for examples | story_bot | examples | validate_rules | story_bot examples validate_rules |
| set up the project area for tests | story_bot | tests | initialize_project | story_bot tests initialize_project |
| gather context for tests | story_bot | tests | gather_context | story_bot tests gather_context |
| decide planning criteria for tests | story_bot | tests | decide_planning_criteria | story_bot tests decide_planning_criteria |
| build the knowledge base for tests | story_bot | tests | build_knowledge | story_bot tests build_knowledge |
| render outputs for tests | story_bot | tests | render_output | story_bot tests render_output |
| validate outputs for tests | story_bot | tests | validate_rules | story_bot tests validate_rules |


