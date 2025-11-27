import xml.etree.ElementTree as ET

def get_geometry(cell):
    geom = cell.find('mxGeometry')
    if geom is not None:
        x = float(geom.get('x', 0))
        y = float(geom.get('y', 0))
        return x, y
    return None, None

tree = ET.parse('story-map.drawio')
root = tree.getroot()

# Search for cells with the increment name text
target_texts = [
    "User Manually Drops Behavior Config Folder to Guide AI Chat",
    "Minimal MCP Tool / AI Creates Data",
    "MCP Behavior Tool Routes To Action",
    "MCP Bot Tool Routes To Behavior and Action",
    "Bot Stores All Data"
]

increments = {}
count = 0

for cell in root.findall('.//mxCell'):
    value = cell.get('value', '').strip().replace('&amp;nbsp;', ' ').replace('&amp;', '&')
    if any(target in value for target in target_texts):
        count += 1
        style = cell.get('style', '')
        x, y = get_geometry(cell)
        cell_id = cell.get('id', 'N/A')
        
        print(f"\nFound cell {count}: ID={cell_id}")
        print(f"  Value: {value[:60]}")
        print(f"  Has strokeColor=#f8f7f7: {'strokeColor=#f8f7f7' in style}")
        print(f"  X={x}, Y={y}")
        print(f"  X < 0: {x is not None and x < 0}")
        
        if 'strokeColor=#f8f7f7' in style and value and x is not None and y is not None and x < 0:
            increments[y] = {'name': value, 'y': y, 'x': x}
            print(f"  -> ADDED TO INCREMENTS")

print(f"\nTotal matching cells found: {count}")
print(f"Total increments found: {len(increments)}")
for y, data in sorted(increments.items()):
    print(f"  Y={y:.1f}: {data['name']}")

