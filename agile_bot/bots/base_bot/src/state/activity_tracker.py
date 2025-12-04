from pathlib import Path
from datetime import datetime
from tinydb import TinyDB, Query


class ActivityTracker:
    
    def __init__(self, workspace_root: Path, bot_name: str):
        self.workspace_root = Path(workspace_root)
        self.bot_name = bot_name
        bot_dir = self.workspace_root / 'agile_bot' / 'bots' / self.bot_name
        self.db_path = bot_dir / 'project_area' / 'activity_log.json'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def track_start(self, bot_name: str, behavior: str, action: str):
        with TinyDB(self.db_path) as db:
            db.insert({
                'action_state': f'{bot_name}.{behavior}.{action}',
                'status': 'started',
                'timestamp': datetime.now().isoformat()
            })
    
    def track_completion(self, bot_name: str, behavior: str, action: str, outputs: dict = None, duration: int = None):
        with TinyDB(self.db_path) as db:
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

