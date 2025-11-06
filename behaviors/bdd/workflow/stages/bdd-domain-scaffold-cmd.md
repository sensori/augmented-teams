### Command: `bdd-domain-scaffold-cmd.md`

**Purpose:** Generate natural language test hierarchy from domain map (Stage 0 - Domain Scaffolding)

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
   - IF NO domain map found: STOPS and tells AI to run `/ddd-analyze` first
   - Outputs domain map content with hierarchy clearly marked
   - Outputs hierarchy mapping instructions with examples
   - Emphasizes PRESERVE DEPTH - no flattening
   - Exits (Python process completes)
4. **MANDATORY: AI Agent reads domain map**:
   - Identifies domain hierarchy (top-level domains, concepts, nested concepts)
   - Notes indentation depth for each concept
   - Maps domain structure to test structure preserving ALL nesting
5. **AI Agent** (in chat):
   - Reads `bdd-domain-fluency-rule.mdc` CRITICAL section on hierarchy preservation
   - Generates describe hierarchy matching domain map depth
   - NEVER flattens: preserves parent-child relationships
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
2. ✓ **HIERARCHY DEPTH**: Does test nesting match domain map indentation? (Count tabs in map = count describe levels in tests)
3. ✓ **TOP-LEVEL DOMAINS**: Are top-level describes the DOMAIN names from map (not individual concepts)?
4. ✓ **NESTED CONCEPTS**: Are domain concepts nested under their parent domain?
5. ✓ **NO FLATTENING**: Are nested concepts (Movement-Triggered, Customization) kept nested, not promoted to siblings?
6. ✓ Do nested describes use 'that/whose/when/with' to show relationships?
7. ✓ Are class/function/module names avoided?
8. ✓ Is the subject clear in every describe chain?
9. ✓ Do siblings relate to same parent concept?
10. ✓ Does nesting show general → specific progression?

**Integration:**

This command integrates with:
* `/ddd-analyze` — Should run first to create domain map
* `\bdd-domain-fluency-rule` — Validation rules for structure
* `\bdd-signature` — Next command after scaffold complete
* `\bdd-workflow` — Orchestrator calls this for Stage 0

**Next Phase:**

After domain scaffold approved:
* `\bdd-signature` — Add "it should..." statements to hierarchy


After domain scaffold approved:
* `\bdd-signature` — Add "it should..." statements to hierarchy
