# BDD Test Command Implementation Plan

## Overview
Create a `/bdd-test` command that generates test implementation code from test signatures following BDD principles. The command will integrate with the existing `BDDWorkflow` infrastructure (Phase 2 - replacing legacy "RED" phase) and support incremental test implementation (sub-domain selection).

## Key Requirements

1. **Use New BDD Rules**: Reference `bdd-rule.mdc` (base principles), `bdd-mamba-rule.mdc` (Python/Mamba framework-specific, includes test implementation guidance)
2. **Focus on Test Implementation**: Write actual test code with Arrange-Act-Assert, mocks, helpers, assertions
3. **Incremental Support**: Allow test implementation for specific sub-domains or let system choose scope (~18 describe blocks per iteration)
4. **Workflow Integration**: Integrate with existing `BDDWorkflow` infrastructure (Phase 2 - replacing RED)
5. **Template References**: Reference templates in prompts, don't duplicate template content
6. **Natural Test Failures**: If production code exists, call it; if it doesn't exist, tests fail naturally - NO commenting out code

## Investigation Results

### 1. Test Implementation Requirements - FINDINGS

**Current State:**
- Test implementation phase instructions exist in `_get_red_instructions()` (lines 1178-1193) - **NEEDS RENAMING to `_get_test_instructions()`**
- Current approach uses commenting out code (legacy pattern to remove)
- Test implementation requirements embedded in workflow instructions
- All references to "RED" need to be removed from code, commands, and rules

**Analysis of Test Implementation Requirements:**
- **Focus**: Test implementation (Stage 2 - write test code with full Arrange-Act-Assert)
- **Key Content**:
  - Convert signature blocks to full test implementations
  - Add proper Arrange-Act-Assert structure
  - Include mocks, stubs, helpers following BDD principles
  - Extract duplicate setup to shared contexts
  - Create helper factories for repeated mocks
  - Tests call production code directly (no commenting)
  - If production code doesn't exist, tests fail naturally
  - Sample Size: ~18 describe/it blocks per iteration
  - Output: Updates test file with implemented test bodies
- **Scope**: Stage 2 (test implementation) only
- **Integration**: Uses signature as input, applies BDD § 1, 2, 3 principles

**Test vs Signature Differences:**
- **Signature**: Code structure only, empty bodies with `# BDD: SIGNATURE` markers
- **Test**: Full test implementation with Arrange-Act-Assert, mocks, assertions
- **Common**: Both preserve hierarchy, follow BDD principles, use ~18 describe blocks per iteration

**Decision: ✅ Add Test Implementation Section to Specializing Rules**

**Integration Strategy:**
- Base rule Sections 1, 2, 3: Apply to test implementation
- Specializing rules: Include test implementation section with framework-specific guidance
- Test command references base rule and specializing rule test implementation section

### 2. Workflow Integration - FINDINGS

**Current State:**
- `BDDWorkflow` class (lines 1029-1102) **FULLY IMPLEMENTED** - creates all 5 phases:
  - Phase 0: Domain Scaffolding
  - Phase 1: Build Test Signatures
  - **Phase 2: Write Tests** ← THIS COMMAND (previously "RED - Create Failing Tests")
  - Phase 3: Write Code (previously "GREEN - Make Tests Pass")
  - Phase 4: REFACTOR - Improve Code
- Wrapping chain: `BDDWorkflowPhaseCommand → IncrementalCommand → CodeAugmentedCommand → SpecializingRuleCommand → Command`
- `BDDIncrementalCommand` extends `IncrementalCommand` and calculates sample size from test structure (lines 828-876)
- `_get_red_instructions()` already exists (lines 1178-1193) - **NEEDS RENAMING to `_get_test_instructions()`**
- CLI entry point exists: `bdd_workflow()` function and workflow command handler

**Decision:** The command should work BOTH ways:
1. **Standalone**: `/bdd-test` can be invoked directly (uses BDDWorkflow Phase 2 infrastructure)
2. **Within Workflow**: `/bdd-workflow` dispatches to Phase 2 (same infrastructure)

### 3. Incremental Test Implementation - FINDINGS

**Current State:**
- `IncrementalCommand` supports `sample_size` and `max_sample_size` (default 18)
- `BDDIncrementalCommand._calculate_sample_size()` finds lowest-level describe block and counts `it` blocks
- Test implementation benefits from incremental approach (~18 describe blocks per iteration)

**Decision:** ✅ **Incremental test implementation with ~18 describe blocks**
- Use existing `BDDIncrementalCommand._calculate_sample_size()` to identify work scope
- Find lowest-level describe block and count `it` blocks
- Target ~18 describe blocks per iteration
- Allow user to specify scope or let system choose next unimplemented section
- Multiple iterations until entire test file has implementations

### 4. Validation Should Check Test Structure and Coverage

**Analysis:**
- Signature structure is **critical input** for test implementation
- Test implementation must align with signature structure
- Validation should verify:
  - Nesting preservation (tests match signature depth)
  - All signatures implemented (no remaining `# BDD: SIGNATURE` markers)
  - Proper Arrange-Act-Assert structure
  - Appropriate mocking (§3 principles)
  - No duplicate code across tests
  - Tests call production code (not commented out)

**Decision:** ✅ **Validation must check signature alignment and test structure**
- Primary validation: Signature alignment (all signatures implemented, structure preserved)
- Secondary validation: Test structure (Arrange-Act-Assert, proper mocking, no duplication)
- Tertiary validation: Base BDD principles (Sections 1, 2, 3)
- If signature not found, validation should warn but still check test structure

## Analysis Results - Questions Resolved

### Question 1: Should test implementation guidance be added to specializing rules?

**Analysis:**
- Base `bdd-rule.mdc` Section 3 "Balance Context Sharing with Localization" covers helper patterns
- Test implementation requirements (framework-specific syntax, mocking, assertions) are **framework-specific** and should be in specializing rules
- Currently `bdd-mamba-rule.mdc` does NOT cover test implementation phase requirements (needs to be added)

**Decision:** ✅ **Add Test Implementation Principles to Base Rule, Examples to Specializing Rules**

**Rationale:**
- Test implementation **principles** are **framework-agnostic** (Arrange-Act-Assert, proper mocking, helper extraction)
- Test implementation **examples** are **framework-specific** (Python syntax vs JavaScript syntax)
- Add new section to `bdd-rule.mdc` with framework-agnostic test implementation principles
- Add examples to specializing rules (`bdd-mamba-rule.mdc`, `bdd-jest-rule.mdc`) showing framework-specific syntax
- Framework-specific details (syntax, mocking libraries) belong in framework-specific rules

### Question 2: Code Already Exists - Command Infrastructure Analysis

**Analysis:**
- `BDDWorkflow` class (lines 1029-1102) **FULLY IMPLEMENTED** - includes Phase 2 (currently "RED - Create Failing Tests")
- `_create_phase_command()` creates Phase 2 with full wrapping chain
- `BDDIncrementalCommand` (lines 828-876) calculates sample size from test structure
- `_get_red_instructions()` (lines 1178-1193) - **NEEDS COMPLETE REFACTORING**
- CLI handler exists: `bdd_workflow()` function and workflow command handler

**Decision:** ✅ **MINIMAL NEW CODE NEEDED** - Rename methods, update instructions, and add test implementation section to rules
- We need to:
  1. **RENAME**: `_get_red_instructions()` → `_get_test_instructions()`
  2. **REMOVE**: All "RED" terminology from code, commands, rules
  3. **UPDATE**: Phase 2 name from "RED - Create Failing Tests" to "Write Tests"
  4. Create command files (`bdd-test-cmd.md` and delegates) that reference existing workflow infrastructure
  5. Add test implementation section to specializing rules (`bdd-mamba-rule.mdc`, `bdd-jest-rule.mdc`)
  6. Update `_get_test_instructions()` to remove comment-out pattern and focus on natural test failures
  7. Both standalone and workflow routes use the same BDDWorkflow Phase 2 infrastructure

### Question 3: Incremental Scope Selection

**Analysis:**
- `BDDIncrementalCommand._calculate_sample_size()` works on test files (finds lowest describe block, counts `it` blocks)
- For test implementation, we work on test files directly (identifying unimplemented signatures)
- Test implementation benefits from incremental approach (~18 describe blocks per iteration)

**Decision:** ✅ **Incremental test implementation with scope selection**
- Use existing `BDDIncrementalCommand._calculate_sample_size()` to identify scope
- Find signatures with `# BDD: SIGNATURE` markers (unimplemented)
- Target ~18 describe blocks per iteration
- Allow user to specify scope or system chooses next unimplemented section
- Multiple iterations until all signatures are implemented

### Question 4: Validation Should Check Implementation Completeness

**Analysis:**
- Signatures are **critical input** for test implementation
- Test implementation must cover all signatures
- Validation should verify:
  - All signatures implemented (no remaining `# BDD: SIGNATURE` markers)
  - Proper test structure (Arrange-Act-Assert)
  - Appropriate mocking (§3 principles - only mock boundaries, not internals)
  - No code duplication (§3 principles - extract to helpers)
  - Tests call production code directly (no commented code)

**Decision:** ✅ **Validation must check implementation completeness and test quality**
- Primary validation: All signatures implemented
- Secondary validation: Test structure quality (Arrange-Act-Assert, proper mocking)
- Tertiary validation: Base BDD principles (Sections 1, 2, 3)
- If signatures remain, warn and guide to next section

## Implementation Plan

### Phase 1: Add Test Implementation Section to Base Rule and Examples to Specializing Rules

**Files:** 
- `behaviors/bdd/bdd-rule.mdc` (framework-agnostic principles)
- `behaviors/bdd/bdd-mamba-rule.mdc` (Python/Mamba examples)
- `behaviors/bdd/bdd-jest-rule.mdc` (JavaScript/Jest examples)

**Integration Strategy:**

**Step 1: Add Test Implementation Principles to Base Rule**

Add a new section to `bdd-rule.mdc` with framework-agnostic test implementation principles:

**Content to Add to `bdd-rule.mdc`:**

```markdown
## 8. Test Implementation Phase

When implementing tests from signatures (Phase 2: Write Tests), convert empty signatures to full test implementations:

### 8.1 Arrange-Act-Assert Structure

Organize each test with clear structure:
- **Arrange**: Set up test data, mocks, and preconditions
- **Act**: Call the production code under test
- **Assert**: Verify the expected outcomes

### 8.2 Proper Mocking

Mock only at architectural boundaries:
- **DO** mock: External dependencies (file I/O, network calls, databases, APIs)
- **DON'T** mock: Internal classes, business logic, or the code under test
- Extract mock creation to helper functions to reduce duplication

### 8.3 Helper Extraction

Avoid duplication through shared setup:
- Extract duplicate test data creation to factory functions
- Move common setup to shared context (beforeEach/before.each)
- Create reusable helper functions for complex setup
- Keep test bodies focused on the specific behavior being tested

### 8.4 Natural Test Failures

Tests call production code directly:
- **DO**: Call production code as it will be used
- **DON'T**: Comment out production code calls
- If production code doesn't exist, tests fail naturally with clear error messages
- This approach shows exactly what needs to be implemented next

### 8.5 Signature Conversion

Replace signature markers with full implementations:
- Find tests marked with `# BDD: SIGNATURE` or `// BDD: SIGNATURE`
- Replace empty bodies with Arrange-Act-Assert structure
- Remove signature markers when implementation complete
- Preserve all test structure and hierarchy from signatures
```

**Step 2: Add Test Implementation Examples to Specializing Rules**

Add framework-specific examples to each specializing rule file:

**Test Implementation Examples to Add (Framework-Specific):**

**For `bdd-mamba-rule.mdc` (Python/Mamba):**

```markdown
## 7. Test Implementation Phase Examples

When implementing tests from signatures (Phase 2: Write Tests), follow base rule § 8 principles with Mamba-specific syntax:

**[DO]:**
* Use Arrange-Act-Assert structure with Python syntax
* Mock using `unittest.mock` or `mamba` mocks
* Extract setup to helper functions or `with before.each`
* Call production code directly - let tests fail naturally if code doesn't exist
* Replace `# BDD: SIGNATURE` markers with full implementation

```python
# From signature:
with it("should create user with valid email"):
    # BDD: SIGNATURE
    pass

# To full test implementation:
with it("should create user with valid email"):
    # Arrange
    email = "test@example.com"
    user_data = {"email": email, "name": "Test User"}
    
    # Act
    user = create_user(user_data)
    
    # Assert
    expect(user.email).to(equal(email))
    expect(user.is_active).to(be_true)
```

**[DON'T]:**
* Comment out production code calls
* Mock internal business logic
* Duplicate setup across sibling tests
```

**For `bdd-jest-rule.mdc` (JavaScript/Jest):**

```markdown
## 7. Test Implementation Phase Examples

When implementing tests from signatures (Phase 2: Write Tests), follow base rule § 8 principles with Jest-specific syntax:

**[DO]:**
* Use Arrange-Act-Assert structure with JavaScript syntax
* Mock using `jest.mock()` for modules or `jest.fn()` for functions
* Extract setup to helper functions or `beforeEach()`
* Call production code directly - let tests fail naturally if code doesn't exist
* Replace `// BDD: SIGNATURE` markers with full implementation

```javascript
// From signature:
it("should create user with valid email", () => {
  // BDD: SIGNATURE
});

// To full test implementation:
it("should create user with valid email", () => {
  // Arrange
  const email = "test@example.com";
  const userData = { email, name: "Test User" };
  
  // Act
  const user = createUser(userData);
  
  // Assert
  expect(user.email).toBe(email);
  expect(user.isActive).toBe(true);
});
```

**[DON'T]:**
* Comment out production code calls
* Mock internal business logic
* Duplicate setup across sibling tests
```

**Step 3: Update Commands Section in Base Rule and Specializing Rules**

Update "Executing Commands" section in `bdd-rule.mdc`:
```markdown
**Executing Commands:**
* `/bdd-validate` — Validate BDD test files against these principles
* `/bdd-workflow` — Execute BDD workflow phases (Domain Scaffold, Signatures, Write Tests, Write Code)
* `/bdd-scaffold` — Generate domain scaffolding (plain English hierarchy) from domain maps
* `/bdd-signature` — Generate test signatures (code structure) from scaffolds
* `/bdd-test` — Implement test code from signatures **NEW**
```

Update "Executing Commands" section in both `bdd-mamba-rule.mdc` and `bdd-jest-rule.mdc`:
```markdown
**Executing Commands:**
* `/bdd-validate` — Validate BDD test files against these principles
* `/bdd-workflow` — Execute BDD workflow phases (Domain Scaffold, Signatures, Write Tests, Write Code)
* `/bdd-scaffold` — Generate domain scaffolding (plain English hierarchy) from domain maps
* `/bdd-signature` — Generate test signatures (code structure) from scaffolds
* `/bdd-test` — Implement test code from signatures **NEW**
```

### Phase 2: Create Command Files

**Phase-Specific Command Files (bdd-test):**
- `behaviors/bdd/bdd-test/bdd-test-cmd.md` - Main phase-specific command file
- `behaviors/bdd/bdd-test/bdd-test-generate-cmd.md` - Generate delegate (delegates to main command generate action)
- `behaviors/bdd/bdd-test/bdd-test-validate-cmd.md` - Validate delegate (delegates to main command validate action)

**Action:** Use `/code-agent-command` to generate:
- Feature: `bdd`
- Command: `bdd-test`
- Purpose: Implement test code from signatures following BDD principles
- Target Entity: Test file with full test implementations (e.g., `test_zorbling.py`)

**Command Structure Requirements:**
- **Purpose**: Implement test code (Arrange-Act-Assert with mocks and assertions) from signatures
- **Base Rule**: Reference `bdd-rule.mdc`:
  - Section 1 (Business Readable Language) - core principles
  - Section 2 (Fluency, Hierarchy, and Storytelling) - hierarchy patterns, fluency
  - Section 3 (Balance Context Sharing with Localization) - helper patterns, mock usage
  - Section 8 (Test Implementation Phase) - framework-agnostic test implementation principles **NEW**
- **Specializing Rule**: Reference `bdd-mamba-rule.mdc` (or `bdd-jest-rule.mdc`):
  - Section 7: Test Implementation Phase Examples - framework-specific syntax examples
- **Runner**: `behaviors/bdd/bdd-runner.py` (uses existing `BDDWorkflow` Phase 2 infrastructure)
- **Actions**: Standard 4-action pattern (Generate → User Feedback → Validate → User Feedback)

**Key Features in Command Files:**
1. **Signature Discovery**: Find signatures with `# BDD: SIGNATURE` markers (unimplemented)
2. **Incremental Test Implementation**: 
   - Use existing `BDDIncrementalCommand._calculate_sample_size()` to identify scope
   - Find unimplemented signatures
   - Target ~18 describe blocks per iteration
   - Allow user to specify scope or system chooses next section
3. **Rule Focus**: Emphasize rules in prompts:
   - `bdd-rule.mdc` Sections 1, 2, 3, 8: Business readable language, fluency, helper patterns, test implementation principles
   - `bdd-mamba-rule.mdc` Section 7: Framework-specific test implementation examples (syntax)

### Phase 3: Configure Command Integration

**No New Runner Code Needed** - The infrastructure already exists!

**Existing Infrastructure to Use (ALL FULLY IMPLEMENTED):**
- `BDDWorkflow` class (lines 1029-1102) - Creates all 5 phases including Phase 2 (RED - Create Failing Tests)
- `BDDWorkflow._create_phase_command()` - Creates Phase 2 command with full wrapping chain
- `BDDWorkflowPhaseCommand` - Wraps WorkflowPhaseCommand, delegates generate/validate/start/approve
- `BDDIncrementalCommand` (lines 828-876) - Handles incremental work, calculates sample size
- `_get_red_instructions()` (lines 1178-1193) - Has RED instructions (needs updating)
- `bdd_workflow()` function - CLI entry point for workflow

**Updates Needed:**
- **RENAME**: `_get_red_instructions()` → `_get_test_instructions()`
- **REMOVE**: All "RED" terminology from method names, phase names, comments
- **UPDATE**: Phase 2 name from "RED - Create Failing Tests" to "Write Tests"
- **UPDATE**: Instructions to remove comment-out pattern and focus on natural test failures

**Command Files Should:**
- Reference existing `BDDWorkflow` Phase 2 infrastructure
- Use existing `BDDIncrementalCommand` pattern for incremental work
- Reference `bdd-rule.mdc` Sections 1, 2, 3, and 8 (base principles including test implementation)
- Reference `bdd-mamba-rule.mdc` Section 7 (framework-specific examples)
- Focus on base rule § 8 for principles, specializing rule § 7 for syntax in generate/validate instructions

### Phase 4: Incremental Test Implementation

**Current State:**
- `BDDIncrementalCommand` infrastructure exists and is fully functional
- Test implementation benefits from incremental approach (~18 describe blocks per iteration)

**Decision:**
- Use existing `BDDIncrementalCommand._calculate_sample_size()` to identify scope
- Find signatures with `# BDD: SIGNATURE` markers (unimplemented)
- Target ~18 describe blocks per iteration
- Allow user to specify scope or system chooses next unimplemented section
- Multiple iterations until all signatures are implemented

**Scope Selection Strategy:**
1. **System-Chosen Scope** (default):
   - Find next section with `# BDD: SIGNATURE` markers
   - Count describe/it blocks in that section
   - Stop when ~18 blocks reached or section ends
2. **User-Specified Scope**:
   - User specifies describe block name or line range
   - Implement tests for that scope only
   - Respect user's scope choice

### Phase 5: Validation Configuration

**Validation Requirements:**
1. **Primary Check**: Implementation completeness
   - All signatures implemented (no remaining `# BDD: SIGNATURE` markers)
   - Test structure preserved (matches signature structure)
   - No flattening detected

2. **Secondary Check**: Test quality (Mamba/Python)
   - Proper Arrange-Act-Assert structure
   - Appropriate mocking (§3 - mock boundaries, not internals)
   - No code duplication (§3 - extract to helpers)
   - Tests call production code directly (no commented code)
   - Proper assertions with `expect()`

3. **Tertiary Check**: BDD principles
   - Base BDD principles (Sections 1, 2, 3)
   - Framework-specific test implementation requirements (specializing rule)

4. **Progress Check**: If signatures remain
   - Warn user about unimplemented signatures
   - Guide to next section for implementation

## Files to Create/Modify

### New Files:
- `behaviors/bdd/bdd-test/bdd-test-cmd.md`
- `behaviors/bdd/bdd-test/bdd-test-generate-cmd.md`
- `behaviors/bdd/bdd-test/bdd-test-validate-cmd.md`

### Modified Files:
- `behaviors/bdd/bdd-rule.mdc` - Add test implementation principles:
  - Add new Section 8: Test Implementation Phase (framework-agnostic principles)
  - Update Commands section with test command references
- `behaviors/bdd/bdd-mamba-rule.mdc` - Add test implementation examples:
  - Add new Section 7: Test Implementation Phase Examples (Python/Mamba syntax)
  - Update Commands section with test command references
- `behaviors/bdd/bdd-jest-rule.mdc` - Add test implementation examples:
  - Add new Section 7: Test Implementation Phase Examples (JavaScript/Jest syntax)
  - Update Commands section with test command references
- `behaviors/bdd/bdd-runner.py` - Update Phase 2:
  - **RENAME**: `_get_red_instructions()` → `_get_test_instructions()`
  - **REMOVE**: All "RED" references (method names, phase names, comments, docstrings)
  - **UPDATE**: Phase 2 name from "RED - Create Failing Tests" to "Write Tests"
  - **UPDATE**: Instructions to remove comment-out pattern and focus on natural test failures
  - **UPDATE**: All references to RED phase in enum, constants, or phase identification

### Code Changes Needed:
- `behaviors/bdd/bdd-runner.py` - Comprehensive Phase 2 refactoring:
  - **RENAME**: `_get_red_instructions()` → `_get_test_instructions()`
  - **REMOVE**: All "RED" terminology (search for "red", "RED", "Red" in method names, variables, comments, docstrings)
  - **UPDATE**: Phase 2 name from "RED - Create Failing Tests" to "Write Tests"
  - **UPDATE**: `_get_test_instructions()` content to remove comment-out pattern
  - **UPDATE**: BDDPhase enum if it exists (RED → TEST)
  - **NEW CODE (if needed)**: Add `BDDTestImplementationHeuristic` class if existing heuristics don't cover test implementation validation

## Implementation Steps (Following BDD TDD Workflow)

### Phase 0: Domain Scaffold (Analysis & Planning)
1. ✅ **Add Test Implementation to Base Rule and Examples to Specializing Rules**: 
   - Add Section 8 to `bdd-rule.mdc` (framework-agnostic test implementation principles)
   - Add Section 7 to `bdd-mamba-rule.mdc` (Python/Mamba framework-specific examples)
   - Add Section 7 to `bdd-jest-rule.mdc` (JavaScript/Jest framework-specific examples)
   - Principles: Arrange-Act-Assert, proper mocking, helper patterns, no commented code, natural test failures
   - Update Commands section in base rule and both specializing rules with test command references

### Phase 1: Signature (Test Structure)
2. **Create Test Signatures**: Add test signatures to `bdd_runner_test.py` (if needed):
   - Test for test implementation validation (if new heuristic needed)
   - Test for signature marker detection (finding unimplemented signatures)
   - Test for proper Arrange-Act-Assert structure validation
   - Test for mocking validation (boundaries only)
   - Test for incremental scope calculation

### Phase 2: RED (Failing Tests)
3. **Implement RED Tests**: Write failing tests first (if new heuristic needed):
   - Test that heuristic detects remaining `# BDD: SIGNATURE` markers
   - Test that heuristic detects commented code violations
   - Test that heuristic validates Arrange-Act-Assert structure
   - Test that test command discovers unimplemented signatures
   - Test that test command generates proper test implementation
   - Test that test validation checks implementation completeness

### Phase 3: GREEN (Make Tests Pass)
4. **Rename and Update Phase 2 Method**: Refactor `_get_red_instructions()`:
   - **RENAME**: `_get_red_instructions()` → `_get_test_instructions()`
   - **REMOVE**: All RED terminology from method, comments, docstrings
   - **UPDATE**: Instructions content:
     * Remove comment-out pattern instructions
     * Add natural test failure guidance (call production code, let tests fail if code doesn't exist)
     * Add Arrange-Act-Assert structure guidance
     * Add proper mocking guidance (boundaries only)
     * Add helper extraction guidance

5. **Remove RED from Codebase**: Global search and replace:
   - Find all references to "RED", "red", "Red" in `bdd-runner.py`
   - Update phase names, enum values, constants
   - Update method names, variable names
   - Update comments and docstrings
   - Change from "RED - Create Failing Tests" to "Write Tests"

6. **Implement Test Heuristic** (if needed): Add heuristic class for test implementation validation

7. **Run Tests**: Verify all RED tests now pass (GREEN state)

### Phase 4: REFACTOR (Improve Code Quality)
8. **Refactor**: Improve code quality:
   - Extract validation logic to helper methods
   - Add comprehensive docstrings
   - Run `/clean-code-validate-cmd` and fix violations
   - Run `/bdd-validate-cmd` and fix violations

### Phase 5: Integration & CLI Testing
9. **Create Command Files**: Use `/code-agent-command` to generate test command files:
   - `behaviors/bdd/bdd-test/bdd-test-cmd.md`
   - `behaviors/bdd/bdd-test/bdd-test-generate-cmd.md`
   - `behaviors/bdd/bdd-test/bdd-test-validate-cmd.md`

10. **Configure Command Files**: Reference `bdd-rule.mdc` Sections 1, 2, 3, and 8 (base principles including test implementation), and `bdd-mamba-rule.mdc` Section 7 (framework-specific examples)

11. **Verify RED Removal**: Search codebase to ensure all RED terminology removed:
    - Search for "RED", "red", "Red" in `bdd-runner.py`
    - Search for "RED" in command files
    - Search for "RED" in rule files
    - Ensure all replaced with "Write Tests" or "test implementation"

12. **CLI Testing**: Test command:
    - Use signature file with `# BDD: SIGNATURE` markers
    - Run `/bdd-test` command
    - Verify test file updated with full test implementations
    - Run `/bdd-test-validate` command
    - Verify validation detects issues

## Success Criteria ✅

- ✅ Command generates test implementations (Python/Mamba code with Arrange-Act-Assert) following base BDD principles and specializing rule requirements
- ✅ Generates implementations incrementally with ~18 describe blocks per iteration
- ✅ Integrates with existing workflow infrastructure (Phase 2)
- ✅ References templates instead of duplicating content
- ✅ Validates against base BDD rules (Sections 1, 2, 3, 8) and specializing rule test implementation examples
- ✅ Works both standalone (`/bdd-test`) and within workflow (`/bdd-workflow`)
- ✅ All tests pass (if new code added: RED → GREEN → REFACTOR cycle complete)
- ✅ CLI testing successful with signature file
- ✅ No commented code pattern - tests call production code directly and fail naturally if code doesn't exist

## Key Insights

1. **Eliminate RED Terminology**: Complete removal of "RED" from all code, commands, rules - focus on "Write Tests"
2. **Method Renaming**: `_get_red_instructions()` → `_get_test_instructions()`
3. **Phase Renaming**: "RED - Create Failing Tests" → "Write Tests"
4. **No Commented Code**: Tests call production code directly; if code doesn't exist, tests fail naturally
5. **Base Rule for Principles**: Test implementation **principles** go in base rule (framework-agnostic)
6. **Specializing Rules for Examples**: Test implementation **examples** go in specializing rules (framework-specific syntax)
7. **Incremental Approach**: Tests benefit from incremental implementation (~18 describe blocks per iteration)
8. **Signature as Input**: Signatures with `# BDD: SIGNATURE` markers are critical input
9. **Follow Existing Patterns**: Use `BDDIncrementalCommand` pattern for incremental work
10. **Template References**: Command files should reference rule templates, not duplicate content
11. **Phase 2 Infrastructure Exists**: Workflow Phase 2 fully implemented, just needs renaming and instruction updates
12. **Scope Selection Strategy**: System chooses next unimplemented section or user specifies scope
13. **Natural Test Failures**: Modern approach - just write tests that call production code, let them fail naturally
14. **Base Rule Stays Framework-Agnostic**: Keep base `bdd-rule.mdc` focused on framework-agnostic principles
15. **Global Refactoring Required**: Search entire codebase for RED references and update them all

## Implementation Status

**Status:** READY FOR IMPLEMENTATION

**Next Steps:**
1. **Global RED Removal**: Search and replace all "RED" terminology in codebase:
   - `bdd-runner.py`: Method names, phase names, enums, constants, comments
   - Rule files: Remove any RED references
   - Command files: Ensure no RED terminology
2. **Method Renaming**: `_get_red_instructions()` → `_get_test_instructions()`
3. **Phase Renaming**: "RED - Create Failing Tests" → "Write Tests" throughout codebase
4. **Add Section 8 to Base Rule**: Add test implementation principles to `bdd-rule.mdc` (framework-agnostic)
5. **Add Section 7 to Specializing Rules**: 
   - Add test implementation examples to `bdd-mamba-rule.mdc` (Python/Mamba syntax)
   - Add test implementation examples to `bdd-jest-rule.mdc` (JavaScript/Jest syntax)
6. **Update Commands Sections**: Update in base rule and both specializing rules
7. **Update Instructions**: Update `_get_test_instructions()` content to remove comment-out pattern
8. Create command files using `/code-agent-command`
9. Configure command files with rule references (base rule § 8 + specializing rule § 7)
10. Verify no RED references remain in codebase
11. CLI testing with signature file

