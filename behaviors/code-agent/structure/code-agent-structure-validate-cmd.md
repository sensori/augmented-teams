### Command: `behavior-structure-validate-cmd.md`

**Purpose:** Validate AI behaviors for structure and naming convention compliance.

**Usage:**
* `\behavior-structure validate` — validate all behaviors for structure compliance
* `\behavior-structure validate <feature>` — validate one feature's behaviors

**What It Checks:**
1. **Behavior Feature outline file**: Each feature must have `<feature>-outline.md` in the feature root directory (overview of main behaviors, purpose of each, and tools they use)
2. File names follow `<feature>-<behavior-name>-<type>.<ext>` pattern
3. Rule-command linkages exist (rules have matching commands - rules can relate to multiple commands with same prefix)
4. **Relationship sections** (documentation that links rules, commands, and code):
   * Rules must list commands that execute them: `**Executing Commands:**`
   * Commands must reference:
     - `**Rule:**` — Which rule this command follows
     - `
**Output:**
* List of structure violations with details
* Missing relationship sections (rules without commands, commands without Steps, etc.)
* Steps format issues (steps that don't specify who/what performs them)
* Naming inconsistencies
* Documentation issues

**File Structure Requirements:**
* All behavior files must be in `behaviors/<feature>/code-agent-behaviors/` (organized in Behavior Features - collections of tightly-knit, strongly related behaviors)
* **Each Behavior Feature must include** `<feature>-outline.md` in the feature root directory that includes:
  * Overview of the overarching purpose of the feature
  * Brief overview of main behaviors (simple format: `**Behavior Name** - description`)
  * Tools section at the end listing only Orchestrator and MCP tools used
* Related files must share the same `<feature>-<behavior-name>` prefix
* Rules can relate to multiple commands (e.g., `behavior-structure-rule.mdc` relates to `behavior-structure-validate-cmd.md`, `behavior-structure-fix-cmd.md`, etc.)
* Index files (`code-agent-index.json`) are stored in `behaviors/<feature>/code-agent-index.json`
* **Behavior Features**: Keep behavior files belonging to the same feature together in one directory (e.g., `behaviors/code-agent-behavior/code-agent-behaviors/`). Never scatter behaviors into separate areas or break them up by component type.

**Naming Patterns:**
* Rules: `<feature>-<behavior-name>-rule.mdc` (no verb suffix)
* Commands: `<feature>-<behavior-name>-cmd.md` OR `<feature>-<behavior-name>-<verb>-cmd.md` (verb suffix for multiple commands, e.g., `behavior-structure-validate-cmd.md`)
* Code: `<feature>-<behavior-name>-cmd.py` (base name, NO verb suffix - one Python file can implement multiple commands)
* MCP: `<feature>-<tool-name>-mcp.json`
* **Note:** A single Python implementation file can serve multiple commands (e.g., `behavior-structure-cmd.py` implements validate, fix, and create actions)

**Relationship Sections Explained:**
These are documentation sections that create clear links between rules, commands, and code:

* **Rules** must include `**Executing Commands:**` section listing which commands execute the rule (e.g., `\behavior-structure validate`, `\behavior-structure fix`)
* **Commands** must include:
  * `**Steps:**` — Sequential actions to execute the behavior - **REQUIRED per behavior-structure-rule.mdc**
    - Each step must specify who/what performs it:
      - "The AI agent..." or "The AI assistant..." (for AI-performed actions)
      - "The code function `name()`..." or "The code function..." (for code-executed actions)
      - "The user..." or "The user is prompted..." (for user interactions)
      - "The MCP tool `tool_name()`..." or "The MCP tool..." (for MCP tool calls)
    - Steps without performers are flagged during validation
  * `**Rule:**` — Which rule this command follows (e.g., `\behavior-structure-rule`)
  * `
**Steps:**
1. **Code** (`Commands.structure(action="validate", feature)`) calls `Feature.validate(feature)` to discover and validate features
2. **Code** scans `behaviors/*` for `behavior.json` marker files
3. **Code** validates structure for each feature's behaviors (naming, relationships, documentation)
4. **Code** outputs validation report with violations and warnings
5. **AI Agent** reviews validation report and presents findings to user

**Watcher Output Integration:**
* When `behavior_structure_watch()` runs and detects file changes, it automatically validates structure and outputs results to stderr
* The AI should automatically:
  1. Check if the watcher timestamp (`.cursor/watchers/last-run-structure.txt`) indicates a recent run (within last 5 minutes)
  2. If a validation was triggered, read any validation output from stderr or check for validation issues
  3. Present a summary of structure validation findings to the user in the chat window
  4. Highlight any structure issues that need fixing (naming violations, missing relationships, documentation problems)
  5. Suggest running `\behavior-structure fix` if auto-fixable issues are detected
* The AI should proactively monitor this timestamp and present validation results when the watcher runs

