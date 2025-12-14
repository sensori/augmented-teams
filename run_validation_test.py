"""Run test validation to verify two-pass system."""
import os
import sys
from pathlib import Path

repo_root = Path(__file__).parent
base_bot_dir = repo_root / 'agile_bot' / 'bots' / 'base_bot'
sys.path.insert(0, str(repo_root))
os.environ['WORKING_AREA'] = str(base_bot_dir.resolve())

from agile_bot.bots.base_bot.src.bot.test_validate_action import TestValidateAction

def main():
    print("=" * 60)
    print("Running Test Validation - Two-Pass System Test")
    print("=" * 60)
    
    bot_dir = base_bot_dir / 'src'
    action = TestValidateAction('base_bot', '7_write_tests', bot_dir)
    
    # Test with one file first
    test_file = base_bot_dir / 'test' / 'test_generate_bot_server_and_tools.py'
    print(f"\nTesting with: {test_file.name}")
    
    result = action.do_execute({'test_files': [str(test_file)]})
    
    print(f"\nStatus: {result.get('status', 'unknown')}")
    
    instructions = result.get('instructions', {})
    rules = instructions.get('validation_rules', [])
    print(f"\nTotal rules processed: {len(rules)}")
    
    # Check two-pass format
    two_pass_rules = []
    single_pass_rules = []
    
    for rule in rules:
        scanner_results = rule.get('scanner_results', {})
        rule_name = Path(rule.get('rule_file', 'unknown')).stem
        
        if 'file_by_file' in scanner_results or 'cross_file' in scanner_results:
            two_pass_rules.append((rule_name, scanner_results))
        elif 'violations' in scanner_results:
            single_pass_rules.append((rule_name, scanner_results))
    
    print(f"\nTwo-pass scanners: {len(two_pass_rules)}")
    print(f"Single-pass scanners: {len(single_pass_rules)}")
    
    # Count violations
    total_file_by_file = 0
    total_cross_file = 0
    
    for rule_name, scanner_results in two_pass_rules:
        file_by_file = scanner_results.get('file_by_file', {}).get('violations', [])
        cross_file = scanner_results.get('cross_file', {}).get('violations', [])
        total_file_by_file += len(file_by_file)
        total_cross_file += len(cross_file)
        
        if file_by_file or cross_file:
            print(f"\n  {rule_name}:")
            print(f"    File-by-file: {len(file_by_file)} violations")
            print(f"    Cross-file: {len(cross_file)} violations")
    
    print(f"\n" + "=" * 60)
    print(f"Summary:")
    print(f"  File-by-file violations: {total_file_by_file}")
    print(f"  Cross-file violations: {total_cross_file}")
    print(f"  Total: {total_file_by_file + total_cross_file}")
    print("=" * 60)
    
    # Check report
    report_path = base_bot_dir / 'docs' / 'stories' / 'validation-report.md'
    if report_path.exists():
        print(f"\nReport generated: {report_path}")
    else:
        print("\nNo report found")

if __name__ == '__main__':
    main()



