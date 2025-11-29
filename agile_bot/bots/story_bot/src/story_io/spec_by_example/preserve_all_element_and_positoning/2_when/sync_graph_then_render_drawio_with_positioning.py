"""
Sync-then-render workflow execution.

WHEN: Graph synced from DrawIO and DrawIO is rendered again

UNIQUE TO THIS WORKFLOW:
- Executes sync-then-render workflow (sync from DrawIO → render with extracted layout)
- Uses render_outline_from_graph (outline mode, all stories)
- Syncs from existing DrawIO to extract story graph + layout
- Renders once with extracted layout to preserve all element positioning
- Preserves positioning for complex diagrams with many users and stories
- Ensures that users are positioned over stories correctly
"""
import sys
from pathlib import Path
import shutil

# Add parent directories to path
when_dir = Path(__file__).parent
test_dir = when_dir.parent
spec_dir = test_dir.parent
story_io_dir = spec_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(spec_dir))
sys.path.insert(0, str(test_dir))

from story_io.story_io_diagram import StoryIODiagram
from story_graph_layout_helper import load_story_graph, load_layout_data, find_extracted_layout

# Import from given folder (handle space in folder name)
given_dir = test_dir / "1_given"
sys.path.insert(0, str(given_dir))
import importlib.util
spec = importlib.util.spec_from_file_location("load_story_graph_and_drawio_data", given_dir / "load_story_graph_and_drawio_data.py")
given_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(given_data)

def sync_graph_then_render_drawio_with_positioning():
    """Sync graph then render drawio with positioning preserved."""
    # Paths
    given_dir = test_dir / "1_given"
    then_dir = test_dir / "3_then"
    
    # Get input files from given (using given helper)
    original_drawio_path = given_data.get_drawio_path()
    original_story_graph_path = given_data.get_story_graph_path()
    
    # Output files
    then_dir.mkdir(parents=True, exist_ok=True)
    synced_json_path = when_dir / "story-graph-drawio-extracted.json"
    synced_layout_path = when_dir / "story-graph-drawio-extracted-layout.json"
    rendered_drawio_path = then_dir / "actual-story-outline.drawio"
    
    print(f"\n{'='*80}")
    print("WHEN: Graph synced from DrawIO and DrawIO is rendered again")
    print(f"{'='*80}")
    print(f"Original DrawIO: {original_drawio_path}")
    print(f"Original story graph: {original_story_graph_path}")
    
    if not original_drawio_path.exists():
        print(f"[ERROR] Original DrawIO not found: {original_drawio_path}")
        return False
    
    if not original_story_graph_path.exists():
        print(f"[ERROR] Original story graph not found: {original_story_graph_path}")
        return False
    
    # Step 1: Sync graph from DrawIO (extract story graph + layout)
    print(f"\n1. Syncing graph from DrawIO...")
    diagram = StoryIODiagram(drawio_file=original_drawio_path)
    diagram.synchronize_outline(
        drawio_path=original_drawio_path,
        original_path=original_story_graph_path,
        output_path=synced_json_path,
        generate_report=True
    )
    diagram.save_story_graph(synced_json_path)
    print(f"   [OK] Synced story graph saved to: {synced_json_path}")
    
    # Load extracted layout (layout file is generated during sync)
    extracted_layout_path = find_extracted_layout(synced_json_path)
    layout_data = None
    if extracted_layout_path:
        layout_data = load_layout_data(extracted_layout_path)
        # Also save to expected location for reference
        if not synced_layout_path.exists():
            shutil.copy(extracted_layout_path, synced_layout_path)
        print(f"   [OK] Extracted layout from: {extracted_layout_path}")
    elif synced_layout_path.exists():
        # Fallback: use existing layout file if it exists
        layout_data = load_layout_data(synced_layout_path)
        print(f"   [OK] Using existing layout file: {synced_layout_path}")
    else:
        print(f"   [WARN] Layout file not found, rendering without layout")
    
    # Step 2: Render DrawIO from synced graph with layout
    print(f"\n2. Rendering DrawIO from synced graph (with layout)...")
    synced_graph = load_story_graph(synced_json_path)
    
    StoryIODiagram.render_outline_from_graph(
        story_graph=synced_graph,
        output_path=rendered_drawio_path,
        layout_data=layout_data
    )
    print(f"   [OK] Rendered DrawIO saved to: {rendered_drawio_path}")
    
    print(f"\n{'='*80}")
    print("[OK] Workflow execution completed")
    print(f"{'='*80}")
    print(f"Synced JSON:  {synced_json_path}")
    print(f"Layout:      {synced_layout_path if synced_layout_path.exists() else 'Not found'}")
    print(f"Rendered:    {rendered_drawio_path}")
    
    return True

if __name__ == '__main__':
    try:
        success = sync_graph_then_render_drawio_with_positioning()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

