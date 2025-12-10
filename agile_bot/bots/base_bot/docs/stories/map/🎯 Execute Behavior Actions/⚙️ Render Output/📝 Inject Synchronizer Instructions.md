# 📝 Inject Synchronizer Instructions

**Navigation:** [📋 Story Map](../../../story-map-outline.drawio) | [⚙️ Feature Overview](../../../../README.md)

**Epic:** Execute Behavior Actions
**Feature:** Render Output
**User:** Bot Behavior
**Sequential Order:** 3
**Story Type:** user

## Story Description

Inject Synchronizer Instructions functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** render_output action processes synchronizer-based render configs

  **then** Action includes synchronizer configs in render_configs array

  **and** Action includes synchronizer execution instructions in base_instructions

  **and** Instructions specify how to instantiate and call synchronizer render method

## Scenarios

### Scenario: Render output includes synchronizer configs in render_configs array (happy_path)

**Steps:**
```gherkin
Given Render JSON file exists with synchronizer field
And Render JSON file specifies renderer_command (optional, for render method variant)
And render_output has loaded render JSON file
And Synchronizer class has been verified
When render_output processes synchronizer-based render configs
Then render_output includes config with synchronizer field in render_configs array
And render_configs[0] includes config with name from render JSON file
And render_configs[0] includes synchronizer class path
And render_configs[0] includes renderer_command (if specified)
And render_configs[0] includes input and output paths from render JSON
```


### Scenario: Render output includes synchronizer execution instructions in base_instructions (happy_path)

**Steps:**
```gherkin
Given Render JSON file exists with synchronizer field
And Render JSON file specifies renderer_command (optional, for render method variant)
And Render JSON file specifies input and output
And render_output has processed synchronizer-based render configs
When render_output merges instructions
Then base_instructions contain instruction to instantiate synchronizer class
And base_instructions contain instruction to call render method on synchronizer instance
And base_instructions specify render method call with input and output paths
And base_instructions specify renderer_command if provided (for method variant)
```

