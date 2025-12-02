#!/usr/bin/env python3
"""Simple test to show traversal output"""
import json
from pathlib import Path
from simple_traverse import traverse_story_graph

# Load story graph
json_path = Path("1_given/new-format-story-graph.json")
with open(json_path, 'r', encoding='utf-8') as f:
    story_graph = json.load(f)

# Collect output
output_lines = []

def collect_visitor(element_type, element, level):
    indent = "  " * level
    name = element.get('name', 'Unknown')
    seq_order = element.get('sequential_order', '')
    connector = element.get('connector', 'and')
    users = element.get('users', [])
    
    if element_type == 'epic':
        output_lines.append(f"{indent}[EPIC] {name} (order: {seq_order})")
    elif element_type == 'sub_epic':
        output_lines.append(f"{indent}[SUB-EPIC] {name} (order: {seq_order})")
    elif element_type == 'story':
        users_str = f" [{', '.join(users)}]" if users else ""
        output_lines.append(f"{indent}[STORY] {name} (order: {seq_order}, connector: {connector}){users_str}")
    elif element_type == 'nested_story':
        users_str = f" [{', '.join(users)}]" if users else ""
        output_lines.append(f"{indent}[NESTED] {name} (order: {seq_order}, connector: {connector}){users_str}")
    elif element_type == 'acceptance_criteria':
        desc = element.get('description', '')
        output_lines.append(f"{indent}[AC] {desc}")

# Traverse
output_lines.append("=" * 80)
output_lines.append("STORY GRAPH TRAVERSAL")
output_lines.append("=" * 80)
output_lines.append("")
traverse_story_graph(story_graph, collect_visitor)

# Count
from simple_traverse import count_visitor
output_lines.append("")
output_lines.append("=" * 80)
output_lines.append("COUNTS")
output_lines.append("=" * 80)
counts = {}
traverse_story_graph(story_graph, lambda t, e, l: count_visitor(t, e, l, counts))
for element_type, count in sorted(counts.items()):
    output_lines.append(f"{element_type}: {count}")

# Write to file
output_file = Path("traversal_output.txt")
output_file.write_text('\n'.join(output_lines), encoding='utf-8')
print('\n'.join(output_lines))
print(f"\nOutput written to: {output_file}")
