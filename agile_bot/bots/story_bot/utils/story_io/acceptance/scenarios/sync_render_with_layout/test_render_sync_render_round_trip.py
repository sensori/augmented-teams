"""
Test extract and render workflow.

Given -> When -> Then workflow:
1. Given: Original DrawIO file (source of truth)
2. When: Extract from DrawIO to JSON
3. Then: Render JSON to DrawIO and assert extracted JSON matches expected

Asserts extracted JSON matches expected JSON.
"""
import sys
import io
import json
import shutil
import xml.etree.ElementTree as ET
import re
from pathlib import Path

# Fix encoding for Windows - ensure output is visible and unbuffered
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Set up logging to file
test_dir = Path(__file__).parent
log_file = test_dir / "test_output.log"
log_handle = open(log_file, 'w', encoding='utf-8', buffering=1)

class TeeOutput:
    """Tee output to both stdout and file."""
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            try:
                f.write(obj)
                f.flush()
            except (ValueError, OSError):
                pass
    def flush(self):
        for f in self.files:
            try:
                f.flush()
            except (ValueError, OSError):
                pass

sys.stdout = TeeOutput(sys.stdout, log_handle)
sys.stderr = TeeOutput(sys.stderr, log_handle)

# Add parent directories to path
scenario_dir = test_dir
acceptance_dir = scenario_dir.parent.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))


def get_cell_value(cell) -> str:
    """Extract text value from a cell, handling HTML entities."""
    value = cell.get('value', '')
    value = value.replace('&amp;', '&').replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    value = re.sub(r'<[^>]+>', '', value)
    return value.strip()


def extract_geometry(cell):
    """Extract geometry information from a cell."""
    geom = cell.find('mxGeometry')
    if geom is None:
        return None
    x = float(geom.get('x', 0))
    y = float(geom.get('y', 0))
    width = float(geom.get('width', 0))
    height = float(geom.get('height', 0))
    return {'x': x, 'y': y, 'width': width, 'height': height}


def extract_drawio_structure(drawio_path: Path) -> dict:
    """
    Extract epic, feature, and story structure from DrawIO file using actual extraction code.
    Includes positioning for epics and features only, not stories.
    """
    from story_io.story_map_drawio_synchronizer import get_epics_features_and_boundaries, build_stories_for_epics_features
    
    # Get epics and features using actual extraction code
    epics_features = get_epics_features_and_boundaries(drawio_path)
    epics = epics_features['epics']
    features = epics_features['features']
    
    # Build stories using actual extraction code
    epics_with_stories = build_stories_for_epics_features(drawio_path, epics, features, return_layout=False)
    
    structure = {
        'epics': [],
        'features': [],
        'stories': []
    }
    
    # Extract epics with positioning
    for epic in epics:
        structure['epics'].append({
            'name': epic['name'],
            'x': epic['x'],
            'y': epic['y']
        })
    
    # Extract features with positioning
    for feature in features:
        structure['features'].append({
            'name': feature['name'],
            'x': feature['x'],
            'y': feature['y']
        })
    
    # Extract stories (names only, no positioning)
    for epic_data in epics_with_stories['epics']:
        for feature_data in epic_data.get('sub_epics', []):
            for story_group in feature_data.get('story_groups', []):
                for story in story_group.get('stories', []):
                    structure['stories'].append({
                        'name': story['name']
                    })
    
    return structure


def compare_drawio_structures(actual_path: Path, expected_path: Path):
    """
    Compare DrawIO files by structure (epics, features, stories) and shapes.
    Compares positioning ONLY for epics and features (sub-epics), NOT for stories.
    Returns (is_match, error_message)
    """
    if not expected_path.exists():
        return True, ""  # No expected file, skip comparison
    
    try:
        actual_struct = extract_drawio_structure(actual_path)
        expected_struct = extract_drawio_structure(expected_path)
        
        errors = []
        tolerance = 10  # pixels tolerance for position comparison
        
        # Compare epics (names and positioning)
        actual_epics_dict = {e['name']: e for e in actual_struct['epics']}
        expected_epics_dict = {e['name']: e for e in expected_struct['epics']}
        actual_epic_names = set(actual_epics_dict.keys())
        expected_epic_names = set(expected_epics_dict.keys())
        if actual_epic_names != expected_epic_names:
            errors.append(f"Epic names mismatch: actual={actual_epic_names}, expected={expected_epic_names}")
        else:
            # Check positioning for each epic
            for epic_name in actual_epic_names:
                actual_epic = actual_epics_dict[epic_name]
                expected_epic = expected_epics_dict[epic_name]
                if (abs(actual_epic['x'] - expected_epic['x']) > tolerance or
                    abs(actual_epic['y'] - expected_epic['y']) > tolerance):
                    errors.append(f"Epic '{epic_name}' position mismatch: actual=({actual_epic['x']}, {actual_epic['y']}), expected=({expected_epic['x']}, {expected_epic['y']})")
        
        # Compare features (names and positioning)
        actual_features_dict = {f['name']: f for f in actual_struct['features']}
        expected_features_dict = {f['name']: f for f in expected_struct['features']}
        actual_feature_names = set(actual_features_dict.keys())
        expected_feature_names = set(expected_features_dict.keys())
        if actual_feature_names != expected_feature_names:
            errors.append(f"Feature names mismatch: actual={actual_feature_names}, expected={expected_feature_names}")
        else:
            # Check positioning for each feature
            for feature_name in actual_feature_names:
                actual_feature = actual_features_dict[feature_name]
                expected_feature = expected_features_dict[feature_name]
                if (abs(actual_feature['x'] - expected_feature['x']) > tolerance or
                    abs(actual_feature['y'] - expected_feature['y']) > tolerance):
                    errors.append(f"Feature '{feature_name}' position mismatch: actual=({actual_feature['x']}, {actual_feature['y']}), expected=({expected_feature['x']}, {expected_feature['y']})")
        
        # Compare stories (names only, NO positioning)
        actual_stories = {s['name'] for s in actual_struct['stories']}
        expected_stories = {s['name'] for s in expected_struct['stories']}
        if actual_stories != expected_stories:
            errors.append(f"Story names mismatch: actual={actual_stories}, expected={expected_stories}")
        
        if errors:
            return False, "; ".join(errors)
        
        return True, ""
    except Exception as e:
        return False, f"Error comparing DrawIO structures: {e}"

def main():
    """Run extract and render workflow."""
    print(f"\n{'='*80}", flush=True)
    print("EXTRACT AND RENDER TEST", flush=True)
    print(f"{'='*80}", flush=True)
    
    given_dir = test_dir / "1_given"
    when_dir = test_dir / "2_when"
    then_dir = test_dir / "3_then"
    
    # Step 1: Given - original DrawIO (source of truth)
    print("\nGIVEN: Original DrawIO file (source of truth)...", flush=True)
    original_drawio = given_dir / "original.drawio"
    
    if not original_drawio.exists():
        print(f"   [ERROR] Original DrawIO not found: {original_drawio}", flush=True)
        return False
    
    print(f"   [OK] Original DrawIO: {original_drawio}", flush=True)
    
    # Step 2: When - Extract from DrawIO to JSON
    print("\nWHEN: Extract from DrawIO to JSON...", flush=True)
    when_dir.mkdir(parents=True, exist_ok=True)
    extracted_json = when_dir / "actual-extracted.json"
    
    from story_io.story_io_diagram import StoryIODiagram
    
    diagram = StoryIODiagram()
    diagram.synchronize_outline(
        drawio_path=original_drawio,
        output_path=extracted_json
    )
    
    print(f"   [OK] Extracted JSON: {extracted_json}", flush=True)
    
    # Assert extracted JSON matches expected
    expected_json = given_dir / "expected-extracted.json"
    if expected_json.exists():
        print("\nASSERT: Extracted JSON matches expected...", flush=True)
        with open(extracted_json, 'r', encoding='utf-8') as f:
            actual_data = json.load(f)
        with open(expected_json, 'r', encoding='utf-8') as f:
            expected_data = json.load(f)
        
        if actual_data != expected_data:
            print(f"   [FAIL] Extracted JSON does not match expected!", flush=True)
            print(f"   Actual:   {extracted_json}", flush=True)
            print(f"   Expected: {expected_json}", flush=True)
            return False
        else:
            print(f"   [OK] Extracted JSON matches expected", flush=True)
    else:
        print(f"   [SKIP] Expected JSON not found: {expected_json}", flush=True)
        print(f"   [INFO] To create expected JSON, copy actual-extracted.json to expected-extracted.json", flush=True)
    
    # Step 3: Then - Move extracted JSON to then directory and render to DrawIO
    print("\nTHEN: Move extracted JSON and render to DrawIO...", flush=True)
    then_dir.mkdir(parents=True, exist_ok=True)
    
    # Move extracted JSON to then directory
    actual_json_then = then_dir / "actual-extracted.json"
    shutil.move(str(extracted_json), str(actual_json_then))
    print(f"   [OK] Moved extracted JSON to: {actual_json_then}", flush=True)
    
    # Assert against expected JSON in then directory if it exists
    expected_json_then = then_dir / "expected.json"
    if expected_json_then.exists():
        print("\nASSERT: Extracted JSON in then matches expected...", flush=True)
        with open(actual_json_then, 'r', encoding='utf-8') as f:
            actual_data = json.load(f)
        with open(expected_json_then, 'r', encoding='utf-8') as f:
            expected_data = json.load(f)
        
        if actual_data != expected_data:
            print(f"   [FAIL] Extracted JSON does not match expected!", flush=True)
            print(f"   Actual:   {actual_json_then}", flush=True)
            print(f"   Expected: {expected_json_then}", flush=True)
            return False
        else:
            print(f"   [OK] Extracted JSON matches expected", flush=True)
    
    # Render JSON to DrawIO
    rendered_drawio = then_dir / "actual-rendered.drawio"
    
    with open(actual_json_then, 'r', encoding='utf-8') as f:
        extracted_graph = json.load(f)
    
    StoryIODiagram.render_outline_from_graph(
        story_graph=extracted_graph,
        output_path=rendered_drawio,
        layout_data=None
    )
    
    print(f"   [OK] Rendered DrawIO: {rendered_drawio}", flush=True)
    
    print(f"\n{'='*80}", flush=True)
    print("Test completed successfully!", flush=True)
    print(f"  Original DrawIO:  {original_drawio}", flush=True)
    print(f"  Extracted JSON:   {extracted_json}", flush=True)
    print(f"  Extracted JSON (then): {actual_json_then}", flush=True)
    print(f"  Rendered DrawIO:  {rendered_drawio}", flush=True)
    print(f"{'='*80}", flush=True)
    
    return True

if __name__ == '__main__':
    success = False
    try:
        success = main()
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}", flush=True)
        import traceback
        traceback.print_exc()
        success = False
    finally:
        try:
            if 'log_handle' in globals() and log_handle:
                log_handle.close()
        except Exception:
            pass
    sys.exit(0 if success else 1)
