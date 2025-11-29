"""
Test render-sync-render round-trip for multiple_users_story_graph.

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
    print(f"\n{'='*80}")
    print("MULTIPLE USERS STORY GRAPH ROUND-TRIP TEST")
    print(f"{'='*80}")
    
    # Step 1: Given - verify input data exists
    print("\nGIVEN: Verify input data exists...")
    given_dir = test_dir / "1_given"
    story_graph_path = given_dir / "story-graph-multiple-users.json"
    
    if not story_graph_path.exists():
        print(f"[ERROR] Story graph not found: {story_graph_path}")
        return False
    
    print(f"   [OK] Story graph: {story_graph_path}")
    
    # Step 2: When - run workflow script
    print("\nWHEN: Run workflow script (render -> sync -> render)...")
    when_dir = test_dir / "2_when"
    workflow_script = when_dir / "render_then_sync_then_render_graph.py"
    
    if not workflow_script.exists():
        print(f"[ERROR] Workflow script not found: {workflow_script}")
        return False
    
    result = subprocess.run(
        [sys.executable, str(workflow_script)],
        cwd=str(when_dir),
        capture_output=False
    )
    
    if result.returncode != 0:
        print(f"[FAIL] Workflow script failed with exit code {result.returncode}")
        return False
    
    print("   [OK] Workflow script completed")
    
    # Step 3: Then - run assertions
    print("\nTHEN: Run assertions...")
    then_dir = test_dir / "3_then"
    assert_script = then_dir / "assert_story_graph_round_trip.py"
    
    if not assert_script.exists():
        print(f"[ERROR] Assertion script not found: {assert_script}")
        return False
    
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
