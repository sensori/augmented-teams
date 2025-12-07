# Test Scenario Comments Inline With Code

## Rule

**Avoid long docstrings at the beginning of test methods.** Instead, place scenario step comments (Given/When/Then) right above the code that implements each step. This keeps requirements and implementation together, making tests easier to read and maintain.

## Pattern

### ❌ WRONG: All scenario at top, code at bottom

```python
def test_close_current_action_marks_complete_and_transitions():
    """
    Scenario: Close current action and transition to next
    
    Given workflow is at action "gather_context"
    And action has NOT been marked complete yet
    When user closes current action
    Then action "gather_context" is saved to completed_actions
    And workflow transitions to "decide_planning_criteria"
    """
    # All code here, far from the scenario steps
    bot_name = 'story_bot'
    behavior = 'shape'
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    project_dir = tmp_path / 'test_project'
    project_dir.mkdir(parents=True)
    workflow = Workflow(...)
    workflow.save_completed_action('gather_context')
    workflow.transition_to_next()
    assert workflow.current_state == 'decide_planning_criteria'
```

**Problem:** Reader has to scroll back up to remember what "Given" vs "When" vs "Then" are

---

### ✅ CORRECT: Scenario steps inline with code

```python
def test_close_current_action_marks_complete_and_transitions():
    """Scenario: Close current action and transition to next"""
    
    # Given workflow is at action "gather_context"
    # And action has NOT been marked complete yet
    bot_name = 'story_bot'
    behavior = 'shape'
    bot_dir = tmp_path / 'agile_bot' / 'bots' / bot_name
    project_dir = tmp_path / 'test_project'
    project_dir.mkdir(parents=True)
    workflow = Workflow(...)
    
    # When user closes current action
    workflow.save_completed_action('gather_context')
    workflow.transition_to_next()
    
    # Then action "gather_context" is saved to completed_actions
    # And workflow transitions to "decide_planning_criteria"
    assert workflow.is_action_completed('gather_context')
    assert workflow.current_state == 'decide_planning_criteria'
```

**Benefits:**
- ✅ Scenario step right above implementing code
- ✅ Easy to see what each code block does
- ✅ No scrolling back to docstring
- ✅ Requirements and implementation co-located

---

## Docstring Content

### Keep docstring SHORT - just the scenario title

**✅ CORRECT:**
```python
def test_workflow_starts_at_first_action():
    """Scenario: Workflow starts at first action when no completed actions"""
```

**✅ CORRECT (with story reference):**
```python
def test_workflow_starts_at_first_action():
    """
    Story: Workflow Action Sequence
    Scenario: Workflow starts at first action when no completed actions
    """
```

**❌ WRONG (too much detail):**
```python
def test_workflow_starts_at_first_action():
    """
    Scenario: Workflow starts at first action when no completed actions
    
    Given workflow has no completed actions
    When workflow is initialized
    Then current_state should be first action
    
    This test verifies that...
    Background context about...
    Implementation notes...
    """
```

---

## Step Comments Format

### Use BDD Step Keywords

```python
# Given [precondition]
# And [additional precondition]
# When [action]
# Then [expected outcome]
# And [additional outcome]
```

### Multiple Steps Use Numbers

```python
# Step 1: Initialize project
code_for_step_1()

# Step 2: Execute gather_context  
code_for_step_2()

# Step 3: Verify state transition
assertions_for_step_3()
```

---

## Complex Test Example

```python
def test_complete_workflow_end_to_end():
    """Story: Close Current Action - Complete end-to-end workflow"""
    
    # Setup
    bot_name = 'story_bot'
    bot = Bot(...)
    
    # Step 1: Initialize project
    result = bot.shape.initialize_project({'confirm': True})
    assert result.action == 'initialize_project'
    assert bot.shape.workflow.is_action_completed('initialize_project')
    
    # Step 2: Forward to gather_context
    result = bot.shape.forward_to_current_action()
    assert bot.shape.workflow.current_state == 'gather_context'
    
    # Step 3: Close gather_context
    bot.shape.workflow.save_completed_action('gather_context')
    bot.shape.workflow.transition_to_next()
    assert bot.shape.workflow.current_state == 'decide_planning_criteria'
    
    # Step 4: Jump to discovery.gather_context (out of order)
    result = bot.discovery.gather_context()
    state = json.loads(workflow_file.read_text())
    assert state['current_behavior'] == 'story_bot.discovery'
    assert state['current_action'] == 'story_bot.discovery.gather_context'
```

**Each step comment immediately above the code that implements it!**

---

## Summary

**Pattern:**
1. **Short docstring** - Just scenario title (1-2 lines)
2. **Inline comments** - Given/When/Then right above implementing code
3. **Co-located** - Requirements next to implementation

**Benefits:**
- Easier to read (no scrolling)
- Easier to maintain (change step and code together)
- Self-documenting (scenario flows with code)
- Clear test structure (visual separation)

**Golden Rule:** Place scenario step comment immediately above the code that implements that step.




