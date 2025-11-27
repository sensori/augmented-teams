#!/usr/bin/env python3
"""Extract story map from drawio file and create markdown format.
Structure: Purple=Epics, Green=Features, Yellow=Stories, Blue=Actors
Swim lanes (Y position) = Increments (vertical grouping)
Horizontal spacing (X position) = Epic/Feature/Story alignment

IMPORTANT: Epics and Features belong to ALL increments - only Stories and Actors differ by increment.
"""

import xml.etree.ElementTree as ET
import re
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
    increments = {}
    for cell in root.findall('.//mxCell[@id]'):
        cell_id = cell.get('id', '')
        if cell_id.startswith('increment_') and not cell_id.endswith('_line'):
            value = cell.get('value', '').strip().replace('&amp;nbsp;', ' ')
            inc_match = re.match(r'increment_(\d+)', cell_id)
            if inc_match and value:
                inc_num = int(inc_match.group(1))
                x, y = get_geometry(cell)
                if y is not None:
                    increments[inc_num] = {'name': value, 'y': y}
    
    # Sort increments by Y to establish boundaries (swim lanes)
    sorted_increments = sorted(increments.items(), key=lambda x: x[1]['y'])
    increment_boundaries = []
    for i, (inc_num, inc_data) in enumerate(sorted_increments):
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
        f.write("            Story (Yellow)\n")
        f.write("        Actor (Blue)\n")
        f.write("\n")
        
        # Write each increment
        for inc_num, _, _, inc_name in increment_boundaries:
            f.write(f"## {inc_name}\n\n")
            
            # Get all epics, sorted by X (horizontal grouping)
            epic_items = sorted(epics.items(), key=lambda x: x[1]['x'])
            
            for epic_id, epic_data in epic_items:
                f.write(f"{epic_data['name']}\n")
                
                # Write actors for this epic in this increment (blue)
                actors_list = sorted(actors_by_increment[inc_num].get(epic_id, []),
                                  key=lambda a: a['x'])
                for actor in actors_list:
                    f.write(f"\t{actor['name']}\n")
                
                # Get features for this epic, sorted by X (horizontal grouping)
                feature_list = sorted(features_by_epic[epic_id],
                                     key=lambda x: x[1]['x'])
                
                for feat_id, feat_data in feature_list:
                    f.write(f"\t{feat_data['name']}\n")
                    
                    # Get stories for this feature in this increment, sorted by X
                    story_list = sorted(stories_by_increment[inc_num].get(feat_id, []),
                                      key=lambda s: s['x'])
                    for story in story_list:
                        f.write(f"\t\t{story['name']}\n")
                
                f.write("\n")
            
            f.write("\n")

if __name__ == '__main__':
    extract_story_map('story-map.drawio', 'story-map-required-from-drawio.md')
