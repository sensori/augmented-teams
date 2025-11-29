"""
Migrate old input/output structure to new scenario-based format.
"""

import shutil
from pathlib import Path

def migrate_to_scenarios():
    """Migrate all old input files to scenario-based structure."""
    acceptance_dir = Path(__file__).parent
    old_input_dir = acceptance_dir / "input"
    old_outputs_dir = acceptance_dir / "outputs"
    scenarios_dir = acceptance_dir / "scenarios"
    
    scenarios_dir.mkdir(exist_ok=True)
    
    # Map of old input files to scenario names
    json_files = [
        "complex_story_graph.json",
        "different_story_types_story_graph.json",
        "incomplete_with_estimates_story_graph.json",
        "multiple_epics_features_test_story_graph.json",
        "multiple_users_story_graph.json",
        "optional_vs_sequential_story_graph.json",
        "simple_story_graph.json",
        "single_epic_story_graph.json",
        "with_acceptance_criteria_story_graph.json",
        "with_increments_story_graph.json",
    ]
    
    # Special case: multiple_epics_features_test.json (might be a duplicate or variant)
    # We'll handle it separately
    
    # DrawIO file
    drawio_file = "story-map-outline-original.drawio"
    
    print("Migrating input files to scenario structure...")
    
    # Migrate JSON files
    for json_file in json_files:
        old_path = old_input_dir / json_file
        if not old_path.exists():
            print(f"  [SKIP] {json_file} not found")
            continue
        
        # Extract scenario name (keep full name, just remove .json extension)
        if json_file.endswith(".json"):
            scenario_name = json_file.replace(".json", "")
        else:
            scenario_name = json_file
        
        # Create scenario folder
        scenario_folder = scenarios_dir / scenario_name
        scenario_folder.mkdir(exist_ok=True)
        
        # Copy to expected_story_graph.json
        expected_path = scenario_folder / "expected_story_graph.json"
        if not expected_path.exists():
            shutil.copy2(old_path, expected_path)
            print(f"  [OK] Created {scenario_name}/expected_story_graph.json")
        else:
            print(f"  [SKIP] {scenario_name}/expected_story_graph.json already exists")
    
    # Handle multiple_epics_features_test.json (might be input for the test scenario)
    test_json = old_input_dir / "multiple_epics_features_test.json"
    if test_json.exists():
        scenario_folder = scenarios_dir / "multiple_epics_features_test"
        scenario_folder.mkdir(exist_ok=True)
        input_dir = scenario_folder / "input"
        input_dir.mkdir(exist_ok=True)
        input_path = input_dir / "input_story_graph.json"
        if not input_path.exists():
            shutil.copy2(test_json, input_path)
            print(f"  [OK] Created multiple_epics_features_test/input/input_story_graph.json")
    
    # Migrate DrawIO file
    drawio_path = old_input_dir / drawio_file
    if drawio_path.exists():
        scenario_name = "story_map_outline_original"
        scenario_folder = scenarios_dir / scenario_name
        scenario_folder.mkdir(exist_ok=True)
        
        expected_path = scenario_folder / "expected_story-map-outline.drawio"
        if not expected_path.exists():
            shutil.copy2(drawio_path, expected_path)
            print(f"  [OK] Created {scenario_name}/expected_story-map-outline.drawio")
            
            # Check if there's an original JSON for merge
            extracted_json = old_input_dir / "story-graph-drawio-extracted.json"
            if extracted_json.exists():
                input_dir = scenario_folder / "input"
                input_dir.mkdir(exist_ok=True)
                original_path = input_dir / "original_story_graph.json"
                if not original_path.exists():
                    shutil.copy2(extracted_json, original_path)
                    print(f"  [OK] Created {scenario_name}/input/original_story_graph.json")
        else:
            print(f"  [SKIP] {scenario_name}/expected_story-map-outline.drawio already exists")
    
    # Handle layout file if it exists
    layout_file = old_input_dir / "story-graph-drawio-extracted-layout.json"
    if layout_file.exists():
        scenario_name = "story_map_outline_original"
        scenario_folder = scenarios_dir / scenario_name
        input_dir = scenario_folder / "input"
        input_dir.mkdir(exist_ok=True)
        layout_path = input_dir / "layout.json"
        if not layout_path.exists():
            shutil.copy2(layout_file, layout_path)
            print(f"  [OK] Created {scenario_name}/input/layout.json")
    
    print("\nMigration complete!")
    print(f"\nScenarios created in: {scenarios_dir}")
    print(f"\nOld input directory preserved at: {old_input_dir}")
    print(f"Old outputs directory preserved at: {old_outputs_dir}")
    print("\nYou can now run tests with:")
    print("  python src/story_io/acceptance/test_scenario_based.py")

if __name__ == "__main__":
    migrate_to_scenarios()

