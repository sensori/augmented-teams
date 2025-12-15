"""
RenderSpec class.

Represents a single render specification with input, output, template, synchronizer, and instructions.
"""
from pathlib import Path
from typing import Dict, Any, Optional
from agile_bot.bots.base_bot.src.actions.render_output.template import Template
from agile_bot.bots.base_bot.src.actions.render_output.synchronizer import Synchronizer


class RenderSpec:
    """Render specification for rendering output.
    
    Domain Model:
        Properties: input, output, template, synchronizer, instructions
    """
    
    def __init__(self, config_data: Dict[str, Any], render_folder: Path, bot_directory: Path, config_file: Path = None):
        """Initialize RenderSpec.
        
        Args:
            config_data: Render config dictionary
            render_folder: Path to render folder
            bot_directory: Path to bot directory
            config_file: Path to config file (optional, for file path tracking)
        """
        self._config_data = config_data.copy()
        self._render_folder = render_folder
        self._bot_directory = bot_directory
        if config_file:
            self._config_data['file'] = str(config_file.relative_to(bot_directory))
        
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
        """Get input path.
        
        Domain Model: input
        """
        return self._input
    
    @property
    def output(self) -> Optional[str]:
        """Get output path.
        
        Domain Model: output
        """
        return self._output
    
    @property
    def template(self) -> Optional[Template]:
        """Get template.
        
        Domain Model: template
        """
        return self._template
    
    @property
    def synchronizer(self) -> Optional[Synchronizer]:
        """Get synchronizer.
        
        Domain Model: synchronizer
        """
        return self._synchronizer
    
    @property
    def instructions(self) -> list:
        """Get instructions.
        
        Domain Model: instructions
        """
        return self._instructions
    
    @property
    def config_data(self) -> Dict[str, Any]:
        """Get full config data."""
        return self._config_data

