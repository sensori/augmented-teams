# Obsolete Test Files to Delete

## Summary
These test files contain domain class tests that have been merged into the main test files organized by sub-epic. After verifying all tests pass, these files should be deleted.

## Files Deleted ✅

### 1. `test_trigger_words.py` ✅ DELETED
**Status:** Tests merged into `test_invoke_cli.py`
**Deleted:** All tests verified passing in `test_invoke_cli.py`

### 2. `test_instructions.py` ✅ DELETED
**Status:** Tests merged into `test_invoke_mcp.py`
**Deleted:** All tests verified passing in `test_invoke_mcp.py`

### 3. `test_merged_instructions.py` ✅ DELETED
**Status:** Tests split and merged
**Deleted:** 
- Base instructions tests merged into `test_perform_behavior_action.py` (Story 6)
- Render instructions and merge tests merged into `test_render_output.py` (Stories 7-8)
- All tests verified passing in new locations

## Verification Steps

Before deleting files:
1. Run all tests: `pytest agile_bot/bots/base_bot/test/`
2. Verify no test failures
3. Verify test coverage is maintained
4. Delete obsolete files

## Legacy Code Still Present (Needs Refactoring)

### `rules.py` - `iterate()` method
**Status:** Marked as legacy but still in use
**Usage:** Called in 4 places:
- `validate_rules_action.py` (2 places)
- `behavior.py` (1 place)
- `bot.py` (1 place)

**Action:** Refactor callers to use `__iter__` instead, then remove `iterate()` method

### `validate_rules_action.py` - Backward compatibility code
**Status:** Still converting Rule objects to legacy dict format
**Action:** According to refactor plan: "Eliminate all old code so that we are only using the new code. Everything will be a fix forward."
**Note:** Need to verify no external callers depend on legacy format before removing

