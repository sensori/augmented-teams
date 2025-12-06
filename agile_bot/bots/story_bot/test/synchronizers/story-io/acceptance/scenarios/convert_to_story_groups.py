#!/usr/bin/env python3
"""
Convert story graph JSON to use story_groups structure.

Converts from:
- sub_epics -> stories (with nested stories)

To:
- sub_epics -> story_groups -> stories (flat, no nested stories)

For tests without DrawIO files, creates a simple default structure:
- All stories in one group with type "and", connector null
"""

import json
from pathlib import Path
from typing import Dict, Any, List


def flatten_stories_to_groups(stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert a list of stories (potentially with nested stories) to story_groups.
    
    Simple default: All stories go into one group with type "and".
    """
    if not stories:
        return []
    
    # Flatten all stories (extract nested stories)
    flat_stories = []
    for story in stories:
        # Add the story itself
        flat_story = {
            "name": story.get("name", ""),
            "sequential_order": story.get("sequential_order", len(flat_stories) + 1),
            "connector": story.get("connector", "and" if flat_stories else None),
            "users": story.get("users", []),
            "story_type": story.get("story_type", "user")
        }
        
        # Copy acceptance_criteria if present
        if "acceptance_criteria" in story:
            flat_story["acceptance_criteria"] = story["acceptance_criteria"]
        if "Steps" in story:
            flat_story["Steps"] = story["Steps"]
        if "steps" in story:
            flat_story["steps"] = story["steps"]
        
        flat_stories.append(flat_story)
        
        # Add nested stories (flatten them into the same group)
        nested_stories = story.get("stories", [])
        for nested_idx, nested in enumerate(nested_stories):
            nested_flat = {
                "name": nested.get("name", ""),
                "sequential_order": len(flat_stories) + 1,
                "connector": nested.get("connector", "and"),
                "users": nested.get("users", []),
                "story_type": nested.get("story_type", "user")
            }
            
            # Copy acceptance_criteria if present
            if "acceptance_criteria" in nested:
                nested_flat["acceptance_criteria"] = nested["acceptance_criteria"]
            if "Steps" in nested:
                nested_flat["Steps"] = nested["Steps"]
            if "steps" in nested:
                nested_flat["steps"] = nested["steps"]
            
            flat_stories.append(nested_flat)
    
    # Renumber sequential_order to be 1, 2, 3...
    for idx, story in enumerate(flat_stories, 1):
        story["sequential_order"] = idx
        # First story has connector null, others have "and"
        if idx == 1:
            story["connector"] = None
        elif story.get("connector") is None:
            story["connector"] = "and"
    
    # Create one story group with all stories
    if flat_stories:
        return [{
            "type": "and",  # Default to horizontal layout
            "connector": None,  # First group
            "stories": flat_stories
        }]
    
    return []


def convert_sub_epic(sub_epic: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Convert a sub_epic to use story_groups."""
    stories = sub_epic.get("stories", [])
    story_groups = flatten_stories_to_groups(stories)
    
    # Convert nested sub_epics
    nested_sub_epics = []
    for nested_idx, nested in enumerate(sub_epic.get("sub_epics", [])):
        nested_sub_epic = convert_sub_epic(nested, nested_idx)
        nested_sub_epics.append(nested_sub_epic)
    
    new_sub_epic = {
        "name": sub_epic.get("name", ""),
        "sequential_order": sub_epic.get("sequential_order", index + 1),
        "estimated_stories": sub_epic.get("estimated_stories", None),
        "sub_epics": nested_sub_epics,
        "story_groups": story_groups
    }
    
    return new_sub_epic


def convert_epic(epic: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Convert an epic to use story_groups."""
    new_sub_epics = []
    
    sub_epics = epic.get("sub_epics", [])
    # Also check for old "features" key
    if not sub_epics:
        sub_epics = epic.get("features", [])
    
    for i, sub_epic in enumerate(sub_epics):
        new_sub_epic = convert_sub_epic(sub_epic, i)
        new_sub_epics.append(new_sub_epic)
    
    new_epic = {
        "name": epic.get("name", ""),
        "sequential_order": epic.get("sequential_order", index + 1),
        "estimated_stories": epic.get("estimated_stories", None),
        "sub_epics": new_sub_epics,
        "stories": []  # Epics don't have stories directly
    }
    
    return new_epic


def convert_story_graph(old_graph: Dict[str, Any]) -> Dict[str, Any]:
    """Convert entire story graph to story_groups structure."""
    new_graph = {
        "epics": []
    }
    
    # Preserve metadata
    if "_explanation" in old_graph:
        new_graph["_explanation"] = old_graph["_explanation"]
    
    epics = old_graph.get("epics", [])
    for i, epic in enumerate(epics):
        new_epic = convert_epic(epic, i)
        new_graph["epics"].append(new_epic)
    
    # Preserve increments if present
    if "increments" in old_graph:
        new_graph["increments"] = old_graph["increments"]
    
    return new_graph


def convert_file(input_path: Path, output_path: Path = None) -> Path:
    """Convert a story graph JSON file to story_groups structure."""
    if output_path is None:
        output_path = input_path
    
    # Load old format
    with open(input_path, 'r', encoding='utf-8') as f:
        old_graph = json.load(f)
    
    # Check if already using story_groups
    already_converted = False
    for epic in old_graph.get("epics", []):
        for sub_epic in epic.get("sub_epics", []):
            if "story_groups" in sub_epic:
                already_converted = True
                break
        if already_converted:
            break
    
    if already_converted:
        print(f"Skipping (already has story_groups): {input_path}")
        return output_path
    
    # Convert to new format
    new_graph = convert_story_graph(old_graph)
    
    # Save new format
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_graph, f, indent=2, ensure_ascii=False)
    
    print(f"Converted: {input_path} -> {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: convert_to_story_groups.py <input_json> [output_json]")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    convert_file(input_path, output_path)

