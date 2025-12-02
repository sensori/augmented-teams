#!/usr/bin/env python3
"""Test if nested stories are in the JSON"""
import json
from pathlib import Path

json_path = Path("1_given/new-format-story-graph.json")
sg = json.load(open(json_path))

print("=" * 80)
print("CHECKING NESTED STORIES IN JSON")
print("=" * 80)

for epic_idx, epic in enumerate(sg.get('epics', []), 1):
    print(f"\nEpic {epic_idx}: {epic['name']}")
    for feat_idx, feat in enumerate(epic.get('sub_epics', []), 1):
        print(f"  Feature {feat_idx}: {feat['name']}")
        for story_idx, story in enumerate(feat.get('stories', []), 1):
            nested = story.get('stories', [])
            if nested:
                print(f"    Story {story_idx}: {story['name']} - HAS {len(nested)} NESTED STORIES")
                for n_idx, n_story in enumerate(nested, 1):
                    print(f"      Nested {n_idx}: {n_story['name']}")
            else:
                print(f"    Story {story_idx}: {story['name']} - no nested stories")

