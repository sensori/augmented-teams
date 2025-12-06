# 📝 Load Render Configurations

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json)

**Epic:** Render Output  
**Feature:** Load Rendered Content

**User:** Bot-Behavior  
**Sequential Order:** 1  
**Story Type:** user

## Story Description

Render Output Action discovers the render folder in 2_content/2_render/, loads all render JSON configuration files, loads instructions.json if it exists, and verifies synchronizer classes exist and have render methods. This prepares all render configurations for injection into instructions.

## Acceptance Criteria

### Behavioral Acceptance Criteria
- **WHEN** render_output action executes for a behavior
- **THEN** render_output discovers render folder in 2_content/2_render/ (or *_content/*_render/)
- **AND** render_output loads all *.json files from render folder (render JSON files)
- **AND** render_output loads instructions.json from render folder if it exists
- **WHEN** render_output loads render JSON file
- **THEN** render_output reads configuration (name, path, template, output, synchronizer if specified)
- **AND** render_output checks if render JSON has synchronizer field
- **WHEN** render JSON specifies synchronizer field
- **THEN** render_output verifies synchronizer field contains full module path and class name (e.g., `synchronizers.story_io.DrawIOSynchronizer`)
- **AND** render_output verifies synchronizer class exists and can be imported
- **AND** render_output verifies synchronizer class has render method
- **WHEN** render_output cannot find render folder
- **THEN** render_output reports error (render folder is required for render_output action)
- **AND** render_output cannot proceed without render configurations
- **WHEN** render JSON file cannot be read
- **THEN** render_output skips that render JSON file
- **AND** render_output continues loading other *.json files from render folder
- **AND** render_output does not fail entire load process
- **WHEN** synchronizer class cannot be imported or does not have render method
- **THEN** render_output reports error for that render config
- **AND** render_output continues loading other render configs

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given behavior folder exists with 2_content/2_render/ folder
And render_output action is executing for the behavior
```

## Scenario Outlines

### Scenario Outline: Render output discovers and loads render JSON files

**Steps:**
```gherkin
Given behavior folder contains 2_content/2_render/ folder
And render folder contains render JSON file "<render_json_file>"
When render_output action executes for the behavior
Then render_output discovers render folder using *_content/*_render pattern
And render_output loads all *.json files from render folder
And render_output reads each render JSON configuration (name, path, template, output, synchronizer if specified)
```

**Examples:**
| render_json_file |
|------------------|
| render_story_exploration.md.json |
| render_story_map_txt.json |
| render_story_map_outline_drawio.json |
| render_exploration_acceptance_criteria_drawio.json |

**Test Method:** test_render_output_discovers_and_loads_render_json_files

### Scenario Outline: Render output loads instructions.json from render folder

**Steps:**
```gherkin
Given render folder contains instructions.json file
And render folder contains render JSON configuration files
When render_output discovers render folder
Then render_output loads instructions.json if it exists
And render_output stores render_instructions for later injection
And render_instructions are separate from render_configs
```

**Test Method:** test_render_output_loads_instructions_json_from_render_folder

### Scenario Outline: Render output verifies synchronizer classes exist and have render method

**Steps:**
```gherkin
Given render JSON file "<render_json_file>" exists with synchronizer field "<synchronizer_class>"
When render_output loads render JSON file "<render_json_file>"
Then render_output verifies synchronizer field "<synchronizer_class>" contains full module path and class name
And render_output verifies synchronizer class "<synchronizer_class>" can be imported
And render_output verifies synchronizer class "<synchronizer_class>" has render method
And render_output stores synchronizer class path in render config
```

**Examples:**
| render_json_file | synchronizer_class |
|------------------|-------------------|
| render_story_map_outline_drawio.json | synchronizers.story_io.DrawIOSynchronizer |
| render_story_exploration_drawio.json | synchronizers.story_io.DrawIOSynchronizer |

**Test Method:** test_render_output_verifies_synchronizer_classes_exist_and_have_render_method

### Scenario Outline: Render output handles missing render folder

**Steps:**
```gherkin
Given behavior folder does not contain 2_content/2_render/ folder
When render_output action executes for the behavior
Then render_output reports error (render folder is required for render_output action)
And render_output cannot proceed without render configurations
```

**Test Method:** test_render_output_handles_missing_render_folder

### Scenario Outline: Render output handles unreadable render JSON files

**Steps:**
```gherkin
Given render folder contains multiple *.json files
And one render JSON file "<render_json_file>" cannot be read (corrupted or invalid JSON)
When render_output loads render JSON files
Then render_output skips unreadable render JSON file
And render_output continues loading other *.json files from render folder
And render_output does not fail entire load process
```

**Examples:**
| render_json_file |
|------------------|
| corrupted_render.json |
| invalid_json.json |

**Test Method:** test_render_output_handles_unreadable_render_json_files

### Scenario Outline: Render output handles invalid synchronizer classes

**Steps:**
```gherkin
Given render JSON file "<render_json_file>" exists with synchronizer field "<synchronizer_class>"
And synchronizer class "<synchronizer_class>" cannot be imported or does not have render method
When render_output loads render JSON file "<render_json_file>"
Then render_output reports error for that render config
And render_output continues loading other render configs
And render_output does not fail entire load process
```

**Examples:**
| render_json_file | synchronizer_class |
|------------------|-------------------|
| render_invalid_sync.json | synchronizers.nonexistent.InvalidSynchronizer |
| render_no_render_method.json | synchronizers.story_io.DrawIOSynchronizer (if class missing render method) |

**Test Method:** test_render_output_handles_invalid_synchronizer_classes

