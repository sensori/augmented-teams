# 📝 Load Render Configurations

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Execute Behavior Actions  
**Feature:** Render Output

**User:** Bot-Behavior  
**Sequential Order:** 1  
**Story Type:** user

**Test File:** test_load_rendered_content.py  
**Test Class:** TestLoadRenderConfigurations  
**Test Methods:** 
- test_render_output_discovers_and_loads_render_json_files
- test_render_output_loads_instructions_json_from_render_folder
- test_render_output_verifies_synchronizer_classes_exist_and_have_render_method
- test_render_output_handles_missing_render_folder
- test_render_output_handles_unreadable_render_json_files
- test_render_output_handles_invalid_synchronizer_classes

## Story Description

Render Output Action discovers and loads render JSON configuration files from the behavior's render folder. The action finds the render folder using the `*_content/*_render` pattern, loads all `*.json` files, verifies synchronizer classes if specified, and loads instructions.json if present.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** render_output action executes for the behavior
- **THEN** render_output discovers render folder using `*_content/*_render` pattern
- **AND** render_output loads all `*.json` files from render folder
- **AND** render_output reads each render JSON configuration
- **AND** render_output loads instructions.json if it exists in render folder
- **AND** render_output verifies synchronizer classes exist and have render method (if synchronizer field specified)
- **WHEN** render folder does not exist
- **THEN** render_output reports error (render folder is required)
- **WHEN** render JSON file cannot be read
- **THEN** render_output skips unreadable file and continues loading others

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Render Output Action is initialized with bot_name and behavior
And workspace_root is available
```

## Scenarios

### Scenario: Render output discovers and loads render JSON files

**Steps:**
```gherkin
Given Behavior folder contains 2_content/2_render/ folder
And Render folder contains render JSON file
When render_output action executes for the behavior
Then render_output discovers render folder using *_content/*_render pattern
And render_output loads all *.json files from render folder
And render_output reads each render JSON configuration
And render_configs array exists and contains loaded configs
```

**Test Method:** `test_render_output_discovers_and_loads_render_json_files`

**Test Details:**
- Creates behavior render folder structure
- Creates multiple render JSON files
- Executes render_output action
- Verifies render_configs array contains all loaded configurations
- Verifies each config includes name and file path

### Scenario: Render output loads instructions.json from render folder

**Steps:**
```gherkin
Given Render folder contains instructions.json file
And Render folder contains render JSON configuration files
When render_output discovers render folder
Then render_output loads instructions.json if it exists
And render_output stores render_instructions for later injection
And render_instructions are separate from render_configs
```

**Test Method:** `test_render_output_loads_instructions_json_from_render_folder`

**Test Details:**
- Creates render folder with instructions.json
- Executes render_output action
- Verifies render_instructions loaded separately from render_configs
- Verifies instructions content is accessible

### Scenario: Render output verifies synchronizer classes exist and have render method

**Steps:**
```gherkin
Given Render JSON file exists with synchronizer field
When render_output loads render JSON file
Then render_output verifies synchronizer field contains full module path and class name
And render_output verifies synchronizer class can be imported
And render_output verifies synchronizer class has render method
And render_output stores synchronizer class path in render config
```

**Test Method:** `test_render_output_verifies_synchronizer_classes_exist_and_have_render_method`

**Test Details:**
- Creates render JSON with synchronizer field using full module path
- Executes render_output action
- Verifies synchronizer class path stored in config
- Verifies synchronizer class can be imported
- Verifies synchronizer class has required method (e.g., synchronize_outline)

### Scenario: Render output handles missing render folder

**Steps:**
```gherkin
Given Behavior folder does not contain 2_content/2_render/ folder
When render_output action executes for the behavior
Then render_output reports error (render folder is required for render_output action)
And render_output cannot proceed without render configurations
```

**Test Method:** `test_render_output_handles_missing_render_folder`

**Test Details:**
- Creates behavior folder without render folder
- Executes render_output action
- Verifies error handling or empty render_configs

### Scenario: Render output handles unreadable render JSON files

**Steps:**
```gherkin
Given Render folder contains multiple *.json files
And One render JSON file cannot be read (corrupted or invalid JSON)
When render_output loads render JSON files
Then render_output skips unreadable render JSON file
And render_output continues loading other *.json files from render folder
And render_output does not fail entire load process
```

**Test Method:** `test_render_output_handles_unreadable_render_json_files`

**Test Details:**
- Creates render folder with valid and invalid JSON files
- Executes render_output action
- Verifies invalid file is skipped
- Verifies valid files are still loaded

### Scenario: Render output handles invalid synchronizer classes

**Steps:**
```gherkin
Given Render JSON file exists with synchronizer field
And Synchronizer class cannot be imported or does not have render method
When render_output loads render JSON file
Then render_output reports error for that render config
And render_output continues loading other render configs
And render_output does not fail entire load process
```

**Test Method:** `test_render_output_handles_invalid_synchronizer_classes`

**Test Details:**
- Creates render JSONs with invalid and valid synchronizers
- Executes render_output action
- Verifies processing continues for valid configs
- Verifies invalid synchronizer configs are handled gracefully

## Test Details

- **Test File:** `test_load_rendered_content.py`
- **Test Class:** `TestLoadRenderConfigurations`
- **Test Methods:**
  - `test_render_output_discovers_and_loads_render_json_files` - Tests discovery and loading of render JSON files
  - `test_render_output_loads_instructions_json_from_render_folder` - Tests loading of instructions.json
  - `test_render_output_verifies_synchronizer_classes_exist_and_have_render_method` - Tests synchronizer verification
  - `test_render_output_handles_missing_render_folder` - Tests error handling for missing folder
  - `test_render_output_handles_unreadable_render_json_files` - Tests handling of corrupted JSON files
  - `test_render_output_handles_invalid_synchronizer_classes` - Tests handling of invalid synchronizer classes

## Implementation Notes

The Render Output Action:
1. Discovers the render folder using the pattern `{behavior}/2_content/2_render/`
2. Loads all `*.json` files from the render folder as render configurations
3. Loads `instructions.json` if present (stored separately as `render_instructions`)
4. Verifies synchronizer classes when `synchronizer` field is specified in render JSON
5. Handles errors gracefully, skipping invalid files/configs and continuing with valid ones
6. Returns `render_configs` array with all successfully loaded configurations
