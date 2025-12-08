# Never Delete Tests Without Explicit Permission

## CRITICAL RULE

**DO NOT REMOVE OR DELETE TEST CODE WITHOUT EXPLICIT USER PERMISSION**

You tend to remove entire tests instead of modifying them to meet new requirements. **STOP DOING THAT.**

## Pattern

### ❌ WRONG: Deleting Tests
```python
# You see test that doesn't match new requirements
def test_old_behavior():
    # ... existing test code ...
    assert old_way_works()

# Your instinct: DELETE THE TEST
# ❌ DO NOT DO THIS
```

### ✅ CORRECT: Modify Tests
```python
# Instead: UPDATE the test to match new requirements
def test_old_behavior():  # Keep same test, update assertions
    # ... modify test code to match new implementation ...
    assert new_way_works()
```

## Rules

### 1. Never Delete Test Code
- **DO NOT** delete entire test functions
- **DO NOT** delete entire test classes
- **DO NOT** delete test files
- **DO NOT** comment out tests

### 2. Always Modify Tests to Match New Requirements
- **UPDATE** test setup to match new structure
- **UPDATE** assertions to match new behavior
- **UPDATE** test data to match new format
- **KEEP** the test coverage - just adapt it

### 3. Only Delete With Explicit Permission
If test is truly obsolete:
- **ASK USER:** "This test appears obsolete because [reason]. Should I delete it or update it?"
- **WAIT** for user to explicitly say "delete it" or "remove it"
- **NEVER** assume you can delete

### 4. Add Tests, Don't Replace
When adding new functionality:
- **ADD** new tests for new behavior
- **KEEP** existing tests (update if needed)
- **DO NOT** replace old tests with new tests

## Examples

### Scenario: Refactoring to Template Method

**❌ WRONG Approach:**
```python
# Old test
def test_gather_context_saves_state():
    result = behavior.gather_context()
    assert result.status == 'completed'

# You refactor code to use template method
# Your instinct: DELETE old test, write new one
# ❌ DO NOT DO THIS
```

**✅ CORRECT Approach:**
```python
# Keep same test, update if needed
def test_gather_context_saves_state():
    result = behavior.gather_context()
    # Test still works! Template method doesn't change behavior
    assert result.status == 'completed'
    # Maybe add new assertions for template behavior
    assert workflow_state_was_saved()
```

---

### Scenario: Changing Function Signature

**❌ WRONG Approach:**
```python
# Old test
def test_execute_action_with_logic_function():
    result = execute_action('test', logic_fn, params)
    assert result.data == expected

# You change signature: execute_action(name, action_class, params)
# Your instinct: DELETE this test (signature changed)
# ❌ DO NOT DO THIS
```

**✅ CORRECT Approach:**
```python
# Update test to match new signature
def test_execute_action_with_action_class():  # Rename if needed
    result = execute_action('test', TestActionClass, params)
    assert result.data == expected
```

---

### Scenario: Test Becomes Obsolete

**❌ WRONG Approach:**
```python
# Old test for feature that was removed
def test_old_feature_that_no_longer_exists():
    # ... test code ...

# Your instinct: DELETE it (feature gone)
# ❌ DO NOT DO THIS WITHOUT ASKING
```

**✅ CORRECT Approach:**
**ASK USER FIRST:**
```
"I see test_old_feature_that_no_longer_exists tests functionality that was 
removed in the refactor. Should I:
1. Delete this test (feature no longer exists)
2. Update it to test the new equivalent feature
3. Keep it as-is

What would you like me to do?"
```

## When It's OK to Delete (Still Ask First)

Even in these cases, **ASK before deleting:**

1. **Duplicate tests** - "These two tests appear identical. Should I remove the duplicate?"
2. **Obsolete tests** - "This tests feature X which was removed. Should I delete it?"
3. **Broken tests** - "This test fails and seems outdated. Should I fix or remove it?"

## Summary

**NEVER delete tests on your own initiative.**

- Default: **MODIFY** tests to match new requirements
- If truly obsolete: **ASK USER** before deleting
- When refactoring: **UPDATE** tests, don't replace them
- When adding features: **ADD** tests, don't delete old ones

**User must explicitly say "delete that test" or "remove it" before you delete test code.**
























