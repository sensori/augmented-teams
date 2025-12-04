from pathlib import Path
from datetime import datetime
from tinydb import TinyDB, Query


class ActivityTracker:
    
    def __init__(self, workspace_root: Path, bot_name: str):
        self.workspace_root = Path(workspace_root)
        self.bot_name = bot_name
        # Don't create directory in __init__, create it when actually writing
    
    @property
    def dir(self) -> Path:
        """Get tracker's bot directory path."""
        return self.workspace_root / 'agile_bot' / 'bots' / self.bot_name
    
    @property
    def current_project_file(self) -> Path:
        """Get current_project.json file path."""
        return self.dir / 'current_project.json'
    
    @property
    def current_project(self) -> Path:
        """Get current project directory."""
        if self.current_project_file.exists():
            try:
                import json
                project_data = json.loads(self.current_project_file.read_text(encoding='utf-8'))
                return Path(project_data.get('current_project', ''))
            except Exception:
                pass
        return self.workspace_root
    
    @property
    def project_location(self) -> Path:
        """Get project location (same as current_project for clarity)."""
        return self.current_project
    
    @property
    def file(self) -> Path:
        """Get activity log file path."""
        return self.project_location / 'activity_log.json'
    
    def track_start(self, bot_name: str, behavior: str, action: str):
        # Don't write if current_project not set
        if not self.current_project_file.exists():
            # Silently skip - project not initialized yet
            return
        
        # Ensure directory exists before writing
        self.file.parent.mkdir(parents=True, exist_ok=True)
        with TinyDB(self.file) as db:
            db.insert({
                'action_state': f'{bot_name}.{behavior}.{action}',
                'status': 'started',
                'timestamp': datetime.now().isoformat()
            })
    
    def track_completion(self, bot_name: str, behavior: str, action: str, outputs: dict = None, duration: int = None):
        # Don't write if current_project not set
        if not self.current_project_file.exists():
            # Silently skip - project not initialized yet
            return
        
        # Ensure directory exists before writing
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

