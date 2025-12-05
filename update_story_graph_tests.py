#!/usr/bin/env python3
"""Update story-graph.json with test fields based on story-graph-tests.json template."""

import json
import sys

def add_test_fields_to_story_graph(file_path):
    """Add test_file, test_class, test_method, and test_cases to story-graph.json"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stats = {
        'test_file_added': 0,
        'test_class_added': 0,
        'test_method_added': 0,
        'test_cases_added': 0
    }
    
    def process_sub_epic(sub_epic):
        """Recursively process sub_epics and add test_file to lowest level ones"""
        # Check if this is a lowest-level sub_epic (has empty sub_epics array)
        if not sub_epic.get('sub_epics') or len(sub_epic.get('sub_epics', [])) == 0:
            # Add test_file if not present
            if 'test_file' not in sub_epic:
                sub_epic['test_file'] = ""
                stats['test_file_added'] += 1
        
        # Process nested sub_epics
        for nested_se in sub_epic.get('sub_epics', []):
            process_sub_epic(nested_se)
        
        # Process stories in story_groups
        for story_group in sub_epic.get('story_groups', []):
            for story in story_group.get('stories', []):
                # Add test_class to story if not present
                if 'test_class' not in story:
                    story['test_class'] = ""
                    stats['test_class_added'] += 1
                
                # Add test_method to scenarios
                for scenario in story.get('scenarios', []):
                    if 'test_method' not in scenario:
                        scenario['test_method'] = ""
                        stats['test_method_added'] += 1
                
                # Add test_method to scenario_outlines
                for scenario_outline in story.get('scenario_outlines', []):
                    if 'test_method' not in scenario_outline:
                        scenario_outline['test_method'] = ""
                        stats['test_method_added'] += 1
                
                # Add test_cases array if story doesn't have scenarios or scenario_outlines
                if 'test_cases' not in story and 'scenarios' not in story and 'scenario_outlines' not in story:
                    story['test_cases'] = []
                    stats['test_cases_added'] += 1
    
    # Process all epics
    for epic in data.get('epics', []):
        # Process sub_epics
        for sub_epic in epic.get('sub_epics', []):
            process_sub_epic(sub_epic)
        
        # Process story_groups at epic level
        for story_group in epic.get('story_groups', []):
            for story in story_group.get('stories', []):
                if 'test_class' not in story:
                    story['test_class'] = ""
                    stats['test_class_added'] += 1
                for scenario in story.get('scenarios', []):
                    if 'test_method' not in scenario:
                        scenario['test_method'] = ""
                        stats['test_method_added'] += 1
                for scenario_outline in story.get('scenario_outlines', []):
                    if 'test_method' not in scenario_outline:
                        scenario_outline['test_method'] = ""
                        stats['test_method_added'] += 1
                if 'test_cases' not in story and 'scenarios' not in story and 'scenario_outlines' not in story:
                    story['test_cases'] = []
                    stats['test_cases_added'] += 1
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully updated {file_path} with test fields")
    print(f"  - test_file fields added: {stats['test_file_added']}")
    print(f"  - test_class fields added: {stats['test_class_added']}")
    print(f"  - test_method fields added: {stats['test_method_added']}")
    print(f"  - test_cases arrays added: {stats['test_cases_added']}")

if __name__ == '__main__':
    file_path = 'agile_bot/bots/base_bot/docs/stories/story-graph.json'
    try:
        add_test_fields_to_story_graph(file_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
