"""
DrawIO Synchronizer

Handles synchronization of story diagrams from DrawIO XML format.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union

# Import the existing synchronizer functions
# story_map_drawio_synchronizer is in the same directory (story_io/)
from .story_map_drawio_synchronizer import (
    synchronize_story_graph_from_drawio_outline,
    synchronize_story_graph_from_drawio_increments,
    generate_merge_report,
    merge_story_graphs
)


class DrawIOSynchronizer:
    """Synchronizer for extracting story diagrams from DrawIO XML format."""
    
    def render(self, input_path: Union[str, Path], output_path: Union[str, Path], 
               renderer_command: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Render story graph to DrawIO diagram.
        
        Lightweight wrapper around StoryIODiagram render methods.
        
        Args:
            input_path: Path to story graph JSON file
            output_path: Path for output DrawIO file
            renderer_command: Command variant ('render-outline', 'render-increments', 'render-exploration')
            **kwargs: Additional arguments (e.g., layout_data)
        
        Returns:
            Dictionary with output_path and summary
        """
        from .story_io_diagram import StoryIODiagram
        
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        if renderer_command == 'render-outline' or renderer_command is None:
            return StoryIODiagram.render_outline_from_graph(input_path, output_path, **kwargs)
        elif renderer_command == 'render-increments':
            return StoryIODiagram.render_increments_from_graph(input_path, output_path, **kwargs)
        elif renderer_command == 'render-exploration':
            return StoryIODiagram.render_exploration_from_graph(input_path, output_path, **kwargs)
        else:
            raise ValueError(f"Unknown renderer_command: {renderer_command}")
    
    def synchronize_outline(self, drawio_path: Path,
                           original_path: Optional[Path] = None,
                           output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Synchronize story graph from DrawIO outline file.
        
        Args:
            drawio_path: Path to DrawIO outline file
            original_path: Optional path to original story graph for comparison
            output_path: Optional path to write extracted JSON
        
        Returns:
            Extracted story graph data
        """
        if output_path is None:
            output_path = drawio_path.parent / "story-graph-drawio-extracted.json"
        
        return synchronize_story_graph_from_drawio_outline(
            drawio_path=drawio_path,
            output_path=output_path,
            original_path=original_path
        )
    
    def synchronize_increments(self, drawio_path: Path,
                              original_path: Optional[Path] = None,
                              output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Synchronize story graph from DrawIO increments file.
        
        Args:
            drawio_path: Path to DrawIO file with increments
            original_path: Optional path to original story graph for comparison
            output_path: Optional path to write extracted JSON
        
        Returns:
            Extracted story graph data
        """
        if output_path is None:
            output_path = drawio_path.parent / "story-graph-drawio-extracted.json"
        
        return synchronize_story_graph_from_drawio_increments(
            drawio_path=drawio_path,
            output_path=output_path,
            original_path=original_path
        )
    
    def generate_merge_report(self, extracted_path: Union[str, Path],
                              original_path: Union[str, Path],
                              report_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Generate a merge report comparing extracted and original story graphs.
        
        Args:
            extracted_path: Path to extracted story graph JSON
            original_path: Path to original story graph JSON
            report_path: Optional path to write report JSON
        
        Returns:
            Dictionary containing merge report data
        """
        extracted_path = Path(extracted_path)
        original_path = Path(original_path)
        if report_path:
            report_path = Path(report_path)
        
        return generate_merge_report(extracted_path, original_path, report_path)
    
    def merge_story_graphs(self, extracted_path: Union[str, Path],
                          original_path: Union[str, Path],
                          report_path: Union[str, Path],
                          output_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Merge extracted story graph with original, preserving Steps from original.
        
        Args:
            extracted_path: Path to extracted story graph JSON
            original_path: Path to original story graph JSON
            report_path: Path to merge report JSON
            output_path: Path to write merged story graph JSON
        
        Returns:
            Dictionary containing merged story graph
        """
        extracted_path = Path(extracted_path)
        original_path = Path(original_path)
        report_path = Path(report_path)
        output_path = Path(output_path)
        
        return merge_story_graphs(extracted_path, original_path, report_path, output_path)

