"""CLI Generator - Generates bot-specific CLI code from bot configuration."""

from pathlib import Path
import json
import stat
from typing import Dict, Any
from agile_bot.bots.base_bot.src.utils import read_json_file


class CliGenerator:
    """Generator that creates CLI code for bots based on bot configuration."""
    
    def __init__(self, workspace_root: Path, bot_location: str = None):
        """Initialize CLI generator.
        
        Args:
            workspace_root: Root workspace directory
            bot_location: Path to bot directory (e.g., 'agile_bot/bots/story_bot')
                          If None, defaults to 'agile_bot/bots/base_bot'
        """
        self.workspace_root = Path(workspace_root)
        
        if bot_location is None:
            bot_location = 'agile_bot/bots/base_bot'
        
        self.bot_location = Path(bot_location)
        
        # Derive bot_name from last folder in bot_location
        self.bot_name = self.bot_location.name
        
        # Config path follows convention: {bot_location}/config/bot_config.json
        self.config_path = self.workspace_root / self.bot_location / 'config' / 'bot_config.json'
    
    def generate_cli_code(self) -> Dict[str, Any]:
        """Generate CLI code for bot.
        
        Returns:
            Dict mapping artifact names to file paths:
            - 'cli_python': Path to Python CLI script
            - 'cli_script': Path to shell script wrapper (bash)
            - 'cli_powershell': Path to PowerShell script wrapper (Windows)
            - 'cursor_commands': Dict mapping command names to cursor command file paths
            - 'registry': Path to updated bot registry
            
        Raises:
            FileNotFoundError: If bot config does not exist
            json.JSONDecodeError: If bot config is malformed
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f'Bot Config not found at {self.config_path}'
            )
        
        try:
            bot_config = read_json_file(self.config_path)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f'Malformed Bot Config at {self.config_path}: {e.msg}',
                e.doc,
                e.pos
            )
        
        # Generate Python CLI script
        cli_python_path = self._generate_python_cli_script()
        
        # Generate shell script wrapper (bash)
        cli_script_path = self._generate_shell_script()
        
        # Generate PowerShell script wrapper (Windows)
        cli_powershell_path = self._generate_powershell_script()
        
        # Generate cursor command files (use Python script directly)
        cursor_commands = self._generate_cursor_commands(cli_python_path)
        
        # Update bot registry
        registry_path = self._update_bot_registry(cli_python_path)
        
        return {
            'cli_python': cli_python_path,
            'cli_script': cli_script_path,
            'cli_powershell': cli_powershell_path,
            'cursor_commands': cursor_commands,
            'registry': registry_path
        }
    
    def _generate_python_cli_script(self) -> Path:
        """Generate Python CLI script that uses BaseBotCli.
        
        Returns:
            Path to generated Python CLI script
        """
        bot_dir = self.workspace_root / self.bot_location
        src_dir = bot_dir / 'src'
        src_dir.mkdir(parents=True, exist_ok=True)
        cli_file = src_dir / f'{self.bot_name}_cli.py'
        
        cli_code = f'''#!/usr/bin/env python3
"""
{self.bot_name.title().replace('_', ' ')} CLI Entry Point

Command-line interface for {self.bot_name} using BaseBotCli.

Usage:
    {self.bot_name} [--behavior <name>] [--action <name>] [--options]
    {self.bot_name} --help          # Show help/usage documentation
    {self.bot_name} --list          # List available behaviors
    {self.bot_name} --behavior <name> --list  # List available actions for behavior
    {self.bot_name} --close         # Close current action

Examples:
    {self.bot_name}                                    # Route to current behavior/action from workflow state
    {self.bot_name} --behavior exploration            # Route to exploration behavior, auto-forward to current action
    {self.bot_name} --behavior exploration --action gather_context  # Route directly to exploration.gather_context action
    {self.bot_name} --behavior exploration --action gather_context --increment_file=increment.txt  # With parameters
"""
from pathlib import Path
import sys
import os
import json

# Setup Python import path for package imports
python_workspace_root = Path(__file__).parent.parent.parent.parent.parent
if str(python_workspace_root) not in sys.path:
    sys.path.insert(0, str(python_workspace_root))

# ============================================================================
# BOOTSTRAP: Set environment variables before importing other modules
# ============================================================================

# 1. Self-detect bot directory from this script's location
bot_directory = Path(__file__).parent.parent  # src/ -> {self.bot_name}/
os.environ['BOT_DIRECTORY'] = str(bot_directory)

# 2. Read agent.json and set workspace directory (if not already set)
if 'WORKING_AREA' not in os.environ and 'WORKING_DIR' not in os.environ:
    agent_json_path = bot_directory / 'agent.json'
    if agent_json_path.exists():
        agent_config = json.loads(agent_json_path.read_text(encoding='utf-8'))
        if 'WORKING_AREA' in agent_config:
            os.environ['WORKING_AREA'] = agent_config['WORKING_AREA']

# ============================================================================
# Now import - everything will read from environment variables
# ============================================================================

from agile_bot.bots.base_bot.src.state.workspace import get_bot_directory, get_workspace_directory
from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli


def main():
    """Main CLI entry point.

    Environment variables are bootstrapped before import:
    - BOT_DIRECTORY: Self-detected from script location
    - WORKING_AREA: Read from agent.json (or pre-set by user)
    
    All subsequent code reads from these environment variables.
    """
    # Get directories (these now just read from env vars we set above)
    bot_directory = get_bot_directory()
    workspace_directory = get_workspace_directory()

    bot_name = '{self.bot_name}'
    bot_config_path = bot_directory / 'config' / 'bot_config.json'
    
    cli = BaseBotCli(
        bot_name=bot_name,
        bot_config_path=bot_config_path
    )
    
    cli.main()


if __name__ == '__main__':
    main()
'''
        
        cli_file.write_text(cli_code, encoding='utf-8')
        
        # Make executable on Unix systems
        cli_file.chmod(cli_file.stat().st_mode | stat.S_IEXEC)
        
        return cli_file
    
    def _generate_shell_script(self) -> Path:
        """Generate shell script wrapper for CLI.
        
        Returns:
            Path to generated shell script
        """
        bot_dir = self.workspace_root / self.bot_location
        script_file = bot_dir / f'{self.bot_name}_cli'
        
        script_content = f'''#!/bin/bash
    # {self.bot_name.title().replace('_', ' ')} CLI Wrapper

    # Get script directory
    SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"

    # Prefer setting WORKING_DIR explicitly for runtime file I/O. If not set,
    # derive a sensible default from the script location.
    export WORKING_DIR="${{WORKING_DIR:-$(cd "$SCRIPT_DIR/../../.." && pwd)}}"

    # Run Python CLI script (it resolves WORKING_AREA itself)
    python3 "$SCRIPT_DIR/src/{self.bot_name}_cli.py" "$@"
    '''
        
        script_file.write_text(script_content, encoding='utf-8')
        
        # Make executable
        script_file.chmod(script_file.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        
        return script_file
    
    def _generate_powershell_script(self) -> Path:
        """Generate PowerShell script wrapper for CLI.
        
        Returns:
            Path to generated PowerShell script
        """
        bot_dir = self.workspace_root / self.bot_location
        script_file = bot_dir / f'{self.bot_name}_cli.ps1'
        
        script_content = f'''# {self.bot_name.title().replace('_', ' ')} CLI Wrapper (PowerShell)

    # Get script directory
    $SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

    # Prefer setting WORKING_DIR explicitly for runtime file I/O. If not set,
    # derive a sensible default from the script location.
    if (-not $env:WORKING_DIR) {{
        $env:WORKING_DIR = (Resolve-Path "$SCRIPT_DIR\\..\\..\\..").Path
    }}

    # Run Python CLI script (it resolves WORKING_AREA itself)
    python "$SCRIPT_DIR\\src\\{self.bot_name}_cli.py" $args
    '''
        
        script_file.write_text(script_content, encoding='utf-8')
        
        return script_file
    
    def _get_behaviors_from_config(self) -> list:
        """Get behaviors list from bot config.
        
        Returns:
            List of behavior names
        """
        if not self.config_path.exists():
            return []
        
        try:
            bot_config = read_json_file(self.config_path)
            return bot_config.get('behaviors', [])
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _generate_cursor_commands(self, cli_script_path: Path) -> Dict[str, Path]:
        """Generate cursor command files for bot.
        
        Args:
            cli_script_path: Path to the Python CLI script that will be invoked
            
        Returns:
            Dict mapping command names to cursor command file paths
        """
        import os
        from agile_bot.bots.base_bot.src.cli.base_bot_cli import BaseBotCli
        
        # Set environment variables before creating BaseBotCli
        bot_directory = self.workspace_root / self.bot_location
        os.environ['BOT_DIRECTORY'] = str(bot_directory)
        # Set a temporary WORKING_AREA if not already set
        if 'WORKING_AREA' not in os.environ:
            os.environ['WORKING_AREA'] = str(self.workspace_root)
        
        # Create BaseBotCli instance to use its generate_cursor_commands method
        bot_config_path = self.workspace_root / self.bot_location / 'config' / 'bot_config.json'
        cli = BaseBotCli(
            bot_name=self.bot_name,
            bot_config_path=bot_config_path
        )
        
        # Generate cursor commands in .cursor/commands directory
        commands_dir = self.workspace_root / '.cursor' / 'commands'
        
        # Use relative path from workspace root for the Python CLI script
        if cli_script_path.is_absolute():
            rel_cli_script_path = cli_script_path.relative_to(self.workspace_root)
        else:
            # If not absolute, construct path relative to workspace root
            rel_cli_script_path = self.bot_location / 'src' / cli_script_path.name
        
        # Convert to forward slashes for cross-platform compatibility (Python handles both)
        cli_script_str = str(rel_cli_script_path).replace('\\', '/')
        
        return cli.generate_cursor_commands(commands_dir, Path(cli_script_str))
    
    def _update_bot_registry(self, cli_script_path: Path) -> Path:
        """Update bot registry with this bot's information.
        
        Args:
            cli_script_path: Path to the bot's CLI script
            
        Returns:
            Path to the registry file
        """
        registry_path = self.workspace_root / 'agile_bot' / 'bots' / 'registry.json'
        
        # Load existing registry or create new one
        if registry_path.exists():
            try:
                registry = read_json_file(registry_path)
            except (json.JSONDecodeError, FileNotFoundError):
                registry = {}
        else:
            registry = {}
            registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load bot-level trigger patterns
        trigger_patterns = self._load_bot_trigger_patterns()
        
        # Compute relative CLI path from workspace root
        if cli_script_path.is_absolute():
            rel_cli_path = str(cli_script_path.relative_to(self.workspace_root))
        else:
            rel_cli_path = str(self.bot_location / 'src' / cli_script_path.name)
        
        # Update registry entry for this bot
        registry[self.bot_name] = {
            'trigger_patterns': trigger_patterns,
            'cli_path': rel_cli_path.replace('\\', '/')
        }
        
        # Write updated registry
        registry_path.write_text(
            json.dumps(registry, indent=2, sort_keys=True),
            encoding='utf-8'
        )
        
        return registry_path
    
    def _load_bot_trigger_patterns(self) -> list:
        """Load bot-level trigger patterns from trigger_words.json.
        
        Returns:
            List of trigger patterns, or empty list if file doesn't exist
        """
        trigger_file = self.workspace_root / self.bot_location / 'trigger_words.json'
        
        if not trigger_file.exists():
            return []
        
        try:
            trigger_data = read_json_file(trigger_file)
            return trigger_data.get('patterns', [])
        except (json.JSONDecodeError, FileNotFoundError):
            return []

