### Command: `bdd-domain-scaffold-verify-cmd.md`

**Purpose:** Verify domain scaffolding against fluency principles (Stage 0 verification)

**Usage:**
* `\bdd-domain-scaffold-verify` — Verify current hierarchy structure
* `python behaviors/bdd/bdd-runner.py workflow <file> domain-scaffold-verify` — Run from command line

**Rule:**
* `\bdd-domain-fluency-rule` — Domain fluency and hierarchy validation

**When to Use:**
After AI has generated/iterated describe hierarchy in Stage 0, before proceeding to signatures.

**What This Validates:**
- Natural language fluency (read-aloud test)
- Domain map alignment
- Proper use of relationship words (that/whose/when/with)
- No class/function/module names
- Clear subject in every chain
- Hierarchical storytelling

**Validation Rules** (from bdd-domain-fluency-rule.mdc):

1. ✓ Read each describe chain aloud - does it flow naturally?
2. ✓ Are top-level describes domain concepts with 'a/an'?
3. ✓ Do nested describes use 'that/whose/when/with' to show relationships?
4. ✓ Does structure match domain map hierarchy (if map exists)?
5. ✓ Are class/function/module names avoided?
6. ✓ Is the subject clear in every describe chain?
7. ✓ Do siblings relate to same parent concept?
8. ✓ Does nesting show general → specific progression?

**Division of Labor:**
* **Code:** Checks state, outputs validation instructions
* **AI Agent:** Reviews hierarchy against fluency rules, reports violations to Human
* **Human:** Decides if violations should be fixed now or are acceptable

**Steps:**

1. **User** runs `\bdd-domain-scaffold-verify` after AI generated hierarchy
2. **Code** checks current run state:
   - Must be in DOMAIN_SCAFFOLD step
   - Must be STARTED status
   - If not, errors and exits
3. **Code** outputs validation requirements:
   ```
   AI Verification Requirements:
   - Run fluency validation (read-aloud test) on hierarchy
   - Check structure against bdd-domain-fluency-rule.mdc
   - Report violations with line numbers and severity
   - Human decides which violations to fix
   ```
4. **Code** records AI_VERIFIED in state
5. **Code** prompts human to run `/bdd-workflow-approve`
6. **AI Agent** (before this command):
   - Should have validated hierarchy
   - Should have reported violations to Human
   - Should have fixed violations per Human direction (if any)
7. **Human** runs `/bdd-workflow-approve` when satisfied

**Example Validation Output from AI:**

```
Domain Fluency Validation Report
=================================

✅ Read-Aloud Test: PASS
   "a power item created from a power that provides characteristics" ✓
   "a power item whose animation is being edited" ✓
   
✅ Domain Alignment: PASS
   Structure matches domain map hierarchy
   
⚠️  Minor Issue (Lines 48-52):
   describe('power roll animations', ...)
   
   Violation: Missing clear subject connection
   Severity: MEDIUM
   
   Suggested Fix:
   describe('a power item', () => {
     describe('that activates when rolled', () => {
       // power roll animation tests
     });
   });
   
   Human: Fix now or defer to refactor?
```

**Integration:**

This command integrates with:
* `\bdd-domain-scaffold` — Verifies output from scaffold command
* `\bdd-domain-fluency-rule` — Validation rules applied
* `/bdd-workflow-approve` — Next step after verification
* `/bdd-workflow-abandon` — Alternative if need to restart

**Next Phase:**

After verification and approval:
* State moves to COMPLETED
* Ready for `\bdd-signature` (Stage 1)

   Severity: MEDIUM
   
   Suggested Fix:
   describe('a power item', () => {
     describe('that activates when rolled', () => {
       // power roll animation tests
     });
   });
   
   Human: Fix now or defer to refactor?
```

**Integration:**

This command integrates with:
* `\bdd-domain-scaffold` — Verifies output from scaffold command
* `\bdd-domain-fluency-rule` — Validation rules applied
* `/bdd-workflow-approve` — Next step after verification
* `/bdd-workflow-abandon` — Alternative if need to restart

**Next Phase:**

After verification and approval:
* State moves to COMPLETED
* Ready for `\bdd-signature` (Stage 1)
