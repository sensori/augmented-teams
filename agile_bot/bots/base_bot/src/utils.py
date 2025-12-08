from pathlib import Path
import json
from typing import Dict, Any


def read_json_file(file_path: Path) -> Dict[str, Any]:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    return json.loads(file_path.read_text(encoding='utf-8'))
























