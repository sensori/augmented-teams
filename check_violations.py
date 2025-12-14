from agile_bot.bots.base_bot.src.scanners.given_when_then_helpers_scanner import GivenWhenThenHelpersScanner
from pathlib import Path

scanner = GivenWhenThenHelpersScanner()
test_file = Path('agile_bot/bots/base_bot/test/test_validate_knowledge_and_content_against_rules.py')
violations = scanner.scan({'test_files': [str(test_file)]}, None)

print(f'Total violations: {len(violations)}')
print('\nFirst 30 violations:')
for i, v in enumerate(violations[:30], 1):
    print(f"{i}. {v['location']}: {v['violation_message']}")
