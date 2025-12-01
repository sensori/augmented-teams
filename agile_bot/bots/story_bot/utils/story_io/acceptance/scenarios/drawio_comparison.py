"""
Common utilities for comparing DrawIO files in acceptance tests.

Shared comparison logic used across multiple test scenarios.
"""
from pathlib import Path
import xml.etree.ElementTree as ET


def compare_drawios(drawio1_path: Path, drawio2_path: Path, tolerance: float = 1.0) -> dict:
    """
    Compare two DrawIO files by comparing XML structure directly.
    Compares positions, sizes, text content, and styles of all cells.
    
    Args:
        drawio1_path: Path to first DrawIO file
        drawio2_path: Path to second DrawIO file
        tolerance: Tolerance for floating point differences (default: 1.0px)
    
    Returns:
        Dictionary with:
        - 'match': bool - True if files match
        - 'differences': list - List of difference descriptions
        - 'message': str - Summary message
    """
    differences = []
    
    # Validate file paths
    if not drawio1_path.exists():
        return {
            'match': False,
            'differences': [f"First DrawIO file not found: {drawio1_path}"],
            'message': f"File not found: {drawio1_path}"
        }
    
    if not drawio2_path.exists():
        return {
            'match': False,
            'differences': [f"Second DrawIO file not found: {drawio2_path}"],
            'message': f"File not found: {drawio2_path}"
        }
    
    # Parse both DrawIO files (they are XML, not JSON)
    try:
        tree1 = ET.parse(drawio1_path)
        root1 = tree1.getroot()
        tree2 = ET.parse(drawio2_path)
        root2 = tree2.getroot()
    except ET.ParseError as e:
        return {
            'match': False,
            'differences': [f"Failed to parse DrawIO XML files: {e}"],
            'message': f"XML parse error: {e}"
        }
    except Exception as e:
        return {
            'match': False,
            'differences': [f"Failed to read DrawIO files: {e}"],
            'message': f"Error: {e}"
        }
    
    # Find all mxCell elements (excluding root cells with id="0" and id="1")
    def get_cells(root):
        cells = {}
        for cell in root.findall('.//mxCell'):
            cell_id = cell.get('id')
            if cell_id and cell_id not in ['0', '1']:
                cells[cell_id] = cell
        return cells
    
    cells1 = get_cells(root1)
    cells2 = get_cells(root2)
    
    # Compare cell counts
    if len(cells1) != len(cells2):
        differences.append(f"Cell count mismatch: {len(cells1)} vs {len(cells2)}")
    
    # Get all cell IDs (union of both)
    all_cell_ids = set(cells1.keys()) | set(cells2.keys())
    
    # Compare each cell
    for cell_id in sorted(all_cell_ids):
        cell1 = cells1.get(cell_id)
        cell2 = cells2.get(cell_id)
        
        if cell1 is None:
            differences.append(f"Cell {cell_id} missing in first DrawIO")
            continue
        if cell2 is None:
            differences.append(f"Cell {cell_id} missing in second DrawIO")
            continue
        
        # Compare value (text content)
        value1 = cell1.get('value', '')
        value2 = cell2.get('value', '')
        if value1 != value2:
            # Only report if it's a significant difference (not just whitespace)
            if value1.strip() != value2.strip():
                differences.append(f"Cell {cell_id} value mismatch")
        
        # Compare style
        style1 = cell1.get('style', '')
        style2 = cell2.get('style', '')
        if style1 != style2:
            differences.append(f"Cell {cell_id} style mismatch")
        
        # Compare geometry (position and size)
        geom1 = cell1.find('mxGeometry')
        geom2 = cell2.find('mxGeometry')
        
        if geom1 is None and geom2 is None:
            continue
        if geom1 is None:
            differences.append(f"Cell {cell_id} missing geometry in first DrawIO")
            continue
        if geom2 is None:
            differences.append(f"Cell {cell_id} missing geometry in second DrawIO")
            continue
        
        # Compare x, y, width, height
        x1 = float(geom1.get('x', 0))
        x2 = float(geom2.get('x', 0))
        y1 = float(geom1.get('y', 0))
        y2 = float(geom2.get('y', 0))
        w1 = float(geom1.get('width', 0))
        w2 = float(geom2.get('width', 0))
        h1 = float(geom1.get('height', 0))
        h2 = float(geom2.get('height', 0))
        
        # Allow small floating point differences
        if abs(x1 - x2) > tolerance:
            differences.append(f"Cell {cell_id} x position mismatch: {x1} vs {x2}")
        if abs(y1 - y2) > tolerance:
            differences.append(f"Cell {cell_id} y position mismatch: {y1} vs {y2}")
        if abs(w1 - w2) > tolerance:
            differences.append(f"Cell {cell_id} width mismatch: {w1} vs {w2}")
        if abs(h1 - h2) > tolerance:
            differences.append(f"Cell {cell_id} height mismatch: {h1} vs {h2}")
    
    return {
        'match': len(differences) == 0,
        'differences': differences,
        'message': 'DrawIOs match' if len(differences) == 0 else f'{len(differences)} differences found'
    }

