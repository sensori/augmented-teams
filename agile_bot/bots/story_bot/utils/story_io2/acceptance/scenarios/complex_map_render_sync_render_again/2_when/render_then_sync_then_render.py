"""
WHEN: Render JSON to DrawIO, sync back to JSON, then render again.

This workflow script performs:
1. Render story-graph.json → DrawIO (first render)
2. Sync DrawIO → JSON (extract story graph)
3. Render synced JSON → DrawIO (second render)
"""

import json
import sys
import io
from pathlib import Path

# Fix encoding for Windows - ensure output is visible and unbuffered
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from story_graph_to_drawio import render_story_graph_to_drawio
from drawio_to_story_graph import DrawIOToStoryGraph


def main():
    """Execute render → sync → render workflow."""
    import traceback
    
    # Get paths
    scenario_dir = Path(__file__).parent.parent
    given_dir = scenario_dir / '1_given'
    when_dir = scenario_dir / '2_when'
    then_dir = scenario_dir / '3_then'
    
    # Set up logging to file
    log_file = when_dir / 'workflow.log'
    
    def log(msg):
        """Log message to both stdout and file."""
        # Replace Unicode checkmarks with ASCII for better compatibility
        safe_msg = msg.replace('\u2713', '[OK]').replace('\u2717', '[FAIL]')
        print(safe_msg)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    
    # Clear log file
    log_file.write_text('', encoding='utf-8')
    
    try:
        # Ensure directories exist
        then_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Render JSON → DrawIO (first render)
        log("Step 1: Rendering story-graph.json to DrawIO...")
        input_json = given_dir / 'story-graph.json'
        first_drawio = then_dir / 'actual-first-render.drawio'
        
        result1 = render_story_graph_to_drawio(input_json, first_drawio)
        log(f"  [OK] Rendered to: {result1['output_path']}")
        log(f"  Epics: {result1['summary']['epics']}")
        
        # Step 2: Sync DrawIO → JSON
        log("\nStep 2: Syncing DrawIO back to JSON...")
        synced_json = when_dir / 'synced-story-graph.json'
        
        parser = DrawIOToStoryGraph(str(first_drawio))
        synced_story_graph = parser.parse()
        
        with open(synced_json, 'w', encoding='utf-8') as f:
            json.dump(synced_story_graph, f, indent=2, ensure_ascii=False)
        
        log(f"  [OK] Synced to: {synced_json}")
        log(f"  Epics extracted: {len(synced_story_graph.get('epics', []))}")
        
        # Step 3: Render synced JSON → DrawIO (second render)
        log("\nStep 3: Rendering synced JSON to DrawIO...")
        second_drawio = then_dir / 'actual-second-render.drawio'
        
        result2 = render_story_graph_to_drawio(synced_json, second_drawio)
        log(f"  [OK] Rendered to: {result2['output_path']}")
        log(f"  Epics: {result2['summary']['epics']}")
        
        log("\n[OK] Workflow completed successfully!")
        log(f"\nGenerated files:")
        log(f"  - First render: {first_drawio}")
        log(f"  - Synced JSON: {synced_json}")
        log(f"  - Second render: {second_drawio}")
    except Exception as e:
        error_msg = f"ERROR: {e}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(error_msg + '\n')
        sys.exit(1)


if __name__ == '__main__':
    main()
