"""Run test validation action to verify two-pass system."""
import os
import sys
from pathlib import Path

# Set up paths
repo_root = Path(__file__).parent
base_bot_dir = repo_root / 'agile_bot' / 'bots' / 'base_bot'
sys.path.insert(0, str(repo_root))

# Set working area
os.environ['WORKING_AREA'] = str(base_bot_dir.resolve())

from agile_bot.bots.base_bot.src.bot.test_validate_action import TestValidateAction
from agile_bot.bots.base_bot.src.utils import read_json_file

def main():
    print("=" * 60)
    print("Running Test Validation Action")
    print("=" * 60)
    
    bot_dir = base_bot_dir / 'src'
    
    # Find story graph
    story_graph_path = base_bot_dir / 'docs' / 'stories' / 'story-graph.json'
    if not story_graph_path.exists():
        print(f"ERROR: Story graph not found at {story_graph_path}")
        print("Please run build_knowledge action first.")
        return
    
    # Find all test files
    test_dir = base_bot_dir / 'test'
    test_files = list(test_dir.glob('test_*.py'))
    
    print(f"Found {len(test_files)} test files")
    print(f"Story graph: {story_graph_path}")
    print()
    
    # Create action
    action = TestValidateAction('base_bot', '7_write_tests', bot_dir)
    
    # Run validation
    print("Executing test_validate action...")
    try:
        parameters = {
            'test_files': [str(tf) for tf in test_files[:5]]  # Test with first 5 files
        }
        
        result = action.do_execute(parameters)
        
        print(f"\nStatus: {result.get('status', 'unknown')}")
        
        if 'instructions' in result:
            instructions = result['instructions']
            if 'validation_rules' in instructions:
                rules = instructions['validation_rules']
                print(f"\nFound {len(rules)} validation rules")
                
                # Check for two-pass format
                two_pass_count = 0
                single_pass_count = 0
                total_file_by_file = 0
                total_cross_file = 0
                
                for rule in rules:
                    scanner_results = rule.get('scanner_results', {})
                    rule_name = Path(rule.get('rule_file', 'unknown')).stem
                    
                    if 'file_by_file' in scanner_results or 'cross_file' in scanner_results:
                        two_pass_count += 1
                        file_by_file = scanner_results.get('file_by_file', {}).get('violations', [])
                        cross_file = scanner_results.get('cross_file', {}).get('violations', [])
                        total_file_by_file += len(file_by_file)
                        total_cross_file += len(cross_file)
                        if file_by_file or cross_file:
                            print(f"  - {rule_name}: {len(file_by_file)} file-by-file, {len(cross_file)} cross-file violations")
                    elif 'violations' in scanner_results:
                        single_pass_count += 1
                
                print(f"\nTwo-pass scanners: {two_pass_count}")
                print(f"Single-pass scanners: {single_pass_count}")
                print(f"Total file-by-file violations: {total_file_by_file}")
                print(f"Total cross-file violations: {total_cross_file}")
        
        # Check for report
        report_path = base_bot_dir / 'docs' / 'stories' / 'validation-report.md'
        if report_path.exists():
            print(f"\nValidation report generated: {report_path}")
        else:
            print("\nNo validation report found")
        
        print("\n" + "=" * 60)
        print("Test validation completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()



