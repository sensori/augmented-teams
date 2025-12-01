"""
Load story graph data for multiple epics features test.

GIVEN: Story graph with multiple epics and features
- Loads input story graph JSON (if input_story_graph.json exists in 1_given)
- Loads expected story graph JSON for comparison
- Provides access to given test data
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directories to path
given_dir = Path(__file__).parent
scenario_dir = given_dir.parent
acceptance_dir = scenario_dir.parent.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(acceptance_dir.parent / "spec_by_example"))

from story_graph_layout_helper import load_story_graph


def get_story_graph() -> Dict[str, Any]:
    """
    Load input story graph from given data.
    Uses input_story_graph.json in 1_given if it exists, otherwise uses expected JSON.
    
    Returns:
        Story graph dictionary
    """
    story_graph_path = get_story_graph_path()
    return load_story_graph(story_graph_path)


def get_story_graph_path() -> Path:
    """
    Get path to input story graph JSON from given data.
    Checks for input_story_graph.json in 1_given first, then falls back to expected JSON.
    
    Returns:
        Path to story graph JSON file
    """
    # Check for input file in 1_given first
    input_file = given_dir / "input_story_graph.json"
    if input_file.exists():
        return input_file
    
    # Fall back to expected JSON
    return given_dir / "story-graph-multiple-epics-features.json"


def get_expected_story_graph_path() -> Path:
    """
    Get path to expected story graph JSON for comparison.
    
    Returns:
        Path to expected story graph JSON file
    """
    return given_dir / "story-graph-multiple-epics-features.json"
