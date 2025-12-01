"""
Test layout position preservation after sync-then-render workflow.

Given -> When -> Then workflow:
1. Given: Original DrawIO file with layout
2. When: Sync DrawIO to extract story graph and layout, then render again
3. Then: Assert that component positions are preserved
"""
import sys
from pathlib import Path
import subprocess

# Add parent directories to path
test_dir = Path(__file__).parent
acceptance_dir = test_dir.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))

def main():
    """Run the complete test workflow."""
    print(f"\n{'='*80}")
    print("LAYOUT POSITION PRESERVATION TEST")
    print(f"{'='*80}")
    
    # Step 1: Given - verify input data exists
    print("\nGIVEN: Verify input data exists...")
    given_dir = test_dir / "1_given"
    
    # Import given helper to check if file exists
    sys.path.insert(0, str(given_dir))
    import importlib.util
    spec = importlib.util.spec_from_file_location("load_drawio_data", given_dir / "load_drawio_data.py")
    given_data = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(given_data)
    
    original_drawio_path = given_data.get_original_drawio_path()
    
    if not original_drawio_path.exists():
        print(f"[ERROR] Original DrawIO not found: {original_drawio_path}")
        print(f"       Please ensure the DrawIO file exists in one of the expected locations")
        return False
    
    print(f"   [OK] Original DrawIO: {original_drawio_path}")
    
    # Step 2: When - run workflow script
    print("\nWHEN: Run workflow script (sync -> render)...")
    when_dir = test_dir / "2_when"
    workflow_script = when_dir / "sync_then_render_with_layout.py"
    
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
    assert_script = then_dir / "assert_layout_positions_preserved.py"
    
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




