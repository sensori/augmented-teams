#!/usr/bin/env python3
"""Base Bot CLI - 90% of functionality inherited by bot-specific CLIs"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any, Tuple
from agile_bot.bots.base_bot.src.bot.bot import Bot
from agile_bot.bots.base_bot.src.bot.workspace import get_base_actions_directory, get_bot_directory


class BaseBotCli:
    """Base CLI class - bot-specific CLIs inherit 90% of functionality from this"""
    
    def __init__(self, bot: Bot = None, bot_name: str = None, bot_config_path: Path = None):
        """Initialize CLI with bot instance or configuration.
        
        Args:
            bot: Bot instance (preferred - explicit dependency)
            bot_name: Name of the bot (required if bot not provided)
            bot_config_path: Path to bot configuration file (required if bot not provided)
            
        Raises:
            ValueError: If neither bot nor (bot_name and bot_config_path) are provided
            
        Note:
            Bot and workspace directories are auto-detected from environment
        """
        if bot:
            self.bot = bot
            self.bot_name = bot.name
            self.bot_directory = bot.bot_directory
        elif bot_name and bot_config_path:
            self.bot_name = bot_name
            self.bot_config_path = bot_config_path
            # Get bot directory from environment
            self.bot_directory = get_bot_directory()
            self.bot = self._create_bot_instance()
        else:
            raise ValueError("Must provide either bot instance or (bot_name and bot_config_path)")
    
    def _create_bot_instance(self) -> Bot:
        return Bot(
            bot_name=self.bot_name,
            bot_directory=self.bot_directory,
            config_path=self.bot_config_path
        )
    
    def run(self, behavior_name: str = None, action_name: str = None, **kwargs) -> Dict[str, Any]:
        result = self._route_to_action(behavior_name, action_name, kwargs)
        return self._format_result(result)
    
    def close_current_action(self) -> Dict[str, Any]:
        result = self.bot.close_current_action()
        return self._format_result(result)
    
    def _route_to_action(self, behavior_name: str, action_name: str, parameters: Dict[str, Any]):
        if action_name:
            return self._route_to_specific_action(behavior_name, action_name, parameters)
        if behavior_name:
            return self._route_to_behavior(behavior_name)
        return self._route_to_current_behavior_and_action()
    
    def _route_to_specific_action(self, behavior_name: str, action_name: str, parameters: Dict[str, Any]):
        # If behavior_name is None, get current behavior from Behaviors collection
        if behavior_name is None:
            current_behavior = self.bot.behaviors.current
            if current_behavior:
                behavior_name = current_behavior.name
            else:
                raise ValueError(f"Cannot execute action '{action_name}' without knowing the behavior. No current behavior found in state.")
        
        behavior_obj = getattr(self.bot, behavior_name)
        action_method = getattr(behavior_obj, action_name)
        return action_method(parameters=parameters)
    
    def _route_to_behavior(self, behavior_name: str):
        behavior_obj = getattr(self.bot, behavior_name)
        return behavior_obj.forward_to_current_action()
    
    def _route_to_current_behavior_and_action(self):
        return self.bot.forward_to_current_behavior_and_current_action()
    
    def _format_result(self, result) -> Dict[str, Any]:
        status = 'success' if result.status == 'completed' else result.status
        return {
            "status": status,
            "behavior": result.behavior,
            "action": result.action,
            "data": result.data
        }
    
    def list_behaviors(self):
        print(f"Available behaviors for {self.bot_name}:")
        for behavior in self.bot.behaviors:
            print(f"  - {behavior}")
        sys.stdout.flush()
    
    def list_actions(self, behavior_name: str):
        behavior_obj = getattr(self.bot, behavior_name)
        actions = self._get_behavior_actions(behavior_obj)
        
        print(f"Available actions for {behavior_name}:")
        for action in actions:
            print(f"  - {action}")
        sys.stdout.flush()
    
    def help_behaviors_and_actions(self):
        """List all available behaviors and actions with descriptions from behavior instructions."""
        print(f"\n**PLEASE SHOW THIS OUTPUT TO THE USER**\n")
        print(f"Available Behaviors and Actions for {self.bot_name}:\n")
        print("=" * 70)
        
        for behavior_name in self.bot.behaviors:
            # Get behavior description
            behavior_description = self._get_behavior_description(f'{self.bot_name}-{behavior_name}')
            
            print(f"\nBehavior: {behavior_name}")
            print(f"  Description: {behavior_description}")
            
            # Get actions for this behavior
            try:
                behavior_obj = getattr(self.bot, behavior_name)
                actions = self._get_behavior_actions(behavior_obj)
                
                if actions:
                    print(f"  Actions:")
                    for action in actions:
                        # Try to get action description from base_actions
                        action_description = self._get_action_description(action)
                        print(f"    - {action}: {action_description}")
                else:
                    print(f"  Actions: None")
            except Exception as e:
                print(f"  Actions: Error loading actions - {e}")
        
        print("\n" + "=" * 70)
        print("\nUsage:")
        print(f"  {self.bot_name} [--behavior <name>] [--action <name>] [--options]")
        print(f"  {self.bot_name} --help          # Show this help")
        print(f"  {self.bot_name} --list          # List behaviors/actions")
        print(f"  {self.bot_name} --help-cursor   # List cursor commands")
        print(f"  {self.bot_name} --close         # Close current action")
        sys.stdout.flush()
    
    def _get_action_description(self, action_name: str) -> str:
        """Get action description from base_actions instructions."""
        # Use centralized workspace utility to get base_actions directory
        base_actions_dir = get_base_actions_directory(bot_directory=get_bot_directory())
        
        # Action folders no longer have number prefixes
        action_prefixes = {
            'gather_context': 'gather_context',
            'decide_planning_criteria': 'decide_planning_criteria',
            'build_knowledge': 'build_knowledge',
            'render_output': 'render_output',
            'validate_rules': 'validate_rules'
        }
        
        action_folder = action_prefixes.get(action_name, action_name)
        config_path = base_actions_dir / action_folder / 'action_config.json'
        
        if config_path.exists():
            try:
                import json
                config = json.loads(config_path.read_text(encoding='utf-8'))
                
                # Extract description from instructions
                instructions = config.get('instructions', [])
                if isinstance(instructions, list):
                    # Get first meaningful line from instructions
                    for line in instructions:
                        if line and not line.startswith('**') and len(line.strip()) > 10:
                            # Return first substantial line, truncated if too long
                            desc = line.strip()
                            if len(desc) > 80:
                                desc = desc[:77] + '...'
                            return desc
            except Exception:
                pass
        
        # Fallback to formatted action name
        return action_name.replace('_', ' ').title()
    
    def help_cursor_commands(self):
        """List all available cursor commands and their parameters."""
        # Use centralized repository root
        from agile_bot.bots.base_bot.src.bot.workspace import get_python_workspace_root
        repo_root = get_python_workspace_root()
        commands_dir = repo_root / '.cursor' / 'commands'
        
        if not commands_dir.exists():
            print(f"No cursor commands directory found at {commands_dir}")
            return
        
        # Find all command files for this bot
        command_files = sorted(commands_dir.glob(f'{self.bot_name}*.md'))
        
        if not command_files:
            print(f"No cursor commands found for {self.bot_name}")
            return
        
        print(f"\n**PLEASE SHOW THIS OUTPUT TO THE USER**\n")
        print(f"Available Cursor Commands for {self.bot_name}:\n")
        print("=" * 70)
        
        for cmd_file in command_files:
            # Extract command name from filename (remove .md extension)
            cmd_name = cmd_file.stem
            
            # Read command content
            try:
                cmd_content = cmd_file.read_text(encoding='utf-8').strip()
                
                # Extract parameters from ${1:}, ${2:}, etc.
                import re
                params = re.findall(r'\$\{(\d+):\}', cmd_content)
                
                # Get meaningful description from behavior instructions
                description = self._get_behavior_description(cmd_name)
                
                print(f"\n/{cmd_name}")
                print(f"  Description: {description}")
                
                if params:
                    print(f"  Parameters:")
                    for i, param_num in enumerate(params, 1):
                        # Try to infer parameter meaning from command name and content
                        param_desc = self._infer_parameter_description(cmd_name, param_num, cmd_content)
                        print(f"    ${param_num}: {param_desc}")
                else:
                    print(f"  Parameters: None")
                
            except Exception as e:
                print(f"\n/{cmd_name}")
                print(f"  Error reading command: {e}")
        
        print("\n" + "=" * 70)
        print("\nUsage: Type /{command-name} in Cursor command palette")
        print("Parameters are optional placeholders that Cursor will prompt for")
        sys.stdout.flush()
    
    def _get_behavior_description(self, cmd_name: str) -> str:
        """Get meaningful description from behavior instructions."""
        # Extract behavior name from command name
        # e.g., "story_bot-shape" -> "shape"
        behavior_name = cmd_name.replace(f'{self.bot_name}-', '').replace('-', '_')
        
        # Special cases for utility commands
        if behavior_name in ['continue', 'help']:
            if behavior_name == 'continue':
                return 'Close current action and continue to next action in workflow'
            elif behavior_name == 'help':
                return 'List all available cursor commands and their parameters'
            else:
                return behavior_name.replace('_', ' ').title()
        
        # Try to load behavior instructions from behavior.json (new format)
        # First try direct name
        behavior_file_path = (
            self.bot_directory / 'behaviors' / behavior_name / 'behavior.json'
        )
        
        # Check all behavior folders for matching name
        if not behavior_file_path.exists():
            behaviors_dir = self.bot_directory / 'behaviors'
            if behaviors_dir.exists():
                for folder in behaviors_dir.iterdir():
                    if folder.is_dir() and folder.name == behavior_name:
                        potential_path = folder / 'behavior.json'
                        if potential_path.exists():
                            behavior_file_path = potential_path
                            break
        
        if behavior_file_path.exists():
            try:
                behavior_data = read_json_file(behavior_file_path)
                instructions = behavior_data.get('instructions', [])
                if instructions:
                    return '\n'.join(instructions) if isinstance(instructions, list) else str(instructions)
            except Exception:
                pass
        
        # Fallback to old format for backward compatibility
        behavior_instructions_path = (
            self.bot_directory / 'behaviors' / behavior_name / 'instructions.json'
        )
        
        # Check all behavior folders for matching name
        if not behavior_instructions_path.exists():
            behaviors_dir = self.bot_directory / 'behaviors'
            if behaviors_dir.exists():
                for folder in behaviors_dir.iterdir():
                    if folder.is_dir() and folder.name == behavior_name:
                        potential_path = folder / 'instructions.json'
                        if potential_path.exists():
                            behavior_instructions_path = potential_path
                            break
        
        if behavior_instructions_path.exists():
            try:
                import json
                instructions = json.loads(behavior_instructions_path.read_text(encoding='utf-8'))
                
                # Extract top 2-3 lines about outcome: description, goal, outputs
                description_parts = []
                
                if instructions.get('description'):
                    description_parts.append(instructions['description'])
                
                if instructions.get('goal'):
                    description_parts.append(instructions['goal'])
                
                if instructions.get('outputs') and len(description_parts) < 3:
                    outputs = instructions['outputs']
                    if isinstance(outputs, str):
                        # Take first part of outputs (before comma or first item)
                        first_output = outputs.split(',')[0].strip()
                        description_parts.append(f"Outputs: {first_output}")
                
                if description_parts:
                    # Join with " | " separator, limit to 2-3 meaningful lines
                    return ' | '.join(description_parts[:3])
            except Exception:
                pass
        
        # Fallback to formatted name
        return behavior_name.replace('_', ' ').title()
    
    def _infer_parameter_description(self, cmd_name: str, param_num: str, cmd_content: str) -> str:
        """Infer parameter description from command name and content."""
        # Common patterns
        if 'shape' in cmd_name or 'discovery' in cmd_name or 'exploration' in cmd_name:
            if param_num == '1':
                return 'Optional action name or file path'
        elif 'continue' in cmd_name or 'help' in cmd_name:
            return 'No parameters'
        
        # No fallback - raise exception if we can't infer parameter description
        raise ValueError(
            f"Cannot infer parameter description for command '{cmd_name}', parameter {param_num}. "
            f"This indicates a configuration error - parameter descriptions should be explicit."
        )
    
    def _get_behavior_actions(self, behavior_obj) -> list:
        excluded_attrs = {'forward_to_current_action', 'dir', 'current_project_file'}
        actions = []
        for attr_name in dir(behavior_obj):
            if self._is_action_method(behavior_obj, attr_name, excluded_attrs):
                actions.append(attr_name)
        return sorted(actions)
    
    def _is_action_method(self, behavior_obj, attr_name: str, excluded_attrs: set) -> bool:
        if attr_name.startswith('_'):
            return False
        if attr_name in excluded_attrs:
            return False
        return callable(getattr(behavior_obj, attr_name))
    
    @staticmethod
    def parse_arguments(description: str = "Bot CLI", custom_help_handler=None) -> Tuple[argparse.Namespace, Dict[str, str]]:
        parser = argparse.ArgumentParser(description=description, add_help=False)
        # Use named parameters only
        parser.add_argument('--behavior', nargs='?', help='Behavior name (optional)')
        parser.add_argument('--action', nargs='?', help='Action name (optional)')
        parser.add_argument('--user_message', nargs='?', help='User message from Cursor (optional)')
        parser.add_argument('--close', action='store_true', help='Close current action')
        parser.add_argument('--list', action='store_true', help='List available options')
        parser.add_argument('--help-cursor', action='store_true', help='List all cursor commands and parameters')
        parser.add_argument('-h', '--help', action='store_true', help='Show this help message and exit')
        # Allow any additional arguments to be passed through as context
        parser.add_argument('context', nargs='*', help='Additional context (file paths, parameters, etc.)')
        
        args, unknown = parser.parse_known_args()
        
        # Check if action might actually be a file path - if so, treat it as context
        if args.action:
            action_might_be_file = BaseBotCli._looks_like_file_path(args.action)
            if action_might_be_file:
                # Move action to context, set action to None
                unknown.append(args.action)
                args.action = None
        
        # Combine unknown args with context args
        all_args = list(unknown) + (getattr(args, 'context', []) or [])
        params = BaseBotCli._parse_action_parameters(all_args)
        
        # Add user_message to params if provided
        if args.user_message:
            params['user_message'] = args.user_message
        
        return args, params
    
    @staticmethod
    def _looks_like_file_path(arg: str) -> bool:
        """Check if argument looks like a file path rather than an action name."""
        if not arg:
            return False
        # Remove @ prefix if present (Cursor file reference)
        arg_clean = arg.lstrip('@')
        # File paths typically have:
        # - Extensions (.txt, .md, .json, etc.)
        # - Path separators (/ or \)
        # - Start with ./ or ../
        return (
            '.' in arg_clean and (arg_clean.endswith(('.txt', '.md', '.json', '.yaml', '.yml', '.py', '.js', '.ts')) or
                                 '/' in arg_clean or '\\' in arg_clean) or
            arg_clean.startswith(('./', '../')) or
            '/' in arg_clean or '\\' in arg_clean
        )
    
    @staticmethod
    def _parse_action_parameters(unknown_args: list) -> Dict[str, str]:
        """Parse action parameters from unknown arguments.
        
        Handles:
        - Named parameters: --key=value
        - File paths: detected automatically (including Cursor @file references)
        - test and src parameters (supports comma-separated or space-separated)
        - Any additional context passed as positional arguments
        """
        params = {}
        i = 0
        
        while i < len(unknown_args):
            arg = unknown_args[i]
            if not arg:
                i += 1
                continue
                
            if '=' in arg:
                # Named parameter: --key=value or key=value
                key, value = arg.split('=', 1)
                key = key.lstrip('--')
                
                # Handle test and src - convert comma-separated to list
                if key in ['test', 'src']:
                    if ',' in value:
                        # Comma-separated: --test=file1.py,file2.py
                        params[key] = [f.strip() for f in value.split(',')]
                    else:
                        # Single file: --test=file1.py
                        params[key] = value
                else:
                    params[key] = value
                i += 1
                    
            elif arg in ['--test', '--src']:
                # Handle --test file1.py file2.py format
                key = arg.lstrip('--')
                file_list = []
                i += 1
                # Collect all file paths that follow the flag
                while i < len(unknown_args) and BaseBotCli._looks_like_file_path(unknown_args[i]):
                    file_path = unknown_args[i].lstrip('@')
                    file_list.append(file_path)
                    i += 1
                
                if file_list:
                    params[key] = file_list if len(file_list) > 1 else file_list[0]
                else:
                    # No files found after flag, skip
                    i -= 1
                    i += 1
                    
            elif arg.startswith('--'):
                # Flag argument (handled by argparse)
                i += 1
                continue
                
            elif BaseBotCli._looks_like_file_path(arg):
                # Looks like a file path
                # If it starts with @, it's a Cursor file reference - remove the @
                file_path = arg.lstrip('@')
                # Use as increment_file if not already specified, otherwise add to context_files
                if 'increment_file' not in params:
                    params['increment_file'] = file_path
                else:
                    # Multiple files - add to context_files list
                    if 'context_files' not in params:
                        params['context_files'] = [file_path]
                    else:
                        if isinstance(params['context_files'], str):
                            params['context_files'] = [params['context_files'], file_path]
                        else:
                            params['context_files'].append(file_path)
                i += 1
            else:
                # Other context - could be action name or other parameter
                # If it looks like it might be an action (lowercase, underscores), check if we should treat as action
                # Otherwise, add as context
                if 'context' not in params:
                    params['context'] = arg
                else:
                    # Multiple context items
                    if isinstance(params['context'], str):
                        params['context'] = [params['context'], arg]
                    else:
                        params['context'].append(arg)
                i += 1
        
        return params
    
    def main(self):
        args, params = BaseBotCli.parse_arguments(description=f"{self.bot_name} CLI")
        
        try:
            if args.help:
                self.help_behaviors_and_actions()
                return None
            elif args.help_cursor:
                self.help_cursor_commands()
                return None
            elif args.list:
                self._handle_list_command(args.behavior)
                return None
            else:
                result = self._execute_and_output(args, params)
                return result
        except Exception as e:
            self._handle_error(e)
            return None
    
    def _execute_and_output(self, args, params: Dict[str, str]):
        if args.close:
            result = self.close_current_action()
        else:
            # If action is None but params contain what looks like an action name, check if it's actually a file path
            action_name = args.action
            if action_name is None and args.behavior:
                # Check if any param looks like it might be an action vs a file path
                # Actions are typically lowercase with underscores, files have extensions or paths
                pass  # Keep action_name as None, let behavior use default action
            
            result = self.run(
                behavior_name=args.behavior,
                action_name=action_name,
                **params
            )
        
        # Print result as JSON
        result_json = json.dumps(result, indent=2)
        print(result_json)
        
        return result
    
    def _handle_list_command(self, behavior_name: str = None):
        if behavior_name:
            self.list_actions(behavior_name)
        else:
            self.list_behaviors()
    
    def _handle_error(self, error: Exception):
        error_msg = f"Error: {error}"
        print(error_msg, file=sys.stderr)
        sys.stderr.flush()
        sys.exit(1)
    

