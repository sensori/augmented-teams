"""
Assert layout positions are preserved after sync-then-render workflow.

THEN: Assert that component positions match between original and rendered DrawIO

UNIQUE TO THIS ASSERTION:
- Asserts sync-then-render workflow preserves layout positions
- Compares positions extracted from original vs rendered DrawIO
- Uses tolerance for position differences
- Reports preservation rate and identifies issues
"""
import sys
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import re
from typing import Dict, Any

# Add parent directories to path
then_dir = Path(__file__).parent
test_dir = then_dir.parent
acceptance_dir = test_dir.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(acceptance_dir.parent / "spec_by_example"))

# Import from given folder
given_dir = test_dir / "1_given"
sys.path.insert(0, str(given_dir))
import importlib.util
spec = importlib.util.spec_from_file_location("load_drawio_data", given_dir / "load_drawio_data.py")
given_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(given_data)

def _get_cell_value(cell) -> str:
    """Extract text value from a cell, handling HTML entities."""
    value = cell.get('value', '')
    value = value.replace('&amp;', '&').replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    value = re.sub(r'<[^>]+>', '', value)
    return value.strip()

def extract_positions_from_drawio(drawio_path: Path) -> Dict[str, Dict[str, float]]:
    """Extract component positions from DrawIO file using same key format as layout system."""
    positions = {}
    
    tree = ET.parse(drawio_path)
    root = tree.getroot()
    cells = root.findall('.//mxCell')
    
    # Extract epics, features, stories using same logic as synchronizer
    epics = []
    features = []
    stories = []
    users = []
    
    for cell in cells:
        cell_id = cell.get('id', '')
        style = cell.get('style', '')
        value = _get_cell_value(cell)
        geometry = cell.find('mxGeometry')
        
        if geometry is None:
            continue
        
        x = float(geometry.get('x', 0))
        y = float(geometry.get('y', 0))
        width = float(geometry.get('width', 0))
        height = float(geometry.get('height', 0))
        
        # Epics: purple boxes
        if 'fillColor=#e1d5e7' in style:
            match = re.match(r'epic(\d+)', cell_id)
            if match:
                epic_num = int(match.group(1))
                epics.append({
                    'num': epic_num,
                    'name': value,
                    'x': x, 'y': y, 'width': width, 'height': height
                })
        
        # Features: green boxes
        elif 'fillColor=#d5e8d4' in style:
            match = re.match(r'e(\d+)f(\d+)', cell_id)
            if match:
                epic_num = int(match.group(1))
                feat_num = int(match.group(2))
                features.append({
                    'epic_num': epic_num,
                    'feat_num': feat_num,
                    'name': value,
                    'x': x, 'y': y, 'width': width, 'height': height
                })
        
        # Stories: yellow/blue/black boxes
        elif ('fillColor=#fff2cc' in style or 'fillColor=#1a237e' in style or 
               'fillColor=#000000' in style or 'fillColor=#000' in style):
            match = re.match(r'e(\d+)f(\d+)s(\d+)', cell_id)
            if match:
                epic_num = int(match.group(1))
                feat_num = int(match.group(2))
                story_num = int(match.group(3))
                stories.append({
                    'epic_num': epic_num,
                    'feat_num': feat_num,
                    'story_num': story_num,
                    'name': value,
                    'x': x, 'y': y, 'width': width, 'height': height
                })
        
        # Users: light blue boxes
        elif 'fillColor=#dae8fc' in style:
            if value:
                users.append({
                    'name': value,
                    'x': x, 'y': y
                })
    
    # Build layout keys in same format as synchronizer
    epics.sort(key=lambda e: e['num'])
    
    # Build epic keys
    for epic in epics:
        key = f"EPIC|{epic['name']}"
        positions[key] = {
            'x': epic['x'],
            'y': epic['y'],
            'width': epic['width'],
            'height': epic['height']
        }
    
    # Build feature keys
    epic_names = {e['num']: e['name'] for e in epics}
    for feature in features:
        epic_name = epic_names.get(feature['epic_num'], f"Epic{feature['epic_num']}")
        key = f"FEATURE|{epic_name}|{feature['name']}"
        positions[key] = {
            'x': feature['x'],
            'y': feature['y'],
            'width': feature['width'],
            'height': feature['height']
        }
    
    # Build story keys
    feature_map = {}
    for feature in features:
        epic_name = epic_names.get(feature['epic_num'], f"Epic{feature['epic_num']}")
        feature_map[(feature['epic_num'], feature['feat_num'])] = feature['name']
    
    for story in stories:
        epic_name = epic_names.get(story['epic_num'], f"Epic{story['epic_num']}")
        feature_name = feature_map.get((story['epic_num'], story['feat_num']), f"Feature{story['feat_num']}")
        key = f"{epic_name}|{feature_name}|{story['name']}"
        positions[key] = {
            'x': story['x'],
            'y': story['y']
        }
    
    # Build user keys
    for user in users:
        key = f"USER|{user['name']}"
        positions[key] = {
            'x': user['x'],
            'y': user['y']
        }
    
    return positions

def compare_layouts(original: Dict[str, Dict[str, float]], 
                   rendered: Dict[str, Dict[str, float]],
                   tolerance: float = 5.0) -> Dict[str, Any]:
    """Compare two layout dictionaries using exact key matching."""
    results = {
        'total_original': len(original),
        'total_rendered': len(rendered),
        'exact_matches': [],
        'position_diffs': [],
        'missing_in_rendered': [],
        'new_in_rendered': [],
        'tolerance': tolerance
    }
    
    # Compare by exact key match
    all_keys = set(original.keys()) | set(rendered.keys())
    
    for key in all_keys:
        if key not in original:
            results['new_in_rendered'].append({
                'key': key,
                'position': rendered[key]
            })
            continue
        
        if key not in rendered:
            results['missing_in_rendered'].append({
                'key': key,
                'position': original[key]
            })
            continue
        
        # Both exist - compare positions
        orig_pos = original[key]
        rend_pos = rendered[key]
        
        x1 = orig_pos.get('x', 0)
        y1 = orig_pos.get('y', 0)
        w1 = orig_pos.get('width', 0)
        h1 = orig_pos.get('height', 0)
        
        x2 = rend_pos.get('x', 0)
        y2 = rend_pos.get('y', 0)
        w2 = rend_pos.get('width', 0)
        h2 = rend_pos.get('height', 0)
        
        x_diff = abs(x1 - x2)
        y_diff = abs(y1 - y2)
        w_diff = abs(w1 - w2)
        h_diff = abs(h1 - h2)
        
        if x_diff <= tolerance and y_diff <= tolerance and w_diff <= tolerance and h_diff <= tolerance:
            results['exact_matches'].append({
                'key': key,
                'original_pos': orig_pos,
                'rendered_pos': rend_pos
            })
        else:
            results['position_diffs'].append({
                'key': key,
                'original_pos': orig_pos,
                'rendered_pos': rend_pos,
                'x_diff': x_diff,
                'y_diff': y_diff,
                'width_diff': w_diff,
                'height_diff': h_diff
            })
    
    return results

def assert_layout_positions_preserved():
    """Assert that layout positions are preserved after sync-then-render."""
    print(f"\n{'='*80}")
    print("THEN: Assert layout positions are preserved")
    print(f"{'='*80}")
    
    # Get original DrawIO
    original_drawio_path = given_data.get_original_drawio_path()
    
    # Get rendered DrawIO
    rendered_drawio_path = then_dir / "actual-rendered.drawio"
    
    if not original_drawio_path.exists():
        print(f"[ERROR] Original DrawIO not found: {original_drawio_path}")
        return False
    
    if not rendered_drawio_path.exists():
        print(f"[ERROR] Rendered DrawIO not found: {rendered_drawio_path}")
        return False
    
    # Extract positions from both DrawIOs
    print(f"\n1. Extracting positions from original DrawIO...")
    original_positions = extract_positions_from_drawio(original_drawio_path)
    print(f"   [OK] Extracted {len(original_positions)} positions from original")
    
    print(f"\n2. Extracting positions from rendered DrawIO...")
    rendered_positions = extract_positions_from_drawio(rendered_drawio_path)
    print(f"   [OK] Extracted {len(rendered_positions)} positions from rendered")
    
    # Compare layouts
    print(f"\n3. Comparing layouts (tolerance: 5.0px)...")
    comparison = compare_layouts(original_positions, rendered_positions, tolerance=5.0)
    
    # Calculate preservation rate
    total_comparable = len(comparison['exact_matches']) + len(comparison['position_diffs'])
    preservation_rate = 0.0
    if total_comparable > 0:
        preservation_rate = len(comparison['exact_matches']) / total_comparable * 100
    
    # Print results
    print(f"\n{'='*80}")
    print("LAYOUT PRESERVATION RESULTS")
    print(f"{'='*80}")
    print(f"Total original positions: {comparison['total_original']}")
    print(f"Total rendered positions: {comparison['total_rendered']}")
    print(f"Exact matches (within {comparison['tolerance']}px): {len(comparison['exact_matches'])}")
    print(f"Position differences: {len(comparison['position_diffs'])}")
    print(f"Missing in rendered: {len(comparison['missing_in_rendered'])}")
    print(f"New in rendered: {len(comparison['new_in_rendered'])}")
    
    if total_comparable > 0:
        print(f"\nLayout preservation rate: {preservation_rate:.1f}%")
    
    # Show top differences
    if comparison['position_diffs']:
        print(f"\nTop 5 position differences:")
        for i, diff in enumerate(comparison['position_diffs'][:5], 1):
            print(f"  {i}. {diff['key'][:60]}")
            print(f"     X diff: {diff['x_diff']:.1f}px, Y diff: {diff['y_diff']:.1f}px")
    
    # Save comparison report
    report_path = then_dir / "layout-comparison-report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    print(f"\nDetailed report saved to: {report_path}")
    
    # Determine success (at least 80% preservation rate)
    success = preservation_rate >= 80.0 and len(comparison['missing_in_rendered']) < len(comparison['total_original']) * 0.2
    
    print(f"\n{'='*80}")
    if success:
        print("[OK] Layout positions are preserved!")
    else:
        print("[FAIL] Layout positions not adequately preserved!")
    print(f"{'='*80}")
    
    return success

if __name__ == '__main__':
    try:
        success = assert_layout_positions_preserved()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Assertion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)




