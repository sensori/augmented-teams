"""
Render story graph increments to text format.
Shows increments with their stories organized by epic/sub-epic.
"""
import json
from pathlib import Path
import sys


def render_story(story, indent_level):
    """Render a single story in increment"""
    indent = "    " * indent_level
    users = story.get('users', [])
    user = users[0] if users else ""
    story_name = story['name']
    
    # Format: Actor --> Story Name or just Story Name if no actor
    if user:
        story_text = f"{user} --> {story_name}"
    else:
        story_text = story_name
    
    return f"{indent}(S) {story_text}"


def render_sub_epic_stories(sub_epic, indent_level):
    """Recursively render sub-epic with its stories"""
    indent = "    " * indent_level
    lines = []
    
    # Only render if has stories
    if sub_epic.get('stories'):
        lines.append(f"{indent}(E) {sub_epic['name']}")
        for story in sub_epic.get('stories', []):
            lines.append(render_story(story, indent_level + 1))
    
    # Recursively render nested sub-epics
    for nested in sub_epic.get('sub_epics', []):
        lines.extend(render_sub_epic_stories(nested, indent_level + 1))
    
    return lines


def render_increments_to_text(story_graph_path, output_path):
    """
    Render story graph increments to text format.
    
    Args:
        story_graph_path: Path to story-graph.json
        output_path: Path to output .txt file
    """
    with open(story_graph_path) as f:
        data = json.load(f)
    
    output = []
    
    # Render increments
    for increment in data.get('increments', []):
        inc_name = increment.get('name', '')
        inc_priority = increment.get('priority', '')
        
        output.append(f"## Increment {inc_priority}: {inc_name}")
        output.append("")
        
        # Render epics in this increment
        for epic in increment.get('epics', []):
            output.append(f"(E) {epic['name']}")
            
            # Handle sub_epics (standardized structure)
            for sub_epic in epic.get('sub_epics', []):
                output.extend(render_sub_epic_stories(sub_epic, 1))
            
            output.append("")  # Blank line between epics
        
        output.append("")  # Blank line between increments
    
    # Write output
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    
    print(f"Rendered {len(data.get('increments', []))} increments to {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python render_increments_txt.py <story-graph.json> <output.txt>")
        sys.exit(1)
    
    story_graph_path = sys.argv[1]
    output_path = sys.argv[2]
    
    render_increments_to_text(story_graph_path, output_path)


