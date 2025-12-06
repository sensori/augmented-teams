# conftest.py Integration Notes for BDD Commands

## Location
`behaviors/bdd/conftest.py`

## Purpose
This pytest plugin file enables VS Code test discovery for Mamba BDD tests. It:
- Parses Mamba test files to discover individual `with it(...)` blocks
- Creates pytest test items for each test, enabling VS Code's test explorer to show individual test play buttons
- **Skips tests inside triple-quoted strings** (sample data) to avoid false test discovery

## Integration with BDD Commands

### Current Commands
- `/bdd-validate` - Uses conftest.py for test discovery
- `/bdd-workflow` - Uses conftest.py for test discovery

### Future Commands (TODO)
When implementing the following BDD workflow commands, ensure they reference and leverage `conftest.py`:

1. **Green Command** (`/bdd-green`)
   - Should use conftest.py to discover tests
   - May need to add executable instructions for running specific tests
   - Should leverage the test discovery mechanism for incremental test execution

2. **Red Command** (`/bdd-red`)
   - Should use conftest.py to discover tests
   - May need to add executable instructions for running failing tests
   - Should leverage the test discovery mechanism for test execution

3. **Refactor Command** (`/bdd-refactor`)
   - Should use conftest.py to discover tests
   - May need to add executable instructions for running tests after refactoring
   - Should leverage the test discovery mechanism to ensure tests still pass after refactoring

## Executable Instructions
Future BDD commands should include executable instructions that:
- Reference `conftest.py` for test discovery
- Use pytest's test collection mechanism
- Leverage the `MambaTestItem` class for running individual tests
- Respect the triple-quoted string filtering (sample data exclusion)

## Key Features
- **String Literal Detection**: The `_is_inside_string_literal()` method correctly identifies when test patterns are inside triple-quoted strings and excludes them from test discovery
- **Test Collection**: Uses regex pattern matching to find `with it(...)` blocks
- **VS Code Integration**: Enables VS Code's test explorer to show individual test play buttons for Mamba tests

## Notes
- This file is project-specific (not part of a library)
- It extends pytest's test collection mechanism
- It handles both `pathlib.Path` and legacy `py.path.local` for compatibility
- Test discovery respects Python string literal boundaries

## Debugging Test Failures

**CRITICAL**: When new tests are failing, it is **NEVER** a global configuration problem. It is **ALWAYS** something specific to those tests.

**Debugging Process:**
1. **Compare failing tests to working tests** - What is different from a meaningful perspective?
2. **Look for structural differences** - Are the failing tests using different patterns, nesting, or syntax?
3. **Check for module-level execution issues** - Are the failing tests executing at module import time when they shouldn't?
4. **Stop messing with the configuration** - The configuration is fine. The problem is in the test code itself.

**Example**: If scaffold tests fail with `TypeError: 'NoneType' object does not support the context manager protocol`, compare them to working tests. The issue is likely that the failing tests have `with context()` blocks executing at module level during pytest import, while working tests are properly guarded or nested differently.

