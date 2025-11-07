### Command: `behavior-index-cmd.md`

**Purpose:** Maintain an up-to-date index of all AI code agent behaviors across features.

**Usage:**
* `\behavior-index` — rebuild the global index
* `\behavior-index <feature>` — rebuild the index for one feature

**File Types Indexed:**
* `.mdc` files (rules)
* `.md` files (commands)
* `.py` files (functions)
* `.json` files (MCP configs)

**Steps:**
1. **User** or **AI Agent** invokes `/code-agent-index` or `/code-agent-index <feature>`
2. **Code** (`Commands.index(feature)`) calls `Feature.generate_index(feature)` to scan and index behaviors
3. **Code** scans features marked with `behavior.json` (deployed: true) for behavior files
4. **Code** detects changed or missing files
5. **Code** skips draft or experimental behaviors
6. **Code** preserves existing purposes from the index (code NEVER extracts or updates purposes)
7. **Code** sets placeholder purpose `"[AI should update this purpose after reviewing the file]"` for new files
8. **Code** records feature name, file type, path, modification timestamp
9. **Code** updates both local (`behaviors/<feature>/code-agent-index.json`) and global (`.cursor/behavior-index.json`) indexes
10. **Code** prints summary with feature counts and last updated time
11. **AI Agent** reviews `.cursor/behavior-index.json` and updates purposes for new files or unclear purposes
12. **AI Agent** (optional) runs `python behaviors/code-agent/code-agent-runner.py index sync-purposes` to copy updated purposes from global to local index files
13. **AI Agent** suggests running `/code-agent-consistency` to validate for inconsistencies, overlaps, or contradictions

**Purpose Management:**
* **Code role:** Code preserves existing purposes and sets placeholders for new files
* **AI role:** AI manually updates purposes in `.cursor/behavior-index.json` after reviewing file contents
* **Code NEVER extracts purposes from files** - this is exclusively an AI responsibility

**Output:**
The index contains entries with:
* `feature` - Feature name
* `file` - File name
* `type` - File extension (.mdc, .md, .py, .json)
* `path` - Full file path
* `modified` - Modification timestamp

**Cursor Environment Integration:**
* The Cursor environment **must constantly refer to `.cursor/behavior-index.json` during chat** to discover and use available commands, rules, functions, and MCP configs.
* This ensures the AI assistant has visibility into all available behaviors across all features.
* The index serves as the single source of truth for what behaviors are available.

**Rule:**
* `\behavior-index-rule` — [description of rule this command follows]

**Output Integration:**
* When `behavior_index()` runs and generates `.cursor/behavior-index.json`, the AI should automatically:
  1. Check if the index file has been recently updated (within last 5 minutes) by checking the `last_updated_timestamp` field
  2. Read the index JSON to understand what behaviors are available
  3. Present a summary of indexed behaviors to the user in the chat window:
     - Total number of behaviors indexed
     - Counts by type (.mdc, .md, .py, .json)
     - Counts by feature
     - Any new behaviors added since last check
  4. Highlight any behaviors with missing or unclear purposes that may need review
* The AI should proactively check this index file when:
  - The command is run manually (`\behavior-index`)
  - Behavior files are synced (as part of `\behavior-sync` workflow)
  - New behavior files are detected
* The index serves as the discovery mechanism - the AI must refer to it to know what commands, rules, and functions are available