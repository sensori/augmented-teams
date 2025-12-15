# 📝 Proceed To Build Knowledge

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Execute Behavior Actions
**Feature:** Decide Strategy Criteria Action
**User:** Bot Behavior
**Sequential Order:** 4
**Story Type:** user

## Story Description

Proceed To Build Knowledge functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** StrategyAction completes execution

- **When** Human says action is done

  **then** StrategyAction saves Workflow State (per "Saves Behavior State" story)

  **and** Workflow injects next action instructions (per "Inject Next Behavior-Action" story)

  **and** Workflow proceeds to build_knowledge

## Scenarios

### Scenario: Seamless transition from strategy to build_knowledge (happy_path)

**Steps:**
```gherkin
Given behavior is 'discovery'
And decide_strategy action is complete
And Human confirms "done" or "proceed"
When decide_strategy action finalizes
Then Action saves Workflow State with:
- current_behavior='story_bot.discovery'
- current_action='story_bot.discovery.decide_strategy'
- timestamp=[completion time]
And Action loads decide_strategy/action configuration
And Action reads next_action='build_knowledge'
And Action injects AI instructions: "When done, proceed to build_knowledge"
And AI invokes build_knowledge tool
And Workflow transitions seamlessly to next action
```


### Scenario: Workflow state captures strategy completion (happy_path)

**Steps:**
```gherkin
Given decide_strategy action completes at timestamp='2025-12-03T10:25:00Z'
And Human confirms "done"
When Action saves workflow state
Then workflow state is updated with:
- current_action='story_bot.exploration.decide_strategy'
- timestamp='2025-12-03T10:25:00Z'
And completed_actions list includes: {action_state: 'story_bot.exploration.decide_strategy', timestamp: '2025-12-03T10:25:00Z'}
And State persists to project_area/workflow state
And If workflow is interrupted after this point, strategy is marked as completed
```

