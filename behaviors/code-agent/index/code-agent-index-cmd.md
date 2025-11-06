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
1. The user or AI agent runs `python command-runners/behavior-index-cmd.py` to generate the index
2. The code function `behavior_index()` scans features marked with `code-agent-behavior.json` (deployed: true) for behavior files
3. The code function detects changed or missing files
4. The code function skips draft or experimental behaviors
5. The code function **PRESERVES existing purposes from the index (code NEVER extracts or updates purposes)**
6. The code function sets placeholder purpose `"[AI should update this purpose after reviewing the file]"` for new files
7. The code function records feature name, file type, path, modification timestamp
8. The code function updates both local (`behaviors/<feature>/code-agent-index.json`) and global (`.cursor/behavior-index.json`) indexes
9. The code function prints summary with feature counts and last updated time
10. **The AI agent must review `.cursor/behavior-index.json` and update purposes for:**
    - New files (with placeholder purposes)
    - Files with unclear or nonsensical purposes
    - Files where the purpose needs refinement
11. **After the AI agent updates purposes in the global index, the user or AI agent runs `python command-runners/behavior-index-cmd.py sync-purposes` to copy the updated purposes from global to all local index files**
12. **The AI agent should consider running `\behavior-consistency` after indexing to validate for inconsistencies, overlaps, or contradictions in behaviors**

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