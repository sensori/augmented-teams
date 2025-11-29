"""
Story graph and layout data helper functions for spec-by-example tests.

Domain-specific helper functions for loading/saving story graphs and layout data.
Used by spec-by-example test scenarios that work with story graphs and DrawIO layouts.
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any


def load_story_graph(story_graph_path: Path) -> Dict[str, Any]:
    """
    Load story graph from JSON file.
    
    Args:
        story_graph_path: Path to story graph JSON file
    
    Returns:
        Story graph dictionary
    """
    with open(story_graph_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_layout_data(layout_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load layout data from JSON file.
    
    Args:
        layout_path: Path to layout JSON file
    
    Returns:
        Layout data dictionary, or None if file doesn't exist
    """
    if layout_path.exists():
        with open(layout_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_layout_data(layout_data: Dict[str, Any], layout_path: Path) -> None:
    """
    Save layout data to JSON file.
    
    Args:
        layout_data: Layout data dictionary
        layout_path: Path to save layout JSON file
    """
    layout_path.parent.mkdir(parents=True, exist_ok=True)
    with open(layout_path, 'w', encoding='utf-8') as f:
        json.dump(layout_data, f, indent=2, ensure_ascii=False)


def find_extracted_layout(synced_json_path: Path) -> Optional[Path]:
    """
    Find extracted layout file that was generated during sync.
    
    Layout files are generated with pattern: {synced_json_path.stem}-layout.json
    
    Args:
        synced_json_path: Path to synced JSON file
    
    Returns:
        Path to layout file if found, None otherwise
    """
    layout_path = synced_json_path.parent / f"{synced_json_path.stem}-layout.json"
    return layout_path if layout_path.exists() else None

