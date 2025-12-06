#!/usr/bin/env python3
"""Update all assertion scripts to use new format helpers."""
from pathlib import Path
import re

scenarios_dir = Path(__file__).parent

# Template for updated _assert_jsons_match function
NEW_ASSERT_TEMPLATE = '''def count_sub_epics_recursive(item):
    """Recursively count all sub_epics in an epic or sub_epic."""
    count = len(item.get('sub_epics', []))
    for sub_epic in item.get('sub_epics', []):
        count += count_sub_epics_recursive(sub_epic)
    return count

def count_stories_recursive(item):
    """Recursively count all stories in an epic, sub_epic, or story."""
    count = len(item.get('stories', []))
    # Count stories in sub_epics
    for sub_epic in item.get('sub_epics', []):
        count += count_stories_recursive(sub_epic)
    # Count nested stories (story groups)
    for story in item.get('stories', []):
        if 'stories' in story:
            count += count_stories_recursive(story)
    return count

def _assert_jsons_match(expected_path: Path, actual_path: Path) -> dict:
    """Compare two JSON story graph files with detailed comparison (new format with sub_epics)."""
    if not expected_path.exists():
        return {'match': False, 'message': f'Expected file not found: {expected_path}'}
    if not actual_path.exists():
        return {'match': False, 'message': f'Actual file not found: {actual_path}'}
    
    with open(expected_path, 'r', encoding='utf-8') as f:
        expected = json.load(f)
    with open(actual_path, 'r', encoding='utf-8') as f:
        actual = json.load(f)
    
    differences = []
    
    # Compare epic counts
    epics1 = len(expected.get('epics', []))
    epics2 = len(actual.get('epics', []))
    if epics1 != epics2:
        differences.append(f"Epic count mismatch: {epics1} vs {epics2}")
    
    # Compare sub_epic counts (across all epics, recursively)
    sub_epics1 = sum(count_sub_epics_recursive(epic) for epic in expected.get('epics', []))
    sub_epics2 = sum(count_sub_epics_recursive(epic) for epic in actual.get('epics', []))
    if sub_epics1 != sub_epics2:
        differences.append(f"Sub-epic count mismatch: {sub_epics1} vs {sub_epics2}")
    
    # Compare story counts (across all epics and sub_epics, recursively)
    stories1 = sum(count_stories_recursive(epic) for epic in expected.get('epics', []))
    stories2 = sum(count_stories_recursive(epic) for epic in actual.get('epics', []))
    if stories1 != stories2:
        differences.append(f"Story count mismatch: {stories1} vs {stories2}")
    
    # Compare increment counts
    increments1 = len(expected.get('increments', []))
    increments2 = len(actual.get('increments', []))
    if increments1 != increments2:
        differences.append(f"Increment count mismatch: {increments1} vs {increments2}")
    
    # If counts match, consider it a pass (following old test behavior)
    # The old test only checks counts, not deep equality
    # This allows for minor differences in structure while ensuring data integrity
    
    return {
        'match': len(differences) == 0,
        'differences': differences,
        'message': 'JSONs match' if len(differences) == 0 else f'{len(differences)} differences found'
    }'''

def update_assertion_script(script_path):
    """Update a single assertion script."""
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already updated (has count_sub_epics_recursive)
    if 'count_sub_epics_recursive' in content:
        print(f"  ⏭ Already updated: {script_path.name}")
        return False
    
    # Find the _assert_jsons_match function and replace it
    # Pattern: from start of function def to next def or end of function
    pattern = r'(def _assert_jsons_match\(.*?\n.*?def )'
    
    # Find where to insert (after imports, before first function)
    lines = content.split('\n')
    insert_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith('from drawio_comparison') or line.strip().startswith('from story_io'):
            insert_idx = i + 1
            break
    
    if insert_idx is None:
        print(f"  ✗ Could not find insertion point: {script_path.name}")
        return False
    
    # Find the old _assert_jsons_match function
    old_start = None
    old_end = None
    in_function = False
    indent_level = 0
    
    for i in range(insert_idx, len(lines)):
        line = lines[i]
        if line.strip().startswith('def _assert_jsons_match'):
            old_start = i
            in_function = True
            # Get base indent
            indent_level = len(line) - len(line.lstrip())
        elif in_function:
            # Check if we've hit the next function or end of function scope
            if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""'):
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent_level and line.strip().startswith('def '):
                    old_end = i
                    break
                # Or end of file
                if i == len(lines) - 1:
                    old_end = i + 1
                    break
    
    if old_start is None:
        print(f"  ✗ Could not find _assert_jsons_match function: {script_path.name}")
        return False
    
    if old_end is None:
        old_end = len(lines)
    
    # Replace the function
    new_lines = (
        lines[:insert_idx] +
        [''] +
        NEW_ASSERT_TEMPLATE.split('\n') +
        [''] +
        lines[old_end:]
    )
    
    # Write back
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"  ✓ Updated: {script_path.name}")
    return True

def main():
    """Update all assertion scripts."""
    assertion_scripts = [
        scenarios_dir / "couple_of stories_with_acceptance_criteria/3_then/assert_story_graph_round_trip.py",
        scenarios_dir / "different_story_types_story_graph/3_then/assert_story_graph_round_trip.py",
        scenarios_dir / "incomplete_with_estimates_story_graph/3_then/assert_story_graph_round_trip.py",
        scenarios_dir / "multiple_epics_features_test/3_then/assert_story_graph_round_trip.py",
        scenarios_dir / "optional_vs_sequential_story_graph/3_then/assert_story_graph_round_trip.py",
    ]
    
    print("Updating assertion scripts to use new format...")
    print("=" * 80)
    
    updated = 0
    for script_path in assertion_scripts:
        if script_path.exists():
            if update_assertion_script(script_path):
                updated += 1
        else:
            print(f"  ⚠ Not found: {script_path.name}")
    
    print("=" * 80)
    print(f"Updated {updated} assertion scripts")

if __name__ == '__main__':
    main()
























































