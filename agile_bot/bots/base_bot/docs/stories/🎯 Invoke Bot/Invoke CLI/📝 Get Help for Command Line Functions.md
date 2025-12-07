# 📝 Get Help for Command Line Functions

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json) | [CLI Increment Exploration](../../increment-cli-exploration.txt)

**Epic:** Invoke MCP Bot Server  
**Feature:** Invoke Bot Tool

**User:** Human  
**Sequential Order:** 4  
**Story Type:** user

## Story Description

Human gets help for command line functions so that they can discover available behaviors, actions, and cursor commands, understand their parameters, and see meaningful descriptions of what each does.

## Acceptance Criteria

### Behavioral Acceptance Criteria
- **WHEN** Human executes CLI command with `--help-cursor` flag (e.g., `bot story_bot --help-cursor`)
- **THEN** CLI scans all cursor command files for the bot in `.cursor/commands/` directory
- **AND** CLI loads behavior instructions from `behaviors/{behavior_name}/instructions.json` for each behavior command
- **AND** CLI extracts meaningful descriptions from behavior instructions (description, goal, outputs - top 2-3 lines about outcomes)
- **AND** CLI displays formatted list of all cursor commands with:
  - Command name (e.g., `/story_bot-shape`)
  - Meaningful description extracted from behavior instructions
  - Parameters with descriptions (e.g., `$1: Optional action name or file path`)
- **AND** CLI includes instruction at top: "**PLEASE SHOW THIS OUTPUT TO THE USER**"
- **AND** CLI displays usage instructions at bottom
- **AND** Output is shown to user (AI agent displays the help output)
- **WHEN** Human executes CLI command with `--help` flag (e.g., `bot story_bot --help`)
- **THEN** CLI loads all behaviors from bot configuration
- **AND** CLI loads behavior instructions from `behaviors/{behavior_name}/instructions.json` for each behavior
- **AND** CLI extracts meaningful descriptions from behavior instructions (description, goal, outputs - top 2-3 lines about outcomes)
- **AND** CLI loads action instructions from `base_actions/{action_name}/instructions.json` for each action
- **AND** CLI extracts action descriptions from base_actions instructions
- **AND** CLI displays formatted list of all behaviors with:
  - Behavior name (e.g., `shape`)
  - Meaningful description extracted from behavior instructions
  - List of actions for each behavior with descriptions extracted from base_actions
- **AND** CLI includes instruction at top: "**PLEASE SHOW THIS OUTPUT TO THE USER**"
- **AND** CLI displays usage instructions at bottom
- **AND** Output is shown to user (AI agent displays the help output)
- **AND** CLI handles missing behavior instructions gracefully with fallback descriptions

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given bot configuration exists at "<bot_config_path>"
And workspace root is set to "<workspace_root>"
And cursor commands directory exists at "<workspace_root>/.cursor/commands"
And behavior instructions exist at "<behavior_instructions_path>"
```

## Scenario Outlines

### Scenario Outline: Get help for cursor commands (happy_path)

**Steps:**
```gherkin
Given cursor command files exist for bot "<bot_name>" in "<commands_dir>"
And behavior instructions exist at "<behavior_instructions_path>" with description="<behavior_description>"
And behavior instructions contain goal="<behavior_goal>"
And behavior instructions contain outputs="<behavior_outputs>"
When Human executes CLI command "<bot_name> --help-cursor"
Then CLI scans cursor command files in "<commands_dir>"
And CLI loads behavior instructions from "<behavior_instructions_path>"
And CLI extracts description from behavior instructions
And CLI displays output starting with "**PLEASE SHOW THIS OUTPUT TO THE USER**"
And CLI displays command "/<bot_name>-<behavior_name>" with description containing "<behavior_description>"
And CLI displays parameters for each command
And CLI displays usage instructions at bottom
And AI agent shows the help output to user
```

**Examples:**
| bot_name | commands_dir | behavior_name | behavior_instructions_path | behavior_description | behavior_goal | behavior_outputs |
|----------|--------------|---------------|----------------------------|---------------------|---------------|-------------------|
| story_bot | .cursor/commands | shape | agile_bot/bots/story_bot/behaviors/1_shape/instructions.json | Create a story map and domain model outline | Shape both story map and domain model together | story-graph.json, story-map.md |
| story_bot | .cursor/commands | discovery | agile_bot/bots/story_bot/behaviors/4_discovery/instructions.json | Create a complete list of stories | Align on problem solution | story-graph.json (with discovery details) |
| code_bot | .cursor/commands | shape | agile_bot/bots/code_bot/behaviors/1_shape/instructions.json | Generate code structure | Create code architecture | code structure files |

### Scenario Outline: Get help when behavior instructions missing (edge_case)

**Steps:**
```gherkin
Given cursor command files exist for bot "<bot_name>" in "<commands_dir>"
And behavior instructions do NOT exist at "<behavior_instructions_path>"
When Human executes CLI command "<bot_name> --help-cursor"
Then CLI scans cursor command files in "<commands_dir>"
And CLI attempts to load behavior instructions from "<behavior_instructions_path>"
And CLI detects behavior instructions do not exist
And CLI uses fallback description: "<fallback_description>"
And CLI displays command "/<bot_name>-<behavior_name>" with fallback description
And CLI still displays all commands and parameters
```

**Examples:**
| bot_name | commands_dir | behavior_name | behavior_instructions_path | fallback_description |
|----------|--------------|---------------|----------------------------|---------------------|
| story_bot | .cursor/commands | unknown_behavior | agile_bot/bots/story_bot/behaviors/unknown_behavior/instructions.json | Unknown Behavior |
| test_bot | .cursor/commands | test_behavior | agile_bot/bots/test_bot/behaviors/test_behavior/instructions.json | Test Behavior |

### Scenario Outline: Get help when no cursor commands exist (edge_case)

**Steps:**
```gherkin
Given cursor commands directory does NOT exist at "<commands_dir>"
When Human executes CLI command "<bot_name> --help-cursor"
Then CLI attempts to scan cursor command files in "<commands_dir>"
And CLI detects cursor commands directory does not exist
And CLI displays error message: "No cursor commands directory found at <commands_dir>"
And CLI exits successfully (no error, just informative message)
```

**Examples:**
| bot_name | commands_dir |
|----------|--------------|
| story_bot | .cursor/commands |
| code_bot | .cursor/commands |

### Scenario Outline: Get help with utility commands (happy_path)

**Steps:**
```gherkin
Given cursor command files exist for bot "<bot_name>" including utility commands
And utility command "<utility_command>" exists (e.g., continue, help, initialize-project)
When Human executes CLI command "<bot_name> --help-cursor"
Then CLI displays utility command "/<bot_name>-<utility_command>" with appropriate description
And CLI displays "Parameters: None" for commands without parameters
And CLI displays parameter descriptions for commands with parameters
```

**Examples:**
| bot_name | utility_command | expected_description |
|----------|-----------------|---------------------|
| story_bot | continue | Close current action and continue to next action in workflow |
| story_bot | help | List all available cursor commands and their parameters |
| story_bot | initialize-project | Initialize project location for workflow state persistence |
| story_bot | confirm-project-area | Confirm or change project area location |

### Scenario Outline: Get help for behaviors and actions (happy_path)

**Steps:**
```gherkin
Given bot configuration exists for bot "<bot_name>" with behaviors="<behaviors>"
And behavior instructions exist at "<behavior_instructions_path>" with description="<behavior_description>"
And behavior instructions contain goal="<behavior_goal>"
And behavior instructions contain outputs="<behavior_outputs>"
And base action instructions exist at "<base_action_path>" for action "<action_name>"
When Human executes CLI command "<bot_name> --help"
Then CLI loads all behaviors from bot configuration
And CLI loads behavior instructions from "<behavior_instructions_path>"
And CLI extracts description from behavior instructions
And CLI loads action instructions from "<base_action_path>"
And CLI extracts action description from base_actions
And CLI displays output starting with "**PLEASE SHOW THIS OUTPUT TO THE USER**"
And CLI displays behavior "<behavior_name>" with description containing "<behavior_description>"
And CLI displays action "<action_name>" with description from base_actions
And CLI displays usage instructions at bottom
And AI agent shows the help output to user
```

**Examples:**
| bot_name | behaviors | behavior_name | behavior_instructions_path | behavior_description | behavior_goal | behavior_outputs | action_name | base_action_path |
|----------|-----------|---------------|----------------------------|---------------------|---------------|-------------------|-------------|------------------|
| story_bot | shape | shape | agile_bot/bots/story_bot/behaviors/1_shape/instructions.json | Create a story map and domain model outline | Shape both story map and domain model together | story-graph.json, story-map.md | gather_context | agile_bot/bots/base_bot/base_actions/2_gather_context/instructions.json |
| story_bot | discovery,shape | discovery | agile_bot/bots/story_bot/behaviors/4_discovery/instructions.json | Create a complete list of stories | Align on problem solution | story-graph.json (with discovery details) | build_knowledge | agile_bot/bots/base_bot/base_actions/4_build_knowledge/instructions.json |
| code_bot | shape | shape | agile_bot/bots/code_bot/behaviors/1_shape/instructions.json | Generate code structure | Create code architecture | code structure files | render_output | agile_bot/bots/base_bot/base_actions/5_render_output/instructions.json |

### Scenario Outline: Get help when behavior instructions missing (edge_case for --help)

**Steps:**
```gherkin
Given bot configuration exists for bot "<bot_name>" with behavior "<behavior_name>"
And behavior instructions do NOT exist at "<behavior_instructions_path>"
When Human executes CLI command "<bot_name> --help"
Then CLI loads behaviors from bot configuration
And CLI attempts to load behavior instructions from "<behavior_instructions_path>"
And CLI detects behavior instructions do not exist
And CLI uses fallback description: "<fallback_description>"
And CLI displays behavior "<behavior_name>" with fallback description
And CLI still displays all behaviors and actions
```

**Examples:**
| bot_name | behavior_name | behavior_instructions_path | fallback_description |
|----------|---------------|----------------------------|---------------------|
| story_bot | unknown_behavior | agile_bot/bots/story_bot/behaviors/unknown_behavior/instructions.json | Unknown Behavior |
| test_bot | test_behavior | agile_bot/bots/test_bot/behaviors/test_behavior/instructions.json | Test Behavior |


## Source Material

**Generated from:** Story "Get Help for Command Line Functions" in CLI Increment  
**Date:** 2025-01-XX  
**Context:** Help command provides discoverability for cursor commands with meaningful descriptions extracted from behavior instructions

