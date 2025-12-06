#!/usr/bin/env python3
"""Batch convert all test input files to new format."""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from convert_to_new_format import convert_file

def main():
    """Convert all test input files."""
    scenarios_dir = Path(__file__).parent
    
    test_files = [
        "couple_of stories_with_acceptance_criteria/1_given/story-graph-complex.json",
        "different_story_types_story_graph/1_given/story-graph-different-story-types.json",
        "exploration_renders_acceptance_criteria/1_given/story-graph-with-acceptance-criteria.json",
        "incomplete_with_estimates_story_graph/1_given/story-graph-incomplete-with-estimates.json",
        "multiple_epics_features_test/1_given/story-graph-multiple-epics-features.json",
        "optional_vs_sequential_story_graph/1_given/story-graph-optional-vs-sequential.json",
    ]
    
    print("Batch converting test files to new format...")
    print("=" * 80)
    
    for test_file in test_files:
        file_path = scenarios_dir / test_file
        if file_path.exists():
            print(f"\nConverting: {test_file}")
            try:
                convert_file(file_path)
                print(f"  ✓ Successfully converted")
            except Exception as e:
                print(f"  ✗ Error: {e}")
        else:
            print(f"\n⚠ File not found: {test_file}")
    
    print("\n" + "=" * 80)
    print("Batch conversion complete!")

if __name__ == "__main__":
    main()
























































