### Command: `behavior-structure-create-cmd.md`

**Purpose:** Scaffold a new AI behavior with all required files and proper structure.

**Usage:**
* `\behavior-structure create <feature> <behavior-name>` — create a new behavior with all files
* `\behavior-structure create <feature> <behavior-name> --no-implementation` — create behavior without Python file (for AI-only behaviors)

**What It Creates:**
1. Rule file (`<feature>-<behavior-name>-rule.mdc`) with template
2. Command file (`<feature>-<behavior-name>-cmd.md`) with template
3. Implementation file (`<feature>-<behavior-name>-cmd.py`) with template (only if automation serves a purpose)
4. Proper documentation structure in each file
5. Cross-references between related files

**Note:** If the Behavior Feature is missing an outline file (`<feature>-outline.md`), use `\behavior-structure fix` to create it. The outline should be updated manually after creating new behaviors.

**When to Use --no-implementation:**
* Use when the behavior is entirely AI-driven (no file operations, no automation needed)
* Examples: `behavior-suggest` (AI analyzes patterns), conversational behaviors
* The command file will note "No Python implementation needed — This is entirely AI-driven"

**Example:**
```bash
python code-agent-structure-cmd.py create code-agent-behavior test-behavior
```
Creates:
* `code-agent-test-behavior-rule.mdc`
* `code-agent-test-behavior-cmd.md`
* `code-agent-test-behavior-cmd.py`

**Rule:**
* `\code-agent-structure-rule` — Behavior structure and naming conventions

**Runner:**
`python behaviors/code-agent/code-agent-runner.py structure create <feature> <behavior-name> [--no-implementation]` — Scaffolds new behavior files

**Steps:**
1. **User** invokes command via `/behavior-structure create <feature> <behavior-name>`
2. **Code** (`Commands.structure(action="create", feature, behavior_name)`) calls `Feature.create(feature, behavior_name)` to scaffold new behavior
3. **Code** creates rule file with When/Then template and `**Executing Commands:**` section
4. **Code** creates command file with governance sections (`**Rule:**`, `**Runner:**`, `**Steps:**`)
5. **Code** creates optional runner file (if implementation needed)
6. **Code** displays list of created files with relative paths
7. **Code** suggests next steps (review templates, run `/code-agent-index`, run `/code-agent-structure validate`)
8. **AI Agent** reviews created files and confirms scaffolding to user

**Template Contents:**
* Rule file: When/then structure with Always/Never sections + `**Executing Commands:**` section
* Command file: Purpose, usage, steps + governance sections:
  * `**Rule:**` — Reference to rule this command follows
  * `**Runner:**` — Reference to runner (if applicable)
  * `**Steps:**` — Sequential execution steps

**Naming Pattern:**
* Files follow: `<feature>-<behavior-name>-<type>.<ext>`
* Function names: `<behavior_name>` (underscores, no hyphens)

**File Location:**
* All files created in `behaviors/<feature>/cursor/` (organized in Behavior Features - collections of tightly-knit, strongly related behaviors)
* Directory created if it doesn't exist
* **Behavior Features**: Keep behavior files belonging to the same feature together in one directory. Never scatter behaviors into separate areas or break them up by component type.

**Output Integration:**
* When `behavior_structure()` runs with action="create" and generates new files, the AI should automatically:
  1. Check the command output for created files
  2. Present a summary of created files to the user in the chat window:
     - List of files created with their paths
     - Note if implementation file was skipped (--no-implementation flag)
  3. Suggest next steps:
     - Review and edit the template content
     - Run `\behavior-index` to add the new behavior to the index
     - Run `\behavior-structure validate` to ensure structure compliance
* The AI should present creation results immediately after the command completes to show what was scaffolded

* **Behavior Features**: Keep behavior files belonging to the same feature together in one directory. Never scatter behaviors into separate areas or break them up by component type.

**Output Integration:**
* When `behavior_structure()` runs with action="create" and generates new files, the AI should automatically:
  1. Check the command output for created files
  2. Present a summary of created files to the user in the chat window:
     - List of files created with their paths
     - Note if implementation file was skipped (--no-implementation flag)
  3. Suggest next steps:
     - Review and edit the template content
     - Run `\behavior-index` to add the new behavior to the index
     - Run `\behavior-structure validate` to ensure structure compliance
* The AI should present creation results immediately after the command completes to show what was scaffolded
