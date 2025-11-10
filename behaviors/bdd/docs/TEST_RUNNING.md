# How to Run Python/Mamba Tests

## Command to Run Tests

**For Mamba tests (BDD-style Python tests):**

```bash
python -m mamba.cli <test_file_path>
```

**Example:**
```bash
python -m mamba.cli behaviors/code-agent/code_agent_runner_test.py
```

## Important Notes

1. **Mamba is a Python package** - Use `python -m mamba.cli` NOT just `mamba` or `python -m mamba`
2. **Test files use importlib** - Since directories have hyphens (like `code-agent`), tests use `importlib.util` to load modules directly
3. **Path resolution** - Tests run from workspace root, paths are relative to that
4. **Import pattern** - Use `patch.object(module, 'ClassName')` for mocking, not string paths like `'module.ClassName'`

## Alternative: Using pytest (via conftest.py)

The codebase has a `conftest.py` that allows pytest to discover and run Mamba tests:

```bash
pytest behaviors/code-agent/code_agent_runner_test.py
```

This uses the custom pytest plugin that wraps mamba execution.

## Common Issues

- **ModuleNotFoundError**: Check import paths - use `importlib.util` for modules in directories with hyphens
- **Syntax errors**: Make sure patch calls use `patch.object(module, 'attr')` not string paths
- **Import errors**: Ensure `sys.path` is set correctly or use `importlib.util` for direct file imports

