# Code Quality Scanners - Complete Summary

## All Available Scanners

**Total:** 30 rules with scanners

### CodeScanner Instances (27 scanners - scan code files)

These require `code_files` parameter to run:

1. **AbstractionLevelsScanner** - `maintain_abstraction_levels.json`
2. **BadCommentsScanner** - `remove_bad_comments.json`
3. **ClassSizeScanner** - `keep_classes_small_compact.json`
4. **ClearParametersScanner** - `use_clear_function_parameters.json`
5. **CompleteRefactoringScanner** - `refactor_completely_not_partially.json`
6. **ConsistentIndentationScanner** - `use_consistent_indentation.json`
7. **ConsistentNamingScanner** - `use_consistent_naming.json`
8. **DuplicationScanner** - `eliminate_duplication.json`
9. **EncapsulationScanner** - `enforce_encapsulation.json`
10. **ErrorHandlingIsolationScanner** - `isolate_error_handling.json`
11. **ExceptionClassificationScanner** - `classify_exceptions_by_caller_needs.json`
12. **ExceptionHandlingScanner** - `use_exceptions_properly.json`
13. **ExplicitDependenciesScanner** - `use_explicit_dependencies.json`
14. **FunctionSizeScanner** - `keep_functions_small_focused.json`
15. **IntentionRevealingNamesScanner** - `use_intention_revealing_names.json`
16. **MeaningfulContextScanner** - `provide_meaningful_context.json`
17. **MinimizeMutableStateScanner** - `minimize_mutable_state.json`
18. **OpenClosedPrincipleScanner** - `follow_open_closed_principle.json`
19. **SeparateConcernsScanner** - `separate_concerns.json`
20. **SingleResponsibilityScanner** - `keep_functions_single_responsibility.json`, `keep_classes_single_responsibility.json`
21. **SimplifyControlFlowScanner** - `simplify_control_flow.json`
22. **SwallowedExceptionsScanner** - `never_swallow_exceptions.json`
23. **ThirdPartyIsolationScanner** - `isolate_third_party_code.json`
24. **UselessCommentsScanner** - `stop_writing_useless_comments.json`, `prefer_code_over_comments.json`
25. **VerticalDensityScanner** - `maintain_vertical_density.json`

### TestScanner Instances (3 scanners - scan test files)

These require `test_files` parameter to run:

1. **OneConceptPerTestScanner** - `test_one_concept_per_test.json`
2. **TestBoundaryBehaviorScanner** - `test_boundary_behavior.json`
3. **TestQualityScanner** - `maintain_test_quality.json`

## Validation Runs Comparison

### Run 1: test_files only
**Parameters:** `test_files` only  
**Scanners that ran:**
- ✅ TestQualityScanner
- ✅ OneConceptPerTestScanner
- ❌ All 25 CodeScanner instances did NOT run

**Results:** 7 violations found
- 2 errors (false positives)
- 5 warnings

### Run 2: test_files + code_files
**Parameters:** `test_files` AND `code_files`  
**Scanners that ran:**
- ✅ TestQualityScanner
- ✅ OneConceptPerTestScanner  
- ✅ TestBoundaryBehaviorScanner
- ✅ All 25 CodeScanner instances

**Results:** **Hundreds of violations found!**

## Key Findings from Full Validation

When ALL scanners ran, violations were found in these categories:

### Top Violation Categories:
1. **use_intention_revealing_names** - 214 violations (generic names like "result", single letters)
2. **keep_functions_small_focused** - 132 violations (functions > 20 lines)
3. **provide_meaningful_context** - 107 violations (numbered variables, magic numbers)
4. **maintain_vertical_density** - 37 violations (variables declared far from usage)
5. **maintain_abstraction_levels** - 18 violations (mixed abstraction levels)
6. **keep_classes_small_compact** - 8 violations (classes > 300 lines)
7. **simplify_control_flow** - 6 violations (deep nesting)
8. **follow_open_closed_principle** - 6 violations (type-based conditionals)
9. **never_swallow_exceptions** - 3 errors (empty except blocks)
10. **eliminate_duplication** - 1 error (duplicate code)
11. **separate_concerns** - 7 errors (mixing I/O with logic)
12. **remove_bad_comments** - 4 errors (commented-out code)
13. **refactor_completely_not_partially** - 5 warnings (commented code, dual patterns)
14. **test_one_concept_per_test** - 5 warnings (multiple concepts per test)
15. **maintain_test_quality** - 2 errors (global state - false positives)
16. **use_clear_function_parameters** - 7 warnings (too many parameters)
17. **keep_classes_single_responsibility** - 15 warnings (multiple responsibilities)
18. **keep_functions_single_responsibility** - 15 warnings (multiple responsibilities)
19. **minimize_mutable_state** - 2 warnings (state mutation)
20. **enforce_encapsulation** - 1 warning (Law of Demeter)
21. **isolate_third_party_code** - 2 info (direct third-party imports)
22. **classify_exceptions_by_caller_needs** - 2 warnings (component-based exceptions)

## Conclusion

**To validate test code comprehensively, you MUST pass both:**
- `test_files` - for test-specific rules
- `code_files` - for general code quality rules

Test code should be held to the same quality standards as production code!



