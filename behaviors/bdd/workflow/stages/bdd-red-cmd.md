### Command: `bdd-red-cmd.md`

**Purpose:** Implement failing tests (Stage 2 - RED phase)

**Usage:**
* `\bdd-red` — Implement/iterate failing tests
* `\bdd-red-verify` — Verify tests follow BDD principles
* `python behaviors/bdd/bdd-runner.py workflow <file> red` — Run from command line

**Rule:**
* `\bdd-jest-rule` or `\bdd-mamba-rule` — Full BDD principles

**Phase:** Stage 2 (after signatures, before GREEN)

**Prerequisites:**
* Stage 1 complete (signatures exist)
* Signatures approved

**What This Does:**
Implement ~18 test signatures with Arrange-Act-Assert, proper mocking, helpers.
Tests should FAIL for the right reason (code not implemented yet).

**3-Method Pattern:**

1. **First Call** (`/bdd-red`):
   - Code loads rule examples
   - Code outputs RED phase guidance
   - AI implements ~18 tests
   - State: STARTED

2. **Iteration** (`/bdd-red` again):
   - Code re-outputs guidance
   - AI revises tests
   - State: STARTED (unchanged)

3. **Verification** (`/bdd-red-verify`):
   - AI runs `/bdd-validate`
   - AI reports violations
   - State: AI_VERIFIED

**Sample vs Expand:**
* **Sample:** Implement ~18 tests
* **Expand:** Implement all remaining signatures

**Runner:**
`python behaviors/bdd/bdd-runner.py workflow <file> red` — Implement failing tests (Stage 2)

**Steps:**
1. **User** invokes command via `\bdd-red`
2. **Code** function `load_rule_examples(framework)` — loads RED phase guidance from bdd-jest-rule.mdc, returns examples dict
3. **Code** displays Arrange-Act-Assert patterns and mocking examples
4. **AI Agent** implements ~18 test bodies with proper test structure ensuring tests fail for right reason
5. **Code** function `update_run_state(status='started')` — marks run as in-progress, returns state

**Next Phase:**
After RED approved:
* `/bdd-green` — Implement code to make tests pass



**Next Phase:**
After RED approved:
* `/bdd-green` — Implement code to make tests pass

