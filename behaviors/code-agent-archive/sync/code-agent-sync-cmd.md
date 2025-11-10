### Command: `code-agent-sync-cmd.md`

**Purpose:** Keep AI behaviors up to date across all features.

**Usage:**
* `/code-agent-sync` — sync all behaviors
* `/code-agent-sync <feature>` — sync a specific feature
* `python behaviors/code-agent/code-agent-runner.py sync [feature] [--force]` — sync from command line
* `python behaviors/code-agent/code-agent-runner.py sync watch` — watch for file changes and auto-sync

**File Routing Rules:**
1. Scans `behaviors/*` for `behavior.json` with `"deployed": true`
2. **Only rule and command files** in marked features are synced
3. Files are routed to correct locations based on extension:
   * `.mdc` files → `.cursor/rules/`
   * `.md` files → `.cursor/commands/`
   * `.py` files → **NOT SYNCED** (runners stay in their feature directory: `behaviors/<feature>/`)
   * `.json` files:
     - `*-mcp.json` → `.cursor/mcp/` (merged if MCP configs exist)
     - `*-tasks.json` → Merged into root `.vscode/tasks.json` (tasks combined, duplicate labels avoided)

**Steps:**
1. **Code** (`Feature.sync(feature, force)`) scans `behaviors/*` for `behavior.json` marker files with `deployed: true`
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
8. **User** (optional) runs `/code-agent-index` after syncing to update the behavior index

**Rule:**
* `/code-agent-sync-rule` — Sync behaviors from features to deployed locations, preserve structure, merge configs, skip drafts

**Runner:**
`python behaviors/code-agent/code-agent-runner.py sync [feature] [--force]` — Syncs behavior files to .cursor/ deployment locations

**Note:** Python runner files (`.py`) are intentionally NOT synced. Each feature maintains its own runners in `behaviors/<feature>/`, and commands reference them using local paths like `python behaviors/<feature>/<runner>.py`

