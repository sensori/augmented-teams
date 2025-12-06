---
execution:
  registry_key: ddd-interaction
  python_import: behaviors.ddd.ddd_runner.DDDInteractionCommand
  cli_runner: behaviors/ddd/ddd_runner.py
  actions:
    generate:
      cli: generate-interaction
      method: generate
    validate:
      cli: validate-interaction
      method: validate
    correct:
      cli: correct-interaction
      method: correct
  working_directory: workspace_root
---

### Command: `/ddd-interaction`

**[Purpose]:** Document domain concept interactions and business flows following DDD principles. Creates scenario-based documentation showing how domain concepts work together.

**[Rule]:**
* `/ddd-rule` — DDD principles:
  - Section 11: Domain interaction analysis principles

**Runner:**
* CLI: `python behaviors/ddd/ddd_runner.py generate-interaction [file-path]` — Document interactions
* CLI: `python behaviors/ddd/ddd_runner.py validate-interaction [interactions-file]` — Validate interactions
* CLI: `python behaviors/ddd/ddd_runner.py correct-interaction [file-path]` — Correct interactions based on errors and chat context

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/ddd-interaction` or `/ddd-interaction-generate`

2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("ddd-interaction", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **AI Agent** references `/ddd-rule.mdc` Section 11 to understand interaction documentation principles

4. **Runner** (`DDDInteractionCommand.generate()`) which documents interactions:
   - Discovers domain map file in same directory
   - Reads source code for implementation flows
   - Identifies business scenarios and triggers
   - Documents transformations, lookups, business rules
   - Maintains domain-level abstraction (no implementation details)
   - Generates scenario-based flows
   - Outputs to `<name>-domain-interactions.txt`

5. **Runner** which displays generated file path

6. **AI Agent** presents generation results to user

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews generated interaction flows and edits if needed

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation via `/ddd-interaction-validate`

2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("ddd-interaction", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **Runner** (`DDDInteractionCommand.validate()`) which validates interactions:
   - Checks abstraction level (§11.1 - no implementation details)
   - Checks scenario structure (§11.2 - trigger, actors, flow, rules, result)
   - Checks transformations are business-level (§11.3)
   - Checks lookups are business strategy (§11.4)
   - Checks business rules not code conditionals (§11.5)
   - Uses heuristics to detect all §11 violations

4. **Runner** which displays validation report

5. **AI Agent** presents validation results with recommendations

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** fixes violations and re-validates if needed

**ACTION 5: CORRECT**
**Steps:**
1. **User** invokes correction via `/ddd-interaction-correct [file-path] [chat-context]` when interactions file has validation errors or needs updates based on chat context

2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("ddd-interaction", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **AI Agent** references `/ddd-rule.mdc` Section 11 to understand how to correct interaction analysis based on:
   - Validation violations (if any) with line numbers and messages
   - Chat context provided by user
   - DDD principles from Section 11

4. **AI Agent** corrects the interactions file:
   - Fixes validation violations (if any)
   - Applies corrections based on chat context
   - Ensures interactions follow DDD principles (abstraction level, scenario structure, business-level transformations)
   - Updates interactions file directly

5. **AI Agent** presents correction results to user:
   - List of corrections made
   - Updated interactions file path
   - Next steps (re-validate, proceed to scaffold generation)
