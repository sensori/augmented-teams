# BDD Signature Command Implementation Plan

## Overview
Create a `/bdd-signature` command that generates test signatures (Python/Mamba code structure) from scaffolds following the new BDD rules. The command will integrate with the existing `BDDWorkflow` infrastructure (Phase 1) and support incremental signature creation (sub-domain selection).

## Key Requirements

1. **Use New BDD Rules**: Reference `bdd-rule.mdc` (base principles), `bdd-mamba-rule.mdc` (Python/Mamba framework-specific, includes signature phase guidance)
2. **Focus on Signature Rules**: Emphasize base BDD Section 1 (Business Readable Language), Section 2 (Fluency, Hierarchy, Storytelling), and specializing rule signature phase section (framework-specific syntax, empty bodies, markers)
3. **Incremental Support**: Allow signature creation for specific sub-domains or let system choose scope (~18 describe blocks per iteration)
4. **Workflow Integration**: Integrate with existing `BDDWorkflow` infrastructure (Phase 1)

## Investigation Results

### 1. Signature-Specific Requirements - FINDINGS

**Current State:**
- Signature phase instructions exist in `_get_signature_instructions()` (lines 1160-1176)
- Signature requirements are embedded in workflow instructions
- Signatures are part of Phase 1 workflow ("Build Test Signatures")

**Analysis of Signature Requirements:**
- **Focus**: Signature-specific (Stage 1 - test code structure generation from scaffold)
- **Key Content**:
  - Convert plain English scaffold to proper code syntax (`describe()`, `it()`, `with_()`)
  - Preserve ALL nesting levels from domain map/scaffold
  - Keep test bodies EMPTY - no mocks, no stubs, no helpers
  - Mark with `# BDD: SIGNATURE` comments
  - Sample Size: ~18 describe/it blocks per iteration
  - Output: Updates test file with signature blocks
- **Scope**: Stage 1 (signature creation) only
- **Integration**: Uses scaffold as input, applies BDD § 1, 2, and 7 principles

**Signature vs Scaffold Differences:**
- **Scaffold**: Plain English ONLY, no code syntax, output to `{test-file-stem}-hierarchy.txt`
- **Signature**: Proper code syntax (Mamba), empty test bodies, output to test file (`.py`)
- **Common**: Both preserve hierarchy, follow BDD principles, use ~18 describe blocks

**Decision: ✅ Deep Integration into `bdd-rule.mdc`**

**Integration Strategy:**
- Base rule Section 1: Business Readable Language applies to both scaffold and signature
- Base rule Section 2: Fluency, Hierarchy, Storytelling applies to both
- Specializing rules: Include signature phase section with framework-specific guidance (code syntax, empty bodies, markers)
- Signature command references base rule (Sections 1, 2) and specializing rule (signature phase section)

### 2. Workflow Integration - FINDINGS

**Current State:**
- `BDDWorkflow` class (lines 1029-1102) **FULLY IMPLEMENTED** - creates all 5 phases:
  - Phase 0: Domain Scaffolding
  - **Phase 1: Build Test Signatures** ← THIS COMMAND
  - Phase 2: RED - Create Failing Tests
  - Phase 3: GREEN - Make Tests Pass
  - Phase 4: REFACTOR - Improve Code
- Wrapping chain: `BDDWorkflowPhaseCommand → IncrementalCommand → CodeAugmentedCommand → SpecializingRuleCommand → Command`
- `BDDIncrementalCommand` extends `IncrementalCommand` and calculates sample size from test structure (lines 828-876)
- Domain map discovery exists: `BDDCommand.discover_domain_maps()` (lines 781-810)
- `_get_signature_instructions()` already exists (lines 1160-1176)
- CLI entry point exists: `bdd_workflow()` function and workflow command handler

**Decision:** The command should work BOTH ways:
1. **Standalone**: `/bdd-signature` can be invoked directly (uses BDDWorkflow Phase 1 infrastructure)
2. **Within Workflow**: `/bdd-workflow` dispatches to Phase 1 (same infrastructure)

### 3. Incremental Signature Creation - FINDINGS

**Current State:**
- `IncrementalCommand` supports `sample_size` and `max_sample_size` (default 18)
- `BDDIncrementalCommand._calculate_sample_size()` finds lowest-level describe block and counts `it` blocks
- Signature creation is more granular than scaffolding - can be done incrementally

**Legacy Rationale for Incremental Approach:**
- **Scaffold Phase**: High-level activity, create entire domain map in one shot, no scoping needed
- **Signature Phase Forward**: More granular, benefit from incremental approach with ~18 describe blocks per iteration
- Domain maps have hierarchical structure (domains → concepts → sub-concepts)
- Tests have similar structure (describe → nested describe → it blocks)
- Working incrementally allows focus on one conceptual area at a time

**Decision:** ✅ **Incremental signature creation with ~18 describe blocks**
- Use existing `BDDIncrementalCommand._calculate_sample_size()` to identify work scope
- Find lowest-level describe block and count `it` blocks
- Target ~18 describe blocks per iteration
- Allow user to specify scope or let system choose
- Multiple iterations to complete entire test file

### 4. Validation Should Check Scaffold Alignment and Code Syntax

**Analysis:**
- Scaffold hierarchy is **critical input** for signature creation
- Signature code structure must align with scaffold structure
- Validation should verify:
  - Nesting preservation (signature matches scaffold depth)
  - Concept alignment (signature describe blocks match scaffold describe blocks)
  - Proper code syntax (Mamba: `describe()`, `it()`, `with_()`)
  - Empty test bodies with `# BDD: SIGNATURE` comments
  - No implementation code (no mocks, stubs, helpers yet)

**Decision:** ✅ **Validation must check scaffold alignment and code syntax as primary checks**
- Primary validation: Scaffold alignment (nesting, concepts, structure preservation)
- Secondary validation: Code syntax (proper Mamba syntax, empty it statements , signature markers)
- Tertiary validation: BDD Section 1, 2, and 7 principles
- If scaffold not found, validation should warn but still check code syntax and BDD principles

## Analysis Results - Questions Resolved

### Question 1: Should signature-specific rules be added to specializing rules?

**Analysis:**
- Base `bdd-rule.mdc` Section 1 "Business Readable Language" already covers: plain English, domain language, nesting, natural sentences
- Base `bdd-rule.mdc` Section 2 "Fluency, Hierarchy, and Storytelling" covers hierarchy patterns and domain map mapping
- Signature requirements (framework-specific code syntax, empty bodies, signature markers) are **framework-specific** and should be in specializing rules
- Currently `bdd-mamba-rule.mdc` does NOT cover signature phase requirements (needs to be added)

**Decision:** ✅ **Add Signature Guidance to Specializing Rules (`bdd-mamba-rule.mdc`, `bdd-jest-rule.mdc`)**

**Rationale:**
- Signature requirements are **framework-specific** (Python syntax vs JavaScript syntax)
- Specializing rules already handle framework-specific patterns
- Keep base rule focused on framework-agnostic principles
- Add signature phase section to each specializing rule as part of rule creation
- Framework-specific details belong in framework-specific rules

### Question 2: Code Already Exists - Command Infrastructure Analysis

**Analysis:**
- `BDDWorkflow` class (lines 1029-1102) **FULLY IMPLEMENTED** - includes Phase 1 (Build Test Signatures)
- `_create_phase_command()` creates Phase 1 with full wrapping chain
- `BDDIncrementalCommand` (lines 828-876) calculates sample size from test structure
- `_get_signature_instructions()` (lines 1160-1176) already has signature instructions
- CLI handler exists: `bdd_workflow()` function and workflow command handler

**Decision:** ✅ **NO NEW CODE NEEDED** - The infrastructure is FULLY IMPLEMENTED and TESTED!
- We only need to:
  1. Create command files (`bdd-signature-cmd.md` and delegates) that reference existing workflow infrastructure
  2. Add signature phase section to specializing rules (`bdd-mamba-rule.mdc`, `bdd-jest-rule.mdc`)
  3. Ensure command files reference the existing `BDDWorkflow` Phase 1 infrastructure
  4. Both standalone and workflow routes use the same BDDWorkflow Phase 1 infrastructure

### Question 3: Incremental Scope Selection

**Analysis:**
- `BDDIncrementalCommand._calculate_sample_size()` works on test files (finds lowest describe block, counts `it` blocks)
- For signatures, we work on test files directly (not domain maps)
- Signature creation benefits from incremental approach (~18 describe blocks per iteration)

**Decision:** ✅ **Incremental signature creation with scope selection**
- Use existing `BDDIncrementalCommand._calculate_sample_size()` to identify scope
- Find lowest-level describe block and count `it` blocks
- Target ~18 describe blocks per iteration
- Allow user to specify scope or let system choose next unimplemented section
- Multiple iterations until entire test file has signatures

### Question 4: Validation Should Check Scaffold Alignment

**Analysis:**
- Scaffold is **critical input** for signature creation
- Signature structure must align with scaffold structure
- Validation should verify:
  - Nesting preservation (signature matches scaffold depth)
  - Concept alignment (signature describes match scaffold describes)
  - Proper code syntax (Mamba/Python)
  - Empty test bodies with signature markers
  - No implementation code yet

**Decision:** ✅ **Validation must check scaffold alignment and code syntax**
- Primary validation: Scaffold alignment (nesting, concepts, structure)
- Secondary validation: Code syntax (Mamba syntax, empty bodies, markers)
- Tertiary validation: BDD Section 1, 2, and 7 principles
- If scaffold not found, warn but still validate code syntax and BDD principles

## Implementation Plan

### Phase 1: Add Signature Guidance to Specializing Rules

**Files:** 
- `behaviors/bdd/bdd-mamba-rule.mdc` (Python/Mamba)
- `behaviors/bdd/bdd-jest-rule.mdc` (JavaScript/Jest)

**Integration Strategy:**

**Step 1: Add Signature Phase Section to Specializing Rules**

Add a new section to each specializing rule file covering signature phase requirements:

**Signature-Specific Content to Add (Framework-Specific):**

**For `bdd-mamba-rule.mdc` (Python/Mamba):**
- **Proper Code Syntax**:
  - Use `with description()`, `with context()`, `with it()`
  - Follow Mamba framework patterns
- **Empty Test Bodies**:
  - Use `pass` statement only
  - No mocks, no stubs, no helpers yet
  - Mark with `# BDD: SIGNATURE` comment at start of test body
- **Output Format**:
  - Updates test file directly (e.g., `test_zorbling.py`)
  - Preserves existing code structure
- **Sample Size**:
  - ~18 describe blocks per iteration
- **Nesting Preservation**:
  - Preserve ALL nesting levels from scaffold
  - Convert plain English to proper Mamba syntax

**For `bdd-jest-rule.mdc` (JavaScript/Jest):**
- **Proper Code Syntax**:
  - Use `describe()`, `it()`, nested `describe()` blocks
  - Follow Jest framework patterns
- **Empty Test Bodies**:
  - Empty function body (no statements)
  - No mocks, no stubs, no helpers yet
  - Mark with `// BDD: SIGNATURE` comment at start of test body
- **Output Format**:
  - Updates test file directly (e.g., `zorbling.test.js`)
  - Preserves existing code structure
- **Sample Size**:
  - ~18 describe blocks per iteration
- **Nesting Preservation**:
  - Preserve ALL nesting levels from scaffold
  - Convert plain English to proper Jest syntax

**Step 2: Update Commands Section in Specializing Rules**

Update the "Executing Commands" section in both `bdd-mamba-rule.mdc` and `bdd-jest-rule.mdc`:

```markdown
**Executing Commands:**
* `/bdd-validate` — Validate BDD test files against these principles
* `/bdd-workflow` — Execute BDD workflow phases (Domain Scaffold, Signatures, RED, GREEN, REFACTOR)
* `/bdd-scaffold` — Generate domain scaffolding (plain English hierarchy) from domain maps
* `/bdd-signature` — Generate test signatures (code structure) from scaffolds **NEW**
```

### Phase 2: Create Command Files

**Phase-Specific Command Files (bdd-signature):**
- `behaviors/bdd/bdd-signature/bdd-signature-cmd.md` - Main phase-specific command file
- `behaviors/bdd/bdd-signature/bdd-signature-generate-cmd.md` - Generate delegate (delegates to main command generate action)
- `behaviors/bdd/bdd-signature/bdd-signature-validate-cmd.md` - Validate delegate (delegates to main command validate action)

**Action:** Use `/code-agent-command` to generate:
- Feature: `bdd`
- Command: `bdd-signature`
- Purpose: Generate test signatures (code structure) from scaffolds following BDD principles
- Target Entity: Test file with signature blocks (e.g., `test_zorbling.py`)

**Command Structure Requirements:**
- **Purpose**: Generate test signatures (code structure) from scaffolds
- **Base Rule**: Reference `bdd-rule.mdc`:
  - Section 1 (Business Readable Language) - core principles
  - Section 2 (Fluency, Hierarchy, and Storytelling) - hierarchy patterns, fluency
- **Specializing Rule**: Reference `bdd-mamba-rule.mdc` (or `bdd-jest-rule.mdc`):
  - Signature Phase Section - framework-specific syntax, empty bodies, signature markers
- **Runner**: `behaviors/bdd/bdd-runner.py` (uses existing `BDDWorkflow` Phase 1 infrastructure)
- **Actions**: Standard 4-action pattern (Generate → User Feedback → Validate → User Feedback)

**Key Features in Command Files:**
1. **Scaffold Discovery**: Find scaffold file (`{test-file-stem}-hierarchy.txt`) to use as input
2. **Incremental Signature Creation**: 
   - Use existing `BDDIncrementalCommand._calculate_sample_size()` to identify scope
   - Find lowest-level describe block and count `it` blocks
   - Target ~18 describe blocks per iteration
   - Allow user to specify scope or system chooses next section
3. **Rule Focus**: Emphasize rules in prompts:
   - `bdd-rule.mdc` Section 1: Business readable language (base principles)
   - `bdd-rule.mdc` Section 2: Fluency, hierarchy, storytelling (base principles)
   - `bdd-mamba-rule.mdc` Signature Phase Section: Framework-specific signature requirements (code syntax, empty bodies, markers)

### Phase 3: Configure Command Integration

**No New Runner Code Needed** - The infrastructure already exists!

**Existing Infrastructure to Use (ALL FULLY IMPLEMENTED):**
- `BDDWorkflow` class (lines 1029-1102) - Creates all 5 phases including Phase 1 (Build Test Signatures)
- `BDDWorkflow._create_phase_command()` - Creates Phase 1 command with full wrapping chain
- `BDDWorkflowPhaseCommand` - Wraps WorkflowPhaseCommand, delegates generate/validate/start/approve
- `BDDIncrementalCommand` (lines 828-876) - Handles incremental work, calculates sample size
- `_get_signature_instructions()` (lines 1160-1176) - Has signature instructions
- `bdd_workflow()` function - CLI entry point for workflow

**Command Files Should:**
- Reference existing `BDDWorkflow` Phase 1 infrastructure
- Use existing `BDDIncrementalCommand` pattern for incremental work
- Reference `bdd-rule.mdc` Sections 1 and 2 (base principles)
- Reference `bdd-mamba-rule.mdc` Signature Phase Section (framework-specific signature requirements)
- Focus on specializing rule's signature phase section in generate/validate instructions

### Phase 4: Incremental Signature Creation

**Current State:**
- `BDDIncrementalCommand` infrastructure exists and is fully functional
- Signature creation benefits from incremental approach (~18 describe blocks per iteration)

**Decision:**
- Use existing `BDDIncrementalCommand._calculate_sample_size()` to identify scope
- Find lowest-level describe block and count `it` blocks
- Target ~18 describe blocks per iteration
- Allow user to specify scope or system chooses next unimplemented section
- Multiple iterations until entire test file has signatures

**Scope Selection Strategy:**
1. **System-Chosen Scope** (default):
   - Find next section without `# BDD: SIGNATURE` markers
   - Count describe/it blocks in that section
   - Stop when ~18 blocks reached or section ends
2. **User-Specified Scope**:
   - User specifies describe block name or line range
   - Generate signatures for that scope only
   - Respect user's scope choice

### Phase 5: Validation Configuration

**Validation Requirements:**
1. **Primary Check**: Scaffold alignment (if scaffold found)
   - Nesting preservation (signature matches scaffold depth)
   - Concept alignment (signature describes match scaffold describes)
   - No flattening (signature preserves all nesting levels)

2. **Secondary Check**: Code syntax (Mamba/Python)
   - Proper syntax: `describe()`, `it()`, `with_()`
   - Empty test bodies (no mocks, stubs, helpers)
   - Signature markers present (`# BDD: SIGNATURE`)
   - No implementation code yet

3. **Tertiary Check**: BDD principles
   - Base BDD principles (Sections 1 and 2)
   - Framework-specific signature requirements (specializing rule signature phase section)

4. **Fallback**: If scaffold not found
   - Warn user
   - Still validate code syntax and BDD principles

## Files to Create/Modify

### New Files:
- `behaviors/bdd/bdd-signature/bdd-signature-cmd.md`
- `behaviors/bdd/bdd-signature/bdd-signature-generate-cmd.md`
- `behaviors/bdd/bdd-signature/bdd-signature-validate-cmd.md`

### Modified Files:
- `behaviors/bdd/bdd-mamba-rule.mdc` - Add signature phase section:
  - Add new section for signature phase requirements (code syntax, empty bodies, markers)
  - Update Commands section with signature command references
- `behaviors/bdd/bdd-jest-rule.mdc` - Add signature phase section:
  - Add new section for signature phase requirements (code syntax, empty bodies, markers)
  - Update Commands section with signature command references with signature commands

### Code Changes Needed:
- `behaviors/bdd/bdd-runner.py` - Add signature heuristics (if needed):
  - **Analyze existing heuristics**: Check if existing BDD heuristics cover signature requirements
  - **NEW CODE (if needed)**: Add `BDDSignatureHeuristic` class for specializing rule signature phase validation
  - **NEW CODE (if needed)**: Update `BDDCommand._get_heuristic_map()` to include signature heuristic

## Implementation Steps (Following BDD TDD Workflow)

### Phase 0: Domain Scaffold (Analysis & Planning)
1. ✅ **Add Signature Phase Section to Specializing Rules**: 
   - Add signature phase section to `bdd-mamba-rule.mdc` (Python/Mamba framework-specific)
   - Add signature phase section to `bdd-jest-rule.mdc` (JavaScript/Jest framework-specific)
   - Include: code syntax, empty bodies, signature markers, nesting preservation
   - Update Commands section in both specializing rules with signature command references

### Phase 1: Signature (Test Structure)
2. **Create Test Signatures**: Add test signatures to `bdd_runner_test.py` (if needed):
   - Test for `BDDSignatureHeuristic` detection logic (if new heuristic needed)
   - Test for signature validation against scaffold
   - Test for proper code syntax validation (Mamba)
   - Test for empty body validation
   - Test for signature marker validation
   - Test for incremental scope calculation

### Phase 2: RED (Failing Tests)
3. **Implement RED Tests**: Write failing tests first (if new heuristic needed):
   - Test that `BDDSignatureHeuristic` detects missing signature markers
   - Test that `BDDSignatureHeuristic` detects implementation code in signature phase
   - Test that `BDDSignatureHeuristic` validates scaffold alignment
   - Test that signature command discovers scaffold files
   - Test that signature command generates code with proper syntax
   - Test that signature validation checks scaffold alignment

### Phase 3: GREEN (Make Tests Pass)
4. **Implement Signature Heuristic** (if needed): Add `BDDSignatureHeuristic` class:
   - Detect missing signature markers (`# BDD: SIGNATURE`)
   - Detect implementation code in signature phase (mocks, stubs, helpers)
   - Validate scaffold alignment (nesting, concepts, structure)
   - Validate proper code syntax (Mamba: `describe()`, `it()`, `with_()`)
   - Validate empty test bodies

5. **Update Heuristic Map** (if needed): Add signature heuristic to `BDDCommand._get_heuristic_map()`:
   ```python
   def _get_heuristic_map(self):
       return {
           1: BDDJargonHeuristic,
           2: BDDComprehensiveHeuristic,
           3: BDDDuplicateCodeHeuristic,
           4: BDDLayerFocusHeuristic,
           5: BDDFrontEndHeuristic,
           7: BDDScaffoldHeuristic,  # Section 7 - Scaffold
           8: BDDSignatureHeuristic,  # Section 7 - Signature (NEW - if needed)
       }
   ```

6. **Run Tests**: Verify all RED tests now pass (GREEN state)

### Phase 4: REFACTOR (Improve Code Quality)
7. **Refactor**: Improve code quality:
   - Extract scaffold parsing logic to helper methods
   - Extract code syntax validation to helper methods
   - Extract signature marker detection to helper methods
   - Add comprehensive docstrings
   - Run `/clean-code-validate-cmd` and fix violations
   - Run `/bdd-validate-cmd` and fix violations

### Phase 5: Integration & CLI Testing
8. **Create Command Files**: Use `/code-agent-command` to generate signature command files:
   - `behaviors/bdd/bdd-signature/bdd-signature-cmd.md`
   - `behaviors/bdd/bdd-signature/bdd-signature-generate-cmd.md`
   - `behaviors/bdd/bdd-signature/bdd-signature-validate-cmd.md`

9. **Configure Command Files**: Reference `bdd-rule.mdc` Sections 1 and 2 (base principles), and `bdd-mamba-rule.mdc` signature phase section (framework-specific)

10. **CLI Testing**: Test command from command line:
    - Use existing test scaffold from `test-scaffold/` directory
    - Run `/bdd-signature` command
    - Verify test file updated with signature blocks
    - Run `/bdd-signature-validate` command
    - Verify validation uses heuristics
    - Test within workflow: `/bdd-workflow` with Phase 1

## Success Criteria ✅

- ✅ Command generates test signature blocks (Python/Mamba code structure) following base BDD principles and specializing rule signature phase requirements
- ✅ Generates signatures incrementally with ~18 describe blocks per iteration
- ✅ Integrates with existing workflow infrastructure (Phase 1)
- ✅ References templates instead of duplicating content
- ✅ Validates against base BDD rules (Sections 1, 2) and specializing rule signature phase requirements using heuristics, plus scaffold alignment
- ✅ Works both standalone (`/bdd-signature`) and within workflow (`/bdd-workflow`)
- ✅ All tests pass (if new code added: RED → GREEN → REFACTOR cycle complete)
- ✅ CLI testing successful with existing test scaffold
- ✅ Heuristics detect violations in signature blocks (implementation code, missing markers, scaffold misalignment)

## New Code Required

### 1. Add Signature Phase Section to Specializing Rules

**Note:** This signature phase section should be added to BOTH `bdd-mamba-rule.mdc` AND `bdd-jest-rule.mdc` with framework-specific examples.

**Location:** `behaviors/bdd/bdd-mamba-rule.mdc` - Add new section after existing sections

**Content to Add (Mamba/Python version):**

```markdown
## 6. Signature Phase Requirements

When creating test signatures (Phase 1: Build Test Signatures), generate test structure with empty bodies:

**[DO]:**
* Use proper Mamba syntax: `with description()`, `with context()`, `with it()`
* Keep test bodies empty with only `pass` statement
* Mark each test with `# BDD: SIGNATURE` comment at start of body
* Preserve ALL nesting levels from scaffold hierarchy
* Convert plain English scaffold to proper code syntax
* Update test file directly (e.g., `test_zorbling.py`)

```python
# From scaffold (plain English):
# Zorbling Management
#   Creating Zorblings
#     should create zorbling with valid data

# To signature (code structure):
with description("Zorbling Management"):
    with context("Creating Zorblings"):
        with it("should create zorbling with valid data"):
            # BDD: SIGNATURE
            pass
```

**[DON'T]:**
* Add mocks, stubs, or helpers in signature phase
* Include implementation code or assertions
* Flatten hierarchy from scaffold
* Skip signature markers
* Change nesting structure from scaffold

```python
# Missing signature marker
with it("should create zorbling"):
    pass

# Has implementation code (wrong for signature phase)
with it("should create zorbling"):
    zorbling = Zorbling()
    expect(zorbling).not_to(be_none)
```
```

**Location:** `behaviors/bdd/bdd-jest-rule.mdc` - Add new section after existing sections  

**Content to Add (Jest/JavaScript version):**

```markdown
## 6. Signature Phase Requirements

When creating test signatures (Phase 1: Build Test Signatures), generate test structure with empty bodies:

**[DO]:**
* Use proper Jest syntax: `describe()`, `it()`, nested `describe()` blocks
* Keep test bodies empty (no statements)
* Mark each test with `// BDD: SIGNATURE` comment at start of body
* Preserve ALL nesting levels from scaffold hierarchy
* Convert plain English scaffold to proper code syntax
* Update test file directly (e.g., `zorbling.test.js`)

```javascript
// From scaffold (plain English):
// Zorbling Management
//   Creating Zorblings
//     should create zorbling with valid data

// To signature (code structure):
describe("Zorbling Management", () => {
  describe("Creating Zorblings", () => {
    it("should create zorbling with valid data", () => {
      // BDD: SIGNATURE
    });
  });
});
```

**[DON'T]:**
* Add mocks, stubs, or helpers in signature phase
* Include implementation code or assertions
* Flatten hierarchy from scaffold
* Skip signature markers
* Change nesting structure from scaffold
```

### 2. Add `BDDSignatureHeuristic` Class (if needed)

**Location:** `behaviors/bdd/bdd-runner.py` (after `BDDScaffoldHeuristic`)

**Purpose:** Validate signature output (code structure) against specializing rule signature phase requirements

**Detection Logic:**
- **Missing Signature Markers**: Scan for missing `# BDD: SIGNATURE` in describe/it blocks during signature phase
- **Implementation Code**: Detect mocks, stubs, helpers in signature phase (should be empty)
- **Scaffold Alignment**: Verify signature structure matches scaffold structure
- **Proper Code Syntax**: Ensure proper Mamba/Python syntax (`describe()`, `it()`, `with_()`)
- **Empty Bodies**: Validate test bodies are empty (only `pass` or `# BDD: SIGNATURE`)

**Implementation:**
```python
class BDDSignatureHeuristic(CodeHeuristic):
    """Heuristic for §7: Detects violations in signature test files"""
    def __init__(self):
        super().__init__("bdd_signature")
    
    def detect_violations(self, content):
        """Detect violations of Signature principles"""
        violations = []
        if not hasattr(content, '_content_lines') or not content._content_lines:
            return None
        
        # Detect missing signature markers
        in_signature_phase = False
        for i, line in enumerate(content._content_lines, 1):
            if '# BDD: SIGNATURE' in line or '// BDD: SIGNATURE' in line:
                in_signature_phase = True
            
            # Detect implementation code in signature phase
            if in_signature_phase:
                implementation_patterns = [
                    r'@patch',  # Mocking decorators
                    r'Mock\(',  # Mock objects
                    r'MagicMock\(',  # MagicMock objects
                    r'\.assert_',  # Assertions
                    r'\.expect\(',  # Expectations
                ]
                
                for pattern in implementation_patterns:
                    if re.search(pattern, line):
                        violations.append(Violation(i, "Signature contains implementation code - should be empty structure only"))
                        break
        
        return violations if violations else None
```

### 3. Update `BDDCommand._get_heuristic_map()` (if needed)

**Add Signature Heuristic:**
```python
def _get_heuristic_map(self):
    return {
        1: BDDJargonHeuristic,
        2: BDDComprehensiveHeuristic,
        3: BDDDuplicateCodeHeuristic,
        4: BDDLayerFocusHeuristic,
        5: BDDFrontEndHeuristic,
        7: BDDScaffoldHeuristic,  # Scaffold phase heuristic
        8: BDDSignatureHeuristic,  # Signature phase heuristic (NEW - if needed)
    }
```

## New Tests Required

### Test File: `behaviors/bdd/bdd_runner_test.py`

**Following RED-GREEN-REFACTOR approach (if new heuristic added):**

#### RED Phase Tests (Failing Initially):
1. **Test `BDDSignatureHeuristic` detects missing markers:**
   ```python
   with it('should detect missing signature markers in signature blocks'):
       # Test detects missing # BDD: SIGNATURE in test bodies
   ```

2. **Test `BDDSignatureHeuristic` detects implementation code:**
   ```python
   with it('should detect implementation code in signature phase'):
       # Test detects mocks, stubs, assertions in signature blocks
   ```

3. **Test `BDDSignatureHeuristic` validates scaffold alignment:**
   ```python
   with it('should validate signature hierarchy matches scaffold structure'):
       # Test compares signature nesting to scaffold nesting
   ```

4. **Test signature command discovers scaffold:**
   ```python
   with it('should discover scaffold files in test directory'):
       # Test finds {test-file-stem}-hierarchy.txt files
   ```

5. **Test signature validation uses heuristics:**
   ```python
   with it('should use BDDSignatureHeuristic for signature validation'):
       # Test that signature validation calls heuristic
   ```

#### GREEN Phase (Make Tests Pass):
- Implement `BDDSignatureHeuristic` class
- Update heuristic map
- Verify all tests pass

#### REFACTOR Phase (Improve Code):
- Extract helper methods
- Add docstrings
- Run validation commands
- Improve code organization

## Key Insights

1. **Code Changes May Be Minimal**: Existing heuristics may already cover signature requirements - analyze before implementing new heuristic
2. **Specializing Rules Strategy**: Signature guidance goes in specializing rules (`bdd-mamba-rule.mdc`, `bdd-jest-rule.mdc`), NOT base rule
3. **Framework-Specific Requirements**: Signature requirements are framework-specific (Python vs JavaScript syntax) so they belong in specializing rules
4. **Incremental Approach**: Signatures benefit from incremental creation (~18 describe blocks per iteration) unlike scaffold (all at once)
5. **Scaffold is Critical Input**: Validation must check scaffold alignment as primary check
6. **Empty Bodies Required**: Signatures have structure only, no implementation code yet
7. **Follow Existing Patterns**: Use `BDDIncrementalCommand` pattern for incremental work
8. **Template References**: Command files should reference rule templates, not duplicate content
9. **Phase 1 Infrastructure Exists**: Workflow Phase 1 fully implemented, command references existing infrastructure
10. **Scope Selection Strategy**: System chooses next unimplemented section or user specifies scope
11. **CLI Testing Critical**: Must test from command line with existing test scaffold to verify end-to-end functionality
12. **Base Rule Stays Framework-Agnostic**: Keep base `bdd-rule.mdc` focused on framework-agnostic principles, specializing rules handle framework-specific details

## Implementation Status

**Status:** READY FOR IMPLEMENTATION

**Next Steps:**
1. Add signature phase section to `bdd-mamba-rule.mdc` (Python/Mamba-specific)
2. Add signature phase section to `bdd-jest-rule.mdc` (JavaScript/Jest-specific)
3. Update Commands section in both specializing rules
4. Analyze if new `BDDSignatureHeuristic` needed or if existing heuristics sufficient
5. Create command files using `/code-agent-command`
6. Configure command files with rule references (base rule + specializing rule)
7. CLI testing with existing test scaffold

