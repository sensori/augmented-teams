"""
THEN: Assert extracted JSON matches expected JSON.

Compares the extracted story graph JSON with the expected JSON.
"""
import sys
import io
from pathlib import Path
import json

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Add parent directories to path
then_dir = Path(__file__).parent
test_dir = then_dir.parent
scenario_dir = test_dir.parent
acceptance_dir = scenario_dir.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(acceptance_dir / "spec_by_example"))
sys.path.insert(0, str(scenario_dir))

def count_stories_recursive(item):
    """Recursively count all stories in an epic or sub_epic."""
    count = 0
    # Count stories in story_groups (new structure)
    for story_group in item.get('story_groups', []):
        count += len(story_group.get('stories', []))
    # Count stories directly under item (legacy structure)
    count += len(item.get('stories', []))
    # Count stories in sub_epics
    for sub_epic in item.get('sub_epics', []):
        count += count_stories_recursive(sub_epic)
    return count

def assert_extracted_matches_expected():
    """Compare extracted JSON with expected JSON."""
    print("="*80)
    print("THEN: Assert extracted JSON matches expected JSON")
    print("="*80)
    
    # Get files
    expected_json_path = then_dir / "expected-story-graph.json"
    extracted_json_path = then_dir / "actual-extracted-story-graph.json"
    
    if not expected_json_path.exists():
        print(f"[ERROR] Expected JSON not found: {expected_json_path}")
        return False
    
    if not extracted_json_path.exists():
        print(f"[ERROR] Extracted JSON not found: {extracted_json_path}")
        return False
    
    # Load JSONs
    with open(expected_json_path, 'r', encoding='utf-8') as f:
        expected = json.load(f)
    
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        extracted = json.load(f)
    
    print(f"\nExpected JSON: {expected_json_path}")
    print(f"Extracted JSON: {extracted_json_path}")
    
    # Compare
    differences = []
    
    # Compare epic counts
    expected_epics = len(expected.get('epics', []))
    extracted_epics = len(extracted.get('epics', []))
    if expected_epics != extracted_epics:
        differences.append(f"Epic count mismatch: {expected_epics} vs {extracted_epics}")
    
    # Compare story counts recursively
    expected_stories = sum(count_stories_recursive(epic) for epic in expected.get('epics', []))
    extracted_stories = sum(count_stories_recursive(epic) for epic in extracted.get('epics', []))
    if expected_stories != extracted_stories:
        differences.append(f"Story count mismatch: {expected_stories} vs {extracted_stories}")
    
    # Detailed comparison for "Generate Bot Server And Tools" feature
    print("\n=== DETAILED COMPARISON ===")
    for epic in extracted.get('epics', []):
        if epic['name'] == 'Build Agile Bots':
            for sub_epic in epic.get('sub_epics', []):
                if sub_epic['name'] == 'Generate Bot Server And Tools':
                    print(f"\nFound feature: {sub_epic['name']}")
                    story_groups = sub_epic.get('story_groups', [])
                    print(f"  Story groups count: {len(story_groups)}")
                    
                    for group_idx, group in enumerate(story_groups, 1):
                        print(f"\n  Story Group {group_idx}:")
                        print(f"    type: {group.get('type')}")
                        print(f"    connector: {group.get('connector')}")
                        print(f"    stories count: {len(group.get('stories', []))}")
                        
                        for story_idx, story in enumerate(group.get('stories', []), 1):
                            print(f"      Story {story_idx}: {story['name']}")
                            print(f"        sequential_order: {story.get('sequential_order')}")
                            print(f"        connector: {story.get('connector')}")
    
    # Compare with expected
    print("\n=== EXPECTED STRUCTURE ===")
    for epic in expected.get('epics', []):
        if epic['name'] == 'Build Agile Bots':
            for sub_epic in epic.get('sub_epics', []):
                if sub_epic['name'] == 'Generate Bot Server And Tools':
                    print(f"\nExpected feature: {sub_epic['name']}")
                    story_groups = sub_epic.get('story_groups', [])
                    print(f"  Expected story groups count: {len(story_groups)}")
                    
                    for group_idx, group in enumerate(story_groups, 1):
                        print(f"\n  Expected Story Group {group_idx}:")
                        print(f"    type: {group.get('type')}")
                        print(f"    connector: {group.get('connector')}")
                        print(f"    stories count: {len(group.get('stories', []))}")
                        
                        for story_idx, story in enumerate(group.get('stories', []), 1):
                            print(f"      Expected Story {story_idx}: {story['name']}")
                            print(f"        sequential_order: {story.get('sequential_order')}")
                            print(f"        connector: {story.get('connector')}")
    
    # Report results
    print("\n" + "="*80)
    if differences:
        print("[FAIL] Differences found:")
        for diff in differences:
            print(f"  - {diff}")
        return False
    else:
        print("[OK] Extracted JSON matches expected JSON!")
        return True

if __name__ == "__main__":
    success = assert_extracted_matches_expected()
    sys.exit(0 if success else 1)

