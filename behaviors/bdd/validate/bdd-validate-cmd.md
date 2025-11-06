### Command: `/bdd-validate`

**Purpose:** Validate actual BDD test files against BDD principles (readable language, comprehensive coverage, proper structure, etc.)

**Usage:**
* `/bdd-validate` — Validate currently open test file
* `/bdd-validate <file-path>` — Validate specific test file

**When invoked, this command MUST:**
1. Run: `python behaviors/bdd/validate/bdd-validate-runner.py <file-path> --cursor`
2. Parse the outputted validation prompts
3. Validate each chunk against the provided checklist
4. Report violations with line numbers
5. Suggest fixes using DO examples

**Rule Files:**
* `bdd-rule.mdc` — Framework-agnostic BDD testing principles
* `bdd-jest-rule.mdc` — Jest-specific BDD patterns
* `bdd-mamba-rule.mdc` — Mamba-specific BDD patterns

**Valid Files** (uses same glob patterns as rules):
* **Jest**: `["**/*.test.js", "**/*.spec.js", "**/*.test.ts", "**/*.spec.ts", "**/*.test.jsx", "**/*.spec.jsx", "**/*.test.tsx", "**/*.spec.tsx", "**/*.test.mjs", "**/*.spec.mjs"]`
* **Mamba**: `["**/*_test.py", "**/test_*.py", "**/*_spec.py", "**/spec_*.py", "**/*_test.pyi", "**/test_*.pyi", "**/*_spec.pyi", "**/spec_*.pyi"]`

---

## Implementation Architecture

### Division of Labor:

**Python Runner (bdd-validate-runner.py):**
- Detects framework (Jest/Mamba)
- Discovers domain maps
- Parses BDD rule files dynamically
- Extracts test structure (describe/it blocks)
- Generates structured validation prompts
- Outputs prompts to stdout for AI to read

**AI Agent (Cursor chat):**
- Reads validation prompts from runner output
- Validates each block against checklist
- Identifies violations (semantic understanding required)
- Suggests fixes using DO examples
- Reports violations with line numbers

---

## Validation Flow

### Step 1: User Invokes Command
```
User: /bdd-validate demo/mm3e-animations/mm3e-effects-section.test.mjs
```

### Step 2: AI Runs Python Script
```bash
python behaviors/bdd/validate/bdd-validate-runner.py demo/mm3e-animations/mm3e-effects-section.test.mjs --cursor
```

**Flags:**
- `--cursor` — Non-interactive mode (outputs all prompts without waiting for ENTER)
- `--batch` — Batch mode (all sections at once instead of iterative)
- `--chunk-size N` — Blocks per chunk (default: 10)

### Step 3: Runner Outputs Validation Prompts

The runner outputs structured prompts like:

```
============================================================
BDD VALIDATOR - ITERATIVE MODE
============================================================

[OK] Detected framework: jest
[OK] Found domain maps for context
[OK] Found 82 test blocks

Validating against 5 sections (§1-§5)
Chunk size: 10 blocks

============================================================
§ 1: Business Readable Language
============================================================

[Chunk 1/9] 10 blocks:

Block 1/82: Line 8
Block: Line 8 - "power activation animation"

VALIDATE AGAINST § 1: Business Readable Language

Principle: Write `describe`/`it` so that inner/outer sentences create natural sentence...

MANDATORY CHECKLIST (answer ALL):

□ Contains technical jargon?
  Keywords to avoid: extract, parse, hook, flag, id
  ❌ DON'T: it('sets isSubmitting flag', () => {});
  ✅ DO: describe('a ranged damage power', () => {

□ Uses nouns (not verbs)?
  Keywords to avoid: when, calls, gets, sets
  ❌ DON'T: describe('when Attack.targetToken()', () => {});
  ✅ DO: describe('a ranged damage power', () => {

□ Starts with "should" (for it() blocks)?
  ✅ DO: it('should calculate DC from target dodge', () => {

Domain Terms Available: Power Item, Animation Resolver, Combat Data Extractor

RESPOND: violations: [list any found]

Block 2/82: Line 10
...

------------------------------------------------------------
AI: Validate above 10 blocks against Section 1
    Report violations in chat
------------------------------------------------------------
```

### Step 4: AI Validates and Reports

AI reads prompts, validates each block, and reports:

```
## Validation Results - § 1: Business Readable Language

✅ Block 1 (Line 8): PASS
✅ Block 2 (Line 10): PASS
❌ Block 10 (Line 72): VIOLATION
   
   Current: "that had provided an animation that has been played"
   Issue: Awkward tense mixing (past perfect + present perfect)
   Fix: "whose animation has been played"
   
   Reasoning: Mixing "had provided" (past perfect) with "has been played" 
   (present perfect) creates unnatural phrasing. Use consistent tense.
```

### Step 5: Repeat for Each Section

Runner outputs prompts for § 2, § 3, § 4, § 5.
AI validates each section and reports violations.

### Step 6: Cross-Section Validation

After all sections complete, runner outputs:

```
============================================================
FINAL PASS: CROSS-SECTION VALIDATION
============================================================

Review ALL violations found across §1-§5 for:
- Systemic issues spanning multiple sections
- Missing abstractions (duplicate setup + testing internals)
- Layer conflicts (front-end tests using business logic)

Violations Found:
  § 1 Line 72: Grammar/tense mixing
  § 3 Lines 105-120: Duplicate Arrange code
  ...

AI: Review all violations above for cross-section issues
============================================================
```

---

## Validation Modes

### 1. Iterative Mode (DEFAULT)
```bash
python behaviors/bdd/validate/bdd-validate-runner.py <file> --cursor
```

**Features:**
- Validates section-by-section (§1, then §2, etc.)
- Processes 10 blocks at a time (configurable)
- Non-interactive in Cursor (all prompts at once)
- Best for thorough validation

**Flow:**
1. Parse BDD rules → generate validation checklists
2. For each §1-§5:
   - Output 10 blocks with structured prompts
   - AI validates and reports violations
3. Final cross-section validation
4. Complete

### 2. Batch Mode (--batch flag)
```bash
python behaviors/bdd/validate/bdd-validate-runner.py <file> --cursor --batch
```

**Features:**
- Outputs ALL sections × ALL blocks at once
- AI validates comprehensively in one response
- Faster but may miss subtle issues
- Still includes cross-section validation

---

## Dynamic Rule Parsing

The validator:
- Parses BDD rule files (.mdc) to extract principles and examples
- Auto-generates validation checklists from DON'T comments
- Extracts technical jargon keywords (e.g., "flag", "hook", "extract")
- Detects action verbs (e.g., "when", "calls", "gets", "sets")
- Caches parsed rules for performance

---

## AI Validation Responsibilities

### MANDATORY Steps:

1. **Read runner output** - Parse validation prompts from stdout
2. **Validate each block** - Check against mandatory checklist
3. **Identify violations** - Use semantic understanding
4. **Report with line numbers** - Precise location of issues
5. **Suggest fixes** - Use DO examples as templates
6. **Apply fixes** - Use search_replace to fix violations
7. **Cross-section check** - Look for systemic issues

### Validation Checklist (AI must check ALL):

**§ 1: Business Readable Language**
- □ Contains technical jargon?
- □ Uses nouns (not verbs) in describe?
- □ Starts with "should" in it()?
- □ Natural sentence flow?
- □ Uses domain terms from map?

**§ 2: Comprehensive and Brief**
- □ Tests observable behavior (not internals)?
- □ Covers normal, edge, and failure paths?
- □ Short and expressive?
- □ Fast and deterministic?

**§ 3: Balance Context Sharing**
- □ Sibling describes have duplicate beforeEach?
- □ Sibling it() blocks (3+) have duplicate Arrange?
- □ Mock objects duplicated across tests?
- □ Helper factories defined multiple times?

**§ 4: Cover All Layers**
- □ Separates front-end, business logic, data access?
- □ Mocks dependencies appropriately?
- □ Focuses on code under test?

**§ 5: Unit Tests Front-End**
- □ Mocks services and routing?
- □ Tests both data structure AND rendered output?
- □ Validates conditional render paths?

---

## Example Output

```
============================================================
BDD Test Validation: mm3e-effects-section.test.mjs (Jest)
============================================================

Domain Maps Found:
  ✓ mm3e-animations-domain-map.txt
  ✓ mm3e-animations-domain-interactions.txt

✅ Domain Alignment: PASS
   Describe blocks match domain hierarchy
   Test names use domain concepts from map

============================================================
Validation Results by Section
============================================================

§ 1: Business Readable Language
  ✅ 81 blocks PASS
  ❌ 1 violation found:
     Line 72: Grammar/tense mixing

§ 2: Comprehensive and Brief
  ✅ All blocks PASS

§ 3: Balance Context Sharing
  ✅ All blocks PASS
  
§ 4: Cover All Layers
  ✅ All blocks PASS

§ 5: Unit Tests Front-End
  ✅ All blocks PASS

============================================================
Detailed Violations
============================================================

❌ Line 72: "that had provided an animation that has been played"
   Section: § 1 Business Readable Language
   Issue: Awkward tense mixing
   Fix: "whose animation has been played"

============================================================
Validation Summary
============================================================
❌ 1 violation found
✅ 81 tests validated

Recommend applying fix to line 72.
```

---

## Integration

This command can be integrated into:
- Pre-commit hooks to validate changes
- CI/CD pipelines for automated checking  
- Development workflow as a manual check
- Sync process to validate before deployment

---

## Command Examples

```bash
# From Cursor (automatic)
/bdd-validate

# With specific file
/bdd-validate demo/mm3e-animations/mm3e-effects-section.test.mjs

# From command line (interactive)
python behaviors/bdd/validate/bdd-validate-runner.py my-test.mjs

# From command line (Cursor/non-interactive)
python behaviors/bdd/validate/bdd-validate-runner.py my-test.mjs --cursor

# Batch mode for quick overview
python behaviors/bdd/validate/bdd-validate-runner.py my-test.mjs --cursor --batch

# Custom chunk size
python behaviors/bdd/validate/bdd-validate-runner.py my-test.mjs --cursor --chunk-size 5
```
