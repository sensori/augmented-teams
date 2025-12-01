"""
WHEN: Sync DrawIO to JSON.

Extracts story graph from DrawIO file and saves to JSON.
"""
import sys
import io
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Add parent directories to path
when_dir = Path(__file__).parent
test_dir = when_dir.parent
scenario_dir = test_dir.parent
acceptance_dir = scenario_dir.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(acceptance_dir / "spec_by_example"))
sys.path.insert(0, str(scenario_dir))

from story_io.story_io_diagram import StoryIODiagram

def sync_from_drawio():
    """Extract story graph from DrawIO and save to JSON."""
    print("="*80)
    print("WHEN: Sync DrawIO to JSON")
    print("="*80)
    
    # Get input DrawIO from 1_given
    given_dir = test_dir / "1_given"
    drawio_path = given_dir / "expected- story-map-outline.drawio"
    
    if not drawio_path.exists():
        print(f"[ERROR] DrawIO file not found: {drawio_path}")
        return False
    
    print(f"Input DrawIO: {drawio_path}")
    
    # Output files:
    # - Extracted JSON goes to 3_then (actual output for comparison)
    # - Layout data goes to 2_when (intermediate file)
    then_dir = test_dir / "3_then"
    extracted_json_path = then_dir / "actual-extracted-story-graph.json"
    
    # Extract from DrawIO
    print("\nExtracting story graph from DrawIO...")
    diagram = StoryIODiagram(drawio_file=drawio_path)
    diagram.synchronize_outline(drawio_path=drawio_path, output_path=extracted_json_path)
    
    print(f"[OK] Extracted JSON saved to: {extracted_json_path}")
    
    # Layout file is saved automatically by synchronize_outline to same directory as output_path
    # But we want it in 2_when, so check if it was created and move it
    layout_in_then = then_dir / "extracted-story-graph-layout.json"
    layout_in_when = when_dir / "extracted-story-graph-layout.json"
    if layout_in_then.exists():
        import shutil
        shutil.move(str(layout_in_then), str(layout_in_when))
        print(f"[OK] Layout data saved to: {layout_in_when}")
    
    return True

if __name__ == "__main__":
    success = sync_from_drawio()
    sys.exit(0 if success else 1)

