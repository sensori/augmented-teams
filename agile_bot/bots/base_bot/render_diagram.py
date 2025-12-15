import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from story_bot.src.synchronizers.story_io.story_io_diagram import StoryIODiagram

# Load and render
diagram = StoryIODiagram.load_from_story_graph(
    Path('docs/stories/story-graph.json'), 
    None
)

result = diagram.render_increments(
    output_path=Path('docs/stories/story-map-increments.drawio'),
    layout_data=None
)

print(f'Generated: {result["output_path"]}')
print(f'Epics: {result["summary"]["epics"]}')
print(f'Increments: {result["summary"]["increments"]}')
print(f'Stories: {result["summary"]["stories"]}')



