from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import importlib
import logging
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.actions.action import Action
from agile_bot.bots.base_bot.src.actions.render_output.render_spec import RenderSpec

logger = logging.getLogger(__name__)


class RenderOutputAction(Action):
    """Render output action for rendering outputs.
    
    Domain Model:
        Instantiated with: Behavior
        Properties: render_specs, templates, synchronizers
    """
    
    def __init__(self, base_action_config=None, behavior=None, activity_tracker=None,
                 bot_name: str = None, action_name: str = 'render_output'):
        """Initialize RenderOutputAction.
        
        Domain Model: Instantiated with: Behavior
        """
        super().__init__(base_action_config=base_action_config, behavior=behavior,
                        activity_tracker=activity_tracker, bot_name=bot_name, action_name=action_name)
        
        # Load render specs from behavior folder
        self._render_specs: List[RenderSpec] = []
        self._load_render_specs()
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute render_output action logic."""
        # Get merged instructions from base class
        instructions = self.instructions.copy()
        
        # Load render-specific data (render_instructions and render_configs)
        behavior_folder = self.behavior.folder if self.behavior else None
        render_instructions = self._load_render_instructions(behavior_folder)
        render_configs = self._load_render_configs(behavior_folder)
        
        # Inject render-specific data into instructions
        self._inject_render_data(instructions, render_instructions, render_configs)
        
        return {'instructions': instructions}
    
    def _find_render_folder(self, behavior_folder: Path) -> Optional[Path]:
        """Find render folder using *_content/*_render pattern."""
        if not behavior_folder or not behavior_folder.exists():
            return None
        
        content_dirs = list(behavior_folder.glob('*_content'))
        for content_dir in content_dirs:
            if content_dir.is_dir():
                render_dirs = list(content_dir.glob('*_render'))
                for render_dir in render_dirs:
                    if render_dir.is_dir():
                        return render_dir
        return None
    
    def _load_render_instructions(self, behavior_folder: Optional[Path]) -> Optional[Dict[str, Any]]:
        """Load instructions.json from render folder if it exists."""
        render_folder = self._find_render_folder(behavior_folder)
        if not render_folder:
            return None
        
        instructions_path = render_folder / 'instructions.json'
        if instructions_path.exists():
            try:
                return read_json_file(instructions_path)
            except Exception as e:
                logger.error(f'Failed to load render instructions from {instructions_path}: {e}')
                return None
        return None
    
    def _load_render_specs(self):
        """Load render specs from behavior folder."""
        behavior_folder = self.behavior.folder if self.behavior else None
        render_folder = self._find_render_folder(behavior_folder)
        
        if not render_folder:
            return
        
        render_json_files = [f for f in render_folder.glob('*.json') if f.name != 'instructions.json']
        
        for render_json_file in render_json_files:
            try:
                config_data = read_json_file(render_json_file)
                render_spec = RenderSpec(config_data, render_folder, self.bot_directory, render_json_file)
                self._render_specs.append(render_spec)
            except Exception as e:
                logger.warning(f'Skipping unreadable render JSON file {render_json_file}: {e}')
    
    @property
    def render_specs(self) -> List[RenderSpec]:
        """Get render specs.
        
        Domain Model: render_specs
        """
        return self._render_specs
    
    @property
    def templates(self) -> List:
        """Get templates.
        
        Domain Model: templates
        """
        templates = []
        for spec in self._render_specs:
            if spec.template:
                templates.append(spec.template)
        return templates
    
    @property
    def synchronizers(self) -> List:
        """Get synchronizers.
        
        Domain Model: synchronizers
        """
        synchronizers = []
        for spec in self._render_specs:
            if spec.synchronizer:
                synchronizers.append(spec.synchronizer)
        return synchronizers
    
    def _load_render_configs(self, behavior_folder: Optional[Path]) -> List[Dict[str, Any]]:
        """Load all render JSON configuration files from render folder."""
        render_folder = self._find_render_folder(behavior_folder)
        if not render_folder:
            return []
        
        render_configs = []
        render_json_files = [f for f in render_folder.glob('*.json') if f.name != 'instructions.json']
        
        for render_json_file in render_json_files:
            try:
                render_config = self._load_single_render_config(render_json_file, render_folder)
                if render_config:
                    render_configs.append(render_config)
            except Exception as e:
                logger.warning(f'Skipping unreadable render JSON file {render_json_file}: {e}')
        
        return render_configs
    
    def _load_single_render_config(self, render_json_file: Path, render_folder: Path) -> Optional[Dict[str, Any]]:
        """Load a single render JSON configuration file."""
        try:
            config = read_json_file(render_json_file)
        except json.JSONDecodeError as e:
            logger.warning(f'Invalid JSON in {render_json_file}: {e}')
            return None
        
        config_entry = {
            'file': str(render_json_file.relative_to(self.bot_directory)),
            'config': config
        }
        
        if 'synchronizer' in config:
            if not self._verify_synchronizer_class(config['synchronizer']):
                logger.warning(f'Render config {render_json_file.name}: synchronizer class {config["synchronizer"]} cannot be verified')
        elif 'template' in config:
            template_content = self._load_template_file(render_folder, config['template'])
            if template_content is not None:
                config_entry['template'] = template_content
        
        return config_entry
    
    def _verify_synchronizer_class(self, synchronizer_class_path: str) -> bool:
        """Verify synchronizer class exists and has render method."""
        try:
            module_path, class_name = synchronizer_class_path.rsplit('.', 1)
            
            module = None
            possible_paths = [
                module_path,
                f'agile_bot.bots.{self.bot_name}.src.{module_path}',
                f'agile_bot.bots.{self.bot_name}.src.synchronizers.{module_path}',
            ]
            
            for path in possible_paths:
                try:
                    module = importlib.import_module(path)
                    if hasattr(module, class_name):
                        break
                    module = None
                except ImportError:
                    continue
            
            if module is None:
                logger.warning(f'Cannot import synchronizer module for {synchronizer_class_path}')
                return False
            
            synchronizer_class = getattr(module, class_name)
            
            has_render = hasattr(synchronizer_class, 'render')
            has_sync_methods = any(
                hasattr(synchronizer_class, method)
                for method in ['synchronize_outline', 'synchronize_increments', 'synchronize_exploration']
            )
            
            return has_render or has_sync_methods
        except (AttributeError, ValueError) as e:
            logger.warning(f'Cannot verify synchronizer class {synchronizer_class_path}: {e}')
            return False
    
    def _load_template_file(self, render_folder: Path, template_path: str) -> Optional[str]:
        """Load template file content from templates folder."""
        if not template_path:
            return None
        
        templates_dir = render_folder / 'templates'
        
        if template_path.startswith('templates/'):
            template_path = template_path[10:]
        
        template_file = templates_dir / template_path
        
        if not template_file.exists():
            logger.warning(f'Template file not found: {template_file}')
            return None
        
        try:
            return template_file.read_text(encoding='utf-8')
        except Exception as e:
            logger.warning(f'Failed to read template file {template_file}: {e}')
            return None
    
    def _inject_render_data(self, instructions: Dict[str, Any], render_instructions: Optional[Dict[str, Any]], render_configs: List[Dict[str, Any]]) -> None:
        """Inject render-specific data into instructions dict."""
        base_instructions_list = instructions.get('base_instructions', []).copy()
        
        # Add workspace path information to instructions
        workspace_path = self.working_dir
        if workspace_path and workspace_path != self.bot_directory:
            workspace_info = f"\n**WORKSPACE PATH: {workspace_path}**\nAll render outputs must be written to paths relative to this workspace path, NOT to the bot's own directories."
            base_instructions_list.insert(0, workspace_info)
        
        # Inject render_instructions and render_configs template variables
        self._inject_render_template_variables(base_instructions_list, render_instructions, render_configs)
        
        # Update instructions dict
        instructions['base_instructions'] = base_instructions_list
        
        # Add render-specific data to instructions dict
        if render_instructions:
            instructions['render_instructions'] = render_instructions
        
        if render_configs:
            instructions['render_configs'] = render_configs
        
        if workspace_path and workspace_path != self.bot_directory:
            instructions['workspace_path'] = str(workspace_path)
    
    def _inject_render_template_variables(self, instructions_list: List[str], render_instructions: Optional[Dict[str, Any]], render_configs: List[Dict[str, Any]]) -> None:
        """Inject render_instructions and render_configs template variables into instructions."""
        render_instructions_text = ''
        if render_instructions:
            render_instructions_text = '\n'.join(render_instructions.get('instructions', []))
        
        # Format render configs for injection
        render_configs_text = self._format_render_configs(render_configs)
        
        # Replace template variables
        new_instructions = []
        for line in instructions_list:
            if '{{render_instructions}}' in line:
                if render_instructions_text:
                    # Split instructions into lines and insert them
                    instructions_lines = render_instructions_text.split('\n')
                    new_instructions.extend(instructions_lines)
                else:
                    new_instructions.append(line.replace('{{render_instructions}}', 'Follow behavior-specific render instructions'))
            elif '{{render_configs}}' in line:
                if render_configs_text:
                    # Split configs into lines and insert them
                    configs_lines = render_configs_text.split('\n')
                    new_instructions.extend(configs_lines)
                else:
                    new_instructions.append(line.replace('{{render_configs}}', 'No render configurations found'))
            else:
                new_instructions.append(line)
        
        instructions_list[:] = new_instructions
    
    def _format_render_configs(self, render_configs: List[Dict[str, Any]]) -> str:
        """Format render configs into readable text for injection."""
        if not render_configs:
            return "No render configurations found."
        
        formatted_parts = []
        formatted_parts.append("**Render Configurations:**")
        formatted_parts.append("")
        
        for i, render_config in enumerate(render_configs, 1):
            config = render_config.get('config', {})
            config_name = config.get('name', f'config_{i}')
            config_file = render_config.get('file', 'unknown')
            
            formatted_parts.append(f"{i}. **{config_name}** ({config_file})")
            
            # Always show instructions first (if present)
            if 'instructions' in config:
                instructions = config.get('instructions', '')
                if isinstance(instructions, str):
                    formatted_parts.append(f"   - Instructions: {instructions}")
                elif isinstance(instructions, list):
                    formatted_parts.append(f"   - Instructions:")
                    for inst in instructions:
                        formatted_parts.append(f"     * {inst}")
            
            # Show execution method fields
            if 'synchronizer' in config:
                synchronizer = config.get('synchronizer', 'N/A')
                formatted_parts.append(f"   - Synchronizer: {synchronizer}")
                if 'renderer_command' in config:
                    renderer_cmd = config.get('renderer_command', 'N/A')
                    formatted_parts.append(f"   - Renderer Command: {renderer_cmd}")
            elif 'template' in config:
                template = config.get('template', 'N/A')
                formatted_parts.append(f"   - Template: {template}")
            
            # Show input and output fields
            if 'input' in config:
                formatted_parts.append(f"   - Input: {config.get('input', 'N/A')}")
            if 'output' in config:
                formatted_parts.append(f"   - Output: {config.get('output', 'N/A')}")
            
            # Show path if present
            if 'path' in config:
                formatted_parts.append(f"   - Path: {config.get('path', 'N/A')}")
            
            formatted_parts.append("")
        
        return '\n'.join(formatted_parts)
    
    
    def inject_next_action_instructions(self):
        return "Proceed to validate_rules action"
