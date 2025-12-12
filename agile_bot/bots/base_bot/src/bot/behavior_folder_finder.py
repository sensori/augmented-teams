"""
Centralized utility for finding behavior folders and subfolders with numbered prefixes.

All bot actions should use these utilities instead of hardcoding paths or implementing
their own glob logic. This ensures consistent handling of numbered folder prefixes like:
- 1_guardrails
- 2_content
- 3_rules
- 1_required_context
- 2_planning
"""
from pathlib import Path
from typing import Optional


def normalize_behavior_name(name: str) -> str:
    """
    Normalize behavior name by stripping number prefix and applying abbreviations.
    
    Used for consistent behavior name matching across the codebase (e.g., in MCP tools,
    confirmations, workflow state).
    
    Args:
        name: Behavior name with optional number prefix (e.g., '1_shape', '8_code', 'shape')
    
    Returns:
        Normalized behavior name (e.g., 'shape', 'code')
        
    Examples:
        >>> normalize_behavior_name('1_shape')  # Returns 'shape'
        >>> normalize_behavior_name('8_code')   # Returns 'code'
        >>> normalize_behavior_name('shape')    # Returns 'shape'
        >>> normalize_behavior_name('6_scenarios')  # Returns 'scenarios'
    """
    # Strip number prefix (e.g., '1_shape' -> 'shape')
    if name and name[0].isdigit() and '_' in name:
        name = name.split('_', 1)[1]
    
    # Abbreviate common long words
    abbreviations = {
        'specification': 'spec',
        'decide_planning_criteria': 'decide_planning',
        'tests': 'write_tests',  # Avoid conflict with pytest "tests"
    }
    
    for full, abbrev in abbreviations.items():
        name = name.replace(full, abbrev)
    
    return name


def find_behavior_subfolder(behavior_folder: Path, subfolder_name: str) -> Optional[Path]:
    """
    Find a subfolder within a behavior folder, handling numbered prefixes.
    
    Args:
        behavior_folder: Path to behavior folder (e.g., behaviors/1_shape)
        subfolder_name: Name of subfolder to find (e.g., 'guardrails', 'content', 'rules')
    
    Returns:
        Path to found folder, or None if not found
        
    Examples:
        >>> find_behavior_subfolder(behavior_folder, 'guardrails')  # Finds '1_guardrails'
        >>> find_behavior_subfolder(behavior_folder, 'content')     # Finds '2_content'
        >>> find_behavior_subfolder(behavior_folder, 'planning')    # Finds '2_planning'
    """
    # Look for folder with pattern: *subfolder_name (e.g., *guardrails, *content)
    for folder in behavior_folder.glob(f'*{subfolder_name}'):
        if folder.is_dir():
            return folder
    return None


def find_nested_subfolder(parent_folder: Path, *subfolder_names: str) -> Optional[Path]:
    """
    Find nested subfolders, handling numbered prefixes at each level.
    
    Args:
        parent_folder: Starting folder
        *subfolder_names: Names of nested subfolders to traverse
    
    Returns:
        Path to final nested folder, or None if any level not found
        
    Examples:
        >>> find_nested_subfolder(behavior_folder, 'guardrails', 'planning')
        # Finds: 1_guardrails/2_planning
        
        >>> find_nested_subfolder(behavior_folder, 'guardrails', 'required_context')
        # Finds: 1_guardrails/1_required_context
        
        >>> find_nested_subfolder(behavior_folder, 'content', 'knowledge_graph')
        # Finds: 2_content/1_knowledge_graph
    """
    current = parent_folder
    for name in subfolder_names:
        found = find_behavior_subfolder(current, name)
        if not found:
            return None
        current = found
    return current


def find_file_in_folder(folder: Path, file_pattern: str) -> Optional[Path]:
    """
    Find a file in a folder, handling numbered prefixes in filename.
    
    Args:
        folder: Folder to search in
        file_pattern: File pattern to match (e.g., 'key_questions.json', 'evidence.json')
    
    Returns:
        Path to found file, or None if not found
        
    Examples:
        >>> find_file_in_folder(required_context_folder, 'key_questions.json')
        # Finds: 1_key_questions.json or key_questions.json
    """
    # Look for file with pattern: *file_pattern
    for file in folder.glob(f'*{file_pattern}'):
        if file.is_file():
            return file
    return None
