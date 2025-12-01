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
    Handles "When ... Then ..." format, HTML formatting, and plain text.
    
    Args:
        ac_text: Text from acceptance criteria box (may contain HTML)
    
    Returns:
        Step text (description) - cleaned and formatted
    """
    if not ac_text:
        return ""
    
    # Remove HTML tags and clean up entities
    # First replace <br> with space, then remove all other HTML tags
    text = ac_text.replace('<br>', ' ').replace('<br/>', ' ').replace('<br />', ' ')
    text = text.replace('&amp;', '&').replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    text = re.sub(r'<[^>]+>', '', text)  # Remove remaining HTML tags
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    
    # Try to extract "When ... Then ..." format
    # Pattern: "When [condition] Then [outcome]" (handles both HTML and plain text)
    # The renderer creates: "<b>When</b> {when_text}<br><b>Then</b> {then_text}"
    # After HTML removal: "When {when_text} Then {then_text}"
    when_match = re.search(r'When\s+([^Tt]+?)(?:\s+Then|$)', text, re.IGNORECASE | re.DOTALL)
    then_match = re.search(r'Then\s+(.+)', text, re.IGNORECASE | re.DOTALL)
    
    if when_match and then_match:
        when_part = when_match.group(1).strip()
        then_part = then_match.group(1).strip()
        # Return as single description
        return f"{when_part} {then_part}".strip()
    elif when_match:
        return when_match.group(1).strip()
    elif then_match:
        return then_match.group(1).strip()
    else:
        # Return cleaned text as-is (remove any dictionary-like strings)
        text = text.strip()
        # Remove any malformed dictionary strings
        if text.startswith("{'") or text.startswith('{"'):
            # Try to extract just the description if it's a malformed dict string
            desc_match = re.search(r"'description':\s*'([^']+)'", text)
            if desc_match:
                return desc_match.group(1).strip()
        # If text contains "User --> Description" format, extract description
        if '-->' in text:
            parts = text.split('-->', 1)
            if len(parts) == 2:
                return parts[1].strip()
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
    Get all epics and sub_epics (features) with their boundaries (x, y, width, height).
    
    Returns:
        Dictionary with 'epics' and 'features' lists (features will become sub_epics)
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
    
    # Assign epic_num to features by position/containment
    # Epics may be in a group with different coordinate space, so we need to be more flexible
    for feature in features:
        if feature['epic_num'] is None:
            feature_x = feature['x']
            feature_y = feature['y']
            
            # Try multiple strategies to assign feature to epic:
            # 1. Check if feature is within epic's horizontal bounds (X coordinate)
            # 2. Check if feature is within epic's vertical bounds (Y coordinate) 
            # 3. Use closest epic by distance
            best_epic = None
            best_score = float('inf')
            
            for epic in sorted(epics, key=lambda e: e['x']):
                epic_x = epic['x']
                epic_y = epic['y']
                epic_width = epic.get('width', 0)
                epic_height = epic.get('height', 60)  # Default height
                epic_right = epic_x + epic_width if epic_width > 0 else float('inf')
                epic_bottom = epic_y + epic_height
                
                # Check horizontal containment (primary)
                x_contained = epic_x <= feature_x <= epic_right
                # Check vertical proximity (features are usually below epics)
                y_proximity = feature_y > epic_y and feature_y < epic_bottom + 1000  # Features can be well below epics
                
                # Calculate distance score (lower is better)
                distance = ((epic_x - feature_x) ** 2 + (epic_y - feature_y) ** 2) ** 0.5
                
                # Prefer epics that contain the feature horizontally
                if x_contained:
                    score = distance * 0.1  # Much lower score for contained features
                elif y_proximity:
                    score = distance * 0.5  # Medium score for vertical proximity
                else:
                    score = distance  # Full distance for others
                
                if score < best_score:
                    best_score = score
                    best_epic = epic
            
            if best_epic:
                feature['epic_num'] = best_epic['epic_num']
            # Fallback: assign to closest epic by X position
            elif epics:
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
    background_rectangles = []  # Story groups (grey background rectangles)
    
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
        
        # Background rectangles (story groups): light grey with dashed border
        # These are the horizontal groups of stories
        elif ('fillColor=#F7F7F7' in style or 'fillColor=#f7f7f7' in style) and 'dashed=1' in style:
            background_rectangles.append({
                'id': cell_id,
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
    
    # Sort acceptance criteria cells by Y position (top to bottom) for proper matching
    acceptance_criteria_cells.sort(key=lambda ac: (ac['y'], ac['x']))
    
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
    
    # Deduplicate users (but don't inherit - stories only get users explicitly assigned in DrawIO)
    for story in all_stories:
        if story['id'] in stories_with_users:
            current_users = stories_with_users[story['id']]
            deduplicated = []
            for user in current_users:
                if user not in deduplicated:
                    deduplicated.append(user)
            stories_with_users[story['id']] = deduplicated
    
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
    # Track which acceptance criteria boxes have been assigned to prevent duplicates
    assigned_ac_ids = set()
    
    for epic in sorted_epics:
        epic_data = {
            'name': epic['name'],
            'sequential_order': epic['sequential_order'],
            'estimated_stories': epic.get('estimated_stories'),  # Include even if null
            'sub_epics': [],
            'stories': []
        }
        
        # Get features for this epic, sorted by X position (these become sub_epics)
        epic_features = sorted([f for f in features if f['epic_num'] == epic['epic_num']], 
                               key=lambda x: (x['x'], x.get('feat_num', 0)))
        
        for feature in epic_features:
            sub_epic_data = {
                'name': feature['name'],
                'sequential_order': feature['sequential_order'],
                'estimated_stories': feature.get('estimated_stories'),  # Include even if null
                'sub_epics': [],
                'story_groups': []  # Changed from 'stories' to 'story_groups'
            }
            
            # Get stories for this sub_epic based on feat_num (assigned by position earlier)
            epic_stories = [s for s in all_stories if s['epic_num'] == epic['epic_num']]
            feat_stories = [s for s in epic_stories 
                          if s['epic_num'] == epic['epic_num'] and s.get('feat_num') == feature.get('feat_num')]
            
            # Get stories for this sub_epic, sorted by sequential_order
            feat_stories.sort(key=lambda s: (
                s.get('sequential_order', 999) if isinstance(s.get('sequential_order'), (int, float)) else 999,
                s['x']
            ))
            
            # Group stories by background rectangles (story groups)
            # Match stories to background rectangles based on containment
            story_groups = {}  # Maps group_id -> list of stories
            group_rectangles = {}  # Maps group_id -> rectangle info
            
            # Filter background rectangles that belong to this feature (horizontally aligned)
            feature_left = feature['x']
            feature_right = feature['x'] + feature.get('width', 0)
            feature_bottom = feature['y'] + feature.get('height', 0)
            
            for bg_rect in background_rectangles:
                bg_x = bg_rect['x']
                bg_y = bg_rect['y']
                bg_width = bg_rect['width']
                bg_height = bg_rect['height']
                bg_right = bg_x + bg_width
                bg_bottom = bg_y + bg_height
                
                # Check if rectangle is below feature and horizontally overlaps
                if (bg_y >= feature_bottom - 50 and  # Below or slightly overlapping feature
                    bg_x < feature_right and bg_right > feature_left):  # Horizontally overlaps
                    
                    group_id = bg_rect['id']
                    story_groups[group_id] = []
                    group_rectangles[group_id] = {
                        'x': bg_x,
                        'y': bg_y,
                        'width': bg_width,
                        'height': bg_height
                    }
            
            # Assign ALL stories to groups based on containment
            # No nested stories - all stories are flat within story groups
            ungrouped_stories = []
            
            for story in feat_stories:
                story_x = story['x']
                story_y = story['y']
                story_center_x = story_x + story.get('width', 50) / 2
                story_center_y = story_y + story.get('height', 50) / 2
                
                assigned = False
                for group_id, rect_info in group_rectangles.items():
                    rect_x = rect_info['x']
                    rect_y = rect_info['y']
                    rect_right = rect_x + rect_info['width']
                    rect_bottom = rect_y + rect_info['height']
                    
                    # Check if story center is within rectangle bounds
                    if (rect_x <= story_center_x <= rect_right and
                        rect_y <= story_center_y <= rect_bottom):
                        story_groups[group_id].append(story)
                        assigned = True
                        break
                
                if not assigned:
                    ungrouped_stories.append(story)
            
            # Sort groups by Y position (top to bottom), then X position (left to right)
            sorted_group_ids = sorted(group_rectangles.keys(), 
                                     key=lambda gid: (group_rectangles[gid]['y'], group_rectangles[gid]['x']))
            
            # Determine group types and connectors based on relative positioning
            # Group TYPE: Groups at same Y level (horizontal) = "and" type, groups at different Y levels (vertical) = "or" type
            # Group CONNECTOR: How this group connects to the previous group
            y_tolerance = 20  # Tolerance for grouping groups into rows
            base_story_y = 337
            opt_story_y = 402
            or_story_y_start = 404.75
            
            group_types = {}  # Group's own type (and/or based on positioning)
            group_connectors = {}  # How group connects to previous group
            previous_group_y = None
            
            for group_id in sorted_group_ids:
                group_y = group_rectangles[group_id]['y']
                
                if previous_group_y is None:
                    # First group - determine type based on absolute Y position
                    if abs(group_y - base_story_y) <= 10:
                        group_types[group_id] = 'and'  # Horizontal group
                    elif abs(group_y - opt_story_y) <= 10:
                        group_types[group_id] = 'opt'  # Optional group
                    else:
                        group_types[group_id] = 'or'  # Vertical group
                    # First group has no connector (it's the first)
                    group_connectors[group_id] = None
                else:
                    # Determine type based on Y position relative to base row
                    if abs(group_y - base_story_y) <= 10:
                        group_types[group_id] = 'and'  # Horizontal group
                    elif abs(group_y - opt_story_y) <= 10:
                        group_types[group_id] = 'opt'  # Optional group
                    elif abs(group_y - previous_group_y) <= y_tolerance:
                        group_types[group_id] = 'and'  # Same Y as previous = horizontal
                    else:
                        group_types[group_id] = 'or'  # Different Y = vertical
                    
                    # Determine connector: how this group connects to previous group
                    if abs(group_y - previous_group_y) <= y_tolerance:
                        # Same Y level (horizontal) - "and" connector
                        group_connectors[group_id] = 'and'
                    else:
                        # Different Y level (vertical) - "or" connector
                        group_connectors[group_id] = 'or'
                
                previous_group_y = group_y
            
            # Process ungrouped stories - create a default group for them
            if ungrouped_stories:
                # Sort ungrouped stories by Y, then X
                ungrouped_stories.sort(key=lambda s: (s['y'], s['x']))
                # Create a default group for ungrouped top-level stories
                default_group_id = 'ungrouped'
                story_groups[default_group_id] = ungrouped_stories
                # Determine type and connector for default group based on first story's Y
                if ungrouped_stories:
                    first_ungrouped_y = ungrouped_stories[0]['y']
                    if abs(first_ungrouped_y - base_story_y) <= y_tolerance:
                        group_types[default_group_id] = 'and'
                    elif abs(first_ungrouped_y - opt_story_y) <= y_tolerance:
                        group_types[default_group_id] = 'opt'
                    else:
                        group_types[default_group_id] = 'or'
                    # Default group has no connector (it's ungrouped, so no previous group)
                    group_connectors[default_group_id] = None
                sorted_group_ids.append(default_group_id)
            
            # Determine connectors for stories based on Y position and X position
            # According to story-map-construction-rules.mdc:
            # - Sequential stories (connector="and"): Y-position = Base story row (y=337)
            # - Optional stories (connector="opt"): Y-position = y=402 (65px below base row)
            # - Alternative stories (connector="or"): Y-position = Below sequential stories (y=404.75+)
            # So: Stories at y=337 (base row) should be "and" (sequential)
            #     Stories at y=402 should be "opt" (optional)
            #     Stories at y=404.75+ should be "or" (alternatives)
            base_story_y = 337
            opt_story_y = 402  # Optional stories start at y=402
            or_story_y_start = 404.75  # Alternative stories start at y=404.75+
            y_tolerance = 10  # pixels tolerance for base row
            x_tolerance = 10  # pixels tolerance for same X position
            story_connectors = {}
            previous_x = None
            previous_y = None
            
            for story in feat_stories:
                story_x = story['x']
                story_y = story['y']
                
                if previous_x is None:
                    # First story - check Y position
                    if abs(story_y - base_story_y) <= y_tolerance:
                        # At base row - sequential "and"
                        story_connectors[story['id']] = 'and'
                    elif abs(story_y - opt_story_y) <= y_tolerance:
                        # At optional row (y=402) - optional "opt"
                        story_connectors[story['id']] = 'opt'
                    else:
                        # Below base row (y=404.75+) - alternative "or"
                        story_connectors[story['id']] = 'or'
                elif abs(story_y - base_story_y) <= y_tolerance:
                    # At base row (y=337) - sequential "and" connector
                    story_connectors[story['id']] = 'and'
                elif abs(story_y - opt_story_y) <= y_tolerance:
                    # At optional row (y=402) - optional "opt" connector
                    story_connectors[story['id']] = 'opt'
                elif abs(story_y - previous_y) <= y_tolerance:
                    # Same Y as previous (both below base row) - check X
                    if abs(story_x - previous_x) < x_tolerance:
                        # Same X position - inherit previous connector type
                        story_connectors[story['id']] = story_connectors.get(feat_stories[feat_stories.index(story) - 1]['id'], 'or')
                    else:
                        # Different X position - "or" (alternative path)
                        story_connectors[story['id']] = 'or'
                else:
                    # Different Y position from previous - check if opt or or
                    if story_y >= or_story_y_start:
                        story_connectors[story['id']] = 'or'
                    elif abs(story_y - opt_story_y) <= y_tolerance:
                        story_connectors[story['id']] = 'opt'
                    else:
                        story_connectors[story['id']] = 'or'
                
                previous_x = story_x
                previous_y = story_y
            
            # Group stories by Y position (rows) within this sub-epic
            # Traversal logic: Go left to right, capture sequence of "and" stories (first row)
            # If there's a next row, add stories to nested children of first story in first row
            y_tolerance_row = 20  # Tolerance for grouping stories into rows (increased to handle slight Y variations)
            stories_by_row = {}
            for story in feat_stories:
                story_y = story['y']
                # Find which row this story belongs to (group by similar Y)
                row_key = None
                for existing_y in stories_by_row.keys():
                    if abs(story_y - existing_y) <= y_tolerance_row:
                        row_key = existing_y
                        break
                if row_key is None:
                    row_key = story_y
                if row_key not in stories_by_row:
                    stories_by_row[row_key] = []
                stories_by_row[row_key].append(story)
            
            # Sort rows by Y position (top to bottom)
            sorted_rows = sorted(stories_by_row.items())
            first_row_y = sorted_rows[0][0] if sorted_rows else None
            
            # Process stories row by row
            # No nested stories - all stories are flat within story groups
            # Initialize temp_stories before processing stories
            if 'temp_stories' not in sub_epic_data:
                sub_epic_data['temp_stories'] = {}  # Maps group_id -> list of story_data
            
            for story_idx, story in enumerate(feat_stories):
                # Skip if this story has already been assigned to another sub_epic (prevent duplicates)
                if story['id'] in assigned_story_ids:
                    continue
                
                story_x = story['x']
                story_y = story['y']
                
                story_data = {
                    'name': story['name'],
                    'sequential_order': story.get('sequential_order', 1),
                    'connector': story_connectors.get(story['id'], 'and'),  # Extract from position
                    'users': stories_with_users.get(story['id'], []),
                    'story_type': story.get('story_type', 'user'),
                    'x': story_x,  # Store x position for sorting
                    'y': story_y   # Store y position for sorting
                }
                
                # Match acceptance criteria to this story (wider boxes below story)
                story_ac = []
                
                # Find acceptance criteria boxes below this story
                # Acceptance criteria should be:
                # - Below the story (y > story_y + story_height)
                # - Horizontally aligned (within tolerance of story_x)
                # - Not already assigned to another story
                tolerance_x = 100  # Increased tolerance for AC boxes (they can be wider than stories)
                story_height = 50  # Approximate story height
                
                # Find all AC boxes that belong to this story
                # AC boxes are positioned below the story, sorted by Y position
                for ac in acceptance_criteria_cells:
                    if ac['id'] in assigned_ac_ids:
                        continue  # Skip already assigned AC boxes
                    
                    ac_x = ac['x']
                    ac_y = ac['y']
                    ac_right = ac_x + ac['width']
                    story_right = story_x + story.get('width', 100)  # Approximate story width
                    
                    # Check if acceptance criteria is below story and aligned
                    # AC boxes can be wider than stories, so check if they overlap horizontally
                    # Also check if AC is not too far below (within reasonable distance)
                    is_below = ac_y > story_y + story_height
                    max_distance_below = story_y + story_height + 500  # Max 500px below story
                    is_within_range = ac_y < max_distance_below
                    is_aligned = (abs(ac_x - story_x) < tolerance_x or 
                                 (ac_x <= story_x <= ac_right) or 
                                 (story_x <= ac_x <= story_right))
                    
                    # Also check if there's a closer story that this AC might belong to
                    # (We'll match to the closest story if multiple stories are candidates)
                    if is_below and is_within_range and is_aligned:
                        # Extract step from acceptance criteria text
                        step_text = extract_step_from_acceptance_criteria(ac['text'])
                        if step_text:
                            # Extract user from AC if present (format: "User --> Description")
                            ac_user = ""
                            if '-->' in step_text:
                                parts = step_text.split('-->', 1)
                                ac_user = parts[0].strip()
                                step_text = parts[1].strip()
                            
                            story_ac.append({
                                'description': step_text,
                                'sequential_order': len(story_ac) + 1,
                                'connector': None,  # Default to 'and' (not shown)
                                'user': ac_user
                            })
                            assigned_ac_ids.add(ac['id'])  # Mark this AC as assigned
                
                # Add acceptance_criteria only if found
                if story_ac:
                    story_data['acceptance_criteria'] = story_ac
                
                # No nested stories - stories are flat within story groups
                
                # Find which group this story belongs to
                story_group_id = None
                for group_id, group_stories in story_groups.items():
                    if story in group_stories:
                        story_group_id = group_id
                        break
                
                # If story not in any group, add to ungrouped
                if story_group_id is None:
                    if 'ungrouped' not in story_groups:
                        story_groups['ungrouped'] = []
                        group_types['ungrouped'] = 'and'  # Default type
                        group_connectors['ungrouped'] = None  # No connector (ungrouped)
                        if 'ungrouped' not in sorted_group_ids:
                            sorted_group_ids.append('ungrouped')
                    story_group_id = 'ungrouped'
                    story_groups['ungrouped'].append(story)
                
                # Store story_data temporarily - we'll organize into groups after processing all stories
                # temp_stories already initialized before the loop
                if story_group_id not in sub_epic_data['temp_stories']:
                    sub_epic_data['temp_stories'][story_group_id] = []
                sub_epic_data['temp_stories'][story_group_id].append(story_data)
                assigned_story_ids.add(story['id'])  # Mark this story as assigned
            
            # Now organize stories into story groups and determine group type based on story layout
            for group_idx, group_id in enumerate(sorted_group_ids, 1):
                group_stories = sub_epic_data['temp_stories'].get(group_id, [])
                if group_stories:
                    # Determine group TYPE based on how stories are laid out within the group
                    # Need to check the actual story positions from the original story data
                    group_story_y_positions = []
                    group_story_x_positions = []
                    for story_data in group_stories:
                        # Find the original story to get its position
                        story_name = story_data['name']
                        for story in feat_stories:
                            if story['name'] == story_name:
                                group_story_y_positions.append(story['y'])
                                group_story_x_positions.append(story['x'])
                                break
                    
                    # Determine group type: if stories are at same Y level (within tolerance), it's "and" (horizontal)
                    # If stories are at different Y levels, it's "or" (vertical)
                    story_y_tolerance = 20  # Tolerance for considering stories at same Y level
                    if len(group_story_y_positions) > 1:
                        min_y = min(group_story_y_positions)
                        max_y = max(group_story_y_positions)
                        if abs(max_y - min_y) <= story_y_tolerance:
                            # Stories are at same Y level - horizontal layout (left to right) = "and" type
                            group_type = 'and'
                        else:
                            # Stories are at different Y levels - vertical layout (top to bottom) = "or" type
                            group_type = 'or'
                    else:
                        # Single story - default to "and" type
                        group_type = 'and'
                    
                    # Sort stories within group based on group type
                    # For "and" type (horizontal): sort by X position (left to right)
                    # For "or" type (vertical): sort by Y position (top to bottom), then X (left to right)
                    group_stories_with_positions = []
                    for story_data in group_stories:
                        story_name = story_data['name']
                        story_y = None
                        story_x = None
                        # Find the original story to get its position - use the story's own x/y if available
                        # Otherwise look it up in feat_stories
                        if 'x' in story_data and 'y' in story_data:
                            story_x = story_data['x']
                            story_y = story_data['y']
                        else:
                            for story in feat_stories:
                                if story['name'] == story_name:
                                    story_y = story['y']
                                    story_x = story['x']
                                    break
                        group_stories_with_positions.append((story_y or 0, story_x or 0, story_data))
                    
                    # Sort based on group type
                    if group_type == 'and':
                        # Horizontal layout: sort by X position (left to right) only
                        group_stories_with_positions.sort(key=lambda s: float(s[1]))  # Sort by X (ensure numeric)
                    else:
                        # Vertical layout: sort by Y first (top to bottom), then X (left to right)
                        group_stories_with_positions.sort(key=lambda s: (float(s[0]), float(s[1])))  # Sort by Y, then X (ensure numeric)
                    group_stories = [story_data for _, _, story_data in group_stories_with_positions]
                    
                    # Renumber stories within group to 1, 2, 3...
                    for story_idx, story_data in enumerate(group_stories, 1):
                        story_data['sequential_order'] = story_idx
                        # Remove x and y coordinates - they're only used for sorting, layout info is stored separately
                        story_data.pop('x', None)
                        story_data.pop('y', None)
                    
                    story_group_data = {
                        'type': group_type,  # Group's own type: "and" = horizontal (left to right), "or" = vertical (top to bottom)
                        'connector': group_connectors.get(group_id, 'and'),  # How it connects to previous group
                        'stories': group_stories
                    }
                    sub_epic_data['story_groups'].append(story_group_data)
            
            # Clean up temp data
            if 'temp_stories' in sub_epic_data:
                del sub_epic_data['temp_stories']
            
            epic_data['sub_epics'].append(sub_epic_data)
        
        # Handle stories directly under epic (not in any sub_epic)
        epic_stories = [s for s in all_stories if s['epic_num'] == epic['epic_num'] and s.get('feat_num') is None]
        epic_stories.sort(key=lambda s: (
            s.get('sequential_order', 999) if isinstance(s.get('sequential_order'), (int, float)) else 999,
            s['x']
        ))
        
        for story in epic_stories:
            if story['id'] in assigned_story_ids:
                continue
            
            story_data = {
                'name': story['name'],
                'sequential_order': story.get('sequential_order', 1),
                'connector': 'and',  # Default to 'and' (can be determined from position if needed)
                'users': stories_with_users.get(story['id'], []),
                'story_type': story.get('story_type', 'user')
            }
            
            # Match acceptance criteria to this story (same logic as sub_epic stories)
            story_x = story['x']
            story_y = story['y']
            story_ac = []
            tolerance_x = 100  # Increased tolerance for AC boxes
            story_height = 50
            
            for ac in acceptance_criteria_cells:
                if ac['id'] in assigned_ac_ids:
                    continue
                
                ac_x = ac['x']
                ac_y = ac['y']
                ac_right = ac_x + ac['width']
                story_right = story_x + story.get('width', 100)
                
                is_below = ac_y > story_y + story_height
                max_distance_below = story_y + story_height + 500  # Max 500px below story
                is_within_range = ac_y < max_distance_below
                is_aligned = (abs(ac_x - story_x) < tolerance_x or 
                             (ac_x <= story_x <= ac_right) or 
                             (story_x <= ac_x <= story_right))
                
                if is_below and is_within_range and is_aligned:
                    step_text = extract_step_from_acceptance_criteria(ac['text'])
                    if step_text:
                        ac_user = ""
                        if '-->' in step_text:
                            parts = step_text.split('-->', 1)
                            ac_user = parts[0].strip()
                            step_text = parts[1].strip()
                        
                        story_ac.append({
                            'description': step_text,
                            'sequential_order': len(story_ac) + 1,
                            'connector': None,
                            'user': ac_user
                        })
                        assigned_ac_ids.add(ac['id'])
            
            if story_ac:
                story_data['acceptance_criteria'] = story_ac
            
            epic_data['stories'].append(story_data)
            assigned_story_ids.add(story['id'])
        
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
                    'sequential_order': epic_order,
                    'sub_epics': {}
                }
            
            if feat_num not in inc_epics[epic_num]['sub_epics']:
                feature = next((f for f in features 
                                if f['epic_num'] == epic_num and f.get('feat_num') == feat_num), None)
                feat_name = feature['name'] if feature else f'Sub-Epic {feat_num}'
                feat_order = feature.get('sequential_order', feat_num) if feature else feat_num
                inc_epics[epic_num]['sub_epics'][feat_num] = {
                    'name': feat_name,
                    'sequential_order': feat_order,
                    'sub_epics': [],
                    'stories': []
                }
            
            story_data = {
                'name': story['name'],
                'sequential_order': story.get('sequential_order', 1),
                'users': stories_with_users.get(story['id'], []),
                'story_type': story.get('story_type', 'user'),
                'acceptance_criteria': [],
                'stories': []
            }
            inc_epics[epic_num]['sub_epics'][feat_num]['stories'].append(story_data)
        
        # Convert to list format and sort by sequential_order
        sorted_inc_epics = sorted(
            inc_epics.items(),
            key=lambda x: (x[1].get('sequential_order', 999), x[0])
        )
        for epic_num, epic_data in sorted_inc_epics:
            # Sort sub_epics by sequential_order
            sorted_sub_epics = sorted(
                epic_data['sub_epics'].items(),
                key=lambda x: (x[1].get('sequential_order', 999) if isinstance(x[1].get('sequential_order'), (int, float)) else 999,
                              x[0] if x[0] is not None else 999)
            )
            # Sort stories by sequential_order within each sub_epic
            for feat_num, sub_epic_data in sorted_sub_epics:
                sub_epic_data['stories'].sort(key=lambda s: (
                    s.get('sequential_order', 999) if isinstance(s.get('sequential_order'), (int, float)) else 999,
                    s.get('sequential_order', '') if isinstance(s.get('sequential_order'), str) else ''
                ))
            epic_data['sub_epics'] = [sub_epic_data for feat_num, sub_epic_data in sorted_sub_epics]
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
        'missing_sub_epics': [],
        'epics_with_many_missing_stories': [],
        'sub_epics_with_many_missing_stories': []
    }
    
    # Build maps for comparison (support both old format 'features' and new format 'sub_epics')
    original_epics = {epic['name']: epic for epic in original_data.get('epics', [])}
    extracted_epics = {epic['name']: epic for epic in extracted_data.get('epics', [])}
    
    # Helper to get sub_epics (supports both formats)
    def get_sub_epics(epic):
        return epic.get('sub_epics', []) or epic.get('features', [])
    
    # Find missing epics
    for epic_name, epic in original_epics.items():
        if epic_name not in extracted_epics:
            original_story_count = sum(
                len(se.get('stories', [])) 
                for se in get_sub_epics(epic)
            )
            deletions['missing_epics'].append({
                'name': epic_name,
                'story_count': original_story_count,
                'sub_epic_count': len(get_sub_epics(epic))
            })
    
    # Find missing sub_epics and epics with many missing stories
    for epic_name, original_epic in original_epics.items():
        if epic_name in extracted_epics:
            extracted_epic = extracted_epics[epic_name]
            
            original_sub_epics = {se['name']: se for se in get_sub_epics(original_epic)}
            extracted_sub_epics = {se['name']: se for se in get_sub_epics(extracted_epic)}
            
            # Find missing sub_epics
            for sub_epic_name, sub_epic in original_sub_epics.items():
                if sub_epic_name not in extracted_sub_epics:
                    deletions['missing_sub_epics'].append({
                        'epic': epic_name,
                        'name': sub_epic_name,
                        'story_count': len(sub_epic.get('stories', []))
                    })
            
            # Check for epics with many missing stories
            original_story_count = sum(
                len(se.get('stories', [])) 
                for se in get_sub_epics(original_epic)
            )
            extracted_story_count = sum(
                len(se.get('stories', [])) 
                for se in get_sub_epics(extracted_epic)
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
            
            # Check for sub_epics with many missing stories
            for sub_epic_name, original_sub_epic in original_sub_epics.items():
                if sub_epic_name in extracted_sub_epics:
                    extracted_sub_epic = extracted_sub_epics[sub_epic_name]
                    orig_stories = len(original_sub_epic.get('stories', []))
                    extr_stories = len(extracted_sub_epic.get('stories', []))
                    
                    if orig_stories > 0:
                        missing_ratio = (orig_stories - extr_stories) / orig_stories
                        if missing_ratio > 0.5:  # More than 50% missing
                            deletions['sub_epics_with_many_missing_stories'].append({
                                'epic': epic_name,
                                'name': sub_epic_name,
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
    
    # Helper to get sub_epics (supports both formats)
    def get_sub_epics(epic):
        return epic.get('sub_epics', []) or epic.get('features', [])
    
    for epic in original_data.get('epics', []):
        epic_name = epic.get('name', '')
        for sub_epic in get_sub_epics(epic):
            sub_epic_name = sub_epic.get('name', '')
            for story in sub_epic.get('stories', []):
                story_data = {
                    'name': story.get('name', ''),
                    'users': story.get('users', []),
                    'Steps': story.get('Steps', []),
                    'acceptance_criteria': story.get('acceptance_criteria', []),
                    'epic_name': epic_name,
                    'sub_epic_name': sub_epic_name
                }
                stories.append(story_data)
    
    return stories


def _flatten_stories_from_extracted(extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten all stories from extracted story graph into a list with context."""
    stories = []
    
    # Helper to get sub_epics (supports both formats)
    def get_sub_epics(epic):
        return epic.get('sub_epics', []) or epic.get('features', [])
    
    for epic in extracted_data.get('epics', []):
        epic_name = epic.get('name', '')
        for sub_epic in get_sub_epics(epic):
            sub_epic_name = sub_epic.get('name', '')
            for story in sub_epic.get('stories', []):
                story_data = {
                    'name': story.get('name', ''),
                    'users': story.get('users', []),
                    'sequential_order': story.get('sequential_order'),
                    'epic_name': epic_name,
                    'sub_epic_name': sub_epic_name
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
        
        # Bonus for same epic/sub_epic context
        context_bonus = 0.0
        if extracted_story.get('epic_name') == orig_story.get('epic_name'):
            context_bonus += 0.1
        # Support both old and new format
        ext_sub_epic = extracted_story.get('sub_epic_name') or extracted_story.get('feature_name', '')
        orig_sub_epic = orig_story.get('sub_epic_name') or orig_story.get('feature_name', '')
        if ext_sub_epic == orig_sub_epic:
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
    
    # Helper to get sub_epics (supports both formats)
    def get_sub_epics(epic):
        return epic.get('sub_epics', []) or epic.get('features', [])
    
    # Create a lookup map for original stories by epic/sub_epic/name
    original_story_map = {}
    for epic in original_data.get('epics', []):
        epic_name = epic.get('name', '')
        for sub_epic in get_sub_epics(epic):
            sub_epic_name = sub_epic.get('name', '')
            for story in sub_epic.get('stories', []):
                story_name = story.get('name', '')
                key = f"{epic_name}|{sub_epic_name}|{story_name}"
                original_story_map[key] = story
    
    # Create a map of matches from report (support both old and new format keys)
    match_map = {}
    for match in report.get('exact_matches', []):
        ext_story = match['extracted']
        orig_story = match['original']
        # Support both 'feature_name' (old) and 'sub_epic_name' (new)
        feature_name = ext_story.get('feature_name') or ext_story.get('sub_epic_name', '')
        key = f"{ext_story['epic_name']}|{feature_name}|{ext_story['name']}"
        match_map[key] = orig_story
    
    for match in report.get('fuzzy_matches', []):
        ext_story = match['extracted']
        orig_story = match['original']
        # Support both 'feature_name' (old) and 'sub_epic_name' (new)
        feature_name = ext_story.get('feature_name') or ext_story.get('sub_epic_name', '')
        key = f"{ext_story['epic_name']}|{feature_name}|{ext_story['name']}"
        match_map[key] = orig_story
    
    # Merge: start with extracted structure, add acceptance_criteria/Steps from matches
    merged_data = json.loads(json.dumps(extracted_data))  # Deep copy
    
    # Merge epics
    for epic in merged_data.get('epics', []):
        epic_name = epic.get('name', '')
        for sub_epic in get_sub_epics(epic):
            sub_epic_name = sub_epic.get('name', '')
            for story in sub_epic.get('stories', []):
                story_name = story.get('name', '')
                key = f"{epic_name}|{sub_epic_name}|{story_name}"
                
                # If we have a match, copy acceptance_criteria/Steps and use extracted users (DrawIO is source of truth)
                if key in match_map:
                    orig_story = match_map[key]
                    # Copy acceptance_criteria (new format)
                    if 'acceptance_criteria' in orig_story:
                        story['acceptance_criteria'] = orig_story['acceptance_criteria']
                    # Copy Steps (legacy format)
                    if 'Steps' in orig_story:
                        story['Steps'] = orig_story['Steps']
                    # Use extracted users only (DrawIO is source of truth for user associations)
                    # Extracted users are already set in story, so no need to merge
                    pass
    
    # Merge increments (if present)
    for increment in merged_data.get('increments', []):
        for epic in increment.get('epics', []):
            epic_name = epic.get('name', '')
            for sub_epic in get_sub_epics(epic):
                sub_epic_name = sub_epic.get('name', '')
                for story in sub_epic.get('stories', []):
                    story_name = story.get('name', '')
                    key = f"{epic_name}|{sub_epic_name}|{story_name}"
                    
                    # If we have a match, copy acceptance_criteria/Steps and use extracted users (DrawIO is source of truth)
                    if key in match_map:
                        orig_story = match_map[key]
                        # Copy acceptance_criteria (new format)
                        if 'acceptance_criteria' in orig_story:
                            story['acceptance_criteria'] = orig_story['acceptance_criteria']
                        # Copy Steps (legacy format)
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
            # Support both old and new format
            sub_epic_name = match['extracted'].get('sub_epic_name') or match['extracted'].get('feature_name', '')
            print(f"  Epic: {match['extracted']['epic_name']} | Sub-Epic: {sub_epic_name}")
            print(f"Original: {match['original']['name']}")
            orig_sub_epic_name = match['original'].get('sub_epic_name') or match['original'].get('feature_name', '')
            print(f"  Epic: {match['original']['epic_name']} | Sub-Epic: {orig_sub_epic_name}")
            print(f"Confidence: {match['confidence']:.2%}")
            print(f"Has Steps: {'Yes' if match['original'].get('Steps') else 'No'}")
            print(f"Has Acceptance Criteria: {'Yes' if match['original'].get('acceptance_criteria') else 'No'}")
    
    if report['new_stories']:
        print("\n" + "-"*80)
        print("NEW STORIES (No match in original)")
        print("-"*80)
        for story in report['new_stories'][:10]:  # Show first 10
            # Support both old and new format
            sub_epic_name = story.get('sub_epic_name') or story.get('feature_name', '')
            print(f"  - {story['name']} ({story['epic_name']} > {sub_epic_name})")
        if len(report['new_stories']) > 10:
            print(f"  ... and {len(report['new_stories']) - 10} more")
    
    if report['removed_stories']:
        print("\n" + "-"*80)
        print("REMOVED STORIES (In original but not in extracted)")
        print("-"*80)
        for story in report['removed_stories'][:10]:  # Show first 10
            # Support both old and new format
            sub_epic_name = story.get('sub_epic_name') or story.get('feature_name', '')
            print(f"  - {story['name']} ({story['epic_name']} > {sub_epic_name})")
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

