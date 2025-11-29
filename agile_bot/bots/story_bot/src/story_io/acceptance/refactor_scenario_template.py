"""
Template script to help refactor scenarios to Given-When-Then structure.

Usage: python refactor_scenario_template.py <scenario_name> <descriptive_json_name>
Example: python refactor_scenario_template.py multiple_epics_features_test story-graph-multiple-epics-features.json
"""
import sys
from pathlib import Path
import shutil

def refactor_scenario(scenario_name: str, json_filename: str):
    """Refactor a scenario to Given-When-Then structure."""
    acceptance_dir = Path(__file__).parent
    scenario_dir = acceptance_dir / "scenarios" / scenario_name
    
    if not scenario_dir.exists():
        print(f"[ERROR] Scenario directory not found: {scenario_dir}")
        return False
    
    # Create folder structure
    given_dir = scenario_dir / "1_given"
    when_dir = scenario_dir / "2_when"
    then_dir = scenario_dir / "3_then"
    
    for dir_path in [given_dir, when_dir, then_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Move expected JSON to 1_given with descriptive name
    expected_json = scenario_dir / "expected_story_graph.json"
    if expected_json.exists():
        new_json_path = given_dir / json_filename
        if not new_json_path.exists():
            shutil.move(str(expected_json), str(new_json_path))
            print(f"[OK] Moved {expected_json.name} -> {new_json_path.name}")
        else:
            print(f"[INFO] {new_json_path.name} already exists")
    
    # Create load_story_graph_data.py
    load_helper = given_dir / "load_story_graph_data.py"
    if not load_helper.exists():
        load_helper_content = f'''"""
Load story graph data for {scenario_name} test.

GIVEN: Story graph data
- Loads story graph JSON
- Provides access to given test data
"""
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directories to path
given_dir = Path(__file__).parent
scenario_dir = given_dir.parent
acceptance_dir = scenario_dir.parent.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(acceptance_dir.parent / "spec_by_example"))

from story_graph_layout_helper import load_story_graph


def get_story_graph() -> Dict[str, Any]:
    """
    Load story graph from given data.
    
    Returns:
        Story graph dictionary
    """
    story_graph_path = given_dir / "{json_filename}"
    return load_story_graph(story_graph_path)


def get_story_graph_path() -> Path:
    """
    Get path to story graph JSON from given data.
    
    Returns:
        Path to story graph JSON file
    """
    return given_dir / "{json_filename}"
'''
        load_helper.write_text(load_helper_content, encoding='utf-8')
        print(f"[OK] Created {load_helper.name}")
    
    # Copy workflow and assertion scripts from simple_story_graph template
    template_scenario = acceptance_dir / "scenarios" / "simple_story_graph"
    
    workflow_template = template_scenario / "2_when" / "render_then_sync_then_render_graph.py"
    workflow_target = when_dir / "render_then_sync_then_render_graph.py"
    if workflow_template.exists() and not workflow_target.exists():
        shutil.copy(str(workflow_template), str(workflow_target))
        print(f"[OK] Copied workflow script")
    
    assertion_template = template_scenario / "3_then" / "assert_story_graph_round_trip.py"
    assertion_target = then_dir / "assert_story_graph_round_trip.py"
    if assertion_template.exists() and not assertion_target.exists():
        shutil.copy(str(assertion_template), str(assertion_target))
        # Update the JSON filename reference
        content = assertion_target.read_text(encoding='utf-8')
        content = content.replace('story-graph-simple.json', json_filename)
        assertion_target.write_text(content, encoding='utf-8')
        print(f"[OK] Copied and updated assertion script")
    
    # Create test orchestrator
    test_file = scenario_dir / "test_render_sync_render_round_trip.py"
    if not test_file.exists():
        test_content = f'''"""
Test render-sync-render round-trip for {scenario_name}.

Given -> When -> Then workflow:
1. Given: Story graph JSON
2. When: Render to DrawIO, sync back to JSON, render again
3. Then: Assert JSONs match and DrawIO layout is preserved
"""
import sys
from pathlib import Path
import subprocess

# Add parent directories to path
test_dir = Path(__file__).parent
acceptance_dir = test_dir.parent.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))

def main():
    """Run the complete test workflow."""
    print(f"\\n{{'='*80}}")
    print("{scenario_name.upper().replace('_', ' ')} ROUND-TRIP TEST")
    print(f"{{'='*80}}")
    
    # Step 1: Given - verify input data exists
    print("\\nGIVEN: Verify input data exists...")
    given_dir = test_dir / "1_given"
    story_graph_path = given_dir / "{json_filename}"
    
    if not story_graph_path.exists():
        print(f"[ERROR] Story graph not found: {{story_graph_path}}")
        return False
    
    print(f"   [OK] Story graph: {{story_graph_path}}")
    
    # Step 2: When - run workflow script
    print("\\nWHEN: Run workflow script (render -> sync -> render)...")
    when_dir = test_dir / "2_when"
    workflow_script = when_dir / "render_then_sync_then_render_graph.py"
    
    if not workflow_script.exists():
        print(f"[ERROR] Workflow script not found: {{workflow_script}}")
        return False
    
    result = subprocess.run(
        [sys.executable, str(workflow_script)],
        cwd=str(when_dir),
        capture_output=False
    )
    
    if result.returncode != 0:
        print(f"[FAIL] Workflow script failed with exit code {{result.returncode}}")
        return False
    
    print("   [OK] Workflow script completed")
    
    # Step 3: Then - run assertions
    print("\\nTHEN: Run assertions...")
    then_dir = test_dir / "3_then"
    assert_script = then_dir / "assert_story_graph_round_trip.py"
    
    if not assert_script.exists():
        print(f"[ERROR] Assertion script not found: {{assert_script}}")
        return False
    
    result = subprocess.run(
        [sys.executable, str(assert_script)],
        cwd=str(then_dir),
        capture_output=False
    )
    
    if result.returncode != 0:
        print(f"[FAIL] Assertions failed with exit code {{result.returncode}}")
        return False
    
    print("\\n" + "="*80)
    print("[OK] All test steps completed successfully!")
    print("="*80)
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\\n[FAIL] Test workflow failed: {{e}}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
'''
        test_file.write_text(test_content, encoding='utf-8')
        print(f"[OK] Created test orchestrator")
    
    print(f"\n[OK] Scenario '{scenario_name}' refactored successfully!")
    print(f"     Next: Review and customize files if needed")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python refactor_scenario_template.py <scenario_name> <descriptive_json_name>")
        print("Example: python refactor_scenario_template.py multiple_epics_features_test story-graph-multiple-epics-features.json")
        sys.exit(1)
    
    scenario_name = sys.argv[1]
    json_filename = sys.argv[2]
    refactor_scenario(scenario_name, json_filename)




