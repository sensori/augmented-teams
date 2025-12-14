# analyze_story_duplicates_and_tests.py
import json
from collections import Counter
from pathlib import Path
import re

# Load story graph
story_graph_path = Path('agile_bot/bots/base_bot/docs/stories/story-graph.json')
data = json.loads(story_graph_path.read_text(encoding='utf-8'))

# Collect all stories from epics section
epic_stories = []
for epic in data['epics']:
    for sub_epic in epic.get('sub_epics', []):
        for group in sub_epic.get('story_groups', []):
            for story in group.get('stories', []):
                epic_stories.append({
                    'name': story['name'],
                    'epic': epic['name'],
                    'sub_epic': sub_epic['name'],
                    'path': f"{epic['name']}|{sub_epic['name']}|{story['name']}"
                })

# Collect all stories from increments section
increment_stories = []
for inc in data['increments']:
    for story in inc.get('stories', []):
        increment_stories.append({
            'name': story['name'],
            'increment': inc['name'],
            'priority': inc.get('priority', 0)
        })

# Find duplicates in epics section
epic_story_names = [s['name'] for s in epic_stories]
epic_duplicates = {name: count for name, count in Counter(epic_story_names).items() if count > 1}

# Find duplicates in increments section
inc_story_names = [s['name'] for s in increment_stories]
inc_duplicates = {name: count for name, count in Counter(inc_story_names).items() if count > 1}

# Find stories that appear in both epics and increments but with different names (potential mismatches)
epic_story_set = set(epic_story_names)
inc_story_set = set(inc_story_names)

# Find test classes
test_dir = Path('agile_bot/bots/base_bot/test')
test_classes = {}
for test_file in test_dir.glob('test_*.py'):
    content = test_file.read_text(encoding='utf-8')
    # Find all test class definitions
    class_matches = re.findall(r'class\s+(Test\w+):', content)
    for class_name in class_matches:
        test_classes[class_name] = test_file.name

# Map test class names to story names (approximate matching)
test_to_story_mappings = {}
story_to_test_mappings = {}

# Common patterns
test_patterns = [
    (r'TestTrackActivityFor(\w+)Action', lambda m: f"Track Activity for {m.group(1)} Action"),
    (r'TestProceedTo(\w+)', lambda m: f"Proceed To {m.group(1)}"),
    (r'TestInject(\w+)', lambda m: f"Inject {m.group(1)}"),
    (r'TestLoad(\w+)', lambda m: f"Load {m.group(1)}"),
    (r'Test(\w+)', lambda m: m.group(1).replace('_', ' ')),
]

for test_class, test_file in test_classes.items():
    matched_story = None
    for pattern, transform in test_patterns:
        match = re.match(pattern, test_class)
        if match:
            try:
                potential_story = transform(match)
                # Try to find exact or close match
                for story_name in epic_story_set:
                    if potential_story.lower() == story_name.lower():
                        matched_story = story_name
                        break
                    # Also try partial matches
                    if potential_story.lower() in story_name.lower() or story_name.lower() in potential_story.lower():
                        if not matched_story or len(matched_story) < len(story_name):
                            matched_story = story_name
            except:
                pass
            break
    
    if matched_story:
        test_to_story_mappings[test_class] = matched_story
        if matched_story not in story_to_test_mappings:
            story_to_test_mappings[matched_story] = []
        story_to_test_mappings[matched_story].append(test_class)

# Manual mappings for known test classes
manual_mappings = {
    'TestInvokeBotTool': 'Invoke Bot Tool',
    'TestLoadAndMergeBehaviorActionInstructions': 'Load And Merge Behavior Action Instructions',
    'TestForwardToCurrentBehaviorAndCurrentAction': 'Forward To Current Behavior and Current Action',
    'TestForwardToCurrentAction': 'Forward To Current Action',
    'TestCloseCurrentAction': 'Close Current Action',
    'TestInvokeBehaviorActionsInWorkflowOrder': 'Complete Workflow Integration',
    'TestInjectKnowledgeGraphTemplateForBuildKnowledge': 'Inject Knowledge Graph Template and Builder Instructions',
    'TestInjectRenderInstructionsAndConfigs': 'Load Render Configurations',  # Approximate
    'TestInjectPlanningCriteriaIntoInstructions': 'Inject Planning Criteria Into Instructions',
    'TestInjectGuardrailsAsPartOfClarifyRequirements': 'Gather Context Action Guardrails',  # Approximate
    'TestFindBehaviorFolder': 'Find Behavior Folder',
    'TestBootstrapWorkspace': 'Initialize Project Location',  # Approximate
    'TestDetectTriggerWordsThroughExtension': 'Detect Trigger Words Through Extension',
    'TestTrackActivityForGatherContextAction': 'Track Activity for Gather Context Action',
    'TestTrackActivityForBuildKnowledgeAction': 'Track Activity for Build Knowledge Action',
    'TestTrackActivityForRenderOutputAction': 'Track Activity for Render Output Action',
    'TestTrackActivityForValidateRulesAction': 'Track Activity for Validate Rules Action',
    'TestProceedToDecidePlanning': 'Proceed To Decide Planning',
    'TestProceedToBuildKnowledge': 'Proceed To Build Knowledge',
    'TestProceedToRenderOutput': 'Proceed To Render Output',
    'TestProceedToValidateRules': 'Proceed To Validate Rules',
}

for test_class, story_name in manual_mappings.items():
    if test_class in test_classes and story_name in epic_story_set:
        test_to_story_mappings[test_class] = story_name
        if story_name not in story_to_test_mappings:
            story_to_test_mappings[story_name] = []
        story_to_test_mappings[story_name].append(test_class)

# Print results
print("=" * 80)
print("STORY GRAPH DUPLICATE ANALYSIS")
print("=" * 80)

print(f"\nTotal stories in epics section: {len(epic_stories)}")
print(f"Unique story names in epics: {len(set(epic_story_names))}")
print(f"Duplicate story names in epics: {len(epic_duplicates)}")

if epic_duplicates:
    print("\n[WARNING] DUPLICATE STORIES IN EPICS SECTION:")
    for name, count in sorted(epic_duplicates.items()):
        print(f"  '{name}': appears {count} times")
        # Show all locations
        for story in epic_stories:
            if story['name'] == name:
                print(f"    - {story['path']}")
else:
    print("\n[OK] No duplicates found in epics section")

print(f"\nTotal stories in increments section: {len(increment_stories)}")
print(f"Unique story names in increments: {len(set(inc_story_names))}")
print(f"Duplicate story names in increments: {len(inc_duplicates)}")

if inc_duplicates:
    print("\n[WARNING] DUPLICATE STORIES IN INCREMENTS SECTION:")
    for name, count in sorted(inc_duplicates.items()):
        print(f"  '{name}': appears {count} times")
        # Show all locations
        for story in increment_stories:
            if story['name'] == name:
                print(f"    - Increment '{story['increment']}' (Priority {story['priority']})")
else:
    print("\n[OK] No duplicates found in increments section")

# Stories in increments but not in epics
orphaned_in_increments = inc_story_set - epic_story_set
if orphaned_in_increments:
    print(f"\n[WARNING] STORIES IN INCREMENTS BUT NOT IN EPICS ({len(orphaned_in_increments)}):")
    for story_name in sorted(orphaned_in_increments):
        print(f"  - '{story_name}'")
        for story in increment_stories:
            if story['name'] == story_name:
                print(f"    Found in increment: '{story['increment']}'")
else:
    print("\n[OK] All stories in increments exist in epics section")

# Stories in epics but not in increments
orphaned_in_epics = epic_story_set - inc_story_set
if orphaned_in_epics:
    print(f"\n📋 STORIES IN EPICS BUT NOT IN INCREMENTS ({len(orphaned_in_epics)}):")
    for story_name in sorted(orphaned_in_epics):
        print(f"  - '{story_name}'")
        for story in epic_stories:
            if story['name'] == story_name:
                print(f"    Found in: {story['path']}")

print("\n" + "=" * 80)
print("TEST CLASS MAPPINGS")
print("=" * 80)

print(f"\nTotal test classes found: {len(test_classes)}")
print(f"Test classes mapped to stories: {len(test_to_story_mappings)}")

if test_to_story_mappings:
    print("\n[OK] TEST CLASS -> STORY MAPPINGS:")
    for test_class, story_name in sorted(test_to_story_mappings.items()):
        print(f"  {test_class} ({test_classes[test_class]}) -> '{story_name}'")

# Stories with multiple test classes
multi_test_stories = {name: tests for name, tests in story_to_test_mappings.items() if len(tests) > 1}
if multi_test_stories:
    print("\n[WARNING] STORIES WITH MULTIPLE TEST CLASSES:")
    for story_name, tests in sorted(multi_test_stories.items()):
        print(f"  '{story_name}':")
        for test_class in tests:
            print(f"    - {test_class} ({test_classes[test_class]})")

# Workflow increment stories with/without tests
workflow_stories = [s['name'] for s in increment_stories if s['increment'] == 'Workflow']
workflow_with_tests = [s for s in workflow_stories if s in story_to_test_mappings]
workflow_without_tests = [s for s in workflow_stories if s not in story_to_test_mappings]

print("\n" + "=" * 80)
print("WORKFLOW INCREMENT TEST COVERAGE")
print("=" * 80)
print(f"\nTotal Workflow stories: {len(workflow_stories)}")
print(f"Stories WITH test classes: {len(workflow_with_tests)}")
print(f"Stories WITHOUT test classes: {len(workflow_without_tests)}")

if workflow_with_tests:
    print("\n[OK] WORKFLOW STORIES WITH TEST CLASSES:")
    for story_name in sorted(workflow_with_tests):
        tests = story_to_test_mappings.get(story_name, [])
        print(f"  - '{story_name}'")
        for test_class in tests:
            print(f"      -> {test_class} ({test_classes[test_class]})")

if workflow_without_tests:
    print("\n[ERROR] WORKFLOW STORIES WITHOUT TEST CLASSES:")
    for story_name in sorted(workflow_without_tests):
        print(f"  - '{story_name}'")

