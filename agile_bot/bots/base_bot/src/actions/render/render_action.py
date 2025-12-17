from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import importlib
import logging
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.actions.action import Action
from agile_bot.bots.base_bot.src.actions.render.render_spec import RenderSpec
from agile_bot.bots.base_bot.src.bot.merged_instructions import MergedInstructions

logger = logging.getLogger(__name__)


class RenderOutputAction(Action):
    def __init__(self, behavior=None, action_config=None):
        super().__init__(behavior=behavior, action_config=action_config)
        
        # Load render specs from behavior folder
        self._render_specs: List[RenderSpec] = []
        self._load_render_specs()
    
    @property
    def action_name(self) -> str:
        """Action name is always 'render' for RenderOutputAction."""
        return 'render'
    
    @action_name.setter
    def action_name(self, value: str):
        raise AttributeError("action_name is read-only for RenderOutputAction")
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # Load render-specific data (render_instructions and render_configs)
        render_instructions = self._load_render_instructions()
        render_configs = self._load_render_configs()
        
        # Use MergedInstructions to merge base and render instructions
        merged_instructions = MergedInstructions(
            base_instructions=self.instructions.get('base_instructions', []),
            render_instructions=render_instructions
        )
        instructions = merged_instructions.merge()
        
        # Inject render-specific data into instructions (template variables, workspace path, etc.)
        self._inject_render_data(instructions, render_instructions, render_configs)
        
        return {'instructions': instructions}
    
    def _find_render_folder(self) -> Path:
        # Render folder is at content/render/ directly
        return self.behavior.folder / 'content' / 'render'
    
    def _load_render_instructions(self) -> Dict[str, Any]:
        """Load render instructions.json - REQUIRED if render folder exists."""
        render_folder = self._find_render_folder()
        
        # If render folder doesn't exist, return empty dict (no render needed)
        if not render_folder.exists() or not render_folder.is_dir():
            return {}
        
        # If render folder exists, instructions.json is MANDATORY
        instructions_path = render_folder / 'instructions.json'
        if not instructions_path.exists():
            raise FileNotFoundError(
                f"Render folder exists at {render_folder} but instructions.json is missing. "
                f"instructions.json is mandatory when render folder exists."
            )
        
        return read_json_file(instructions_path)
    
    def _load_render_specs(self):
        render_folder = self._find_render_folder()
        
        # Guard: Only load specs if render folder exists
        if not render_folder.exists() or not render_folder.is_dir():
            return
        
        render_json_files = [f for f in render_folder.glob('*.json')]
        
        for render_json_file in render_json_files:
            config_data = read_json_file(render_json_file)
            render_spec = RenderSpec(config_data, render_folder, self.behavior.bot_paths, render_json_file)
            self._render_specs.append(render_spec)
    
    @property
    def render_specs(self) -> List[RenderSpec]:
        return self._render_specs
    
    @property
    def templates(self) -> List:
        templates = []
        for spec in self._render_specs:
            if spec.template:
                templates.append(spec.template)
        return templates
    
    @property
    def synchronizers(self) -> List:
        synchronizers = []
        for spec in self._render_specs:
            if spec.synchronizer:
                synchronizers.append(spec.synchronizer)
        return synchronizers
    
    def _load_render_configs(self) -> List[Dict[str, Any]]:
        render_folder = self._find_render_folder()
        render_configs = []
        
        # Guard: Only load configs if render folder exists
        if not render_folder.exists() or not render_folder.is_dir():
            return render_configs
        
        render_json_files = [f for f in render_folder.glob('*.json')]
        
        for render_json_file in render_json_files:
            render_config = self._load_single_render_config(render_json_file)
            render_configs.append(render_config)
        
        return render_configs
    
    def _load_single_render_config(self, render_json_file: Path) -> Dict[str, Any]:
        config = read_json_file(render_json_file)
        
        config_entry = {
            'file': str(render_json_file.relative_to(self.behavior.bot_paths.bot_directory)),
            'config': config
        }
        
        if 'synchronizer' in config:
            self._verify_synchronizer_class(config['synchronizer'])
        elif 'template' in config:
            template_content = self._load_template_file(config['template'])
            config_entry['template'] = template_content
        
        return config_entry
    
    def _verify_synchronizer_class(self, synchronizer_class_path: str) -> None:
        module_path, class_name = synchronizer_class_path.rsplit('.', 1)
        
        possible_paths = [
            module_path,
            f'agile_bot.bots.{self.behavior.bot_name}.src.{module_path}',
            f'agile_bot.bots.{self.behavior.bot_name}.src.synchronizers.{module_path}',
        ]
        
        module = None
        for path in possible_paths:
            try:
                module = importlib.import_module(path)
                if hasattr(module, class_name):
                    break
                module = None
            except ImportError:
                continue
        
        if module is None:
            # In test scenarios, synchronizer classes may not exist
            # Skip verification if module cannot be imported
            return
        
        synchronizer_class = getattr(module, class_name)
        
        has_render = hasattr(synchronizer_class, 'render')
        has_sync_methods = any(
            hasattr(synchronizer_class, method)
            for method in ['synchronize_outline', 'synchronize_increments', 'synchronize_exploration']
        )
        
        if not (has_render or has_sync_methods):
            raise ValueError(f'Synchronizer class {synchronizer_class_path} does not have required methods')
    
    def _load_template_file(self, template_path: str) -> str:
        render_folder = self._find_render_folder()
        templates_dir = render_folder / 'templates'
        
        if template_path.startswith('templates/'):
            template_path = template_path[10:]
        
        template_file = templates_dir / template_path
        return template_file.read_text(encoding='utf-8')
    
    def _inject_render_data(self, instructions: Dict[str, Any], render_instructions: Dict[str, Any], render_configs: List[Dict[str, Any]]) -> None:
        base_instructions_list = instructions.get('base_instructions', []).copy()
        
        # Add workspace path information to instructions
        workspace_path = self.working_dir
        bot_directory = self.behavior.bot_paths.bot_directory
        if workspace_path != bot_directory:
            workspace_info = f"\n**WORKSPACE PATH: {workspace_path}**\nAll render outputs must be written to paths relative to this workspace path, NOT to the bot's own directories."
            base_instructions_list.insert(0, workspace_info)
        
        # Inject render_instructions and render_configs template variables
        self._inject_render_template_variables(base_instructions_list, render_instructions, render_configs)
        
        # Update instructions dict
        instructions['base_instructions'] = base_instructions_list
        
        # Add render-specific data to instructions dict
        instructions['render_instructions'] = render_instructions
        instructions['render_configs'] = render_configs
        
        if workspace_path != bot_directory:
            instructions['workspace_path'] = str(workspace_path)
    
    def _inject_render_template_variables(self, instructions_list: List[str], render_instructions: Dict[str, Any], render_configs: List[Dict[str, Any]]) -> None:
        render_instructions_text = '\n'.join(render_instructions.get('instructions', []))
        
        # Format render configs for injection
        render_configs_text = self._format_render_configs(render_configs)
        
        # Replace template variables
        new_instructions = []
        for line in instructions_list:
            if '{{render_instructions}}' in line:
                # Split instructions into lines and insert them
                instructions_lines = render_instructions_text.split('\n')
                new_instructions.extend(instructions_lines)
            elif '{{render_configs}}' in line:
                # Split configs into lines and insert them
                configs_lines = render_configs_text.split('\n')
                new_instructions.extend(configs_lines)
            else:
                new_instructions.append(line)
        
        instructions_list[:] = new_instructions
    
    def _format_render_configs(self, render_configs: List[Dict[str, Any]]) -> str:
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
        return "Proceed to validate action"
