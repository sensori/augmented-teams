# Acceptance Tests Refactoring Summary

## Status: In Progress

### Completed ✅

**All 10 JSON-based scenarios have been refactored to Given-When-Then structure:**

1. ✅ `simple_story_graph` → `test_render_sync_render_round_trip.py`
2. ✅ `single_epic_story_graph` → `test_render_sync_render_round_trip.py`
3. ✅ `multiple_epics_features_test` → `test_render_sync_render_round_trip.py` (with input folder support)
4. ✅ `multiple_users_story_graph` → `test_render_sync_render_round_trip.py`
5. ✅ `optional_vs_sequential_story_graph` → `test_render_sync_render_round_trip.py`
6. ✅ `complex_story_graph` → `test_render_sync_render_round_trip.py` (with input folder support)
7. ✅ `different_story_types_story_graph` → `test_render_sync_render_round_trip.py`
8. ✅ `incomplete_with_estimates_story_graph` → `test_render_sync_render_round_trip.py`
9. ✅ `with_acceptance_criteria_story_graph` → `test_render_sync_render_round_trip.py`
10. ✅ `with_increments_story_graph` → `test_render_sync_render_round_trip.py` (uses render_increments_from_graph)

### Structure Created

Each scenario now follows this structure:
```
scenarios/<scenario_name>/
├── test_render_sync_render_round_trip.py    # Top-level orchestrator
├── 1_given/                                  # Input data
│   ├── load_story_graph_data.py            # Data loading helper
│   └── story-graph-<descriptive-name>.json  # Input/expected JSON
├── 2_when/                                   # Workflow execution
│   └── render_then_sync_then_render_graph.py
└── 3_then/                                   # Assertions
    └── assert_story_graph_round_trip.py
```

### Special Cases Handled

- **Input folders**: Scenarios with `input/` folders (multiple_epics_features_test, complex_story_graph) now check input folder first, then fall back to expected JSON
- **Increments**: `with_increments_story_graph` automatically detects increments and uses `render_increments_from_graph` / `synchronize_increments`

### Completed Additional Refactoring ✅

11. ✅ **layout_preservation** → `test_preserve_layout_positions.py`
    - Tests sync-then-render workflow preserves layout positions
    - Compares positions from original vs rendered DrawIO
    - Reports preservation rate and identifies issues

### Remaining Work ⏳

1. **test_epic_feature_positioning.py** - Validation test (different structure, may not need refactoring)
2. **test_actual_story_map.py** - Needs refactoring to spec-by-example structure
3. **Cleanup**:
   - Remove old test runners (`test_acceptance.py`, `test_scenario_based.py`)
   - Archive or remove old `actual/` folders
   - Update documentation

### Naming Conventions Applied

- **Test files**: `test_<verb>_<noun>.py` (e.g., `test_render_sync_render_round_trip.py`)
- **Workflow files**: `<verb>_<noun>_<specifier>.py` (e.g., `render_then_sync_then_render_graph.py`)
- **Assertion files**: `assert_<what>_<verified>.py` (e.g., `assert_story_graph_round_trip.py`)
- **Data files**: Descriptive names with hyphens (e.g., `story-graph-multiple-epics-features.json`)

### Shared Utilities Used

- `spec_by_example/drawio_comparison.py` - For DrawIO comparisons
- `spec_by_example/story_graph_layout_helper.py` - For loading/saving story graphs and layouts

### Next Steps

1. Test all refactored scenarios to ensure they work correctly
2. Refactor remaining test files (test_layout_preservation.py, test_epic_feature_positioning.py)
3. Create README documenting the new structure
4. Clean up old files
5. Update CI/CD if needed

