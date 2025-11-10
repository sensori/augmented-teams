# How to Run Python/Mamba Tests

## Mamba BDD Tests

Mamba tests use the BDD pattern with `with description`, `with context`, and `with it` blocks.

### Running All Tests in a File

```bash
python -m mamba.cli behaviors/path/to/test_file_test.py
```

### Running via Pytest (VS Code Integration)

```bash
pytest behaviors/path/to/test_file_test.py
```

Pytest will use `conftest.py` to discover and run individual Mamba tests.

### Running a Specific Test by Line Number

```bash
python -m mamba.cli behaviors/path/to/test_file_test.py --line 123
```

### Common Issues

1. **Import errors**: If tests import modules with hyphens in directory names (e.g., `code-agent`), use `importlib.util` to load them directly:
   ```python
   import importlib.util
   module_path = Path(__file__).parent / "module_name.py"
   spec = importlib.util.spec_from_file_location("module_name", module_path)
   module = importlib.util.module_from_spec(spec)
   spec.loader.exec_module(module)
   ```

2. **Module not found**: Ensure you're running from the workspace root, or adjust `sys.path` accordingly.

3. **Patching**: When patching modules loaded via `importlib.util`, use `patch.object(module, 'ClassName')` instead of string-based patching.

## Test File Naming

- Mamba test files: `*_test.py` or `test_*.py`
- Located in `behaviors/` directory structure

## Example Test Structure

```python
from mamba import description, context, it, before
from expects import expect, equal, be_true

with description('a feature'):
    with context('that does something'):
        with it('should behave correctly'):
            expect(result).to(equal(expected))
```
