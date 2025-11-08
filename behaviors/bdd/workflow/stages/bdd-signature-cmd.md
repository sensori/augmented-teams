### Command: `bdd-signature-cmd.md`

**Purpose:** Convert plain English hierarchy to code syntax (Stage 1 - Signatures)

**Usage:**
* `\bdd-signature` — Convert plain English to code syntax
* `\bdd-signature-verify` — Verify signatures follow BDD principles
* `python behaviors/bdd/bdd-runner.py workflow <file> signatures` — Run from command line

**Rule:**
* `\bdd-jest-rule` or `\bdd-mamba-rule` — Full BDD principles (framework-specific)
* `\bdd-domain-fluency-rule` — Hierarchy already validated in Stage 0

**Phase:** Stage 1 (after domain scaffold, before RED)

**Prerequisites:**
* Stage 0 complete (`*.domain.scaffold.txt` exists with plain English hierarchy)
* Domain scaffold approved

**What This Does:**
Converts plain English hierarchy to actual code syntax (Jest or Mamba).
Creates actual test file from scaffold.

**Example Input (from Stage 0 - `*.domain.scaffold.txt`):**
```
describe a power item
  created from a power
    that provides animation characteristics
      it should provide primary descriptor
      it should provide effect type
      it should provide range
```

**Example Output (Stage 1 - `*.test.js`):**
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

**Conversion:**
- Plain English `describe` → Code `describe('...', () => {})`
- Plain English `it should` → Code `it('should...', () => {})`
- Add empty bodies with `// BDD: SIGNATURE` comments

**3-Method Pattern:**

1. **First Call** (`/bdd-signature`):
   - Code loads plain English from `*.domain.scaffold.txt`
   - Code loads rule examples from bdd-jest-rule.mdc or bdd-mamba-rule.mdc
   - Code outputs scaffold + DO/DON'T examples
   - AI converts ~18 describe blocks from plain English to code syntax
   - AI writes to actual test file (`*.test.js` or `*_test.py`)
   - State: STARTED

2. **Iteration** (`/bdd-signature` again):
   - Code re-outputs scaffold + examples
   - AI revises code syntax
   - State: STARTED (unchanged)

3. **Verification** (`/bdd-signature-verify`):
   - AI runs `/bdd-validate` on actual test file
   - AI reports violations to Human
   - State: AI_VERIFIED
   - Ready for `/bdd-workflow-approve`

**Sample vs Expand:**
* **Sample:** Convert ~18 describe blocks to code syntax
* **Expand:** Convert all remaining describe blocks

**Division of Labor:**
* **Code:** Load scaffold file, load rule examples, output instructions
* **AI Agent:** Convert plain English to Jest/Mamba code syntax following examples
* **Human:** Review code syntax, approve

**Runner:**
`python behaviors/bdd/bdd-runner.py workflow <file> signatures` — Generate test signatures (Stage 1)

**Steps:**
1. **User** invokes command via `\bdd-signature`
2. **Code** function `load_scaffold_file()` — loads `*.domain.scaffold.txt` with plain English hierarchy
3. **Code** function `load_rule_examples(framework)` — loads DO/DON'T examples from bdd-jest-rule.mdc or bdd-mamba-rule.mdc, returns examples dict
4. **Code** displays scaffold content + BDD principles and syntax examples
5. **AI Agent** converts ~18 describe blocks from plain English to Jest/Mamba code syntax following examples
6. **AI Agent** writes code to actual test file (`*.test.js` or `*_test.py`)
7. **Code** function `update_run_state(status='started')` — marks run as in-progress, returns state

**Next Phase:**
After signatures approved:
* `/bdd-red` — Implement failing tests (Stage 2)

