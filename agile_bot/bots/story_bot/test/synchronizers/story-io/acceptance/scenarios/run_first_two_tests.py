#!/usr/bin/env python3
"""
Run the first two converted tests: simple_story_graph and single_epic_story_graph.
"""
import sys
from pathlib import Path
import subprocess

# Get the scenarios directory
scenarios_dir = Path(__file__).parent

def run_test(test_name):
    """Run a single test and return success status."""
    print(f"\n{'='*80}")
    print(f"RUNNING TEST: {test_name}")
    print(f"{'='*80}\n")
    
    test_dir = scenarios_dir / test_name
    test_script = test_dir / "test_render_sync_render_round_trip.py"
    
    if not test_script.exists():
        print(f"[ERROR] Test script not found: {test_script}")
        return False
    
    # Run the test
    result = subprocess.run(
        [sys.executable, str(test_script)],
        cwd=str(test_dir),
        capture_output=False,
        text=True
    )
    
    success = result.returncode == 0
    
    print(f"\n{'='*80}")
    if success:
        print(f"[PASS] {test_name}")
    else:
        print(f"[FAIL] {test_name} (exit code: {result.returncode})")
    print(f"{'='*80}\n")
    
    return success

def main():
    """Run both tests."""
    print("\n" + "="*80)
    print("TESTING FIRST TWO CONVERTED SCENARIOS")
    print("="*80)
    
    tests = [
        "simple_story_graph",
        "single_epic_story_graph"
    ]
    
    results = {}
    
    for test_name in tests:
        results[test_name] = run_test(test_name)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("="*80)
    
    if all_passed:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
























































