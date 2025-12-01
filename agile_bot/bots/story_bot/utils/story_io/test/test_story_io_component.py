"""
BDD Tests for StoryIOComponent

Tests for the base StoryIOComponent class following Mamba BDD patterns.
"""

from mamba import description, context, it, before
from expects import expect, equal, be_none, be_true, be_false, raise_error

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from story_io.story_io_component import StoryIOComponent
from story_io.story_io_position import Position, Boundary


class TestComponent(StoryIOComponent):
    """Test implementation of StoryIOComponent for testing."""
    
    def synchronize(self):
        return {'name': self.name}
    
    def synchronize_report(self):
        return {'status': 'test'}
    
    def compare(self, other):
        return {'match': self.name == other.name}
    
    def render(self):
        return {'name': self.name}


with description('a StoryIOComponent'):
    with context('that is newly created'):
        with before.each:
            self.component = TestComponent(name='Test Component')
        
        with it('should have the specified name'):
            expect(self.component.name).to(equal('Test Component'))
        
        with it('should have no parent'):
            expect(self.component.parent).to(be_none)
        
        with it('should have no children'):
            expect(self.component.children).to(equal([]))
        
        with it('should not be flagged'):
            expect(self.component.flag).to(be_false)
    
    with context('that has a position'):
        with before.each:
            self.position = Position(x=10.0, y=20.0)
            self.component = TestComponent(name='Test', position=self.position)
        
        with it('should store the position'):
            expect(self.component.position.x).to(equal(10.0))
            expect(self.component.position.y).to(equal(20.0))
    
    with context('that has children'):
        with before.each:
            self.parent = TestComponent(name='Parent')
            self.child1 = TestComponent(name='Child 1')
            self.child2 = TestComponent(name='Child 2')
        
        with it('should add child when child parent is set'):
            self.child1.parent = self.parent
            expect(self.parent.children).to(equal([self.child1]))
        
        with it('should have multiple children'):
            self.child1.parent = self.parent
            self.child2.parent = self.parent
            expect(len(self.parent.children)).to(equal(2))
        
        with it('should set child parent when adding child'):
            self.child1.parent = self.parent
            expect(self.child1.parent).to(equal(self.parent))
    
    with context('that searches for children'):
        with before.each:
            self.parent = TestComponent(name='Parent Component')
            self.child1 = TestComponent(name='Child Alpha')
            self.child2 = TestComponent(name='Child Beta')
            self.child1.parent = self.parent
            self.child2.parent = self.parent
        
        with it('should find children matching query'):
            results = self.parent.search_for_all_children('Alpha')
            expect(len(results)).to(equal(1))
            expect(results[0].name).to(equal('Child Alpha'))
        
        with it('should find parent when query matches'):
            results = self.parent.search_for_all_children('Parent')
            expect(len(results)).to(equal(1))
            expect(results[0].name).to(equal('Parent Component'))
        
        with it('should perform case-insensitive search'):
            results = self.parent.search_for_all_children('beta')
            expect(len(results)).to(equal(1))
            expect(results[0].name).to(equal('Child Beta'))
    
    with context('that has leaf components'):
        with before.each:
            self.root = TestComponent(name='Root')
            self.child1 = TestComponent(name='Child 1')
            self.child2 = TestComponent(name='Child 2')
            self.grandchild = TestComponent(name='Grandchild')
            self.child1.parent = self.root
            self.child2.parent = self.root
            self.grandchild.parent = self.child1
        
        with it('should return only leaf nodes'):
            leafs = self.root.leafs
            expect(len(leafs)).to(equal(2))
            expect(leafs[0].name).to(equal('Grandchild'))
            expect(leafs[1].name).to(equal('Child 2'))
    
    with context('that reorders siblings'):
        with before.each:
            self.parent = TestComponent(name='Parent')
            self.child1 = TestComponent(name='Child 1')
            self.child2 = TestComponent(name='Child 2')
            self.child3 = TestComponent(name='Child 3')
            self.child1.parent = self.parent
            self.child2.parent = self.parent
            self.child3.parent = self.parent
        
        with it('should move component before target'):
            self.child3.move_before(self.child2)
            children = self.parent.children
            expect(children[0].name).to(equal('Child 1'))
            expect(children[1].name).to(equal('Child 3'))
            expect(children[2].name).to(equal('Child 2'))
        
        with it('should raise error when moving components with different parents'):
            other_parent = TestComponent(name='Other Parent')
            other_child = TestComponent(name='Other Child')
            other_child.parent = other_parent
            
            expect(lambda: self.child1.move_before(other_child)).to(raise_error(ValueError))
    
    with context('that changes parent'):
        with before.each:
            self.old_parent = TestComponent(name='Old Parent')
            self.new_parent = TestComponent(name='New Parent')
            self.child = TestComponent(name='Child')
            self.child.parent = self.old_parent
        
        with it('should move child to new parent'):
            self.child.change_parent(self.new_parent)
            expect(self.child.parent).to(equal(self.new_parent))
            expect(len(self.new_parent.children)).to(equal(1))
        
        with it('should remove child from old parent'):
            self.child.change_parent(self.new_parent)
            expect(len(self.old_parent.children)).to(equal(0))
    
    with context('that converts to dictionary'):
        with before.each:
            self.component = TestComponent(name='Test Component', sequential_order=1.0)
            self.child = TestComponent(name='Child')
            self.child.parent = self.component
        
        with it('should include name in dictionary'):
            result = self.component.to_dict()
            expect(result['name']).to(equal('Test Component'))
        
        with it('should include sequential order in dictionary'):
            result = self.component.to_dict()
            expect(result['sequential_order']).to(equal(1.0))
        
        with it('should include children in dictionary'):
            result = self.component.to_dict()
            expect(len(result['children'])).to(equal(1))
    
    with context('that determines children at level'):
        with before.each:
            self.root = TestComponent(name='Root')
            self.child1 = TestComponent(name='Child 1')
            self.child2 = TestComponent(name='Child 2')
            self.grandchild = TestComponent(name='Grandchild')
            self.child1.parent = self.root
            self.child2.parent = self.root
            self.grandchild.parent = self.child1
        
        with it('should return self at level 0'):
            results = self.root.children_at_level(0)
            expect(len(results)).to(equal(1))
            expect(results[0].name).to(equal('Root'))
        
        with it('should return direct children at level 1'):
            results = self.root.children_at_level(1)
            expect(len(results)).to(equal(2))
        
        with it('should return grandchildren at level 2'):
            results = self.root.children_at_level(2)
            expect(len(results)).to(equal(1))
            expect(results[0].name).to(equal('Grandchild'))
    
    with context('that determines children'):
        with before.each:
            self.root = TestComponent(name='Root')
            self.child = TestComponent(name='Child')
            self.child.parent = self.root
        
        with it('should return children at specified level'):
            results = self.root.determine_children(1)
            expect(len(results)).to(equal(1))
            expect(results[0].name).to(equal('Child'))

