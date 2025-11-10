### Command: `/code-agent-sync`

**[Purpose]:** Synchronize all commands and rules from behaviors folders (or any folder) with deployed=true to cursor deployed areas (.cursor/rules/, .cursor/commands/, .cursor/mcp/, .vscode/tasks.json), then update behavior index (.cursor/behavior-index.json)

**[Rule]:**
* Rule file containing principles regarding behavior patterns, including command generation and validation

**Runner:**
* CLI: `python behaviors/code-agent/code_agent_runner.py sync [feature-name] [--force] [--target-dirs]` — Execute full workflow (Sync → Index if changes)
* CLI: `python behaviors/code-agent/code_agent_runner.py generate-sync [feature-name] [--force] [--target-dirs]` — Generate only
* CLI: `python behaviors/code-agent/code_agent_runner.py validate-sync [feature-name] [--force] [--target-dirs]` — Validate only

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/code-agent-sync` and generate has not been called for this command, command cli invokes generate action
OR
1. **User** explicitly invokes command via `/code-agent-sync-generate`

2. **AI Agent** (using `SyncIndexCommand.generate()`) determines the command parameters (feature-name (optional), --force flag (optional), --target-dirs (optional list)) from user input or context
3. **AI Agent** references rule file to understand how to synchronize commands, rules, and configuration files that follows all the principles specified in the rule file
4. **Runner** (`SyncIndexCommand.generate()`) synchronizes the commands, rules, and configuration files according to the principles specified in the rule file, specifically the following sync operations:
Sync operations include:
   - Discover deployed features by scanning target directories for behavior.json files with deployed=true
   - Route files to appropriate destinations based on file extension (.mdc → .cursor/rules/, .md → .cursor/commands/, *-mcp.json → .cursor/mcp/, *-tasks.json → .vscode/tasks.json)
   - Sync files using timestamp comparison (only sync if source newer than destination, unless --force flag is used)
   - Merge MCP configs and tasks.json files (combine arrays, avoid duplicates)
   - Copy other files using shutil.copy2() (preserves metadata)
   - Update behavior index (.cursor/behavior-index.json and local behaviors/<feature>/behavior-index.json) only if sync made changes
5. **Runner** displays sync results: features processed, files synced, files merged, files skipped
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
3. **AI Agent** references rule file to validate if synchronized commands, rules, and configuration files follow all the principles specified in the rule file
4. **Runner** (`SyncIndexCommand.validate()`) validates if the synchronized files follow the principles specified in the rule file
    - scans content using validation heuristics in runner
        - Verify sync destinations exist and files were routed correctly
        - Verify merge logic worked correctly for MCP configs and tasks.json
        - Verify exclusion logic correctly skipped docs/, .py files, drafts
        - Verify timestamp comparison logic worked correctly
        - Verify index structure is correct (JSON format, required fields present)
        - Verify index preserves existing purposes and sets placeholders for new files
5. **AI Agent** presents validation results to user: summary of validation status, list of violations to fix (if any), confirmation when validation passes, and next steps (review synced files, verify merges, check index updates)

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** reviews validation results and fixes violations if needed
2. **User** optionally calls execute, generate, or validate as needed
