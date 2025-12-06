#!/usr/bin/env python3
"""
Run all test scenarios and identify issues:
1. Check JSON structure (should use story_groups, no nested stories)
2. Identify missing expected files
3. Run all tests
4. Create expected files from actual where needed
"""
import sys
import json
from pathlib import Path
import subprocess

scenarios_dir = Path(__file__).parent

def has_nested_stories(data):
    """Check if JSON has nested stories (old structure)."""
    if isinstance(data, dict):
        # Check for stories array that contains stories with nested stories
        if 'stories' in data:
            for story in data.get('stories', []):
                if isinstance(story, dict) and 'stories' in story:
                    return True
        # Check sub_epics recursively
        for sub_epic in data.get('sub_epics', []):
            if has_nested_stories(sub_epic):
                return True
        # Check epics
        for epic in data.get('epics', []):
            if has_nested_stories(epic):
                return True
    elif isinstance(data, list):
        for item in data:
            if has_nested_stories(item):
                return True
    return False

def uses_story_groups(data):
    """Check if JSON uses story_groups structure."""
    if isinstance(data, dict):
        if 'story_groups' in data:
            return True
        # Check sub_epics recursively
        for sub_epic in data.get('sub_epics', []):
            if uses_story_groups(sub_epic):
                return True
        # Check epics
        for epic in data.get('epics', []):
            if uses_story_groups(epic):
                return True
    elif isinstance(data, list):
        for item in data:
            if uses_story_groups(item):
                return True
    return False

def check_json_structure(file_path):
    """Check if JSON file uses new structure."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        has_nested = has_nested_stories(data)
        has_groups = uses_story_groups(data)
        
        return {
            'valid': not has_nested and has_groups,
            'has_nested_stories': has_nested,
            'uses_story_groups': has_groups
        }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }

def find_test_scenarios():
    """Find all test scenario directories."""
    scenarios = []
    for item in scenarios_dir.iterdir():
        if item.is_dir() and not item.name.startswith('_') and item.name != '__pycache__':
            test_file = item / "test_render_sync_render_round_trip.py"
            if test_file.exists():
                scenarios.append(item.name)
    return sorted(scenarios)

def check_expected_files(scenario_dir):
    """Check what expected files exist and what's missing."""
    given_dir = scenario_dir / "1_given"
    then_dir = scenario_dir / "3_then"
    when_dir = scenario_dir / "2_when"
    
    expected = {
        'json_given': None,
        'json_expected': None,
        'drawio_expected': None,
        'json_actual': None,
        'drawio_actual': None
    }
    
    # Check given JSON
    if given_dir.exists():
        for json_file in given_dir.glob("*.json"):
            if 'story-graph' in json_file.name.lower():
                expected['json_given'] = json_file
                break
    
    # Check expected files in 3_then
    if then_dir.exists():
        for json_file in then_dir.glob("expected*.json"):
            expected['json_expected'] = json_file
        for drawio_file in then_dir.glob("expected*.drawio"):
            expected['drawio_expected'] = drawio_file
        for json_file in then_dir.glob("actual*.json"):
            expected['json_actual'] = json_file
        for drawio_file in then_dir.glob("actual*.drawio"):
            expected['drawio_actual'] = drawio_file
    
    return expected

def run_test(scenario_name):
    """Run a single test scenario."""
    print(f"\n{'='*80}")
    print(f"TESTING: {scenario_name}")
    print(f"{'='*80}\n")
    
    scenario_dir = scenarios_dir / scenario_name
    test_script = scenario_dir / "test_render_sync_render_round_trip.py"
    
    if not test_script.exists():
        print(f"[SKIP] No test script found")
        return {'status': 'skip', 'reason': 'No test script'}
    
    # Run the test
    try:
        result = subprocess.run(
            [sys.executable, str(test_script)],
            cwd=str(scenario_dir),
            capture_output=True,
            text=True,
            timeout=120
        )
        
        return {
            'status': 'pass' if result.returncode == 0 else 'fail',
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except subprocess.TimeoutExpired:
        return {'status': 'timeout', 'reason': 'Test timed out'}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def main():
    """Main function to run all tests and check structure."""
    print("\n" + "="*80)
    print("RUNNING ALL TEST SCENARIOS")
    print("="*80)
    
    scenarios = find_test_scenarios()
    print(f"\nFound {len(scenarios)} test scenarios:")
    for s in scenarios:
        print(f"  - {s}")
    
    # Check JSON structure
    print(f"\n{'='*80}")
    print("CHECKING JSON STRUCTURE")
    print(f"{'='*80}\n")
    
    structure_issues = []
    for scenario_name in scenarios:
        scenario_dir = scenarios_dir / scenario_name
        given_dir = scenario_dir / "1_given"
        
        if given_dir.exists():
            for json_file in given_dir.glob("*.json"):
                if 'story-graph' in json_file.name.lower():
                    check = check_json_structure(json_file)
                    if not check['valid']:
                        structure_issues.append({
                            'scenario': scenario_name,
                            'file': json_file,
                            'issue': check
                        })
                        print(f"[ISSUE] {scenario_name}: {json_file.name}")
                        if check.get('has_nested_stories'):
                            print(f"  - Has nested stories (old structure)")
                        if not check.get('uses_story_groups'):
                            print(f"  - Missing story_groups structure")
                        if check.get('error'):
                            print(f"  - Error: {check['error']}")
    
    # Check for missing expected files
    print(f"\n{'='*80}")
    print("CHECKING FOR MISSING EXPECTED FILES")
    print(f"{'='*80}\n")
    
    missing_expected = []
    for scenario_name in scenarios:
        scenario_dir = scenarios_dir / scenario_name
        expected = check_expected_files(scenario_dir)
        
        missing = []
        if not expected['json_expected'] and expected['json_actual']:
            missing.append('expected JSON')
        if not expected['drawio_expected'] and expected['drawio_actual']:
            missing.append('expected DrawIO')
        
        if missing:
            missing_expected.append({
                'scenario': scenario_name,
                'missing': missing,
                'has_actual': {
                    'json': expected['json_actual'] is not None,
                    'drawio': expected['drawio_actual'] is not None
                }
            })
            print(f"[MISSING] {scenario_name}: {', '.join(missing)}")
    
    # Run all tests
    print(f"\n{'='*80}")
    print("RUNNING ALL TESTS")
    print(f"{'='*80}\n")
    
    results = {}
    for scenario_name in scenarios:
        results[scenario_name] = run_test(scenario_name)
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}\n")
    
    passed = sum(1 for r in results.values() if r['status'] == 'pass')
    failed = sum(1 for r in results.values() if r['status'] == 'fail')
    skipped = sum(1 for r in results.values() if r['status'] == 'skip')
    
    for scenario_name, result in sorted(results.items()):
        status = result['status'].upper()
        if result['status'] == 'fail':
            print(f"  [FAIL] {scenario_name} (exit code: {result.get('exit_code', '?')})")
        elif result['status'] == 'skip':
            print(f"  [SKIP] {scenario_name} ({result.get('reason', 'unknown')})")
        else:
            print(f"  [PASS] {scenario_name}")
    
    print(f"\nTotal: {len(results)} tests")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    
    if structure_issues:
        print(f"\nStructure Issues: {len(structure_issues)}")
    if missing_expected:
        print(f"Missing Expected Files: {len(missing_expected)}")
    
    print("="*80)
    
    return {
        'results': results,
        'structure_issues': structure_issues,
        'missing_expected': missing_expected
    }

if __name__ == '__main__':
    try:
        summary = main()
        # Exit with error code if any tests failed
        failed_count = sum(1 for r in summary['results'].values() if r['status'] == 'fail')
        sys.exit(0 if failed_count == 0 else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)




















































