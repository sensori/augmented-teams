#!/usr/bin/env python3
"""
Convert old story-graph.json to new structure with workflow grouping.
Positioning rules:
- Different X, same Y = "and" (horizontal sequence)
- Different Y, same X = "or" (vertical alternatives)
"""

import json
from collections import defaultdict
from pathlib import Path

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_story_key(epic_name, feature_name, story_name):
    """Generate story key for layout lookup"""
    return f"{epic_name}|{feature_name}|{story_name}"

def group_stories_by_position(stories, layout, epic_name, feature_name):
    """Group stories by X/Y position to determine workflow relationships"""
    story_positions = {}
    
    for story in stories:
        key = get_story_key(epic_name, feature_name, story["name"])
        pos = layout.get(key, {})
        if "x" in pos and "y" in pos:
            story_positions[story["name"]] = {
                "x": pos["x"],
                "y": pos["y"],
                "story": story
            }
    
    # Group by Y (rows) - stories in same row (same Y) are sequential (and)
    rows = defaultdict(list)
    for name, info in story_positions.items():
        rows[info["y"]].append((info["x"], name, info["story"]))
    
    # Sort each row by X (left to right)
    for y in rows:
        rows[y].sort(key=lambda x: x[0])
    
    return rows, story_positions

def determine_workflow_connector(index, rows, story_positions, story_name):
    """Determine workflow connector based on position"""
    if index == 0:
        return None
    
    # Find this story's position
    story_info = story_positions.get(story_name)
    if not story_info:
        return "and"  # Default to "and" if no position
    
    # Get all stories in same row (same Y)
    same_row = [s for s in rows[story_info["y"]] if s[1] != story_name]
    if same_row:
        # Check if there's a story before this one in the row
        before = [s for s in same_row if s[0] < story_info["x"]]
        if before:
            return "and"
    
    # Check if there's a story above (same X, different Y) - this would be "or"
    same_x = [s for s in story_positions.values() 
              if s["x"] == story_info["x"] and s["y"] != story_info["y"]]
    if same_x:
        # Find if there's one above (smaller Y)
        above = [s for s in same_x if s["y"] < story_info["y"]]
        if above:
            return "or"
    
    return "and"  # Default

def find_workflow_children(story_name, rows, story_positions):
    """Find workflow children based on positioning"""
    story_info = story_positions.get(story_name)
    if not story_info:
        return []
    
    children = []
    
    # Stories with same X but different Y (vertical stack) = "or" alternatives
    same_x_different_y = [
        name for name, info in story_positions.items()
        if name != story_name
        and abs(info["x"] - story_info["x"]) < 1.0  # Same X (with tolerance)
        and abs(info["y"] - story_info["y"]) > 1.0  # Different Y
    ]
    
    if same_x_different_y:
        # Sort by Y (top to bottom)
        same_x_different_y.sort(key=lambda n: story_positions[n]["y"])
        children.extend(same_x_different_y)
    
    return children

def normalize_sequential_order(order):
    """Ensure sequential_order is always an integer"""
    return int(order) if isinstance(order, (int, float)) else order

def convert_story(story, index, rows, story_positions, epic_name, feature_name):
    """Convert a single story to new format"""
    story_name = story["name"]
    original_order = story.get("sequential_order")
    
    # Ensure sequential_order is always an integer
    sequential_order = normalize_sequential_order(original_order)
    
    # Use _connector from parser if available (including None/null), otherwise infer from layout
    if "_connector" in story:
        # _connector was explicitly set (could be None/null, "and", "or", etc.)
        connector = story.get("_connector")  # Preserve None if that's what was set
    else:
        # _connector not set - infer from layout
        connector = determine_workflow_connector(
            index, rows, story_positions, story_name
        )
    
    new_story = {
        "name": story["name"],
        "sequential_order": sequential_order,
        "connector": connector,
        "users": story.get("users", []),
        "story_type": "user"
    }
    
    # Convert acceptance_criteria if present
    acceptance_criteria = story.get("acceptance_criteria", [])
    if acceptance_criteria:
        new_story["acceptance_criteria"] = []
        for ac in acceptance_criteria:
            new_ac = {
                "description": ac.get("description", ac.get("name", "")),
                "sequential_order": normalize_sequential_order(ac.get("sequential_order", 1)),
                "connector": ac.get("connector") or ac.get("_connector"),
                "user": ac.get("user", "") if isinstance(ac.get("user"), str) else (ac.get("users", [""])[0] if ac.get("users") else "")
            }
            new_story["acceptance_criteria"].append(new_ac)
    
    # Convert nested stories if present (story groups)
    nested_stories = story.get("stories", [])
    if nested_stories:
        new_story["stories"] = []
        for nested_idx, nested_story in enumerate(nested_stories):
            nested_new = convert_story(nested_story, nested_idx, rows, story_positions, epic_name, feature_name)
            new_story["stories"].append(nested_new)
    
    return new_story

def convert_feature_to_sub_epic(feature, index, epic, layout, parent_feature_name=None):
    """Convert a feature to sub_epic, handling nested features recursively"""
    epic_name = epic["name"]
    feature_name = feature["name"]
    
    # Group stories by position
    rows, story_positions = group_stories_by_position(
        feature.get("stories", []), layout, epic_name, feature_name
    )
    
    # Convert all stories (they may already have nested stories in their stories array)
    all_stories = feature.get("stories", [])
    new_stories = []
    
    for i, story in enumerate(all_stories):
        new_story = convert_story(story, i, rows, story_positions, epic_name, feature_name)
        new_stories.append(new_story)
    
    # Convert nested features (sub-epics within this feature)
    new_nested_sub_epics = []
    nested_features = feature.get("features", [])
    if nested_features:
        for nested_idx, nested_feature in enumerate(nested_features):
            nested_sub_epic = convert_feature_to_sub_epic(
                nested_feature, nested_idx, epic, layout, feature_name
            )
            new_nested_sub_epics.append(nested_sub_epic)
    
    new_sub_epic = {
        "name": feature["name"],
        "sequential_order": feature["sequential_order"],
        "estimated_stories": None,
        "sub_epics": new_nested_sub_epics,
        "stories": new_stories
    }
    
    return new_sub_epic

def convert_epic(epic, index, layout):
    """Convert an epic to new format - epics don't have workflow_connector"""
    new_sub_epics = []
    
    for i, feature in enumerate(epic.get("features", [])):
        new_sub_epic = convert_feature_to_sub_epic(feature, i, epic, layout)
        new_sub_epics.append(new_sub_epic)
    
    new_epic = {
        "name": epic["name"],
        "sequential_order": epic["sequential_order"],
        "estimated_stories": None,
        "sub_epics": new_sub_epics,
        "stories": []
    }
    
    return new_epic

def convert_story_graph(old_graph, layout):
    """Convert entire story graph to new structure"""
    new_graph = {
        "epics": []
    }
    
    for i, epic in enumerate(old_graph.get("epics", [])):
        new_epic = convert_epic(epic, i, layout)
        new_graph["epics"].append(new_epic)
    
    return new_graph

def main():
    # Load files
    base_dir = Path(__file__).parent / "stories"
    old_graph_path = base_dir / "story-graph.json"
    layout_path = base_dir / "story-graph-drawio-layout.json"
    output_path = base_dir / "story-graph-new.json"
    
    print(f"Loading {old_graph_path}...")
    old_graph = load_json(old_graph_path)
    
    print(f"Loading {layout_path}...")
    layout = load_json(layout_path)
    
    print("Converting to new structure...")
    new_graph = convert_story_graph(old_graph, layout)
    
    print(f"Saving to {output_path}...")
    save_json(new_graph, output_path)
    
    print("Done!")

if __name__ == "__main__":
    main()

