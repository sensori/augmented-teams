from pathlib import Path
from typing import Dict, Any
from agile_bot.bots.base_bot.src.utils import read_json_file


class ContentIdentifier:
    """Identifies content to validate from the project workspace.
    
    Finds rendered outputs, clarification files, planning files, and sets report path.
    """
    
    def __init__(self, bot_directory: Path, bot_name: str, behavior: str, workspace_directory: Path):
        """Initialize ContentIdentifier.
        
        Args:
            bot_directory: Directory where bot code lives
            bot_name: Name of the bot
            behavior: Name of the behavior
            workspace_directory: Workspace directory where content files are located
        """
        self.bot_directory = bot_directory
        self.bot_name = bot_name
        self.behavior = behavior
        self.workspace_directory = workspace_directory
    
    def identify_content(self) -> Dict[str, Any]:
        """Identify what content needs to be validated from the project.
        
        Returns:
            Dictionary with project_location, rendered_outputs, clarification_file,
            planning_file, and report_path
        """
        project_dir = self.workspace_directory
        content_info = {
            'project_location': str(project_dir),
            'rendered_outputs': [],
            'clarification_file': None,
            'planning_file': None,
            'report_path': None
        }
        
        docs_path = self._find_docs_path()
        docs_dir = project_dir / docs_path
        
        self._find_clarification_and_planning(docs_dir, content_info)
        self._set_report_path(docs_dir, content_info)
        self._find_rendered_outputs(docs_dir, content_info)
        
        return content_info
    
    def _find_docs_path(self) -> str:
        """Find docs_path from behavior config or default to 'docs/stories'."""
        try:
            from agile_bot.bots.base_bot.src.bot.bot import Behavior
            behavior_folder = Behavior.find_behavior_folder(
                self.bot_directory,
                self.bot_name,
                self.behavior
            )
            # Try to find config that specifies docs_path from behavior.json (new format)
            behavior_file = behavior_folder / 'behavior.json'
            if behavior_file.exists():
                behavior_data = read_json_file(behavior_file)
                return behavior_data.get('docs_path', 'docs/stories')
            else:
                # Fallback to old format for backward compatibility
                config_file = behavior_folder / 'instructions.json'
                if config_file.exists():
                    config_data = read_json_file(config_file)
                    return config_data.get('docs_path', 'docs/stories')
        except FileNotFoundError:
            pass
        
        return 'docs/stories'
    
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
