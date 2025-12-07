import json
import ast
from pathlib import Path

# Load story graph
story_graph_path = Path('agile_bot/bots/base_bot/docs/stories/story-graph.json')
with open(story_graph_path, 'r', encoding='utf-8') as f:
    story_graph = json.load(f)

# Extract test file mappings
test_file_to_sub_epic = {}
for epic in story_graph.get('epics', []):
    epic_name = epic.get('name', '')
    for sub_epic in epic.get('sub_epics', []):
        sub_epic_name = sub_epic.get('name', '')
        test_file = sub_epic.get('test_file', '')
        if test_file:
            test_file_to_sub_epic[test_file] = (epic_name, sub_epic_name)
        
        # Also check stories
        for story_group in sub_epic.get('story_groups', []):
            for story in story_group.get('stories', []):
                story_test_file = story.get('test_file', '')
                if story_test_file:
                    test_file_to_sub_epic[story_test_file] = (epic_name, sub_epic_name)

# Get all test files
test_dir = Path('agile_bot/bots/base_bot/test')
test_files = sorted(test_dir.glob('test_*.py'))

print("MISMATCHES FOUND:\n")
print("=" * 80)

# Check each test file
for test_file in test_files:
    test_file_name = test_file.name
    mapping = test_file_to_sub_epic.get(test_file_name)
    
    if not mapping:
        print(f"\nTest File: {test_file_name}")
        print(f"  Epic: NOT FOUND")
        print(f"  Sub-Epic: NOT FOUND")
        
        # Parse test file to get classes
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                    print(f"  Test Class: {node.name} -> Story: NOT FOUND")
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                            print(f"    Test Method: {item.name} -> Scenario: NOT FOUND")
        except:
            pass

print("\n" + "=" * 80)
