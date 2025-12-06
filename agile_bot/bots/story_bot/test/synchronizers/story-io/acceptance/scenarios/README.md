# Scenario-Based Acceptance Tests

Each scenario follows a **Given-When-Then** (BDD) structure with separate folders for each phase.

## Scenario Structure

```
scenarios/
└── scenario_name/
    ├── 1_given/                           # GIVEN: Setup and test data
    │   ├── load_*.py                      # Script to load/prepare test data
    │   ├── story-graph.json               # Input story graph JSON
    │   ├── layout.json                    # (optional) Layout data
    │   └── original_story_graph.json      # For scenarios that need merge
    ├── 2_when/                            # WHEN: Actions/workflow execution
    │   ├── <action>_then_<action>.py      # Workflow script
    │   ├── synced-story-graph.json        # Generated: Synced JSON output
    │   ├── temp_*.json                     # Temporary files generated during workflow
    │   └── ...                            # Other generated intermediate files
    ├── 3_then/                            # THEN: Assertions and verification
    │   ├── assert_*.py                    # Assertion script
    │   ├── expected.drawio                # Expected DrawIO output (required)
    │   ├── expected.json                  # (optional) Expected JSON output
    │   ├── actual-*.drawio                # Generated: Actual render outputs
    │   ├── actual-*.json                  # Generated: Actual extracted JSONs
    │   └── ...                            # Other assertion outputs
    └── test_render_sync_render_round_trip.py  # Main test orchestrator
```

## Given-When-Then Workflow

### 1. GIVEN (Setup Phase)
**Folder**: `1_given/`

- **Purpose**: Prepare test data and setup
- **Contains**:
  - Input story graph JSON files
  - Layout data files (if needed)
  - Data loading scripts (e.g., `load_story_graph_data.py`)
  - Helper functions to access test data
  - Additional input files like `original_story_graph.json` for merge scenarios (directly in `1_given/`)

**Example**:
```python
# 1_given/load_story_graph_data.py
def get_story_graph() -> Dict[str, Any]:
    """Load story graph from given data."""
    story_graph_path = given_dir / "story-graph-simple.json"
    return load_story_graph(story_graph_path)
```

### 2. WHEN (Action Phase)
**Folder**: `2_when/`

- **Purpose**: Execute the workflow/actions being tested
- **Contains**:
  - Workflow execution scripts (e.g., `render_then_sync_then_render_graph.py`)
  - Generated intermediate files (synced JSON, merge reports, layouts, etc.)
  - Temporary files (`temp_*.json`, `temp_*.drawio`) - Generated during workflow execution
  - Action scripts that perform render, sync, merge operations
  - **Note**: Actual outputs are written to `3_then/`, temporary files stay in `2_when/`

**Example Workflows**:
- Render JSON → DrawIO → Sync back to JSON → Render again (round-trip)
- Sync DrawIO → JSON → Merge with original → Render merged JSON
- Exploration render with layout preservation

### 3. THEN (Assertion Phase)
**Folder**: `3_then/`

- **Purpose**: Verify expected results match actual results
- **Contains**:
  - **Expected files** (required): `expected.drawio`, `expected.json`, etc. - These define what the test expects
  - **Actual files** (generated): `actual-*.drawio`, `actual-*.json`, etc. - Generated during `2_when/` execution and written to `3_then/`
  - Assertion scripts (e.g., `assert_story_graph_round_trip.py`) - Compare expected vs actual
  - Comparison results

**Important**: All tests validate **expected** (from `3_then/` or `1_given/`) vs **actual** (generated during `2_when/`)

**Example Assertions**:
- JSONs match: expected JSON (from `1_given/`) vs intermediate synced JSON (from `2_when/`)
- DrawIOs match: expected DrawIO (from `3_then/expected.drawio`) vs actual rendered DrawIO (from `3_then/actual-*.drawio`)
- Layout preservation: element positioning matches expected
- Story graph data integrity through round-trip
- Acceptance criteria extraction: Acceptance criteria are extracted from DrawIO and matched to their stories

**Note**: 
- **Intermediate files** (synced JSONs, merge reports, layouts) stay in `2_when/`
- **Temporary files** (`temp_*.json`, `temp_*.drawio`) are generated in `2_when/`
- **Actual output files** (rendered DrawIOs, extracted JSONs) are written to `3_then/` during `2_when/` execution for comparison with expected files

## Running Tests

### Run a specific scenario:

**Using Python directly:**
```bash
python scenarios/scenario_name/test_render_sync_render_round_trip.py
```

**Using test runner scripts (Windows):**
```bash
# Batch file
scenarios/scenario_name/run_test.bat

# PowerShell
scenarios/scenario_name/run_test.ps1
```

**From scenario directory:**
```bash
cd scenarios/scenario_name
python test_render_sync_render_round_trip.py
# or
run_test.bat
# or
.\run_test.ps1
```

### Test Runner Scripts

Each scenario may include test runner scripts for convenience:

- **`run_test.bat`** - Windows batch file that runs the test with proper encoding
- **`run_test.ps1`** - PowerShell script with colored output
- **`test_render_sync_render_round_trip.py`** - Main Python test orchestrator

The test orchestrator (`test_render_sync_render_round_trip.py`) follows the Given-When-Then pattern:
1. **GIVEN**: Verifies input data exists in `1_given/`
2. **WHEN**: Executes workflow script from `2_when/`
3. **THEN**: Runs assertion script from `3_then/`

## Test Execution Flow

1. **GIVEN**: Test orchestrator loads data from `1_given/` (including all input files directly in `1_given/`)
2. **WHEN**: Executes workflow script from `2_when/`
   - Generates intermediate files in `2_when/` (synced JSONs, merge reports, layouts)
   - Generates temporary files in `2_when/` (temp_*.json, temp_*.drawio)
   - Generates actual output files in `3_then/` (e.g., `actual-first-render.drawio`, `actual-second-render.drawio`)
3. **THEN**: Runs assertion script from `3_then/`
   - **Always validates expected vs actual**:
     - Expected files from `3_then/expected.*` or `1_given/*.json`
     - Actual files in `3_then/actual-*.*` (generated during `2_when/` execution)
   - Compares expected vs actual
   - Reports pass/fail status

## Output Locations

- **Intermediate files**: `2_when/` (synced JSONs, merge reports, layouts) - Generated during workflow execution
- **Temporary files**: `2_when/` (temp_*.json, temp_*.drawio) - Generated during workflow execution, cleaned up after use
- **Actual outputs**: `3_then/` (actual-*.drawio, actual-*.json) - Generated during `2_when/` execution, written to `3_then/`
- **Expected files**: `3_then/` (expected.drawio, expected.json) - Always present for validation

## Common Test Patterns

### Round-Trip Test (Render → Sync → Render)
- **Given**: Story graph JSON
- **When**: Render to DrawIO, sync back to JSON, render again
- **Then**: Assert JSONs match and DrawIO layout is preserved

### Layout Preservation Test
- **Given**: Story graph with layout data
- **When**: Render with layout, sync, render again
- **Then**: Assert element positions are preserved

### Merge Test
- **Given**: Original story graph + DrawIO file
- **When**: Sync DrawIO, merge with original, render merged
- **Then**: Assert merged result matches expected




