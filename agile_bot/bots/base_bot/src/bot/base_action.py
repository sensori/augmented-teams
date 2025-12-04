from pathlib import Path
from typing import Dict, Any, Optional
from agile_bot.bots.base_bot.src.state.activity_tracker import ActivityTracker


class BaseAction:
    
    def __init__(self, bot_name: str, behavior: str, workspace_root: Path, action_name: str):
        self.bot_name = bot_name
        self.behavior = behavior
        self.workspace_root = Path(workspace_root)
        self.action_name = action_name
        self.tracker = ActivityTracker(workspace_root, bot_name)
    
    @property
    def dir(self) -> Path:
        """Get action's bot directory path."""
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
    
    
    def track_activity_on_start(self):
        self.tracker.track_start(self.bot_name, self.behavior, self.action_name)
    
    def track_activity_on_completion(self, outputs: dict = None, duration: int = None):
        self.tracker.track_completion(self.bot_name, self.behavior, self.action_name, outputs, duration)
    
    def execute(self, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Template method that automatically tracks activity. Override do_execute() in subclasses."""
        # Track start
        self.track_activity_on_start()
        
        # Execute action logic (subclass implements this)
        result = self.do_execute(parameters or {})
        
        # Track completion
        self.track_activity_on_completion(outputs=result)
        
        return result
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Override this in subclasses to implement action logic."""
        raise NotImplementedError("Subclasses must implement do_execute()")
    
    def finalize_and_transition(self, next_action: Optional[str] = None):
        class TransitionResult:
            pass
        
        result = TransitionResult()
        result.next_action = next_action
        return result

