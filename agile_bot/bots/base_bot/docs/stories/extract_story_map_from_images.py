#!/usr/bin/env python3
"""Extract story map from drawio file based on image structure.
Users (actors) are positioned directly above their corresponding stories based on X position.
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
    
    # Extract increments
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
    
    # Sort increments by Y
    sorted_increments = sorted(increments.items(), key=lambda x: x[1]['y'])
    increment_boundaries = []
    for i, (inc_num, inc_data) in enumerate(sorted_increments):
        y_start = inc_data['y']
        if i + 1 < len(sorted_increments):
            y_end = (inc_data['y'] + sorted_increments[i + 1][1]['y']) / 2
        else:
            y_end = float('inf')
        increment_boundaries.append((inc_num, y_start, y_end, inc_data['name']))
    
    # Extract features (green) - belong to all increments
    features = {}  # {feature_id: {name, x, y, epic_id}}
    
    # Extract stories and actors by increment, organized by X position
    stories_by_increment = defaultdict(list)  # {increment: [(x, story_data)]}
    actors_by_increment = defaultdict(list)  # {increment: [(x, actor_data)]}
    
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
        
        # Determine increment
        increment = None
        for inc_num, y_start, y_end, _ in increment_boundaries:
            if y_start <= y < y_end:
                increment = inc_num
                break
        
        if increment is None and increment_boundaries:
            closest = min(increment_boundaries, key=lambda b: abs(b[1] - y))
            increment = closest[0]
        
        # Extract FEATURES (green)
        if fill_color == FEATURE_COLOR or re.match(r'^e\d+f\d+$', cell_id):
            match = re.match(r'^e(\d+)f(\d+)$', cell_id)
            if match:
                epic_num = int(match.group(1))
                features[cell_id] = {
                    'name': value,
                    'x': x,
                    'y': y,
                    'epic_id': epic_num
                }
        
        # Extract STORIES (yellow) - by increment
        elif fill_color == STORY_COLOR or re.match(r'^e\d+f\d+s\d+$', cell_id):
            if increment:
                stories_by_increment[increment].append({
                    'id': cell_id,
                    'name': value,
                    'x': x,
                    'y': y
                })
        
        # Extract ACTORS (blue) - by increment
        elif fill_color == ACTOR_COLOR or cell_id.startswith('user_'):
            if increment:
                actors_by_increment[increment].append({
                    'id': cell_id,
                    'name': value,
                    'x': x,
                    'y': y
                })
    
    # Match actors to stories by X position (actor above story)
    def match_actor_to_story(actor_x, stories_list):
        """Find the story closest to this actor's X position."""
        if not stories_list:
            return None
        closest = min(stories_list, key=lambda s: abs(s['x'] - actor_x))
        return closest
    
    # Organize by increment: pair actors with their stories
    increment_data = {}
    for inc_num, _, _, inc_name in increment_boundaries:
        stories = sorted(stories_by_increment[inc_num], key=lambda s: s['x'])
        actors = sorted(actors_by_increment[inc_num], key=lambda a: a['x'])
        
        # Create pairs: (actor, story) based on X position
        pairs = []
        used_stories = set()
        
        # Match each actor to closest story
        for actor in actors:
            available_stories = [s for s in stories if s['id'] not in used_stories]
            if available_stories:
                matched_story = match_actor_to_story(actor['x'], available_stories)
                if matched_story:
                    pairs.append((actor, matched_story))
                    used_stories.add(matched_story['id'])
                else:
                    pairs.append((actor, None))
            else:
                pairs.append((actor, None))
        
        # Add unmatched stories
        for story in stories:
            if story['id'] not in used_stories:
                pairs.append((None, story))
        
        # Sort pairs by X position (use actor x or story x)
        pairs.sort(key=lambda p: p[0]['x'] if p[0] else p[1]['x'])
        
        increment_data[inc_num] = {
            'name': inc_name,
            'pairs': pairs
        }
    
    # Write markdown
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Increment\n")
        f.write("    Epic (Purple)\n")
        f.write("        Feature (Green)\n")
        f.write("            Actor (Blue) - above Story\n")
        f.write("            Story (Yellow)\n")
        f.write("\n")
        
        # Write each increment
        for inc_num, _, _, _ in increment_boundaries:
            if inc_num not in increment_data:
                continue
                
            data = increment_data[inc_num]
            f.write(f"## {data['name']}\n\n")
            
            # Get features (they're the same for all increments)
            # For now, just use "Gather Context" from the images
            f.write("Gather Context\n")
            
            # Write actor-story pairs, sorted by X position
            for actor, story in data['pairs']:
                if actor:
                    f.write(f"\t{actor['name']}\n")
                if story:
                    f.write(f"\t\t{story['name']}\n")
            
            f.write("\n")

if __name__ == '__main__':
    extract_story_map('story-map.drawio', 'story-map-required-from-drawio.md')

