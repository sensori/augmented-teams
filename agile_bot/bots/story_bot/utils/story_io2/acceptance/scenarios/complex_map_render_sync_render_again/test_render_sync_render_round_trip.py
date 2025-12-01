"""
Test Orchestrator: Render → Sync → Render Round-Trip Test

Follows Given-When-Then pattern:
- GIVEN: Story graph JSON in 1_given/
- WHEN: Execute render → sync → render workflow
- THEN: Assert results match expected
"""

import sys
import io
from pathlib import Path

# Fix encoding for Windows - ensure output is visible and unbuffered
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)


def main():
    """Run the round-trip test."""
    scenario_dir = Path(__file__).parent
    given_dir = scenario_dir / '1_given'
    when_dir = scenario_dir / '2_when'
    then_dir = scenario_dir / '3_then'
    
    # Set up test output file
    test_output_file = scenario_dir / 'test_output.log'
    test_output_file.write_text('', encoding='utf-8')
    
    def log(msg):
        """Log message to both stdout and file."""
        # Replace Unicode characters with ASCII for better compatibility
        safe_msg = msg.replace('\u2713', '[OK]').replace('\u2717', '[FAIL]').replace('\u274c', '[ERROR]')
        print(safe_msg)
        with open(test_output_file, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    
    log("=" * 80)
    log("RENDER → SYNC → RENDER ROUND-TRIP TEST")
    log("=" * 80)
    
    # GIVEN: Verify input data exists
    log("\n[GIVEN] Verifying input data...")
    input_json = given_dir / 'story-graph.json'
    
    if not input_json.exists():
        log(f"[ERROR] Input JSON not found: {input_json}")
        sys.exit(1)
    
    log(f"  [OK] Found input JSON: {input_json}")
    
    # WHEN: Execute workflow
    log("\n[WHEN] Executing render → sync → render workflow...")
    workflow_script = when_dir / 'render_then_sync_then_render.py'
    
    if not workflow_script.exists():
        log(f"[ERROR] Workflow script not found: {workflow_script}")
        sys.exit(1)
    
    import subprocess
    result = subprocess.run(
        [sys.executable, str(workflow_script)],
        cwd=str(scenario_dir),
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    
    if result.returncode != 0:
        log("[ERROR] Workflow execution failed")
        log(result.stdout)
        log(result.stderr)
        sys.exit(1)
    
    log(result.stdout)
    
    # THEN: Run assertions
    log("\n[THEN] Running assertions...")
    assert_script = then_dir / 'assert_round_trip.py'
    
    if not assert_script.exists():
        log(f"[ERROR] Assertion script not found: {assert_script}")
        sys.exit(1)
    
    result = subprocess.run(
        [sys.executable, str(assert_script)],
        cwd=str(scenario_dir),
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    
    log(result.stdout)
    if result.stderr:
        log(result.stderr)
    
    log(f"\nTest output written to: {test_output_file}")
    sys.exit(result.returncode)


if __name__ == '__main__':
    main()
