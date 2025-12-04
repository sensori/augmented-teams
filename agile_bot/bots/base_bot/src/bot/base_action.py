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
    
    def track_activity_on_start(self):
        self.tracker.track_start(self.bot_name, self.behavior, self.action_name)
    
    def track_activity_on_completion(self, outputs: dict = None, duration: int = None):
        self.tracker.track_completion(self.bot_name, self.behavior, self.action_name, outputs, duration)
    
    def finalize_and_transition(self, next_action: Optional[str] = None):
        class TransitionResult:
            pass
        
        result = TransitionResult()
        result.next_action = next_action
        return result

