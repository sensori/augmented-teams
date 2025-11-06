### Command: `bdd-refactor-cmd.md`

**Purpose:** Suggest and implement code improvements (Stage 4 - REFACTOR phase)

**Usage:**
* `\bdd-refactor` — Suggest/iterate refactorings
* `\bdd-refactor-verify` — Verify refactorings
* `python behaviors/bdd/bdd-runner.py workflow <file> refactor` — Run from command line

**Rule:**
* `\bdd-jest-rule` or `\bdd-mamba-rule` — Full BDD principles

**Phase:** Stage 4 (after GREEN, optional)

**Prerequisites:**
* Stage 3 complete (tests passing)
* GREEN phase approved

**What This Does:**
Suggest and implement code improvements while keeping tests green.

**3-Method Pattern:**

1. **First Call** (`/bdd-refactor`):
   - Code outputs refactor guidance
   - AI suggests improvements
   - State: STARTED

2. **Iteration** (`/bdd-refactor` again):
   - AI implements refactorings
   - AI runs tests after each change
   - State: STARTED (unchanged)

3. **Verification** (`/bdd-refactor-verify`):
   - AI confirms tests still pass
   - AI runs `/bdd-validate`
   - State: AI_VERIFIED

**Runner:**
`python behaviors/bdd/bdd-runner.py workflow <file> refactor` — Suggest code improvements (Stage 4)

**Steps:**
1. **User** invokes command via `\bdd-refactor`
2. **Code** displays REFACTOR phase guidance on code quality improvements
3. **AI Agent** analyzes code for smells and suggests improvements while keeping tests green
4. **AI Agent** implements refactorings incrementally, running tests after each change
5. **Code** function `update_run_state(status='started')` — marks run as in-progress, returns state

**Next Phase:**
After REFACTOR approved - DONE! Or return to RED for next feature.


1. **User** invokes command via `\bdd-refactor`
2. **Code** displays REFACTOR phase guidance on code quality improvements
3. **AI Agent** analyzes code for smells and suggests improvements while keeping tests green
4. **AI Agent** implements refactorings incrementally, running tests after each change
5. **Code** function `update_run_state(status='started')` — marks run as in-progress, returns state

**Next Phase:**
After REFACTOR approved - DONE! Or return to RED for next feature.

