"""
Assert layout preservation after exploration render workflow.

THEN: Assert expected matches actual (DrawIO layout is all we care about, JSON not important)

UNIQUE TO THIS ASSERTION:
- Asserts exploration rendering workflow (render → sync → render with layout)
- Asserts 2 renders: first (no layout) vs second (with layout)
- Also performs round-trip assertion to verify layout preservation
- Asserts that exploration rendering correctly preserves layout when re-rendering
"""
import sys
from pathlib import Path

# Add parent directories to path
test_dir = Path(__file__).parent
acceptance_dir = test_dir.parent.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(acceptance_dir))

from drawio_comparison import compare_drawios

def assert_layout_preserved():
    """Assert that layout is preserved after exploration render workflow."""
    print(f"\n{'='*80}")
    print("THEN: Compare expected to actual (DrawIO layout only)")
    print(f"{'='*80}")
    
    # Expected file
    expected_path = test_dir / "expected-story-exploration.drawio"
    
    # Actual files
    actual_first_path = test_dir / "actual-first-render-story-exploration.drawio"
    actual_second_path = test_dir / "actual-second-render-story-exploration.drawio"
    
    if not expected_path.exists():
        print(f"[ERROR] Expected file not found: {expected_path}")
        return False
    
    if not actual_first_path.exists():
        print(f"[ERROR] Actual first render not found: {actual_first_path}")
        return False
    
    if not actual_second_path.exists():
        print(f"[ERROR] Actual second render not found: {actual_second_path}")
        return False
    
    all_passed = True
    
    # Compare expected with second render (this is the one that should match)
    print(f"\n1. Comparing expected with second render (with layout)...")
    result2 = compare_drawios(expected_path, actual_second_path)
    if result2['match']:
        print(f"   [OK] Expected matches second render!")
    else:
        print(f"   [FAIL] Expected doesn't match second render: {result2['message']}")
        if result2.get('differences'):
            print(f"   Differences: {len(result2['differences'])}")
            for diff in result2['differences'][:10]:
                print(f"      - {diff}")
        all_passed = False
    
    # Also compare first and second render (round-trip test)
    print(f"\n2. Comparing first render with second render (round-trip)...")
    result_roundtrip = compare_drawios(actual_first_path, actual_second_path)
    if result_roundtrip['match']:
        print(f"   [OK] First render matches second render (round-trip)!")
    else:
        print(f"   [INFO] First render differs from second render (expected - layout applied): {result_roundtrip['message']}")
        if result_roundtrip.get('differences'):
            print(f"   Differences: {len(result_roundtrip['differences'])}")
            # This is expected - first render has no layout, second has layout
    
    print(f"\n{'='*80}")
    if all_passed:
        print("[OK] All comparisons passed!")
    else:
        print("[FAIL] Some comparisons failed!")
    print(f"{'='*80}")
    
    return all_passed

if __name__ == '__main__':
    try:
        success = assert_layout_preserved()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Assertion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

