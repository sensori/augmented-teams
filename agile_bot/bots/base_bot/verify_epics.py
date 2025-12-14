import xml.etree.ElementTree as ET

tree = ET.parse('docs/stories/story-map-increments.drawio')
root = tree.getroot()

# Get epics
epics = {}
for cell in root.findall('.//mxCell'):
    cid = cell.get('id', '')
    geom = cell.find('mxGeometry')
    if geom is not None and cid.startswith('epic') and cid != 'epic-group':
        try:
            epic_idx = int(cid[4:]) if len(cid) > 4 else 1
            x = float(geom.get('x', 0))
            w = float(geom.get('width', 0))
            epics[epic_idx] = (cid, x, w, x + w)
        except (ValueError, IndexError):
            pass

# Get features
features = {}
for cell in root.findall('.//mxCell'):
    cid = cell.get('id', '')
    geom = cell.find('mxGeometry')
    if geom is not None and cid.startswith('e') and 'f' in cid and 's' not in cid and len(cid) <= 4:
        parts = cid[1:].split('f')
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            epic_idx = int(parts[0])
            feat_idx = int(parts[1])
            x = float(geom.get('x', 0))
            w = float(geom.get('width', 0))
            if epic_idx not in features:
                features[epic_idx] = []
            features[epic_idx].append((cid, x, w, x + w))

print("EPIC POSITION VERIFICATION:")
print("=" * 80)

all_ok = True
for epic_idx in sorted(epics.keys()):
    epic_id, epic_x, epic_w, epic_right = epics[epic_idx]
    print(f"\nEpic {epic_idx} ({epic_id}):")
    print(f"  Position: x={epic_x:.1f}, width={epic_w:.1f}, right={epic_right:.1f}")
    
    if epic_idx in features:
        feat_list = sorted(features[epic_idx], key=lambda x: x[1])
        if feat_list:
            first_feat_x = feat_list[0][1]
            last_feat_right = max(f[3] for f in feat_list)
            
            print(f"  Features: {len(feat_list)}")
            print(f"  First feature: x={first_feat_x:.1f}")
            print(f"  Last feature ends: {last_feat_right:.1f}")
            
            # Epic should start at or before first feature
            if epic_x > first_feat_x + 5:
                print(f"  ❌ ISSUE: Epic starts at {epic_x:.1f} but first feature starts at {first_feat_x:.1f}")
                all_ok = False
            else:
                print(f"  ✓ Epic starts before/at first feature")
            
            # Epic should end at or after last feature
            if epic_right < last_feat_right - 5:
                print(f"  ❌ ISSUE: Epic ends at {epic_right:.1f} but last feature ends at {last_feat_right:.1f}")
                all_ok = False
            else:
                print(f"  ✓ Epic ends after/at last feature")

print("\n" + "=" * 80)
if all_ok:
    print("[OK] All epics properly positioned to cover their features!")
else:
    print("[ISSUES FOUND] See above for details.")

