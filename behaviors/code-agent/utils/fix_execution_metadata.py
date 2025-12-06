"""
Script to fix execution metadata in command files by verifying and correcting
Python import paths and CLI actions based on actual runner implementations.
"""

import re
import ast
from pathlib import Path
from typing import Dict, Optional, Tuple


def find_command_classes(runner_path: Path) -> Dict[str, str]:
    """Parse runner file to find command class names"""
    if not runner_path.exists():
        return {}
    
    try:
        content = runner_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        command_classes = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a Command class (ends with Command)
                if node.name.endswith('Command') and not node.name.startswith('CodeAugmented'):
                    # Get the module path
                    module_parts = runner_path.parts
                    if 'behaviors' in module_parts:
                        behaviors_idx = module_parts.index('behaviors')
                        module_path = '.'.join(module_parts[behaviors_idx:-1])  # Exclude filename
                        runner_module = runner_path.stem
                        full_path = f"{module_path}.{runner_module}.{node.name}"
                        command_classes[node.name] = full_path
        
        return command_classes
    except Exception as e:
        print(f"Error parsing {runner_path}: {e}")
        return {}


def extract_metadata_from_file(file_path: Path) -> Optional[Dict]:
    """Extract execution metadata from command file"""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Check for YAML frontmatter
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not frontmatter_match:
            return None
        
        import yaml
        yaml_content = frontmatter_match.group(1)
        data = yaml.safe_load(yaml_content)
        
        if 'execution' in data:
            return data['execution']
        return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def get_correct_class_name(command_name: str, feature_name: str, command_classes: Dict[str, str]) -> Optional[str]:
    """Try to find the correct class name for a command"""
    # Try different naming patterns
    patterns = [
        f"{feature_name.title().replace('-', '')}{command_name.title().replace('-', '')}Command",
        f"{command_name.title().replace('-', '')}Command",
        f"{feature_name.upper().replace('-', '_')}{command_name.title().replace('-', '')}Command",
    ]
    
    for pattern in patterns:
        for class_name in command_classes.keys():
            if class_name == pattern or class_name.lower() == pattern.lower():
                return command_classes[class_name]
    
    return None


def fix_command_file(file_path: Path, runner_path: Path, feature_name: str, command_name: str) -> bool:
    """Fix execution metadata in a command file"""
    metadata = extract_metadata_from_file(file_path)
    if not metadata:
        print(f"  [SKIP] {file_path.name} - no metadata found")
        return False
    
    command_classes = find_command_classes(runner_path)
    if not command_classes:
        print(f"  [WARN] {file_path.name} - couldn't parse runner classes")
        return False
    
    # Find correct class
    correct_import = get_correct_class_name(command_name, feature_name, command_classes)
    if not correct_import:
        print(f"  [WARN] {file_path.name} - couldn't find class for {command_name}")
        return False
    
    # Check if import path is correct
    current_import = metadata.get('python_import', '')
    if current_import == correct_import:
        print(f"  [OK] {file_path.name} - import path correct")
        return False
    
    # Update the import path
    print(f"  [FIX] {file_path.name}")
    print(f"    Old: {current_import}")
    print(f"    New: {correct_import}")
    
    # Read file and update
    content = file_path.read_text(encoding='utf-8')
    
    # Replace the python_import line
    old_pattern = f"python_import: {re.escape(current_import)}"
    new_pattern = f"python_import: {correct_import}"
    content = re.sub(old_pattern, new_pattern, content)
    
    file_path.write_text(content, encoding='utf-8')
    return True


def process_all_commands(workspace_root: Path):
    """Process all command files and fix metadata"""
    behaviors_dir = workspace_root / 'behaviors'
    if not behaviors_dir.exists():
        print(f"Behaviors directory not found: {behaviors_dir}")
        return
    
    command_files = list(behaviors_dir.rglob('*-cmd.md'))
    main_commands = [f for f in command_files if not any(x in f.stem for x in ['-generate-', '-validate-', '-correct-', '-plan-'])]
    
    print(f"Checking {len(main_commands)} command files...\n")
    
    fixed_count = 0
    
    for cmd_file in main_commands:
        parts = cmd_file.parts
        if 'behaviors' not in parts:
            continue
        
        behaviors_idx = parts.index('behaviors')
        if behaviors_idx + 1 >= len(parts):
            continue
        
        feature_name = parts[behaviors_idx + 1]
        command_name = cmd_file.stem.replace('-cmd', '')
        if command_name.startswith(feature_name):
            command_name = command_name[len(feature_name) + 1:] if len(command_name) > len(feature_name) else command_name
        
        runner_path = workspace_root / 'behaviors' / feature_name / f"{feature_name}_runner.py"
        if not runner_path.exists():
            # Try alternative naming
            runner_path = workspace_root / 'behaviors' / feature_name / f"{feature_name.replace('-', '_')}_runner.py"
        
        if runner_path.exists():
            if fix_command_file(cmd_file, runner_path, feature_name, command_name):
                fixed_count += 1
    
    print(f"\nSummary: Fixed {fixed_count} command files")


if __name__ == "__main__":
    import sys
    workspace_root = Path(__file__).parent.parent.parent.parent
    process_all_commands(workspace_root)

