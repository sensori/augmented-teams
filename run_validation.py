"""Run validation to generate report with hyperlinks."""

import os
import sys
from pathlib import Path

# Set WORKING_AREA before importing bot modules
os.environ['WORKING_AREA'] = str(Path(__file__).parent / 'agile_bot' / 'bots' / 'base_bot')

# Add to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root / 'agile_bot' / 'bots' / 'base_bot' / 'src'))

from bot.bot import Bot

# Initialize bot
bot_directory = repo_root / 'agile_bot' / 'bots' / 'story_bot'
config_path = bot_directory / 'config' / 'bot_config.json'

if not config_path.exists():
    # Try alternative location
    config_path = bot_directory / 'bot_config.json'

bot = Bot('story_bot', bot_directory, config_path)

# Run validation with test files
test_file = repo_root / 'agile_bot' / 'bots' / 'base_bot' / 'test' / 'test_generate_bot_server_and_tools.py'
parameters = {
    'test_files': [str(test_file)],
    'code_files': [str(test_file)]
}

print(f'Running validation on: {test_file}')
result = bot.validate_rules(parameters)

print(f'\nValidation completed!')
print(f'Status: {result.status}')
print(f'Report path: {result.data.get("report_path", "N/A")}')

# Check if report was generated
report_path = result.data.get('report_path')
if report_path and Path(report_path).exists():
    print(f'\nReport generated at: {report_path}')
    # Check for hyperlinks
    report_content = Path(report_path).read_text(encoding='utf-8')
    has_hyperlinks = '](' in report_content and 'file://' in report_content
    print(f'Report contains hyperlinks: {has_hyperlinks}')
    
    # Show a sample of violations
    lines = report_content.split('\n')
    violation_lines = [l for l in lines if 'WARNING' in l or 'ERROR' in l][:5]
    if violation_lines:
        print('\nSample violation lines:')
        for line in violation_lines:
            print(f'  {line[:100]}...' if len(line) > 100 else f'  {line}')
else:
    print('\nNo report path found in result')

