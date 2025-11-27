"""
Domain Driven Design Agent Builders

Builders for creating structured content and folder structures from Domain Graph JSON.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import shutil
from datetime import datetime


class BaseBuilder:
    """Base builder class with common functionality"""
    
    def __init__(self, project_path: Path, structured_content_path: Optional[Path] = None):
        """
        Initialize builder with project path and optional structured content path.
        
        Args:
            project_path: Path to project root
            structured_content_path: Optional path to structured.json file
        """
        self.project_path = Path(project_path)
        self.structured_content_path = structured_content_path or self._find_structured_json()
    
    def _find_structured_json(self) -> Optional[Path]:
        """Find structured.json in docs/domain directory"""
        structured_path = self.project_path / "docs" / "domain" / "structured.json"
        if structured_path.exists():
            return structured_path
        return None
    
    def _load_domain_graph(self) -> Dict[str, Any]:
        """Load domain graph from structured.json"""
        if not self.structured_content_path or not self.structured_content_path.exists():
            raise FileNotFoundError(
                f"Structured content file not found: {self.structured_content_path}. "
                "Ensure shaping phase has been completed."
            )
        
        with open(self.structured_content_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _slugify(self, text: str) -> str:
        """Convert text to kebab-case slug"""
        return text.lower().replace(' ', '-').replace('_', '-').replace('/', '-')


class DomainFolderStructureBuilder(BaseBuilder):
    """Builder for creating folder structure from Domain Graph"""
    
    def build(self, create_aggregate_files: bool = False) -> Dict[str, Any]:
        """
        Build folder structure from Domain Graph JSON.
        
        Args:
            create_aggregate_files: If True, create aggregate stub files. If False, only create folders.
        
        Returns:
            Dictionary with operation results (created, existing, archived, etc.)
        """
        domain_graph = self._load_domain_graph()
        
        # Determine base directory (docs/domain/map)
        map_base = self.project_path / "docs" / "domain" / "map"
        map_base.mkdir(parents=True, exist_ok=True)
        
        # Create timestamp for archiving
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        archive_dir = map_base / "z_archive" / timestamp
        
        # Track operations
        created_folders: List[str] = []
        created_aggregates: List[str] = []
        archived_folders: List[str] = []
        existing_folders: List[str] = []
        
        # Get existing bounded context folders
        existing_bc_folders = set()
        if map_base.exists():
            for item in map_base.iterdir():
                if not item.is_dir():
                    continue
                if item.name in ['z_archive']:
                    continue
                if item.name.startswith('🏛️') or item.name.startswith('bc-'):
                    existing_bc_folders.add(item.name)
        
        # Process bounded contexts from domain graph
        bounded_contexts = domain_graph.get("bounded_contexts", [])
        
        for bc in bounded_contexts:
            bc_name = bc.get("name", "").strip()
            if not bc_name:
                continue
            
            # Create bounded context folder name with emoji prefix
            bc_folder_name = f'🏛️ {bc_name}'
            bc_path = map_base / bc_folder_name
            
            # Remove from existing set if found
            if bc_folder_name in existing_bc_folders:
                existing_bc_folders.discard(bc_folder_name)
                existing_folders.append(bc_folder_name)
            
            # Create bounded context folder if doesn't exist
            if not bc_path.exists():
                bc_path.mkdir(parents=True, exist_ok=True)
                created_folders.append(str(bc_path.relative_to(map_base)))
            
            # Process aggregates
            aggregates = bc.get("aggregates", [])
            for aggregate in aggregates:
                aggregate_name = aggregate.get("name", "").strip()
                if not aggregate_name:
                    continue
                
                # Create aggregate folder name with emoji prefix
                aggregate_folder_name = f'📦 {aggregate_name}'
                aggregate_path = bc_path / aggregate_folder_name
                
                # Create aggregate folder if doesn't exist
                if not aggregate_path.exists():
                    aggregate_path.mkdir(parents=True, exist_ok=True)
                    created_folders.append(str(aggregate_path.relative_to(map_base)))
                
                # Process aggregate files if create_aggregate_files is True
                if create_aggregate_files:
                    # Create aggregate specification file
                    aggregate_filename = f'📋 {aggregate_name}.md'
                    aggregate_file_path = aggregate_path / aggregate_filename
                    
                    if not aggregate_file_path.exists():
                        aggregate_content = self._create_aggregate_stub(
                            aggregate_name, bc_name, map_base
                        )
                        aggregate_file_path.write_text(aggregate_content, encoding='utf-8')
                        created_aggregates.append(str(aggregate_file_path.relative_to(map_base)))
        
        # Archive obsolete bounded context folders
        if existing_bc_folders:
            for obsolete_folder in existing_bc_folders:
                source_path = map_base / obsolete_folder
                if source_path.is_dir():
                    # Create archive directory if needed
                    if not archive_dir.exists():
                        archive_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Move to archive
                    dest_path = archive_dir / obsolete_folder
                    shutil.move(str(source_path), str(dest_path))
                    archived_folders.append(f"{obsolete_folder} -> z_archive/{timestamp}/")
        
        return {
            "created_folders": created_folders,
            "created_aggregates": created_aggregates,
            "archived_folders": archived_folders,
            "existing_folders": existing_folders,
            "summary": {
                "folders_created": len(created_folders),
                "aggregates_created": len(created_aggregates),
                "folders_archived": len(archived_folders),
                "folders_existing": len(existing_folders)
            }
        }
    
    def _create_aggregate_stub(self, aggregate_name: str, bc_name: str, map_base: Path) -> str:
        """Create basic aggregate stub with navigation breadcrumbs"""
        import urllib.parse
        
        # URL-encode paths for markdown compatibility
        bc_folder = urllib.parse.quote(f'🏛️ {bc_name}')
        
        domain_map_path = "../domain-map.md"
        bc_path = f"../{bc_folder}/"
        
        return f"""# {aggregate_name}

**Navigation:**
- [Domain Map]({domain_map_path})
- [Bounded Context: {bc_name}]({bc_path})

## Aggregate

{aggregate_name}

## Entities

(To be added during discovery phase)

## Value Objects

(To be added during discovery phase)

## Domain Events

(To be added during discovery phase)

## Commands

(To be added during discovery phase)

## Invariants

(To be added during exploration phase)

## Domain Rules

(To be added during exploration phase)
"""


def ddd_agent_build_folder_structure(
    project_path: str,
    structured_content_path: Optional[str] = None,
    create_aggregate_files: bool = False
) -> Dict[str, Any]:
    """
    Builder function for creating folder structure from Domain Graph.
    
    This function is called by the agent when executing the build_structure action
    for the arrange behavior.
    
    Args:
        project_path: Path to project root
        structured_content_path: Optional path to structured.json (auto-detected if not provided)
        create_aggregate_files: If True, create aggregate stub files. If False, only create folders.
    
    Returns:
        Dictionary with operation results
    """
    builder = DomainFolderStructureBuilder(
        project_path=Path(project_path),
        structured_content_path=Path(structured_content_path) if structured_content_path else None
    )
    return builder.build(create_aggregate_files=create_aggregate_files)

