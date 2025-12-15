# Load + Inject Template - Story Exploration

**Story:** Load + Inject Template  
**Epic:** Render Output  
**Feature:** Load Rendered Content  
**Story Type:** User  
**User:** Bot-Behavior

## Story Description

Render Output Action loads render JSON files from content/render/ that specify what needs to be rendered, then loads template files specified in those render JSON files (for template-based rendering, not builders), and injects both the render JSON configurations and template content into instructions so that the AI can use them during render output execution.

---

## Domain AC (Story Level)

### Core Domain Concepts

- **Render Output Action**: Base bot action that executes render_output workflow step
- **Behavior Folder**: Contains behavior-specific content (content/render/, content/synchronize/, etc.)
- **Render JSON Files**: Configuration files in content/render/ that specify what to render (name, path, template, output, builder)
- **Template File**: File-based template (not code) specified in render JSON template field
- **Builder File**: Python code file specified in render JSON builder field (executed, not injected)
- **Instructions**: Merged instruction set that includes base instructions, behavior instructions, and injected render configs/templates

---

### Domain Behaviors

- **Render Output Action loads render JSON filesrenb**: Discovers and loads all *.json files from content/render/ folder
- **Render Output Action loads templates**: Reads template files specified in render JSON template field (for non-builder renders)
- **Render Output Action injects into instructions**: Adds render configs and templates to merged instructions dictionary
- **Render Output Action executes builders**: Runs builder Python files specified in render JSON builder field (not injected)
- **AI uses injected templates**: Accesses template content from instructions to use during rendering

---

### Domain Rules

- **Render folder contains render JSON files**: All *.json files in content/render/ define what needs to be rendered
- **Templates are for non-builder renders**: Only render JSONs without builder field use templates (templates get injected)
- **Builders are executed, not injected**: Render JSONs with builder field execute Python code (builders don't get injected)
- **Template paths are relative to templates folder**: Template paths in render JSON are relative to render/templates/ folder
- **Missing files are skipped gracefully**: If template or render JSON file cannot be read, skip it and continue
- **Synchronize folder is separate**: synchronize/ folder is for post-render synchronization (not part of Load + Inject Template)

---

## Story: Load + Inject Template

**Acceptance Criteria:**

(AC) WHEN render_output action executes for a behavior
(AC) THEN render_output discovers render folder in content/render/
(AC) AND render_output loads all *.json files from render folder (render JSON files)
(AC) AND render_output loads instructions.json from render folder if it exists

(AC) WHEN render_output loads render JSON file
(AC) THEN render_output reads configuration (name, path, template, output, builder if specified)
(AC) AND render_output checks if render JSON has template field (and no builder field)
(AC) AND render_output loads template file specified in template field for non-builder renders

(AC) WHEN render JSON specifies template file (without builder field)
(AC) THEN render_output loads template file from render/templates/ folder
(AC) AND render_output loads template file as text content
(AC) AND render_output stores template content with render config
(AC) AND render_output handles missing template files gracefully (skips if not found)

(AC) WHEN render_output has loaded render JSON files and templates
(AC) THEN render_output injects render_configs array into merged instructions
(AC) AND each render_config entry includes config and loaded template content (if template-based, not builder)
(AC) AND render_output injects render_instructions if instructions.json exists in render folder

(AC) WHEN AI receives injected instructions with render_configs
(AC) THEN AI can access render configuration from render_configs array
(AC) AND AI can access loaded template content for template-based renders
(AC) AND AI can use templates to generate output artifacts during rendering

(AC) WHEN render JSON specifies builder field
(AC) THEN render_output does not inject template for that render config
(AC) AND render_output executes builder Python file instead (builders are executed, not injected)
(AC) AND builder execution happens separately from template injection

(AC) WHEN render_output cannot find render folder
(AC) THEN render_output reports error (render folder is required for render_output action)
(AC) AND render_output cannot proceed without render configurations

(AC) WHEN render JSON file cannot be read
(AC) THEN render_output skips that render JSON file
(AC) AND render_output continues loading other *.json files from render folder
(AC) AND render_output does not fail entire load process

(AC) WHEN template file cannot be read for template-based render
(AC) THEN render_output skips that template file
(AC) AND render_output continues loading other templates
(AC) AND render_output includes successfully loaded templates with render configs

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

