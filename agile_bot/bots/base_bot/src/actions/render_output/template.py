"""
Template class.

Loads template content from template file.
"""
from pathlib import Path
from typing import Optional


class Template:
    """Template for rendering output.
    
    Domain Model:
        Property: content
    """
    
    def __init__(self, template_path: Path):
        """Initialize Template.
        
        Args:
            template_path: Path to template file
        """
        self._template_path = template_path
        self._content: Optional[str] = None
        self._load_template()
    
    def _load_template(self):
        """Load template content from file."""
        if not self._template_path.exists():
            raise FileNotFoundError(
                f'Template file not found: {self._template_path}'
            )
        
        self._content = self._template_path.read_text(encoding='utf-8')
    
    @property
    def content(self) -> str:
        """Get template content.
        
        Domain Model: content
        """
        return self._content
    
    @property
    def template_path(self) -> Path:
        """Get path to template file."""
        return self._template_path



