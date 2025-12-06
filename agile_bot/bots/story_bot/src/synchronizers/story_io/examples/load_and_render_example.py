"""
Direct Example: Load structured.json and Render

This is the exact code pattern you requested.
"""

import sys
import json
from pathlib import Path

from ..story_io_diagram import StoryIODiagram
from .render_example import adapt_story_graph

# File path
structured_file = Path(__file__).parent.parent.parent.parent / "demo" / "cheap_wealth_online" / "docs" / "stories" / "structured.json"

# Load and adapt the story graph
with open(structured_file, 'r', encoding='utf-8') as f:
    original_data = json.load(f)

# Adapt to our format (converts behavioral_ac to Steps)
adapted_data = adapt_story_graph(original_data)

# Now load into diagram (using adapted data)
# Create diagram instance
diagram = StoryIODiagram()

# Load the adapted data
diagram._load_from_story_graph_format(adapted_data)

# Render outline
result = diagram.render_outline(
    output_path='demo/cheap_wealth_online/docs/stories/story-map-outline.drawio'
)

print(f"Rendered to: {result['output_path']}")
print(f"Epics: {result['summary'].get('epics', 0)}")

