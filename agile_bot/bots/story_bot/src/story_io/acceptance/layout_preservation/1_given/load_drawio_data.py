"""
Load DrawIO data for layout preservation test.

GIVEN: Original DrawIO file with layout
- Loads original DrawIO file
- Provides access to given test data
"""
import sys
from pathlib import Path

# Add parent directories to path
given_dir = Path(__file__).parent
test_dir = given_dir.parent
acceptance_dir = test_dir.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))


def get_original_drawio_path() -> Path:
    """
    Get path to original DrawIO file from given data.
    Checks multiple possible locations.
    
    Returns:
        Path to original DrawIO file
    """
    # Check acceptance input directory first
    input_dir = acceptance_dir / "input"
    original_drawio = input_dir / "story-map-outline-original.drawio"
    
    if original_drawio.exists():
        return original_drawio
    
    # Fallback to docs directory
    docs_drawio = src_dir.parent / "docs" / "stories" / "map" / "story-map-outline original.drawio"
    if docs_drawio.exists():
        return docs_drawio
    
    # If neither exists, return the expected path (will fail with clear error)
    return original_drawio




