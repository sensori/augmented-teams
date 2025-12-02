"""
Test render-sync-render round-trip for nested workflow story graph.

Given -> When -> Then workflow:
1. Given: Story graph JSON with nested stories
2. When: Render to DrawIO, sync back to JSON, render again
3. Then: Assert JSONs match and DrawIO layout is preserved
"""
import sys
import io
from pathlib import Path
import subprocess

# Fix encoding for Windows - ensure output is visible and unbuffered
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Set up logging to file
test_dir = Path(__file__).parent
log_file = test_dir / "test_output.log"
log_handle = open(log_file, 'w', encoding='utf-8', buffering=1)

class TeeOutput:
    """Tee output to both stdout and file."""
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            try:
                f.write(obj)
                f.flush()
            except (ValueError, OSError):
                # File may be closed, ignore
                pass
    def flush(self):
        for f in self.files:
            try:
                f.flush()
            except (ValueError, OSError):
                # File may be closed, ignore
                pass

sys.stdout = TeeOutput(sys.stdout, log_handle)
sys.stderr = TeeOutput(sys.stderr, log_handle)

# Add parent directories to path (test_dir already set above)
acceptance_dir = test_dir.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))

def main():
    """Run the complete test workflow."""
    print(f"\n{'='*80}", flush=True)
    print("NESTED WORKFLOW STORY GRAPH ROUND-TRIP TEST", flush=True)
    print(f"{'='*80}", flush=True)
    
    # Step 1: Given - verify input data exists
    print("\nGIVEN: Verify input data exists...", flush=True)
    given_dir = test_dir / "1_given"
    story_graph_path = given_dir / "story-graph.json"
    
    if not story_graph_path.exists():
        print(f"[ERROR] Story graph not found: {story_graph_path}")
        return False
    
    print(f"   [OK] Story graph: {story_graph_path}", flush=True)
    
    # Step 2: When - run workflow script
    print("\nWHEN: Run workflow script (render -> sync -> render)...", flush=True)
    when_dir = test_dir / "2_when"
    workflow_script = when_dir / "render_then_sync_then_render_graph.py"
    
    if not workflow_script.exists():
        print(f"[ERROR] Workflow script not found: {workflow_script}")
        return False
    
    result = subprocess.run(
        [sys.executable, '-u', str(workflow_script)],
        cwd=str(when_dir),
        capture_output=False,
        text=True,
        bufsize=0
    )
    
    if result.returncode != 0:
        print(f"[FAIL] Workflow script failed with exit code {result.returncode}")
        return False
    
    print("   [OK] Workflow script completed", flush=True)
    
    # Step 3: Then - run assertions
    print("\nTHEN: Run assertions...", flush=True)
    then_dir = test_dir / "3_then"
    assert_script = then_dir / "assert_story_graph_round_trip.py"
    
    if not assert_script.exists():
        print(f"[ERROR] Assertion script not found: {assert_script}")
        return False
    
    result = subprocess.run(
        [sys.executable, '-u', str(assert_script)],
        cwd=str(then_dir),
        capture_output=False,
        text=True,
        bufsize=0
    )
    
    if result.returncode != 0:
        print(f"[FAIL] Assertions failed with exit code {result.returncode}")
        return False
    
    print("\n" + "="*80, flush=True)
    print("[OK] All test steps completed successfully!", flush=True)
    print("="*80, flush=True)
    return True

if __name__ == '__main__':
    success = False
    try:
        success = main()
    except Exception as e:
        print(f"\n[FAIL] Test workflow failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    finally:
        try:
            if 'log_handle' in globals() and log_handle:
                log_handle.close()
        except Exception:
            pass  # Ignore errors during cleanup
    sys.exit(0 if success else 1)

