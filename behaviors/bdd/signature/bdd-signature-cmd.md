---
execution:
  registry_key: bdd-signature
  python_import: behaviors.bdd.bdd_runner.SignatureCommand
  cli_runner: behaviors/bdd/bdd_runner.py
  actions:
    generate:
      cli: generate-signature
      method: generate
    validate:
      cli: validate-signature
      method: validate
    correct:
      cli: correct-signature
      method: correct
  working_directory: workspace_root
---

### Command: `/bdd-signature`

**[Purpose]:** Generate test signatures (code structure with empty bodies) from scaffolds following BDD principles. This command converts plain English hierarchies into proper test framework syntax.

**[Rule]:**
* `/bdd-rule` — Base BDD principles:
  - Section 1: Business Readable Language
  - Section 2: Fluency, Hierarchy, and Storytelling
* `/bdd-mamba-rule` (or `/bdd-jest-rule`) — Framework-specific principles:
  - Section 6: Signature Phase Requirements

**Runner:**
* CLI: `python behaviors/bdd/bdd-runner.py workflow [test-file] [framework] 1 --no-guard` — Execute Phase 1 (Build Test Signatures) via workflow
* CLI: `python behaviors/bdd/bdd-runner.py run [test-file] [framework]` — Run tests after signature generation
* CLI: `python behaviors/bdd/bdd-runner.py correct-signature [test-file]` — Correct signatures based on errors and chat context

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/bdd-signature` and generate has not been called for this command, command CLI invokes generate action
OR
1. **User** explicitly invokes command via `/bdd-signature-generate`

2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("bdd-signature", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **AI Agent** references rule files to understand how to generate test signatures:
   - `/bdd-rule.mdc` Sections 1 and 2 for base BDD principles
   - `/bdd-mamba-rule.mdc` Section 6 for framework-specific signature requirements

4. **Runner** (`BDDWorkflow.Phase1.generate()`) generates test signatures:
   - Discovers scaffold file (`{test-file-stem}-hierarchy.txt`) to use as input
   - Uses incremental approach (~18 describe blocks per iteration)
   - Converts plain English scaffold to proper framework syntax (see Section 6 of specializing rule)
   - Updates test file directly with signature blocks

5. **Runner** which displays list of updated files with relative paths

6. **AI Agent** presents generation results to user:
   - Updated test file path
   - Scaffold file used (if found)
   - Number of describe/it blocks generated
   - Next step after human feedback (regenerate, proceed to validation, continue to next iteration)

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews generated test signatures and adds/edits content:
   - Reviews code structure matches scaffold hierarchy
   - Verifies proper framework syntax (see specializing rule Section 6)
   - Confirms empty bodies with signature markers
   - Edits signatures if needed

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation (implicit when calling `/bdd-signature` again, or explicit `/bdd-signature-validate`)

2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("bdd-signature", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **Runner** (`BDDWorkflow.Phase1.validate()`) validates if test signatures follow the principles:
   - **Primary Check**: Scaffold alignment (if scaffold found)
   - **Secondary Check**: Proper framework syntax (Section 6 of specializing rule)
   - **Tertiary Check**: Base BDD principles (Sections 1 and 2)
   - Uses heuristics to detect violations

4. **Runner** which displays validation report with violations (if any)

5. **AI Agent** presents validation results:
   - List of violations (if any) with line numbers and messages
   - Recommendations for fixing violations
   - Next steps (fix violations and re-validate, continue iteration, or proceed to RED phase)

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** fixes violations (if any) and re-invokes validation
2. **User** continues signature generation for remaining test sections (if not complete)
3. **User** proceeds to RED phase (test implementation) if all signatures complete and validation passes

**ACTION 5: CORRECT**
**Steps:**
1. **User** invokes correction via `/bdd-signature-correct [test-file] [chat-context]` when signatures have validation errors or need updates based on chat context

2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("bdd-signature", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **AI Agent** references rule files to understand how to correct test signatures based on:
   - Validation violations (if any) with line numbers and messages
   - Chat context provided by user
   - BDD principles from Sections 1, 2, and framework-specific Section 6

4. **AI Agent** corrects the test file:
   - Fixes validation violations (if any)
   - Applies corrections based on chat context
   - Ensures signatures follow BDD principles
   - Updates test file directly

5. **AI Agent** presents correction results to user:
   - List of corrections made
   - Updated test file path
   - Next steps (re-validate, proceed to RED phase)

**ACTION 6: RUN**
**Steps:**
1. **User** invokes test execution via `/bdd-run [test-file] [framework]` to run tests after signature generation (optional - signatures typically don't run until tests are implemented)

2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("bdd-signature", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **Runner** (`BDDWorkflow.run_tests()`) executes tests:
   - **Mamba/Python**: Runs `python -m mamba.cli [test-file]` from test file's directory
   - **Jest/JavaScript**: Runs `npm test -- [test-file]` from project root
   - Captures stdout, stderr, and return code
   - Parses test results (pass/fail counts)

4. **Runner** which displays test execution results:
   - Test output (stdout + stderr)
   - Pass/fail counts
   - Success/failure status

5. **AI Agent** presents execution results to user:
   - Test results summary
   - Pass/fail counts
   - Next steps (proceed to test implementation phase, re-run tests if needed)
