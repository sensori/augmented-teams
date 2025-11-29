"""
DrawIO Story Map Synchronizer for Story Bot (Shared)

Synchronizes story graph structure from DrawIO story map diagrams.
The DrawIO file is the source of truth - this synchronizer reads-only.

Supports two modes:
- Outline mode (shaping): No increments, preserves layout, detects large deletions
- Increments mode (prioritization): Includes increments for marketable releases

Pattern: DrawIO → synchronizer → story-graph-drawio-extracted.json → merge → story_graph.json
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import json
import xml.etree.ElementTree as ET
import re
import sys
import difflib
from datetime import datetime


def get_cell_value(cell) -> str:
    """Extract text value from a cell, handling HTML entities."""
    value = cell.get('value', '')
    value = value.replace('&amp;', '&').replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    value = re.sub(r'<[^>]+>', '', value)
    return value.strip()


def extract_step_from_acceptance_criteria(ac_text: str) -> str:
    """
    Extract step text from acceptance criteria box.
    Handles "When ... Then ..." format.
    
    Args:
        ac_text: Text from acceptance criteria box
    
    Returns:
        Step text (combines When and Then parts)
    """
    # Remove HTML tags and clean up
    text = ac_text.replace('&amp;', '&').replace('&nbsp;', ' ')
    
    # Try to extract "When ... Then ..." format
    when_match = re.search(r'When\s+([^T]+)', text, re.IGNORECASE)
    then_match = re.search(r'Then\s+(.+)', text, re.IGNORECASE)
    
    if when_match and then_match:
        when_part = when_match.group(1).strip()
        then_part = then_match.group(1).strip()
        # Return as single step text or structured format
        return f"{when_part} {then_part}".strip()
    elif when_match:
        return when_match.group(1).strip()
    else:
        # Return cleaned text as-is
        return text.strip()


def extract_story_count_from_value(cell) -> Optional[int]:
    """
    Extract story count/estimated_stories from cell HTML value.
    Checks both bottom position (outline mode) and top-right position (increments mode).
    """
    raw_value = cell.get('value', '')
    
    # First try top-right position (increments mode): "position: absolute; top: 2px; right: 5px; ... X stories"
    top_right_match = re.search(r'position:\s*absolute[^>]*>(\d+)\s*stories', raw_value, re.IGNORECASE | re.DOTALL)
    if top_right_match:
        return int(top_right_match.group(1))
    
    # Try bottom position (outline mode): Look for pattern like "~## stories" or "<number> stories" in HTML
    # Pattern: <span>##</span><span>stories</span> or similar
    match = re.search(r'(\d+)\s*&nbsp;.*?stories', raw_value, re.IGNORECASE)
    if match:
        return int(match.group(1))
    # Also try parsing from HTML structure
    match = re.search(r'<span[^>]*>(\d+)</span>.*?<span[^>]*>stories</span>', raw_value, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def extract_story_type_from_style(style: str) -> str:
    """
    Extract story_type from DrawIO cell style based on fillColor.
    
    Returns:
        'user' (default), 'system', or 'technical'
    """
    if 'fillColor=#1a237e' in style:  # Dark blue - system story
        return 'system'
    elif 'fillColor=#000000' in style or 'fillColor=#000' in style:  # Black - technical story
        return 'technical'
    else:
        return 'user'  # Default (yellow or other)


def extract_geometry(cell) -> Optional[Dict[str, float]]:
    """Extract geometry information from a cell."""
    geom = cell.find('mxGeometry')
    if geom is None:
        return None
    x = float(geom.get('x', 0))
    y = float(geom.get('y', 0))
    width = float(geom.get('width', 0))
    height = float(geom.get('height', 0))
    return {'x': x, 'y': y, 'width': width, 'height': height}


def get_increments_and_boundaries(drawio_path: Path) -> List[Dict[str, Any]]:
    """
    Get all increment squares (white squares on the left) and their boundaries.
    
    Returns:
        List of increment dictionaries with id, name, x, y, width, height
    """
    tree = ET.parse(drawio_path)
    root = tree.getroot()
    cells = root.findall('.//mxCell')
    
    increments = []
    
    for cell in cells:
        cell_id = cell.get('id', '')
        style = cell.get('style', '')
        geom = extract_geometry(cell)
        
        # Check for increment squares: white squares (strokeColor=#f8f7f7) positioned on the left (negative X)
        if 'strokeColor=#f8f7f7' in style and geom and geom['x'] < 0:
            value = get_cell_value(cell)
            if value:  # Only include if it has a name
                increments.append({
                    'id': cell_id,
                    'name': value,
                    'x': geom['x'],
                    'y': geom['y'],
                    'width': geom['width'],
                    'height': geom['height']
                })
    
    # Sort by Y position (top to bottom)
    increments.sort(key=lambda x: x['y'])
    
    return increments


def get_epics_features_and_boundaries(drawio_path: Path) -> Dict[str, Any]:
    """
    Get all epics and features with their boundaries (x, y, width, height).
    
    Returns:
        Dictionary with 'epics' and 'features' lists
    """
    tree = ET.parse(drawio_path)
    root = tree.getroot()
    cells = root.findall('.//mxCell')
    
    epics = []
    features = []
    
    for cell in cells:
        cell_id = cell.get('id', '')
        style = cell.get('style', '')
        value = get_cell_value(cell)
        geom = extract_geometry(cell)
        
        if geom is None:
            continue
        
        # Epics: purple boxes (fillColor=#e1d5e7)
        # NEVER match by ID - extract all epics by position/containment only
        if 'fillColor=#e1d5e7' in style:
            epic_data = {
                'id': cell_id,
                'name': value,
                'epic_num': None,  # Will assign by position/order
                'x': geom['x'],
                'y': geom['y'],
                'width': geom['width'],
                'height': geom['height']
            }
            # Extract estimated_stories from cell HTML value
            estimated_stories = extract_story_count_from_value(cell)
            if estimated_stories:
                epic_data['estimated_stories'] = estimated_stories
                epic_data['total_stories'] = estimated_stories  # Also set total_stories
            epics.append(epic_data)
        
        # Features: green boxes (fillColor=#d5e8d4)
        # NEVER match by ID - extract all features by position/containment only
        elif 'fillColor=#d5e8d4' in style:
            feature_data = {
                'id': cell_id,
                'name': value,
                'epic_num': None,  # Will assign by position/containment
                'feat_num': None,  # Will assign by position/order within epic
                'x': geom['x'],
                'y': geom['y'],
                'width': geom['width'],
                'height': geom['height']
            }
            # Extract estimated_stories (story_count) from cell HTML value
            estimated_stories = extract_story_count_from_value(cell)
            if estimated_stories:
                feature_data['estimated_stories'] = estimated_stories
                feature_data['story_count'] = estimated_stories  # Legacy field
                feature_data['total_stories'] = estimated_stories  # Also set total_stories
            features.append(feature_data)
    
    # Assign epic_num to epics by position/order (left to right, top to bottom)
    epics.sort(key=lambda x: (x['x'], x['y']))
    for idx, epic in enumerate(epics, 1):
        if epic.get('epic_num') is None:
            epic['epic_num'] = idx
    
    # Assign epic_num to features by position/containment (X coordinate within epic bounds)
    for feature in features:
        if feature['epic_num'] is None:
            # Find which epic contains this feature based on X position/containment
            feature_x = feature['x']
            for epic in sorted(epics, key=lambda e: e['x']):
                epic_x = epic['x']
                epic_width = epic.get('width', 0)
                epic_right = epic_x + epic_width if epic_width > 0 else float('inf')
                # Feature belongs to epic if it's within epic's horizontal bounds
                if epic_x <= feature_x <= epic_right:
                    feature['epic_num'] = epic['epic_num']
                    break
            # If still None, assign to closest epic by X position
            if feature['epic_num'] is None and epics:
                closest_epic = min(epics, key=lambda e: abs(e['x'] - feature['x']))
                feature['epic_num'] = closest_epic['epic_num']
    
    # Assign feat_num to features by position/order within each epic (left to right)
    for epic in epics:
        epic_features = [f for f in features if f['epic_num'] == epic['epic_num']]
        # Sort by X position to get order
        epic_features.sort(key=lambda f: f['x'])
        # Assign feat_num based on order (starting from 1)
        for idx, feature in enumerate(epic_features, 1):
            if feature.get('feat_num') is None:
                feature['feat_num'] = idx
    
    # Sort features by epic_num, then feat_num, then x
    features.sort(key=lambda x: (x['epic_num'] if x['epic_num'] is not None else 999, 
                                  x['feat_num'] if x['feat_num'] is not None else 999, 
                                  x['x']))
    
    return {
        'epics': epics,
        'features': features
    }


def build_stories_for_epics_features(drawio_path: Path, epics: List[Dict], features: List[Dict], 
                                     return_layout: bool = False) -> Dict[str, Any]:
    """
    Go through each epic and feature, and build all stories.
    Preserves layout and spacing from DrawIO.
    
    Args:
        drawio_path: Path to DrawIO file
        epics: List of epic dictionaries
        features: List of feature dictionaries
        return_layout: If True, also return layout data (X/Y coordinates) for stories
    
    Returns:
        Dictionary with epics containing features containing stories.
        If return_layout=True, also includes 'layout' key with story coordinates.
    """
    tree = ET.parse(drawio_path)
    root = tree.getroot()
    cells = root.findall('.//mxCell')
    
    # Extract all stories
    all_stories = []
    user_cells = []
    acceptance_criteria_cells = []
    
    for cell in cells:
        cell_id = cell.get('id', '')
        style = cell.get('style', '')
        value = get_cell_value(cell)
        geom = extract_geometry(cell)
        
        if geom is None:
            continue
        
        # Acceptance criteria: wider boxes (width > 100, height > 50, rounded=0, yellow fill)
        # These appear below stories in exploration mode
        # Check for AC boxes first to exclude them from story detection
        is_ac_box = (cell_id.startswith('ac_') or 
                    ('fillColor=#fff2cc' in style and 'rounded=0' in style and 
                     geom['width'] > 100 and geom['height'] > 50))
        
        if is_ac_box:
            # This is an acceptance criteria box
            # Extract step text from value (handles "When ... Then ..." format)
            ac_text = value
            acceptance_criteria_cells.append({
                'id': cell_id,
                'text': ac_text,
                'x': geom['x'],
                'y': geom['y'],
                'width': geom['width'],
                'height': geom['height']
            })
            continue  # Skip story detection for AC boxes
        
        # Stories: detect by fillColor (yellow #fff2cc, dark blue #1a237e, black #000000)
        # NEVER match by ID - extract all stories by position/containment only
        # Exclude AC boxes (already handled above)
        is_story = ('fillColor=#fff2cc' in style or 'fillColor=#1a237e' in style or 'fillColor=#000000' in style or 'fillColor=#000' in style)
        if is_story:
            # Extract all stories - will assign to features by name matching and position/containment
            story_type = extract_story_type_from_style(style)
            all_stories.append({
                'id': cell_id,
                'name': value,
                'epic_num': None,  # Will assign by position/containment
                'feat_num': None,  # Will assign by name matching and position/containment
                'x': geom['x'],
                'y': geom['y'],
                'width': geom['width'],
                'height': geom['height'],
                'story_type': story_type
            })
        
        # Legacy AC detection (should not be reached if AC boxes are detected above)
        elif ('fillColor=#fff2cc' in style and 'rounded=0' in style and 
              geom['width'] > 100 and geom['height'] > 50):
            # This is likely an acceptance criteria box
            # Extract step text from value (handles "When ... Then ..." format)
            ac_text = value
            acceptance_criteria_cells.append({
                'id': cell_id,
                'text': ac_text,
                'x': geom['x'],
                'y': geom['y'],
                'width': geom['width'],
                'height': geom['height']
            })
        
        # Users: blue boxes (fillColor=#dae8fc)
        elif 'fillColor=#dae8fc' in style:
            user_name = value
            if user_name:
                user_cells.append({
                    'id': cell_id,
                    'name': user_name,
                    'x': geom['x'],
                    'y': geom['y']
                })
    
    # Assign epic/feature to stories by position/containment and name matching (NEVER by ID)
    for story in all_stories:
        story_x = story['x']
        story_y = story['y']
        story_name = story['name'].lower()
        
        # Assign epic by position/containment (X coordinate within epic bounds)
        if story['epic_num'] is None:
            for epic in sorted(epics, key=lambda e: e['x']):
                epic_x = epic['x']
                epic_width = epic.get('width', 0)
                epic_right = epic_x + epic_width if epic_width > 0 else float('inf')
                # Story belongs to epic if it's within epic's horizontal bounds
                if epic_x <= story_x <= epic_right:
                    story['epic_num'] = epic['epic_num']
                    break
            # If still None, assign to closest epic by X position
            if story['epic_num'] is None and epics:
                closest_epic = min(epics, key=lambda e: abs(e['x'] - story_x))
                story['epic_num'] = closest_epic['epic_num']
        
        # Assign feature by name matching (fuzzy) AND position/containment
        if story['epic_num'] is not None:
            epic_features = [f for f in features if f['epic_num'] == story['epic_num']]
            if epic_features:
                # First, try to match by name (fuzzy matching)
                best_match = None
                best_similarity = 0.0
                
                for feature in epic_features:
                    feature_name = feature['name'].lower()
                    # Check if story name contains feature name or vice versa (exact match)
                    if feature_name in story_name or story_name in feature_name:
                        similarity = 1.0
                    else:
                        # Fuzzy match using SequenceMatcher
                        similarity = difflib.SequenceMatcher(None, story_name, feature_name).ratio()
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = feature
                
                # If fuzzy match found (similarity > 0.3), verify by position/containment
                if best_match and best_similarity > 0.3:
                    feature_x = best_match['x']
                    feature_width = best_match.get('width', 200)
                    feature_right = feature_x + feature_width
                    # Verify story is within feature's horizontal bounds
                    if feature_x <= story_x <= feature_right:
                        story['feat_num'] = best_match.get('feat_num', 0)
                
                # If no fuzzy match or position doesn't match, assign by position/containment only
                if story['feat_num'] is None:
                    for feature in sorted(epic_features, key=lambda f: f['x']):
                        feature_x = feature['x']
                        feature_width = feature.get('width', 200)
                        feature_right = feature_x + feature_width
                        # Story belongs to feature if it's within feature's horizontal bounds
                        if feature_x <= story_x <= feature_right:
                            story['feat_num'] = feature.get('feat_num', 0)
                            break
                    
                    # If still None, assign to closest feature by X position
                    if story['feat_num'] is None:
                        closest_feature = min(epic_features, key=lambda f: abs(f['x'] - story_x))
                        story['feat_num'] = closest_feature.get('feat_num', 0)
    
    # Match users to stories based on X position alignment
    stories_with_users = {}
    for story in all_stories:
        story_x = story['x']
        story_y = story['y']
        tolerance = 25  # pixels
        
        story_users = []
        for user_cell in user_cells:
            user_x = user_cell['x']
            user_y = user_cell['y']
            
            # Check if user is horizontally aligned with story (within tolerance) and above the story
            if abs(user_x - story_x) <= tolerance and user_y < story_y:
                user_name = user_cell['name']
                # Only add if not already in list (remove duplicates)
                if user_name not in story_users:
                    story_users.append(user_name)
        
        stories_with_users[story['id']] = story_users
    
    # Assign sequential order based on left-to-right position and vertical stacking
    _assign_sequential_order(all_stories)
    
    # Inherit users from previous story if current story has no users
    # Sort all stories by sequential_order to process in order
    sorted_stories = sorted(all_stories, key=lambda s: (
        s.get('sequential_order', 999) if isinstance(s.get('sequential_order'), (int, float)) else 999,
        s['x'], s['y']
    ))
    
    last_users = []
    for story in sorted_stories:
        if not stories_with_users.get(story['id']):
            # No users assigned, inherit from previous story
            if last_users:
                stories_with_users[story['id']] = last_users.copy()
        else:
            # Story has users, deduplicate
            current_users = stories_with_users[story['id']]
            deduplicated = []
            for user in current_users:
                if user not in deduplicated:
                    deduplicated.append(user)
            stories_with_users[story['id']] = deduplicated
            last_users = deduplicated.copy()
    
    # Assign sequential order to epics (left to right)
    sorted_epics = sorted(epics, key=lambda x: (x['x'], x['epic_num']))
    for idx, epic in enumerate(sorted_epics, 1):
        epic['sequential_order'] = idx
    
    # Assign sequential order to features (left to right within each epic)
    for epic in sorted_epics:
        epic_features = sorted([f for f in features if f['epic_num'] == epic['epic_num']], 
                               key=lambda x: (x['x'], x.get('feat_num', 0)))
        for idx, feature in enumerate(epic_features, 1):
            feature['sequential_order'] = idx
    
    # Build epic/feature/story hierarchy
    result = {'epics': []}
    
    # Track which stories have been assigned to prevent duplicates
    assigned_story_ids = set()
    
    for epic in sorted_epics:
        epic_data = {
            'name': epic['name'],
            'users': [],
            'sequential_order': epic['sequential_order'],
            'features': []
        }
        # Include estimated_stories if present
        if 'estimated_stories' in epic:
            epic_data['estimated_stories'] = epic['estimated_stories']
        
        # Get epic-level users (from first story in epic)
        epic_stories = [s for s in all_stories if s['epic_num'] == epic['epic_num']]
        if epic_stories:
            first_story = min(epic_stories, key=lambda s: (
                s.get('feat_num') if s.get('feat_num') is not None else 999,
                s['x'], s['y']
            ))
            if first_story['id'] in stories_with_users:
                epic_data['users'] = stories_with_users[first_story['id']]
        
        # Get features for this epic, sorted by X position
        epic_features = sorted([f for f in features if f['epic_num'] == epic['epic_num']], 
                               key=lambda x: (x['x'], x.get('feat_num', 0)))
        
        for feature in epic_features:
            feature_data = {
                'name': feature['name'],
                'users': [],
                'sequential_order': feature['sequential_order'],
                'stories': []
            }
            # Include estimated_stories/story_count if present
            if 'estimated_stories' in feature:
                feature_data['estimated_stories'] = feature['estimated_stories']
                feature_data['story_count'] = feature['estimated_stories']  # Legacy field
            elif 'story_count' in feature:
                feature_data['story_count'] = feature['story_count']
                feature_data['estimated_stories'] = feature['story_count']  # New field
            
            # Get stories for this feature based on feat_num (assigned by position earlier)
            feat_stories = [s for s in epic_stories 
                          if s['epic_num'] == epic['epic_num'] and s.get('feat_num') == feature.get('feat_num')]
            if feat_stories:
                first_story = min(feat_stories, key=lambda s: (s['x'], s['y']))
                if first_story['id'] in stories_with_users:
                    feature_data['users'] = stories_with_users[first_story['id']]
            
            # Get stories for this feature, sorted by sequential_order
            feat_stories.sort(key=lambda s: (
                s.get('sequential_order', 999) if isinstance(s.get('sequential_order'), (int, float)) else 999,
                s['x']
            ))
            
            for story in feat_stories:
                # Skip if this story has already been assigned to another feature (prevent duplicates)
                if story['id'] in assigned_story_ids:
                    continue
                
                story_data = {
                    'name': story['name'],
                    'users': stories_with_users.get(story['id'], [])
                }
                if 'sequential_order' in story:
                    story_data['sequential_order'] = story['sequential_order']
                if 'story_type' in story and story['story_type'] != 'user':
                    story_data['story_type'] = story['story_type']
                
                # Match acceptance criteria to this story (wider boxes below story)
                story_x = story['x']
                story_y = story['y']
                story_steps = []
                
                # Find acceptance criteria boxes below this story
                # Acceptance criteria should be:
                # - Below the story (y > story_y + story_height)
                # - Horizontally aligned (within tolerance of story_x)
                tolerance_x = 30
                for ac in acceptance_criteria_cells:
                    ac_x = ac['x']
                    ac_y = ac['y']
                    # Check if acceptance criteria is below story and aligned
                    if (ac_y > story_y + 50 and  # Below story (story height ~50)
                        abs(ac_x - story_x) < tolerance_x):  # Aligned horizontally
                        # Extract step from acceptance criteria text
                        step_text = extract_step_from_acceptance_criteria(ac['text'])
                        if step_text:
                            story_steps.append(step_text)
                
                # Add Steps if found
                if story_steps:
                    story_data['Steps'] = story_steps
                
                feature_data['stories'].append(story_data)
                assigned_story_ids.add(story['id'])  # Mark this story as assigned
            
            epic_data['features'].append(feature_data)
        
        result['epics'].append(epic_data)
    
    # Build layout data if requested
    if return_layout:
        layout_data = {}
        
        # Store epic coordinates and dimensions
        for epic in sorted_epics:
            epic_key = f"EPIC|{epic['name']}"
            layout_data[epic_key] = {
                'x': epic['x'],
                'y': epic['y'],
                'width': epic.get('width', 0),
                'height': epic.get('height', 0)
            }
        
        # Store feature coordinates and dimensions
        for feature in features:
            epic = next((e for e in sorted_epics if e['epic_num'] == feature['epic_num']), None)
            if epic:
                feature_key = f"FEATURE|{epic['name']}|{feature['name']}"
                layout_data[feature_key] = {
                    'x': feature['x'],
                    'y': feature['y'],
                    'width': feature.get('width', 0),
                    'height': feature.get('height', 0)
                }
        
        # Store story coordinates
        for story in all_stories:
            # Create key: epic_name|feature_name|story_name
            epic = next((e for e in sorted_epics if e['epic_num'] == story['epic_num']), None)
            if epic:
                epic_features = sorted([f for f in features if f['epic_num'] == epic['epic_num']], 
                                      key=lambda x: (x['x'], x.get('feat_num', 0)))
                feature = next((f for f in epic_features if f.get('feat_num') == story.get('feat_num')), None)
                if feature:
                    key = f"{epic['name']}|{feature['name']}|{story['name']}"
                    layout_data[key] = {
                        'x': story['x'],
                        'y': story['y']
                    }
        
        # Store user coordinates - match users to their stories/epics/features
        # Skip users at top of map (y < 50) - these are "deleted" users
        for user_cell in user_cells:
            user_name = user_cell['name']
            user_x = user_cell['x']
            user_y = user_cell['y']
            
            # Skip users at top of map (deleted users)
            if user_y < 50:
                continue
            
            # Try to find which story this user is associated with
            tolerance = 25
            matched = False
            for story in all_stories:
                story_x = story['x']
                story_y = story['y']
                # User is above and horizontally aligned with story
                if abs(user_x - story_x) <= tolerance and user_y < story_y:
                    epic = next((e for e in sorted_epics if e['epic_num'] == story['epic_num']), None)
                    if epic:
                        epic_features = sorted([f for f in features if f['epic_num'] == epic['epic_num']], 
                                              key=lambda x: (x['x'], x.get('feat_num', 0)))
                        feature = next((f for f in epic_features if f.get('feat_num') == story.get('feat_num')), None)
                        if feature:
                            # Story-level user: epic_name|feature_name|story_name|user_name
                            story_key = f"{epic['name']}|{feature['name']}|{story['name']}"
                            user_key = f"{story_key}|{user_name}"
                            layout_data[user_key] = {
                                'x': user_x,
                                'y': user_y
                            }
                            matched = True
                            break
            
            # If not matched to a story, check if it's epic or feature level
            if not matched:
                # Check epic level (users above epic Y position)
                for epic in sorted_epics:
                    if abs(user_x - epic['x']) <= 100 and user_y < epic['y'] + 100:
                        # Epic-level user: epic_name|user_name
                        user_key = f"{epic['name']}|{user_name}"
                        layout_data[user_key] = {
                            'x': user_x,
                            'y': user_y
                        }
                        matched = True
                        break
                
                # Check feature level (users above feature Y position)
                if not matched:
                    for feature in features:
                        if abs(user_x - feature['x']) <= 100 and user_y < feature['y'] + 100:
                            epic = next((e for e in sorted_epics if e['epic_num'] == feature['epic_num']), None)
                            if epic:
                                # Feature-level user: epic_name|feature_name|user_name
                                user_key = f"{epic['name']}|{feature['name']}|{user_name}"
                                layout_data[user_key] = {
                                    'x': user_x,
                                    'y': user_y
                                }
                                matched = True
                                break
        
        result['layout'] = layout_data
    
    return result


def _assign_sequential_order(all_stories: List[Dict]):
    """
    Assign sequential_order to stories based on left-to-right position.
    When a story is below another story (higher Y), use num.num format.
    Sequential order is global across all stories in the map.
    """
    # Sort all stories by X position (left to right), then by Y position (top to bottom)
    all_stories.sort(key=lambda x: (x['x'], x['y']))
    
    # Tolerance for considering stories at the same X position (for vertical stacking)
    x_tolerance = 30  # pixels
    
    stories_by_x_group = {}
    
    # Group stories by X position (within tolerance)
    for story in all_stories:
        story_x = story['x']
        
        # Find if this story belongs to an existing X group
        found_group = False
        for group_x, group_stories in stories_by_x_group.items():
            if abs(story_x - group_x) <= x_tolerance:
                # Add to existing group
                group_stories.append(story)
                found_group = True
                break
        
        if not found_group:
            # Create new X group
            stories_by_x_group[story_x] = [story]
    
    # Sort X groups by X position
    sorted_x_groups = sorted(stories_by_x_group.items(), key=lambda x: x[0])
    
    # Assign sequential order globally
    current_order = 1
    for group_x, group_stories in sorted_x_groups:
        # Sort stories in this group by Y position (top to bottom)
        group_stories.sort(key=lambda x: x['y'])
        
        if len(group_stories) == 1:
            # Single story - just assign order number
            group_stories[0]['sequential_order'] = current_order
            current_order += 1
        else:
            # Multiple stories stacked vertically - use num.num format
            base_order = current_order
            for idx, story in enumerate(group_stories):
                if idx == 0:
                    # First story in stack gets base order
                    story['sequential_order'] = base_order
                else:
                    # Subsequent stories get base_order.idx format
                    story['sequential_order'] = float(f"{base_order}.{idx}")
            current_order += 1


def build_stories_for_increments(drawio_path: Path, increments: List[Dict], 
                                 epics: List[Dict], features: List[Dict]) -> List[Dict[str, Any]]:
    """
    Build stories for each increment based on Y position alignment with increment squares.
    
    Returns:
        List of increment dictionaries with epics, features, and stories
    """
    tree = ET.parse(drawio_path)
    root = tree.getroot()
    cells = root.findall('.//mxCell')
    
    # Extract all stories
    all_stories = []
    user_cells = []
    
    for cell in cells:
        cell_id = cell.get('id', '')
        style = cell.get('style', '')
        value = get_cell_value(cell)
        geom = extract_geometry(cell)
        
        if geom is None:
            continue
        
        # Skip acceptance criteria boxes (they have IDs starting with 'ac_' or are wide yellow boxes)
        is_ac_box = (cell_id.startswith('ac_') or 
                    ('fillColor=#fff2cc' in style and 'rounded=0' in style and 
                     geom['width'] > 100 and geom['height'] > 50))
        if is_ac_box:
            continue  # Skip AC boxes in increments mode too
        
        # Stories: detect by fillColor (yellow #fff2cc, dark blue #1a237e, black #000000)
        # NEVER match by ID - extract all stories by position/containment only
        # Exclude AC boxes (already handled above)
        is_story = ('fillColor=#fff2cc' in style or 'fillColor=#1a237e' in style or 'fillColor=#000000' in style or 'fillColor=#000' in style)
        if is_story:
            story_type = extract_story_type_from_style(style)
            all_stories.append({
                'id': cell_id,
                'name': value,
                'epic_num': None,  # Will assign by position/containment
                'feat_num': None,  # Will assign by name matching and position/containment
                'x': geom['x'],
                'y': geom['y'],
                'story_type': story_type
            })
        
        # Users: blue boxes
        elif 'fillColor=#dae8fc' in style:
            user_name = value
            if user_name:
                user_cells.append({
                    'id': cell_id,
                    'name': user_name,
                    'x': geom['x'],
                    'y': geom['y']
                })
    
    # Assign epic/feature to stories by position/containment and name matching (NEVER by ID)
    for story in all_stories:
        story_x = story['x']
        story_y = story['y']
        story_name = story['name'].lower()
        
        # Assign epic by position/containment (X coordinate within epic bounds)
        if story['epic_num'] is None:
            for epic in sorted(epics, key=lambda e: e['x']):
                epic_x = epic['x']
                epic_width = epic.get('width', 0)
                epic_right = epic_x + epic_width if epic_width > 0 else float('inf')
                # Story belongs to epic if it's within epic's horizontal bounds
                if epic_x <= story_x <= epic_right:
                    story['epic_num'] = epic['epic_num']
                    break
            # If still None, assign to closest epic by X position
            if story['epic_num'] is None and epics:
                closest_epic = min(epics, key=lambda e: abs(e['x'] - story_x))
                story['epic_num'] = closest_epic['epic_num']
        
        # Assign feature by name matching (fuzzy) AND position/containment
        if story['epic_num'] is not None:
            epic_features = [f for f in features if f['epic_num'] == story['epic_num']]
            if epic_features:
                # First, try to match by name (fuzzy matching)
                best_match = None
                best_similarity = 0.0
                
                for feature in epic_features:
                    feature_name = feature['name'].lower()
                    # Check if story name contains feature name or vice versa (exact match)
                    if feature_name in story_name or story_name in feature_name:
                        similarity = 1.0
                    else:
                        # Fuzzy match using SequenceMatcher
                        similarity = difflib.SequenceMatcher(None, story_name, feature_name).ratio()
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = feature
                
                # If fuzzy match found (similarity > 0.3), verify by position/containment
                if best_match and best_similarity > 0.3:
                    feature_x = best_match['x']
                    feature_width = best_match.get('width', 200)
                    feature_right = feature_x + feature_width
                    # Verify story is within feature's horizontal bounds
                    if feature_x <= story_x <= feature_right:
                        story['feat_num'] = best_match.get('feat_num', 0)
                
                # If no fuzzy match or position doesn't match, assign by position/containment only
                if story['feat_num'] is None:
                    for feature in sorted(epic_features, key=lambda f: f['x']):
                        feature_x = feature['x']
                        feature_width = feature.get('width', 200)
                        feature_right = feature_x + feature_width
                        # Story belongs to feature if it's within feature's horizontal bounds
                        if feature_x <= story_x <= feature_right:
                            story['feat_num'] = feature.get('feat_num', 0)
                            break
                    
                    # If still None, assign to closest feature by X position
                    if story['feat_num'] is None:
                        closest_feature = min(epic_features, key=lambda f: abs(f['x'] - story_x))
                        story['feat_num'] = closest_feature.get('feat_num', 0)
    
    # Match users to stories
    stories_with_users = {}
    for story in all_stories:
        story_x = story['x']
        story_y = story['y']
        tolerance = 25
        
        story_users = []
        for user_cell in user_cells:
            user_x = user_cell['x']
            user_y = user_cell['y']
            if abs(user_x - story_x) <= tolerance and user_y < story_y:
                user_name = user_cell['name']
                # Only add if not already in list (remove duplicates)
                if user_name not in story_users:
                    story_users.append(user_name)
        stories_with_users[story['id']] = story_users
    
    # Assign sequential order
    _assign_sequential_order(all_stories)
    
    # Inherit users from previous story if current story has no users
    # Sort all stories by sequential_order to process in order
    sorted_stories = sorted(all_stories, key=lambda s: (
        s.get('sequential_order', 999) if isinstance(s.get('sequential_order'), (int, float)) else 999,
        s['x'], s['y']
    ))
    
    last_users = []
    for story in sorted_stories:
        if not stories_with_users.get(story['id']):
            # No users assigned, inherit from previous story
            if last_users:
                stories_with_users[story['id']] = last_users.copy()
        else:
            # Story has users, deduplicate and update last_users for next story
            current_users = stories_with_users[story['id']]
            # Remove duplicates while preserving order
            deduplicated = []
            for user in current_users:
                if user not in deduplicated:
                    deduplicated.append(user)
            stories_with_users[story['id']] = deduplicated
            last_users = deduplicated.copy()
    
    # Assign stories to increments based on Y position
    # Stories belong to increment if their Y is close to increment's Y (within tolerance)
    increment_tolerance = 100  # pixels - stories within this Y distance belong to increment
    
    result = []
    for inc_idx, increment in enumerate(increments, 1):
        inc_data = {
            'name': increment['name'],
            'priority': inc_idx,
            'epics': []
        }
        
        # Find stories that belong to this increment
        inc_stories = []
        for story in all_stories:
            # Check if story Y is within tolerance of increment Y
            if abs(story['y'] - increment['y']) <= increment_tolerance:
                inc_stories.append(story)
        
        # Build epic/feature/story structure for this increment
        inc_epics = {}
        for story in inc_stories:
            epic_num = story['epic_num']
            feat_num = story['feat_num']
            
            if epic_num not in inc_epics:
                epic = next((e for e in epics if e['epic_num'] == epic_num), None)
                epic_name = epic['name'] if epic else f'Epic {epic_num}'
                epic_order = epic.get('sequential_order', epic_num) if epic else epic_num
                inc_epics[epic_num] = {
                    'name': epic_name,
                    'users': [],
                    'sequential_order': epic_order,
                    'features': {}
                }
            
            if feat_num not in inc_epics[epic_num]['features']:
                feature = next((f for f in features 
                                if f['epic_num'] == epic_num and f.get('feat_num') == feat_num), None)
                feat_name = feature['name'] if feature else f'Feature {feat_num}'
                feat_order = feature.get('sequential_order', feat_num) if feature else feat_num
                inc_epics[epic_num]['features'][feat_num] = {
                    'name': feat_name,
                    'users': [],
                    'sequential_order': feat_order,
                    'stories': []
                }
            
            story_data = {
                'name': story['name'],
                'users': stories_with_users.get(story['id'], [])
            }
            if 'sequential_order' in story:
                story_data['sequential_order'] = story['sequential_order']
            if 'story_type' in story and story['story_type'] != 'user':
                story_data['story_type'] = story['story_type']
            inc_epics[epic_num]['features'][feat_num]['stories'].append(story_data)
        
        # Convert to list format and sort by sequential_order
        sorted_inc_epics = sorted(
            inc_epics.items(),
            key=lambda x: (x[1].get('sequential_order', 999), x[0])
        )
        for epic_num, epic_data in sorted_inc_epics:
            # Sort features by sequential_order
            sorted_features = sorted(
                epic_data['features'].items(),
                key=lambda x: (x[1].get('sequential_order', 999) if isinstance(x[1].get('sequential_order'), (int, float)) else 999,
                              x[0] if x[0] is not None else 999)
            )
            # Sort stories by sequential_order within each feature
            for feat_num, feat_data in sorted_features:
                feat_data['stories'].sort(key=lambda s: (
                    s.get('sequential_order', 999) if isinstance(s.get('sequential_order'), (int, float)) else 999,
                    s.get('sequential_order', '') if isinstance(s.get('sequential_order'), str) else ''
                ))
            epic_data['features'] = [feat_data for feat_num, feat_data in sorted_features]
            inc_data['epics'].append(epic_data)
        
        result.append(inc_data)
    
    return result


def _detect_large_deletions(
    original_data: Dict[str, Any],
    extracted_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Detect large deletions (entire epics or features missing).
    Returns a report of potential accidental deletions.
    """
    deletions = {
        'missing_epics': [],
        'missing_features': [],
        'epics_with_many_missing_stories': [],
        'features_with_many_missing_stories': []
    }
    
    # Build maps for comparison
    original_epics = {epic['name']: epic for epic in original_data.get('epics', [])}
    extracted_epics = {epic['name']: epic for epic in extracted_data.get('epics', [])}
    
    # Find missing epics
    for epic_name, epic in original_epics.items():
        if epic_name not in extracted_epics:
            original_story_count = sum(
                len(f.get('stories', [])) 
                for f in epic.get('features', [])
            )
            deletions['missing_epics'].append({
                'name': epic_name,
                'story_count': original_story_count,
                'feature_count': len(epic.get('features', []))
            })
    
    # Find missing features and epics with many missing stories
    for epic_name, original_epic in original_epics.items():
        if epic_name in extracted_epics:
            extracted_epic = extracted_epics[epic_name]
            
            original_features = {f['name']: f for f in original_epic.get('features', [])}
            extracted_features = {f['name']: f for f in extracted_epic.get('features', [])}
            
            # Find missing features
            for feat_name, feature in original_features.items():
                if feat_name not in extracted_features:
                    deletions['missing_features'].append({
                        'epic': epic_name,
                        'name': feat_name,
                        'story_count': len(feature.get('stories', []))
                    })
            
            # Check for epics with many missing stories
            original_story_count = sum(
                len(f.get('stories', [])) 
                for f in original_epic.get('features', [])
            )
            extracted_story_count = sum(
                len(f.get('stories', [])) 
                for f in extracted_epic.get('features', [])
            )
            
            if original_story_count > 0:
                missing_ratio = (original_story_count - extracted_story_count) / original_story_count
                if missing_ratio > 0.5:  # More than 50% missing
                    deletions['epics_with_many_missing_stories'].append({
                        'name': epic_name,
                        'original_count': original_story_count,
                        'extracted_count': extracted_story_count,
                        'missing_count': original_story_count - extracted_story_count,
                        'missing_ratio': missing_ratio
                    })
            
            # Check for features with many missing stories
            for feat_name, original_feature in original_features.items():
                if feat_name in extracted_features:
                    extracted_feature = extracted_features[feat_name]
                    orig_stories = len(original_feature.get('stories', []))
                    extr_stories = len(extracted_feature.get('stories', []))
                    
                    if orig_stories > 0:
                        missing_ratio = (orig_stories - extr_stories) / orig_stories
                        if missing_ratio > 0.5:  # More than 50% missing
                            deletions['features_with_many_missing_stories'].append({
                                'epic': epic_name,
                                'name': feat_name,
                                'original_count': orig_stories,
                                'extracted_count': extr_stories,
                                'missing_count': orig_stories - extr_stories,
                                'missing_ratio': missing_ratio
                            })
    
    return deletions


def _display_large_deletions(deletions: Dict[str, Any]) -> None:
    """Display large deletion warnings in a prominent format."""
    has_warnings = False
    
    if deletions.get('missing_epics'):
        has_warnings = True
        print("\n" + "!"*80)
        print("WARNING: ENTIRE EPICS MISSING FROM DRAWIO")
        print("!"*80)
        for epic in deletions['missing_epics']:
            print(f"  MISSING EPIC: {epic['name']}")
            print(f"    - {epic['feature_count']} features")
            print(f"    - {epic['story_count']} stories")
            print(f"    - This may be an accidental deletion!")
        print("!"*80)
    
    if deletions.get('missing_features'):
        has_warnings = True
        print("\n" + "!"*80)
        print("WARNING: ENTIRE FEATURES MISSING FROM DRAWIO")
        print("!"*80)
        for feature in deletions['missing_features']:
            print(f"  MISSING FEATURE: {feature['epic']} > {feature['name']}")
            print(f"    - {feature['story_count']} stories")
            print(f"    - This may be an accidental deletion!")
        print("!"*80)
    
    if deletions.get('epics_with_many_missing_stories'):
        has_warnings = True
        print("\n" + "-"*80)
        print("WARNING: EPICS WITH MANY MISSING STORIES (>50%)")
        print("-"*80)
        for epic in deletions['epics_with_many_missing_stories']:
            print(f"  EPIC: {epic['name']}")
            print(f"    - Original: {epic['original_count']} stories")
            print(f"    - Extracted: {epic['extracted_count']} stories")
            print(f"    - Missing: {epic['missing_count']} stories ({epic['missing_ratio']:.1%})")
        print("-"*80)
    
    if deletions.get('features_with_many_missing_stories'):
        has_warnings = True
        print("\n" + "-"*80)
        print("WARNING: FEATURES WITH MANY MISSING STORIES (>50%)")
        print("-"*80)
        for feature in deletions['features_with_many_missing_stories']:
            print(f"  FEATURE: {feature['epic']} > {feature['name']}")
            print(f"    - Original: {feature['original_count']} stories")
            print(f"    - Extracted: {feature['extracted_count']} stories")
            print(f"    - Missing: {feature['missing_count']} stories ({feature['missing_ratio']:.1%})")
        print("-"*80)
    
    if has_warnings:
        print("\n" + "="*80)
        print("RECOMMENDATION: Review these deletions carefully before merging.")
        print("Large batches of deleted stories may indicate accidental deletion.")
        print("="*80 + "\n")


def _flatten_stories_from_original(original_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten all stories from original story graph into a list with context."""
    stories = []
    
    for epic in original_data.get('epics', []):
        epic_name = epic.get('name', '')
        for feature in epic.get('features', []):
            feature_name = feature.get('name', '')
            for story in feature.get('stories', []):
                story_data = {
                    'name': story.get('name', ''),
                    'users': story.get('users', []),
                    'Steps': story.get('Steps', []),
                    'epic_name': epic_name,
                    'feature_name': feature_name
                }
                stories.append(story_data)
    
    return stories


def _flatten_stories_from_extracted(extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten all stories from extracted story graph into a list with context."""
    stories = []
    
    for epic in extracted_data.get('epics', []):
        epic_name = epic.get('name', '')
        for feature in epic.get('features', []):
            feature_name = feature.get('name', '')
            for story in feature.get('stories', []):
                story_data = {
                    'name': story.get('name', ''),
                    'users': story.get('users', []),
                    'sequential_order': story.get('sequential_order'),
                    'epic_name': epic_name,
                    'feature_name': feature_name
                }
                if 'story_type' in story and story.get('story_type') != 'user':
                    story_data['story_type'] = story['story_type']
                stories.append(story_data)
    
    return stories


def _fuzzy_match_story(extracted_story: Dict[str, Any], original_stories: List[Dict[str, Any]], 
                       threshold: float = 0.7) -> Optional[Tuple[Dict[str, Any], float]]:
    """
    Find best matching story from original using fuzzy matching.
    
    Returns:
        Tuple of (matched_story, similarity_score) or None if no match above threshold
    """
    extracted_name = extracted_story['name'].lower()
    best_match = None
    best_score = 0.0
    
    for orig_story in original_stories:
        orig_name = orig_story['name'].lower()
        
        # Calculate similarity
        similarity = difflib.SequenceMatcher(None, extracted_name, orig_name).ratio()
        
        # Bonus for same epic/feature context
        context_bonus = 0.0
        if extracted_story.get('epic_name') == orig_story.get('epic_name'):
            context_bonus += 0.1
        if extracted_story.get('feature_name') == orig_story.get('feature_name'):
            context_bonus += 0.1
        
        # Bonus for user overlap
        extracted_users = set(u.lower() for u in extracted_story.get('users', []))
        orig_users = set(u.lower() for u in orig_story.get('users', []))
        if extracted_users and orig_users:
            user_overlap = len(extracted_users & orig_users) / max(len(extracted_users), len(orig_users))
            context_bonus += user_overlap * 0.1
        
        total_score = min(1.0, similarity + context_bonus)
        
        if total_score > best_score:
            best_score = total_score
            best_match = orig_story
    
    if best_score >= threshold:
        return (best_match, best_score)
    return None


def generate_merge_report(
    extracted_path: Path,
    original_path: Path,
    report_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Generate a merge report comparing extracted and original story graphs.
    
    Args:
        extracted_path: Path to extracted story graph JSON
        original_path: Path to original story graph JSON
        report_path: Optional path to write report JSON
        
    Returns:
        Dictionary containing merge report data
    """
    # Load both JSON files
    with open(extracted_path, 'r', encoding='utf-8') as f:
        extracted_data = json.load(f)
    
    with open(original_path, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    # Flatten stories for comparison
    extracted_stories = _flatten_stories_from_extracted(extracted_data)
    original_stories = _flatten_stories_from_original(original_data)
    
    # Match stories
    exact_matches = []
    fuzzy_matches = []
    new_stories = []
    unmatched_original = []
    
    matched_original_indices = set()
    
    for ext_story in extracted_stories:
        # Try exact match first
        exact_match = None
        for idx, orig_story in enumerate(original_stories):
            if (ext_story['name'].lower() == orig_story['name'].lower() and
                idx not in matched_original_indices):
                exact_match = (orig_story, idx)
                break
        
        if exact_match:
            orig_story, idx = exact_match
            exact_matches.append({
                'extracted': ext_story,
                'original': orig_story,
                'match_type': 'exact',
                'confidence': 1.0
            })
            matched_original_indices.add(idx)
        else:
            # Try fuzzy match
            fuzzy_result = _fuzzy_match_story(ext_story, original_stories)
            if fuzzy_result:
                orig_story, score = fuzzy_result
                # Find index of matched story
                for idx, o in enumerate(original_stories):
                    if o['name'] == orig_story['name'] and idx not in matched_original_indices:
                        fuzzy_matches.append({
                            'extracted': ext_story,
                            'original': orig_story,
                            'match_type': 'fuzzy',
                            'confidence': score
                        })
                        matched_original_indices.add(idx)
                        break
            else:
                # New story in extracted
                new_stories.append(ext_story)
    
    # Find unmatched original stories
    for idx, orig_story in enumerate(original_stories):
        if idx not in matched_original_indices:
            unmatched_original.append(orig_story)
    
    # Build report
    report = {
        'timestamp': datetime.now().isoformat(),
        'extracted_file': str(extracted_path),
        'original_file': str(original_path),
        'summary': {
            'total_extracted_stories': len(extracted_stories),
            'total_original_stories': len(original_stories),
            'exact_matches': len(exact_matches),
            'fuzzy_matches': len(fuzzy_matches),
            'new_stories': len(new_stories),
            'removed_stories': len(unmatched_original)
        },
        'exact_matches': exact_matches,
        'fuzzy_matches': fuzzy_matches,
        'new_stories': new_stories,
        'removed_stories': unmatched_original
    }
    
    # Write report if path provided
    if report_path:
        report_path = Path(report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report


def merge_story_graphs(
    extracted_path: Path,
    original_path: Path,
    report_path: Path,
    output_path: Path
) -> Dict[str, Any]:
    """
    Merge extracted story graph with original, preserving Steps from original.
    
    Args:
        extracted_path: Path to extracted story graph JSON
        original_path: Path to original story graph JSON
        report_path: Path to merge report JSON
        output_path: Path to write merged story graph JSON
        
    Returns:
        Dictionary containing merged story graph
    """
    # Load files
    with open(extracted_path, 'r', encoding='utf-8') as f:
        extracted_data = json.load(f)
    
    with open(original_path, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # Create a lookup map for original stories by epic/feature/name
    original_story_map = {}
    for epic in original_data.get('epics', []):
        epic_name = epic.get('name', '')
        for feature in epic.get('features', []):
            feature_name = feature.get('name', '')
            for story in feature.get('stories', []):
                story_name = story.get('name', '')
                key = f"{epic_name}|{feature_name}|{story_name}"
                original_story_map[key] = story
    
    # Create a map of matches from report
    match_map = {}
    for match in report.get('exact_matches', []):
        ext_story = match['extracted']
        orig_story = match['original']
        key = f"{ext_story['epic_name']}|{ext_story['feature_name']}|{ext_story['name']}"
        match_map[key] = orig_story
    
    for match in report.get('fuzzy_matches', []):
        ext_story = match['extracted']
        orig_story = match['original']
        key = f"{ext_story['epic_name']}|{ext_story['feature_name']}|{ext_story['name']}"
        match_map[key] = orig_story
    
    # Merge: start with extracted structure, add Steps from matches
    merged_data = json.loads(json.dumps(extracted_data))  # Deep copy
    
    # Merge epics
    for epic in merged_data.get('epics', []):
        epic_name = epic.get('name', '')
        for feature in epic.get('features', []):
            feature_name = feature.get('name', '')
            for story in feature.get('stories', []):
                story_name = story.get('name', '')
                key = f"{epic_name}|{feature_name}|{story_name}"
                
                # If we have a match, copy Steps and use extracted users (DrawIO is source of truth)
                if key in match_map:
                    orig_story = match_map[key]
                    if 'Steps' in orig_story:
                        story['Steps'] = orig_story['Steps']
                    # Use extracted users only (DrawIO is source of truth for user associations)
                    # Extracted users are already set in story, so no need to merge
                    pass
    
    # Merge increments (if present)
    for increment in merged_data.get('increments', []):
        for epic in increment.get('epics', []):
            epic_name = epic.get('name', '')
            for feature in epic.get('features', []):
                feature_name = feature.get('name', '')
                for story in feature.get('stories', []):
                    story_name = story.get('name', '')
                    key = f"{epic_name}|{feature_name}|{story_name}"
                    
                    # If we have a match, copy Steps and use extracted users (DrawIO is source of truth)
                    if key in match_map:
                        orig_story = match_map[key]
                        if 'Steps' in orig_story:
                            story['Steps'] = orig_story['Steps']
                        # Use extracted users only (DrawIO is source of truth for user associations)
                        # Extracted users are already set in story, so no need to merge
                        pass
    
    # Write merged result
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    
    return merged_data


def display_merge_report(report: Dict[str, Any]) -> None:
    """Display merge report in a human-readable format."""
    print("\n" + "="*80)
    print("STORY GRAPH MERGE REPORT")
    print("="*80)
    print(f"Generated: {report['timestamp']}")
    print(f"Extracted: {report['extracted_file']}")
    print(f"Original: {report['original_file']}")
    print("\n" + "-"*80)
    print("SUMMARY")
    print("-"*80)
    summary = report['summary']
    print(f"Total Extracted Stories: {summary['total_extracted_stories']}")
    print(f"Total Original Stories: {summary['total_original_stories']}")
    print(f"Exact Matches: {summary['exact_matches']}")
    print(f"Fuzzy Matches: {summary['fuzzy_matches']}")
    print(f"New Stories (in extracted): {summary['new_stories']}")
    print(f"Removed Stories (in original only): {summary['removed_stories']}")
    
    if report['fuzzy_matches']:
        print("\n" + "-"*80)
        print("FUZZY MATCHES (Require Review)")
        print("-"*80)
        for match in report['fuzzy_matches']:
            print(f"\nExtracted: {match['extracted']['name']}")
            print(f"  Epic: {match['extracted']['epic_name']} | Feature: {match['extracted']['feature_name']}")
            print(f"Original: {match['original']['name']}")
            print(f"  Epic: {match['original']['epic_name']} | Feature: {match['original']['feature_name']}")
            print(f"Confidence: {match['confidence']:.2%}")
            print(f"Has Steps: {'Yes' if match['original'].get('Steps') else 'No'}")
    
    if report['new_stories']:
        print("\n" + "-"*80)
        print("NEW STORIES (No match in original)")
        print("-"*80)
        for story in report['new_stories'][:10]:  # Show first 10
            print(f"  - {story['name']} ({story['epic_name']} > {story['feature_name']})")
        if len(report['new_stories']) > 10:
            print(f"  ... and {len(report['new_stories']) - 10} more")
    
    if report['removed_stories']:
        print("\n" + "-"*80)
        print("REMOVED STORIES (In original but not in extracted)")
        print("-"*80)
        for story in report['removed_stories'][:10]:  # Show first 10
            print(f"  - {story['name']} ({story['epic_name']} > {story['feature_name']})")
        if len(report['removed_stories']) > 10:
            print(f"  ... and {len(report['removed_stories']) - 10} more")
    
    # Display large deletions if present
    if 'large_deletions' in report:
        _display_large_deletions(report['large_deletions'])
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("1. Review fuzzy matches above")
    print("2. Confirm which matches are correct")
    print("3. Run merge command to apply changes")
    print("="*80 + "\n")


def synchronize_story_graph_from_drawio_outline(
    drawio_path: Path,
    output_path: Optional[Path] = None,
    original_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Synchronize story graph structure from DrawIO outline (shaping behavior).
    No increments - just epics, features, and stories.
    Preserves layout and spacing to maintain visual clarity.
    Detects and flags large deletions (entire epics/features missing).
    
    Args:
        drawio_path: Path to DrawIO story map outline file (story-map-outline.drawio)
        output_path: Optional path to write extracted JSON
        original_path: Optional path to original story graph for merge report and deletion detection
        
    Returns:
        Dictionary with extracted story graph structure (epics only, no increments)
    """
    # Step 1: Get epics and features
    epics_features = get_epics_features_and_boundaries(drawio_path)
    epics = epics_features['epics']
    features = epics_features['features']
    
    # Step 2: Build stories for epics/features (preserves layout)
    epics_with_stories = build_stories_for_epics_features(drawio_path, epics, features, return_layout=True)
    
    result = {
        'epics': epics_with_stories['epics']
        # No increments for outline
    }
    
    layout_data = epics_with_stories.get('layout', {})
    
    # Write extracted JSON
    if output_path:
        output_path = Path(output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Write separate layout JSON file
        layout_path = output_path.parent.resolve() / f"{output_path.stem}-layout.json"
        # Ensure parent directory exists and is accessible
        try:
            layout_path.parent.mkdir(parents=True, exist_ok=True)
            # Use a temporary file in a shorter path if the target path is too long
            if len(str(layout_path)) > 260:  # Windows MAX_PATH limit
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
                json.dump(layout_data, temp_file, indent=2, ensure_ascii=False)
                temp_file.close()
                import shutil
                shutil.move(temp_file.name, str(layout_path))
            else:
                with open(str(layout_path), 'w', encoding='utf-8') as f:
                    json.dump(layout_data, f, indent=2, ensure_ascii=False)
            print(f"Layout data saved to: {layout_path}")
        except Exception as e:
            print(f"Warning: Could not save layout file to {layout_path}: {e}")
            # Try saving to a shorter path as fallback
            try:
                import tempfile
                fallback_path = Path(tempfile.gettempdir()) / f"{output_path.stem}-layout.json"
                with open(str(fallback_path), 'w', encoding='utf-8') as f:
                    json.dump(layout_data, f, indent=2, ensure_ascii=False)
                print(f"Layout data saved to fallback location: {fallback_path}")
            except Exception as e2:
                print(f"Error: Could not save layout file even to fallback location: {e2}")
        
        # Generate merge report and detect large deletions if original path provided
        if original_path and original_path.exists():
            report_path = output_path.parent / f"{output_path.stem}-merge-report.json"
            report = generate_merge_report(output_path, original_path, report_path)
            
            # Detect large deletions
            with open(original_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
            deletions = _detect_large_deletions(original_data, result)
            report['large_deletions'] = deletions
            
            # Write updated report with deletion info
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            display_merge_report(report)
            print(f"\nMerge report saved to: {report_path}")
    
    return result


def synchronize_story_graph_from_drawio_increments(
    drawio_path: Path,
    output_path: Optional[Path] = None,
    original_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Synchronize story graph structure from DrawIO with increments (prioritization behavior).
    Includes both epics/features/stories AND increments.
    
    Args:
        drawio_path: Path to DrawIO story map file (story-map.drawio)
        output_path: Optional path to write extracted JSON
        original_path: Optional path to original story graph for merge report
        
    Returns:
        Dictionary with extracted story graph structure (epics and increments)
    """
    # Step 1: Get increments
    increments = get_increments_and_boundaries(drawio_path)
    
    # Step 2: Get epics and features
    epics_features = get_epics_features_and_boundaries(drawio_path)
    epics = epics_features['epics']
    features = epics_features['features']
    
    # Step 3: Build stories for epics/features
    epics_with_stories = build_stories_for_epics_features(drawio_path, epics, features)
    
    # Step 4: Build stories for increments
    increments_with_stories = build_stories_for_increments(drawio_path, increments, epics, features)
    
    result = {
        'epics': epics_with_stories['epics'],
        'increments': increments_with_stories
    }
    
    # Write extracted JSON
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Generate merge report if original path provided
        if original_path and original_path.exists():
            report_path = output_path.parent / f"{output_path.stem}-merge-report.json"
            report = generate_merge_report(output_path, original_path, report_path)
            display_merge_report(report)
            print(f"\nMerge report saved to: {report_path}")
    
    return result


# Keep the original function for backward compatibility
# It now delegates to the increments version
def synchronize_story_map_from_drawio(
    drawio_path: Path,
    output_path: Optional[Path] = None,
    original_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Synchronize story graph structure from DrawIO file (backward compatibility).
    Delegates to synchronize_story_graph_from_drawio_increments.
    """
    return synchronize_story_graph_from_drawio_increments(drawio_path, output_path, original_path)


if __name__ == "__main__":
    """Command-line interface for synchronizing story maps from DrawIO."""
    import argparse
    import tempfile
    
    parser = argparse.ArgumentParser(description='Synchronize story graph from DrawIO story map')
    parser.add_argument('drawio_path', type=Path, nargs='?', help='Path to DrawIO story map file')
    parser.add_argument('--output', type=Path, help='Output path for extracted JSON')
    parser.add_argument('--original', type=Path, help='Path to original story graph JSON for merge report')
    parser.add_argument('--merge', action='store_true', help='Merge extracted with original based on report')
    parser.add_argument('--report', type=Path, help='Path to merge report JSON (required for --merge)')
    parser.add_argument('--merged-output', type=Path, help='Output path for merged JSON (default: overwrites original)')
    parser.add_argument('--outline', action='store_true', help='Use outline mode (no increments, for shaping)')
    
    args = parser.parse_args()
    
    try:
        # Handle merge operation
        if args.merge:
            if not args.report:
                print("Error: --report is required when using --merge", file=sys.stderr)
                sys.exit(1)
            
            if not args.original:
                print("Error: --original is required when using --merge", file=sys.stderr)
                sys.exit(1)
            
            # Determine output path
            if args.merged_output:
                output_path = args.merged_output
            else:
                output_path = args.original  # Overwrite original by default
            
            # Find extracted file from report
            with open(args.report, 'r', encoding='utf-8') as f:
                report = json.load(f)
            extracted_path = Path(report['extracted_file'])
            
            if not extracted_path.exists():
                print(f"Error: Extracted file not found: {extracted_path}", file=sys.stderr)
                sys.exit(1)
            
            print(f"Merging story graphs...")
            print(f"  Extracted: {extracted_path}")
            print(f"  Original: {args.original}")
            print(f"  Report: {args.report}")
            print(f"  Output: {output_path}")
            
            merged = merge_story_graphs(extracted_path, args.original, args.report, output_path)
            
            print(f"\nSuccessfully merged story graphs!")
            print(f"  Epics: {len(merged.get('epics', []))}")
            if 'increments' in merged:
                print(f"  Increments: {len(merged.get('increments', []))}")
            print(f"  Merged output written to: {output_path}")
            sys.exit(0)
        
        # Handle extraction operation
        if not args.drawio_path:
            parser.print_help()
            sys.exit(1)
        
        # If no output specified, create temp file
        if not args.output:
            temp_dir = Path(tempfile.gettempdir())
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            args.output = temp_dir / f"story-graph-extracted-{timestamp}.json"
            print(f"Using temporary file: {args.output}")
        
        # Choose function based on mode or file name
        if args.outline or 'outline' in str(args.drawio_path).lower():
            result = synchronize_story_graph_from_drawio_outline(args.drawio_path, args.output, args.original)
            print(f"\nSuccessfully synchronized story map outline from DrawIO")
        else:
            result = synchronize_story_graph_from_drawio_increments(args.drawio_path, args.output, args.original)
            print(f"\nSuccessfully synchronized story map from DrawIO")
        
        print(f"Epics: {len(result['epics'])}")
        if 'increments' in result:
            print(f"Increments: {len(result['increments'])}")
        print(f"Output written to: {args.output}")
        
        if args.original:
            report_path = args.output.parent / f"{args.output.stem}-merge-report.json"
            print("\nMerge report generated. Review the report above before proceeding with merge.")
            print(f"\nTo merge, run:")
            print(f"  python {Path(__file__).name} --merge --report {report_path} --original {args.original} --merged-output {args.original}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

