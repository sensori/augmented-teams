"""
Load story graph and DrawIO data for preserve all element and positioning test.

GIVEN: Story graph with many users and sequential and optional stories
- Loads story graph JSON
- Loads DrawIO file
- Provides access to given test data
"""
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

# Add parent directories to path
given_dir = Path(__file__).parent
scenario_dir = given_dir.parent
acceptance_dir = scenario_dir.parent.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(acceptance_dir.parent / "spec_by_example"))
sys.path.insert(0, str(scenario_dir.parent))  # Add scenarios directory for story_graph_layout_helper

from story_graph_layout_helper import load_story_graph, load_layout_data


def get_story_graph() -> Dict[str, Any]:
    """
    Load story graph from given data.
    
    Returns:
        Story graph dictionary
    """
    story_graph_path = given_dir / "story-graph-with-many-users-and-optional-stories.json"
    return load_story_graph(story_graph_path)


def get_drawio_path() -> Path:
    """
    Get path to DrawIO file from given data.
    
    Returns:
        Path to DrawIO file
    """
    return given_dir / "story-outline-with-complex-custom-positoning.drawio"


def get_story_graph_path() -> Path:
    """
    Get path to story graph JSON from given data.
    
    Returns:
        Path to story graph JSON file
    """
    return given_dir / "story-graph-with-many-users-and-optional-stories.json"


def get_drawio_file() -> Path:
    """
    Get DrawIO file path (alias for get_drawio_path for consistency).
    
    Returns:
        Path to DrawIO file
    """
    return get_drawio_path()

