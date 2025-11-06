# Behavior Index Feature

The **Behavior Index** feature maintains an up-to-date index of all AI behaviors across features, providing visibility into what behaviors exist, where they live, and which ones are active.

## Implementation

The behavior index is implemented in `code-agent-runner.py` via the `behavior_index()` function according to `code-agent-index-rule.mdc`.

### Rule Compliance

**Always:**
- ✅ Scans features marked with `behavior.json` (deployed: true)
- ✅ Records feature name, file type, path, and modification timestamp
- ✅ Updates global index (`.cursor/behavior-index.json`)
- ✅ Logs the number of behaviors detected and updated
- ✅ Uses `iterdir()` for direct directory scanning (not recursive glob)
- ✅ Filters out excluded files (runners, behavior.json, docs, __pycache__)

**Never:**
- ❌ Manually edit index files
- ❌ Include draft or experimental behaviors in the index
- ❌ Include documentation files from `docs/` directories

### Index Structure

The global index (`.cursor/behavior-index.json`) contains:

```json
{
  "last_updated": "Thu Nov  7 10:30:45 2024",
  "total_behaviors": 51,
  "features_count": 3,
  "behaviors": [
    {
      "feature": "code-agent",
      "file": "code-agent-structure-rule.mdc",
      "type": ".mdc",
      "path": "behaviors/code-agent/structure/code-agent-structure-rule.mdc",
      "modified_timestamp": 1730987445.123
    },
    ...
  ]
}
```

Each entry includes:
- `feature` - Feature name (directory name)
- `file` - File name
- `type` - File extension (.mdc, .md, .py, .json)
- `path` - Full file path (forward slashes, relative to project root)
- `modified_timestamp` - Last modification time (Unix timestamp)

### Indexing Logic

The indexer:
1. Finds all directories in `behaviors/` with `behavior.json` where `deployed: true`
2. For each feature directory:
   - Uses `iterdir()` to scan direct children
   - Checks `behavior.json` for `deployed: true`
   - Recursively finds all behavior files with `rglob()`
   - Filters by extension (`.mdc`, `.md`, `.py`, `.json`)
   - Excludes:
     - `behavior.json` files
     - Runner files (`*-runner.py`)
     - Index files (`*-index.json`)
     - `__pycache__` directories
     - `docs/` directories
3. Writes consolidated index to `.cursor/behavior-index.json`

### File Structure

```
behaviors/<feature>/
  ├── behavior.json                    ← Marker file (deployed: true)
  ├── <feature>-runner.py              ← Excluded from index
  ├── <behavior-group>/
  │   ├── <feature>-<behavior>-rule.mdc       ← Indexed
  │   ├── <feature>-<behavior>-cmd.md         ← Indexed
  │   └── <feature>-<behavior>-index.json     ← Excluded from index
  └── docs/                            ← Excluded from index
      └── <feature>-<behavior>.md
```

### Usage

```bash
# Index all features
python behaviors/code-agent/code-agent-runner.py index

# Index specific feature
python behaviors/code-agent/code-agent-runner.py index <feature-name>
```

**Important:** When running with flags like `--no-guard`, the argument parser now correctly filters them out so they don't get treated as feature names.

### Output

The script provides detailed reporting:
- ✅ **Indexed**: Number of behaviors indexed
- 📁 **Features**: Number of features processed
- ⏭️ **Skipped**: Files skipped (if any)

Example output:
```
✅ Indexed 51 behaviors across 3 features
```

### Cursor Environment Integration

The Cursor environment should refer to `.cursor/behavior-index.json` to discover available behaviors. The index provides:

* Complete visibility into all available behaviors across all features
* File locations and types for commands, rules, and configs
* Modification timestamps for freshness tracking
* Single source of truth for what behaviors are deployed

### Integration with Workflow

The index integrates with your behavior workflow:

```
1. Edit behavior files in behaviors/<feature>/
2. Run sync: python behaviors/code-agent/code-agent-runner.py sync
3. Run index: python behaviors/code-agent/code-agent-runner.py index
4. Updated index reflects all deployed behaviors
```

### Troubleshooting

**Issue:** Indexer returns 0 behaviors
- **Cause:** Argument parsing treating flags as feature names
- **Fix:** Updated argument parser to filter out `--no-guard` and `--from-command` flags

**Issue:** Wrong features indexed
- **Cause:** Using `glob("**/behavior.json")` which is recursive
- **Fix:** Changed to `iterdir()` for direct directory scanning

## Related Files

- `code-agent-index-rule.mdc` - The rule definition
- `code-agent-index-cmd.md` - Command documentation
- `code-agent-runner.py` - Implementation (`behavior_index()` function)
- `.cursor/behavior-index.json` - Global index output
