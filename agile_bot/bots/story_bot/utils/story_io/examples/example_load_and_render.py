"""
Example: Load and render from structured.json

This shows exactly how to:
1. Load story graph from file
2. Render to DrawIO
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from story_io.story_io_diagram import StoryIODiagram
from story_io.render_example import adapt_story_graph
import json


# Load from the structured.json file
structured_path = Path(__file__).parent.parent.parent.parent / "demo" / "cheap_wealth_online" / "docs" / "stories" / "structured.json"

# Load the JSON
with open(structured_path, 'r', encoding='utf-8') as f:
    original_data = json.load(f)

# Adapt format (converts behavioral_ac to Steps, handles empty users)
adapted_data = adapt_story_graph(original_data)

# Option 1: Load into diagram, then render
diagram = StoryIODiagram.load_from_story_graph(
    story_graph_path=structured_path,  # Note: This expects our format, so use adapted
    drawio_file=None
)

# Load adapted data into diagram
diagram._load_from_story_graph_format(adapted_data)

# Render outline
result = diagram.render_outline(output_path='demo/cheap_wealth_online/docs/stories/story-map-outline.drawio')

print(f"Rendered: {result['output_path']}")
print(f"Epics: {result['summary'].get('epics', 0)}")


# Option 2: Render directly from graph (simpler)
# result = StoryIODiagram.render_outline_from_graph(
#     story_graph=adapted_data,
#     output_path='demo/cheap_wealth_online/docs/stories/story-map-outline.drawio'
# )

