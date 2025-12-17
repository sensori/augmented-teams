from pathlib import Path
from datetime import datetime
from tinydb import TinyDB
from typing import Optional
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths


class ActivityTracker:
    def __init__(self, bot_paths: BotPaths, bot_name: str):
        self._bot_paths = bot_paths
        self.bot_name = bot_name
    
    @property
    def workspace_dir(self) -> Path:
        return self._bot_paths.workspace_directory

    @property
    def file(self) -> Path:
        return self._bot_paths.workspace_directory / 'activity_log.json'
    
    def track_start(self, bot_name: str, behavior: str, action: str):
        self.file.parent.mkdir(parents=True, exist_ok=True)
        with TinyDB(self.file) as db:
            db.insert({
                'action_state': f'{bot_name}.{behavior}.{action}',
                'status': 'started',
                'timestamp': datetime.now().isoformat()
            })
    
    def track_completion(self, bot_name: str, behavior: str, action: str, outputs: dict = None, duration: int = None):
        self.file.parent.mkdir(parents=True, exist_ok=True)
        with TinyDB(self.file) as db:
            entry = {
                'action_state': f'{bot_name}.{behavior}.{action}',
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            }
            if outputs:
                entry['outputs'] = outputs
            if duration:
                entry['duration'] = duration
            db.insert(entry)
