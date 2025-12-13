"""Test hyperlink generation for validation reports."""

from pathlib import Path
import sys

# Add repo root to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root / 'agile_bot' / 'bots' / 'base_bot' / 'src'))

from bot.validate_rules_action import ValidateRulesAction

# Create action instance
action = ValidateRulesAction('story_bot', '8_code', repo_root / 'agile_bot' / 'bots' / 'story_bot')

# Test file path - use absolute path
test_file = repo_root / 'agile_bot' / 'bots' / 'base_bot' / 'test' / 'test_generate_bot_server_and_tools.py'
test_location = str(test_file.resolve())
line_number = 774

print(f'Testing with file: {test_location}')
print(f'Line number: {line_number}')
print()

# Test file link generation
link = action._create_file_link(test_location, line_number)
print('File link:', link)
print('Is markdown link:', '[' in link and '](' in link and 'file://' in link)
print()

# Test test info extraction
test_msg = 'Test "test_rules_file_includes_bot_goal_and_behavior_descriptions" appears to test multiple concepts'
test_info = action._extract_test_info(test_msg, test_location, line_number)
print('Original message:', test_msg)
print('Enhanced message:', test_info)
print()

# Test what the final violation line would look like
if test_info:
    violation_line = f"- 🟡 **WARNING** - {link}: {test_info}"
else:
    violation_line = f"- 🟡 **WARNING** - {link}: {test_msg}"
print('Final violation line:')
print(violation_line)
print()

# Test with relative path too
rel_path = 'agile_bot/bots/base_bot/test/test_generate_bot_server_and_tools.py'
rel_link = action._create_file_link(rel_path, line_number)
print('Relative path link:', rel_link)

