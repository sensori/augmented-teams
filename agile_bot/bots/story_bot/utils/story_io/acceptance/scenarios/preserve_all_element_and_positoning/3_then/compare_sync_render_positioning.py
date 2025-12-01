"""
Compare sync-then-render positioning preservation.

THEN: Compare expected to actual (DrawIO layout is all we care about, JSON not important)

UNIQUE TO THIS TEST:
- Tests sync-then-render workflow (sync from DrawIO → render with extracted layout)
- Compares single render: expected vs actual (after sync-then-render)
- Validates that users are positioned over stories correctly
- Validates that all elements preserve positioning after sync-then-render cycle
- Tests positioning preservation for complex diagrams with many users and stories
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

def assert_positioning_preserved():
    """Assert that positioning is preserved after sync-then-render workflow."""
    print(f"\n{'='*80}")
    print("THEN: Compare expected to actual (DrawIO layout only)")
    print("      Users should be over stories and stories positioned correctly")
    print(f"{'='*80}")
    
    # Expected file
    expected_path = test_dir / "expected-story-outline.drawio"
    
    # Actual file
    actual_path = test_dir / "actual-story-outline.drawio"
    
    if not expected_path.exists():
        print(f"[ERROR] Expected file not found: {expected_path}")
        return False
    
    if not actual_path.exists():
        print(f"[ERROR] Actual file not found: {actual_path}")
        return False
    
    # Compare expected with actual
    print(f"\nComparing expected with actual...")
    result = compare_drawios(expected_path, actual_path)
    if result['match']:
        print(f"   [OK] Expected matches actual!")
        print(f"   [OK] Users are over stories and stories are positioned correctly")
    else:
        print(f"   [FAIL] Expected doesn't match actual: {result['message']}")
        if result.get('differences'):
            print(f"   Differences: {len(result['differences'])}")
            for diff in result['differences'][:20]:  # Show first 20 differences
                print(f"      - {diff}")
            if len(result['differences']) > 20:
                print(f"      ... and {len(result['differences']) - 20} more differences")
    
    print(f"\n{'='*80}")
    if result['match']:
        print("[OK] All comparisons passed!")
        print("[OK] Positioning is correct!")
    else:
        print("[FAIL] Some comparisons failed!")
        print("[FAIL] Positioning may be incorrect!")
    print(f"{'='*80}")
    
    return result['match']

if __name__ == '__main__':
    try:
        success = assert_positioning_preserved()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Assertion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

