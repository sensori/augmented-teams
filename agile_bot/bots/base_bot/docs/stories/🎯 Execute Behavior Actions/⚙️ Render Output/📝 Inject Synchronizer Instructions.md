# 📝 Inject Synchronizer Instructions

**Navigation:** [📋 Story Map](../../story-map-outline.drawio) | [⚙️ Feature Overview](../../README.md)

**Epic:** Execute Behavior Actions  
**Feature:** Render Output

**User:** Bot-Behavior  
**Sequential Order:** 3  
**Story Type:** user

**Test File:** test_load_rendered_content.py  
**Test Class:** TestInjectSynchronizerInstructions  
**Test Methods:** 
- test_render_output_includes_synchronizer_configs_in_render_configs_array
- test_render_output_includes_synchronizer_execution_instructions_in_base_instructions

## Story Description

Render Output Action injects synchronizer class paths and execution instructions for synchronizer-based renders. When a render JSON includes a `synchronizer` field, the action includes the synchronizer configuration in render_configs and adds execution instructions to base_instructions for instantiating and calling the synchronizer's render method.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **WHEN** render_output processes synchronizer-based render configs
- **THEN** render_output includes config with synchronizer field in render_configs array
- **AND** render_configs[0] includes config with name from render JSON file
- **AND** render_configs[0] includes synchronizer class path
- **AND** render_configs[0] includes renderer_command (if specified)
- **AND** render_configs[0] includes input and output paths from render JSON
- **AND** base_instructions contain instruction to instantiate synchronizer class
- **AND** base_instructions contain instruction to call render method on synchronizer instance
- **AND** base_instructions specify render method call with input and output paths
- **AND** base_instructions specify renderer_command if provided (for method variant)

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Render Output Action is initialized with bot_name and behavior
And render_configs have been loaded
And synchronizer classes have been verified
```

## Scenarios

### Scenario: Render output includes synchronizer configs in render_configs array

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
And Template should NOT be included for synchronizer-based renders
```

**Test Method:** `test_render_output_includes_synchronizer_configs_in_render_configs_array`

**Test Details:**
- Creates render JSON with synchronizer field and renderer_command
- Executes render_output action
- Verifies synchronizer config included in render_configs
- Verifies all fields present: name, synchronizer, renderer_command, input, output
- Verifies template is NOT included for synchronizer-based renders

### Scenario: Render output includes synchronizer execution instructions in base_instructions

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

**Test Method:** `test_render_output_includes_synchronizer_execution_instructions_in_base_instructions`

**Test Details:**
- Creates render JSON with synchronizer and renderer_command
- Executes render_output action
- Verifies base_instructions contain synchronizer execution instructions
- Verifies instructions mention synchronizer class and render method
- Verifies renderer_command is included in instructions

## Test Details

- **Test File:** `test_load_rendered_content.py`
- **Test Class:** `TestInjectSynchronizerInstructions`
- **Test Methods:**
  - `test_render_output_includes_synchronizer_configs_in_render_configs_array` - Tests inclusion of synchronizer configs
  - `test_render_output_includes_synchronizer_execution_instructions_in_base_instructions` - Tests injection of execution instructions

## Implementation Notes

The Render Output Action handles synchronizer-based renders:
1. Processes render configs that include a `synchronizer` field
2. Includes synchronizer configuration in `render_configs` array with:
   - Synchronizer class path (full module path)
   - `renderer_command` (optional, specifies which render method variant to call)
   - Input and output paths
3. Injects execution instructions into `base_instructions` that tell the AI to:
   - Instantiate the synchronizer class
   - Call the appropriate render method (or method variant specified by renderer_command)
   - Pass input and output paths to the render method
4. Does NOT include template content for synchronizer-based renders (templates are only for template-only renders)

Synchronizer-based renders use code execution rather than template substitution, so the synchronizer class handles the actual rendering logic.
