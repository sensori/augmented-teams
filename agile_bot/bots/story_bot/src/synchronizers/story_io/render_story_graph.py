"""
Simple script to render any story graph JSON to DrawIO.

Usage:
    python render_story_graph.py <story_graph.json> [output.drawio]

Example:
    python render_story_graph.py demo/cheap_wealth_online/docs/stories/structured.json
"""

import json
import sys
from pathlib import Path

from .story_io_diagram import StoryIODiagram


def convert_behavioral_ac_to_steps(story_data):
    """Convert behavioral_ac array to Steps format."""
    if 'behavioral_ac' in story_data and story_data['behavioral_ac']:
        steps = []
        for step_text in story_data['behavioral_ac']:
            step_type = "Given"
            step_lower = step_text.lower()
            if step_lower.startswith('when'):
                step_type = "When"
            elif step_lower.startswith('then'):
                step_type = "Then"
            elif step_lower.startswith('and') and steps:
                step_type = steps[-1]['type']
            
            steps.append({
                "description": step_text,
                "type": step_type
            })
        return steps
    return story_data.get('Steps', [])


def adapt_story_graph(data):
    """Adapt story graph to our expected format."""
    adapted = {}
    
    if 'solution' in data:
        adapted['solution'] = data['solution']
    
    if 'epics' in data:
        adapted['epics'] = []
        for epic in data['epics']:
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
            
            adapted['epics'].append(adapted_epic)
    
    if 'increments' in data:
        adapted['increments'] = []
        for increment in data['increments']:
            adapted_increment = {
                'name': increment['name'],
                'priority': increment.get('priority', 'NEXT')
            }
            
            if 'epics' in increment:
                adapted_increment['epics'] = []
                for epic in increment['epics']:
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
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python render_story_graph.py <story_graph.json> [output.drawio]")
        print("\nExample:")
        print("  python render_story_graph.py demo/cheap_wealth_online/docs/stories/structured.json")
        sys.exit(1)
    
    # Get input file
    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    
    # Determine output path
    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])
    else:
        output_path = input_path.parent / "story-map-outline.drawio"
    
    print(f"Loading: {input_path}")
    
    # Load and adapt
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    adapted_data = adapt_story_graph(data)
    
    # Render
    print(f"Rendering to: {output_path}")
    result = StoryIODiagram.render_outline_from_graph(
        story_graph=adapted_data,
        output_path=output_path
    )
    
    print(f"\n[SUCCESS] Rendered!")
    print(f"Output file: {output_path}")
    print(f"Epics: {result['summary'].get('epics', 0)}")
    print(f"\nOpen {output_path} in DrawIO to verify.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

