"""
Load story graph data for nested workflow test.

GIVEN: Story graph with nested stories structure
- Loads story graph JSON
- Provides access to given test data
"""
import sys
from pathlib import Path
from typing import Dict, Any

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
    Load story graph from given data.
    
    Returns:
        Story graph dictionary
    """
    story_graph_path = given_dir / "story-graph.json"
    return load_story_graph(story_graph_path)


def get_story_graph_path() -> Path:
    """
    Get path to story graph JSON from given data.
    
    Returns:
        Path to story graph JSON file
    """
    return given_dir / "story-graph.json"
