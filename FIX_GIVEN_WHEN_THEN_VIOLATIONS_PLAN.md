# Plan to Fix Remaining Given/When/Then Helper Violations

## Overview
- **Total Violations:** ~254 (248 file-by-file + 6 cross-file)
- **Fixed So Far:** ~20 violations
- **Remaining:** ~234 violations
- **Strategy:** Focus on actual inline code violations, ignore docstring-only violations

## Completed ✅
1. **Cross-file violations (6)**: Consolidated duplicate helpers into `conftest.py`
2. **test_build_knowledge.py**: Extracted inline steps into helpers
3. **test_validate_knowledge_and_content_against_rules.py**: Started extracting inline assertions

## Remaining Work Plan

### Phase 1: High-Impact Files (Most Violations)
**Priority: HIGH** - These files have the most violations and will have biggest impact

#### 1.1 test_validate_knowledge_and_content_against_rules.py (~157 violations)
**Status:** Partially fixed (8+ violations fixed, ~149 remaining)

**Patterns to Extract:**
- Multiple consecutive assertions → Extract into `then_*` helpers
- Variable assignments + assertions → Extract into `given_*` or `when_*` helpers  
- Multi-line setup blocks → Extract into `given_*` helpers
- Complex validation blocks → Extract into `then_*` helpers

**Approach:**
1. Scan file for blocks of 2+ consecutive lines that are:
   - Assertions
   - Variable assignments + usage
   - Setup code
2. Group similar patterns together
3. Create helper functions following Given/When/Then naming
4. Replace inline code with helper calls

**Estimated Time:** 4-6 hours

#### 1.2 test_generate_bot_server_and_tools.py (~30+ violations)
**Patterns:**
- Multi-line scenario docstrings (IGNORE - docstrings)
- Setup blocks with multiple steps
- Assertion chains

**Approach:**
- Extract setup blocks into `given_*` helpers
- Extract assertion chains into `then_*` helpers
- Skip docstring violations

**Estimated Time:** 2-3 hours

#### 1.3 test_gather_context.py (~15+ violations)
**Patterns:**
- Activity tracking setup
- Clarification data setup
- Multi-step assertions

**Approach:**
- Extract activity log setup
- Extract clarification JSON setup
- Extract assertion chains

**Estimated Time:** 1-2 hours

### Phase 2: Medium-Impact Files
**Priority: MEDIUM** - Moderate number of violations

#### 2.1 test_decide_planning_criteria.py (~10+ violations)
**Patterns:**
- Planning data setup
- Multi-line function calls
- Assertion chains

**Estimated Time:** 1 hour

#### 2.2 test_complete_workflow_integration.py (~5+ violations)
**Patterns:**
- Workflow setup blocks
- Flow descriptions (IGNORE if docstrings)

**Estimated Time:** 30 minutes

#### 2.3 test_workflow_action_sequence.py (~10+ violations)
**Patterns:**
- Workflow state setup
- Transition assertions

**Estimated Time:** 1 hour

### Phase 3: Low-Impact Files
**Priority: LOW** - Few violations, quick wins

#### 3.1 test_base_action.py (~3 violations - all docstrings, SKIP)
**Status:** All violations are docstrings - IGNORE per user instruction

#### 3.2 Other scattered files (~10-15 violations total)
**Files:**
- test_close_current_action.py
- test_invoke_bot_cli.py  
- test_invoke_bot_tool.py
- test_render_output.py
- Other test files

**Approach:**
- Quick scan for actual code violations
- Extract inline blocks
- Skip docstrings

**Estimated Time:** 1-2 hours

## Extraction Patterns

### Pattern 1: Multiple Assertions
**Before:**
```python
assert 'key1' in result
assert 'key2' in result
value = result['key1']
assert value > 0
```

**After:**
```python
value = then_result_has_keys_and_value(result, 'key1', 'key2')
```

### Pattern 2: Setup + Assertion
**Before:**
```python
data = {'key': 'value'}
file.write(json.dumps(data))
assert file.exists()
```

**After:**
```python
file = given_file_with_data(file, {'key': 'value'})
then_file_exists(file)
```

### Pattern 3: Variable Assignment Chain
**Before:**
```python
result = action.execute()
instructions = result['instructions']
base = instructions['base']
```

**After:**
```python
base = when_action_executes_then_extract_base_instructions(action)
```

## Implementation Strategy

### Step 1: Identify Violation Types
For each file:
1. Read violation report entries
2. Check if violation is:
   - **Docstring only** → SKIP
   - **Actual code** → FIX
3. Group similar violations together

### Step 2: Create Helper Functions
1. Name helpers following Given/When/Then pattern:
   - `given_*` - Setup/arrange
   - `when_*` - Action/execution  
   - `then_*` - Assertion/verification
2. Place helpers in appropriate section:
   - File-specific → Top of file in helper section
   - Shared across files → `conftest.py` or `test_helpers.py`

### Step 3: Replace Inline Code
1. Replace inline blocks with helper calls
2. Ensure helper returns needed values
3. Maintain test readability

### Step 4: Verify
1. Run tests to ensure no breakage
2. Check linter errors
3. Verify helper functions are used correctly

## File-by-File Checklist

### High Priority
- [ ] test_validate_knowledge_and_content_against_rules.py (~149 remaining)
- [ ] test_generate_bot_server_and_tools.py (~30+)
- [ ] test_gather_context.py (~15+)

### Medium Priority  
- [ ] test_decide_planning_criteria.py (~10+)
- [ ] test_complete_workflow_integration.py (~5+)
- [ ] test_workflow_action_sequence.py (~10+)

### Low Priority
- [ ] test_base_action.py (SKIP - all docstrings)
- [ ] Other scattered files (~10-15)

## Success Criteria
- ✅ All actual code violations extracted into helpers
- ✅ Docstring-only violations ignored
- ✅ Tests still pass
- ✅ Code is more readable and maintainable
- ✅ Helpers follow Given/When/Then naming convention

## Estimated Total Time
- Phase 1: 7-11 hours
- Phase 2: 2.5-3.5 hours  
- Phase 3: 1-2 hours
- **Total: 10.5-16.5 hours**

## Notes
- Focus on actual code, not docstrings
- Prioritize files with most violations
- Reuse helpers where possible
- Maintain test readability
- Verify after each file
