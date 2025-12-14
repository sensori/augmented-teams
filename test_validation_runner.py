"""Test script to run test_validate action and verify two-pass system."""
import os
import sys
from pathlib import Path

# Set up paths
repo_root = Path(__file__).parent
base_bot_dir = repo_root / 'agile_bot' / 'bots' / 'base_bot'
sys.path.insert(0, str(repo_root))

# Set working area
os.environ['WORKING_AREA'] = str(base_bot_dir.resolve())

from agile_bot.bots.base_bot.src.bot.bot import Bot

def main():
    print("=" * 60)
    print("Running Test Validation Action")
    print("=" * 60)
    
    # Create a temporary bot config for testing
    import tempfile
    import json
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        bot_dir = tmp_path / 'bot'
        bot_dir.mkdir()
        config_dir = bot_dir / 'config'
        config_dir.mkdir()
        
        config_path = config_dir / 'bot_config.json'
        config_data = {
            "bot_name": "base_bot",
            "goal": "Test validation",
            "behaviors": ["7_write_tests"]
        }
        config_path.write_text(json.dumps(config_data, indent=2))
        
        bot = Bot(
            bot_name='base_bot',
            bot_directory=bot_dir,
            config_path=config_path
        )
    
    print(f"Bot initialized: {bot.bot_name}")
    print(f"Working directory: {os.environ.get('WORKING_AREA')}")
    print()
    
    # Run test_validate action
    print("Executing test_validate action...")
    try:
        result = bot.execute_behavior('7_write_tests', 'test_validate', {})
        
        print(f"\nStatus: {result.status}")
        print(f"Behavior: {result.behavior}")
        print(f"Action: {result.action}")
        
        if result.data:
            print(f"\nResult data keys: {list(result.data.keys())}")
            
            # Check for instructions
            if 'instructions' in result.data:
                instructions = result.data['instructions']
                if 'validation_rules' in instructions:
                    rules = instructions['validation_rules']
                    print(f"\nFound {len(rules)} validation rules")
                    
                    # Check for two-pass format
                    two_pass_count = 0
                    single_pass_count = 0
                    
                    for rule in rules[:5]:  # Check first 5 rules
                        scanner_results = rule.get('scanner_results', {})
                        if 'file_by_file' in scanner_results or 'cross_file' in scanner_results:
                            two_pass_count += 1
                            file_by_file = scanner_results.get('file_by_file', {}).get('violations', [])
                            cross_file = scanner_results.get('cross_file', {}).get('violations', [])
                            rule_name = Path(rule.get('rule_file', 'unknown')).stem
                            print(f"  - {rule_name}: {len(file_by_file)} file-by-file, {len(cross_file)} cross-file violations")
                        elif 'violations' in scanner_results:
                            single_pass_count += 1
                    
                    print(f"\nTwo-pass scanners: {two_pass_count}")
                    print(f"Single-pass scanners: {single_pass_count}")
        
        print("\n" + "=" * 60)
        print("Test validation completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

