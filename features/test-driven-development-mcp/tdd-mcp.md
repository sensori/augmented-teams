<!-- 57f0c5ff-2b8e-4c1d-bb27-793a07188bb2 e3abd762-e52a-4e1a-8597-3cc123d13b7e -->
# MCP-Based Delivery Pipeline for Cursor Chat

## Thin-Slice Delivery Approach

### Phase 1: Barebones MCP Server (Chat Echo)
**Goal:** Test phrase recognition and workflow response

**Implementation:**
1. Restore delivery-pipeline.py from git (basic structure)
2. Create minimal MCP server with 2 tools:
   - `execute_next_step(feature_name)` - Execute pipeline step
   - `get_current_step(feature_name)` - Get current step
3. Tool handlers:
   - Execute step → returns step result as JSON
   - Echo everything to chat
4. Test phrases in Cursor Chat:
   - "continue" → should call execute_next_step
   - "what step?" → should call get_current_step
   - "generate tests" → should recognize dev_test_red
5. Verify: Chat shows step execution and results

**Success Criteria:**
- Can call MCP tools from Cursor Chat
- Can see step execution in chat
- Phrases trigger correct tools
- Generic fallback works when uncertain

### Phase 2: Code Execution & Prompt Injection
**Goal:** Combine prompts + code + context, identify refinements

**Implementation:**
1. Execute actual code for each step
2. Generate prompts specific to steps (from PHASES)
3. Inject:
   - Current context (what file we're working on)
   - Pipeline state (what phase/step)
   - Canned prompts for AI steps
4. Show Cursor what it needs to do
5. Test: Does Cursor get enough context?
6. Refine prompts based on chat feedback

**Success Criteria:**
- Code execution happens
- Prompts are contextually relevant
- Cursor understands what to do
- Can identify what needs refinement

### Phase 3+: Additional Slices (TBD)
- Add parameter support (num_tests, etc.)
- Add reset functionality
- Add all 12 tools
- Add parameter persistence
- Testing & refinement

## Implementation Order

**Phase 1 (Current):**
1. Restore delivery-pipeline.py from git
2. Create barebones mcp-delivery-pipeline.py
3. Implement execute_next_step and get_current_step only
4. Update mcp.json
5. Test in Cursor Chat with phrases

**Phase 2 (Next):**
6. Add code execution to steps
7. Generate contextual prompts
8. Test prompt quality
9. Refine based on results

**Future Phases:**
10. Add remaining tools
11. Add parameters
12. Add reset
13. Polish

## Tool Categories (Full Vision)

### Generic Tools (When Cursor Doesn't Know Context)

1. `get_pipeline_step(feature_name: str)` - Get current step/phase
2. `execute_next_step(feature_name: str)` - Execute whatever is next
3. `repeat_current_step(feature_name: str)` - Repeat current step with feedback
4. `get_workflow_status(feature_name: str)` - Show all phases and their status
5. `resume_pipeline(feature_name: str, approval: bool)` - Resume from human activity
6. `reset_pipeline(feature_name: str)` - Reset pipeline to beginning

### Phase-Specific Tools (When Cursor Knows What Phase)

7. `dev_test_scaffold(feature_name: str)` - Test Scaffolding step in dev phase
8. `dev_test_red(feature_name: str, num_tests: int = 5)` - Test Red step in dev phase  
9. `dev_code_green(feature_name: str)` - Code Green step in dev phase 
10. `dev_refactor(feature_name: str)` - Refactor step in dev phase 

### Workflow Discovery

11. `list_workflow_phases(feature_name: str)` - Returns all phases with status
12. `get_phase_details(feature_name: str, phase_name: str)` - Get specific phase info

## Tool Parameters

Key parameters:
- **num_tests** (in dev_test_red): How many tests to generate (default: 5, carries forward to subsequent steps)
- **max_retries** (for CODE_RETRY step): How many times to retry code generation (default: 5)
- **approval** (in resume_pipeline): True to approve, False to reject

### To-dos

- [ ] Thin-slice 1: Build barebones MCP server with execute_next_step and get_current_step
- [ ] Thin-slice 2: Add code execution and prompt injection
- [ ] Restore delivery-pipeline.py from git
- [ ] Test phrase recognition in Cursor Chat
- [ ] Add code execution to steps
- [ ] Generate contextual prompts
- [ ] Add remaining tools incrementally
- [ ] Add parameter support
- [ ] Add reset functionality

