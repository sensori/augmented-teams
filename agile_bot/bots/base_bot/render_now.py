#!/usr/bin/env python3
import sys
from pathlib import Path

# Add workspace root to path
workspace_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(workspace_root))

# Now import
from agile_bot.bots.story_bot.src.synchronizers.story_io.story_io_diagram import StoryIODiagram

# Render
base_bot_dir = Path(__file__).parent
story_graph = base_bot_dir / 'docs/stories/story-graph.json'
output = base_bot_dir / 'docs/stories/story-map-increments.drawio'

print(f"Loading from: {story_graph}")
diagram = StoryIODiagram.load_from_story_graph(story_graph, None)

print(f"Rendering to: {output}")
result = diagram.render_increments(output_path=output, layout_data=None)

print(f"Generated: {result['output_path']}")
print(f"Epics: {result['summary']['epics']}")
print(f"Increments: {result['summary']['increments']}")
print("Done!")
