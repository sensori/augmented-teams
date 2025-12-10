# Test Migration Guide

## Bootstrap Pattern Changes

All tests need to be updated to use the new bootstrap pattern where environment variables are set at the beginning of each test.

##  Core Pattern

### OLD Pattern (❌ Remove)
```python
@pytest.fixture
def workspace_root(tmp_path):
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    return workspace

# In tests:
action = GatherContextAction(
    bot_name='story_bot',
    behavior='discovery',
    workspace_root=workspace_root  # ❌ Remove
)
```

### NEW Pattern (✅ Use)
```python
@pytest.fixture
def bot_directory(tmp_path):
    bot_dir = tmp_path / 'agile_bot' / 'bots' / 'story_bot'
    bot_dir.mkdir(parents=True)
    return bot_dir

@pytest.fixture
def workspace_directory(tmp_path):
    workspace_dir = tmp_path / 'workspace'
    workspace_dir.mkdir(parents=True)
    return workspace_dir

# In tests:
from test_helpers import bootstrap_env

# Bootstrap at start of test
bootstrap_env(bot_directory, workspace_directory)

action = GatherContextAction(
    bot_name='story_bot',
    behavior='discovery',
    bot_directory=bot_directory  # ✅ Use bot_directory
)
```

## Systematic Changes Required

### 1. Update Fixtures

**Files**: All test_*.py files with local fixtures

**Change**:
```python
# OLD
@pytest.fixture
def workspace_root(tmp_path):
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    return workspace

# NEW - Use fixtures from conftest.py or define both:
@pytest.fixture
def bot_directory(tmp_path):
    bot_dir = tmp_path / 'agile_bot' / 'bots' / 'story_bot'
    bot_dir.mkdir(parents=True)
    return bot_dir

@pytest.fixture
def workspace_directory(tmp_path):
    workspace_dir = tmp_path / 'workspace'
    workspace_dir.mkdir(parents=True)
    return workspace_dir
```

### 2. Update Action Class Instantiation

**Files**: All tests creating Action instances

**Pattern**: Remove `workspace_root` parameter, add `bot_directory`

```python
# OLD
action = GatherContextAction(
    bot_name='story_bot',
    behavior='discovery',
    workspace_root=workspace_root
)

# NEW
bootstrap_env(bot_directory, workspace_directory)
action = GatherContextAction(
    bot_name='story_bot',
    behavior='discovery',
    bot_directory=bot_directory
)
```

**Apply to all action classes**:
- GatherContextAction
- PlanningAction
- BuildKnowledgeAction
- RenderOutputAction
- ValidateRulesAction

### 3. Update Bot Instantiation

**Files**: test_invoke_bot_tool.py, test_invoke_bot_cli.py, test_complete_workflow_integration.py

```python
# OLD
bot = Bot(
    bot_name='story_bot',
    workspace_root=workspace_root,
    config_path=config_path
)

# NEW
bootstrap_env(bot_directory, workspace_directory)
bot = Bot(
    bot_name='story_bot',
    bot_directory=bot_directory,
    config_path=config_path
)
```

### 4. Update Workflow Instantiation

**Files**: test_close_current_action.py, test_workflow_action_sequence.py, others

```python
# OLD
workflow = Workflow(
    bot_name='story_bot',
    behavior='shape',
    workspace_root=workspace_root,
    states=states,
    transitions=transitions
)

# NEW
bootstrap_env(bot_directory, workspace_directory)
workflow = Workflow(
    bot_name='story_bot',
    behavior='shape',
    bot_directory=bot_directory,
    states=states,
    transitions=transitions
)
```

### 5. Update ActivityTracker

**Files**: test_invoke_bot_tool.py, test_guards_prevent_writes_without_project.py

```python
# OLD
tracker = ActivityTracker(workspace_root=workspace, bot_name='story_bot')

# NEW
bootstrap_env(bot_directory, workspace_directory)
tracker = ActivityTracker(bot_name='story_bot')  # No parameters needed
```

### 6. Update MCPServerGenerator

**Files**: test_generate_bot_server_and_tools.py

```python
# OLD
generator = MCPServerGenerator(
    workspace_root=workspace_root,
    bot_location='agile_bot/bots/test_bot'
)

# NEW
generator = MCPServerGenerator(
    bot_directory=bot_directory,
    bot_location='agile_bot/bots/test_bot'
)
```

### 7. Update BaseBotCli

**Files**: test_invoke_bot_cli.py

```python
# OLD
cli = BaseBotCli(
    bot_name='story_bot',
    bot_config_path=config_path,
    workspace_root=workspace_root
)

# NEW
bootstrap_env(bot_directory, workspace_directory)
cli = BaseBotCli(
    bot_name='story_bot',
    bot_config_path=config_path
)
```

### 8. Update Helper Function Calls

**Files**: All files using test_helpers.py functions

```python
# OLD
verify_action_tracks_start(workspace_root, GatherContextAction, 'gather_context')

# NEW
verify_action_tracks_start(bot_directory, workspace_directory, GatherContextAction, 'gather_context')

# OLD
verify_workflow_transition(workspace_root, 'gather_context', 'decide_planning_criteria')

# NEW
verify_workflow_transition(bot_directory, workspace_directory, 'gather_context', 'decide_planning_criteria')
```

### 9. Update Factory Function Calls

**Files**: All files using conftest.py or test_helpers.py factories

```python
# OLD
create_bot_config(workspace_root, 'test_bot', ['shape'])

# NEW
create_bot_config(bot_directory, 'test_bot', ['shape'])

# OLD
create_guardrails_files(workspace_root, 'test_bot', 'shape', questions, evidence)

# NEW
create_guardrails_files(bot_directory, 'shape', questions, evidence)
```

### 10. Fix Legacy Parameter Names

**Find/Replace**: `botspace_root` → `bot_directory`

Some tests use the typo `botspace_root` which should be `bot_directory`.

## File-by-File Checklist

### ✅ COMPLETED
- [x] test_init_project.py - Completely rewritten
- [x] test_helpers.py - All helpers updated
- [x] test_utils.py - Behavior.find_behavior_folder fixed
- [x] test_workflow_action_sequence.py - All tests updated
- [x] conftest.py - Bootstrap fixtures added

### 📝 TODO - Action Tests
- [ ] test_gather_context.py (~9 tests)
- [ ] test_gather_context_action.py (~2 tests)
- [ ] test_decide_planning_criteria.py (~6 tests)
- [ ] test_build_knowledge.py (~6 tests)
- [ ] test_render_output.py (~6 tests)
- [ ] test_validate_knowledge_and_content_against_rules.py (~9 tests)
- [ ] test_load_rendered_content.py (~10 tests)

### 📝 TODO - Workflow/Integration Tests
- [ ] test_close_current_action.py (~6 tests)
- [ ] test_complete_workflow_integration.py (~1 test)

### 📝 TODO - Bot/CLI Tests
- [ ] test_invoke_bot_tool.py (~10 tests)
- [ ] test_invoke_bot_cli.py (~4 tests)

### 📝 TODO - Generator Tests
- [ ] test_generate_bot_server_and_tools.py (~13 tests)

### 📝 TODO - Guards Tests
- [ ] test_guards_prevent_writes_without_project.py (~6 tests)

### 📝 TODO - Context Tests
- [ ] test_context_folder_management.py (~4 tests) - May need removal/rewrite

## Quick Reference: Common Patterns

### Pattern 1: Simple Action Test
```python
def test_action_does_something(bot_directory, workspace_directory):
    # Bootstrap
    bootstrap_env(bot_directory, workspace_directory)
    
    # Create action
    action = SomeAction(
        bot_name='story_bot',
        behavior='shape',
        bot_directory=bot_directory
    )
    
    # Test action
    result = action.execute()
    assert result.status == 'completed'
```

### Pattern 2: Workflow Test
```python
def test_workflow_transitions(bot_directory, workspace_directory):
    # Bootstrap
    bootstrap_env(bot_directory, workspace_directory)
    
    # Create workflow state file
    create_workflow_state(workspace_directory, 'story_bot', 'shape.gather_context')
    
    # Create workflow
    workflow = Workflow(
        bot_name='story_bot',
        behavior='shape',
        bot_directory=bot_directory,
        states=states,
        transitions=transitions
    )
    
    # Test
    workflow.transition_to_next()
    assert workflow.state == 'decide_planning_criteria'
```

### Pattern 3: Bot Integration Test
```python
def test_bot_executes_action(bot_directory, workspace_directory):
    # Bootstrap
    bootstrap_env(bot_directory, workspace_directory)
    
    # Create bot config
    config_path = create_bot_config(bot_directory, 'story_bot', ['shape'])
    
    # Create bot
    bot = Bot(
        bot_name='story_bot',
        bot_directory=bot_directory,
        config_path=config_path
    )
    
    # Test
    result = bot.shape.gather_context()
    assert result.status == 'completed'
```

## Validation

After fixing each file, run:
```bash
python -m pytest agile_bot/bots/base_bot/test/test_FILE_NAME.py -v
```

After fixing all files, run full suite:
```bash
python -m pytest agile_bot/bots/base_bot/test/ -v
```

Target: All 130+ tests passing ✅



