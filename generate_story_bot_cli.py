"""Generate CLI files for story_bot."""
import sys
from pathlib import Path

# Add workspace root to Python path
workspace_root = Path(__file__).parent
sys.path.insert(0, str(workspace_root))

from agile_bot.bots.base_bot.src.cli.cli_generator import CliGenerator

print("Generating CLI files for story_bot...")
generator = CliGenerator(
    workspace_root=workspace_root,
    bot_location='agile_bot/bots/story_bot'
)

artifacts = generator.generate_cli_code()

print('\nGenerated CLI files:')
print(f'  Python CLI: {artifacts["cli_python"]}')
print(f'  Bash script: {artifacts["cli_script"]}')
print(f'  PowerShell script: {artifacts["cli_powershell"]}')

print('\nGenerated Cursor Commands:')
cursor_commands = artifacts.get('cursor_commands', {})
if cursor_commands:
    for cmd_name, cmd_path in sorted(cursor_commands.items()):
        print(f'  {cmd_name}: {cmd_path}')
    print(f'\nTotal: {len(cursor_commands)} cursor command files')
else:
    print('  No cursor commands generated')

