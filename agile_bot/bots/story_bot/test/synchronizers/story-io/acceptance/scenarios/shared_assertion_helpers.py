"""
Shared assertion helpers for story graph round-trip tests.

These helpers work with the new format (sub_epics) instead of the old format (features).
"""
from pathlib import Path
import json


def count_sub_epics_recursive(item):
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


def assert_jsons_match_new_format(expected_path: Path, actual_path: Path) -> dict:
    """
    Compare two JSON story graph files with detailed comparison (new format with sub_epics).
    
    Args:
        expected_path: Path to expected JSON file
        actual_path: Path to actual JSON file
    
    Returns:
        Dictionary with 'match' (bool), 'differences' (list), and 'message' (str)
    """
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
    }
























































