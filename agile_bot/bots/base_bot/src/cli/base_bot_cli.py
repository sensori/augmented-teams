#!/usr/bin/env python3
"""Base Bot CLI - 90% of functionality inherited by bot-specific CLIs"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any, Tuple
from agile_bot.bots.base_bot.src.bot.bot import Bot


class BaseBotCli:
    """Base CLI class - bot-specific CLIs inherit 90% of functionality from this"""
    
    def __init__(self, bot: Bot = None, bot_name: str = None, bot_config_path: Path = None, workspace_root: Path = None):
        """Initialize CLI with bot instance or configuration.
        
        Args:
            bot: Bot instance (preferred - explicit dependency)
            bot_name: Name of the bot (required if bot not provided)
            bot_config_path: Path to bot configuration file (required if bot not provided)
            workspace_root: Root workspace directory (defaults to current directory if bot not provided)
            
        Raises:
            ValueError: If neither bot nor (bot_name and bot_config_path) are provided
        """
        if bot:
            self.bot = bot
            self.bot_name = bot.name
        elif bot_name and bot_config_path:
            self.bot_name = bot_name
            self.workspace_root = workspace_root or Path.cwd()
            self.bot_config_path = bot_config_path
            self.bot = self._create_bot_instance()
        else:
            raise ValueError("Must provide either bot instance or (bot_name and bot_config_path)")
    
    def _create_bot_instance(self) -> Bot:
        return Bot(
            bot_name=self.bot_name,
            workspace_root=self.workspace_root,
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
    def parse_arguments(description: str = "Bot CLI") -> Tuple[argparse.Namespace, Dict[str, str]]:
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('behavior', nargs='?', help='Behavior name (optional)')
        parser.add_argument('action', nargs='?', help='Action name (optional)')
        parser.add_argument('--close', action='store_true', help='Close current action')
        parser.add_argument('--list', action='store_true', help='List available options')
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
        - Any additional context passed as positional arguments
        """
        params = {}
        
        for arg in unknown_args:
            if not arg:
                continue
            if '=' in arg:
                # Named parameter: --key=value or key=value
                key, value = arg.split('=', 1)
                params[key.lstrip('--')] = value
            elif arg.startswith('--'):
                # Flag argument (handled by argparse)
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
        
        return params
    
    def main(self):
        args, params = BaseBotCli.parse_arguments(description=f"{self.bot_name} CLI")
        
        try:
            if args.list:
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
    
    def generate_cursor_commands(self, commands_dir: Path, cli_script_path: Path) -> Dict[str, Path]:
        """Generate cursor command files for bot and behaviors.
        
        Generates:
        - Bot command: routes to current behavior/action
        - Behavior commands: one per behavior, accepts optional action parameter via ${1:}
          If no action parameter provided, uses default/current action
        
        Args:
            commands_dir: Directory where cursor command files will be written (.cursor/commands/)
            cli_script_path: Path to the CLI script that will be invoked
            
        Returns:
            Dict mapping command name to file path
        """
        commands_dir.mkdir(parents=True, exist_ok=True)
        
        current_command_files = self._get_current_command_files(commands_dir)
        commands = {}
        
        # Bot command: routes to current behavior/action
        cli_script_str = str(cli_script_path)
        bot_command = f"{cli_script_str}"
        commands[f'{self.bot_name}'] = self._write_command_file(commands_dir / f'{self.bot_name}.md', bot_command)
        
        # Behavior commands: accept optional action parameter and any additional context
        for behavior_name in self.bot.behaviors:
            # ${1:} is optional action name (if provided, routes to that action)
            # ${2:} is optional context (file paths, parameters, etc. - CLI will parse and pass to action)
            # If no action provided, behavior uses default/current action
            # Note: Cursor will replace ${1:} and ${2:} with user input or empty string
            # Additional arguments can be passed as --key=value or file paths
            # Convert cli_script_path to string for command
            cli_script_str = str(cli_script_path)
            behavior_command = f"{cli_script_str} {behavior_name} ${{1:}}"
            commands[f'{self.bot_name}-{behavior_name}'] = self._write_command_file(
                commands_dir / f'{self.bot_name}-{behavior_name}.md', 
                behavior_command
            )
        
        self._remove_obsolete_command_files(commands_dir, current_command_files, commands)
        
        return commands
    
    def _get_current_command_files(self, commands_dir: Path) -> set:
        """Get set of existing command files for this bot.
        
        Args:
            commands_dir: Directory containing command files
            
        Returns:
            Set of existing command file paths
        """
        if not commands_dir.exists():
            return set()
        
        bot_prefix = f'{self.bot_name}'
        existing_files = set()
        
        for file_path in commands_dir.glob(f'{bot_prefix}*.md'):
            existing_files.add(file_path)
        
        return existing_files
    
    def _remove_obsolete_command_files(self, commands_dir: Path, existing_files: set, current_commands: Dict[str, Path]):
        """Remove command files that no longer correspond to current bot behaviors/actions.
        
        Args:
            commands_dir: Directory containing command files
            existing_files: Set of existing command file paths before generation
            current_commands: Dict of current command names to file paths
        """
        current_file_paths = set(current_commands.values())
        
        for file_path in existing_files:
            if file_path not in current_file_paths:
                file_path.unlink(missing_ok=True)
    
    def _write_command_file(self, file_path: Path, command: str) -> Path:
        """Write cursor command file with command content.
        
        Args:
            file_path: Path to command file
            command: Command string to write
            
        Returns:
            Path to written file
        """
        file_path.write_text(command, encoding='utf-8')
        return file_path

