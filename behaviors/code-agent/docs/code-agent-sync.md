# Behavior Sync Feature

The **Behavior Sync** feature keeps feature-local AI behaviors in sync with the global `.cursor/` environment so the IDE agent always sees the latest rules, commands, and tools.

## Implementation

The behavior sync is implemented in `code-agent-runner.py` via the `behavior_sync()` function according to `code-agent-sync-rule.mdc`.

### Rule Compliance

**Always:**
- ✅ Syncs files from features marked with `behavior.json` (deployed: true)
- ✅ Routes files by extension to correct destinations
- ✅ Merges MCP configs (`*-mcp.json`) if they already exist
- ✅ Overwrites only if the source is newer (unless `--force` flag used)
- ✅ Logs synced and merged files
- ✅ Skips files marked as "draft" or "experimental"
- ✅ Skips files in `docs/` directories

**Never:**
- ❌ Edit `.cursor/` files directly (they're generated)
- ❌ Sync behaviors marked as "draft" or "experimental"
- ❌ Sync documentation files from `docs/` directories

### File Structure & Routing

**All files** in features marked with `behavior.json` (deployed: true) are synced to their destination:

```
behaviors/<feature>/
  ├── <rule-name>.mdc          → .cursor/rules/
  ├── <command-name>.md         → .cursor/commands/
  └── <tool-name>-mcp.json      → .cursor/mcp/ (merged if exists)
```

**Routing Rules:**
- `.mdc` files → `.cursor/rules/`
- `.md` files → `.cursor/commands/`
- `.json` files (MCP configs) → `.cursor/mcp/` (merged for existing files)

**Excluded from sync:**
- `behavior.json` files
- Runner files (`*-runner.py`)
- Index files (`*-index.json`)
- Documentation directories (`docs/`)
- Draft/experimental files (marked in frontmatter)

### Usage

```bash
# Sync all features
python behaviors/code-agent/code-agent-runner.py sync

# Sync specific feature
python behaviors/code-agent/code-agent-runner.py sync <feature-name>

# Force sync (overwrite regardless of timestamps)
python behaviors/code-agent/code-agent-runner.py sync --force
```

### Sync Logic

The sync process:
1. Finds all directories with `behavior.json` where `deployed: true`
2. For each feature directory:
   - Recursively finds all behavior files (`.mdc`, `.md`, `.json`)
   - Skips excluded files and directories
   - Checks for draft/experimental markers in file content
   - Routes files to appropriate destinations
   - For MCP configs: merges with existing if present
   - For other files: copies only if source is newer (or `--force` used)

### Output

The script provides detailed reporting:
- ✅ **Synced**: Files copied to `.cursor/`
- 🔄 **Merged**: MCP configs merged (preserves existing + adds new)
- ⏭️ **Skipped**: Files skipped due to:
  - Draft/experimental markers
  - Source not newer than destination
  - Merge/copy errors

Example output:
```
Processing feature: code-agent
✅ Synced code-agent-structure-rule.mdc → .cursor/rules/
✅ Synced code-agent-structure-validate-cmd.md → .cursor/commands/
⏭️  Skipped code-agent-runner.py (excluded file)

============================================================
Behavior Sync Report
============================================================
✅ Synced: 15 files
🔄 Merged: 2 files
⏭️  Skipped: 8 files
```

### Integration with Workflow

The sync integrates with your behavior workflow:

```
1. Edit behavior file in behaviors/<feature>/
2. Run sync: python behaviors/code-agent/code-agent-runner.py sync
3. Files deployed to .cursor/
4. Run index: python behaviors/code-agent/code-agent-runner.py index
5. Cursor environment sees updated behaviors
```

### Post-Sync Actions

After syncing, run the indexer to update the behavior index:
```bash
python behaviors/code-agent/code-agent-runner.py index
```

## Related Files

- `code-agent-sync-rule.mdc` - The rule definition
- `code-agent-sync-cmd.md` - Command documentation
- `code-agent-runner.py` - Implementation (`behavior_sync()` function)
