#!/usr/bin/env python3
"""Extract story map from drawio file and create markdown format.
Structure: Purple=Epics, Green=Features, Yellow=Stories, Blue=Actors
Swim lanes (Y position) = Increments (vertical grouping)
Horizontal spacing (X position) = Epic/Feature/Story alignment

IMPORTANT: Epics and Features belong to ALL increments - only Stories and Actors differ by increment.
"""

import xml.etree.ElementTree as ET
import re
import os
import sys
from collections import defaultdict

def get_geometry(cell):
    """Extract x, y coordinates from cell geometry."""
    geom = cell.find('mxGeometry')
    if geom is not None:
        x = float(geom.get('x', 0))
        y = float(geom.get('y', 0))
        return x, y
    return None, None

def get_fill_color(cell):
    """Extract fill color from cell style."""
    style = cell.get('style', '')
    match = re.search(r'fillColor=([^;]+)', style)
    if match:
        return match.group(1)
    return None

def extract_story_map(drawio_file, output_file):
    """Extract story map structure from drawio and write to markdown."""
    tree = ET.parse(drawio_file)
    root = tree.getroot()
    
    # Color mappings
    EPIC_COLOR = '#e1d5e7'  # Purple
    FEATURE_COLOR = '#d5e8d4'  # Green
    STORY_COLOR = '#fff2cc'  # Yellow
    ACTOR_COLOR = '#dae8fc'  # Blue
    
    # Extract increments first to establish swim lane boundaries
    # Increment names are in white boxes (strokeColor=#f8f7f7) positioned to the left of epics (negative X)
    increments = {}
    generic_increments = {}  # Store generic increment_* cells as fallback
    
    # First pass: find white boxes with negative X (these are the descriptive increment names)
    for cell in root.findall('.//mxCell'):
        value = cell.get('value', '').strip()
        if not value:
            continue
        # Handle HTML entities
        value = value.replace('&amp;nbsp;', ' ').replace('&amp;', '&').replace('&lt;br&gt;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('\n', ' ').replace('\r', ' ').strip()
        style = cell.get('style', '')
        x, y = get_geometry(cell)
        
        # Check if this is an increment name cell: white box (strokeColor=#f8f7f7) to the left of epics (negative X)
        if 'strokeColor=#f8f7f7' in style and value and x is not None and y is not None:
            if x < 0:
                # This is a descriptive increment name - prioritize these
                increments[y] = {'name': value, 'y': y, 'x': x}
            elif cell.get('id', '').startswith('increment_') and not cell.get('id', '').endswith('_line'):
                # This is a generic increment_* cell - store as fallback
                generic_increments[y] = {'name': value, 'y': y, 'x': x}
    
    # Second pass: use generic increment_* cells only for Y positions we didn't find descriptive names
    for y, inc_data in generic_increments.items():
        if y not in increments:
            increments[y] = inc_data
    
    # Sort increments by Y to establish boundaries (swim lanes) and assign increment numbers
    sorted_increments = sorted(increments.items(), key=lambda x: x[1]['y'])
    increment_boundaries = []
    for i, (y_key, inc_data) in enumerate(sorted_increments):
        inc_num = i + 1  # Assign increment number based on Y position order
        y_start = inc_data['y']
        if i + 1 < len(sorted_increments):
            y_end = (inc_data['y'] + sorted_increments[i + 1][1]['y']) / 2
        else:
            y_end = float('inf')
        increment_boundaries.append((inc_num, y_start, y_end, inc_data['name']))
    
    # Extract ALL epics and features (they belong to all increments)
    epics = {}  # {epic_id: {name, x, y}}
    features = {}  # {feature_id: {name, x, y, epic_id}}
    
    # Extract stories and actors by increment (they differ per increment)
    stories_by_increment = defaultdict(lambda: defaultdict(list))  # {increment: {feature_id: [stories]}}
    actors_by_increment = defaultdict(lambda: defaultdict(list))  # {increment: {epic_id: [actors]}}
    
    for cell in root.findall('.//mxCell[@id]'):
        cell_id = cell.get('id', '')
        value = cell.get('value', '').strip()
        
        if not value:
            continue
            
        value = value.replace('&amp;nbsp;', ' ').replace('&amp;', '&')
        x, y = get_geometry(cell)
        fill_color = get_fill_color(cell)
        
        if x is None or y is None:
            continue
        
        # Determine which increment this cell belongs to (for stories and actors)
        increment = None
        for inc_num, y_start, y_end, _ in increment_boundaries:
            if y_start <= y < y_end:
                increment = inc_num
                break
        
        if increment is None and increment_boundaries:
            closest = min(increment_boundaries, key=lambda b: abs(b[1] - y))
            increment = closest[0]
        
        # Extract EPICS (purple) - belong to all increments
        if fill_color == EPIC_COLOR or (cell_id.startswith('epic') and cell_id[4:].isdigit()):
            epic_num = int(cell_id[4:]) if cell_id[4:].isdigit() else None
            if epic_num:
                epics[epic_num] = {'name': value, 'x': x, 'y': y}
        
        # Extract FEATURES (green) - belong to all increments
        elif fill_color == FEATURE_COLOR or re.match(r'^e\d+f\d+$', cell_id):
            match = re.match(r'^e(\d+)f(\d+)$', cell_id)
            if match:
                epic_num = int(match.group(1))
                feat_num = int(match.group(2))
                features[cell_id] = {
                    'name': value,
                    'x': x,
                    'y': y,
                    'epic_id': epic_num
                }
        
        # Extract STORIES (yellow) - differ by increment
        elif fill_color == STORY_COLOR or re.match(r'^e\d+f\d+s\d+$', cell_id):
            match = re.match(r'^e(\d+)f(\d+)s(\d+)$', cell_id)
            if match:
                epic_num = int(match.group(1))
                feat_num = int(match.group(2))
                feat_id = f'e{epic_num}f{feat_num}'
                if increment:
                    stories_by_increment[increment][feat_id].append({
                        'id': cell_id,
                        'name': value,
                        'x': x,
                        'y': y
                    })
        
        # Extract ACTORS (blue) - differ by increment
        elif fill_color == ACTOR_COLOR or cell_id.startswith('user_'):
            if increment:
                # Find which epic this actor belongs to (by X position proximity)
                epic_positions = [(eid, edata['x']) for eid, edata in epics.items()]
                if epic_positions:
                    closest_epic = min(epic_positions, key=lambda e: abs(e[1] - x))
                    epic_id = closest_epic[0]
                    actors_by_increment[increment][epic_id].append({
                        'id': cell_id,
                        'name': value,
                        'x': x,
                        'y': y
                    })
    
    # Organize features by epic (for all increments)
    features_by_epic = defaultdict(list)
    for feat_id, feat_data in features.items():
        epic_id = feat_data['epic_id']
        features_by_epic[epic_id].append((feat_id, feat_data))
    
    # Write markdown - Group by increment first
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Increment\n")
        f.write("    Epic (Purple)\n")
        f.write("        Feature (Green)\n")
        f.write("            Actor (Blue) - above Story\n")
        f.write("            Story (Yellow)\n")
        f.write("\n")
        
        # Write each increment
        for inc_num, _, _, inc_name in increment_boundaries:
            f.write(f"## Increment {inc_num} : {inc_name}\n\n")
            
            # Get all epics, sorted by X (horizontal grouping)
            epic_items = sorted(epics.items(), key=lambda x: x[1]['x'])
            
            for epic_id, epic_data in epic_items:
                f.write(f"{epic_data['name']}\n")
                
                # Get features for this epic, sorted by X (horizontal grouping)
                feature_list = sorted(features_by_epic[epic_id],
                                     key=lambda x: x[1]['x'])
                
                for feat_id, feat_data in feature_list:
                    f.write(f"\t{feat_data['name']}\n")
                    
                    # Get stories and actors for this feature in this increment
                    story_list = sorted(stories_by_increment[inc_num].get(feat_id, []),
                                      key=lambda s: s['x'])
                    actors_for_epic = sorted(actors_by_increment[inc_num].get(epic_id, []),
                                           key=lambda a: a['x'])
                    
                    # Match actors to stories by X position (actor above story)
                    # Create pairs: (actor, story) sorted by X position
                    pairs = []
                    used_stories = set()
                    
                    # Match each actor to closest story by X position
                    for actor in actors_for_epic:
                        available_stories = [s for s in story_list if s['id'] not in used_stories]
                        if available_stories:
                            closest_story = min(available_stories, key=lambda s: abs(s['x'] - actor['x']))
                            pairs.append((actor, closest_story))
                            used_stories.add(closest_story['id'])
                        else:
                            pairs.append((actor, None))
                    
                    # Add unmatched stories
                    for story in story_list:
                        if story['id'] not in used_stories:
                            pairs.append((None, story))
                    
                    # Sort pairs by X position (use actor x or story x)
                    pairs.sort(key=lambda p: p[0]['x'] if p[0] else p[1]['x'])
                    
                    # Write pairs: actor above story
                    for actor, story in pairs:
                        if actor:
                            f.write(f"\t\t{actor['name']}\n")
                        if story:
                            f.write(f"\t\t\t{story['name']}\n")
                
                f.write("\n")
            
            f.write("\n")

if __name__ == '__main__':
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Allow input file to be specified as command line argument, or use default
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        if not os.path.isabs(input_file):
            input_file = os.path.join(script_dir, input_file)
    else:
        input_file = os.path.join(script_dir, 'story-map.drawio')
    
    # Allow output file to be specified as second argument, or use default
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        if not os.path.isabs(output_file):
            output_file = os.path.join(script_dir, output_file)
    else:
        output_file = os.path.join(script_dir, 'story-map-required-from-drawio.md')
    
    extract_story_map(input_file, output_file)
