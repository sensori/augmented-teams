"""
Tests for story map hyperlink functionality
Tests: connect_story_maps_to_documents, validate_story_map_links, correct_story_map_links
"""

import pytest
from pathlib import Path
import tempfile
import shutil

# Import functions to test
import sys
sys.path.insert(0, str(Path(__file__).parent))
from stories_runner import connect_story_maps_to_documents, validate_story_map_links, correct_story_map_links


@pytest.fixture
def temp_story_structure():
    """Create a temporary story map structure for testing"""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create directory structure
    stories_dir = temp_dir / "docs" / "stories"
    map_dir = stories_dir / "map"
    increments_dir = stories_dir / "increments"
    
    map_dir.mkdir(parents=True)
    increments_dir.mkdir(parents=True)
    
    # Create epic and feature folders
    epic_dir = map_dir / "🎯 Create Character"
    feature_dir = epic_dir / "⚙️ Establish Identity"
    feature_dir.mkdir(parents=True)
    
    # Create actual story files
    story1_path = feature_dir / "📝 User enters character name.md"
    story2_path = feature_dir / "📝 User selects power level.md"
    story3_path = feature_dir / "📝 User enters character concept.md"
    
    story1_path.write_text("# User enters character name\n\nTest story content", encoding='utf-8')
    story2_path.write_text("# User selects power level\n\nTest story content", encoding='utf-8')
    story3_path.write_text("# User enters character concept\n\nTest story content", encoding='utf-8')
    
    # Create story map file
    story_map_content = """# Product Story Map

## Epic Hierarchy

├─ 🎯 **Create Character**
│  │
│  ├─ ⚙️ **Establish Identity** (5 stories)
│  │  ├─ 📝 User enters character name
│  │  │   - and system saves name to character
│  │  ├─ 📝 User selects power level
│  │  │   - and system calculates and displays total point budget
│  │  ├─ 📝 User enters character concept
│  │  │   - and system saves concept to character
│  │  ├─ 📝 User enters identity numeric fields
│  │  │   - and system saves age, height, and weight
│  │  ├─ 📝 User clears identity field
│  │     - and system removes value and updates display
"""
    
    story_map_path = map_dir / "test-story-map.md"
    story_map_path.write_text(story_map_content, encoding='utf-8')
    
    # Create increments file
    increments_content = """# Story Map Increments

## Value Increment 1: Core Character Creation - NOW

│
├─ 🎯 **Create Character** (PARTIAL - 1 of 8 features)
│  │
│  ├─ ⚙️ **Establish Identity** (5 stories)
│  │  ├─ 📝 User enters character name
│  │  │   - and system saves name to character
│  │  ├─ 📝 User selects power level
│  │  │   - and system calculates and displays total point budget
│  │  ├─ 📝 User enters character concept
│  │  │   - and system saves concept to character
"""
    
    increments_path = increments_dir / "test-story-map-increments.md"
    increments_path.write_text(increments_content, encoding='utf-8')
    
    yield {
        'temp_dir': temp_dir,
        'map_dir': map_dir,
        'increments_dir': increments_dir,
        'story_map_path': story_map_path,
        'increments_path': increments_path,
        'story1_path': story1_path,
        'story2_path': story2_path,
        'story3_path': story3_path,
    }
    
    # Cleanup
    shutil.rmtree(temp_dir)


class TestConnectStoryMapsToDocuments:
    """Test the connect_story_maps_to_documents function"""
    
    def test_creates_links_for_existing_stories_in_story_map(self, temp_story_structure):
        """Should create hyperlinks for stories that exist as files"""
        story_map_path = temp_story_structure['story_map_path']
        
        # Run connection function
        links_created = connect_story_maps_to_documents(story_map_path, verbose=False)
        
        # Should create 3 links (story1, story2, story3 exist)
        assert links_created == 3
        
        # Read modified content
        content = story_map_path.read_text(encoding='utf-8')
        
        # Check that links were created with correct format
        assert '[📝 User enters character name](./🎯 Create Character/⚙️ Establish Identity/📝 User enters character name.md)' in content
        assert '[📝 User selects power level](./🎯 Create Character/⚙️ Establish Identity/📝 User selects power level.md)' in content
        assert '[📝 User enters character concept](./🎯 Create Character/⚙️ Establish Identity/📝 User enters character concept.md)' in content
    
    def test_does_not_create_links_for_missing_stories(self, temp_story_structure):
        """Should not create links for stories that don't exist as files"""
        story_map_path = temp_story_structure['story_map_path']
        
        # Run connection function
        connect_story_maps_to_documents(story_map_path, verbose=False)
        
        # Read modified content
        content = story_map_path.read_text(encoding='utf-8')
        
        # Stories 4 and 5 don't exist, should remain unlinked
        assert '📝 User enters identity numeric fields' in content
        assert '[📝 User enters identity numeric fields]' not in content
        assert '📝 User clears identity field' in content
        assert '[📝 User clears identity field]' not in content
    
    def test_creates_links_in_increments_file(self, temp_story_structure):
        """Should create links in increments file with correct relative path"""
        increments_path = temp_story_structure['increments_path']
        
        # Run connection function
        links_created = connect_story_maps_to_documents(increments_path, verbose=False)
        
        # Should create 3 links
        assert links_created == 3
        
        # Read modified content
        content = increments_path.read_text(encoding='utf-8')
        
        # Check that links use ../map/ prefix for increments file
        assert '[📝 User enters character name](../map/🎯 Create Character/⚙️ Establish Identity/📝 User enters character name.md)' in content
        assert '[📝 User selects power level](../map/🎯 Create Character/⚙️ Establish Identity/📝 User selects power level.md)' in content
    
    def test_preserves_indentation_and_tree_structure(self, temp_story_structure):
        """Should preserve tree characters and indentation when creating links"""
        story_map_path = temp_story_structure['story_map_path']
        
        # Run connection function
        connect_story_maps_to_documents(story_map_path, verbose=False)
        
        # Read modified content
        content = story_map_path.read_text(encoding='utf-8')
        
        # Check that tree structure is preserved
        assert '│  │  ├─ [📝 User enters character name]' in content
        assert '│  │  ├─ [📝 User selects power level]' in content
    
    def test_does_not_duplicate_links(self, temp_story_structure):
        """Should not create duplicate links if run multiple times"""
        story_map_path = temp_story_structure['story_map_path']
        
        # Run twice
        connect_story_maps_to_documents(story_map_path, verbose=False)
        links_created = connect_story_maps_to_documents(story_map_path, verbose=False)
        
        # Second run should create 0 links (already linked)
        assert links_created == 0
        
        # Read content
        content = story_map_path.read_text(encoding='utf-8')
        
        # Should not have double links like [[📝...]]
        assert '[[📝' not in content
    
    def test_handles_nonexistent_story_map(self):
        """Should handle nonexistent story map gracefully"""
        fake_path = Path("/nonexistent/story-map.md")
        
        links_created = connect_story_maps_to_documents(fake_path, verbose=False)
        
        assert links_created == 0


class TestValidateStoryMapLinks:
    """Test the validate_story_map_links function"""
    
    def test_validates_all_links_correct(self, temp_story_structure):
        """Should return no broken links when all links are valid"""
        story_map_path = temp_story_structure['story_map_path']
        
        # First create links
        connect_story_maps_to_documents(story_map_path, verbose=False)
        
        # Validate
        broken_links = validate_story_map_links(story_map_path, verbose=False)
        
        # Should have no broken links
        assert len(broken_links) == 0
    
    def test_detects_broken_links(self, temp_story_structure):
        """Should detect broken links"""
        story_map_path = temp_story_structure['story_map_path']
        
        # Manually create a broken link
        content = story_map_path.read_text(encoding='utf-8')
        # Add a link to non-existent story
        content += "\n│  │  ├─ [📝 Nonexistent Story](./🎯 Create Character/⚙️ Establish Identity/📝 Nonexistent Story.md)"
        story_map_path.write_text(content, encoding='utf-8')
        
        # Validate
        broken_links = validate_story_map_links(story_map_path, verbose=False)
        
        # Should detect 1 broken link
        assert len(broken_links) == 1
        assert broken_links[0][1] == '📝 Nonexistent Story'
        assert 'does not exist' in broken_links[0][3]
    
    def test_returns_line_numbers_for_broken_links(self, temp_story_structure):
        """Should return correct line numbers for broken links"""
        story_map_path = temp_story_structure['story_map_path']
        
        # Add broken link
        content = story_map_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        lines.append("│  │  ├─ [📝 Broken Link](./🎯 Create Character/⚙️ Establish Identity/📝 Broken Link.md)")
        content = '\n'.join(lines)
        story_map_path.write_text(content, encoding='utf-8')
        
        # Validate
        broken_links = validate_story_map_links(story_map_path, verbose=False)
        
        # Check line number is returned
        assert broken_links[0][0] > 0  # Line number should be positive


class TestCorrectStoryMapLinks:
    """Test the correct_story_map_links function"""
    
    def test_corrects_broken_links(self, temp_story_structure):
        """Should correct broken links to point to correct path"""
        story_map_path = temp_story_structure['story_map_path']
        story1_path = temp_story_structure['story1_path']
        
        # Create a broken link (wrong path)
        content = story_map_path.read_text(encoding='utf-8')
        content = content.replace(
            '│  │  ├─ 📝 User enters character name',
            '│  │  ├─ [📝 User enters character name](./wrong/path/📝 User enters character name.md)'
        )
        story_map_path.write_text(content, encoding='utf-8')
        
        # Verify link is broken
        broken_links = validate_story_map_links(story_map_path, verbose=False)
        assert len(broken_links) == 1
        
        # Correct links
        corrections_made = correct_story_map_links(story_map_path, verbose=False)
        
        # Should have corrected 1 link
        assert corrections_made == 1
        
        # Verify link is now correct
        broken_links = validate_story_map_links(story_map_path, verbose=False)
        assert len(broken_links) == 0
        
        # Check content has correct path
        content = story_map_path.read_text(encoding='utf-8')
        assert '[📝 User enters character name](./🎯 Create Character/⚙️ Establish Identity/📝 User enters character name.md)' in content
    
    def test_corrects_multiple_broken_links(self, temp_story_structure):
        """Should correct multiple broken links in one pass"""
        story_map_path = temp_story_structure['story_map_path']
        
        # Create multiple broken links
        content = story_map_path.read_text(encoding='utf-8')
        content = content.replace(
            '│  │  ├─ 📝 User enters character name',
            '│  │  ├─ [📝 User enters character name](./wrong/path1.md)'
        )
        content = content.replace(
            '│  │  ├─ 📝 User selects power level',
            '│  │  ├─ [📝 User selects power level](./wrong/path2.md)'
        )
        story_map_path.write_text(content, encoding='utf-8')
        
        # Correct links
        corrections_made = correct_story_map_links(story_map_path, verbose=False)
        
        # Should have corrected 2 links
        assert corrections_made == 2
        
        # Verify all links are now correct
        broken_links = validate_story_map_links(story_map_path, verbose=False)
        assert len(broken_links) == 0
    
    def test_handles_no_broken_links(self, temp_story_structure):
        """Should handle case when there are no broken links"""
        story_map_path = temp_story_structure['story_map_path']
        
        # Create valid links first
        connect_story_maps_to_documents(story_map_path, verbose=False)
        
        # Try to correct (should find nothing to fix)
        corrections_made = correct_story_map_links(story_map_path, verbose=False)
        
        # Should have corrected 0 links
        assert corrections_made == 0
    
    def test_corrects_increments_file_links(self, temp_story_structure):
        """Should correct broken links in increments file with correct ../map/ prefix"""
        increments_path = temp_story_structure['increments_path']
        
        # Create a broken link
        content = increments_path.read_text(encoding='utf-8')
        content = content.replace(
            '│  │  ├─ 📝 User enters character name',
            '│  │  ├─ [📝 User enters character name](./wrong/path.md)'
        )
        increments_path.write_text(content, encoding='utf-8')
        
        # Correct links
        corrections_made = correct_story_map_links(increments_path, verbose=False)
        
        # Should have corrected 1 link
        assert corrections_made == 1
        
        # Check content has correct path with ../map/ prefix
        content = increments_path.read_text(encoding='utf-8')
        assert '[📝 User enters character name](../map/🎯 Create Character/⚙️ Establish Identity/📝 User enters character name.md)' in content


class TestIntegration:
    """Integration tests combining all functions"""
    
    def test_full_workflow_connect_validate_correct(self, temp_story_structure):
        """Test full workflow: connect links, validate, break them, correct them"""
        story_map_path = temp_story_structure['story_map_path']
        
        # Step 1: Connect links
        links_created = connect_story_maps_to_documents(story_map_path, verbose=False)
        assert links_created == 3
        
        # Step 2: Validate - should be all good
        broken_links = validate_story_map_links(story_map_path, verbose=False)
        assert len(broken_links) == 0
        
        # Step 3: Manually break a link
        content = story_map_path.read_text(encoding='utf-8')
        content = content.replace(
            '[📝 User enters character name](./🎯 Create Character/⚙️ Establish Identity/📝 User enters character name.md)',
            '[📝 User enters character name](./broken/path.md)'
        )
        story_map_path.write_text(content, encoding='utf-8')
        
        # Step 4: Validate - should detect broken link
        broken_links = validate_story_map_links(story_map_path, verbose=False)
        assert len(broken_links) == 1
        
        # Step 5: Correct links
        corrections_made = correct_story_map_links(story_map_path, verbose=False)
        assert corrections_made == 1
        
        # Step 6: Final validation - should be all good again
        broken_links = validate_story_map_links(story_map_path, verbose=False)
        assert len(broken_links) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])









