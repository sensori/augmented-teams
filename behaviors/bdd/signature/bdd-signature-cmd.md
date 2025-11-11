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

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/bdd-signature` and generate has not been called for this command, command CLI invokes generate action
OR
1. **User** explicitly invokes command via `/bdd-signature-generate`

2. **AI Agent** (using `BDDWorkflow.Phase1.generate()`) determines the test file path (from user input or context)

3. **AI Agent** references rule files to understand how to generate test signatures:
   - `/bdd-rule.mdc` Sections 1 and 2 for base BDD principles
   - `/bdd-mamba-rule.mdc` Section 6 for framework-specific signature requirements

4. **Runner** (`BDDWorkflow.Phase1.generate()`) generates test signatures:
   - Discovers scaffold file (`{test-file-stem}-hierarchy.txt`) to use as input
   - Uses incremental approach (~18 describe blocks per iteration)
   - Converts plain English scaffold to proper framework syntax (see Section 6 of specializing rule)
   - Updates test file directly with signature blocks

5. **Runner** displays list of updated files with relative paths

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

2. **AI Agent** references rule files to validate test signatures:
   - `/bdd-rule.mdc` Sections 1 and 2 for base principles
   - `/bdd-mamba-rule.mdc` Section 6 for signature requirements

3. **Runner** (`BDDWorkflow.Phase1.validate()`) validates if test signatures follow the principles:
   - **Primary Check**: Scaffold alignment (if scaffold found)
   - **Secondary Check**: Proper framework syntax (Section 6 of specializing rule)
   - **Tertiary Check**: Base BDD principles (Sections 1 and 2)
   - Uses heuristics to detect violations

4. **Runner** displays validation report with violations (if any)

5. **AI Agent** presents validation results:
   - List of violations (if any) with line numbers and messages
   - Recommendations for fixing violations
   - Next steps (fix violations and re-validate, continue iteration, or proceed to RED phase)

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** fixes violations (if any) and re-invokes validation
2. **User** continues signature generation for remaining test sections (if not complete)
3. **User** proceeds to RED phase (test implementation) if all signatures complete and validation passes
