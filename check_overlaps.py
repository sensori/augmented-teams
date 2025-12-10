import xml.etree.ElementTree as ET

tree = ET.parse('demo/mob_minion/docs/stories/story-map-discovery-Increment1.drawio')
root = tree.getroot()

# Get all stories for epic 1
stories = []
for cell in root.findall('.//mxCell[@id]'):
    cell_id = cell.get('id', '')
    if cell_id.startswith('inc1_e1f') and 's' in cell_id and 'user' not in cell_id:
        geom = cell.find('mxGeometry')
        if geom is not None:
            x = float(geom.get('x', 0))
            y = float(geom.get('y', 0))
            stories.append((cell_id, x, y))

stories.sort(key=lambda s: (s[2], s[1]))  # Sort by Y, then X

print('All stories for epic 1 (sorted by Y then X):')
for story_id, x, y in stories:
    print(f'{story_id}: x={x}, y={y}')

# Check for overlaps
print('\nChecking for overlaps (stories at same X,Y):')
seen_positions = {}
for story_id, x, y in stories:
    pos_key = (x, y)
    if pos_key in seen_positions:
        print(f'OVERLAP: {seen_positions[pos_key]} and {story_id} both at ({x}, {y})')
    else:
        seen_positions[pos_key] = story_id

# Check X positions - should be sequential
print('\nX positions (should be sequential with 60px spacing):')
x_positions = sorted(set(x for _, x, _ in stories))
for i, x in enumerate(x_positions):
    if i > 0:
        spacing = x - x_positions[i-1]
        if spacing != 60:
            print(f'  Gap between {x_positions[i-1]} and {x}: {spacing}px (expected 60px)')

