# BDD Code Command Implementation Plan

## Overview
Create a `/bdd-code` command that generates production code to make tests pass following BDD principles. The command will integrate with the existing `BDDWorkflow` infrastructure (Phase 3 - replacing legacy "GREEN" phase) and support incremental code implementation.

## Key Requirements

1. **Use New BDD Rules**: Reference `bdd-rule.mdc` (base principles), `bdd-mamba-rule.mdc` (Python/Mamba framework-specific, includes code implementation guidance)
2. **Focus on Production Code**: Write minimal code to make tests pass, no extra features
3. **Incremental Support**: Allow code implementation for specific test sections or let system choose scope
4. **Workflow Integration**: Integrate with existing `BDDWorkflow` infrastructure (Phase 3 - replacing GREEN)
5. **Template References**: Reference templates in prompts, don't duplicate template content
6. **Minimal Implementation**: Only implement what tests demand - no speculative features

## Investigation Results

### 1. Code Implementation Requirements - FINDINGS

**Current State:**
- GREEN phase instructions exist in `_get_green_instructions()` (lines ~1196-1206) - **NEEDS RENAMING to `_get_code_instructions()` - ALREADY DONE**
- Focus on making tests pass with minimal code
- Code implementation requirements embedded in workflow instructions
- All references to "GREEN" need to be removed from code, commands, and rules (mostly done, verify remaining)

**Analysis of Code Implementation Requirements:**
- **Focus**: Production code implementation (Stage 3 - write code to make tests pass)
- **Key Content**:
  - Implement minimal production code for failing tests
  - Make tests pass with simplest solution
  - Resist adding features no test demands
  - Verify tests pass after implementation
  - Check for regressions in existing tests
  - Sample Size: Code for ~18 tests per iteration
  - Output: Updates production code files
- **Scope**: Stage 3 (code implementation) only
- **Integration**: Uses test implementations as input, applies minimalism principle

**Code vs Test Differences:**
- **Test**: Write test code with Arrange-Act-Assert, mocks, assertions
- **Code**: Write production code to make tests pass, minimal implementation only
- **Common**: Both work incrementally, follow BDD principles

**Decision: ✅ Add Code Implementation Principles to Base Rule, Examples to Specializing Rules**

**Integration Strategy:**
- Base rule Section 9: Framework-agnostic code implementation principles
- Specializing rules Section 8: Framework-specific code implementation examples
- Code command references base rule and specializing rule

### 2. Workflow Integration - FINDINGS

**Current State:**
- `BDDWorkflow` class (lines 1029-1102) **FULLY IMPLEMENTED** - creates all 5 phases:
  - Phase 0: Domain Scaffolding
  - Phase 1: Build Test Signatures
  - Phase 2: Write Tests (updated from RED)
  - **Phase 3: Write Code** ← THIS COMMAND (was "GREEN - Make Tests Pass" - ALREADY RENAMED)
  - Phase 4: REFACTOR - Improve Code
- Wrapping chain: `BDDWorkflowPhaseCommand → IncrementalCommand → CodeAugmentedCommand → SpecializingRuleCommand → Command`
- `BDDIncrementalCommand` extends `IncrementalCommand` and calculates sample size from test structure
- `_get_code_instructions()` already exists (renamed from `_get_green_instructions()`) - ALREADY UPDATED
- CLI entry point exists: `bdd_workflow()` function and workflow command handler

**Decision:** The command should work BOTH ways:
1. **Standalone**: `/bdd-code` can be invoked directly (uses BDDWorkflow Phase 3 infrastructure)
2. **Within Workflow**: `/bdd-workflow` dispatches to Phase 3 (same infrastructure)

### 3. Incremental Code Implementation - FINDINGS

**Current State:**
- `BDDIncrementalCommand` infrastructure exists and is fully functional
- Code implementation benefits from incremental approach (implement code for ~18 tests per iteration)

**Decision:** ✅ **Incremental code implementation aligned with test scope**
- Use existing `BDDIncrementalCommand._calculate_sample_size()` to identify test scope
- Implement code for the same ~18 tests that were just implemented
- Allow user to specify scope or system chooses tests needing code
- Multiple iterations until all tests pass

**Scope Selection Strategy:**
1. **System-Chosen Scope** (default):
   - Find tests that are failing (production code doesn't exist or is incomplete)
   - Implement code for ~18 tests per iteration
   - Run tests to verify they pass
2. **User-Specified Scope**:
   - User specifies which tests need code
   - Implement code for that scope only
   - Respect user's scope choice

### 4. Validation Should Check Test Passage and Minimalism

**Analysis:**
- Tests are **critical input** for code implementation
- Code implementation must make tests pass without over-engineering
- Validation should verify:
  - Tests pass after code implementation
  - Code is minimal (no extra features beyond what tests demand)
  - No regressions in existing tests
  - Clean code principles followed

**Decision:** ✅ **Validation must check test passage and code minimalism**
- Primary validation: Tests pass (run tests and verify)
- Secondary validation: Code minimalism (no extra features)
- Tertiary validation: Clean code principles
- Check for regressions in other tests

## Analysis Results - Questions Resolved

### Question 1: Should code implementation guidance be added to base rule or specializing rules?

**Analysis:**
- Code implementation **principles** are **framework-agnostic** (minimalism, make tests pass, no extra features)
- Code implementation **examples** are **framework-specific** (Python class syntax vs JavaScript module syntax)
- Currently no code implementation guidance exists in rules (needs to be added)

**Decision:** ✅ **Add Code Implementation Principles to Base Rule, Examples to Specializing Rules**

**Rationale:**
- Code implementation **principles** are **framework-agnostic** (minimalism, test-driven, simplicity)
- Code implementation **examples** are **framework-specific** (Python syntax vs JavaScript syntax)
- Add new section to `bdd-rule.mdc` with framework-agnostic code implementation principles
- Add examples to specializing rules showing framework-specific syntax
- Framework-specific details (syntax, module patterns) belong in framework-specific rules

### Question 2: Code Already Exists - Command Infrastructure Analysis

**Analysis:**
- `BDDWorkflow` class (lines 1029-1102) **FULLY IMPLEMENTED** - includes Phase 3 (Write Code - ALREADY RENAMED)
- `_create_phase_command()` creates Phase 3 with full wrapping chain
- `BDDIncrementalCommand` calculates sample size from test structure
- `_get_code_instructions()` already exists (ALREADY RENAMED from `_get_green_instructions()`)
- CLI handler exists: `bdd_workflow()` function and workflow command handler

**Decision:** ✅ **MINIMAL NEW CODE NEEDED** - Add code implementation section to rules and create command files
- We only need to:
  1. Add code implementation section to base rule (`bdd-rule.mdc` Section 9)
  2. Add code implementation examples to specializing rules (Section 8)
  3. Create command files (`bdd-code-cmd.md` and delegates)
  4. Verify no GREEN references remain in codebase
  5. Both standalone and workflow routes use the same BDDWorkflow Phase 3 infrastructure

### Question 3: Incremental Scope Selection

**Analysis:**
- `BDDIncrementalCommand._calculate_sample_size()` works on test files (finds tests)
- For code implementation, we implement code for failing tests
- Code implementation aligns with test scope (~18 tests per iteration)

**Decision:** ✅ **Incremental code implementation aligned with test scope**
- Implement code for tests that were just implemented (same scope as Phase 2)
- Target code for ~18 tests per iteration
- Allow user to specify scope or system chooses failing tests
- Multiple iterations until all tests pass

### Question 4: Validation Should Verify Tests Pass

**Analysis:**
- Tests are **critical input** for code implementation
- Code must make tests pass
- Validation should verify:
  - Tests pass after code implementation
  - Code is minimal (follows YAGNI - You Aren't Gonna Need It)
  - No regressions
  - Clean code principles

**Decision:** ✅ **Validation must run tests and verify they pass**
- Primary validation: Run tests and verify they pass
- Secondary validation: Code minimalism (no extra features)
- Tertiary validation: Clean code principles
- Check for regressions

## Implementation Plan

### Phase 1: Add Code Implementation Section to Base Rule and Examples to Specializing Rules

**Files:** 
- `behaviors/bdd/bdd-rule.mdc` (framework-agnostic principles)
- `behaviors/bdd/bdd-mamba-rule.mdc` (Python/Mamba examples)
- `behaviors/bdd/bdd-jest-rule.mdc` (JavaScript/Jest examples)

**Integration Strategy:**

**Step 1: Add Code Implementation Principles to Base Rule**

Add a new section to `bdd-rule.mdc` with framework-agnostic code implementation principles:

**Content to Add to `bdd-rule.mdc`:**

```markdown
## 9. Code Implementation Phase

When implementing production code from tests (Phase 3: Write Code), write minimal code to make tests pass:

### 9.1 Minimal Implementation

Implement only what tests demand:
- **DO**: Write simplest code that makes tests pass
- **DON'T**: Add features, abstractions, or complexity not required by tests
- Follow YAGNI (You Aren't Gonna Need It) principle
- If you think "I might need this later" - you don't, the tests will tell you when you do

The tests define the requirements. If there's no test for it, don't implement it.

### 9.2 Make Tests Pass

Focus on making failing tests pass:
- Run tests to identify what's failing
- Implement minimal code to fix failures
- Verify tests pass after implementation
- Don't add extra functionality beyond what tests verify

### 9.3 Avoid Over-Engineering

Keep it simple:
- **DO**: Use simplest data structures and algorithms that work
- **DON'T**: Create elaborate class hierarchies or abstractions prematurely
- Start with simple solutions (e.g., dictionary before custom class)
- Refactor later if tests demand more complexity

Premature abstraction is harder to change than simple code. Let tests drive when complexity is needed.

### 9.4 Check for Regressions

Ensure existing tests still pass:
- Run all tests, not just the new ones
- Verify no regressions introduced
- If regressions occur, fix them before proceeding
- Maintain backwards compatibility

### 9.5 Incremental Implementation

Work in small batches aligned with test scope:
- Implement code for ~18 tests per iteration (matching test implementation scope)
- Verify tests pass after each batch
- Continue until all tests pass
- Keep changes focused and manageable

**Framework-specific examples:** See specializing rules (`bdd-mamba-rule.mdc`, `bdd-jest-rule.mdc`) for concrete syntax examples showing how to implement production code in your chosen framework.
```

**Step 2: Add Code Implementation Examples to Specializing Rules**

Add framework-specific examples to each specializing rule file:

**Code Implementation Examples to Add (Framework-Specific):**

**For `bdd-mamba-rule.mdc` (Python/Mamba):**

```markdown
## 8. Code Implementation Phase Examples

When implementing production code from tests (Phase 3: Write Code), follow base rule § 9 principles with Python-specific syntax:

**[DO]:**
* Implement minimal Python code to make tests pass
* Use simple data structures (dict, list) before creating classes
* Follow Python conventions (PEP 8)
* Return what tests expect, nothing more

```python
# Test expects:
with it("should create user with valid email"):
    user = create_user({"email": "test@example.com", "name": "Test"})
    expect(user.email).to(equal("test@example.com"))
    expect(user.is_active).to(be_true)

# Minimal implementation:
def create_user(user_data):
    """Create user with validated data"""
    email = user_data.get("email")
    if not email or "@" not in email:
        raise ValueError("Invalid email format")
    
    return {
        "email": email,
        "name": user_data.get("name"),
        "role": user_data.get("role", "user"),
        "is_active": True
    }
```

**[DON'T]:**
* Add features not tested
* Create complex class hierarchies prematurely
* Add configuration or options not tested

```python
# DON'T: Over-engineered with untested features
class User:
    def __init__(self, email, name, role="user", permissions=None, preferences=None):
        self.email = email
        self.name = name
        self.role = role
        self.permissions = permissions or []  # Not tested
        self.preferences = preferences or {}  # Not tested
        self.created_at = datetime.now()      # Not tested
```
```

**For `bdd-jest-rule.mdc` (JavaScript/Jest):**

```markdown
## 8. Code Implementation Phase Examples

When implementing production code from tests (Phase 3: Write Code), follow base rule § 9 principles with JavaScript-specific syntax:

**[DO]:**
* Implement minimal JavaScript code to make tests pass
* Use simple objects before creating classes
* Follow JavaScript conventions (ES6+)
* Return what tests expect, nothing more

```javascript
// Test expects:
it("should create user with valid email", () => {
  const user = createUser({ email: "test@example.com", name: "Test" });
  expect(user.email).toBe("test@example.com");
  expect(user.isActive).toBe(true);
});

// Minimal implementation:
function createUser(userData) {
  const { email, name, role = "user" } = userData;
  
  if (!email || !email.includes("@")) {
    throw new Error("Invalid email format");
  }
  
  return {
    email,
    name,
    role,
    isActive: true
  };
}
```

**[DON'T]:**
* Add features not tested
* Create complex class structures prematurely
* Add configuration or options not tested

```javascript
// DON'T: Over-engineered with untested features
class User {
  constructor(email, name, role = "user", permissions = [], preferences = {}) {
    this.email = email;
    this.name = name;
    this.role = role;
    this.permissions = permissions;  // Not tested
    this.preferences = preferences;  // Not tested
    this.createdAt = new Date();     // Not tested
  }
}
```
```

**Step 3: Update Commands Section in Base Rule and Specializing Rules**

Update "Executing Commands" section in `bdd-rule.mdc`:
```markdown
**Executing Commands:**
* `/bdd-validate` — Validate BDD test files against these principles
* `/bdd-workflow` — Execute BDD workflow phases (Domain Scaffold, Signatures, Write Tests, Write Code)
* `/bdd-scaffold` — Generate domain scaffolding (plain English hierarchy) from domain maps
* `/bdd-signature` — Generate test signatures (code structure) from scaffolds
* `/bdd-test` — Implement test code from signatures
* `/bdd-code` — Implement production code to make tests pass **NEW**
```

Update "Executing Commands" section in both `bdd-mamba-rule.mdc` and `bdd-jest-rule.mdc`:
```markdown
**Executing Commands:**
* `/bdd-validate` — Validate BDD test files against these principles
* `/bdd-workflow` — Execute BDD workflow phases (Domain Scaffold, Signatures, Write Tests, Write Code)
* `/bdd-scaffold` — Generate domain scaffolding (plain English hierarchy) from domain maps
* `/bdd-signature` — Generate test signatures (code structure) from scaffolds
* `/bdd-test` — Implement test code from signatures
* `/bdd-code` — Implement production code to make tests pass **NEW**
```

### Phase 2: Create Command Files

**Phase-Specific Command Files (bdd-code):**
- `behaviors/bdd/code/bdd-code-cmd.md` - Main phase-specific command file
- `behaviors/bdd/code/bdd-code-generate-cmd.md` - Generate delegate (delegates to main command generate action)
- `behaviors/bdd/code/bdd-code-validate-cmd.md` - Validate delegate (delegates to main command validate action)

**Action:** Use `/code-agent-command` to generate:
- Feature: `bdd`
- Command: `bdd-code`
- Purpose: Implement production code to make tests pass following BDD principles
- Target Entity: Production code files (e.g., `user_management.py`)

**Command Structure Requirements:**
- **Purpose**: Implement minimal production code to make tests pass
- **Base Rule**: Reference `bdd-rule.mdc`:
  - Section 9 (Code Implementation Phase) - framework-agnostic code implementation principles **NEW**
- **Specializing Rule**: Reference `bdd-mamba-rule.mdc` (or `bdd-jest-rule.mdc`):
  - Section 8: Code Implementation Phase Examples - framework-specific syntax examples
- **Runner**: `behaviors/bdd/bdd-runner.py` (uses existing `BDDWorkflow` Phase 3 infrastructure)
- **Actions**: Standard 4-action pattern (Generate → User Feedback → Validate → User Feedback)

**Key Features in Command Files:**
1. **Test Discovery**: Find failing tests (tests calling non-existent production code)
2. **Incremental Code Implementation**: 
   - Implement code for ~18 tests per iteration (aligned with test implementation scope)
   - Allow user to specify scope or system chooses failing tests
3. **Rule Focus**: Emphasize rules in prompts:
   - `bdd-rule.mdc` Section 9: Code implementation principles (minimalism, YAGNI)
   - `bdd-mamba-rule.mdc` Section 8: Framework-specific code implementation examples (syntax)

### Phase 3: Configure Command Integration

**No New Runner Code Needed** - The infrastructure already exists and was already updated!

**Existing Infrastructure (ALREADY UPDATED):**
- `BDDWorkflow` class - Creates Phase 3 "Write Code" (already renamed)
- `BDDWorkflow._create_phase_command()` - Creates Phase 3 with full wrapping chain
- `BDDWorkflowPhaseCommand` - Wraps WorkflowPhaseCommand
- `BDDIncrementalCommand` - Handles incremental work
- `_get_code_instructions()` - Has code instructions (ALREADY RENAMED and UPDATED)
- `bdd_workflow()` function - CLI entry point

**Command Files Should:**
- Reference existing `BDDWorkflow` Phase 3 infrastructure
- Use existing `BDDIncrementalCommand` pattern for incremental work
- Reference `bdd-rule.mdc` Section 9 (base principles)
- Reference `bdd-mamba-rule.mdc` Section 8 (framework-specific examples)
- Focus on base rule § 9 for principles, specializing rule § 8 for syntax

### Phase 4: Incremental Code Implementation

**Current State:**
- `BDDIncrementalCommand` infrastructure exists and is fully functional
- Code implementation benefits from incremental approach (code for ~18 tests per iteration)

**Decision:**
- Implement code for the same test scope (~18 tests)
- Run tests after each implementation batch
- Allow user to specify scope or system chooses failing tests
- Multiple iterations until all tests pass

### Phase 5: Validation Configuration

**Validation Requirements:**
1. **Primary Check**: Tests pass
   - Run tests and verify they pass
   - All previously failing tests now pass
   - Clear error messages if tests still fail

2. **Secondary Check**: Code minimalism
   - No extra features beyond what tests demand
   - Simple data structures and algorithms
   - No premature abstractions

3. **Tertiary Check**: Clean code principles
   - Readable, maintainable code
   - Proper naming conventions
   - No code duplication

4. **Regression Check**: Existing tests still pass
   - Run all tests, not just new ones
   - Verify no regressions introduced

## Files to Create/Modify

### New Files:
- `behaviors/bdd/code/bdd-code-cmd.md`
- `behaviors/bdd/code/bdd-code-generate-cmd.md`
- `behaviors/bdd/code/bdd-code-validate-cmd.md`

### Modified Files:
- `behaviors/bdd/bdd-rule.mdc` - Add code implementation principles:
  - Add new Section 9: Code Implementation Phase (framework-agnostic principles)
  - Update Commands section with code command references (ALREADY PARTIALLY DONE)
- `behaviors/bdd/bdd-mamba-rule.mdc` - Add code implementation examples:
  - Add new Section 8: Code Implementation Phase Examples (Python syntax)
  - Update Commands section with code command references
- `behaviors/bdd/bdd-jest-rule.mdc` - Add code implementation examples:
  - Add new Section 8: Code Implementation Phase Examples (JavaScript syntax)
  - Update Commands section with code command references

### Code Changes Needed:
- `behaviors/bdd/bdd-runner.py` - Verify GREEN removal (mostly done):
  - **VERIFY**: No remaining "GREEN" references in code
  - **ALREADY DONE**: `_get_green_instructions()` → `_get_code_instructions()`
  - **ALREADY DONE**: Phase 3 name "GREEN - Make Tests Pass" → "Write Code"
  - **ALREADY DONE**: BDDPhase.GREEN → BDDPhase.CODE

## Implementation Steps (Following BDD TDD Workflow)

### Phase 0: Domain Scaffold (Analysis & Planning)
1. ✅ **Add Code Implementation to Base Rule and Examples to Specializing Rules**: 
   - Add Section 9 to `bdd-rule.mdc` (framework-agnostic code implementation principles)
   - Add Section 8 to `bdd-mamba-rule.mdc` (Python framework-specific examples)
   - Add Section 8 to `bdd-jest-rule.mdc` (JavaScript framework-specific examples)
   - Principles: Minimalism, YAGNI, make tests pass, no over-engineering, check regressions
   - Update Commands section in base rule and both specializing rules with code command references

### Phase 1: Signature (Test Structure)
2. **Verify Existing Tests**: Check if existing `bdd_runner_test.py` covers code implementation validation

### Phase 2: RED/Write Tests (if needed)
3. **Implement Tests** (if new validation needed): Write tests for code implementation validation

### Phase 3: GREEN/Write Code (Make Tests Pass)
4. **Verify GREEN Removal**: Ensure all GREEN terminology removed from codebase
5. **Create Command Files**: Use `/code-agent-command` to generate code command files
6. **Configure Command Files**: Reference `bdd-rule.mdc` Section 9 and specializing rule Section 8

### Phase 4: REFACTOR (Improve Code Quality)
7. **Refactor**: Run validation commands and fix violations

### Phase 5: Integration & CLI Testing
8. **Update Indexes**: Run index generation to include new command files
9. **CLI Testing**: Test command:
    - Use test file with failing tests
    - Run `/bdd-code` command
    - Verify production code generated
    - Verify tests pass
    - Run `/bdd-code-validate` command

## Success Criteria ✅

- ✅ Command generates production code to make tests pass following minimalism principles
- ✅ Generates code incrementally aligned with test scope
- ✅ Integrates with existing workflow infrastructure (Phase 3)
- ✅ References templates instead of duplicating content
- ✅ Validates that tests pass and code is minimal
- ✅ Works both standalone (`/bdd-code`) and within workflow (`/bdd-workflow`)
- ✅ No over-engineering - only implements what tests demand
- ✅ CLI testing successful with failing test file

## Key Insights

1. **GREEN Already Renamed**: Phase 3 already renamed to "Write Code" and `_get_code_instructions()` already exists
2. **Method Already Renamed**: `_get_green_instructions()` → `_get_code_instructions()` already done
3. **Phase Already Renamed**: "GREEN - Make Tests Pass" → "Write Code" already done
4. **Base Rule for Principles**: Code implementation **principles** go in base rule (framework-agnostic)
5. **Specializing Rules for Examples**: Code implementation **examples** go in specializing rules (framework-specific syntax)
6. **Minimalism Focus**: YAGNI principle - only implement what tests demand
7. **Test-Driven**: Tests define requirements - no test means no feature
8. **Incremental Approach**: Code for ~18 tests per iteration (aligned with test scope)
9. **Follow Existing Patterns**: Use `BDDIncrementalCommand` pattern for incremental work
10. **Template References**: Command files should reference rule templates, not duplicate content
11. **Phase 3 Infrastructure Exists**: Workflow Phase 3 fully implemented and already updated
12. **Validation Runs Tests**: Primary validation is running tests and verifying they pass
13. **Base Rule Stays Framework-Agnostic**: Keep base `bdd-rule.mdc` focused on framework-agnostic principles
14. **Most Work Already Done**: Phase 3 already updated in earlier refactoring, just need rules and commands

## Implementation Status

**Status:** READY FOR IMPLEMENTATION

**Next Steps:**
1. **Verify GREEN Removal**: Search for any remaining "GREEN" references in codebase
2. **Add Section 9 to Base Rule**: Add code implementation principles to `bdd-rule.mdc` (framework-agnostic)
3. **Add Section 8 to Specializing Rules**: 
   - Add code implementation examples to `bdd-mamba-rule.mdc` (Python syntax)
   - Add code implementation examples to `bdd-jest-rule.mdc` (JavaScript syntax)
4. **Update Commands Sections**: Update in base rule and both specializing rules
5. Create command files using `/code-agent-command`
6. Configure command files with rule references (base rule § 9 + specializing rule § 8)
7. Update indexes
8. CLI testing with failing test file

