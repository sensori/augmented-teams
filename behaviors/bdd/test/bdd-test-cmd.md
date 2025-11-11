### Command: `/bdd-test`

**[Purpose]:** Implement test code (Arrange-Act-Assert with mocks and assertions) from signatures following BDD principles. This command converts empty signature blocks into full test implementations.

**[Rule]:**
* `/bdd-rule` — Base BDD principles:
  - Section 1: Business Readable Language
  - Section 2: Fluency, Hierarchy, and Storytelling
  - Section 3: Balance Context Sharing with Localization
  - Section 8: Test Implementation Phase (Arrange-Act-Assert, proper mocking, helper extraction, natural test failures)
* `/bdd-mamba-rule` (or `/bdd-jest-rule`) — Framework-specific examples:
  - Section 7: Test Implementation Phase Examples

**Runner:**
* CLI: `python behaviors/bdd/bdd-runner.py workflow [test-file] [framework] 2 --no-guard` — Execute Phase 2 (Write Tests) via workflow

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/bdd-test` and generate has not been called for this command, command CLI invokes generate action
OR
1. **User** explicitly invokes command via `/bdd-test-generate`

2. **AI Agent** (using `BDDWorkflow.Phase2.generate()`) determines the test file path (from user input or context)

3. **AI Agent** references rule files to understand how to implement tests:
   - `/bdd-rule.mdc` Sections 1, 2, 3, and 8 for base BDD principles and test implementation guidance
   - `/bdd-mamba-rule.mdc` Section 7 for framework-specific examples

4. **Runner** (`BDDWorkflow.Phase2.generate()`) implements tests:
   - Finds signatures with `# BDD: SIGNATURE` markers (unimplemented)
   - Uses incremental approach (~18 describe blocks per iteration)
   - Converts signatures to full test implementations (see Section 8 of base rule and Section 7 of specializing rule)
   - Updates test file directly with implemented test bodies

5. **Runner** displays list of updated files with relative paths

6. **AI Agent** presents generation results to user:
   - Updated test file path
   - Number of tests implemented
   - Number of remaining signatures (if any)
   - Next step after human feedback (regenerate, proceed to validation, continue to next iteration)

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews implemented tests and adds/edits content:
   - Reviews Arrange-Act-Assert structure
   - Verifies proper mocking (boundaries only, see base rule § 8.2)
   - Confirms production code is called directly (no commented code, § 8.4)
   - Checks helper extraction (§ 8.3)
   - Edits implementations if needed

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation (implicit when calling `/bdd-test` again, or explicit `/bdd-test-validate`)

2. **AI Agent** references rule files to validate test implementations:
   - `/bdd-rule.mdc` Sections 1, 2, 3, and 8 for base principles and test implementation requirements
   - `/bdd-mamba-rule.mdc` Section 7 for framework-specific patterns

3. **Runner** (`BDDWorkflow.Phase2.validate()`) validates if test implementations follow the principles:
   - **Primary Check**: Implementation completeness (all signatures implemented, no remaining `# BDD: SIGNATURE` markers)
   - **Secondary Check**: Test structure quality (Arrange-Act-Assert, proper mocking per § 8.2, no duplication per § 8.3)
   - **Tertiary Check**: Base BDD principles (Sections 1, 2, 3, 8)
   - Uses heuristics to detect violations

4. **Runner** displays validation report with violations (if any)

5. **AI Agent** presents validation results:
   - List of violations (if any) with line numbers and messages
   - Recommendations for fixing violations
   - Next steps (fix violations and re-validate, continue iteration, or proceed to Write Code phase)

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** fixes violations (if any) and re-invokes validation
2. **User** continues test implementation for remaining signatures (if not complete)
3. **User** proceeds to Write Code phase (production code implementation) if all tests complete and validation passes
