"""
Test orchestrator for couple_of stories_with_acceptance_criteria scenario.

Follows Given-When-Then (BDD) structure:
- GIVEN: Setup and test data from 1_given/
- WHEN: Execute workflow from 2_when/
- THEN: Assert results from 3_then/

Workflow: Render story graph → Sync from DrawIO → Render again
Validates: JSON round-trip, DrawIO elements, layout preservation
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
    """Run the complete test workflow following Given-When-Then pattern."""
    print(f"\n{'='*80}")
    print("COUPLE OF STORIES WITH ACCEPTANCE CRITERIA - ROUND-TRIP TEST")
    print(f"{'='*80}")
    
    # GIVEN: Verify input data exists
    print("\nGIVEN: Verify input data exists...")
    given_dir = test_dir / "1_given"
    story_graph_path = given_dir / "story-graph-complex.json"
    
    if not story_graph_path.exists():
        print(f"[ERROR] Story graph not found: {story_graph_path}")
        return False
    
    # Verify load script exists
    load_script = given_dir / "load_story_graph_data.py"
    if not load_script.exists():
        print(f"[WARN] Load script not found: {load_script}")
    else:
        print(f"   [OK] Load script: {load_script}")
    
    print(f"   [OK] Story graph: {story_graph_path}")
    
    # WHEN: Execute workflow script
    print("\nWHEN: Execute workflow (render -> sync -> render)...")
    when_dir = test_dir / "2_when"
    workflow_script = when_dir / "render_then_sync_then_render_graph.py"
    
    if not workflow_script.exists():
        print(f"[ERROR] Workflow script not found: {workflow_script}")
        return False
    
    print(f"   [INFO] Running: {workflow_script.name}")
    result = subprocess.run(
        [sys.executable, str(workflow_script)],
        cwd=str(when_dir),
        capture_output=False
    )
    
    if result.returncode != 0:
        print(f"[FAIL] Workflow script failed with exit code {result.returncode}")
        return False
    
    print("   [OK] Workflow completed - outputs written to 3_then/")
    
    # THEN: Run assertions
    print("\nTHEN: Assert expected matches actual...")
    then_dir = test_dir / "3_then"
    assert_script = then_dir / "assert_json_drawio_round_trip_validation.py"
    
    if not assert_script.exists():
        print(f"[ERROR] Assertion script not found: {assert_script}")
        return False
    
    # Verify expected files exist
    expected_drawio = then_dir / "expected.drawio"
    expected_json = then_dir / "expected-extracted-story-graph.json"
    if not expected_drawio.exists():
        print(f"[WARN] Expected DrawIO not found: {expected_drawio}")
    if not expected_json.exists():
        print(f"[WARN] Expected JSON not found: {expected_json}")
    
    print(f"   [INFO] Running: {assert_script.name}")
    result = subprocess.run(
        [sys.executable, str(assert_script)],
        cwd=str(then_dir),
        capture_output=False
    )
    
    if result.returncode != 0:
        print(f"[FAIL] Assertions failed with exit code {result.returncode}")
        return False
    
    print("\n" + "="*80)
    print("[OK] All test steps completed successfully!")
    print("="*80)
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Test workflow failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
