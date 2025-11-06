### Command: `bdd-green-cmd.md`

**Purpose:** Implement minimal code to make tests pass (Stage 3 - GREEN phase)

**Usage:**
* `\bdd-green` — Implement/iterate minimal code
* `\bdd-green-verify` — Verify implementation and tests
* `python behaviors/bdd/bdd-runner.py workflow <file> green` — Run from command line

**Rule:**
* `\bdd-jest-rule` or `\bdd-mamba-rule` — Full BDD principles

**Phase:** Stage 3 (after RED, before REFACTOR)

**Prerequisites:**
* Stage 2 complete (failing tests exist)
* RED phase approved

**What This Does:**
Implement minimal code for ~18 tests.
Resist adding features no test demands.

**3-Method Pattern:**

1. **First Call** (`/bdd-green`):
   - Code outputs GREEN phase guidance
   - AI implements minimal code
   - State: STARTED

2. **Iteration** (`/bdd-green` again):
   - Code re-outputs guidance
   - AI revises implementation
   - State: STARTED (unchanged)

3. **Verification** (`/bdd-green-verify`):
   - AI confirms tests pass
   - AI runs `/bdd-validate`
   - State: AI_VERIFIED

**Runner:**
`python behaviors/bdd/bdd-runner.py workflow <file> green` — Implement minimal code (Stage 3)

**Steps:**
1. **User** invokes command via `\bdd-green`
2. **Code** displays GREEN phase guidance emphasizing minimal implementation
3. **AI Agent** implements minimal code to make ~18 tests pass without adding untested features
4. **Code** function `update_run_state(status='started')` — marks run as in-progress, returns state

**Next Phase:**
After GREEN approved:
* `/bdd-refactor` — Improve code quality


2. **Code** displays GREEN phase guidance emphasizing minimal implementation
3. **AI Agent** implements minimal code to make ~18 tests pass without adding untested features
4. **Code** function `update_run_state(status='started')` — marks run as in-progress, returns state

**Next Phase:**
After GREEN approved:
* `/bdd-refactor` — Improve code quality

