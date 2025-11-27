### Command: `/story-arrange`

**Purpose:** Arrange and validate story map folder structure to match story map document. Creates/updates/moves folders based on the story map hierarchy, never deleting files (moves to archive instead).

**Rule:**
* `/stories-rule` — Story writing practices and standards, including epic/feature/story hierarchy structure

**Runner:**
* CLI: `python behaviors/stories/stories_runner.py execute-arrange [story-map-file]` — Execute full workflow (Generate → User Review → Validate)
* CLI: `python behaviors/stories/stories_runner.py generate-arrange [story-map-file]` — Generate folder structure only
* CLI: `python behaviors/stories/stories_runner.py validate-arrange [story-map-file]` — Validate folder structure matches story map

**⚠️ EXECUTION CONTEXT FOR AI AGENTS:**
* **Working Directory**: ALWAYS run commands from workspace root (`C:\dev\augmented-teams` or equivalent)
* **Path Format**: Use forward slashes `/` or escaped backslashes `\\` in Python paths. For PowerShell commands, use backslashes `\`
* **PowerShell Syntax**: Use semicolon `;` to chain commands, NOT `&&`. Example: `cd C:\dev\augmented-teams; python behaviors\stories\stories_runner.py arrange story-map.md`
* **Path Resolution**: Runner paths are relative to workspace root
* **Before Running**: Always ensure you're in workspace root

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/story-arrange` or explicitly via `/story-arrange-generate`

2. **AI Agent** determines the story map file location (from user input or context)
   - Story map file location: `<solution-folder>/docs/stories/map/[product-name]-story-map.md`

3. **AI Agent** references `/stories-rule.mdc` to understand the epic/feature/story hierarchy structure

4. **Runner** (`StoryArrangeCommand.generate()`) generates the folder structure according to the story map:
   - **Location**: Epic/feature folders created INSIDE `<solution-folder>/docs/stories/map/`
   - **Exact Structure**:
     ```
     <solution-folder>/docs/stories/map/
     ├── [product-name]-story-map.md
     ├── 🎯 Epic Name/
     │   ├── ⚙️ Feature Name/
     │   │   └── 📝 Story Name.md
     │   └── ⚙️ Another Feature/
     └── 🎯 Another Epic/
     ```
   - **Parse Story Map**: Extract epic and feature names from story map document
   - **Create Folders**: Create `🎯 Epic Name/⚙️ Feature Name/` folder structure INSIDE `map/` directory
   - **Story Files Deferred**: Story stub files NOT created (will be created during `/story-specification` phase)
   - **Archive Old Folders**: Move obsolete folders to `map/z_archive/[timestamp]/` (NEVER delete)
   - **Move Files**: Move existing files to new folder locations if hierarchy changed
   - **Detect Merge Candidates**: If multiple files exist for same entity, archive ALL to `map/z_archive/[timestamp]/`
   - **Generate Merge List**: Create `merge-list.md` with AI prompts for each merge needed
   - **Update Paths**: Update any internal file references to reflect new structure
   - **Report**: Display summary of folders created, moved, archived, and merges needed

5. **Runner** displays:
   - Folders created (with paths)
   - Folders moved/archived (from → to)
   - Files moved (from → to)
   - Files archived (with timestamp)
   - Merge list created (if merge candidates found): `merge-list.md`

6. **AI Agent** presents arrangement results to user:
   - Summary of folder structure changes
   - List of created folders
   - List of moved/archived folders and files
   - Location of archive folder: `archive/[timestamp]/`
   - Location of merge list (if created): `merge-list.md`
   - Next steps (review changes, merge files if needed, run validation)

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews arranged folder structure:
   - Verify `epic-[name]/feature-[name]/` folders match story map
   - Check archived files in `archive/[timestamp]/` folder
   - Verify moved files are in correct locations
   - Review `merge-list.md` for merge candidates (if exists)
   - Use AI prompts in merge list to merge files
   - Manually adjust if needed

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation via `/story-arrange-validate`

2. **AI Agent** references `/stories-rule.mdc` to understand expected hierarchy structure

3. **Runner** (`StoryArrangeCommand.validate()`) validates folder structure matches story map:
   - **Parse Story Map**: Extract epic and feature names from story map document
   - **Check Folders Exist**: Verify each epic/feature has corresponding folder
   - **Check Missing Folders**: Identify epics/features in story map without folders
   - **Check Extra Folders**: Identify folders that don't match any epic/feature in story map
   - **Check Naming**: Verify folder names follow `epic-[name]/feature-[name]/` pattern
   - **Generate Report**: Create validation report with mismatches

4. **Runner** displays validation report:
   - ✅ Folders matching story map (count)
   - ❌ Missing folders (epic/feature in story map, no folder exists)
   - ⚠️ Extra folders (folder exists, not in story map)
   - ⚠️ Naming violations (folders not following `epic-[name]/feature-[name]/` pattern)
   - Summary: PASS/FAIL with mismatch count

5. **AI Agent** presents validation results to user:
   - Validation status (PASS/FAIL)
   - List of missing folders (need to be created)
   - List of extra folders (may need to be archived)
   - List of naming violations (need to be renamed)
   - Next steps (re-arrange if failed, proceed if passed)

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** reviews validation results and decides:
   - Re-run arrange to fix mismatches
   - Manually adjust folder structure
   - Update story map to reflect current structure

**Notes:**
- **NEVER DELETE FILES**: All removals move to `map/z_archive/[timestamp]/` folder
- **Folder Naming**: Use emoji prefixes: `🎯 Epic Name`, `⚙️ Feature Name`, `📝 Story Name.md`
- **Archive Structure**: `<solution-folder>/docs/stories/map/z_archive/[YYYYMMDD-HHMMSS]/[original-path]`
- **Story Map Location**: `<solution-folder>/docs/stories/map/[product-name]-story-map.md`
- **Epic Folders Location**: INSIDE `<solution-folder>/docs/stories/map/` (not at stories/ level)
- **Story Files**: Created with basic template during Arrange phase (elaborated in Discovery/Exploration)
- **Merge List Format**: `merge-list.md` contains AI prompts for each merge:
  ```markdown
  ## Merge 1: [Epic/Feature Name]
  **Target Location**: `epic-[name]/feature-[name]/[entity]-doc.md`
  **Source Files** (archived):
  - `archive/[timestamp]/path/to/file1.md`
  - `archive/[timestamp]/path/to/file2.md`
  
  **AI Prompt**:
  "Merge the following files into a single [entity] document at [target-location]. 
  Review both archived files, preserve all unique content, resolve conflicts by 
  keeping most recent/complete information, and create a unified document."
  ```
