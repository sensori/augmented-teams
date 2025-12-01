#!/usr/bin/env python3
"""
Convert all test JSON files to story_groups structure and add grey squares to expected DrawIO files.
"""

import sys
import json
from pathlib import Path
import xml.etree.ElementTree as ET

# Add parent directories to path
scenarios_dir = Path(__file__).parent
sys.path.insert(0, str(scenarios_dir))
sys.path.insert(0, str(scenarios_dir.parent))

from convert_to_story_groups import convert_file


def add_grey_squares_to_drawio(drawio_path: Path):
    """Add grey background rectangles for story groups to DrawIO file."""
    if not drawio_path.exists():
        print(f"  DrawIO file not found: {drawio_path}")
        return False
    
    try:
        tree = ET.parse(drawio_path)
        root = tree.getroot()
        
        # Find all story cells (yellow boxes) - they're directly in the XML tree
        story_cells = []
        root_container = None
        
        for cell in root.findall('.//mxCell'):
            style = cell.get('style', '')
            # Story cells have fillColor=#fff2cc (yellow)
            if 'fillColor=#fff2cc' in style:
                geom = cell.find('mxGeometry')
                if geom is not None:
                    x = float(geom.get('x', 0))
                    y = float(geom.get('y', 0))
                    width = float(geom.get('width', 50))
                    height = float(geom.get('height', 50))
                    story_cells.append({
                        'cell': cell,
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height
                    })
                    # Find the root container (parent of cells)
                    if root_container is None:
                        # Find parent by searching for this cell in all possible parents
                        for possible_parent in root.findall('.//root'):
                            if cell in list(possible_parent):
                                root_container = possible_parent
                                break
        
        if not story_cells:
            print(f"  No story cells found in: {drawio_path}")
            return False
        
        if root_container is None:
            print(f"  No root container found in: {drawio_path}")
            return False
        
        # Group stories by Y position (rows) within tolerance
        tolerance = 10
        rows = {}
        for story in story_cells:
            y_key = round(story['y'] / tolerance) * tolerance
            if y_key not in rows:
                rows[y_key] = []
            rows[y_key].append(story)
        
        # Remove existing grey rectangles
        grey_rects_to_remove = []
        for cell in root.findall('.//mxCell'):
            style = cell.get('style', '')
            if 'fillColor=#F7F7F7' in style or 'fillColor=#f7f7f7' in style:
                grey_rects_to_remove.append(cell)
        
        for cell in grey_rects_to_remove:
            parent = None
            # Find parent by searching for this cell in all possible parents
            for possible_parent in root.findall('.//root'):
                if cell in list(possible_parent):
                    parent = possible_parent
                    break
            
            if parent is not None:
                parent.remove(cell)
        
        # Find max ID
        max_id = 0
        for cell in root.findall('.//mxCell'):
            cell_id = cell.get('id', '')
            if cell_id.isdigit():
                max_id = max(max_id, int(cell_id))
        
        bg_rect_id = max_id + 1
        padding = 5
        
        # Find first story cell to insert before
        first_story_cell = story_cells[0]['cell'] if story_cells else None
        
        rectangles_to_insert = []
        
        for y_key in sorted(rows.keys()):
            row_stories = rows[y_key]
            if len(row_stories) < 2:
                continue
            
            # Calculate bounding box
            min_x = min(s['x'] for s in row_stories) - padding
            max_x = max(s['x'] + s['width'] for s in row_stories) + padding
            min_y = min(s['y'] for s in row_stories) - padding
            max_y = max(s['y'] + s['height'] for s in row_stories) + padding
            
            rect_width = max_x - min_x
            rect_height = max_y - min_y
            
            # Create grey background rectangle
            bg_rect = ET.Element('mxCell',
                                id=str(bg_rect_id),
                                value='',
                                style='rounded=0;whiteSpace=wrap;html=1;dashed=1;dashPattern=1 2;strokeColor=#FFFFFF;fillColor=#F7F7F7;',
                                parent='1', vertex='1')
            bg_geom = ET.SubElement(bg_rect, 'mxGeometry',
                                    x=str(min_x), y=str(min_y),
                                    width=str(rect_width), height=str(rect_height))
            bg_geom.set('as', 'geometry')
            
            rectangles_to_insert.append((bg_rect_id, bg_rect))
            bg_rect_id += 1
        
        # Insert rectangles before first story cell
        if rectangles_to_insert and first_story_cell is not None:
            story_index = list(root_container).index(first_story_cell)
            for rect_id, bg_rect in reversed(rectangles_to_insert):
                root_container.insert(story_index, bg_rect)
        
        # Save file
        tree.write(drawio_path, encoding='utf-8', xml_declaration=True)
        print(f"  Added {len(rectangles_to_insert)} grey rectangles to: {drawio_path}")
        return True
        
    except Exception as e:
        import traceback
        print(f"  Error processing {drawio_path}: {e}")
        traceback.print_exc()
        return False


def find_all_test_scenarios():
    """Find all test scenario directories."""
    scenarios_dir = Path(__file__).parent
    scenarios = []
    
    for item in scenarios_dir.iterdir():
        if item.is_dir() and not item.name.startswith('_'):
            # Check if it has a test structure
            if (item / "1_given").exists() or (item / "test_").exists() or any(item.glob("test_*.py")):
                scenarios.append(item)
    
    return sorted(scenarios)


def convert_all_json_files():
    """Convert all JSON files in test scenarios to story_groups structure."""
    scenarios_dir = Path(__file__).parent
    
    # Find all story-graph JSON files
    json_files = list(scenarios_dir.rglob("story-graph*.json"))
    json_files.extend(scenarios_dir.rglob("**/1_given/*.json"))
    
    converted = 0
    skipped = 0
    
    for json_file in json_files:
        # Skip files that are already outputs or in 2_when/3_then
        if "2_when" in str(json_file) or "3_then" in str(json_file) or "actual" in str(json_file):
            continue
        
        try:
            # Check if already converted
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            already_converted = False
            for epic in data.get("epics", []):
                for sub_epic in epic.get("sub_epics", []):
                    if "story_groups" in sub_epic:
                        already_converted = True
                        break
                if already_converted:
                    break
            
            if already_converted:
                skipped += 1
                continue
            
            # Convert
            convert_file(json_file)
            converted += 1
            
        except Exception as e:
            print(f"Error converting {json_file}: {e}")
    
    print(f"\nConverted {converted} files, skipped {skipped} files")


def add_grey_squares_to_all_drawio():
    """Add grey squares to all expected DrawIO files."""
    scenarios_dir = Path(__file__).parent
    
    # Find all expected DrawIO files
    drawio_files = list(scenarios_dir.rglob("expected*.drawio"))
    drawio_files.extend(scenarios_dir.rglob("**/3_then/*.drawio"))
    
    processed = 0
    
    for drawio_file in drawio_files:
        # Skip actual files
        if "actual" in str(drawio_file):
            continue
        
        print(f"\nProcessing: {drawio_file}")
        if add_grey_squares_to_drawio(drawio_file):
            processed += 1
    
    print(f"\nProcessed {processed} DrawIO files")


def run_all_tests():
    """Run all test scripts."""
    scenarios_dir = Path(__file__).parent
    
    # Find all test scripts
    test_scripts = list(scenarios_dir.rglob("test_*.py"))
    
    results = []
    
    for test_script in sorted(test_scripts):
        # Skip this script and conversion scripts
        if "convert" in test_script.name or "add_grey" in test_script.name:
            continue
        
        print(f"\n{'='*80}")
        print(f"Running: {test_script}")
        print(f"{'='*80}")
        
        import subprocess
        try:
            result = subprocess.run(
                [sys.executable, str(test_script)],
                cwd=str(test_script.parent),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            success = result.returncode == 0
            results.append({
                'script': test_script.name,
                'path': str(test_script),
                'success': success,
                'output': result.stdout,
                'error': result.stderr
            })
            
            if success:
                print(f"[OK] {test_script.name}")
            else:
                print(f"[FAIL] {test_script.name}")
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr)
                    
        except Exception as e:
            print(f"[ERROR] {test_script.name}: {e}")
            results.append({
                'script': test_script.name,
                'path': str(test_script),
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {len(results)}")
    
    if failed > 0:
        print("\nFailed tests:")
        for r in results:
            if not r['success']:
                print(f"  - {r['script']}")
    
    return failed == 0


if __name__ == "__main__":
    print("="*80)
    print("CONVERT ALL TESTS TO STORY_GROUPS AND ADD GREY SQUARES")
    print("="*80)
    
    # Step 1: Convert all JSON files
    print("\nStep 1: Converting JSON files to story_groups structure...")
    convert_all_json_files()
    
    # Step 2: Add grey squares to DrawIO files
    print("\nStep 2: Adding grey squares to expected DrawIO files...")
    add_grey_squares_to_all_drawio()
    
    # Step 3: Run all tests
    print("\nStep 3: Running all tests...")
    success = run_all_tests()
    
    sys.exit(0 if success else 1)

