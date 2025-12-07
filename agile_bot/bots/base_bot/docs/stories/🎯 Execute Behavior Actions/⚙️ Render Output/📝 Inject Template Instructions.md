# 📝 Inject Template Instructions

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Execute Behavior Actions  
**Feature:** Render Output

**User:** Bot-Behavior  
**Sequential Order:** 2  
**Story Type:** user

**Test File:** test_load_rendered_content.py  
**Test Class:** TestInjectTemplateInstructions  
**Test Methods:** 
- test_render_output_loads_template_files_from_render_json
- test_render_output_injects_template_content_into_instructions
- test_render_output_handles_missing_template_files_gracefully

## Story Description

Render Output Action loads template files for template-only renders (renders without synchronizers) and injects the template content into the instructions. Templates are loaded from the `2_content/2_render/templates/` folder and stored with their corresponding render configurations.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** render_output processes template-only render configs
- **THEN** render_output checks for template field in configuration
- **AND** render_output loads template file from templates folder
- **AND** render_output loads template file as text content
- **AND** render_output stores template content with render config
- **AND** render_output injects template content into instructions
- **WHEN** template file does not exist
- **THEN** render_output skips missing template file
- **AND** render_output continues loading other templates

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Render Output Action is initialized with bot_name and behavior
And render_configs have been loaded
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

**Test Method:** `test_render_output_loads_template_files_from_render_json`

**Test Details:**
- Creates render JSON with template field (no synchronizer)
- Creates template file in templates folder
- Executes render_output action
- Verifies template content is loaded and stored with render config
- Verifies template path is preserved in config

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

**Test Method:** `test_render_output_injects_template_content_into_instructions`

**Test Details:**
- Creates render JSON and template file
- Executes render_output action
- Verifies render_configs array in instructions
- Verifies template content is included in render config
- Verifies template content matches file content

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

**Test Method:** `test_render_output_handles_missing_template_files_gracefully`

**Test Details:**
- Creates render JSONs with existing and missing templates
- Executes render_output action
- Verifies missing template is handled gracefully
- Verifies valid templates are still loaded and included

## Test Details

- **Test File:** `test_load_rendered_content.py`
- **Test Class:** `TestInjectTemplateInstructions`
- **Test Methods:**
  - `test_render_output_loads_template_files_from_render_json` - Tests loading of template files
  - `test_render_output_injects_template_content_into_instructions` - Tests injection of template content
  - `test_render_output_handles_missing_template_files_gracefully` - Tests error handling for missing templates

## Implementation Notes

The Render Output Action handles template-only renders:
1. Checks for `template` field in render JSON configuration
2. Only processes templates when `synchronizer` field is NOT present
3. Loads template files from `{behavior}/2_content/2_render/templates/` folder
4. Stores template content as text with the render config
5. Injects template content into `render_configs` array in instructions
6. Handles missing templates gracefully, skipping them and continuing with valid ones

Template content is stored in the render config object alongside the configuration, allowing the AI to use the template for rendering output.
