#!/usr/bin/env python3
"""Show traversal output - simple algorithm to follow all stories"""
import json
from pathlib import Path

def traverse_story(story, level=0, lines=None):
    if lines is None:
        lines = []
    indent = "  " * level
    name = story.get('name', 'Unknown')
    seq = story.get('sequential_order', '')
    connector = story.get('connector', 'and')
    users = story.get('users', [])
    users_str = f" [{', '.join(users)}]" if users else ""
    lines.append(f"{indent}[STORY] {name} (order: {seq}, connector: {connector}){users_str}")
    # Follow nested stories recursively
    for nested in story.get('stories', []):
        traverse_story(nested, level + 1, lines)
    return lines

def traverse_sub_epic(sub_epic, level=0, lines=None):
    if lines is None:
        lines = []
    indent = "  " * level
    name = sub_epic.get('name', 'Unknown')
    seq = sub_epic.get('sequential_order', '')
    lines.append(f"{indent}[SUB-EPIC] {name} (order: {seq})")
    # Stories
    for story in sub_epic.get('stories', []):
        traverse_story(story, level + 1, lines)
    # Nested sub-epics
    for nested_sub in sub_epic.get('sub_epics', []):
        traverse_sub_epic(nested_sub, level + 1, lines)
    return lines

def traverse_epic(epic, level=0, lines=None):
    if lines is None:
        lines = []
    indent = "  " * level
    name = epic.get('name', 'Unknown')
    seq = epic.get('sequential_order', '')
    lines.append(f"{indent}[EPIC] {name} (order: {seq})")
    # Sub-epics
    for sub_epic in epic.get('sub_epics', []) or epic.get('features', []):
        traverse_sub_epic(sub_epic, level + 1, lines)
    # Stories directly in epic
    for story in epic.get('stories', []):
        traverse_story(story, level + 1, lines)
    return lines

# Load and traverse
script_dir = Path(__file__).parent.absolute()
json_path = script_dir / "1_given" / "new-format-story-graph.json"

print(f"Loading from: {json_path}")
with open(json_path, 'r', encoding='utf-8') as f:
    story_graph = json.load(f)

lines = ["=" * 80, "STORY GRAPH TRAVERSAL - FOLLOWING ALL STORIES", "=" * 80, ""]
for epic in story_graph.get('epics', []):
    traverse_epic(epic, 0, lines)
    lines.append("")
lines.append("=" * 80)
lines.append("DONE")
lines.append("=" * 80)

# Write to file
output_file = script_dir / "traversal_output.txt"
output_text = '\n'.join(lines)
output_file.write_text(output_text, encoding='utf-8')

# Print output
print('\n'.join(lines))
print(f"\nOutput written to: {output_file}")
