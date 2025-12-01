"""
Example: Load and render a story graph from structured.json

Converts format and renders to DrawIO.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from story_io.story_io_diagram import StoryIODiagram


def convert_behavioral_ac_to_steps(story_data):
    """Convert behavioral_ac array to Steps format."""
    if 'behavioral_ac' in story_data and story_data['behavioral_ac']:
        steps = []
        for i, step_text in enumerate(story_data['behavioral_ac'], 1):
            # Determine step type from content
            step_type = "Given"
            step_lower = step_text.lower()
            if step_lower.startswith('when'):
                step_type = "When"
            elif step_lower.startswith('then'):
                step_type = "Then"
            elif step_lower.startswith('and'):
                step_type = steps[-1]['type'] if steps else "Given"
            
            steps.append({
                "description": step_text,
                "type": step_type
            })
        return steps
    return story_data.get('Steps', [])


def adapt_story_graph(data):
    """
    Adapt story graph to our expected format.
    Converts behavioral_ac to Steps, handles empty users arrays, etc.
    """
    adapted = {}
    
    # Copy solution if exists
    if 'solution' in data:
        adapted['solution'] = data['solution']
    
    # Adapt epics
    if 'epics' in data:
        adapted['epics'] = []
        for epic in data['epics']:
            adapted_epic = {
                'name': epic['name'],
                'sequential_order': epic.get('sequential_order')
            }
            
            # Handle users - use epic users if story users is empty
            epic_users = epic.get('users', [])
            
            # Adapt features
            if 'features' in epic:
                adapted_epic['features'] = []
                for feature in epic['features']:
                    adapted_feature = {
                        'name': feature['name'],
                        'sequential_order': feature.get('sequential_order')
                    }
                    
                    # Adapt stories
                    if 'stories' in feature:
                        adapted_feature['stories'] = []
                        for story in feature['stories']:
                            adapted_story = {
                                'name': story['name'],
                                'sequential_order': story.get('sequential_order'),
                                'users': story.get('users', epic_users) if story.get('users') else epic_users,
                                'vertical_order': story.get('vertical_order')
                            }
                            
                            # Convert behavioral_ac to Steps
                            steps = convert_behavioral_ac_to_steps(story)
                            if steps:
                                adapted_story['Steps'] = steps
                            
                            adapted_feature['stories'].append(adapted_story)
                    
                    adapted_epic['features'].append(adapted_feature)
            
            adapted['epics'].append(adapted_epic)
    
    # Adapt increments
    if 'increments' in data:
        adapted['increments'] = []
        for increment in data['increments']:
            adapted_increment = {
                'name': increment['name'],
                'priority': increment.get('priority', 'NEXT')
            }
            
            # Increments can have epics directly
            if 'epics' in increment:
                adapted_increment['epics'] = []
                for epic in increment['epics']:
                    # Same adaptation as main epics
                    adapted_epic = {
                        'name': epic['name'],
                        'sequential_order': epic.get('sequential_order')
                    }
                    epic_users = epic.get('users', [])
                    
                    if 'features' in epic:
                        adapted_epic['features'] = []
                        for feature in epic['features']:
                            adapted_feature = {
                                'name': feature['name'],
                                'sequential_order': feature.get('sequential_order')
                            }
                            
                            if 'stories' in feature:
                                adapted_feature['stories'] = []
                                for story in feature['stories']:
                                    adapted_story = {
                                        'name': story['name'],
                                        'sequential_order': story.get('sequential_order'),
                                        'users': story.get('users', epic_users) if story.get('users') else epic_users,
                                        'vertical_order': story.get('vertical_order')
                                    }
                                    
                                    steps = convert_behavioral_ac_to_steps(story)
                                    if steps:
                                        adapted_story['Steps'] = steps
                                    
                                    adapted_feature['stories'].append(adapted_story)
                            
                            adapted_epic['features'].append(adapted_feature)
                    
                    adapted_increment['epics'].append(adapted_epic)
            
            adapted['increments'].append(adapted_increment)
    
    return adapted


def main():
    """Load structured.json and render to DrawIO."""
    # Path to the structured.json file (relative to workspace root)
    # From story_io/render_example.py -> story_io -> src -> story_bot -> bots -> agile_bot -> workspace root
    workspace_root = Path(__file__).parent.parent.parent.parent.parent.parent
    structured_path = workspace_root / "demo" / "cheap_wealth_online" / "docs" / "stories" / "structured.json"
    
    # Also try direct path from workspace root if provided as argument
    if len(sys.argv) > 1:
        structured_path = Path(sys.argv[1])
    
    if not structured_path.exists():
        print(f"Error: File not found: {structured_path}")
        print(f"Current working directory: {Path.cwd()}")
        return 1
    
    print(f"Loading: {structured_path}")
    
    # Load and adapt the story graph
    with open(structured_path, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    print(f"Original epics: {len(original_data.get('epics', []))}")
    print(f"Original increments: {len(original_data.get('increments', []))}")
    
    # Adapt format
    adapted_data = adapt_story_graph(original_data)
    
    # Save adapted version for reference
    adapted_path = structured_path.parent / "structured_adapted.json"
    with open(adapted_path, 'w', encoding='utf-8') as f:
        json.dump(adapted_data, f, indent=2, ensure_ascii=False)
    print(f"Adapted format saved to: {adapted_path}")
    
    # Render outline
    output_path = structured_path.parent / "story-map-outline.drawio"
    print(f"\nRendering to: {output_path}")
    
    result = StoryIODiagram.render_outline_from_graph(
        story_graph=adapted_data,
        output_path=output_path
    )
    
    print(f"\n[OK] Render complete!")
    print(f"Output: {output_path}")
    print(f"Epics: {result['summary'].get('epics', 0)}")
    
    # Optionally render with increments
    if adapted_data.get('increments'):
        output_increments = structured_path.parent / "story-map-increments.drawio"
        print(f"\nRendering with increments to: {output_increments}")
        
        result_increments = StoryIODiagram.render_increments_from_graph(
            story_graph=adapted_data,
            output_path=output_increments
        )
        
        print(f"[OK] Increments render complete!")
        print(f"Output: {output_increments}")
        print(f"Epics: {result_increments['summary'].get('epics', 0)}")
        print(f"Increments: {result_increments['summary'].get('increments', 0)}")
    
    print(f"\n{'='*80}")
    print("Next steps:")
    print(f"1. Open {output_path} in DrawIO to verify")
    print(f"2. Check {adapted_path} to see adapted format")
    print(f"{'='*80}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

