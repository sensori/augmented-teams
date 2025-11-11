### Command: `/ddd-structure`

**[Purpose]:** Analyze code, text, or diagrams to extract domain structure following DDD principles. Creates hierarchical domain maps representing business concepts and relationships.

**[Rule]:**
* `/ddd-rule` — DDD principles:
  - Sections 1-10: Domain structure analysis principles

**Runner:**
* CLI: `python behaviors/ddd/ddd_runner.py generate-structure [file-path]` — Analyze and generate domain map
* CLI: `python behaviors/ddd/ddd_runner.py validate-structure [domain-map]` — Validate domain map against DDD principles

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/ddd-structure` or `/ddd-structure-generate`

2. **AI Agent** determines the file path to analyze (from user input or context)

3. **AI Agent** references `/ddd-rule.mdc` Sections 1-10 to understand domain structure principles

4. **Runner** (`DDDStructureCommand.generate()`) analyzes source and generates domain map:
   - Reads source file (code, text, diagram)
   - Extracts domain concepts and relationships
   - Applies DDD principles (outcome verbs, ordering, integration, etc.)
   - Generates hierarchical text format with tabs for nesting
   - Outputs to `<name>-domain-map.txt`

5. **Runner** displays generated file path

6. **AI Agent** presents generation results to user

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews generated domain map and edits if needed

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation via `/ddd-structure-validate`

2. **AI Agent** references `/ddd-rule.mdc` Sections 1-10 to validate domain structure

3. **Runner** (`DDDStructureCommand.validate()`) validates domain map:
   - Checks for communication verbs (§1)
   - Checks for separated system support (§2)
   - Checks ordering follows user mental model (§3)
   - Checks domain-first organization (§4)
   - Uses heuristics to detect all §1-10 violations

4. **Runner** displays validation report

5. **AI Agent** presents validation results with recommendations

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** fixes violations and re-validates if needed
2. **User** proceeds to `/ddd-interaction` to document business flows
