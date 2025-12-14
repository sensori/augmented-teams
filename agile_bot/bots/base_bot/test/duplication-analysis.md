# Code Duplication Analysis Across Test Files

This document identifies duplicate code patterns found across test files in `agile_bot/bots/base_bot/test/`.

## Summary

**Total Duplication Patterns Found:** 4 major patterns across multiple files

---

## 1. MockBot Class Duplication

**Location:** `test_build_knowledge.py`

**Duplicates Found:**
- Line 767-769: `MockBot` class with `__init__` method
- Line 806-808: Identical `MockBot` class with `__init__` method

**Code:**
```python
class MockBot:
    def __init__(self, bot_directory):
        self.bot_directory = bot_directory
```

**Recommendation:** Extract to a shared helper function or fixture in `conftest.py` or `test_helpers.py`.

---

## 2. create_bot_config / create_bot_config_file Duplication

**Locations:** 7 files with similar implementations

### Files with `create_bot_config`:
1. `test_helpers.py` (line 54-59) - Uses `get_bot_config_path()` helper
2. `test_base_action.py` (line 20-30) - Hardcoded 'story_bot' name
3. `test_init_project.py` (line 25-30) - Direct path construction
4. `test_generate_bot_server_and_tools.py` (line 23-29) - Uses workspace path

### Files with `create_bot_config_file`:
5. `test_invoke_bot_tool.py` (line 27-36) - Uses workspace path
6. `test_bot_execute_behavior.py` (line 17-26) - Uses workspace path
7. `conftest.py` (line 91-97) - Factory function in conftest

**Common Pattern:**
```python
def create_bot_config(bot_directory: Path, bot_name: str, behaviors: list) -> Path:
    config_dir = bot_directory / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'bot_config.json'
    config_file.write_text(json.dumps({'name': bot_name, 'behaviors': behaviors}), encoding='utf-8')
    return config_file
```

**Variations:**
- Some use `workspace / 'agile_bot' / 'bots' / bot_name / 'config'` path
- Some use `bot_directory / 'config'` path
- Some hardcode bot_name as 'story_bot'

**Recommendation:** Standardize on `conftest.py`'s `create_bot_config_file()` and update all tests to use it, or create a unified version that handles both path patterns.

---

## 3. create_workflow_state Variations Duplication

**Locations:** 6+ files with similar but varying implementations

### Files Found:
1. `test_helpers.py` (line 68-83) - Uses `get_workflow_state_path()` helper
2. `test_invoke_bot_tool.py` (line 57-67) - Direct workspace path, hardcoded timestamp
3. `test_validate_knowledge_and_content_against_rules.py` (line 33-42) - `create_workflow_state_local()`, hardcoded behavior
4. `test_workflow_action_sequence.py` (line 18-33) - Wrapper calling `create_workflow_state_file()`
5. `test_close_current_action.py` (line 24-38) - Wrapper calling `create_workflow_state_file()`
6. `conftest.py` (line 99-114) - `create_workflow_state_file()` factory function

**Common Pattern:**
```python
def create_workflow_state(workspace_dir: Path, current_behavior: str, current_action: str, completed_actions: list = None) -> Path:
    state_file = workspace_dir / 'workflow_state.json'
    state_file.write_text(json.dumps({
        'current_behavior': current_behavior,
        'current_action': current_action,
        'completed_actions': completed_actions or [],
        'timestamp': '2025-12-03T10:00:00Z'  # or similar
    }), encoding='utf-8')
    return state_file
```

**Variations:**
- Some use `bot_name.behavior` format for `current_behavior`
- Some use `bot_name.behavior.action` format for `current_action`
- Some hardcode behavior name (e.g., 'story_bot.exploration')
- Some include timestamp, some don't
- Some use different parameter names (`workspace_dir` vs `workspace`)

**Recommendation:** Standardize on `conftest.py`'s `create_workflow_state_file()` and update all tests to use it. Handle variations through optional parameters.

---

## 4. create_actions_workflow_json Duplication

**Locations:** 2 files with different implementations

### Files Found:
1. `test_helpers.py` (line 201-280+) - Full implementation with optional actions parameter, new format with instructions array per action
2. `test_bot_execute_behavior.py` (line 29-58+) - Simpler implementation, old format with `actions_workflow` structure

**Key Differences:**
- `test_helpers.py`: Uses new format with `instructions` array per action in actions list
- `test_bot_execute_behavior.py`: Uses old format with separate `actions_workflow` key and different structure
- `test_helpers.py`: More flexible, accepts optional `actions` parameter
- `test_bot_execute_behavior.py`: Hardcodes behavior name parsing logic

**Recommendation:** Consolidate to `test_helpers.py` version (newer format) and update `test_bot_execute_behavior.py` to use it. Consider deprecating old format if no longer needed.

---

## Additional Patterns to Investigate

### Story Graph Creation Pattern
Multiple test files create similar story graph structures. Consider extracting a helper function for common story graph patterns.

### Bootstrap Environment Pattern
`bootstrap_env()` is called in multiple places. Verify it's properly centralized in `test_helpers.py`.

---

## Action Items

1. **High Priority:**
   - Extract `MockBot` class to shared helper/fixture
   - Standardize `create_bot_config` functions to use `conftest.py` version
   - Standardize `create_workflow_state` functions to use `conftest.py` version

2. **Medium Priority:**
   - Consolidate `create_actions_workflow_json` implementations
   - Review and refactor story graph creation patterns

3. **Low Priority:**
   - Audit other helper functions for duplication
   - Create test helper documentation

---

## Files Requiring Updates

### Files to Update (remove duplicates):
- `test_build_knowledge.py` - Remove duplicate `MockBot` classes
- `test_base_action.py` - Replace `create_bot_config` with conftest version
- `test_init_project.py` - Replace `create_bot_config` with conftest version
- `test_generate_bot_server_and_tools.py` - Replace `create_bot_config` with conftest version
- `test_invoke_bot_tool.py` - Replace `create_bot_config_file` and `create_workflow_state` with conftest versions
- `test_bot_execute_behavior.py` - Replace `create_bot_config_file` and `create_actions_workflow_json` with test_helpers versions
- `test_validate_knowledge_and_content_against_rules.py` - Replace `create_workflow_state_local` with conftest version
- `test_workflow_action_sequence.py` - Verify using conftest version
- `test_close_current_action.py` - Verify using conftest version

### Files to Keep/Enhance (shared helpers):
- `conftest.py` - Keep and enhance factory functions
- `test_helpers.py` - Keep and enhance shared helpers




