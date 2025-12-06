# Load + Inject Template - Story Exploration

**Story:** Load + Inject Template  
**Epic:** Render Output  
**Feature:** Load Rendered Content  
**Story Type:** User  
**User:** Bot-Behavior

## Story Description

Render Output Action loads configuration files relating to content necessary to render content (synchronize_*.json files) and loads template files specified in those configurations, then injects both the configuration files and templates into instructions so that the AI can use them during render output execution.

---

## Domain AC (Story Level)

### Core Domain Concepts

- **Render Output Action**: Base bot action that executes render_output workflow step
- **Behavior Folder**: Contains behavior-specific content (2_content/2_render/, 2_content/3_synchronize/, etc.)
- **Synchronize Configuration**: synchronize_*.json files in 2_content/3_synchronize/ that define sync scripts and templates
- **Template File**: File-based template (not code) specified in synchronize config templates array
- **Instructions**: Merged instruction set that includes base instructions, behavior instructions, and injected configs/templates
- **Synchronize Instructions**: General instructions from 3_synchronize/instructions.json
- **Synchronize Configs**: Array of loaded synchronize_*.json configurations with loaded templates

---

### Domain Behaviors

- **Render Output Action loads synchronize configuration**: Discovers and loads synchronize_*.json files from behavior folder
- **Render Output Action loads templates**: Reads template files specified in synchronize config templates array
- **Render Output Action injects into instructions**: Adds synchronize_configs and templates to merged instructions dictionary
- **AI uses injected templates**: Accesses template content from instructions to use during synchronization

---

### Domain Rules

- **Synchronize folder is optional**: Behavior may or may not have 2_content/3_synchronize/ folder
- **Templates are file-based**: Templates are text files (not code/builders) loaded as content
- **Template paths are relative to synchronize folder**: Template paths in config are relative to 3_synchronize/ folder
- **Missing files are skipped gracefully**: If template or config file cannot be read, skip it and continue
- **Templates are injected with configs**: Each synchronize_config entry includes both config and loaded templates dictionary

---

## Story: Load + Inject Template

**Acceptance Criteria:**

(AC) WHEN render_output action executes for a behavior
(AC) THEN render_output discovers synchronize folder in 2_content/3_synchronize/ (or *_content/*_synchronize/)
(AC) AND render_output loads instructions.json from synchronize folder if it exists
(AC) AND render_output loads all synchronize_*.json configuration files from synchronize folder

(AC) WHEN render_output loads synchronize_*.json configuration file
(AC) THEN render_output reads configuration (name, description, scripts, templates, instructions)
(AC) AND render_output checks for templates array in configuration
(AC) AND render_output loads template files specified in templates array

(AC) WHEN synchronize configuration specifies template files in templates array
(AC) THEN render_output loads each template file as text content
(AC) AND render_output stores template content in dictionary keyed by template path
(AC) AND render_output handles missing template files gracefully (skips if not found)

(AC) WHEN render_output has loaded synchronize configurations and templates
(AC) THEN render_output injects synchronize_instructions into merged instructions
(AC) AND render_output injects synchronize_configs array into merged instructions
(AC) AND each synchronize_config entry includes config, templates dictionary, and file path

(AC) WHEN AI receives injected instructions with synchronize_configs
(AC) THEN AI can access synchronize configuration from synchronize_configs array
(AC) AND AI can access loaded template content from templates dictionary in each config entry
(AC) AND AI can use templates for formatting rules and reference during synchronization

(AC) WHEN render_output cannot find synchronize folder
(AC) THEN render_output continues without synchronize configuration
(AC) AND render_output does not inject synchronize_configs into instructions
(AC) AND render_output does not raise error (synchronize is optional)

(AC) WHEN synchronize configuration file cannot be read
(AC) THEN render_output skips that configuration file
(AC) AND render_output continues loading other synchronize_*.json files
(AC) AND render_output does not fail entire load process

(AC) WHEN template file cannot be read
(AC) THEN render_output skips that template file
(AC) AND render_output continues loading other templates
(AC) AND render_output includes successfully loaded templates in templates dictionary

---

## Consolidation Decisions

_No consolidation decisions needed at this time._

---

## Domain Rules Referenced

- Component paths must be relative to behavior folder
- Component metadata must include type
- Component references must be valid
- Story graph must preserve component metadata

---

## Source Material

- Story graph JSON structure
- Render output action implementation
- Synchronize configuration discovery
- Builder pattern implementation
- Template loading mechanism

