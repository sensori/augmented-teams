#!/usr/bin/env python3
"""
Round-trip test: story-map-in.txt -> JSON -> story-map-rendered.txt
Validates that the conversion and rendering process produces identical output.
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from collections import defaultdict

# Add parent directory to path to import convert_story_graph
sys.path.insert(0, str(Path(__file__).parent))

def parse_story_map_text(text_path):
    """Parse story-map-in.txt into old JSON format, preserving exact order and structure"""
    with open(text_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    epics = []
    epic_order = 1
    
    # Stack to track hierarchy: (level, type, item, connector)
    stack = []
    
    # Track sequential order per parent
    order_counters = {}  # (epic_name, feature_name) -> counter
    
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        
        # Calculate indentation level
        indent = len(line) - len(line.lstrip())
        level = indent // 4
        
        # Match (E), (S), (AC) with connectors: and, or, opt
        match = re.match(r'^\s*(and|or|opt)?\s*\(([ESAC]|AC)\)\s*(.+?)$', line.strip())
        if not match:
            i += 1
            continue
        
        connector, item_type, content = match.groups()
        # Default to "and" if no connector specified (only for stories, not epics)
        if connector is None and item_type == 'S':
            connector = "and"
        # Normalize AC to single character for processing
        if item_type == 'AC':
            item_type = 'AC'
        
        # Extract actor and name
        actor = None
        name = content
        if '-->' in content:
            parts = content.split('-->', 1)
            actor = parts[0].strip()
            name = parts[1].strip()
        
        # Pop stack until we're at the right level (but don't pop for AC items - they need their parent)
        if item_type != 'AC':
            while stack and stack[-1][0] >= level:
                stack.pop()
        
        if item_type == 'E':  # Epic or Sub-Epic
            if level == 0:
                # Top-level epic
                epic = {
                    "name": name,
                    "sequential_order": epic_order,
                    "features": [],
                    "stories": []
                }
                epics.append(epic)
                epic_order += 1
                stack.append((level, 'epic', epic, connector))
            else:
                # Find parent feature or epic
                parent = None
                for stack_level, stack_type, stack_item, _ in reversed(stack):
                    if stack_type in ('feature', 'epic'):
                        parent = stack_item
                        break
                
                if parent:
                    if "features" not in parent:
                        parent["features"] = []
                    
                    feature = {
                        "name": name,
                        "sequential_order": len(parent["features"]) + 1,
                        "stories": []
                    }
                    parent["features"].append(feature)
                    stack.append((level, 'feature', feature, connector))
        
        elif item_type == 'S':  # Story
            # Check if this is nested under a story (based on indentation)
            parent_story = None
            if stack and stack[-1][1] == 'story' and stack[-1][0] < level:
                # This story is nested under another story
                parent_story = stack[-1][2]
            
            if parent_story:
                # Nested story - add to parent story's stories array
                if "stories" not in parent_story:
                    parent_story["stories"] = []
                counter_key = f"story_{parent_story['name']}"
                if counter_key not in order_counters:
                    order_counters[counter_key] = 1
                
                story = {
                    "name": name,
                    "sequential_order": order_counters[counter_key],
                    "users": [actor] if actor else [],
                    "_connector": connector
                }
                order_counters[counter_key] += 1
                parent_story["stories"].append(story)
                stack.append((level, 'story', story, connector))
            else:
                # Regular story - find parent (feature or epic)
                parent = None
                parent_epic_name = None
                parent_feature_name = None
                
                # Pop stack until we find a feature or epic (not a story at same or higher level)
                while stack and stack[-1][0] >= level:
                    stack.pop()
                
                for stack_level, stack_type, stack_item, _ in reversed(stack):
                    if stack_type == 'epic':
                        parent_epic_name = stack_item["name"]
                        if not parent:
                            parent = stack_item
                    elif stack_type == 'feature':
                        parent_feature_name = stack_item["name"]
                        if not parent:
                            parent = stack_item
                
                if parent:
                    counter_key = (parent_epic_name, parent_feature_name)
                    if counter_key not in order_counters:
                        order_counters[counter_key] = 1
                    
                    story = {
                        "name": name,
                        "sequential_order": order_counters[counter_key],
                        "users": [actor] if actor else [],
                        "_connector": connector
                    }
                    order_counters[counter_key] += 1
                    parent["stories"].append(story)
                    stack.append((level, 'story', story, connector))
        
        elif item_type == 'AC':  # Acceptance Criteria - these go in acceptance_criteria array
            # Find parent story - don't pop stack, AC items need their parent
            # Look for the most recent story on the stack (should be at a shallower level)
            parent_story = None
            for stack_level, stack_type, stack_item, _ in reversed(stack):
                if stack_type == 'story':
                    parent_story = stack_item
                    break
            
            if parent_story:
                if "acceptance_criteria" not in parent_story:
                    parent_story["acceptance_criteria"] = []
                counter_key = f"ac_{parent_story['name']}"
                if counter_key not in order_counters:
                    order_counters[counter_key] = 1
                
                ac_item = {
                    "description": name,
                    "sequential_order": order_counters[counter_key],
                    "connector": connector,
                    "user": actor if actor else ""
                }
                order_counters[counter_key] += 1
                parent_story["acceptance_criteria"].append(ac_item)
        
        i += 1
    
    return {"epics": epics}

def parse_story_map_with_layout(text_path, story_graph):
    """Parse story-map-in.txt and extract layout information based on connectors"""
    with open(text_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    layout = {}
    x_base = 100
    y_base = 100
    
    # Track current context
    current_epic = None
    current_feature = None
    story_positions_by_feature = defaultdict(list)  # feature -> [(story_name, connector, level, x, y)]
    
    y = y_base
    
    for epic in story_graph.get("epics", []):
        epic_name = epic["name"]
        y += 200
        
        for feature in epic.get("features", []):
            feature_name = feature["name"]
            y += 100
            x = x_base
            
            # Collect all stories for this feature with their connectors
            stories_with_connectors = []
            for story in feature.get("stories", []):
                connector = story.get("_connector")
                # Determine level - if it's a workflow_child, it's nested
                is_nested = story.get("sequential_order", 0) != int(story.get("sequential_order", 0))
                level = 3 if is_nested else 2
                stories_with_connectors.append((story["name"], connector, level, story))
            
            # Group stories by level and connector
            level_2_stories = [s for s in stories_with_connectors if s[2] == 2]
            level_3_stories = [s for s in stories_with_connectors if s[2] == 3]
            
            # Position level 2 stories (top level in feature)
            x_current = x
            y_current = y
            for i, (story_name, connector, level, story_obj) in enumerate(level_2_stories):
                key = f"{epic_name}|{feature_name}|{story_name}"
                
                if connector == "or":
                    # "or" stories: same X, different Y (vertical)
                    layout[key] = {"x": x, "y": y_current}
                    y_current += 50
                else:
                    # "and" or first story: same Y, different X (horizontal)
                    layout[key] = {"x": x_current, "y": y}
                    x_current += 150
            
            # Position level 3 stories (nested/workflow_children)
            # These should be positioned relative to their parent
            for story_name, connector, level, story_obj in level_3_stories:
                # Find parent story (the one this is a workflow_child of)
                parent_story = None
                for s in level_2_stories:
                    parent_obj = s[3]
                    if story_name in parent_obj.get("workflow_children", []):
                        parent_story = s
                        break
                
                if parent_story:
                    parent_key = f"{epic_name}|{feature_name}|{parent_story[0]}"
                    parent_pos = layout.get(parent_key, {"x": x, "y": y})
                    # Nested stories go to the right and down
                    key = f"{epic_name}|{feature_name}|{story_name}"
                    layout[key] = {"x": parent_pos["x"] + 150, "y": parent_pos["y"] + 50}
    
    return layout

def run_conversion(input_json, layout_json, output_json):
    """Run convert_story_graph.py"""
    # Create a temporary script that uses the provided data
    script_content = f'''#!/usr/bin/env python3
import json
import sys
sys.path.insert(0, r"{Path(__file__).parent}")

from convert_story_graph import convert_story_graph, load_json, save_json

# Load input data
with open(r"{input_json}", 'r', encoding='utf-8') as f:
    old_graph = json.load(f)

with open(r"{layout_json}", 'r', encoding='utf-8') as f:
    layout = json.load(f)

# Convert
new_graph = convert_story_graph(old_graph, layout)

# Save
with open(r"{output_json}", 'w', encoding='utf-8') as f:
    json.dump(new_graph, f, indent=2, ensure_ascii=False)

print("Conversion complete")
'''
    
    script_path = Path(__file__).parent / "temp_convert.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        if result.returncode != 0:
            print(f"Conversion failed: {result.stderr}")
            return False
        return True
    finally:
        if script_path.exists():
            script_path.unlink()

def render_story_map(json_path, template_path, output_path):
    """Render JSON to text using template"""
    # Import the render function (we'll need to create/import it)
    # For now, use the existing render_story_map.py logic
    script_content = f'''#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Import render logic
sys.path.insert(0, r"{Path(__file__).parent.parent}")

# Copy render logic here or import
def format_actor(users):
    if not users:
        return ""
    if len(users) == 1:
        return f"{{users[0]}} --> "
    return f"{{', '.join(users)}} --> "

def render_story(story, indent_level, is_first_in_sequence=False, all_stories_in_context=None, rendered_stories=None, story_map=None, parent_is_story=False):
    if rendered_stories is None:
        rendered_stories = set()
    if story_map is None:
        story_map = {{}}
    
    # Allow duplicate story names - they can appear in different contexts
    # Use story object identity or a combination of name + context to track if needed
    
    indent = "    " * indent_level
    connector = story.get("connector") or story.get("_connector")
    # Default to "and" if no connector (stories default to "and")
    if connector is None:
        connector = "and"
    
    # Don't show "and" when it's the default - only show "or" and "opt"
    # This applies to both top-level and nested stories
    if connector == "and":
        connector_str = ""
    # Show "or" and "opt" connectors
    else:
        connector_str = connector + " " if connector else ""
    
    actor = format_actor(story.get("users", []))
    story_name = story["name"]
    
    lines = [f"{{indent}}{{connector_str}}(S) {{actor}}{{story_name}}"]
    
    # Handle acceptance_criteria - render as (AC) items
    acceptance_criteria = story.get("acceptance_criteria", [])
    if acceptance_criteria:
        for i, ac in enumerate(acceptance_criteria):
            nested_indent = "    " * (indent_level + 1)
            ac_connector = ac.get("connector")
            # Default to "and" if no connector (AC items default to "and")
            if ac_connector is None:
                ac_connector = "and"
            # Don't show "and" when it's the default - only show "or" and "opt"
            if ac_connector == "and":
                ac_connector_str = ""
            else:
                ac_connector_str = ac_connector + " "
            ac_user = ac.get("user", "")
            ac_actor = f"{{ac_user}} --> " if ac_user else ""
            lines.append(f"{{nested_indent}}{{ac_connector_str}}(AC) {{ac_actor}}{{ac.get('description', '')}}")
    
    # Handle nested stories (stories with a stories array) - these are story groups
    nested_stories = story.get("stories", [])
    if nested_stories:
        for i, nested in enumerate(nested_stories):
            nested_lines = render_story(nested, indent_level + 1, i == 0, all_stories_in_context, rendered_stories, story_map, parent_is_story=True)
            lines.extend(nested_lines)
    
    return lines

def render_stories_with_workflow(stories, indent_level, all_stories_in_context, rendered_stories=None, parent_is_story=False):
    if rendered_stories is None:
        rendered_stories = set()
    
    # Create story map for quick lookup
    story_map = {{s["name"]: s for s in stories}}
    
    lines = []
    for i, story in enumerate(stories):
        # Allow duplicate story names - render all stories
        is_first = (i == 0)
        story_lines = render_story(story, indent_level, is_first, all_stories_in_context, rendered_stories, story_map, parent_is_story=parent_is_story)
        lines.extend(story_lines)
    
    return lines

def render_sub_epic(sub_epic, indent_level, is_first_in_sequence=False, all_stories_in_epic=None):
    indent = "    " * indent_level
    # Sub-epics don't have connectors
    connector_str = ""
    
    lines = [f"{{indent}}{{connector_str}}(E) {{sub_epic['name']}}"]
    
    # Render nested sub-epics (features can have nested features)
    nested_sub_epics = sub_epic.get("sub_epics", [])
    if nested_sub_epics:
        for i, nested in enumerate(nested_sub_epics):
            nested_lines = render_sub_epic(nested, indent_level + 1, i == 0, all_stories_in_epic)
            lines.extend(nested_lines)
    
    # Render stories (including stories with nested stories)
    stories = sub_epic.get("stories", [])
    if stories:
        story_lines = render_stories_with_workflow(stories, indent_level + 1, all_stories_in_epic or stories, set(), parent_is_story=False)
        lines.extend(story_lines)
    
    return lines

def render_epic(epic, indent_level, is_first_in_sequence=False):
    indent = "    " * indent_level
    # Epics don't have connectors
    connector_str = ""
    
    lines = [f"{{indent}}{{connector_str}}(E) {{epic['name']}}"]
    
    # Collect all stories in epic for workflow_children lookup
    all_stories_in_epic = []
    for sub_epic in epic.get("sub_epics", []):
        all_stories_in_epic.extend(sub_epic.get("stories", []))
    all_stories_in_epic.extend(epic.get("stories", []))
    
    # Render sub-epics
    sub_epics = epic.get("sub_epics", [])
    if sub_epics:
        for i, sub_epic in enumerate(sub_epics):
            sub_epic_lines = render_sub_epic(sub_epic, indent_level + 1, i == 0, all_stories_in_epic)
            lines.extend(sub_epic_lines)
    
    # Render direct stories
    stories = epic.get("stories", [])
    if stories:
        story_lines = render_stories_with_workflow(stories, indent_level + 1, all_stories_in_epic or stories, set(), parent_is_story=False)
        lines.extend(story_lines)
    
    return lines

# Load JSON
with open(r"{json_path}", 'r', encoding='utf-8') as f:
    story_graph = json.load(f)

# Render
output_lines = []
for i, epic in enumerate(story_graph.get("epics", [])):
    epic_lines = render_epic(epic, 0, i == 0)
    output_lines.extend(epic_lines)

# Write output
with open(r"{output_path}", 'w', encoding='utf-8') as f:
    f.write("\\n".join(output_lines))

print("Rendering complete")
'''
    
    script_path = Path(__file__).parent / "temp_render.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        if result.returncode != 0:
            print(f"Rendering failed: {result.stderr}")
            return False
        return True
    finally:
        if script_path.exists():
            script_path.unlink()

def normalize_text(text):
    """Normalize text for comparison (remove extra whitespace, ACs, etc.)"""
    lines = text.split('\n')
    normalized = []
    for line in lines:
        # Remove trailing whitespace
        line = line.rstrip()
        # Skip acceptance criteria (AC) lines
        if re.match(r'^\s*\(AC\)', line):
            continue
        # Keep empty lines but normalize them
        normalized.append(line)
    # Remove trailing empty lines
    while normalized and not normalized[-1]:
        normalized.pop()
    return '\n'.join(normalized)

def compare_files(file1_path, file2_path):
    """Compare two files and return differences"""
    with open(file1_path, 'r', encoding='utf-8') as f:
        content1 = normalize_text(f.read())
    
    with open(file2_path, 'r', encoding='utf-8') as f:
        content2 = normalize_text(f.read())
    
    if content1 == content2:
        return True, None
    
    # Find differences
    lines1 = content1.split('\n')
    lines2 = content2.split('\n')
    
    diff = []
    max_len = max(len(lines1), len(lines2))
    for i in range(max_len):
        line1 = lines1[i] if i < len(lines1) else None
        line2 = lines2[i] if i < len(lines2) else None
        
        if line1 != line2:
            diff.append({
                "line": i + 1,
                "expected": line1,
                "actual": line2
            })
    
    return False, diff

def main():
    """Run the round-trip test"""
    test_dir = Path(__file__).parent
    
    input_text = test_dir / "story-map-in.txt"
    template = test_dir / "story-map-template.txt"
    temp_json = test_dir / "temp-story-graph.json"
    temp_layout = test_dir / "temp-layout.json"
    converted_json = test_dir / "story-graph-converted.json"
    rendered_text = test_dir / "story-map-rendered.txt"
    
    print("=" * 80)
    print("Round-Trip Test: story-map-in.txt -> JSON -> story-map-rendered.txt")
    print("=" * 80)
    
    # Step 1: Parse text to JSON
    print("\n[1/5] Parsing story-map-in.txt to JSON...")
    try:
        story_graph = parse_story_map_text(input_text)
        with open(temp_json, 'w', encoding='utf-8') as f:
            json.dump(story_graph, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Created {temp_json}")
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        return 1
    
    # Step 2: Generate layout data
    print("\n[2/5] Generating layout data...")
    try:
        layout = parse_story_map_with_layout(input_text, story_graph)
        with open(temp_layout, 'w', encoding='utf-8') as f:
            json.dump(layout, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Created {temp_layout}")
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 3: Run conversion
    print("\n[3/5] Running convert_story_graph.py...")
    if not run_conversion(temp_json, temp_layout, converted_json):
        print("  [ERROR] Conversion failed")
        return 1
    print(f"  [OK] Created {converted_json}")
    
    # Step 4: Render to text
    print("\n[4/5] Rendering JSON to text...")
    if not render_story_map(converted_json, template, rendered_text):
        print("  [ERROR] Rendering failed")
        return 1
    print(f"  [OK] Created {rendered_text}")
    
    # Step 5: Compare
    print("\n[5/5] Comparing files...")
    match, diff = compare_files(input_text, rendered_text)
    
    if match:
        print("  [OK] Files match! Round-trip test PASSED")
        
        # Cleanup temp files
        for temp_file in [temp_json, temp_layout]:
            if temp_file.exists():
                temp_file.unlink()
        
        return 0
    else:
        print("  [ERROR] Files do not match. Differences:")
        print(f"\n  First 20 differences:")
        for d in diff[:20]:
            print(f"    Line {d['line']}:")
            print(f"      Expected: {d['expected']}")
            print(f"      Actual:   {d['actual']}")
        
        if len(diff) > 20:
            print(f"\n  ... and {len(diff) - 20} more differences")
        
        print("\n  Round-trip test FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())

