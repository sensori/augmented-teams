"""
Load story graph and layout data for exploration renders acceptance criteria test.

GIVEN: Story graph with acceptance criteria and explore diagram with layout
- Loads story graph JSON
- Loads layout data JSON
- Provides access to given test data
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directories to path
given_dir = Path(__file__).parent
spec_dir = given_dir.parent.parent
story_io_dir = spec_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(spec_dir))

from story_graph_layout_helper import load_story_graph, load_layout_data


def get_story_graph() -> Dict[str, Any]:
    """
    Load story graph from given data.
    
    Returns:
        Story graph dictionary
    """
    story_graph_path = given_dir / "story-graph-with-acceptance-criteria.json"
    return load_story_graph(story_graph_path)


def get_layout_data() -> Optional[Dict[str, Any]]:
    """
    Load layout data from given data.
    
    Returns:
        Layout data dictionary, or None if not found
    """
    layout_path = given_dir / "story-outline-drawio-with-acceptance-criteria-layout.json"
    return load_layout_data(layout_path)


def get_story_graph_path() -> Path:
    """
    Get path to story graph JSON from given data.
    
    Returns:
        Path to story graph JSON file
    """
    return given_dir / "story_graph.json"


def get_layout_path() -> Path:
    """
    Get path to layout JSON from given data.
    
    Returns:
        Path to layout JSON file
    """
    return given_dir / "story-outline-layout.json"

