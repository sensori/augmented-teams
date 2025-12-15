# 📝 Proceed To Decide Strategy

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Execute Behavior Actions
**Feature:** Gather Context
**User:** Bot Behavior
**Sequential Order:** 5
**Story Type:** user

## Story Description

Proceed To Decide Strategy functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** GatherContextAction completes execution

  **and** Human says action is done

  **then** GatherContextAction saves Workflow State (per "Saves Behavior State" story)

  **and** Workflow injects next action instructions (per "Inject Next Behavior-Action" story)

  **and** Workflow proceeds to decide_strategy

## Scenarios

### Scenario: Seamless transition from gather_context to decide_strategy (happy_path)

**Steps:**
```gherkin
Given behavior is 'discovery'
And gather_context action is complete
And Human confirms "done" or "proceed"
When gather_context action finalizes
Then Action saves Workflow State with:
- current_behavior='story_bot.discovery'
- current_action='story_bot.discovery.gather_context'
- timestamp=[completion time]
And Action loads gather_context/action configuration
And Action reads next_action='decide_strategy'
And Action injects AI instructions: "When done, proceed to decide_strategy"
And AI invokes decide_strategy tool
And Workflow transitions seamlessly to next action
```


### Scenario: Workflow state captures gather_context completion (happy_path)

**Steps:**
```gherkin
Given gather_context action completes at timestamp='2025-12-03T10:05:30Z'
And Human confirms "done"
When Action saves workflow state
Then workflow state is updated with:
- current_action='story_bot.exploration.gather_context'
- timestamp='2025-12-03T10:05:30Z'
And completed_actions list includes: {action_state: 'story_bot.exploration.gather_context', timestamp: '2025-12-03T10:05:30Z'}
And State persists to project_area/workflow state
And If workflow is interrupted after this point, gather_context is marked as completed
```


### Scenario: Workflow resumes at decide_strategy after interruption (happy_path)

**Steps:**
```gherkin
Given gather_context is completed and chat was interrupted
When user reopens chat and invokes bot tool
Then Router forwards to decide_strategy action
```

