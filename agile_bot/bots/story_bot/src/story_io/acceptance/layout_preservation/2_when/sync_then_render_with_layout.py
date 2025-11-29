"""
Sync then render with layout workflow execution.

WHEN: DrawIO is synced to extract story graph and layout, then rendered again

UNIQUE TO THIS WORKFLOW:
- Executes sync-then-render workflow (sync from DrawIO → render with extracted layout)
- Uses render_outline_from_graph (outline mode, all stories)
- Syncs from original DrawIO to extract story graph + layout
- Renders once with extracted layout to preserve all element positioning
- Tests layout preservation for real-world workflow
"""
import sys
from pathlib import Path

# Add parent directories to path
when_dir = Path(__file__).parent
test_dir = when_dir.parent
acceptance_dir = test_dir.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(acceptance_dir.parent / "spec_by_example"))

from story_io.story_io_diagram import StoryIODiagram
from story_graph_layout_helper import load_story_graph, load_layout_data, find_extracted_layout

# Import from given folder
given_dir = test_dir / "1_given"
sys.path.insert(0, str(given_dir))
import importlib.util
spec = importlib.util.spec_from_file_location("load_drawio_data", given_dir / "load_drawio_data.py")
given_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(given_data)

def sync_then_render_with_layout():
    """Sync DrawIO to extract story graph and layout, then render with layout."""
    # Paths
    then_dir = test_dir / "3_then"
    
    # Get input files from given
    original_drawio_path = given_data.get_original_drawio_path()
    
    # Output files
    then_dir.mkdir(parents=True, exist_ok=True)
    extracted_json_path = when_dir / "extracted-story-graph.json"
    rendered_drawio_path = then_dir / "actual-rendered.drawio"
    
    print(f"\n{'='*80}")
    print("WHEN: Sync DrawIO to extract story graph and layout, then render again")
    print(f"{'='*80}")
    print(f"Original DrawIO: {original_drawio_path}")
    
    if not original_drawio_path.exists():
        print(f"[ERROR] Original DrawIO not found: {original_drawio_path}")
        return False
    
    # Step 1: Sync from DrawIO to extract story graph + layout
    print(f"\n1. Syncing from DrawIO to extract story graph and layout...")
    diagram = StoryIODiagram(drawio_file=original_drawio_path)
    diagram.synchronize_outline(
        drawio_path=original_drawio_path,
        original_path=None,
        output_path=extracted_json_path,
        generate_report=True
    )
    diagram.save_story_graph(extracted_json_path)
    print(f"   [OK] Extracted story graph saved to: {extracted_json_path}")
    
    # Load extracted layout (layout file is generated during sync)
    extracted_layout_path = find_extracted_layout(extracted_json_path)
    layout_data = None
    if extracted_layout_path:
        layout_data = load_layout_data(extracted_layout_path)
        print(f"   [OK] Extracted layout from: {extracted_layout_path}")
    else:
        print(f"   [WARN] Layout file not found, rendering without layout")
    
    # Step 2: Render DrawIO from extracted graph with layout
    print(f"\n2. Rendering DrawIO from extracted graph (with layout)...")
    extracted_graph = load_story_graph(extracted_json_path)
    
    StoryIODiagram.render_outline_from_graph(
        story_graph=extracted_graph,
        output_path=rendered_drawio_path,
        layout_data=layout_data
    )
    print(f"   [OK] Rendered DrawIO saved to: {rendered_drawio_path}")
    
    print(f"\n{'='*80}")
    print("[OK] Workflow execution completed")
    print(f"{'='*80}")
    print(f"Extracted JSON: {extracted_json_path}")
    print(f"Layout:       {extracted_layout_path if extracted_layout_path else 'Not found'}")
    print(f"Rendered:     {rendered_drawio_path}")
    
    return True

if __name__ == '__main__':
    try:
        success = sync_then_render_with_layout()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)




