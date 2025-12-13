# Code Quality Scanners Inventory

## Summary

**Total Rules with Scanners:** 30  
**CodeScanner instances:** ~27 (scan code files, need `code_files` parameter)  
**TestScanner instances:** ~3 (scan test files, need `test_files` parameter)

## CodeScanner Instances (Code Quality Scanners)

These scanners scan source code files and require `code_files` parameter:

1. **IntentionRevealingNamesScanner** - `use_intention_revealing_names.json`
2. **ExplicitDependenciesScanner** - `use_explicit_dependencies.json`
3. **ExceptionHandlingScanner** - `use_exceptions_properly.json`
4. **ConsistentNamingScanner** - `use_consistent_naming.json`
5. **ConsistentIndentationScanner** - `use_consistent_indentation.json`
6. **ClearParametersScanner** - `use_clear_function_parameters.json`
7. **UselessCommentsScanner** - `stop_writing_useless_comments.json`, `prefer_code_over_comments.json`
8. **SeparateConcernsScanner** - `separate_concerns.json`
9. **SimplifyControlFlowScanner** - `simplify_control_flow.json`
10. **CompleteRefactoringScanner** - `refactor_completely_not_partially.json`
11. **BadCommentsScanner** - `remove_bad_comments.json`
12. **MeaningfulContextScanner** - `provide_meaningful_context.json`
13. **MinimizeMutableStateScanner** - `minimize_mutable_state.json`
14. **SwallowedExceptionsScanner** - `never_swallow_exceptions.json`
15. **VerticalDensityScanner** - `maintain_vertical_density.json`
16. **AbstractionLevelsScanner** - `maintain_abstraction_levels.json`
17. **FunctionSizeScanner** - `keep_functions_small_focused.json`
18. **SingleResponsibilityScanner** - `keep_functions_single_responsibility.json`, `keep_classes_single_responsibility.json`
19. **ClassSizeScanner** - `keep_classes_small_compact.json`
20. **ThirdPartyIsolationScanner** - `isolate_third_party_code.json`
21. **ErrorHandlingIsolationScanner** - `isolate_error_handling.json`
22. **EncapsulationScanner** - `enforce_encapsulation.json`
23. **OpenClosedPrincipleScanner** - `follow_open_closed_principle.json`
24. **DuplicationScanner** - `eliminate_duplication.json`
25. **ExceptionClassificationScanner** - `classify_exceptions_by_caller_needs.json`

## TestScanner Instances (Test-Specific Scanners)

These scanners scan test files and require `test_files` parameter:

1. **TestQualityScanner** - `maintain_test_quality.json`
2. **OneConceptPerTestScanner** - `test_one_concept_per_test.json`
3. **TestBoundaryBehaviorScanner** - `test_boundary_behavior.json`

## Why Only Test Scanners Ran Initially

**First validation run:** Only passed `test_files` parameter, which means:
- ✅ TestScanner instances ran (TestQualityScanner, OneConceptPerTestScanner)
- ❌ CodeScanner instances did NOT run (all 25+ code quality scanners)
- **Result:** Only 7 violations found (2 errors, 5 warnings)

**Second validation run:** Passed BOTH `test_files` AND `code_files` parameters:
- ✅ TestScanner instances ran (TestQualityScanner, OneConceptPerTestScanner, TestBoundaryBehaviorScanner)
- ✅ CodeScanner instances ran (all 25+ code quality scanners)
- **Result:** **Hundreds of violations found** - all code quality rules now applied to test code!

## Solution

To validate test code with ALL scanners, pass test files as BOTH:
- `test_files` - for TestScanner instances (test-specific rules)
- `code_files` - for CodeScanner instances (general code quality rules)

This allows code quality scanners to also analyze the test code for:
- Function size (132 violations found!)
- Intention-revealing names (214 violations found!)
- Meaningful context (107 violations found!)
- Vertical density (37 violations found!)
- Abstraction levels (18 violations found!)
- And all other code quality rules

## Validation Results Summary

**With test_files only:** 7 violations  
**With test_files + code_files:** Hundreds of violations across all code quality rules

This demonstrates that test code should be validated against BOTH test-specific rules AND general code quality rules!

