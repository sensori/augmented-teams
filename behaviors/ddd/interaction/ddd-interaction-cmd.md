### Command: `/ddd-interaction`

**[Purpose]:** Document domain concept interactions and business flows following DDD principles. Creates scenario-based documentation showing how domain concepts work together.

**[Rule]:**
* `/ddd-rule` — DDD principles:
  - Section 11: Domain interaction analysis principles

**Runner:**
* CLI: `python behaviors/ddd/ddd_runner.py generate-interaction [file-path]` — Document interactions
* CLI: `python behaviors/ddd/ddd_runner.py validate-interaction [interactions-file]` — Validate interactions

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/ddd-interaction` or `/ddd-interaction-generate`

2. **AI Agent** determines the file path (source code and domain map)

3. **AI Agent** references `/ddd-rule.mdc` Section 11 to understand interaction documentation principles

4. **Runner** (`DDDInteractionCommand.generate()`) documents interactions:
   - Discovers domain map file in same directory
   - Reads source code for implementation flows
   - Identifies business scenarios and triggers
   - Documents transformations, lookups, business rules
   - Maintains domain-level abstraction (no implementation details)
   - Generates scenario-based flows
   - Outputs to `<name>-domain-interactions.txt`

5. **Runner** displays generated file path

6. **AI Agent** presents generation results to user

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews generated interaction flows and edits if needed

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation via `/ddd-interaction-validate`

2. **AI Agent** references `/ddd-rule.mdc` Section 11 to validate interaction analysis

3. **Runner** (`DDDInteractionCommand.validate()`) validates interactions:
   - Checks abstraction level (§11.1 - no implementation details)
   - Checks scenario structure (§11.2 - trigger, actors, flow, rules, result)
   - Checks transformations are business-level (§11.3)
   - Checks lookups are business strategy (§11.4)
   - Checks business rules not code conditionals (§11.5)
   - Uses heuristics to detect all §11 violations

4. **Runner** displays validation report

5. **AI Agent** presents validation results with recommendations

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** fixes violations and re-validates if needed
