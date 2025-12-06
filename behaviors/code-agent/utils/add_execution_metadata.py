"""
Script to add execution metadata to existing command files.

This script:
1. Scans for all command files (*-cmd.md) in behaviors/
2. Extracts feature name, command name, and runner path from file structure
3. Generates execution metadata based on patterns
4. Adds YAML frontmatter to command files that don't have it
"""

import re
from pathlib import Path
from typing import Optional, Dict, Tuple


def extract_feature_and_command(file_path: Path) -> Tuple[Optional[str], Optional[str]]:
    """Extract feature name and command name from file path"""
    parts = file_path.parts
    if 'behaviors' not in parts:
        return None, None
    
    behaviors_idx = parts.index('behaviors')
    if behaviors_idx + 1 >= len(parts):
        return None, None
    
    feature_name = parts[behaviors_idx + 1]
    
    # Command name is the filename without -cmd.md
    command_name = file_path.stem.replace('-cmd', '')
    
    # For commands like code-agent-sync, the command name includes feature
    if command_name.startswith(feature_name):
        # Extract just the command part
        command_name = command_name[len(feature_name) + 1:] if len(command_name) > len(feature_name) else command_name
    
    return feature_name, command_name


def get_runner_path(feature_name: str) -> str:
    """Get runner path for a feature"""
    return f"behaviors/{feature_name}/{feature_name}_runner.py"


def get_python_import_path(feature_name: str, command_name: str) -> str:
    """Get Python import path for command class"""
    # Convert feature-name to module path
    module_parts = ['behaviors'] + feature_name.split('-')
    module_path = '.'.join(module_parts)
    
    # Get runner module name
    runner_module = feature_name.replace('-', '_') + '_runner'
    
    # Get command class name (TitleCase, no hyphens)
    command_class = ''.join(word.capitalize() for word in command_name.split('-')) + 'Command'
    
    return f"{module_path}.{runner_module}.{command_class}"


def get_cli_actions(feature_name: str, command_name: str) -> Dict[str, str]:
    """Get CLI actions for a command"""
    full_command = f"{feature_name}-{command_name}"
    return {
        "generate": f"generate-{command_name}",
        "validate": f"validate-{command_name}",
        "correct": f"correct-{command_name}"
    }


def generate_execution_metadata(feature_name: str, command_name: str) -> str:
    """Generate YAML frontmatter execution metadata"""
    registry_key = f"{feature_name}-{command_name}"
    python_import = get_python_import_path(feature_name, command_name)
    cli_runner = get_runner_path(feature_name)
    actions = get_cli_actions(feature_name, command_name)
    
    yaml_content = f"""---
execution:
  registry_key: {registry_key}
  python_import: {python_import}
  cli_runner: {cli_runner}
  actions:
    generate:
      cli: {actions['generate']}
      method: generate
    validate:
      cli: {actions['validate']}
      method: validate
    correct:
      cli: {actions['correct']}
      method: correct
  working_directory: workspace_root
---"""
    return yaml_content


def has_frontmatter(content: str) -> bool:
    """Check if content already has YAML frontmatter"""
    return content.strip().startswith('---')


def add_metadata_to_file(file_path: Path, feature_name: str, command_name: str) -> bool:
    """Add execution metadata to a command file if it doesn't have it"""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Skip if already has frontmatter
        if has_frontmatter(content):
            print(f"  [SKIP] {file_path.name} - already has frontmatter")
            return False
        
        # Generate metadata
        metadata = generate_execution_metadata(feature_name, command_name)
        
        # Add metadata at the beginning
        new_content = metadata + "\n\n" + content
        
        # Write back
        file_path.write_text(new_content, encoding='utf-8')
        print(f"  [ADDED] {file_path.name}")
        return True
    except Exception as e:
        print(f"  [ERROR] {file_path.name}: {e}")
        return False


def process_all_commands(workspace_root: Path):
    """Process all command files in behaviors/"""
    behaviors_dir = workspace_root / 'behaviors'
    if not behaviors_dir.exists():
        print(f"Behaviors directory not found: {behaviors_dir}")
        return
    
    command_files = list(behaviors_dir.rglob('*-cmd.md'))
    print(f"Found {len(command_files)} command files")
    
    # Filter to main command files (not delegate files)
    main_commands = [f for f in command_files if not any(x in f.stem for x in ['-generate-', '-validate-', '-correct-', '-plan-'])]
    
    print(f"Processing {len(main_commands)} main command files...")
    
    added_count = 0
    skipped_count = 0
    
    for cmd_file in main_commands:
        feature_name, command_name = extract_feature_and_command(cmd_file)
        
        if not feature_name or not command_name:
            print(f"  [SKIP] {cmd_file.name} - couldn't extract feature/command")
            skipped_count += 1
            continue
        
        if add_metadata_to_file(cmd_file, feature_name, command_name):
            added_count += 1
        else:
            skipped_count += 1
    
    print(f"\nSummary:")
    print(f"  Added metadata: {added_count}")
    print(f"  Skipped: {skipped_count}")


if __name__ == "__main__":
    import sys
    workspace_root = Path(__file__).parent.parent.parent.parent
    process_all_commands(workspace_root)

