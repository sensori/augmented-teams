# How to Run Python/Mamba Tests

## CRITICAL: Always Run from Workspace Root

**ALL test commands MUST be run from the workspace root (`c:\dev\augmented-teams`), NOT from subdirectories.**

## Quick Reference - WORKING COMMANDS

**To run all tests (from workspace root):**
```bash
python -m mamba.cli behaviors/code-agent/code_agent_runner_test.py
```

**To run with detailed output:**
```bash
python -m mamba.cli behaviors/code-agent/code_agent_runner_test.py --format documentation
```

**To run with progress dots:**
```bash
python -m mamba.cli behaviors/code-agent/code_agent_runner_test.py --format progress
```

**Expected output when tests run successfully:**
```
X examples ran in X.XXXX seconds
```
(Where X is the number of tests - should be 29+ for code_agent_runner_test.py)

**If you see "0 examples ran":**
- You're in the wrong directory - go to workspace root
- Check that the file path is correct relative to workspace root

## Important Notes

1. **ALWAYS run from workspace root** - Test files use relative paths (`Path(__file__).parent.parent`) that only work from root
2. **Mamba tests use `python -m mamba.cli`** - NOT `mamba` directly
3. **Always check syntax with `read_lints` FIRST** before running tests
4. **Test files use `importlib.util` to load modules** when directory names have hyphens (like `code-agent`)
5. **Patch calls should use `patch.object(module, 'ClassName')`** when patching imported modules
6. **Windows PowerShell encoding**: If you see Unicode errors, tests still run - the failures will show at the end

## Why Tests Must Run from Workspace Root

Test files use relative path resolution like:
```python
common_runner_path = Path(__file__).parent.parent / "common_command_runner" / "common_command_runner.py"
```

This assumes `__file__` is at `behaviors/code-agent/code_agent_runner_test.py`, so:
- `Path(__file__).parent` = `behaviors/code-agent/`
- `Path(__file__).parent.parent` = `behaviors/`
- Final path = `behaviors/common_command_runner/common_command_runner.py` ✅

If you run from `behaviors/code-agent/`, the path resolution breaks.

## Common Issues

- **"0 examples ran"**: You're probably running from wrong directory - go to workspace root
- **FileNotFoundError for common_command_runner**: You're running from wrong directory - go to workspace root  
- **ModuleNotFoundError**: Check import paths - use `importlib.util` for hyphenated directories
- **SyntaxError**: Run `read_lints` first to catch syntax errors before running tests
- **Import errors**: Verify you're running from workspace root, paths are relative to that
- **UnicodeEncodeError in output**: Tests still run - ignore encoding warnings, check the actual test results

## Verification

To verify you're in the right place:
```bash
# Should show workspace root files
ls .git
ls behaviors

# Then run tests - should show "X examples ran"
python -m mamba.cli behaviors/code-agent/code_agent_runner_test.py
```

## Test Results Interpretation

- **"X examples ran in X.XXXX seconds"** = Tests executed successfully
- **"X examples failed of Y ran"** = Some tests failed, but tests are running
- **"0 examples ran"** = Tests not discovered - check directory and file path
