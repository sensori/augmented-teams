# Test Implementation Plan: Refactored Domain Classes

## Overview
This document outlines the implementation plan for adding/updating tests based on the refactored domain classes documented in `story ap reverse.md`.

## Files to Update

### 1. `test_invoke_cli.py` - ADD Stories 1-2 (TriggerWords)
**Current Status:** Has `TestDetectTriggerWordsThroughExtension` but missing domain class tests
**Action:** Add `TestGetTriggerPriority` and `TestMatchTextAgainstTriggers` classes
**Source:** Merge from `test_trigger_words.py` (then delete that file)

### 2. `test_invoke_mcp.py` - ADD Stories 3-5 (Instructions)
**Current Status:** Needs domain class tests
**Action:** Add `TestGetBaseInstructions`, `TestGetBehaviorInstructions`, `TestMergeInstructions` classes
**Source:** Merge from `test_instructions.py` (then delete that file)

### 3. `test_perform_behavior_action.py` - ADD Stories 6, 21-24
**Current Status:** Has workflow/action execution tests but missing domain class tests
**Action:** Add:
- `TestGetBaseInstructions` (Story 6 - MergedInstructions base_instructions)
- `TestLoadBehaviorConfig` (Story 21)
- `TestManageBehaviorsCollection` (Story 22)
- `TestLoadBotConfiguration` (Story 23)
- `TestResolveBotPaths` (Story 24)

### 4. `test_render_output.py` - ADD Stories 7-8 (MergedInstructions render)
**Current Status:** Has render output action tests but missing domain class tests
**Action:** Add:
- `TestGetRenderInstructions` (Story 7)
- `TestMergeBaseAndRenderInstructions` (Story 8)
**Source:** Merge relevant parts from `test_merged_instructions.py` (then delete that file)

### 5. `test_validate_knowledge_and_content_against_rules.py` - ADD Stories 9-16
**Current Status:** Has validation action tests but missing domain class tests
**Action:** Add:
- `TestLoadRulesCollection` (Story 9)
- `TestFindRuleByName` (Story 10)
- `TestIterateRules` (Story 11)
- `TestLoadRuleFromFile` (Story 12)
- `TestLoadScannerForRule` (Story 13)
- `TestGetRuleProperties` (Story 14)
- `TestCreateValidationScope` (Story 15)
- `TestLoadScannerClass` (Story 16)

### 6. `test_gather_context.py` - ADD Stories 17-20
**Current Status:** Has gather context action tests but missing domain class tests
**Action:** Add:
- `TestLoadBaseActionConfig` (Story 17)
- `TestAccessActions` (Story 18 - renamed from ManageActionsCollection)
- `TestInitializeAction` (Story 19)
- `TestLoadGuardrails` (Story 20)

## Files to DELETE (Obsolete)

These files contain domain class tests that should be merged into the main test files:

1. **`test_trigger_words.py`** - Merge into `test_invoke_cli.py`
   - Contains: `TestMatchTriggerPattern`, `TestGetTriggerPriority`, `TestMatchTextAgainstTriggers`
   - Action: Move test classes to `test_invoke_cli.py`, delete file

2. **`test_instructions.py`** - Merge into `test_invoke_mcp.py`
   - Contains: Instructions domain class tests
   - Action: Move test classes to `test_invoke_mcp.py`, delete file

3. **`test_merged_instructions.py`** - Split and merge
   - Contains: MergedInstructions domain class tests
   - Action: 
     - Move base_instructions tests to `test_perform_behavior_action.py` (Story 6)
     - Move render_instructions and merge tests to `test_render_output.py` (Stories 7-8)
     - Delete file

## Implementation Notes

1. **Test Structure:** Each story = one test class, each scenario = one test method
2. **Helper Functions:** Use `given_`, `when_`, `then_` prefixes per testing rules
3. **Examples Tables:** Use pytest.mark.parametrize for scenarios with examples tables
4. **Consolidation:** Many property tests have been consolidated - follow the simplified scenarios in `story ap reverse.md`
5. **File Organization:** Tests are organized by epic/sub-epic, not by domain class

## Priority Order

1. **High Priority:** Stories 1-2, 3-5 (domain classes used by actions)
2. **Medium Priority:** Stories 6-8, 21-24 (core domain objects)
3. **Lower Priority:** Stories 9-20 (supporting domain objects)

## Next Steps

1. Add test classes to each file following the story document
2. Merge helpers from obsolete files
3. Update existing tests that test the same functionality
4. Delete obsolete test files
5. Run tests to verify everything works

