### Command: `behavior-sync-cmd.md`

**Purpose:** Keep AI behaviors up to date across all features.

**Usage:**
* `\behavior-sync` — sync all behaviors
* `\behavior-sync <feature>` — sync a specific feature
* `python behaviors/code-agent-behavior/code-agent-sync-cmd.py watch` — watch for file changes and auto-sync

**File Routing Rules:**
1. Scans `behaviors/*` for `code-agent-behavior.json` with `"deployed": true`
2. **Only rule and command files** in marked features are synced
3. Files are routed to correct locations based on extension:
   * `.mdc` files → `.cursor/rules/`
   * `.md` files → `.cursor/commands/`
   * `.py` files → **NOT SYNCED** (runners stay in their feature directory: `behaviors/<feature>/`)
   * `.json` files:
     - `*-mcp.json` → `.cursor/mcp/` (merged if MCP configs exist)
     - `*-tasks.json` → Merged into root `.vscode/tasks.json` (tasks combined, duplicate labels avoided)

**Steps:**
1. **Code** (`behavior_sync()`) scans `behaviors/*` for `<feature>.json` or `code-agent-behavior.json` marker files with `deployed: true`
2. **Code** iterates through files in each feature, skipping:
   - Files in `docs/` directories (documentation only)
   - Files marked as "draft" or "experimental" in first 10 lines
3. **Code** routes files to correct destination based on extension:
   - `.mdc` → `.cursor/rules/`
   - `.md` → `.cursor/commands/`
   - `.py` → **SKIP** (runners remain in `behaviors/<feature>/`, commands reference local path)
   - `.json` → `.cursor/mcp/`
4. **Code** merges MCP configs (`*-mcp.json`) if they already exist
5. **Code** collects `*-tasks.json` files and merges their tasks into root `.vscode/tasks.json` (duplicate labels avoided)
6. **Code** overwrites only if source is newer (except for merged JSON files)
7. **Code** reports results (synced, merged, skipped counts)
8. **User** (optional) runs `\behavior-index` after syncing to update the behavior index

**Note:** Python runner files (`.py`) are intentionally NOT synced. Each feature maintains its own runners in `behaviors/<feature>/`, and commands reference them using local paths like `python behaviors/<feature>/<runner>.py`

**Rule Association:**
* Follow rules in `behaviors/*/cursor/rules/` folders when syncing
* Rules are associated with their respective features and should be maintained accordingly




**Rule:**
* `\behavior-sync-rule` — When a behavior is added or updated in a feature's `cursor/` folder, sync it to the corresponding location in `.cursor/`. Always preserve file structure, merge MCP configs and tasks.json, overwrite only if source is newer, and never sync draft/experimental behaviors.

**Implementation:**
* `behavior_sync(feature=None)` — Scans `behaviors/*/cursor/` folders, routes `.mdc` and `.md` files to `.cursor/`, merges MCP configs and tasks.json files, skips `.py` files (they stay local), skips draft/experimental markers, and reports sync results.
* `behavior_sync_watch()` — Watches for file changes in cursor directories and automatically syncs when files are modified (with 2-second debounce to batch changes).

**AI Usage:**
* Not needed for this command — it's a pure file operation that routes and merges files based on deterministic rules.

**Code Usage:**
* Always use code execution — this command performs file system operations (copying, merging JSON, checking timestamps) that require code execution.

<!-- Test change: 2024-12-19 14:47 -->