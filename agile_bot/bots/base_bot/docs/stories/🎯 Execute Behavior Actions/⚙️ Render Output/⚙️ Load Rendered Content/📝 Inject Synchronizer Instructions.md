# 📝 Inject Synchronizer Instructions

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json)

**Epic:** Render Output  
**Feature:** Load Rendered Content

**User:** Bot-Behavior  
**Sequential Order:** 3  
**Story Type:** user

## Story Description

Render Output Action processes synchronizer-based render configurations, includes synchronizer class paths and render method information in render_configs, and injects instructions into base_instructions so the AI can instantiate synchronizer classes and call their render methods to generate output artifacts.

## Acceptance Criteria

### Behavioral Acceptance Criteria
- **WHEN** render_output has loaded render JSON files with synchronizer fields
- **AND** synchronizer classes have been verified to exist and have render methods
- **THEN** render_output includes synchronizer class path in render_configs
- **AND** render_output includes renderer_command in config if specified (for render method variant)
- **AND** render_output includes instructions to instantiate synchronizer class and call render method
- **WHEN** render_output merges instructions for synchronizer-based renders
- **THEN** render_output injects render_configs array into merged instructions
- **AND** each synchronizer-based render_config entry includes config and synchronizer class path
- **AND** base_instructions contain instruction to instantiate synchronizer class
- **AND** base_instructions contain instruction to call render method on synchronizer instance
- **AND** base_instructions specify render method call with input and output paths

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given render_output has loaded render JSON files with synchronizer fields
And synchronizer classes have been verified to exist and have render methods
```

## Scenario Outlines

### Scenario Outline: Render output includes synchronizer configs in render_configs array

**Steps:**
```gherkin
Given render JSON file "<render_json_file>" exists with synchronizer field "<synchronizer_class>"
And render JSON file specifies renderer_command "<renderer_command>" (optional, for render method variant)
And render_output has loaded render JSON file "<render_json_file>"
And synchronizer class "<synchronizer_class>" has been verified
When render_output processes synchronizer-based render configs
Then render_output includes config with synchronizer field "<synchronizer_class>" in render_configs array
And render_configs[0] includes config with name from "<render_json_file>"
And render_configs[0] includes synchronizer class path "<synchronizer_class>"
And render_configs[0] includes renderer_command "<renderer_command>" (if specified)
And render_configs[0] includes input and output paths from render JSON
```

**Examples:**
| render_json_file | synchronizer_class | renderer_command |
|------------------|-------------------|------------------|
| render_story_map_outline_drawio.json | synchronizers.story_io.DrawIOSynchronizer | render-outline |
| render_story_exploration_drawio.json | synchronizers.story_io.DrawIOSynchronizer | render-exploration |

**Test Method:** test_render_output_includes_synchronizer_configs_in_render_configs_array

### Scenario Outline: Render output includes synchronizer execution instructions in base_instructions

**Steps:**
```gherkin
Given render JSON file "<render_json_file>" exists with synchronizer field "<synchronizer_class>"
And render JSON file specifies renderer_command "<renderer_command>" (optional, for render method variant)
And render JSON file specifies input "<input>" and output "<output>"
And render_output has processed synchronizer-based render configs
When render_output merges instructions
Then base_instructions contain instruction to instantiate synchronizer class "<synchronizer_class>"
And base_instructions contain instruction to call render method on synchronizer instance
And base_instructions specify render method call with input "<input>" and output "<output>" paths
And base_instructions specify renderer_command "<renderer_command>" if provided (for method variant)
```

**Examples:**
| render_json_file | synchronizer_class | renderer_command | input | output |
|------------------|-------------------|------------------|-------|--------|
| render_story_map_outline_drawio.json | synchronizers.story_io.DrawIOSynchronizer | render-outline | story-graph.json | story-map-outline.drawio |
| render_story_exploration_drawio.json | synchronizers.story_io.DrawIOSynchronizer | render-exploration | story-graph.json | story-map-explored-{scope}.drawio |

**Test Method:** test_render_output_includes_synchronizer_execution_instructions_in_base_instructions

