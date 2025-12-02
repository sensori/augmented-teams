"""
Simple script to extract story graph JSON from DrawIO diagrams.

Usage:
    python extract_story_graph.py <input.drawio> [output.json] [--exploration]

Example:
    python extract_story_graph.py story-map-outline.drawio
    python extract_story_graph.py story-map-outline.drawio extracted.json
    python extract_story_graph.py story-map-outline.drawio extracted.json --exploration

Options:
    --exploration    Extract in exploration mode (with acceptance criteria)
    --outline        Extract in outline mode (default, without acceptance criteria)
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from story_io.story_map_drawio_synchronizer import StoryMapDrawIOSynchronizer


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python extract_story_graph.py <input.drawio> [output.json] [--exploration]")
        print("\nExample:")
        print("  python extract_story_graph.py story-map-outline.drawio")
        print("  python extract_story_graph.py story-map-outline.drawio extracted.json")
        print("  python extract_story_graph.py story-map-outline.drawio extracted.json --exploration")
        print("\nOptions:")
        print("  --exploration    Extract in exploration mode (with acceptance criteria)")
        print("  --outline        Extract in outline mode (default, without acceptance criteria)")
        sys.exit(1)
    
    # Get input file
    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    
    # Parse arguments
    is_exploration = False
    output_path = None
    
    for arg in sys.argv[2:]:
        if arg == '--exploration':
            is_exploration = True
        elif arg == '--outline':
            is_exploration = False
        elif not output_path:
            output_path = Path(arg)
    
    # Determine output path if not specified
    if not output_path:
        if is_exploration:
            output_path = input_path.parent / "story-graph-exploration.json"
        else:
            output_path = input_path.parent / "story-graph-outline.json"
    
    mode_str = "exploration" if is_exploration else "outline"
    print(f"Extracting from: {input_path}")
    print(f"Mode: {mode_str}")
    
    # Extract
    synchronizer = StoryMapDrawIOSynchronizer(str(input_path))
    story_graph = synchronizer.extract_story_graph(is_exploration=is_exploration)
    
    # Save
    print(f"Saving to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(story_graph, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n[SUCCESS] Extracted!")
    print(f"Output file: {output_path}")
    
    if 'epics' in story_graph:
        epics_count = len(story_graph['epics'])
        print(f"Epics: {epics_count}")
        
        # Count features and stories
        features_count = 0
        stories_count = 0
        for epic in story_graph['epics']:
            if 'features' in epic:
                features_count += len(epic['features'])
                for feature in epic['features']:
                    if 'story_groups' in feature:
                        for group in feature['story_groups']:
                            stories_count += len(group.get('stories', []))
                    if 'sub_epics' in feature:
                        for sub_epic in feature['sub_epics']:
                            if 'story_groups' in sub_epic:
                                for group in sub_epic['story_groups']:
                                    stories_count += len(group.get('stories', []))
        
        print(f"Features: {features_count}")
        print(f"Stories: {stories_count}")
    
    if 'increments' in story_graph:
        increments_count = len(story_graph['increments'])
        print(f"Increments: {increments_count}")
    
    print(f"\nExtracted story graph in {mode_str} mode.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

