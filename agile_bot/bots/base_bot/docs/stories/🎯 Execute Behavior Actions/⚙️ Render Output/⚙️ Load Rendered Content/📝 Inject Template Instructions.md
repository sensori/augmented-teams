# 📝 Inject Template Instructions

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json)

**Epic:** Render Output  
**Feature:** Load Rendered Content

**User:** Bot-Behavior  
**Sequential Order:** 2  
**Story Type:** user

## Story Description

Render Output Action processes template-only render configurations (those without a synchronizer field), loads template files from 2_render/templates/, and injects template content into instructions so the AI can use templates to generate output artifacts.

## Acceptance Criteria

### Behavioral Acceptance Criteria
- **WHEN** render_output has loaded render JSON files
- **AND** render JSON file specifies template field (without synchronizer field)
- **THEN** render_output loads template file from 2_render/templates/ folder
- **AND** render_output loads template file as text content
- **AND** render_output stores template content with render config
- **WHEN** render_output has loaded template files for template-only renders
- **THEN** render_output injects render_configs array into merged instructions
- **AND** each template-only render_config entry includes config and loaded template content
- **WHEN** template file cannot be read for template-only render
- **THEN** render_output skips that template file
- **AND** render_output continues loading other templates
- **AND** render_output includes successfully loaded templates with render configs

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given render_output has loaded render JSON files
And render JSON files have been verified and are ready for processing
```

## Scenario Outlines

### Scenario Outline: Render output loads template files from render JSON

**Steps:**
```gherkin
Given render JSON file specifies template field "<template_path>"
And render JSON does not have synchronizer field
And template file exists at 2_content/2_render/templates/<template_path>
When render_output processes template-only render configs
Then render_output checks for template field in configuration
And render_output loads template file from templates folder
And render_output loads template file as text content
And render_output stores template content with render config
```

**Examples:**
| template_path |
|---------------|
| story-exploration.md |
| story-map.txt |
| story-doc-scenarios.md |

**Test Method:** test_render_output_loads_template_files_from_render_json

### Scenario Outline: Render output injects template content into instructions

**Background:**

```gherkin
Given behavior folder structure exists with 2_content/2_render/ folder
```

**Steps:**
```gherkin
Given render JSON file "<render_json_file>" exists without synchronizer field
And render JSON file specifies template field "<template_file>"
And render_output has loaded render JSON file "<render_json_file>"
And render_output has loaded template file "<template_file>"
When render_output merges instructions
Then render_output injects render_configs array into merged instructions
And render_configs[0] includes config with name from "<render_json_file>"
And render_configs[0] includes loaded template content from "<template_file>"
```

**Examples:**
| render_json_file | template_file |
|------------------|---------------|
| render_story_exploration.md.json | templates/story-exploration.md |
| render_story_map_txt.json | templates/story-map.md |

**Test Method:** test_render_output_injects_template_content_into_instructions

### Scenario Outline: Render output handles missing template files gracefully

**Steps:**
```gherkin
Given render JSON specifies template file "<template_path>" that does not exist
And render JSON does not have synchronizer field
And other render JSONs with templates do exist
When render_output loads template files
Then render_output skips missing template file
And render_output continues loading other templates
And render_output includes successfully loaded templates with render configs
```

**Examples:**
| template_path |
|---------------|
| missing-template.md |
| nonexistent-template.txt |

**Test Method:** test_render_output_handles_missing_template_files_gracefully

