from pathlib import Path
import tempfile
from agile_bot.bots.base_bot.src.bot.behavior import Behavior
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths

tmp = Path(tempfile.mkdtemp())
bot_dir = tmp / 'agile_bot' / 'bots' / 'test_bot'
(bot_dir / 'behaviors' / '1_exploration').mkdir(parents=True)
(bot_dir / 'behaviors' / '1_exploration' / 'behavior.json').write_text('{}')
(bot_dir / 'behaviors' / '1_exploration' / 'guardrails' / 'required_context').mkdir(parents=True)
(bot_dir / 'behaviors' / '1_exploration' / 'guardrails' / 'required_context' / 'key_questions.json').write_text('{"questions": []}')

bot_paths = BotPaths(bot_directory=bot_dir)
behavior = Behavior('exploration', 'test_bot', bot_paths)
print('behavior_config.behavior_directory:', behavior.behavior_config.behavior_directory)
print('guardrails._behavior_config.behavior_directory:', behavior.guardrails._behavior_config.behavior_directory)

