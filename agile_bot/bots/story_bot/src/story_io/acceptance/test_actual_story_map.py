"""
Test to validate the actual story-io-story-map-outline.drawio file for positioning issues.

This test checks the actual rendered story map for epic and feature positioning problems.
"""

import sys
from pathlib import Path
from test_epic_feature_positioning import PositioningValidator

# Add parent directories to path
acceptance_dir = Path(__file__).parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))


def test_actual_story_map():
    """Test the actual story-io-story-map-outline.drawio file."""
    print("="*80)
    print("Testing Actual Story Map Positioning")
    print("="*80)
    
    # Path to the actual story map
    story_map_path = acceptance_dir.parent.parent.parent / "docs" / "stories" / "map" / "story-io-story-map-outline.drawio"
    
    if not story_map_path.exists():
        print(f"[ERROR] Story map file not found: {story_map_path}")
        return False
    
    print(f"\n1. Loading story map: {story_map_path}")
    
    # Validate positioning
    print(f"\n2. Validating epic and feature positioning...")
    validator = PositioningValidator(story_map_path)
    
    results = validator.validate_all()
    
    print(f"\n   Epics found: {results['epics_count']}")
    print(f"   Features found: {results['features_count']}")
    print(f"   Stories found: {results['stories_count']}")
    
    # Print validation results
    print(f"\n3. Validation Results:")
    print(f"   {'='*76}")
    
    all_passed = True
    
    # Feature vertical stacking
    stack_result = results['validations']['feature_vertical_stack']
    if stack_result['passed']:
        print(f"   [OK] Feature vertical stacking: PASSED")
    else:
        all_passed = False
        print(f"   [FAIL] Feature vertical stacking: FAILED ({len(stack_result['errors'])} errors)")
        for error in stack_result['errors'][:5]:  # Show first 5
            print(f"      - {error['feature1_name']} overlaps {error['feature2_name']} by {error['overlap_amount']:.1f}px")
        if len(stack_result['errors']) > 5:
            print(f"      ... and {len(stack_result['errors']) - 5} more overlaps")
        
        # Show warnings
        if stack_result.get('warnings'):
            print(f"   [WARN] Close spacing warnings: {len(stack_result['warnings'])}")
    
    # Epic width
    width_result = results['validations']['epic_width']
    if width_result['passed']:
        print(f"   [OK] Epic width validation: PASSED")
    else:
        all_passed = False
        print(f"   [FAIL] Epic width validation: FAILED ({len(width_result['errors'])} errors)")
        for error in width_result['errors'][:5]:  # Show first 5
            print(f"      - Epic '{error['epic_name']}' width {error['epic_width']:.1f}px is too narrow")
            print(f"        Required: {error['min_required_width']:.1f}px (max feature: {error['max_feature_width']:.1f}px)")
            print(f"        Deficit: {error['deficit']:.1f}px")
        if len(width_result['errors']) > 5:
            print(f"      ... and {len(width_result['errors']) - 5} more epic width issues")
    
    # Epic horizontal separation
    separation_result = results['validations']['epic_horizontal_separation']
    if separation_result['passed']:
        print(f"   [OK] Epic horizontal separation: PASSED")
    else:
        all_passed = False
        print(f"   [FAIL] Epic horizontal separation: FAILED ({len(separation_result['errors'])} errors)")
        for error in separation_result['errors'][:5]:  # Show first 5
            print(f"      - Epic '{error['epic1_name']}' overlaps '{error['epic2_name']}' by {error['overlap_amount']:.1f}px")
        if len(separation_result['errors']) > 5:
            print(f"      ... and {len(separation_result['errors']) - 5} more overlaps")
    
    # Save detailed results
    output_dir = acceptance_dir / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "actual_story_map_validation.json"
    import json
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n4. Detailed results saved to: {results_path}")
    
    print(f"\n{'='*80}")
    if all_passed:
        print(f"[OK] All validations passed!")
    else:
        print(f"[FAIL] Some validations failed. See details above and in {results_path}")
        print(f"\n   To fix issues:")
        print(f"   1. Review the detailed results in {results_path}")
        print(f"   2. Check the DrawIO file for overlapping elements")
        print(f"   3. Re-render the story map after fixing the renderer")
    print(f"{'='*80}\n")
    
    return all_passed


if __name__ == "__main__":
    success = test_actual_story_map()
    sys.exit(0 if success else 1)




