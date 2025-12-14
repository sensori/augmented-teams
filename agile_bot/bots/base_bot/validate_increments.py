#!/usr/bin/env python3
"""
Validate that all stories in increments section come from epics section.
Check for orphaned stories and ensure renderer updates increments file.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Set

def collect_all_story_names_from_epics(epics: List[Dict[str, Any]]) -> Set[str]:
    """Collect all story names from epics section."""
    story_names = set()
    
    def traverse_epic(epic: Dict[str, Any]):
        # Check direct stories on epic
        for story in epic.get('stories', []):
            if 'name' in story:
                story_names.add(story['name'])
        
        # Check sub_epics
        for sub_epic in epic.get('sub_epics', []):
            # Check direct stories on sub_epic
            for story in sub_epic.get('stories', []):
                if 'name' in story:
                    story_names.add(story['name'])
            
            # Check story_groups
            for story_group in sub_epic.get('story_groups', []):
                for story in story_group.get('stories', []):
                    if 'name' in story:
                        story_names.add(story['name'])
            
            # Recursively check nested sub_epics
            if 'sub_epics' in sub_epic:
                traverse_sub_epic(sub_epic)
    
    def traverse_sub_epic(sub_epic: Dict[str, Any]):
        # Check direct stories
        for story in sub_epic.get('stories', []):
            if 'name' in story:
                story_names.add(story['name'])
        
        # Check story_groups
        for story_group in sub_epic.get('story_groups', []):
            for story in story_group.get('stories', []):
                if 'name' in story:
                    story_names.add(story['name'])
        
        # Check nested sub_epics
        for nested_sub_epic in sub_epic.get('sub_epics', []):
            traverse_sub_epic(nested_sub_epic)
    
    for epic in epics:
        traverse_epic(epic)
    
    return story_names

def collect_all_story_names_from_increments(increments: List[Dict[str, Any]]) -> Set[str]:
    """Collect all story names from increments section."""
    story_names = set()
    
    def traverse_epic(epic: Dict[str, Any]):
        # Check direct stories on epic
        for story in epic.get('stories', []):
            if 'name' in story:
                story_names.add(story['name'])
        
        # Check sub_epics
        for sub_epic in epic.get('sub_epics', []):
            # Check direct stories on sub_epic
            for story in sub_epic.get('stories', []):
                if 'name' in story:
                    story_names.add(story['name'])
            
            # Check story_groups
            for story_group in sub_epic.get('story_groups', []):
                for story in story_group.get('stories', []):
                    if 'name' in story:
                        story_names.add(story['name'])
            
            # Recursively check nested sub_epics
            if 'sub_epics' in sub_epic:
                traverse_sub_epic(sub_epic)
    
    def traverse_sub_epic(sub_epic: Dict[str, Any]):
        # Check direct stories
        for story in sub_epic.get('stories', []):
            if 'name' in story:
                story_names.add(story['name'])
        
        # Check story_groups
        for story_group in sub_epic.get('story_groups', []):
            for story in story_group.get('stories', []):
                if 'name' in story:
                    story_names.add(story['name'])
        
        # Check nested sub_epics
        for nested_sub_epic in sub_epic.get('sub_epics', []):
            traverse_sub_epic(nested_sub_epic)
    
    for increment in increments:
        for epic in increment.get('epics', []):
            traverse_epic(epic)
    
    return story_names

def validate_increments(story_graph_path: Path):
    """Validate increments section against epics section."""
    print(f"Loading {story_graph_path}...")
    with open(story_graph_path, 'r', encoding='utf-8') as f:
        story_graph = json.load(f)
    
    epics = story_graph.get('epics', [])
    increments = story_graph.get('increments', [])
    
    print(f"\nEpics count: {len(epics)}")
    print(f"Increments count: {len(increments)}")
    
    # Collect all story names from epics
    epic_story_names = collect_all_story_names_from_epics(epics)
    print(f"\nTotal unique stories in epics: {len(epic_story_names)}")
    
    # Collect all story names from increments
    increment_story_names = collect_all_story_names_from_increments(increments)
    print(f"Total unique stories in increments: {len(increment_story_names)}")
    
    # Find orphaned stories (stories in increments but not in epics)
    orphaned_stories = increment_story_names - epic_story_names
    
    if orphaned_stories:
        print(f"\n[ERROR] FOUND {len(orphaned_stories)} ORPHANED STORIES in increments:")
        for story_name in sorted(orphaned_stories):
            print(f"  - {story_name}")
    else:
        print("\n[OK] No orphaned stories found - all increment stories exist in epics")
    
    # Find missing stories (stories in epics but not in increments)
    if increments:
        missing_stories = epic_story_names - increment_story_names
        if missing_stories:
            print(f"\n[WARN] Found {len(missing_stories)} stories in epics but not in increments:")
            # Show first 10
            for story_name in sorted(list(missing_stories))[:10]:
                print(f"  - {story_name}")
            if len(missing_stories) > 10:
                print(f"  ... and {len(missing_stories) - 10} more")
    else:
        print("\n[WARN] Increments array is empty - no stories assigned to increments")
    
    # Check for code scanner related stories
    code_scanner_stories = [s for s in epic_story_names if 'scanner' in s.lower() or 'code scanner' in s.lower()]
    if code_scanner_stories:
        print(f"\n[INFO] Code Scanner related stories in epics ({len(code_scanner_stories)}):")
        for story_name in sorted(code_scanner_stories):
            print(f"  - {story_name}")
    
    if increments:
        code_scanner_in_increments = [s for s in increment_story_names if 'scanner' in s.lower() or 'code scanner' in s.lower()]
        if code_scanner_in_increments:
            print(f"\n[INFO] Code Scanner related stories in increments ({len(code_scanner_in_increments)}):")
            for story_name in sorted(code_scanner_in_increments):
                print(f"  - {story_name}")
    
    return len(orphaned_stories) == 0

if __name__ == "__main__":
    workspace_root = Path(__file__).parent
    story_graph_path = workspace_root / 'docs' / 'stories' / 'story-graph.json'
    
    if not story_graph_path.exists():
        print(f"Error: story-graph.json not found at {story_graph_path}")
        exit(1)
    
    is_valid = validate_increments(story_graph_path)
    exit(0 if is_valid else 1)

