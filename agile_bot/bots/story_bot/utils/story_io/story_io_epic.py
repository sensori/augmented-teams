"""
Epic Domain Component

Represents an epic in the story map hierarchy.
"""

from typing import List, Dict, Any, Optional
from dataclasses import field
from .story_io_component import StoryIOComponent
from .story_io_feature import Feature
from .story_io_story import Story


class Epic(StoryIOComponent):
    """Represents an epic containing features and stories."""
    
    def __init__(self, name: str, sequential_order: Optional[float] = None,
                 position: Optional[Any] = None, boundary: Optional[Any] = None,
                 flag: bool = False, parent: Optional[StoryIOComponent] = None,
                 estimated_stories: Optional[int] = None):
        super().__init__(name, sequential_order, position, boundary, flag, parent)
        self._estimated_stories = estimated_stories
    
    @property
    def features(self) -> List[Feature]:
        """Get all features in this epic."""
        return [child for child in self.children if isinstance(child, Feature)]
    
    @property
    def stories(self) -> List[Story]:
        """Get all stories directly in this epic (not through features)."""
        return [child for child in self.children if isinstance(child, Story)]
    
    @property
    def estimated_stories(self) -> Optional[int]:
        """Get estimated story count if stories are not fully enumerated."""
        return self._estimated_stories
    
    @property
    def total_stories(self) -> int:
        """Get total stories: actual stories + estimated stories from features."""
        actual_stories = len(self.stories)
        # Sum actual stories from all features
        feature_stories = sum(len(feature.stories) for feature in self.features)
        # Sum estimated stories from features (that don't have actual stories)
        estimated_from_features = sum(
            (feature.estimated_stories or 0) if feature.estimated_stories and len(feature.stories) == 0 
            else 0 
            for feature in self.features
        )
        # Epic-level estimated stories (if no features exist or features are incomplete)
        epic_estimated = self._estimated_stories or 0
        # Use epic estimate if it exists and no features have stories yet
        if epic_estimated > 0 and feature_stories == 0 and estimated_from_features == 0:
            return actual_stories + epic_estimated
        return actual_stories + feature_stories + estimated_from_features
    
    def add_feature(self, feature: Feature, target: Optional[Feature] = None) -> None:
        """Add a feature to this epic."""
        if target:
            feature.change_parent(self, target)
        else:
            feature.change_parent(self)
    
    def remove_feature(self, feature: Feature) -> None:
        """Remove a feature from this epic."""
        if feature in self.features:
            self._remove_child(feature)
    
    def synchronize(self) -> Dict[str, Any]:
        """Synchronize epic from external source (new format: sub_epics)."""
        result = {
            'name': self.name,
            'sequential_order': self.sequential_order,
            'sub_epics': [f.synchronize_as_sub_epic() for f in self.features],
            'stories': [s.synchronize() for s in self.stories]
        }
        if self._estimated_stories is not None:
            result['estimated_stories'] = self._estimated_stories
        return result
    
    def synchronize_report(self) -> Dict[str, Any]:
        """Generate synchronization report for this epic."""
        return {
            'epic': self.name,
            'features_count': len(self.features),
            'stories_count': len(self.stories),
            'estimated_stories': self._estimated_stories,
            'total_stories': self.total_stories,
            'total_children': len(self.children),
            'status': 'synchronized'
        }
    
    def compare(self, other: 'StoryIOComponent') -> Dict[str, Any]:
        """Compare this epic with another component."""
        if not isinstance(other, Epic):
            return {'match': False, 'reason': 'Type mismatch'}
        
        return {
            'match': self.name == other.name,
            'name_match': self.name == other.name,
            'sequential_order_match': self.sequential_order == other.sequential_order,
            'features_count_match': len(self.features) == len(other.features),
            'stories_count_match': len(self.stories) == len(other.stories)
        }
    
    def render(self) -> Dict[str, Any]:
        """Render epic to JSON representation (new format: sub_epics)."""
        result = {
            'name': self.name,
            'sequential_order': self.sequential_order,
            'sub_epics': [f.render_as_sub_epic() for f in self.features],
            'stories': [s.render() for s in self.stories]
        }
        if self._estimated_stories is not None:
            result['estimated_stories'] = self._estimated_stories
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert epic to dictionary."""
        result = super().to_dict()
        result['type'] = 'epic'
        result['features'] = [f.to_dict() for f in self.features]
        if self._estimated_stories is not None:
            result['estimated_stories'] = self._estimated_stories
        return result

