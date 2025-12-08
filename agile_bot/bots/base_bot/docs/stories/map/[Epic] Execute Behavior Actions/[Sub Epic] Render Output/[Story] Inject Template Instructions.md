# [Story] Inject Template Instructions

**Navigation:** [Story Map](../../../story-map-outline.drawio) | [Epic Overview](../../../README.md)

**Epic:** Execute Behavior Actions  
**Sub Epic:** Render Output
**User:** Bot Behavior  
**Sequential Order:** 2  
**Story Type:** user

## Story Description

Inject Template Instructions functionality for the bot system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN render_output action processes template-only render configs**
- **THEN Action loads template file from templates folder**
- **AND Action injects template content into instructions**
- **AND render_configs array includes template content**

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given system is ready
And action is executing
```

## Scenarios

### Scenario: Render output loads template files from render JSON

**Steps:**
```gherkin
Given Render JSON file specifies template field
And Render JSON does not have synchronizer field
And Template file exists at 2_content/2_render/templates/
When render_output processes template-only render configs
Then render_output checks for template field in configuration
And render_output loads template file from templates folder
And render_output loads template file as text content
And render_output stores template content with render config
```


### Scenario: Render output injects template content into instructions

**Steps:**
```gherkin
Given Render JSON file exists without synchronizer field
And Render JSON file specifies template field
And render_output has loaded render JSON file
And render_output has loaded template file
When render_output merges instructions
Then render_output injects render_configs array into merged instructions
And render_configs[0] includes config with name from render JSON file
And render_configs[0] includes loaded template content from template file
```


### Scenario: Render output handles missing template files gracefully

**Steps:**
```gherkin
Given Render JSON specifies template file that does not exist
And Render JSON does not have synchronizer field
And Other render JSONs with templates do exist
When render_output loads template files
Then render_output skips missing template file
And render_output continues loading other templates
And render_output includes successfully loaded templates with render configs
```


