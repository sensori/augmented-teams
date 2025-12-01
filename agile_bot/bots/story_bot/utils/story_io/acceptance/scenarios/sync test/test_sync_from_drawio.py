"""
Test sync from DrawIO to JSON.

Given-When-Then workflow:
1. Given: DrawIO file and expected JSON
2. When: Sync DrawIO to JSON
3. Then: Assert extracted JSON matches expected JSON
"""
import sys
import io
from pathlib import Path
import subprocess

# Fix encoding for Windows
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
                pass
    def flush(self):
        for f in self.files:
            try:
                f.flush()
            except (ValueError, OSError):
                pass

sys.stdout = TeeOutput(sys.stdout, log_handle)
sys.stderr = TeeOutput(sys.stderr, log_handle)

def main():
    """Run the complete test workflow."""
    print(f"\n{'='*80}", flush=True)
    print("SYNC FROM DRAWIO TO JSON TEST", flush=True)
    print(f"{'='*80}", flush=True)
    
    # Step 1: Given - verify input data exists
    print("\nGIVEN: Verify input data exists...", flush=True)
    given_dir = test_dir / "1_given"
    drawio_path = given_dir / "expected- story-map-outline.drawio"
    expected_json_path = given_dir / "story-graph.json"
    
    if not drawio_path.exists():
        print(f"[ERROR] DrawIO file not found: {drawio_path}")
        return False
    
    if not expected_json_path.exists():
        print(f"[ERROR] Expected JSON not found: {expected_json_path}")
        return False
    
    print(f"   [OK] DrawIO file: {drawio_path}", flush=True)
    print(f"   [OK] Expected JSON: {expected_json_path}", flush=True)
    
    # Step 2: When - run sync script
    print("\nWHEN: Run sync script (DrawIO → JSON)...", flush=True)
    when_dir = test_dir / "2_when"
    sync_script = when_dir / "sync_from_drawio.py"
    
    if not sync_script.exists():
        print(f"[ERROR] Sync script not found: {sync_script}")
        return False
    
    result = subprocess.run(
        [sys.executable, '-u', str(sync_script)],
        cwd=str(when_dir),
        capture_output=False,
        text=True,
        bufsize=0
    )
    
    if result.returncode != 0:
        print(f"[FAIL] Sync script failed with exit code {result.returncode}")
        return False
    
    print("   [OK] Sync script completed", flush=True)
    
    # Step 3: Then - run assertions
    print("\nTHEN: Run assertions...", flush=True)
    then_dir = test_dir / "3_then"
    assert_script = then_dir / "assert_extracted_matches_expected.py"
    
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
            pass
    sys.exit(0 if success else 1)

