from pathlib import Path
from typing import Dict, Any, Optional
from agile_bot.bots.base_bot.src.actions.render.template import Template
from agile_bot.bots.base_bot.src.actions.render.synchronizer import Synchronizer
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths


class RenderSpec:
    def __init__(self, config_data: Dict[str, Any], render_folder: Path, bot_paths: BotPaths, config_file: Path = None):
        self._config_data = config_data.copy()
        self._render_folder = render_folder
        self._bot_paths = bot_paths
        if config_file:
            self._config_data['file'] = str(config_file.relative_to(bot_paths.bot_directory))
        
        # Extract properties from config
        self._input = config_data.get('input')
        self._output = config_data.get('output')
        self._instructions = config_data.get('instructions', [])
        
        # Instantiate Template or Synchronizer based on config
        self._template = None
        self._synchronizer = None
        
        if 'synchronizer' in config_data:
            self._synchronizer = Synchronizer(config_data['synchronizer'])
        elif 'template' in config_data:
            template_path_str = config_data['template']
            # Handle templates/ prefix
            if template_path_str.startswith('templates/'):
                template_path_str = template_path_str[10:]
            
            templates_dir = render_folder / 'templates'
            template_path = templates_dir / template_path_str
            
            if template_path.exists():
                self._template = Template(template_path)
    
    @property
    def input(self) -> Optional[str]:
        return self._input
    
    @property
    def output(self) -> Optional[str]:
        return self._output
    
    @property
    def template(self) -> Optional[Template]:
        return self._template
    
    @property
    def synchronizer(self) -> Optional[Synchronizer]:
        return self._synchronizer
    
    @property
    def instructions(self) -> list:
        return self._instructions
    
    @property
    def config_data(self) -> Dict[str, Any]:
        return self._config_data

