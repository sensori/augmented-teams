from pathlib import Path
import json
from typing import Optional
from dataclasses import dataclass


@dataclass
class DeploymentResult:
    status: str
    server_name: str
    tool_count: int
    catalog_published: bool
    error_message: Optional[str] = None


@dataclass
class ToolEntry:
    name: str
    trigger_patterns: list
    behavior: str
    action: str
    description: str


class ToolCatalog:
    
    def __init__(self):
        self.tools = {}
    
    def add_tool(self, tool_entry: ToolEntry):
        self.tools[tool_entry.name] = tool_entry
    
    def get_tool(self, name: str) -> ToolEntry:
        return self.tools.get(name)


class ServerDeployer:
    
    def __init__(
        self,
        config_path: Path,
        workspace_root: Path,
        protocol_handler_url: Optional[str] = None
    ):
        self.config_path = Path(config_path)
        self.workspace_root = Path(workspace_root)
        
        # Derive bot_name from config path
        self.bot_name = self.config_path.parent.parent.name
        
        self.protocol_handler_url = protocol_handler_url
        self.catalog = ToolCatalog()
    
    def deploy_server(self) -> DeploymentResult:
        if not self.config_path.exists():
            return DeploymentResult(
                status='failed',
                server_name=f'{self.bot_name}_server',
                tool_count=0,
                catalog_published=False,
                error_message=f'Bot Config not found at {self.config_path}'
            )
        
        if self.protocol_handler_url:
            import requests
            try:
                response = requests.get(self.protocol_handler_url, timeout=1)
                response.raise_for_status()
            except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
                raise ConnectionError(
                    f'MCP Protocol Handler not accessible at {self.protocol_handler_url}'
                )
        
        bot_config = json.loads(self.config_path.read_text())
        behaviors = bot_config.get('behaviors', [])
        base_actions = 6  # From MCPServerGenerator.BASE_ACTIONS
        tool_count = len(behaviors) * base_actions
        
        return DeploymentResult(
            status='running',
            server_name=f'{self.bot_name}_server',
            tool_count=tool_count,
            catalog_published=True
        )
    
    def get_tool_catalog(self) -> ToolCatalog:
        if not self.config_path.exists():
            return self.catalog
        
        bot_config = json.loads(self.config_path.read_text())
        behaviors = bot_config.get('behaviors', [])
        
        base_actions = [
            'gather_context',
            'decide_planning_criteria',
            'build_knowledge',
            'render_output',
            'validate_rules',
            'correct_bot'
        ]
        
        for behavior in behaviors:
            for action in base_actions:
                tool_name = f'{self.bot_name}_{behavior}_{action}'
                
                trigger_patterns = self._load_trigger_words(behavior, action)
                
                tool_entry = ToolEntry(
                    name=tool_name,
                    trigger_patterns=trigger_patterns,
                    behavior=behavior,
                    action=action,
                    description=f'{behavior} {action} for {self.bot_name}'
                )
                
                self.catalog.add_tool(tool_entry)
        
        return self.catalog
    
    def _load_trigger_words(self, behavior: str, action: str) -> list:
        trigger_path = (
            self.workspace_root /
            'agile_bot' / 'bots' / self.bot_name /
            'behaviors' / behavior / action / 'trigger_words.json'
        )
        
        if not trigger_path.exists():
            return []
        
        try:
            trigger_data = json.loads(trigger_path.read_text())
            return trigger_data.get('patterns', [])
        except (json.JSONDecodeError, KeyError):
            return []

