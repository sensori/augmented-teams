#!/usr/bin/env python3
"""Run validate_rules action for base_bot"""

import sys
import os
from pathlib import Path

# Add workspace root to path (go up from agile_bot/bots/base_bot to workspace root)
workspace_root = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.insert(0, str(workspace_root))

# Set WORKING_AREA environment variable BEFORE importing bot modules
# WORKING_AREA should point to the project directory (where docs/stories/ is)
project_dir = workspace_root / 'agile_bot' / 'bots' / 'base_bot'
os.environ['WORKING_AREA'] = str(project_dir.resolve())

from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction

def main():
    import sys
    
    # Use story_bot for write_tests behavior (has 27 rules with scanners)
    workspace_root = Path(__file__).parent.parent.parent.parent.resolve()
    bot_directory = workspace_root / 'agile_bot' / 'bots' / 'story_bot'
    bot_name = 'story_bot'
    behavior = '7_write_tests'  # This behavior has rules with scanners
    
    # Collect test files from base_bot/test
    base_bot_test_dir = workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'test'
    test_files = []
    if base_bot_test_dir.exists():
        test_files = [str(f) for f in base_bot_test_dir.glob('test_*.py')]
        print(f"Found {len(test_files)} test files to validate")
    
    print(f"Initializing ValidateRulesAction...")
    print(f"Bot: {bot_name}")
    print(f"Behavior: {behavior}")
    print(f"Bot Directory: {bot_directory}")
    print(f"Test Files: {len(test_files)} files")
    
    action = ValidateRulesAction(
        bot_name=bot_name,
        behavior=behavior,
        bot_directory=bot_directory
    )
    
    print("\nExecuting validate_rules action...")
    try:
        parameters = {
            'test_files': test_files
        }
        
        result = action.do_execute(parameters=parameters)
        print("\n[OK] Validation completed successfully!")
        print(f"Result keys: {list(result.keys())}")
        
        # Show rule count
        instructions = result.get('instructions', {})
        validation_rules = instructions.get('validation_rules', [])
        print(f"\nRules executed: {len(validation_rules)}")
        
        return 0
    except Exception as e:
        print(f"\n[ERROR] Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

