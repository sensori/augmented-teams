"""
Folder Structure Synchronizer

Creates folder hierarchy from story-graph.json matching the story structure.
Follows arrange behavior rules with emoji prefixes.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union
import json


class FolderStructureSynchronizer:
    """Synchronizer for creating folder structure from story graph."""
    
    def render(self, input_path: Union[str, Path], output_path: Union[str, Path], 
               **kwargs) -> Dict[str, Any]:
        """
        Render folder structure from story graph.
        
        Args:
            input_path: Path to story graph JSON file
            output_path: Base path where map/ folder structure will be created
                        (typically project_path/docs/stories, creates map/ subdirectory)
            **kwargs: Additional arguments (unused for now)
        
        Returns:
            Dictionary with output_path and summary
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        map_path = output_path / "map"
        
        # Read story graph
        if not input_path.exists():
            raise FileNotFoundError(f"Story graph not found at {input_path}")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        epics = data.get('epics', [])
        
        # Create base map directory
        map_path.mkdir(parents=True, exist_ok=True)
        
        created_count = 0
        epic_folders = []
        sub_epic_folders = []
        
        # Iterate through epics and sub_epics
        for epic in epics:
            epic_name = epic.get('name', '')
            if not epic_name:
                continue
            
            # Create epic folder with emoji
            epic_folder = map_path / f"🎯 {epic_name}"
            try:
                epic_folder.mkdir(exist_ok=True)
                epic_folders.append(epic_folder.name)
                created_count += 1
            except Exception as e:
                raise RuntimeError(f"Error creating epic folder {epic_folder.name}: {e}")
            
            # Get sub_epics (features)
            sub_epics = epic.get('sub_epics', []) or epic.get('features', [])
            
            for sub_epic in sub_epics:
                sub_epic_name = sub_epic.get('name', '')
                if not sub_epic_name:
                    continue
                
                # Create sub_epic folder with emoji
                sub_epic_folder = epic_folder / f"⚙️ {sub_epic_name}"
                try:
                    sub_epic_folder.mkdir(exist_ok=True)
                    sub_epic_folders.append(sub_epic_folder.name)
                    created_count += 1
                except Exception as e:
                    raise RuntimeError(f"Error creating sub_epic folder {sub_epic_folder.name}: {e}")
        
        return {
            'output_path': map_path,
            'summary': {
                'epics': len(epic_folders),
                'sub_epics': len(sub_epic_folders),
                'total_folders': created_count
            }
        }
