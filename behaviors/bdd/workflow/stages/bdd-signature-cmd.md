### Command: `bdd-signature-cmd.md`

**Purpose:** Add "it should..." statements to describe hierarchy (Stage 1 - Signatures)

**Usage:**
* `\bdd-signature` — Generate/iterate test signatures
* `\bdd-signature-verify` — Verify signatures follow BDD principles
* `python behaviors/bdd/bdd-runner.py workflow <file> signatures` — Run from command line

**Rule:**
* `\bdd-jest-rule` or `\bdd-mamba-rule` — Full BDD principles (framework-specific)
* `\bdd-domain-fluency-rule` — Hierarchy already validated in Stage 0

**Phase:** Stage 1 (after domain scaffold, before RED)

**Prerequisites:**
* Stage 0 complete (describe hierarchy exists)
* Domain scaffold approved

**What This Adds:**
"it should..." statements inside existing describe blocks.
Leverages DO/DON'T examples from bdd-jest-rule.mdc (same as legacy Stage 0).

**Example Input (from Stage 0):**
```javascript
describe('a power item', () => {
  describe('created from a power', () => {
    describe('that provides animation characteristics', () => {
      // EMPTY - Stage 1 adds "it should..." here
    });
  });
});
```

**Example Output (Stage 1):**
```javascript
describe('a power item', () => {
  describe('created from a power', () => {
    describe('that provides animation characteristics', () => {
      it('should provide primary descriptor', () => {
        // BDD: SIGNATURE
      });
      
      it('should provide effect type', () => {
        // BDD: SIGNATURE
      });
      
      it('should provide range', () => {
        // BDD: SIGNATURE
      });
    });
  });
});
```

**3-Method Pattern:**

1. **First Call** (`/bdd-signature`):
   - Code loads rule examples from bdd-jest-rule.mdc
   - Code outputs DO/DON'T examples
   - AI adds ~18 "it should..." statements
   - State: STARTED

2. **Iteration** (`/bdd-signature` again):
   - Code re-outputs examples
   - AI revises signatures
   - State: STARTED (unchanged)

3. **Verification** (`/bdd-signature-verify`):
   - AI runs `/bdd-validate` 
   - AI reports violations to Human
   - State: AI_VERIFIED
   - Ready for `/bdd-workflow-approve`

**Sample vs Expand:**
* **Sample:** Add ~18 "it should..." statements
* **Expand:** Add all remaining signatures

**Division of Labor:**
* **Code:** Load rule examples, output instructions
* **AI Agent:** Create "it should..." statements following examples
* **Human:** Review signatures, approve

**Runner:**
`python behaviors/bdd/bdd-runner.py workflow <file> signatures` — Generate test signatures (Stage 1)

**Steps:**
1. **User** invokes command via `\bdd-signature`
2. **Code** function `load_rule_examples(framework)` — loads DO/DON'T examples from bdd-jest-rule.mdc or bdd-mamba-rule.mdc, returns examples dict
3. **Code** displays BDD principles and signature examples for Stage 1
4. **AI Agent** analyzes describe hierarchy and adds ~18 "it should..." statements following examples
5. **Code** function `update_run_state(status='started')` — marks run as in-progress, returns state

**Next Phase:**
After signatures approved:
* `/bdd-red` — Implement failing tests (Stage 2)



**Next Phase:**
After signatures approved:
* `/bdd-red` — Implement failing tests (Stage 2)

