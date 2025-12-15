"""
Render story graph increments to flat backlog text format.
Shows simple list of stories per increment for backlog management.
"""
import json
from pathlib import Path
import sys


def collect_stories_from_sub_epic(sub_epic, stories_list):
    """Recursively collect all stories from sub-epic"""
    stories_list.extend(sub_epic.get('stories', []))
    for nested in sub_epic.get('sub_epics', []):
        collect_stories_from_sub_epic(nested, stories_list)


def render_increments_backlog_to_text(story_graph_path, output_path):
    """
    Render story graph increments to flat backlog text format.
    
    Args:
        story_graph_path: Path to story-graph.json
        output_path: Path to output .txt file
    """
    with open(story_graph_path) as f:
        data = json.load(f)
    
    output = []
    output.append("# Incremental Backlog")
    output.append("")
    
    # Render increments
    for increment in data.get('increments', []):
        inc_name = increment.get('name', '')
        inc_priority = increment.get('priority', '')
        
        output.append(f"## Increment {inc_priority}: {inc_name}")
        output.append("")
        
        # Collect all stories from all epics/sub_epics in this increment
        all_stories = []
        for epic in increment.get('epics', []):
            # Handle sub_epics (standardized structure) - recursively collect
            for sub_epic in epic.get('sub_epics', []):
                collect_stories_from_sub_epic(sub_epic, all_stories)
        
        # Render as flat list
        for story in all_stories:
            users = story.get('users', [])
            user = users[0] if users else ""
            story_name = story['name']
            
            if user:
                output.append(f"- {user} --> {story_name}")
            else:
                output.append(f"- {story_name}")
        
        output.append("")  # Blank line between increments
    
    # Write output
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    
    print(f"Rendered {len(data.get('increments', []))} increments (backlog) to {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python render_increments_backlog_txt.py <story-graph.json> <output.txt>")
        sys.exit(1)
    
    story_graph_path = sys.argv[1]
    output_path = sys.argv[2]
    
    render_increments_backlog_to_text(story_graph_path, output_path)


