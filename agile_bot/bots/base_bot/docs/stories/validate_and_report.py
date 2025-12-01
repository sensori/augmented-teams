"""Quick validation script that writes to file."""
import json
import xml.etree.ElementTree as ET
from collections import defaultdict

# Load JSON
with open('story-graph_new.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# Load DrawIO
tree = ET.parse('story-map-outline.drawio')
root = tree.getroot()

# Extract epics from DrawIO
drawio_epics = []
for cell in root.findall(".//mxCell[@vertex='1']"):
    style = cell.get('style', '')
    if '#e1d5e7' in style and 'rounded=1' in style:
        value = cell.get('value', '').strip()
        if value:
            drawio_epics.append(value)

# Extract sub-epics from DrawIO
drawio_sub_epics = defaultdict(list)
current_epic = None
for cell in root.findall(".//mxCell[@vertex='1']"):
    style = cell.get('style', '')
    value = cell.get('value', '').strip()
    geometry = cell.find('mxGeometry')
    
    if not geometry or not value:
        continue
    
    y = float(geometry.get('y', 0))
    
    # Epic
    if '#e1d5e7' in style and 'rounded=1' in style and abs(y - 130) < 50:
        current_epic = value
    # Sub-epic
    elif '#d5e8d4' in style and 'rounded=1' in style and 196 <= y <= 250:
        if current_epic:
            drawio_sub_epics[current_epic].append(value)

# Extract stories from DrawIO
drawio_stories = defaultdict(lambda: defaultdict(list))
current_sub_epic = None
for cell in root.findall(".//mxCell[@vertex='1']"):
    style = cell.get('style', '')
    value = cell.get('value', '').strip()
    geometry = cell.find('mxGeometry')
    
    if not geometry or not value:
        continue
    
    y = float(geometry.get('y', 0))
    
    # Sub-epic
    if '#d5e8d4' in style and 'rounded=1' in style and 196 <= y <= 250:
        # Find parent epic
        x = float(geometry.get('x', 0))
        for epic_name in drawio_epics:
            epic_cell = next((c for c in root.findall(".//mxCell[@vertex='1']") 
                            if c.get('value', '').strip() == epic_name), None)
            if epic_cell:
                epic_geo = epic_cell.find('mxGeometry')
                if epic_geo:
                    epic_x = float(epic_geo.get('x', 0))
                    epic_width = float(epic_geo.get('width', 0))
                    if epic_x <= x <= epic_x + epic_width:
                        current_sub_epic = (epic_name, value)
                        break
    # Story
    elif y >= 337 and '#fff2cc' in style:
        if current_sub_epic:
            drawio_stories[current_sub_epic[0]][current_sub_epic[1]].append(value)

# Extract JSON structure
json_epics = {epic['name'] for epic in json_data.get('epics', [])}
json_sub_epics = defaultdict(list)
json_stories = defaultdict(lambda: defaultdict(set))

for epic in json_data.get('epics', []):
    epic_name = epic['name']
    for sub_epic in epic.get('sub_epics', []):
        sub_epic_name = sub_epic['name']
        json_sub_epics[epic_name].append(sub_epic_name)
        for story in sub_epic.get('stories', []):
            json_stories[epic_name][sub_epic_name].add(story['name'])
            # Collect nested stories
            def collect_nested(s):
                for nested in s.get('stories', []):
                    json_stories[epic_name][sub_epic_name].add(nested['name'])
                    collect_nested(nested)
            collect_nested(story)

# Generate report
report = []
report.append("=" * 80)
report.append("STORY GRAPH VALIDATION REPORT")
report.append("=" * 80)
report.append("")

# Check epics
report.append("EPICS:")
report.append(f"  JSON: {sorted(json_epics)}")
report.append(f"  DrawIO: {sorted(drawio_epics)}")
missing_in_drawio = json_epics - set(drawio_epics)
missing_in_json = set(drawio_epics) - json_epics
if missing_in_drawio:
    report.append(f"  ERROR: Missing in DrawIO: {missing_in_drawio}")
if missing_in_json:
    report.append(f"  WARNING: Missing in JSON: {missing_in_json}")
report.append("")

# Check sub-epics
report.append("SUB-EPICS:")
all_epics = json_epics | set(drawio_epics)
for epic_name in sorted(all_epics):
    json_subs = set(json_sub_epics.get(epic_name, []))
    drawio_subs = set(drawio_sub_epics.get(epic_name, []))
    if json_subs != drawio_subs:
        report.append(f"  Epic '{epic_name}':")
        report.append(f"    JSON: {sorted(json_subs)}")
        report.append(f"    DrawIO: {sorted(drawio_subs)}")
        missing = json_subs - drawio_subs
        extra = drawio_subs - json_subs
        if missing:
            report.append(f"    ERROR: Missing in DrawIO: {missing}")
        if extra:
            report.append(f"    WARNING: Missing in JSON: {extra}")
report.append("")

# Check stories (sample)
report.append("STORIES (Sample - first 3 sub-epics):")
count = 0
for epic_name in sorted(all_epics):
    if count >= 3:
        break
    for sub_epic_name in sorted(set(json_sub_epics.get(epic_name, [])) | set(drawio_sub_epics.get(epic_name, []))):
        if count >= 3:
            break
        json_story_set = json_stories.get(epic_name, {}).get(sub_epic_name, set())
        drawio_story_list = drawio_stories.get(epic_name, {}).get(sub_epic_name, [])
        drawio_story_set = set(drawio_story_list)
        
        if json_story_set != drawio_story_set:
            report.append(f"  Sub-epic '{sub_epic_name}' (Epic '{epic_name}'):")
            report.append(f"    JSON count: {len(json_story_set)}")
            report.append(f"    DrawIO count: {len(drawio_story_set)}")
            missing = json_story_set - drawio_story_set
            extra = drawio_story_set - json_story_set
            if missing:
                report.append(f"    ERROR: Missing in DrawIO ({len(missing)}): {list(missing)[:5]}")
            if extra:
                report.append(f"    WARNING: Missing in JSON ({len(extra)}): {list(extra)[:5]}")
        count += 1

# Write report
with open('validation_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print('\n'.join(report))


