#!/usr/bin/env python3
"""
Simple algorithm to read through story graph and follow all stories.
Traverses: Epics -> Sub-Epics -> Stories -> Nested Stories (recursively)
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Callable

def traverse_story_graph(story_graph: Dict[str, Any], 
                        visitor: Callable[[str, Any, int], None],
                        level: int = 0):
    """
    Simple recursive traversal of story graph.
    
    Args:
        story_graph: Story graph dictionary
        visitor: Function called for each element: visitor(element_type, element_data, level)
        level: Current nesting level (0 = root)
    """
    # Visit epics
    for epic in story_graph.get('epics', []):
        visitor('epic', epic, level)
        traverse_epic(epic, visitor, level + 1)

def traverse_epic(epic: Dict[str, Any], 
                 visitor: Callable[[str, Any, int], None],
                 level: int = 0):
    """Traverse an epic and all its sub-epics and stories"""
    # Visit sub-epics (features)
    for sub_epic in epic.get('sub_epics', []) or epic.get('features', []):
        visitor('sub_epic', sub_epic, level)
        traverse_sub_epic(sub_epic, visitor, level + 1)
    
    # Visit stories directly in epic
    for story in epic.get('stories', []):
        visitor('story', story, level)
        traverse_story(story, visitor, level + 1)

def traverse_sub_epic(sub_epic: Dict[str, Any], 
                     visitor: Callable[[str, Any, int], None],
                     level: int = 0):
    """Traverse a sub-epic and all its nested sub-epics and stories"""
    # Visit nested sub-epics (recursive)
    for nested_sub_epic in sub_epic.get('sub_epics', []):
        visitor('sub_epic', nested_sub_epic, level)
        traverse_sub_epic(nested_sub_epic, visitor, level + 1)
    
    # Visit stories
    for story in sub_epic.get('stories', []):
        visitor('story', story, level)
        traverse_story(story, visitor, level + 1)

def traverse_story(story: Dict[str, Any], 
                  visitor: Callable[[str, Any, int], None],
                  level: int = 0):
    """Traverse a story and all its nested stories (recursively)"""
    # Visit nested stories (recursive)
    for nested_story in story.get('stories', []):
        visitor('nested_story', nested_story, level)
        traverse_story(nested_story, visitor, level + 1)  # Recursive call
    
    # Visit acceptance criteria
    for ac in story.get('acceptance_criteria', []):
        visitor('acceptance_criteria', ac, level)

def print_visitor(element_type: str, element: Dict[str, Any], level: int):
    """Simple visitor that prints the structure"""
    indent = "  " * level
    name = element.get('name', 'Unknown')
    seq_order = element.get('sequential_order', '')
    connector = element.get('connector', 'and')
    users = element.get('users', [])
    
    if element_type == 'epic':
        print(f"{indent}[EPIC] {name} (order: {seq_order})")
    elif element_type == 'sub_epic':
        print(f"{indent}[SUB-EPIC] {name} (order: {seq_order})")
    elif element_type == 'story':
        users_str = f" [{', '.join(users)}]" if users else ""
        print(f"{indent}[STORY] {name} (order: {seq_order}, connector: {connector}){users_str}")
    elif element_type == 'nested_story':
        users_str = f" [{', '.join(users)}]" if users else ""
        print(f"{indent}[NESTED] {name} (order: {seq_order}, connector: {connector}){users_str}")
    elif element_type == 'acceptance_criteria':
        desc = element.get('description', '')
        print(f"{indent}[AC] {desc}")

def count_visitor(element_type: str, element: Dict[str, Any], level: int, counts: Dict[str, int]):
    """Visitor that counts elements"""
    counts[element_type] = counts.get(element_type, 0) + 1

if __name__ == "__main__":
    import sys
    # Load story graph
    json_path = Path("1_given/new-format-story-graph.json")
    with open(json_path, 'r', encoding='utf-8') as json_file:
        story_graph = json.load(json_file)
    
    # Write to both stdout and file
    output_file = Path("traversal_output.txt")
    with open(output_file, 'w', encoding='utf-8') as out_file:
        def write_both(text):
            sys.stdout.write(text)
            sys.stdout.flush()
            out_file.write(text)
            out_file.flush()
        
        write_both("=" * 80 + "\n")
        write_both("STORY GRAPH TRAVERSAL\n")
        write_both("=" * 80 + "\n")
        write_both("\n")
        
        # Print structure
        def print_and_save(element_type, element, level):
            indent = "  " * level
            name = element.get('name', 'Unknown')
            seq_order = element.get('sequential_order', '')
            connector = element.get('connector', 'and')
            users = element.get('users', [])
            
            if element_type == 'epic':
                text = f"{indent}[EPIC] {name} (order: {seq_order})\n"
            elif element_type == 'sub_epic':
                text = f"{indent}[SUB-EPIC] {name} (order: {seq_order})\n"
            elif element_type == 'story':
                users_str = f" [{', '.join(users)}]" if users else ""
                text = f"{indent}[STORY] {name} (order: {seq_order}, connector: {connector}){users_str}\n"
            elif element_type == 'nested_story':
                users_str = f" [{', '.join(users)}]" if users else ""
                text = f"{indent}[NESTED] {name} (order: {seq_order}, connector: {connector}){users_str}\n"
            elif element_type == 'acceptance_criteria':
                desc = element.get('description', '')
                text = f"{indent}[AC] {desc}\n"
            else:
                text = ""
            
            write_both(text)
        
        traverse_story_graph(story_graph, print_and_save)
        
        write_both("\n")
        write_both("=" * 80 + "\n")
        write_both("COUNTS\n")
        write_both("=" * 80 + "\n")
        
        # Count elements
        counts = {}
        traverse_story_graph(story_graph, lambda t, e, l: count_visitor(t, e, l, counts))
        
        for element_type, count in sorted(counts.items()):
            write_both(f"{element_type}: {count}\n")
    
    print(f"\nOutput also written to: {output_file}")
