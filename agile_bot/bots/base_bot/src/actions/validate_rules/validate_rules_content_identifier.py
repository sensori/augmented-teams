from pathlib import Path
from typing import Dict, Any, Optional
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths


class ContentIdentifier:
    """Identifies content to validate from the project workspace.
    
    Finds rendered outputs, clarification files, planning files, and sets report path.
    """
    
    def __init__(self, bot_paths: BotPaths, bot_name: str, behavior: str):
        """Initialize ContentIdentifier.
        
        Args:
            bot_paths: BotPaths instance for accessing paths
            bot_name: Name of the bot
            behavior: Name of the behavior
        """
        self._bot_paths = bot_paths
        self.bot_name = bot_name
        self.behavior = behavior
    
    def identify_content(self) -> Dict[str, Any]:
        """Identify what content needs to be validated from the project.
        
        Returns:
            Dictionary with workspace, rendered_outputs, clarification_file,
            planning_file, and report_path
        """
        workspace_directory = self._bot_paths.workspace_directory
        content_info = {
            'workspace': str(workspace_directory),
            'rendered_outputs': [],
            'clarification_file': None,
            'planning_file': None,
            'report_path': None
        }
        
        docs_path = self._bot_paths.documentation_path
        docs_dir = workspace_directory / docs_path
        
        self._find_clarification_and_planning(docs_dir, content_info)
        self._set_report_path(docs_dir, content_info)
        self._find_rendered_outputs(docs_dir, content_info)
        
        return content_info
    
    
    def _find_clarification_and_planning(self, docs_dir: Path, content_info: Dict[str, Any]) -> None:
        """Find clarification.json and planning.json files."""
        clarification_file = docs_dir / 'clarification.json'
        planning_file = docs_dir / 'planning.json'
        
        if clarification_file.exists():
            content_info['clarification_file'] = str(clarification_file)
        if planning_file.exists():
            content_info['planning_file'] = str(planning_file)
    
    def _set_report_path(self, docs_dir: Path, content_info: Dict[str, Any]) -> None:
        """Set validation report path."""
        report_file = docs_dir / 'validation-report.md'
        content_info['report_path'] = str(report_file)
    
    def _find_rendered_outputs(self, docs_dir: Path, content_info: Dict[str, Any]) -> None:
        """Find rendered outputs (story maps, domain models, etc.)."""
        if not docs_dir.exists():
            return
        
        rendered_patterns = [
            '*-story-map.md',
            '*-domain-model-description.md',
            '*-domain-model-diagram.md',
            'story-graph.json',
            '*-increments.md'
        ]
        for pattern in rendered_patterns:
            for file_path in docs_dir.glob(pattern):
                content_info['rendered_outputs'].append(str(file_path))
