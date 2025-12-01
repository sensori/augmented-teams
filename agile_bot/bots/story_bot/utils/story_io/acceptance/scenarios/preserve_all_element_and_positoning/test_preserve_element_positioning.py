"""
Test preserve element positioning after sync-then-render workflow.

Given -> When -> Then workflow:
1. Given: Input data is there (story graph, DrawIO) - don't extract, it's already there
2. When: Sync graph from DrawIO, then render DrawIO again (test script)
3. Then: Compare expected to actual (DrawIO layout is all we care about, JSON not important)
"""
import sys
from pathlib import Path

# Add parent directories to path
scenario_dir = Path(__file__).parent
acceptance_dir = scenario_dir.parent.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))

def main():
    """Run the complete test workflow."""
    print(f"\n{'='*80}")
    print("PRESERVE ALL ELEMENT AND POSITIONING TEST")
    print(f"{'='*80}")
    
    # Step 1: Given - verify input data exists
    print("\nGIVEN: Verify input data exists...")
    given_dir = scenario_dir / "1_given"
    story_graph_path = given_dir / "story-graph-with-many-users-and-optional-stories.json"
    drawio_path = given_dir / "story-outline-with-complex-custom-positoning.drawio"
    
    if not story_graph_path.exists():
        print(f"[ERROR] Story graph not found: {story_graph_path}")
        return False
    
    if not drawio_path.exists():
        print(f"[ERROR] DrawIO file not found: {drawio_path}")
        return False
    
    print(f"   [OK] Story graph: {story_graph_path}")
    print(f"   [OK] DrawIO file: {drawio_path}")
    
    # Step 2: When - run test script
    print("\nWHEN: Run test script (sync graph and render)...")
    when_dir = scenario_dir / "2_when"
    test_script = when_dir / "sync_graph_then_render_drawio_with_positioning.py"
    
    if not test_script.exists():
        print(f"[ERROR] Test script not found: {test_script}")
        return False
    
    import subprocess
    result = subprocess.run(
        [sys.executable, str(test_script)],
        cwd=str(when_dir),
        capture_output=False
    )
    
    if result.returncode != 0:
        print(f"[FAIL] Test script failed with exit code {result.returncode}")
        return False
    
    print("   [OK] Test script completed")
    
    # Step 3: Then - compare results
    print("\nTHEN: Compare expected to actual...")
    then_dir = scenario_dir / "3_then"
    compare_script = then_dir / "assert_positioning_preserved.py"
    
    if not compare_script.exists():
        print(f"[ERROR] Compare script not found: {compare_script}")
        return False
    
    result = subprocess.run(
        [sys.executable, str(compare_script)],
        cwd=str(then_dir),
        capture_output=False
    )
    
    if result.returncode != 0:
        print(f"[FAIL] Comparison failed with exit code {result.returncode}")
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

