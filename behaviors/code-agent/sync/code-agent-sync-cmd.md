---
execution:
  registry_key: code-agent-sync
  python_import: behaviors.code-agent.code_agent_runner.SyncIndexCommand
  cli_runner: behaviors/code-agent/code_agent_runner.py
  actions:
    generate:
      cli: sync
      method: generate
    validate:
      cli: validate-sync
      method: validate
    correct:
      cli: correct-sync
      method: correct
  working_directory: workspace_root
---

### Command: `/code-agent-sync`

**[Purpose]:** Synchronize all commands and rules from behaviors folders (or any folder) with deployed=true to cursor deployed areas (.cursor/rules/, .cursor/commands/, .cursor/mcp/, .vscode/tasks.json), then update behavior index (.cursor/behavior-index.json)

**[Rule]:**
* Rule file containing principles regarding behavior patterns, including command generation and validation

**Execution:**
* **Python Import** (Preferred): Import and call `SyncIndexCommand().generate()` from `behaviors.code_agent.code_agent_runner.SyncIndexCommand`
* **CLI** (Fallback): `python behaviors/code-agent/code_agent_runner.py sync [feature-name] [--force] [--target-dirs]`

**Runner:**
* CLI: `python behaviors/code-agent/code_agent_runner.py sync [feature-name] [--force] [--target-dirs]` — Execute full workflow (Sync → Index if changes)
* CLI: `python behaviors/code-agent/code_agent_runner.py generate-sync [feature-name] [--force] [--target-dirs]` — Generate only
* CLI: `python behaviors/code-agent/code_agent_runner.py validate-sync [feature-name] [--force] [--target-dirs]` — Validate only
* CLI: `python behaviors/code-agent/code_agent_runner.py correct-sync [feature-name] [--force] [--target-dirs]` — Correct sync based on errors and chat context

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/code-agent-sync` and generate has not been called for this command, command cli invokes generate action
OR
1. **User** explicitly invokes command via `/code-agent-sync-generate`

2. **AI Agent** (using `SyncIndexCommand.generate()`) determines the command parameters (feature-name (optional), --force flag (optional), --target-dirs (optional list)) from user input or context
3. **AI Agent** references rule file to understand how to synchronize commands, rules, and configuration files that follows all the principles specified in the rule file
4. **Runner** (`SyncIndexCommand.generate()`) synchronizes the commands, rules, and configuration files according to the principles specified in the rule file:
   - **Code**: `base_rule.resolve_target_directories(target_directories, workspace_root)` → Returns List[Path]. Resolves target directories, defaults to behaviors/ if not provided.
   - **Code**: `base_rule.discover_deployed_features(target_dirs)` → Returns List[FeatureInfo]. Scans directories for behavior.json files with deployed=true, returns feature info objects.
   - **Code**: `SyncCommand._sync_all_files(target_dirs)` → Returns Dict with sync results. Orchestrates sync for all features, returns counts and feature list.
   - **Code**: `SyncCommand._sync_feature_files(feature_info)` → Returns Dict with synced/merged/skipped counts. Processes all files in feature directory.
   - **Code**: `FileRouter(workspace_root).route_file(file_path)` → Returns Optional[Path]. Routes .mdc → .cursor/rules/, -cmd.md → .cursor/commands/, -mcp.json → .cursor/mcp/, -tasks.json → .vscode/tasks.json.
   - **Code**: `FileSyncer(router, merger, force).should_sync_file(source, dest)` → Returns bool. Checks if source is newer than dest (or force=true), returns True if should sync.
   - **Code**: `FileSyncer.sync_single_file(source, dest)` → Returns bool. Creates dest parent dirs, merges JSON files or copies with shutil.copy2(), returns True if synced.
   - **Code**: `JsonMerger().merge_mcp_config(source, dest)` → Returns Dict. Merges MCP configs, combines arrays, avoids duplicates, writes merged config.
   - **Code**: `JsonMerger().merge_tasks_json(source, dest)` → Returns Dict. Merges tasks arrays, avoids duplicate labels, writes merged tasks.json.
   - **Code**: `IndexCommand._index_all_behaviors(target_dirs)` → Returns Dict with indexed count. Scans features, builds index entries, writes to .cursor/behavior-index.json and local indexes.
5. **Runner** which displays sync results: features processed, files synced, files merged, files skipped
6. **AI Agent** presents sync results to user:
Sync results include:
   - Number of features processed
   - Number of files synced
   - Number of files merged
   - Number of files skipped
   - List of features processed
   - Index update status (if index ran or was skipped)

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews synced files and adds/edits content:
   - Review synced files in .cursor/rules/, .cursor/commands/, .cursor/mcp/
   - Verify merged MCP configs and tasks.json are correct
   - Check behavior index was updated correctly

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation (implicit when calling `/code-agent-sync` again, or explicit `/code-agent-sync-validate`)
2. **AI Agent** determines parameters from user input or context
3. **AI Agent** references rule file to validate if synchronized commands, rules, and configuration files follow all the principles specified in the rule file
4. **Runner** (`SyncIndexCommand.validate()`) validates if the synchronized files follow the principles specified in the rule file:
    - scans content using validation heuristics in runner
        - Verify sync destinations exist and files were routed correctly
        - Verify merge logic worked correctly for MCP configs and tasks.json
        - Verify exclusion logic correctly skipped docs/, .py files, drafts
        - Verify timestamp comparison logic worked correctly
        - Verify index structure is correct (JSON format, required fields present)
        - Verify index preserves existing purposes and sets placeholders for new files
        - Verify all code agents have minimum required command files (main command, generate delegate, validate delegate, correct delegate)
5. **AI Agent** presents validation results to user: summary of validation status, list of violations to fix (if any), confirmation when validation passes, and next steps (review synced files, verify merges, check index updates)

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** reviews validation results and fixes violations if needed
2. **User** optionally calls execute, generate, or validate as needed

**ACTION 5: CORRECT**
**Steps:**
1. **User** invokes correction via `/code-agent-sync-correct [feature-name] [chat-context]` when sync has validation errors or needs updates based on chat context

2. **AI Agent** reads sync results and validation errors (if any), plus chat context provided by user
3. **AI Agent** references rule file to understand how to correct sync operations based on:
   - Validation violations (if any) with details
   - Chat context provided by user
   - Code agent principles from rule file

4. **AI Agent** corrects sync operations:
   - Fixes validation violations (if any)
   - Applies corrections based on chat context
   - Ensures sync follows code agent principles
   - Updates synced files or sync configuration as needed

5. **AI Agent** presents correction results to user:
   - List of corrections made
   - Updated file paths
   - Next steps (re-validate, re-sync if needed)
