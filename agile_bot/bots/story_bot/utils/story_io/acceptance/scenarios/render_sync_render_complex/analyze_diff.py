#!/usr/bin/env python3
"""Analyze differences between actual and expected DrawIO files"""
import xml.etree.ElementTree as ET
from pathlib import Path

actual_path = Path("3_then/actual-rendered-story-map-outline.drawio")
expected_path = Path("3_then/expected-rendered-story-map-outline.drawio")

def get_cells(filepath):
    tree = ET.parse(filepath)
    cells = {}
    for cell in tree.findall('.//mxCell'):
        cell_id = cell.get('id', '')
        if cell_id:
            geom = cell.find('mxGeometry')
            if geom is not None:
                cells[cell_id] = {
                    'id': cell_id,
                    'value': cell.get('value', ''),
                    'x': float(geom.get('x', 0)),
                    'y': float(geom.get('y', 0)),
                    'width': float(geom.get('width', 0)),
                    'height': float(geom.get('height', 0))
                }
    return cells

actual_cells = get_cells(actual_path)
expected_cells = get_cells(expected_path)

print("=" * 80)
print("EPIC ANALYSIS")
print("=" * 80)

actual_epics = {k: v for k, v in actual_cells.items() if 'epic' in k.lower() and k not in ['epic-group', '0', '1']}
expected_epics = {k: v for k, v in expected_cells.items() if 'epic' in k.lower() and k not in ['epic-group', '0', '1']}

print(f"\nActual Epics: {len(actual_epics)}")
for epic_id, epic in sorted(actual_epics.items()):
    print(f"  {epic_id}: x={epic['x']:.0f}, width={epic['width']:.0f}, name={epic['value'][:50]}")

print(f"\nExpected Epics: {len(expected_epics)}")
for epic_id, epic in sorted(expected_epics.items()):
    print(f"  {epic_id}: x={epic['x']:.0f}, width={epic['width']:.0f}, name={epic['value'][:50]}")

print("\n" + "=" * 80)
print("STORY COUNT ANALYSIS")
print("=" * 80)

actual_stories = {k: v for k, v in actual_cells.items() if k.startswith('e') and 's' in k and 'ac_' not in k and k.count('s') >= 1}
expected_stories = {k: v for k, v in expected_cells.items() if k.startswith('e') and 's' in k and 'ac_' not in k and k.count('s') >= 1}

print(f"\nActual Stories: {len(actual_stories)}")
print(f"Expected Stories: {len(expected_stories)}")
print(f"Missing: {len(expected_stories) - len(actual_stories)}")

# Group by epic/feature
def get_epic_feat(story_id):
    parts = story_id.split('s')
    if len(parts) >= 2:
        return parts[0]  # e1f1, e2f1, etc.
    return None

actual_by_epic = {}
for story_id, story in actual_stories.items():
    key = get_epic_feat(story_id)
    if key:
        actual_by_epic.setdefault(key, []).append(story_id)

expected_by_epic = {}
for story_id, story in expected_stories.items():
    key = get_epic_feat(story_id)
    if key:
        expected_by_epic.setdefault(key, []).append(story_id)

print("\nStories by Epic/Feature:")
for key in sorted(set(list(actual_by_epic.keys()) + list(expected_by_epic.keys()))):
    actual_count = len(actual_by_epic.get(key, []))
    expected_count = len(expected_by_epic.get(key, []))
    if actual_count != expected_count:
        print(f"  {key}: Actual={actual_count}, Expected={expected_count} [MISMATCH]")
    else:
        print(f"  {key}: {actual_count} stories")

print("\n" + "=" * 80)
print("NESTED STORIES")
print("=" * 80)

actual_nested = {k: v for k, v in actual_stories.items() if '_n' in k}
expected_nested = {k: v for k, v in expected_stories.items() if '_n' in k}

print(f"\nActual Nested Stories: {len(actual_nested)}")
print(f"Expected Nested Stories: {len(expected_nested)}")

if actual_nested:
    print("\nActual nested stories:")
    for story_id in sorted(actual_nested.keys())[:10]:
        print(f"  {story_id}: {actual_cells[story_id]['value'][:60]}")

if expected_nested:
    print("\nExpected nested stories:")
    for story_id in sorted(expected_nested.keys())[:10]:
        print(f"  {story_id}: {expected_cells[story_id]['value'][:60]}")

