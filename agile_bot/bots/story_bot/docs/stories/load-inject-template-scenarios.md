# 📝 Load + Inject Template

**Navigation:** [📋 Story Map](story-map-outline.drawio) | [⚙️ Feature Overview](../README.md)

**Epic:** Render Output  
**Feature:** Load Rendered Content

## Story Description

Render Output Action loads configuration files relating to content necessary to render content (synchronize_*.json files) and loads template files specified in those configurations, then injects both the configuration files and templates into instructions so that the AI can use them during render output execution.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** render_output action executes for a behavior, **then** render_output discovers synchronize folder in 2_content/3_synchronize/
- **When** render_output loads synchronize_*.json configuration file, **then** render_output reads configuration and checks for templates array
- **When** synchronize configuration specifies template files, **then** render_output loads each template file as text content
- **When** render_output has loaded synchronize configurations and templates, **then** render_output injects them into merged instructions
- **When** AI receives injected instructions, **then** AI can access synchronize configuration and template content

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given behavior folder exists with 2_content/2_render/ folder
And render_output action is executing for the behavior
```

## Scenarios

### Scenario: Render output discovers and loads render JSON files

**Steps:**
```gherkin
Given behavior folder contains 2_content/2_render/ folder
And render folder contains render_story_exploration.md.json file
When render_output action executes for the behavior
Then render_output discovers render folder using *_content/*_render pattern
And render_output loads all *.json files from render folder
And render_output reads each render JSON configuration (name, path, template, output, builder if specified)
```

### Scenario: Render output loads template files from render JSON

**Steps:**
```gherkin
Given render JSON file specifies template field "story-exploration.md"
And render JSON does not have builder field
And template file exists at 2_content/2_render/templates/story-exploration.md
When render_output loads render JSON file
Then render_output checks for template field in configuration
And render_output loads template file from templates folder
And render_output loads template file as text content
And render_output stores template content with render config
```

### Scenario: Render output injects render configs and templates into instructions

**Steps:**
```gherkin
Given render_output has loaded render JSON files
And render_output has loaded template files for template-based renders
When render_output merges instructions
Then render_output injects render_configs array into merged instructions
And each render_config entry includes config and loaded template content (for template-based renders)
And render_output injects render_instructions if instructions.json exists in render folder
```

### Scenario: AI accesses injected render configuration and templates

**Steps:**
```gherkin
Given render_output has injected render_configs into instructions
And render_configs array contains template-based render configs with loaded templates
When AI receives merged instructions
Then AI can access render configuration from render_configs array
And AI can access loaded template content for template-based renders
And AI can use templates to generate output artifacts during rendering
```

### Scenario: Render output handles builder-based renders separately

**Steps:**
```gherkin
Given render JSON file specifies builder field "render_story_map_txt.py"
And render JSON also specifies template field
When render_output loads render JSON file
Then render_output does not inject template for that render config
And render_output marks render config as builder-based (not template-based)
And render_output will execute builder Python file separately (builders are executed, not injected)
```

### Scenario: Render output handles missing render folder

**Steps:**
```gherkin
Given behavior folder does not contain 2_content/2_render/ folder
When render_output action executes for the behavior
Then render_output reports error (render folder is required for render_output action)
And render_output cannot proceed without render configurations
```

### Scenario: Render output handles missing template files gracefully

**Steps:**
```gherkin
Given render JSON specifies template file that does not exist
And render JSON does not have builder field
And other render JSONs with templates do exist
When render_output loads template files
Then render_output skips missing template file
And render_output continues loading other templates
And render_output includes successfully loaded templates with render configs
```

### Scenario: Render output loads instructions.json from render folder

**Steps:**
```gherkin
Given render folder contains instructions.json file
And render folder contains render JSON configuration files
When render_output discovers render folder
Then render_output loads instructions.json if it exists
And render_output injects render_instructions into merged instructions
And render_instructions are separate from render_configs
```

### Scenario: Render output handles unreadable render JSON files

**Steps:**
```gherkin
Given render folder contains multiple *.json files
And one render JSON file cannot be read (corrupted or invalid JSON)
When render_output loads render JSON files
Then render_output skips unreadable render JSON file
And render_output continues loading other *.json files from render folder
And render_output does not fail entire load process
```

### Scenario: Render output loads multiple render configurations with templates

**Steps:**
```gherkin
Given render folder contains multiple render JSON files
And some render JSONs specify templates (no builder)
And some render JSONs specify builders
When render_output loads all render JSON files
Then render_output loads each render JSON configuration
And render_output loads templates only for template-based renders (no builder field)
And render_output includes all render configs in render_configs array
And render_output marks which configs are template-based vs builder-based
```

