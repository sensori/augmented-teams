# BDD Heuristic Scanners - Legacy Code Summary

## Overview
This document summarizes the heuristic scanner implementation found in the legacy BDD runner code. The `common_command_runner.py` file is missing from the repository, but its usage patterns can be inferred from `bdd-runner.py`.

## Main File
- **`agile_bot/legacy_code/bdd_bot/src/bdd-runner.py`** - Contains BDD-specific heuristic implementations

## Missing File
- **`common_command_runner/common_command_runner.py`** - Should contain base classes:
  - `CodeHeuristic` (base class for all heuristics)
  - `CodeAugmentedCommand` (command wrapper that uses heuristics)
  - `Content`, `Command`, `BaseRule`, `Violation`, etc.

## BDD Heuristic Classes

All heuristics extend `CodeHeuristic` and implement `detect_violations(content)` method.

### 1. BDDJargonHeuristic (Line 139)
- **Purpose**: Detects technical jargon and missing 'should' in test names
- **Detects**:
  - Technical patterns: `getDescriptor`, `isActive`, `PowerItem`, `test_getDescriptor`
  - Missing "should" in `it()` blocks
- **Returns**: List of `Violation` objects with line numbers

### 2. BDDComprehensiveHeuristic (Line 171)
- **Purpose**: Detects overly broad tests and internal assertions
- **Detects**:
  - Internal framework calls: `.toHaveBeenCalled`, `.assert_called`, `.mock.`, `.spyOn(`
- **Returns**: Violations for tests that focus on internals rather than observable behavior

### 3. BDDDuplicateCodeHeuristic (Line 198)
- **Purpose**: Detects duplicate code using string similarity
- **Detects**:
  - 3+ sibling test blocks with >70% similar Arrange code
  - Framework-specific recommendations (Mamba vs Jest)
- **Returns**: Violations with framework-specific fix suggestions

### 4. BDDLayerFocusHeuristic (Line 288)
- **Purpose**: Detects wrong layer focus (testing dependencies instead of code under test)
- **Detects**:
  - Excessive mocking patterns: `mock().mock`, `jest.mock()`, `@patch()`
  - More than 2 mocks per line suggests wrong focus
- **Returns**: Violations indicating focus on dependencies rather than code under test

### 5. BDDFrontEndHeuristic (Line 314)
- **Purpose**: Detects implementation details in front-end tests
- **Detects** (only for `.jsx`, `.tsx`, `.test.jsx`, `.test.tsx`, `.spec.jsx`, `.spec.tsx` files):
  - Implementation detail assertions: `.state.`, `.props.`, `.instance()`, `.debug()`
- **Returns**: Violations for tests that access implementation details

### 6. BDDUnicodeHeuristic (Line 346)
- **Purpose**: Detects non-ASCII characters in test code
- **Detects**:
  - Any character with `ord(char) > 127`
  - Skips encoding declarations and example comments
- **Returns**: Violations with character code and context

### 7. BDDScaffoldBaseHeuristic (Line 383)
- **Purpose**: Base class for scaffold-specific heuristics
- **Provides**:
  - Common scaffold parsing utilities
  - Domain map loading utilities
  - Scaffold file path resolution

## How It Works

1. **BDDCommand** extends `CodeAugmentedCommand` and provides `_get_heuristic_map()`:
   ```python
   def _get_heuristic_map(self):
       return {
           1: BDDRule.BDDJargonHeuristic,
           2: BDDRule.BDDComprehensiveHeuristic,
           3: BDDRule.BDDDuplicateCodeHeuristic,
           4: BDDRule.BDDLayerFocusHeuristic,
           5: BDDRule.BDDFrontEndHeuristic,
           10: BDDRule.BDDUnicodeHeuristic,
       }
   ```

2. **CodeAugmentedCommand** (from missing `common_command_runner.py`) should:
   - Load heuristics based on the heuristic map
   - Run `validate()` method that scans code using heuristics
   - Return violation reports before code execution

3. **Heuristics** scan code line-by-line:
   - Access `content._content_lines` (list of code lines)
   - Use regex patterns to detect violations
   - Return `Violation` objects with line numbers and messages

## Violation Class Structure

Based on usage, `Violation` should have:
- `line_number`: int
- `message`: str
- `principle`: Optional[str] (for some heuristics)

## CodeHeuristic Base Class

Should provide:
- `__init__(detection_pattern: str)` - Initialize with pattern name
- `detect_violations(content)` - Abstract method to implement
- Returns: `List[Violation]` or `None` if no violations

## Integration Points

- **BDDCommand** wraps `CodeAugmentedCommand` and adds BDD-specific heuristics
- **BDDScaffoldCommand** uses `BDDScaffoldRule` which injects scaffold-specific heuristics
- **BDDWorkflow** creates phase commands that use `CodeAugmentedCommand` for validation












