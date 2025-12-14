"""
Analyze test files against story graph and create tree view mapping.
"""
import json
import ast
import re
from pathlib import Path
from collections import defaultdict

def normalize_name(name):
    """Normalize names for matching."""
    return re.sub(r'[^a-zA-Z0-9]', '', name.lower())

def extract_story_names_from_graph(story_graph):
    """Extract all story names from the story graph."""
    stories = []
    
    def extract_from_epic(epic):
        if 'sub_epics' in epic:
            for sub_epic in epic['sub_epics']:
                extract_from_epic(sub_epic)
        if 'story_groups' in epic:
            for group in epic['story_groups']:
                if 'stories' in group:
                    for story in group['stories']:
                        stories.append(story['name'])
    
    for epic in story_graph.get('epics', []):
        extract_from_epic(epic)
    
    return stories

def parse_test_file(file_path):
    """Parse a test file and extract classes and methods."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Try to parse, but handle syntax errors gracefully
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Fallback: use regex to find test classes
            classes = []
            class_pattern = r'class\s+(Test\w+)'
            method_pattern = r'def\s+(test_\w+)'
            
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
                # Find methods in this class (simplified)
                class_start = match.end()
                class_end = content.find('\nclass ', class_start)
                if class_end == -1:
                    class_end = len(content)
                
                class_content = content[class_start:class_end]
                methods = re.findall(method_pattern, class_content)
                
                classes.append({
                    'name': class_name,
                    'methods': methods,
                    'file': file_path.name
                })
            
            return classes
        
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'methods': [],
                    'file': file_path.name
                }
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                        class_info['methods'].append(item.name)
                
                classes.append(class_info)
        
        return classes
    except Exception as e:
        # Fallback to regex parsing
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            classes = []
            class_pattern = r'class\s+(Test\w+)'
            
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
                classes.append({
                    'name': class_name,
                    'methods': [],
                    'file': file_path.name
                })
            
            return classes
        except:
            return []

def match_test_to_story(test_name, story_names):
    """Try to match a test class name to a story name."""
    test_normalized = normalize_name(test_name)
    
    # Remove common prefixes
    test_clean = test_normalized.replace('test', '')
    
    best_matches = []
    for story in story_names:
        story_normalized = normalize_name(story)
        
        # Check if test name contains story name or vice versa
        if test_clean in story_normalized or story_normalized in test_clean:
            # Calculate similarity score
            score = len(set(test_clean) & set(story_normalized))
            best_matches.append((story, score))
    
    if best_matches:
        best_matches.sort(key=lambda x: x[1], reverse=True)
        return best_matches[0][0]
    
    return None

def build_story_tree(story_graph):
    """Build a hierarchical tree structure from story graph."""
    tree = {}
    
    def add_epic(epic, parent_path=""):
        epic_name = epic['name']
        current_path = f"{parent_path}/{epic_name}" if parent_path else epic_name
        
        node = {
            'name': epic_name,
            'path': current_path,
            'stories': [],
            'sub_epics': {}
        }
        
        # Add sub-epics
        if 'sub_epics' in epic:
            for sub_epic in epic['sub_epics']:
                sub_name = sub_epic['name']
                node['sub_epics'][sub_name] = add_epic(sub_epic, current_path)
        
        # Add stories
        if 'story_groups' in epic:
            for group in epic['story_groups']:
                if 'stories' in group:
                    for story in group['stories']:
                        node['stories'].append(story['name'])
        
        return node
    
    for epic in story_graph.get('epics', []):
        tree[epic['name']] = add_epic(epic)
    
    return tree

def print_tree_view(story_tree, test_mapping, indent=0):
    """Print tree view with test mappings."""
    prefix = "  " * indent
    
    for epic_name, epic_data in story_tree.items():
        print(f"{prefix}[EPIC] {epic_name}")
        
        # Print sub-epics
        for sub_epic_name, sub_epic_data in epic_data['sub_epics'].items():
            print(f"{prefix}  [SUB-EPIC] {sub_epic_name}")
            
            # Print stories in this sub-epic
            for story_name in sub_epic_data['stories']:
                print(f"{prefix}    [STORY] {story_name}")
                
                # Find matching tests
                matching_tests = test_mapping.get(story_name, [])
                if matching_tests:
                    for test_file, test_classes in matching_tests.items():
                        print(f"{prefix}      [TEST FILE] {test_file}")
                        for test_class in test_classes:
                            print(f"{prefix}        |-- Class: {test_class['name']}")
                            if test_class['methods']:
                                for method in test_class['methods'][:3]:  # Show first 3 methods
                                    print(f"{prefix}        |   |-- Method: {method}")
                                if len(test_class['methods']) > 3:
                                    print(f"{prefix}        |   |-- ... ({len(test_class['methods']) - 3} more)")
                else:
                    print(f"{prefix}      [NO TESTS]")
        
        # Print stories directly in epic
        for story_name in epic_data['stories']:
            print(f"{prefix}  [STORY] {story_name}")
            matching_tests = test_mapping.get(story_name, [])
            if matching_tests:
                for test_file, test_classes in matching_tests.items():
                    print(f"{prefix}    [TEST FILE] {test_file}")
                    for test_class in test_classes:
                        print(f"{prefix}      |-- Class: {test_class['name']}")

def main():
    # Load story graph
    story_graph_path = Path('agile_bot/bots/base_bot/docs/stories/story-graph.json')
    with open(story_graph_path, 'r', encoding='utf-8') as f:
        story_graph = json.load(f)
    
    # Extract all story names
    story_names = extract_story_names_from_graph(story_graph)
    
    # Parse all test files
    test_dir = Path('agile_bot/bots/base_bot/test')
    test_files = list(test_dir.glob('test_*.py'))
    
    # Build test mapping: story_name -> {test_file: [test_classes]}
    test_mapping = defaultdict(lambda: defaultdict(list))
    
    for test_file in test_files:
        if test_file.name in ['test_helpers.py', 'test_utils.py', 'conftest.py']:
            continue
        
        classes = parse_test_file(test_file)
        
        for test_class in classes:
            # Try to match class name to story
            matched_story = match_test_to_story(test_class['name'], story_names)
            
            if matched_story:
                test_mapping[matched_story][test_file.name].append(test_class)
            else:
                # Try to match based on file name
                file_base = test_file.stem.replace('test_', '')
                for story in story_names:
                    if normalize_name(file_base) in normalize_name(story) or normalize_name(story) in normalize_name(file_base):
                        test_mapping[story][test_file.name].append(test_class)
                        break
    
    # Build story tree
    story_tree = build_story_tree(story_graph)
    
    # Print tree view
    print("=" * 80)
    print("TEST FILE MAPPING TO STORY GRAPH")
    print("=" * 80)
    print()
    
    print_tree_view(story_tree, test_mapping)
    
    # Print unmapped test files
    print("\n" + "=" * 80)
    print("UNMAPPED TEST FILES")
    print("=" * 80)
    
    mapped_files = set()
    for story_tests in test_mapping.values():
        mapped_files.update(story_tests.keys())
    
    for test_file in test_files:
        if test_file.name not in mapped_files and test_file.name not in ['test_helpers.py', 'test_utils.py', 'conftest.py']:
            classes = parse_test_file(test_file)
            print(f"\n[UNMAPPED FILE] {test_file.name}")
            for cls in classes:
                print(f"  |-- {cls['name']} ({len(cls['methods'])} methods)")

if __name__ == '__main__':
    main()

