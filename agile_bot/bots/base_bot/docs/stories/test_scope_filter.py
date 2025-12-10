#!/usr/bin/env python3
import sys
import json
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agile_bot.bots.story_bot.src.synchronizers.story_io.story_io_diagram import StoryIODiagram

# Load story graph
with open('story-graph.json', 'r', encoding='utf-8') as f:
    story_graph = json.load(f)

# Find Code Scanner increment
code_scanner_inc = None
for inc in story_graph.get("increments", []):
    if inc.get("name") == "Code Scanner":
        code_scanner_inc = inc
        break

if code_scanner_inc:
    print(f"Found Code Scanner increment")
    # Count stories
    story_count = 0
    for epic in code_scanner_inc.get("epics", []):
        epic_name = epic.get("name", "")
        for sub_epic in epic.get("sub_epics", []):
            sub_epic_name = sub_epic.get("name", "")
            for story_group in sub_epic.get("story_groups", []):
                for story in story_group.get("stories", []):
                    story_count += 1
                    print(f"  Story: {epic_name}|{sub_epic_name}|{story.get('name', '')}")
    print(f"Total stories in Code Scanner increment: {story_count}")
else:
    print("Code Scanner increment not found!")

# Render with scope
diagram = StoryIODiagram()
result = diagram.render_exploration(
    story_graph=story_graph,
    output_path=Path('story-map-explored-Code-Scanner.drawio'),
    scope="Code Scanner"
)
print(f"\nRender result: {result}")

