"""
Feature Domain Component

Represents a feature in the story map hierarchy.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from .story_io_component import StoryIOComponent
from .story_io_story import Story

if TYPE_CHECKING:
    from .story_io_feature import Feature


class Feature(StoryIOComponent):
    """Represents a feature containing stories."""
    
    def __init__(self, name: str, sequential_order: Optional[float] = None,
                 position: Optional[Any] = None, boundary: Optional[Any] = None,
                 flag: bool = False, parent: Optional[StoryIOComponent] = None,
                 story_count: Optional[int] = None):
        super().__init__(name, sequential_order, position, boundary, flag, parent)
        self._story_count = story_count
    
    @property
    def stories(self) -> List[Story]:
        """Get all stories in this feature."""
        return [child for child in self.children if isinstance(child, Story)]
    
    @property
    def story_count(self) -> Optional[int]:
        """Get estimated story count if stories are not fully enumerated."""
        return self._story_count
    
    @property
    def estimated_stories(self) -> Optional[int]:
        """Get estimated story count (alias for story_count)."""
        return self._story_count
    
    @property
    def total_stories(self) -> int:
        """Get total stories: actual stories + estimated stories."""
        actual_stories = len(self.stories)
        estimated = self._story_count or 0
        # If we have actual stories, use them; otherwise use estimate
        if actual_stories > 0:
            return actual_stories
        return estimated
    
    def synchronize(self) -> Dict[str, Any]:
        """Synchronize feature from external source (old format: features)."""
        result = {
            'name': self.name,
            'sequential_order': self.sequential_order,
            'stories': [s.synchronize() for s in self.stories]
        }
        if self._story_count is not None:
            result['story_count'] = self._story_count
            result['estimated_stories'] = self._story_count
        return result
    
    def synchronize_as_sub_epic(self) -> Dict[str, Any]:
        """Synchronize feature as sub_epic (new format: supports nested sub_epics)."""
        result = {
            'name': self.name,
            'sequential_order': self.sequential_order,
            'sub_epics': [f.synchronize_as_sub_epic() for f in self.features],
            'stories': [s.synchronize() for s in self.stories]
        }
        if self._story_count is not None:
            result['estimated_stories'] = self._story_count
        return result
    
    def synchronize_report(self) -> Dict[str, Any]:
        """Generate synchronization report for this feature."""
        return {
            'feature': self.name,
            'stories_count': len(self.stories),
            'estimated_stories': self._story_count,
            'total_stories': self.total_stories,
            'status': 'synchronized'
        }
    
    def compare(self, other: 'StoryIOComponent') -> Dict[str, Any]:
        """Compare this feature with another component."""
        if not isinstance(other, Feature):
            return {'match': False, 'reason': 'Type mismatch'}
        
        return {
            'match': self.name == other.name,
            'name_match': self.name == other.name,
            'sequential_order_match': self.sequential_order == other.sequential_order,
            'stories_count_match': len(self.stories) == len(other.stories)
        }
    
    def render(self) -> Dict[str, Any]:
        """Render feature to JSON representation (old format: features)."""
        result = {
            'name': self.name,
            'sequential_order': self.sequential_order,
            'users': [],  # Feature-level users from first story
            'stories': [s.render() for s in self.stories]
        }
        if self._story_count is not None:
            result['story_count'] = self._story_count
            result['estimated_stories'] = self._story_count
        return result
    
    def render_as_sub_epic(self) -> Dict[str, Any]:
        """Render feature as sub_epic (new format: supports nested sub_epics)."""
        result = {
            'name': self.name,
            'sequential_order': self.sequential_order,
            'sub_epics': [f.render_as_sub_epic() for f in self.features],
            'stories': [s.render() for s in self.stories]
        }
        if self._story_count is not None:
            result['estimated_stories'] = self._story_count
        return result
    
    @property
    def features(self) -> List['Feature']:
        """Get nested features (for sub_epic support)."""
        return [child for child in self.children if isinstance(child, Feature)]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert feature to dictionary."""
        result = super().to_dict()
        result['type'] = 'feature'
        result['stories'] = [s.to_dict() for s in self.stories]
        if self._story_count is not None:
            result['story_count'] = self._story_count
            result['estimated_stories'] = self._story_count
        return result

