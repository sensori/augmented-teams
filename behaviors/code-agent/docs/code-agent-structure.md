# Behavior Structure Feature

The **Behavior Structure** feature standardizes how AI behaviors are organized, named, and related. It ensures consistency and discoverability across all behaviors.

## Implementation

The behavior structure is implemented in `code-agent-runner.py` according to `code-agent-structure-rule.mdc`.

### Rule Compliance

**Always:**
- ✅ Name files using `<feature>-<behavior-name>-<type>.<ext>` pattern
- ✅ For rules with multiple commands, add a verb suffix: `<feature>-<behavior-name>-<verb>-cmd.md`
- ✅ Keep each behavior in its own feature folder under `behaviors/<feature>/` (mark with `behavior.json`)
- ✅ Organize related behaviors into subdirectories (e.g., `structure/`, `index/`, `consistency/`)
- ✅ Link related files by prefix (same `<feature>-<behavior-name>` prefix)
- ✅ Rules must reference the commands that execute them: `**Executing Commands:**`
- ✅ Commands must include:
  - `**Rule:**` - Which rule this command follows
  - `**Runner:**` - Runner function and invocation (one-liner)
  - `**Steps:**` - Sequential actions to execute (REQUIRED)
- ✅ Rules must start with `**When** <event> condition,` (after frontmatter if present)
- ✅ Include a short description at the top of every rule and command file

**Never:**
- ❌ Mix unrelated behaviors in the same folder
- ❌ Use ambiguous names like `new-rule.mdc` or `temp-cmd.md`
- ❌ Leave files undocumented or unreferenced
- ❌ Include deprecated sections: `**AI Usage:**`, `**Code Usage:**`, `**Implementation:**`

### Naming Patterns

* Rules: `<feature>-<behavior-name>-rule.mdc` (no verb suffix)
* Commands: `<feature>-<behavior-name>-cmd.md` OR `<feature>-<behavior-name>-<verb>-cmd.md` (e.g., `validate-cmd.md`, `fix-cmd.md`)
* Runners: `<feature>-runner.py` (feature-level) OR `<feature>-<behavior>-runner.py` (behavior-level)
* MCP: `<feature>-<tool-name>-mcp.json`

### Consolidated Runner Pattern

Code-agent uses a **consolidated runner** approach where all behaviors share a single Python file:

```
behaviors/code-agent/
  ├── code-agent-runner.py          ← Single runner for all behaviors
  ├── structure/
  │   ├── code-agent-structure-rule.mdc
  │   ├── code-agent-structure-validate-cmd.md
  │   ├── code-agent-structure-fix-cmd.md
  │   └── code-agent-structure-create-cmd.md
  ├── sync/
  │   ├── code-agent-sync-rule.mdc
  │   └── code-agent-sync-cmd.md
  └── index/
      ├── code-agent-index-rule.mdc
      └── code-agent-index-cmd.md
```

**Runner invocation:**
```bash
python behaviors/code-agent/code-agent-runner.py structure validate
python behaviors/code-agent/code-agent-runner.py sync
python behaviors/code-agent/code-agent-runner.py index
```

### Relationship Sections

**Rules** must include:
- `**Executing Commands:**` section listing which commands execute the rule

**Commands** must include:
- `**Rule:**` — Which rule this command follows
- `**Runner:**` — One-liner specifying runner function: `behavior_structure()` in `code-agent-runner.py`
- `**Steps:**` — Sequential actions to execute (REQUIRED)
  - Each step must specify who/what performs it (AI agent, code function, user, MCP tool)
  - Example: "The code function `behavior_structure()` validates all behavior files..."

**Deprecated sections (DO NOT USE):**
- ~~`**AI Usage:**`~~ - Replaced by `**Steps:**`
- ~~`**Code Usage:**`~~ - Replaced by `**Steps:**`
- ~~`**Implementation:**`~~ - Replaced by `**Runner:**`

### Actions

The behavior structure command supports three actions:

#### 1. Validate

Checks structure compliance:
- File names follow naming pattern
- Rule-command linkages exist
- Relationship sections are present (`**Executing Commands:**`, `**Rule:**`, `**Steps:**`)
- Rules start with `**When**` (after frontmatter)
- Related files share consistent prefixes
- No deprecated sections present
- Specialization files are properly declared in `behavior.json`

```bash
# Validate all behaviors
python behaviors/code-agent/code-agent-runner.py structure validate

# Validate specific feature
python behaviors/code-agent/code-agent-runner.py structure validate <feature>
```

#### 2. Fix

Automatically fixes structure issues:
- Creates missing command files for existing rules
- Adds missing relationship sections to rules and commands
- Adds basic documentation headers to empty files

```bash
# Fix all behaviors
python behaviors/code-agent/code-agent-runner.py structure fix

# Fix specific feature
python behaviors/code-agent/code-agent-runner.py structure fix <feature>
```

#### 3. Create

Scaffolds a new behavior with all required files:
- Rule file with When/then structure
- Command file with relationship sections

```bash
# Create new behavior
python behaviors/code-agent/code-agent-runner.py structure create <feature> <behavior-name>
```

### File Structure

```
behaviors/<feature>/
  ├── behavior.json                    ← Feature marker (deployed: true)
  ├── <feature>-runner.py              ← Consolidated runner
  ├── <behavior-group>/                ← Subdirectory for related behaviors
  │   ├── <feature>-<behavior>-rule.mdc
  │   ├── <feature>-<behavior>-validate-cmd.md
  │   ├── <feature>-<behavior>-fix-cmd.md
  │   └── <feature>-<behavior>-create-cmd.md
  └── docs/                            ← Documentation (excluded from validation)
      └── <feature>-<behavior>.md
```

### Multiple Commands Per Rule

When a rule has multiple commands (e.g., validate, fix, create), use verb suffixes:
- `code-agent-structure-rule.mdc` relates to:
  - `code-agent-structure-validate-cmd.md`
  - `code-agent-structure-fix-cmd.md`
  - `code-agent-structure-create-cmd.md`

The validation uses prefix-based matching and allows commands in the same directory or subdirectories.

### Specialization Pattern

Some behaviors support **specialization** for framework/language variations:
- Base rule defines common behavior
- Specialized rules extend for specific contexts
- Reference files provide examples
- Declared in `behavior.json` with `isSpecialized: true`

Example: BDD testing has base rule + Jest/Mamba specializations

### Index Files

Index files (`*-index.json`) are excluded from validation and stored in feature directories.

## Related Files

- `code-agent-structure-rule.mdc` - The rule definition
- `code-agent-structure-validate-cmd.md` - Validate command documentation
- `code-agent-structure-fix-cmd.md` - Fix command documentation
- `code-agent-structure-create-cmd.md` - Create command documentation
- `code-agent-runner.py` - Consolidated implementation
