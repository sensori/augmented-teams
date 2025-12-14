"""
Create simple tree view with side-by-side format
"""
import json
import ast
import re
from pathlib import Path
from collections import defaultdict

def normalize_name(name):
    """Normalize names for matching."""
    # Replace & with and, then remove all non-alphanumeric characters
    name = name.replace('&', 'and').replace(' and ', 'and')
    return re.sub(r'[^a-zA-Z0-9]', '', name.lower())

def extract_scenarios_from_story_file(story_file_path):
    """Extract scenarios from a story markdown file."""
    try:
        with open(story_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        scenarios = []
        pattern = r'###\s+Scenario:\s+(.+?)(?=\n###|\n##|\Z)'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            scenario_text = match.group(1).strip()
            scenario_name = scenario_text.split('\n')[0].strip()
            scenarios.append(scenario_name)
        
        return scenarios
    except Exception:
        return []

def find_story_files(story_name, stories_dir):
    """Find story markdown files matching a story name."""
    story_files = []
    story_normalized = normalize_name(story_name)
    
    map_dir = stories_dir / 'map'
    if not map_dir.exists():
        return story_files
    
    for md_file in map_dir.rglob('*.md'):
        file_name = md_file.stem
        file_name_clean = re.sub(r'^[📝📄📋📌📎]+\s*', '', file_name)
        file_normalized = normalize_name(file_name_clean)
        
        if story_normalized in file_normalized or file_normalized in story_normalized:
            story_files.append(md_file)
    
    return story_files

def parse_test_file(file_path):
    """Parse a test file and extract classes and methods."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
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
    except Exception:
        return []

def find_helper_file(test_file_name, test_dir):
    """Find helper file for a test file."""
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
        method_words = set(method_normalized.replace('_', ' ').split())
        method_words = {w for w in method_words if w not in ['when', 'then', 'given', 'test', 'should', 'does', 'not']}
        
        scenario_words = set(scenario_normalized.split())
        scenario_words = {w for w in scenario_words if w not in ['scenario', 'happy', 'path', 'edge', 'case', 'the', 'a', 'an', 'to', 'for', 'with', 'when', 'then', 'given']}
        
        if method_words and scenario_words:
            overlap = 0
            for mw in method_words:
                for sw in scenario_words:
                    if len(mw) > 3 and len(sw) > 3:
                        if mw in sw or sw in mw:
                            overlap += 2
                        elif mw[:4] == sw[:4]:
                            overlap += 1
            
            if overlap > best_score:
                best_score = overlap
                best_match = scenario
    
    return best_match if best_score > 0 else None

def format_scenario_name(scenario):
    """Format scenario name for display."""
    if isinstance(scenario, dict):
        scenario = scenario.get('name', 'Unknown Scenario')
    # Remove (happy_path) or (edge_case) suffixes
    scenario = re.sub(r'\s*\(happy_path\)', '', scenario)
    scenario = re.sub(r'\s*\(edge_case\)', '', scenario)
    return scenario.strip()

def generate_scenario_name_from_method(method_name):
    """Generate a readable scenario name from test method name."""
    # Remove 'test_' prefix
    name = method_name.replace('test_', '')
    # Split on underscores and capitalize each word
    words = name.split('_')
    return ' '.join(word.capitalize() for word in words)

def get_scenarios_from_story_graph(story_name, story_graph):
    """Get scenarios for a story from the story graph."""
    scenarios = []
    for epic in story_graph.get('epics', []):
        # Check stories directly under epic
        for story_group in epic.get('story_groups', []):
            for story in story_group.get('stories', []):
                if story.get('name') == story_name:
                    scenarios.extend(story.get('scenarios', []))
        
        # Check stories in sub-epics
        for sub_epic in epic.get('sub_epics', []):
            for story_group in sub_epic.get('story_groups', []):
                for story in story_group.get('stories', []):
                    if story.get('name') == story_name:
                        scenarios.extend(story.get('scenarios', []))
    return scenarios

def print_tree(story_structure, test_mapping, stories_dir, test_dir, file_to_epic, story_graph):
    """Print simple tree view with side-by-side format."""
    
    for epic_name, epic_data in story_structure.items():
        print(f"EPIC: {epic_name}")
        
        for sub_epic_name, sub_epic_data in epic_data['sub_epics'].items():
            # Find helper file for this sub-epic
            helper_file = None
            sub_epic_normalized = normalize_name(sub_epic_name)
            
            # First, try to find a helper file that matches the sub-epic name
            helper_file = None
            base_name = sub_epic_normalized.replace(' ', '_').replace('-', '_')
            # Try different variations
            possible_helper_names = [
                f"test_{base_name}_helpers.py",
                f"test_{sub_epic_normalized}_helpers.py",
            ]
            # Also try with underscores instead of removing them
            base_with_underscores = re.sub(r'([a-z])([A-Z])', r'\1_\2', sub_epic_name).lower().replace(' ', '_')
            possible_helper_names.append(f"test_{base_with_underscores}_helpers.py")
            
            for helper_name in possible_helper_names:
                helper_path = test_dir / helper_name
                if helper_path.exists():
                    helper_file = helper_name
                    break
            
            # If still not found, search all helper files for a match
            if not helper_file:
                for helper_file_path in test_dir.glob('*_helpers.py'):
                    helper_base = helper_file_path.stem.replace('test_', '').replace('_helpers', '')
                    helper_base_normalized = normalize_name(helper_base)
                    if sub_epic_normalized in helper_base_normalized or helper_base_normalized in sub_epic_normalized:
                        helper_file = helper_file_path.name
                        break
            
            # If no helper file found, find matching test file
            matching_test_file = None
            if not helper_file:
                for test_file in test_dir.glob('test_*.py'):
                    if test_file.name.endswith('_helpers.py'):
                        continue
                    file_base = test_file.stem.replace('test_', '')
                    file_base_normalized = normalize_name(file_base)
                    
                    # Check both directions: sub-epic in file, or file in sub-epic
                    if sub_epic_normalized in file_base_normalized or file_base_normalized in sub_epic_normalized:
                        matching_test_file = test_file.name
                        break
            
            # Always show helper file if found, otherwise show test file, never "x"
            if helper_file:
                helper_display = helper_file
            elif matching_test_file:
                helper_display = matching_test_file
            else:
                helper_display = "x"
            print(f"  SUB-EPIC: {sub_epic_name}    --    {helper_display}")
            
            for story_info in sub_epic_data['stories']:
                story_name = story_info['name']
                matching_tests = test_mapping.get(story_name, {})
                
                # Check if there's a test file that matches the story name better than any test class
                story_normalized = normalize_name(story_name)
                best_file_match = None
                best_file_score = 0
                
                for test_file in test_dir.glob('test_*.py'):
                    if test_file.name.endswith('_helpers.py'):
                        continue
                    file_base = test_file.stem.replace('test_', '')
                    file_base_normalized = normalize_name(file_base)
                    
                    # Calculate match score: longer common substring = better match
                    if story_normalized in file_base_normalized:
                        score = len(story_normalized) / len(file_base_normalized) if file_base_normalized else 0
                    elif file_base_normalized in story_normalized:
                        score = len(file_base_normalized) / len(story_normalized) if story_normalized else 0
                    else:
                        score = 0
                    
                    if score > best_file_score:
                        best_file_score = score
                        best_file_match = test_file.name
                
                if matching_tests:
                    # Get scenarios from story graph
                    scenarios = get_scenarios_from_story_graph(story_name, story_graph)
                    
                    # Get test class for this story
                    test_class = None
                    test_file_name = None
                    for test_file, test_classes in matching_tests.items():
                        if test_classes:
                            test_class = test_classes[0]  # Take first class
                            test_file_name = test_file
                            break
                    
                    # If we found a better file match, prefer showing the file name
                    if best_file_match and best_file_score > 0.5:
                        # Check if the matched test file is the same as the one with the test class
                        if test_file_name != best_file_match:
                            # File match is better - show file name instead
                            print(f"    STORY: {story_name}  --  {best_file_match} (file match, no exact test class)")
                        else:
                            # Same file, show test class
                            class_display = test_class['name'] if test_class else "x"
                            print(f"    STORY: {story_name}  --  {class_display}")
                    else:
                        class_display = test_class['name'] if test_class else "x"
                        print(f"    STORY: {story_name}  --  {class_display}")
                    
                    # Match scenarios to methods using test_method field
                    if test_class and scenarios:
                        # Create mapping: test_method -> scenario
                        method_to_scenario = {}
                        scenario_to_method = {}
                        
                        for scenario in scenarios:
                            test_method = scenario.get('test_method')
                            if test_method:
                                # Find this method in test class
                                if test_method in test_class['methods']:
                                    method_to_scenario[test_method] = scenario
                                    scenario_to_method[scenario.get('name')] = test_method
                        
                        # Print scenarios with their methods
                        for scenario in scenarios:
                            scenario_name = scenario.get('name', 'Unknown Scenario')
                            test_method = scenario.get('test_method')
                            
                            if test_method and test_method in test_class['methods']:
                                # Method exists, show scenario name and method
                                print(f"            SCENARIO: {scenario_name}  --  {test_method}")
                            elif test_method:
                                # Method specified but not found in class
                                print(f"            SCENARIO: {scenario_name}  --  {test_method} (not found)")
                            else:
                                # No test method specified
                                print(f"            SCENARIO: {scenario_name}  --  x")
                        
                        # Print methods without scenarios
                        for method in test_class['methods']:
                            if method not in method_to_scenario:
                                # Generate scenario name from method
                                scenario_name = generate_scenario_name_from_method(method)
                                print(f"            SCENARIO: {scenario_name}  --  {method}")
                    elif test_class:
                        # Has class but no scenarios from story graph
                        for method in test_class['methods']:
                            scenario_name = generate_scenario_name_from_method(method)
                            print(f"            SCENARIO: {scenario_name}  --  {method}")
                    elif scenarios:
                        # Has scenarios but no class
                        for scenario in scenarios:
                            scenario_name = scenario.get('name', 'Unknown Scenario')
                            test_method = scenario.get('test_method', 'x')
                            print(f"            SCENARIO: {scenario_name}  --  {test_method}")
                else:
                    # No matching test classes found, but check if there's a test file that matches the story name
                    story_normalized = normalize_name(story_name)
                    matching_test_file = None
                    
                    for test_file in test_dir.glob('test_*.py'):
                        if test_file.name.endswith('_helpers.py'):
                            continue
                        file_base = test_file.stem.replace('test_', '')
                        file_base_normalized = normalize_name(file_base)
                        
                        # Check if story name matches test file name
                        if (story_normalized in file_base_normalized or 
                            file_base_normalized in story_normalized or
                            story_normalized == file_base_normalized):
                            matching_test_file = test_file.name
                            break
                    
                    # Display test file name if found, otherwise "x"
                    if matching_test_file:
                        print(f"    STORY: {story_name}  --  {matching_test_file} (no matching test class)")
                    else:
                        print(f"    STORY: {story_name}  --  x")
                    
                    # Check if story has scenarios but no tests
                    scenarios = get_scenarios_from_story_graph(story_name, story_graph)
                    if scenarios:
                        for scenario in scenarios:
                            scenario_name = scenario.get('name', 'Unknown Scenario')
                            test_method = scenario.get('test_method', 'x')
                            print(f"            SCENARIO: {scenario_name}  --  {test_method}")
        
        for story_info in epic_data['stories']:
            story_name = story_info['name']
            matching_tests = test_mapping.get(story_name, {})
            
            if matching_tests:
                # Get scenarios from story graph
                scenarios = get_scenarios_from_story_graph(story_name, story_graph)
                
                test_class = None
                for test_file, test_classes in matching_tests.items():
                    if test_classes:
                        test_class = test_classes[0]
                        break
                
                class_display = test_class['name'] if test_class else "x"
                print(f"  STORY: {story_name}  --  {class_display}")
                
                if test_class and scenarios:
                    # Create mapping: test_method -> scenario
                    method_to_scenario = {}
                    
                    for scenario in scenarios:
                        test_method = scenario.get('test_method')
                        if test_method and test_method in test_class['methods']:
                            method_to_scenario[test_method] = scenario
                    
                    for scenario in scenarios:
                        scenario_name = scenario.get('name', 'Unknown Scenario')
                        test_method = scenario.get('test_method')
                        
                        if test_method and test_method in test_class['methods']:
                            print(f"        SCENARIO: {scenario_name}  --  {test_method}")
                        elif test_method:
                            print(f"        SCENARIO: {scenario_name}  --  {test_method} (not found)")
                        else:
                            print(f"        SCENARIO: {scenario_name}  --  x")
                    
                    # Print methods without scenarios
                    for method in test_class['methods']:
                        if method not in method_to_scenario:
                            scenario_name = generate_scenario_name_from_method(method)
                            print(f"        SCENARIO: {scenario_name}  --  {method}")
                elif test_class:
                    for method in test_class['methods']:
                        scenario_name = generate_scenario_name_from_method(method)
                        print(f"        SCENARIO: {scenario_name}  --  {method}")
                elif scenarios:
                    for scenario in scenarios:
                        scenario_name = scenario.get('name', 'Unknown Scenario')
                        test_method = scenario.get('test_method', 'x')
                        print(f"        SCENARIO: {scenario_name}  --  {test_method}")
            else:
                print(f"  STORY: {story_name}  --  x")
                scenarios = get_scenarios_from_story_graph(story_name, story_graph)
                if scenarios:
                    for scenario in scenarios:
                        scenario_name = scenario.get('name', 'Unknown Scenario')
                        test_method = scenario.get('test_method', 'x')
                        print(f"        SCENARIO: {scenario_name}  --  {test_method}")

def main():
    story_graph_path = Path('agile_bot/bots/base_bot/docs/stories/story-graph.json')
    with open(story_graph_path, 'r', encoding='utf-8') as f:
        story_graph = json.load(f)
    
    def build_structure(epic):
        node = {
            'name': epic['name'],
            'stories': [],
            'sub_epics': {}
        }
        
        if 'sub_epics' in epic:
            for sub_epic in epic['sub_epics']:
                node['sub_epics'][sub_epic['name']] = build_structure(sub_epic)
        
        if 'story_groups' in epic:
            for group in epic['story_groups']:
                if 'stories' in group:
                    for story in group['stories']:
                        node['stories'].append({'name': story['name']})
        
        return node
    
    story_structure = {}
    for epic in story_graph.get('epics', []):
        story_structure[epic['name']] = build_structure(epic)
    
    story_names = []
    def collect_stories(node):
        story_names.extend([s['name'] for s in node['stories']])
        for sub_epic in node['sub_epics'].values():
            collect_stories(sub_epic)
    
    for epic_node in story_structure.values():
        collect_stories(epic_node)
    
    test_dir = Path('agile_bot/bots/base_bot/test')
    stories_dir = Path('agile_bot/bots/base_bot/docs/stories')
    test_files = list(test_dir.glob('test_*.py'))
    
    test_mapping = defaultdict(lambda: defaultdict(list))
    file_to_epic = {}
    
    for test_file in test_files:
        if test_file.name in ['test_helpers.py', 'test_utils.py', 'conftest.py']:
            continue
        
        classes = parse_test_file(test_file)
        
        file_base = test_file.stem.replace('test_', '')
        matched_epic = None
        
        for epic_name, epic_data in story_structure.items():
            for sub_epic_name, sub_epic_data in epic_data['sub_epics'].items():
                if normalize_name(sub_epic_name) in normalize_name(file_base) or normalize_name(file_base) in normalize_name(sub_epic_name):
                    matched_epic = epic_name
                    break
            
            if normalize_name(epic_name) in normalize_name(file_base) or normalize_name(file_base) in normalize_name(epic_name):
                matched_epic = epic_name
                break
        
        file_to_epic[test_file.name] = matched_epic
        
        # Track which classes have already matched stories
        matched_classes = set()
        
        for test_class in classes:
            matched_story = match_test_to_story(test_class['name'], story_names)
            
            if matched_story:
                test_mapping[matched_story][test_file.name].append(test_class)
                matched_classes.add(test_class['name'])
            else:
                for story in story_names:
                    if normalize_name(file_base) in normalize_name(story) or normalize_name(story) in normalize_name(file_base):
                        test_mapping[story][test_file.name].append(test_class)
                        matched_classes.add(test_class['name'])
                        break
        
        # Also check if file base name matches any stories that don't have test matches yet
        # This handles cases where a test file contains tests for multiple stories
        # Split file base into words BEFORE normalizing (to preserve word boundaries)
        file_base_words_raw = re.split(r'[_\s]+', file_base.replace('test_', ''))
        file_base_words = {normalize_name(w) for w in file_base_words_raw if len(w) > 2}
        file_base_normalized = normalize_name(file_base)
        
        for story in story_names:
            # Skip if story already has matches from this file
            if test_file.name in test_mapping[story]:
                continue
                
            # Split story into words BEFORE normalizing
            story_words_raw = re.split(r'[_\s]+', story)
            story_words = {normalize_name(w) for w in story_words_raw if len(w) > 2}
            story_normalized = normalize_name(story)
            
            # Check if significant words from file base are in story name
            # This handles cases like "invoke_cli" matching "Invoke Bot CLI"
            if file_base_words and story_words:
                # Count how many file base words appear in story words
                matching_words = file_base_words & story_words
                # Require at least 2 matching words (for multi-word file bases)
                # OR if file base is a significant substring of story (at least 6 chars)
                # This prevents false matches like "generate_cli" matching "Invoke Bot CLI"
                should_match = False
                if len(matching_words) >= 2:
                    # Strong match: at least 2 words match
                    should_match = True
                elif len(file_base_words) == 1 and len(matching_words) == 1:
                    # Single word file base matches single word in story - only if it's a significant word
                    matching_word = list(matching_words)[0]
                    if len(matching_word) >= 4:  # At least 4 chars to be significant
                        should_match = True
                elif file_base_normalized in story_normalized and len(file_base_normalized) >= 6:
                    # File base is a substring of story and is significant length
                    should_match = True
                
                if should_match:
                    # Add only TEST classes (starting with "Test") that haven't matched other stories yet
                    for test_class in classes:
                        if test_class['name'].startswith('Test') and test_class['name'] not in matched_classes:
                            test_mapping[story][test_file.name].append(test_class)
    
    print_tree(story_structure, test_mapping, stories_dir, test_dir, file_to_epic, story_graph)

if __name__ == '__main__':
    main()

