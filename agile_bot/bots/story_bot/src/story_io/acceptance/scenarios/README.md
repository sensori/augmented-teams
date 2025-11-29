# Scenario-Based Acceptance Tests

Each scenario is a folder containing test files and optionally an `input/` directory.

## Scenario Structure

```
scenarios/
└── scenario_name/
    ├── expected_story_graph.json          # OR
    ├── expected_story-map-outline.drawio  # (one of these required)
    ├── input/                              # (optional)
    │   ├── original_story_graph.json      # For DrawIO scenarios that need merge
    │   └── ...                             # Other input files
    └── original_story_graph.json          # Alternative location for original (DrawIO scenarios)
```

## Test Types

### JSON-Based Scenarios
- **Expected file**: `expected_story_graph.json`
- **Workflow**: 
  1. Render expected JSON → DrawIO
  2. Sync DrawIO → JSON
  3. Render synced JSON → DrawIO
  4. Assert: Both JSONs match, both DrawIOs match

### DrawIO-Based Scenarios
- **Expected file**: `expected_story-map-outline.drawio`
- **Workflow**:
  1. Sync DrawIO → JSON
  2. Merge with original (if `original_story_graph.json` exists)
  3. Render merged JSON → DrawIO
  4. Assert: Rendered DrawIO matches expected DrawIO

## Running Tests

### Run all scenarios:
```bash
python src/story_io/acceptance/test_scenario_based.py
```

### Run specific scenario:
```bash
python src/story_io/acceptance/test_scenario_based.py --scenario complex_story_graph
```

### Custom directories:
```bash
python src/story_io/acceptance/test_scenario_based.py \
  --scenarios-dir my_scenarios \
  --output-dir my_outputs
```

## Output

Test results are saved to `outputs/scenario_tests/<scenario_name>/`:
- Rendered DrawIO files
- Synced/merged JSON files
- Layout files
- Comparison reports
- Test summary JSON




