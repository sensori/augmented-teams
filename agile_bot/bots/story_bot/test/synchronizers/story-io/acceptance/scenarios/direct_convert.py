#!/usr/bin/env python3
"""Directly convert files - load, convert, save."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from convert_to_new_format import convert_story_graph

def convert_file_direct(file_path):
    """Convert file directly."""
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"ERROR: {file_path} not found")
        return False
    
    print(f"Converting {file_path.name}...")
    
    # Load
    with open(file_path, 'r', encoding='utf-8') as f:
        old_graph = json.load(f)
    
    # Convert
    new_graph = convert_story_graph(old_graph)
    
    # Save
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(new_graph, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Converted {file_path.name}")
    return True

if __name__ == "__main__":
    scenarios_dir = Path(__file__).parent
    
    files_to_convert = [
        scenarios_dir / "couple_of stories_with_acceptance_criteria/1_given/story-graph-complex.json",
        scenarios_dir / "different_story_types_story_graph/1_given/story-graph-different-story-types.json",
        scenarios_dir / "exploration_renders_acceptance_criteria/1_given/story-graph-with-acceptance-criteria.json",
        scenarios_dir / "incomplete_with_estimates_story_graph/1_given/story-graph-incomplete-with-estimates.json",
        scenarios_dir / "multiple_epics_features_test/1_given/story-graph-multiple-epics-features.json",
        scenarios_dir / "optional_vs_sequential_story_graph/1_given/story-graph-optional-vs-sequential.json",
    ]
    
    print("Direct conversion of test files...")
    print("=" * 80)
    
    for file_path in files_to_convert:
        convert_file_direct(file_path)
    
    print("=" * 80)
    print("Done!")
























































