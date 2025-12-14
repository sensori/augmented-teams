"""
Create side-by-side tree view: Test File | Epic (with helper files), Class | Story, Method | Scenario
"""
import json
import ast
import re
from pathlib import Path
from collections import defaultdict

def normalize_name(name):
    """Normalize names for matching."""
    return re.sub(r'[^a-zA-Z0-9]', '', name.lower())

def extract_scenarios_from_story_file(story_file_path):
    """Extract scenarios from a story markdown file."""
    try:
        with open(story_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        scenarios = []
        # Look for "### Scenario:" patterns
        pattern = r'###\s+Scenario:\s+(.+?)(?=\n###|\n##|\Z)'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            scenario_text = match.group(1).strip()
            # Extract the scenario name (first line)
            scenario_name = scenario_text.split('\n')[0].strip()
            scenarios.append(scenario_name)
        
        return scenarios
    except Exception as e:
        return []

def find_story_files(story_name, stories_dir):
    """Find story markdown files matching a story name."""
    story_files = []
    story_normalized = normalize_name(story_name)
    
    # Search in the map directory structure
    map_dir = stories_dir / 'map'
    if not map_dir.exists():
        return story_files
    
    for md_file in map_dir.rglob('*.md'):
        # Remove emoji prefix if present (e.g., "📝 Story Name.md" -> "Story Name")
        file_name = md_file.stem
        # Remove common emoji prefixes
        file_name_clean = re.sub(r'^[📝📄📋📌📎]+\s*', '', file_name)
        file_normalized = normalize_name(file_name_clean)
        
        # Check if story name matches file name
        if story_normalized in file_normalized or file_normalized in story_normalized:
            story_files.append(md_file)
    
    return story_files

def extract_story_structure(story_graph):
    """Extract epic -> sub-epic -> story structure."""
    structure = {}
    
    def add_epic(epic, parent_path=""):
        epic_name = epic['name']
        current_path = f"{parent_path}/{epic_name}" if parent_path else epic_name
        
        node = {
            'name': epic_name,
            'path': current_path,
            'stories': [],
            'sub_epics': {}
        }
        
        if 'sub_epics' in epic:
            for sub_epic in epic['sub_epics']:
                sub_name = sub_epic['name']
                node['sub_epics'][sub_name] = add_epic(sub_epic, current_path)
        
        if 'story_groups' in epic:
            for group in epic['story_groups']:
                if 'stories' in group:
                    for story in group['stories']:
                        node['stories'].append({
                            'name': story['name'],
                            'epic': epic_name,
                            'sub_epic': None
                        })
        
        return node
    
    for epic in story_graph.get('epics', []):
        structure[epic['name']] = add_epic(epic)
    
    # Fix sub-epic references
    def fix_sub_epic_refs(node, parent_epic=None, parent_sub_epic=None):
        if parent_sub_epic:
            for story in node['stories']:
                story['sub_epic'] = parent_sub_epic
        
        for sub_epic_name, sub_epic_node in node['sub_epics'].items():
            fix_sub_epic_refs(sub_epic_node, parent_epic or node['name'], sub_epic_name)
    
    for epic_name, epic_node in structure.items():
        fix_sub_epic_refs(epic_node, epic_name)
    
    return structure

def parse_test_file(file_path):
    """Parse a test file and extract classes and methods."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Fallback to regex
            classes = []
            class_pattern = r'class\s+(Test\w+)'
            method_pattern = r'def\s+(test_\w+)'
            
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
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
        return []

def find_helper_file(test_file_name, test_dir):
    """Find helper file for a test file."""
    # Check for _helpers.py pattern
    base_name = test_file_name.replace('test_', '').replace('.py', '')
    helper_name = f"test_{base_name}_helpers.py"
    helper_path = test_dir / helper_name
    
    if helper_path.exists():
        return helper_name
    return None

def match_test_to_story(test_name, story_names):
    """Match test class name to story name."""
    test_normalized = normalize_name(test_name.replace('Test', ''))
    
    best_match = None
    best_score = 0
    
    for story in story_names:
        story_normalized = normalize_name(story)
        
        # Calculate overlap score
        test_words = set(test_normalized.split())
        story_words = set(story_normalized.split())
        
        if test_words and story_words:
            overlap = len(test_words & story_words)
            if overlap > best_score:
                best_score = overlap
                best_match = story
    
    return best_match

def match_method_to_scenario(method_name, scenarios):
    """Match test method name to scenario name."""
    method_normalized = normalize_name(method_name.replace('test_', ''))
    
    best_match = None
    best_score = 0
    
    for scenario in scenarios:
        scenario_normalized = normalize_name(scenario)
        
        # Extract key words from method (remove common test words)
        method_words = set(method_normalized.replace('_', ' ').split())
        # Remove common test words
        method_words = {w for w in method_words if w not in ['when', 'then', 'given', 'test', 'should', 'does', 'not']}
        
        # Extract key words from scenario
        scenario_words = set(scenario_normalized.split())
        # Remove common words
        scenario_words = {w for w in scenario_words if w not in ['scenario', 'happy', 'path', 'edge', 'case', 'the', 'a', 'an', 'to', 'for', 'with', 'when', 'then', 'given']}
        
        if method_words and scenario_words:
            # Check for substring matches (more flexible)
            overlap = 0
            for mw in method_words:
                for sw in scenario_words:
                    if len(mw) > 3 and len(sw) > 3:  # Only match substantial words
                        if mw in sw or sw in mw:
                            overlap += 2
                        elif mw[:4] == sw[:4]:  # Prefix match
                            overlap += 1
            
            if overlap > best_score:
                best_score = overlap
                best_match = scenario
    
    return best_match if best_score > 0 else None

def print_side_by_side_tree(story_structure, test_mapping, stories_dir, test_dir, file_to_epic):
    """Print side-by-side tree view."""
    
    print("=" * 140)
    print("SIDE-BY-SIDE TEST TO STORY MAPPING")
    print("=" * 140)
    print()
    
    for epic_name, epic_data in story_structure.items():
        print(f"EPIC: {epic_name}")
        print("-" * 140)
        
        # Process sub-epics
        for sub_epic_name, sub_epic_data in epic_data['sub_epics'].items():
            print(f"\n  SUB-EPIC: {sub_epic_name}")
            print("  " + "-" * 138)
            
            for story_info in sub_epic_data['stories']:
                story_name = story_info['name']
                
                # Find matching tests
                matching_tests = test_mapping.get(story_name, {})
                
                if matching_tests:
                    for test_file, test_classes in matching_tests.items():
                        # Check for helper file
                        helper_file = find_helper_file(test_file, test_dir)
                        helper_indicator = f" [HELPER: {helper_file}]" if helper_file else ""
                        
                        # Find scenarios for this story
                        story_files = find_story_files(story_name, stories_dir)
                        scenarios = []
                        for sf in story_files:
                            scenarios.extend(extract_scenarios_from_story_file(sf))
                        
                        print(f"\n  STORY: {story_name}")
                        print("  " + "=" * 136)
                        
                        # Show test file with epic
                        epic_for_file = file_to_epic.get(test_file, "[UNMAPPED]")
                        print(f"\n  TEST FILE: {test_file:<55} | EPIC: {epic_for_file}{helper_indicator}")
                        print("  " + "-" * 136)
                        
                        for test_class in test_classes:
                            print(f"\n  CLASS: {test_class['name']:<55} | STORY: {story_name}")
                            print("  " + "-" * 136)
                            
                            # Match methods to scenarios
                            for method in test_class['methods']:
                                matched_scenario = match_method_to_scenario(method, scenarios) if scenarios else None
                                scenario_display = matched_scenario if matched_scenario else "[NO SCENARIO MATCH]"
                                
                                # Truncate long names
                                method_display = method[:50] + "..." if len(method) > 53 else method
                                scenario_display_trunc = scenario_display[:50] + "..." if len(scenario_display) > 53 else scenario_display
                                
                                print(f"    METHOD: {method_display:<53} | SCENARIO: {scenario_display_trunc}")
                            
                            if not test_class['methods']:
                                print(f"    [NO METHODS]")
                else:
                    print(f"\n  STORY: {story_name}")
                    print("  " + "=" * 136)
                    print(f"    [NO TESTS]")
        
        # Process stories directly in epic
        for story_info in epic_data['stories']:
            story_name = story_info['name']
            matching_tests = test_mapping.get(story_name, {})
            
            if matching_tests:
                for test_file, test_classes in matching_tests.items():
                    helper_file = find_helper_file(test_file, test_dir)
                    helper_indicator = f" [HELPER: {helper_file}]" if helper_file else ""
                    
                    story_files = find_story_files(story_name, stories_dir)
                    scenarios = []
                    for sf in story_files:
                        scenarios.extend(extract_scenarios_from_story_file(sf))
                    
                    print(f"\n  STORY: {story_name}")
                    print("  " + "=" * 136)
                    
                    epic_for_file = file_to_epic.get(test_file, "[UNMAPPED]")
                    print(f"\n  TEST FILE: {test_file:<55} | EPIC: {epic_for_file}{helper_indicator}")
                    print("  " + "-" * 136)
                    
                    for test_class in test_classes:
                        print(f"\n  CLASS: {test_class['name']:<55} | STORY: {story_name}")
                        print("  " + "-" * 136)
                        
                        for method in test_class['methods']:
                            matched_scenario = match_method_to_scenario(method, scenarios) if scenarios else None
                            scenario_display = matched_scenario if matched_scenario else "[NO SCENARIO MATCH]"
                            
                            method_display = method[:50] + "..." if len(method) > 53 else method
                            scenario_display_trunc = scenario_display[:50] + "..." if len(scenario_display) > 53 else scenario_display
                            
                            print(f"    METHOD: {method_display:<53} | SCENARIO: {scenario_display_trunc}")

def main():
    # Load story graph
    story_graph_path = Path('agile_bot/bots/base_bot/docs/stories/story-graph.json')
    with open(story_graph_path, 'r', encoding='utf-8') as f:
        story_graph = json.load(f)
    
    # Extract story structure
    story_structure = extract_story_structure(story_graph)
    
    # Get all story names
    story_names = []
    def collect_stories(node):
        story_names.extend([s['name'] for s in node['stories']])
        for sub_epic in node['sub_epics'].values():
            collect_stories(sub_epic)
    
    for epic_node in story_structure.values():
        collect_stories(epic_node)
    
    # Parse test files
    test_dir = Path('agile_bot/bots/base_bot/test')
    stories_dir = Path('agile_bot/bots/base_bot/docs/stories')
    test_files = list(test_dir.glob('test_*.py'))
    
    # Build test mapping: story_name -> {test_file: [test_classes]}
    test_mapping = defaultdict(lambda: defaultdict(list))
    file_to_epic = {}
    
    for test_file in test_files:
        if test_file.name in ['test_helpers.py', 'test_utils.py', 'conftest.py']:
            continue
        
        classes = parse_test_file(test_file)
        
        # Try to match file to epic/sub-epic
        file_base = test_file.stem.replace('test_', '')
        matched_epic = None
        
        for epic_name, epic_data in story_structure.items():
            # Check sub-epics
            for sub_epic_name, sub_epic_data in epic_data['sub_epics'].items():
                if normalize_name(sub_epic_name) in normalize_name(file_base) or normalize_name(file_base) in normalize_name(sub_epic_name):
                    matched_epic = epic_name
                    break
            
            if normalize_name(epic_name) in normalize_name(file_base) or normalize_name(file_base) in normalize_name(epic_name):
                matched_epic = epic_name
                break
        
        file_to_epic[test_file.name] = matched_epic
        
        for test_class in classes:
            matched_story = match_test_to_story(test_class['name'], story_names)
            
            if matched_story:
                test_mapping[matched_story][test_file.name].append(test_class)
            else:
                # Try file-based matching
                for story in story_names:
                    if normalize_name(file_base) in normalize_name(story) or normalize_name(story) in normalize_name(file_base):
                        test_mapping[story][test_file.name].append(test_class)
                        break
    
    # Print side-by-side tree
    print_side_by_side_tree(story_structure, test_mapping, stories_dir, test_dir, file_to_epic)
    
    # Print summary of helper files
    print("\n" + "=" * 140)
    print("HELPER FILES SUMMARY")
    print("=" * 140)
    print()
    
    helper_files_found = {}
    for test_file in test_files:
        if test_file.name.endswith('_helpers.py'):
            base_name = test_file.name.replace('test_', '').replace('_helpers.py', '')
            helper_files_found[base_name] = test_file.name
    
    for base_name, helper_file in sorted(helper_files_found.items()):
        print(f"  {base_name:<50} -> {helper_file}")

if __name__ == '__main__':
    main()

