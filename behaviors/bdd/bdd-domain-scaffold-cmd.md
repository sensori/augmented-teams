### Command: `bdd-domain-scaffold-cmd.md`

**Purpose:** Generate natural language test hierarchy from domain map (Stage 0 - NO code yet)

**Usage:**
* `\bdd-domain-scaffold` — Generate/iterate describe hierarchy for current test file
* `\bdd-domain-scaffold-verify` — Verify hierarchy follows fluency principles
* `python behaviors/bdd/bdd-runner.py workflow <file> domain-scaffold` — Run from command line

**Rule:**
* `\bdd-domain-fluency-rule` — Hierarchy and fluency principles
* `\ddd-structure-analysis-rule` — Domain concept mapping (referenced by fluency rule)

**Phase:** Stage 0 (before signatures, before any code)

**What This Creates:**
Plain English behavioral structure (no code syntax yet).

**Example:**
```
describe a power item
  created from a power
    it should provide access to the original power
    it should play animation for the token
  whose animation is being edited
    that has its effects modified
      it should add effect to selection
```

This is pure English - converted to code syntax in Stage 1.

**Stage 0 Stops Here** - Next: `/bdd-signature` (Stage 1) converts to code syntax

**3-Method Pattern:**

1. **First Call** (`/bdd-domain-scaffold`):
   - Code loads domain map (if exists)
   - Code outputs domain map and instructions to AI
   - AI generates ~18 describe blocks
   - AI creates hierarchy in test file
   - State: STARTED

2. **Iteration** (`/bdd-domain-scaffold` again):
   - Code re-outputs domain map and instructions
   - AI revises hierarchy based on feedback
   - State: STARTED (unchanged)

3. **Verification** (`/bdd-domain-scaffold-verify`):
   - AI confirms hierarchy validated against `bdd-domain-fluency-rule.mdc`
   - AI reports: "Read aloud test passed, 0 violations"
   - State: AI_VERIFIED
   - Ready for `/bdd-workflow-approve`

**Sample vs Expand:**
* **Sample:** Generate ~18 describe blocks for one domain concept
* **Expand:** Generate full hierarchy for entire domain map

**Division of Labor:**
* **Code:** Load domain map, output instructions
* **AI Agent:** Generate hierarchy, validate fluency, write to test file
* **Human:** Review structure, approve

**Steps:**

1. **User** invokes `\bdd-domain-scaffold <file-path>`
2. **Code** detects if first call or repeat:
   - No active run → `start_step(DOMAIN_SCAFFOLD, scaffolder.output_instructions)`
   - Active run → `repeat_step(scaffolder.output_instructions)`
3. **Code** `DomainScaffolder.output_instructions()`:
   - Loads domain map from test directory
   - Outputs domain map content to chat
   - Outputs instructions for AI
   - Exits (Python process completes)
4. **AI Agent** (in chat):
   - Reads domain map
   - Reads `bdd-domain-fluency-rule.mdc`
   - Generates describe hierarchy (~18 blocks for sample)
   - Writes to test file using `write` or `search_replace`
5. **Human** reviews structure in test file
6. **IF needs iteration:**
   - **User** runs `\bdd-domain-scaffold` again (repeat)
   - Go to step 2
7. **IF structure looks good:**
   - **User** runs `\bdd-domain-scaffold-verify`
   - **Code** prompts AI to confirm validation
   - **AI** confirms: "Read aloud test passed, hierarchy matches domain map"
   - **Code** records AI_VERIFIED in state
8. **User** runs `\bdd-workflow-approve` to complete stage
9. **Ready** for Stage 1 (signatures)

**Hierarchy Validation Checklist** (AI performs during verify):

1. ✓ Read each describe chain aloud - does it flow naturally?
2. ✓ Are top-level describes domain concepts with 'a/an'?
3. ✓ Do nested describes use 'that/whose/when/with' to show relationships?
4. ✓ Does structure match domain map hierarchy (if map exists)?
5. ✓ Are class/function/module names avoided?
6. ✓ Is the subject clear in every describe chain?
7. ✓ Do siblings relate to same parent concept?
8. ✓ Does nesting show general → specific progression?

**Integration:**

This command integrates with:
* `/ddd-analyze` — Should run first to create domain map
* `\bdd-domain-fluency-rule` — Validation rules for structure
* `\bdd-signature` — Next command after scaffold complete
* `\bdd-workflow` — Orchestrator calls this for Stage 0

**Next Phase:**

After domain scaffold approved:
* `\bdd-signature` — Add "it should..." statements to hierarchy
