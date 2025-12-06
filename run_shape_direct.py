#!/usr/bin/env python3
"""Direct test of shape behavior"""
import sys
import json
from pathlib import Path

workspace_root = Path(__file__).parent
sys.path.insert(0, str(workspace_root))

from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli

# Create CLI
cli = BaseBotCli(
    bot_name='story_bot',
    bot_config_path=workspace_root / 'agile_bot' / 'bots' / 'story_bot' / 'config' / 'bot_config.json',
    workspace_root=workspace_root
)

# Run shape behavior with input file
print("Running shape behavior...", flush=True)
result = cli.run(
    behavior_name='shape',
    action_name=None,  # Will use current/default action
    increment_file='demo/mob_minion/input.txt'
)

print("\n" + "="*50)
print("RESULT:")
print("="*50)
print(json.dumps(result, indent=2, default=str))
print("="*50)








