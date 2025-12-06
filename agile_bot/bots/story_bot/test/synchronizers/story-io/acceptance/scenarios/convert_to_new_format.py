#!/usr/bin/env python3
"""
Convert old story graph format (with features) to new format (with sub_epics).

Old format:
- epics -> features -> stories

New format:
- epics -> sub_epics -> stories
- Stories have connector field ("and", "or", or null)
- Sequential orders are always integers
"""

import json
from pathlib import Path
from typing import Dict, Any, List


def normalize_sequential_order(order):
    """Ensure sequential_order is always an integer."""
    if order is None:
        return 1
    return int(order) if isinstance(order, (int, float)) else order


def convert_story(story: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Convert a single story to new format."""
    new_story = {
        "name": story.get("name", ""),
        "sequential_order": normalize_sequential_order(story.get("sequential_order", index + 1)),
        "connector": None if index == 0 else "and",  # Default to "and" for sequential stories
        "users": story.get("users", []),
        "story_type": story.get("story_type", "user")
    }
    
    # Copy acceptance_criteria if present
    if "acceptance_criteria" in story:
        new_story["acceptance_criteria"] = story["acceptance_criteria"]
    
    # Convert nested stories (story groups) if present
    nested_stories = story.get("stories", [])
    if nested_stories:
        new_story["stories"] = []
        for nested_idx, nested_story in enumerate(nested_stories):
            nested_new = convert_story(nested_story, nested_idx)
            new_story["stories"].append(nested_new)
    
    return new_story


def convert_feature_to_sub_epic(feature: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Convert a feature to sub_epic format."""
    # Convert stories
    new_stories = []
    all_stories = feature.get("stories", [])
    
    for i, story in enumerate(all_stories):
        new_story = convert_story(story, i)
        new_stories.append(new_story)
    
    # Convert nested features (sub-epics within this feature)
    new_nested_sub_epics = []
    nested_features = feature.get("features", [])
    if nested_features:
        for nested_idx, nested_feature in enumerate(nested_features):
            nested_sub_epic = convert_feature_to_sub_epic(nested_feature, nested_idx)
            new_nested_sub_epics.append(nested_sub_epic)
    
    new_sub_epic = {
        "name": feature.get("name", ""),
        "sequential_order": normalize_sequential_order(feature.get("sequential_order", index + 1)),
        "estimated_stories": feature.get("estimated_stories", None),
        "sub_epics": new_nested_sub_epics,
        "stories": new_stories
    }
    
    return new_sub_epic


def convert_epic(epic: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Convert an epic to new format."""
    new_sub_epics = []
    
    features = epic.get("features", [])
    for i, feature in enumerate(features):
        new_sub_epic = convert_feature_to_sub_epic(feature, i)
        new_sub_epics.append(new_sub_epic)
    
    new_epic = {
        "name": epic.get("name", ""),
        "sequential_order": normalize_sequential_order(epic.get("sequential_order", index + 1)),
        "estimated_stories": epic.get("estimated_stories", None),
        "sub_epics": new_sub_epics,
        "stories": []
    }
    
    return new_epic


def convert_story_graph(old_graph: Dict[str, Any]) -> Dict[str, Any]:
    """Convert entire story graph to new structure."""
    new_graph = {
        "epics": []
    }
    
    # Add explanation if present
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
    """
    Convert a story graph JSON file from old format to new format.
    
    Args:
        input_path: Path to input JSON file (old format)
        output_path: Path to output JSON file (if None, overwrites input)
    
    Returns:
        Path to converted file
    """
    if output_path is None:
        output_path = input_path
    
    # Load old format
    with open(input_path, 'r', encoding='utf-8') as f:
        old_graph = json.load(f)
    
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
        print("Usage: convert_to_new_format.py <input_json> [output_json]")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    convert_file(input_path, output_path)
























































