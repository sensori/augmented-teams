---
execution:
  registry_key: ddd-structure
  python_import: behaviors.ddd.ddd_runner.DDDStructureCommand
  cli_runner: behaviors/ddd/ddd_runner.py
  actions:
    generate:
      cli: generate-structure
      method: generate
    validate:
      cli: validate-structure
      method: validate
    correct:
      cli: correct-structure
      method: correct
  working_directory: workspace_root
---

### Command: `/ddd-structure`

**[Purpose]:** Analyze code, text, or diagrams to extract domain structure following DDD principles. Creates hierarchical domain maps representing business concepts and relationships.

**[Rule]:**
* `/ddd-rule` — DDD principles:
  - Sections 1-10: Domain structure analysis principles

**Runner:**
* CLI: `python behaviors/ddd/ddd_runner.py generate-structure [file-path]` — Analyze and generate domain map
* CLI: `python behaviors/ddd/ddd_runner.py validate-structure [domain-map]` — Validate domain map against DDD principles
* CLI: `python behaviors/ddd/ddd_runner.py correct-structure [file-path]` — Correct domain map based on errors and chat context

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/ddd-structure` or `/ddd-structure-generate`

2. **AI Agent** determines the file path to analyze (from user input or context) 3. **AI Agent** references `/ddd-rule.mdc` Sections 1-10 to understand domain structure principles

4. **Runner** (`DDDStructureCommand.generate()`) which analyzes source and generates domain map:
   - Reads source file (code, text, diagram)
   - Extracts domain concepts and relationships
   - Applies DDD principles (outcome verbs, ordering, integration, etc.)
   - Generates hierarchical text format with tabs for nesting
   - Outputs to `<name>-domain-map.txt`

5. **Runner** which displays generated file path

6. **AI Agent** presents generation results to user

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews generated domain map and edits if needed

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation via `/ddd-structure-validate`

2. **AI Agent** determines the domain map file to validate (from user input or context) 3. **Runner** (`DDDStructureCommand.validate()`) which validates domain map:
   - Checks for communication verbs (§1)
   - Checks for separated system support (§2)
   - Checks ordering follows user mental model (§3)
   - Checks domain-first organization (§4)
   - Uses heuristics to detect all §1-10 violations

4. **Runner** which displays validation report

5. **AI Agent** presents validation results with recommendations

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** fixes violations and re-validates if needed
2. **User** proceeds to `/ddd-interaction` to document business flows

**ACTION 5: CORRECT**
**Steps:**
1. **User** invokes correction via `/ddd-structure-correct [file-path] [chat-context]` when domain map has validation errors or needs updates based on chat context

2. **AI Agent** reads domain map file and validation errors (if any), plus chat context provided by user,    - Calls `execute_command("ddd-structure", "correct", **params)` where params include file_path and chat_context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
3. **AI Agent** references `/ddd-rule.mdc` Sections 1-10 to understand how to correct domain structure based on:
   - Validation violations (if any) with line numbers and messages
   - Chat context provided by user
   - DDD principles from Sections 1-10

4. **AI Agent** corrects the domain map file:
   - Fixes validation violations (if any)
   - Applies corrections based on chat context
   - Ensures domain map follows DDD principles
   - Updates domain map file directly

5. **AI Agent** presents correction results to user:
   - List of corrections made
   - Updated domain map file path
   - Next steps (re-validate, proceed to interaction analysis)
