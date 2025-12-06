"""
Compare rendered diagram to expected.

THEN: Compare actual rendered diagram to expected diagram

WHAT THIS TEST DOES:
- Compares the actual rendered DrawIO diagram to the expected diagram
- Reports how close the actual is to the expected
- Shows differences in element positioning, structure, and content
"""
import sys
from pathlib import Path

# Add parent directories to path
then_dir = Path(__file__).parent
scenario_dir = then_dir.parent
acceptance_dir = scenario_dir.parent.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(acceptance_dir.parent / "spec_by_example"))
sys.path.insert(0, str(scenario_dir.parent))  # Add scenarios directory for drawio_comparison

from drawio_comparison import compare_drawios

def compare_rendered_to_expected():
    """Compare rendered diagram to expected diagram."""
    print(f"\n{'='*80}")
    print("THEN: Compare actual rendered diagram to expected")
    print("      How close is the rendered diagram to the expected?")
    print(f"{'='*80}")
    
    # Expected file
    expected_path = then_dir / "expected-story-outline.drawio"
    
    # Actual file (rendered in 2_when)
    actual_path = then_dir / "actual-story-outline.drawio"
    
    if not expected_path.exists():
        print(f"[WARN] Expected file not found: {expected_path}")
        print(f"[INFO] If this is the first run, create expected file from actual")
        print(f"[INFO] Actual file saved to: {actual_path}")
        return True  # Don't fail if expected doesn't exist yet
    
    if not actual_path.exists():
        print(f"[ERROR] Actual file not found: {actual_path}")
        print(f"[INFO] Run 2_when script first to generate actual diagram")
        return False
    
    # Compare expected with actual
    print(f"\nComparing expected with actual...")
    print(f"Expected: {expected_path}")
    print(f"Actual:   {actual_path}")
    
    result = compare_drawios(expected_path, actual_path)
    
    if result['match']:
        print(f"\n   [OK] Diagrams match!")
        print(f"   [OK] Rendered diagram is identical to expected")
    else:
        print(f"\n   [DIFF] Diagrams differ: {result['message']}")
        if result.get('differences'):
            print(f"\n   Found {len(result['differences'])} differences:")
            for i, diff in enumerate(result['differences'][:30], 1):  # Show first 30 differences
                print(f"      {i}. {diff}")
            if len(result['differences']) > 30:
                print(f"      ... and {len(result['differences']) - 30} more differences")
        print(f"\n   [INFO] Review differences to see how close actual is to expected")
    
    print(f"\n{'='*80}")
    if result['match']:
        print("[OK] Comparison passed - diagrams match!")
    else:
        print("[DIFF] Comparison shows differences - review to assess closeness")
    print(f"{'='*80}")
    
    return result['match']

if __name__ == '__main__':
    try:
        success = compare_rendered_to_expected()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Comparison failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

