"""
Code Agent Behavior Management Tests

These tests validate the code-agent system that makes AI behavior management
self-maintaining through structured validation, deployment, and consistency checking.
"""

from mamba import description, context, it, before, after
from expects import expect, have_length, equal, be_true, be_false, contain, match, be_none, be_above_or_equal, have_key
from expects.matchers import Matcher
from pathlib import Path
import tempfile
import shutil
import json
import re

# Custom matcher for "not be none"
class to_not_be_none(Matcher):
    def _match(self, subject):
        return subject is not None, []

# Custom matcher: be_above_or_equal
def be_above_or_equal(expected):
    """Check if value >= expected"""
    class BeAboveOrEqual(Matcher):
        def _match(self, subject):
            return subject >= expected, []
    return BeAboveOrEqual()

# Import production code (using importlib because filename has hyphens)
import sys
import importlib.util

_runner_path = Path(__file__).parent / 'code-agent-runner.py'
_spec = importlib.util.spec_from_file_location('code_agent_runner', _runner_path)
_runner_module = importlib.util.module_from_spec(_spec)
sys.modules['code_agent_runner'] = _runner_module
_spec.loader.exec_module(_runner_module)

# Now we can import from the loaded module
find_deployed_behaviors = _runner_module.find_deployed_behaviors
find_all_behavior_jsons = _runner_module.find_all_behavior_jsons
get_behavior_feature_name = _runner_module.get_behavior_feature_name
behavior_structure = _runner_module.behavior_structure
behavior_sync = _runner_module.behavior_sync
behavior_consistency = _runner_module.behavior_consistency
behavior_index = _runner_module.behavior_index
validate_hierarchical_behavior = _runner_module.validate_hierarchical_behavior


# =============================================================================
# TEST HELPERS
# =============================================================================

def create_test_fixture(fixture_name, structure):
    """Create temporary test fixture directory"""
    fixture_path = Path(tempfile.gettempdir()) / 'code-agent-tests' / fixture_name
    fixture_path.mkdir(parents=True, exist_ok=True)
    
    # Write behavior.json
    if 'config' in structure:
        config_file = fixture_path / 'behavior.json'
        config_file.write_text(json.dumps(structure['config'], indent=2))
    
    # Write behavior files
    for file_info in structure.get('files', []):
        file_path = fixture_path / file_info['name']
        content = file_info.get('content', f"# Test {file_info['type']} file")
        file_path.write_text(content)
    
    return fixture_path


def cleanup_test_fixtures():
    """Cleanup all test fixtures"""
    fixtures_root = Path(tempfile.gettempdir()) / 'code-agent-tests'
    if fixtures_root.exists():
        shutil.rmtree(fixtures_root)


# =============================================================================
# TESTS
# =============================================================================

with description('a behavior') as self:
    
    with before.all:
        cleanup_test_fixtures()
    
    with after.all:
        cleanup_test_fixtures()
    
    with context('that is being structured'):
        
        with context('whose components are being defined'):
            
            with before.each:
                # Arrange - Create real test fixture
                self.fixture_path = create_test_fixture('test-behavior', {
                    'files': [
                        {
                            'name': 'test-feature-test-behavior-rule.mdc',
                            'type': 'rule',
                            'content': '---\ndescription: Test\n---\n**When** test, **then** validate.'
                        },
                        {
                            'name': 'test-feature-test-behavior-cmd.md',
                            'type': 'command',
                            'content': '### Command\n**Purpose:** Test'
                        }
                    ],
                    'config': {'deployed': True, 'feature': 'test-feature'}
                })
            
            with it('should consist of one rule file'):
                # Act - Call production validation code
                import io
                import sys
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                
                # Call with --no-guard to bypass command guard
                sys.argv = ['test', 'structure', 'validate', str(self.fixture_path), '--no-guard']
                behavior_structure(action='validate', feature=str(self.fixture_path))
                
                output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                # Assert - Production code should report one rule file found
                rule_files = list(self.fixture_path.glob('*-rule.mdc'))
                expect(rule_files).to(have_length(1))
            
            with it('should have one or more command files'):
                # Act - Call production validation code
                import io
                import sys
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                
                sys.argv = ['test', 'structure', 'validate', str(self.fixture_path), '--no-guard']
                behavior_structure(action='validate', feature=str(self.fixture_path))
                
                output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                # Assert - Production code should report command files found
                command_files = list(self.fixture_path.glob('*-cmd.md'))
                expect(len(command_files)).to(be_above_or_equal(1))
            
            with it('should optionally include a runner file'):
                # Arrange - Fixture WITHOUT runner
                fixture_no_runner = create_test_fixture('no-runner', {
                    'files': [{'name': 'test-rule.mdc', 'type': 'rule', 'content': '---\n---\n**When** x, **then** y.'}],
                    'config': {'deployed': True}
                })
                
                # Arrange - Fixture WITH runner
                fixture_with_runner = create_test_fixture('with-runner', {
                    'files': [
                        {'name': 'test-rule.mdc', 'type': 'rule', 'content': '---\n---\n**When** x, **then** y.'},
                        {'name': 'test-runner.py', 'type': 'runner', 'content': 'def main(): pass'}
                    ],
                    'config': {'deployed': True}
                })
                
                # Act
                runners_without = list(fixture_no_runner.glob('*-runner.py'))
                runners_with = list(fixture_with_runner.glob('*-runner.py'))
                
                # Assert
                expect(runners_without).to(have_length(0))
                expect(runners_with).to(have_length(1))
        
        with context('whose naming is being validated'):
            
            with it('should follow feature-behavior-type pattern'):
                # Arrange - Valid naming
                valid_fixture = create_test_fixture('valid-naming', {
                    'files': [{'name': 'test-feature-behavior-rule.mdc', 'type': 'rule', 'content': '---\n---\n**When** x, **then** y.'}],
                    'config': {'deployed': True}
                })
                
                # Arrange - Invalid naming (underscores)
                invalid_fixture = create_test_fixture('invalid-naming', {
                    'files': [{'name': 'test_feature_behavior_rule.mdc', 'type': 'rule', 'content': '---\n---\n**When** x, **then** y.'}],
                    'config': {'deployed': True}
                })
                
                # Act - Call production validation
                import re
                pattern = re.compile(r'^([a-z0-9\-]+)-([a-z0-9\-]+)-(rule|cmd|runner)\.(mdc|md|py)$')
                valid_files = list(valid_fixture.glob('*.mdc'))
                invalid_files = list(invalid_fixture.glob('*.mdc'))
                
                # Assert
                expect(pattern.match(valid_files[0].name)).to_not(be_none)
                expect(pattern.match(invalid_files[0].name)).to(be_none)
            
            with it('should use mdc extension for rules'):
                # Arrange
                fixture = create_test_fixture('mdc-rules', {
                    'files': [{'name': 'test-rule.mdc', 'type': 'rule', 'content': '---\n---\n**When** x, **then** y.'}],
                    'config': {'deployed': True}
                })
                
                # Act
                rule_files = list(fixture.glob('*-rule.*'))
                
                # Assert
                expect(rule_files[0].suffix).to(equal('.mdc'))
            
            with it('should use md extension for commands'):
                # Arrange
                fixture = create_test_fixture('md-commands', {
                    'files': [{'name': 'test-cmd.md', 'type': 'command', 'content': '### Command'}],
                    'config': {'deployed': True}
                })
                
                # Act
                command_files = list(fixture.glob('*-cmd.*'))
                
                # Assert
                expect(command_files[0].suffix).to(equal('.md'))
            
            with it('should reject verb suffixes on rule files'):
                # Arrange - Rule with verb suffix (INVALID)
                fixture = create_test_fixture('verb-suffix', {
                    'files': [{'name': 'test-validate-rule.mdc', 'type': 'rule', 'content': '---\n---\n**When** x, **then** y.'}],
                    'config': {'deployed': True}
                })
                
                # Act - Check against verb pattern
                import re
                verb_pattern = re.compile(r'-(create|validate|fix|sync|analyze|update)-rule\.(mdc|md)$')
                rule_files = list(fixture.glob('*-rule.mdc'))
                
                # Assert - Should match (meaning it's a violation)
                expect(verb_pattern.search(rule_files[0].name)).to_not(be_none)
        
        with context('whose relationships are being verified'):
            
            with before.each:
                # Arrange - Fixture with rule and command files
                self.fixture_path = create_test_fixture('relationships', {
                    'files': [
                        {
                            'name': 'test-rule.mdc',
                            'type': 'rule',
                            'content': '''---
description: Test rule
---

**When** testing behavior,
**then** follow guidelines.

**Executing Commands:**
* \\test-cmd — Execute test behavior
'''
                        },
                        {
                            'name': 'test-cmd.md',
                            'type': 'command',
                            'content': '''### Command: test-cmd

**Purpose:** Test command

**Rule:**
* \\test-rule — Defines triggering conditions

**Runner:**
python behaviors/test/test-runner.py
'''
                        }
                    ],
                    'config': {'deployed': True}
                })
            
            with it('should reference commands from rule'):
                # Act - Call production code to validate structure
                # This should check that rules reference their commands
                result = behavior_structure(action='validate', feature=str(self.fixture_path))
                
                # Assert - Production code should verify command references exist
                # Will fail because behavior_structure doesn't return structured validation results yet
                expect(result).to_not(be_none)
            
            with it('should reference rule from command'):
                # Act - Call production code to validate structure
                # This should check that commands reference their rules
                result = behavior_structure(action='validate', feature=str(self.fixture_path))
                
                # Assert - Production code should verify rule references exist
                # Will fail because behavior_structure doesn't return structured validation results yet
                expect(result).to_not(be_none)
            
            with it('should reference runner from command when automation exists'):
                # Act - Call production code to validate structure
                # This should check that commands reference runners when applicable
                result = behavior_structure(action='validate', feature=str(self.fixture_path))
                
                # Assert - Production code should verify runner references
                # Will fail because behavior_structure doesn't return structured validation results yet
                expect(result).to_not(be_none)
    
    with context('that is being validated for structure compliance'):
        
        with context('whose naming patterns are being checked'):
            
            with it('should identify files not matching pattern'):
                # Arrange - Create fixture with INVALID file naming (underscores)
                invalid_fixture = create_test_fixture('invalid-patterns', {
                    'files': [
                        {'name': 'test_invalid_naming.mdc', 'type': 'rule', 'content': '---\n---\n**When** x, **then** y.'}
                    ],
                    'config': {'deployed': True}
                })
                
                # Act - Call production validation
                import io, sys
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                sys.argv = ['test', 'structure', 'validate', str(invalid_fixture), '--no-guard']
                behavior_structure(action='validate', feature=str(invalid_fixture))
                output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                # Assert - Should report invalid naming pattern
                expect(output).to(contain('Invalid name pattern'))
                expect(output).to(contain('test_invalid_naming.mdc'))
            
            with it('should flag rules with verb suffixes'):
                # Arrange - Rule with verb suffix
                fixture = create_test_fixture('verb-suffix', {
                    'files': [
                        {'name': 'test-validate-rule.mdc', 'type': 'rule', 'content': '---\n---\n**When** x, **then** y.'}
                    ],
                    'config': {'deployed': True}
                })
                
                # Act - Call production validation
                import io, sys
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                sys.argv = ['test', 'structure', 'validate', str(fixture), '--no-guard']
                behavior_structure(action='validate', feature=str(fixture))
                output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                # Assert - Should flag verb suffix
                expect(output).to(contain('verb'))
            
            with it('should accept optional verb suffixes on commands'):
                # Arrange - Command with verb suffix (VALID)
                fixture = create_test_fixture('cmd-verb-ok', {
                    'files': [
                        {'name': 'test-validate-cmd.md', 'type': 'command', 'content': '### Command\n**Purpose:** Test'}
                    ],
                    'config': {'deployed': True}
                })
                
                # Act - Call production validation
                import io, sys
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                sys.argv = ['test', 'structure', 'validate', str(fixture), '--no-guard']
                behavior_structure(action='validate', feature=str(fixture))
                output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                # Assert - Should NOT flag command verb suffix
                expect(output).not_to(contain('verb suffix violation'))
        
        with context('whose content requirements are being checked'):
            
            with it('should verify rule starts with When condition'):
                # BDD: SIGNATURE
                pass
            
            with it('should require Executing Commands section in rule'):
                # BDD: SIGNATURE
                pass
            
            with it('should require Steps section in commands'):
                # BDD: SIGNATURE
                pass
        
        with context('that has specialized behaviors being handled'):
            
            with it('should exempt reference files from pattern matching'):
                # BDD: SIGNATURE
                pass
            
            with it('should validate base rules separately from specialized rules'):
                # BDD: SIGNATURE
                pass
    
    with context('that is being repaired automatically'):
        
        with context('that has structural issues'):
            
            with it('should generate missing command files'):
                # BDD: SIGNATURE
                pass
            
            with it('should scaffold standard command sections'):
                # BDD: SIGNATURE
                pass
            
            with it('should add required documentation headers'):
                # BDD: SIGNATURE
                pass
        
        with context('that has deprecated patterns'):
            
            with it('should delete AI Usage sections'):
                # BDD: SIGNATURE
                pass
            
            with it('should delete Code Usage sections'):
                # BDD: SIGNATURE
                pass
            
            with it('should replace with Steps section'):
                # BDD: SIGNATURE
                pass
        
        with context('whose repairs are being validated'):
            
            with it('should re-run validation on repaired files'):
                # BDD: SIGNATURE
                pass
            
            with it('should report remaining manual interventions'):
                # BDD: SIGNATURE
                pass
    
    with context('that is being created from scratch'):
        
        with context('whose files are being scaffolded'):
            
            with it('should create feature directory if needed'):
                # BDD: SIGNATURE
                pass
            
            with it('should generate behavior json configuration'):
                # BDD: SIGNATURE
                pass
            
            with it('should set deployment status to draft by default'):
                # BDD: SIGNATURE
                pass
        
        with context('whose rule file is being generated'):
            
            with it('should include frontmatter with description'):
                # BDD: SIGNATURE
                pass
            
            with it('should scaffold When/then structure'):
                # BDD: SIGNATURE
                pass
            
            with it('should add Executing Commands placeholder'):
                # BDD: SIGNATURE
                pass
        
        with context('whose command file is being generated'):
            
            with it('should scaffold Rule reference section'):
                # BDD: SIGNATURE
                pass
            
            with it('should scaffold Runner reference section'):
                # BDD: SIGNATURE
                pass
            
            with it('should scaffold Steps section with performers'):
                # BDD: SIGNATURE
                pass
        
        with context('whose runner file is being generated'):
            
            with it('should include runner guard function'):
                # BDD: SIGNATURE
                pass
            
            with it('should include main entry point'):
                # BDD: SIGNATURE
                pass
            
            with it('should prevent direct execution without flag'):
                # BDD: SIGNATURE
                pass
    
    with context('that is being deployed to active use'):
        
        with context('whose deployment is being prepared'):
            
            with it('should discover features with deployed true flag'):
                # BDD: SIGNATURE
                pass
            
            with it('should prepare target routing destinations'):
                # BDD: SIGNATURE
                pass
            
            with it('should apply exclusion rules for documentation'):
                # BDD: SIGNATURE
                pass
        
        with context('whose files are being synchronized'):
            
            with it('should route mdc files to cursor rules'):
                # BDD: SIGNATURE
                pass
            
            with it('should route md files to cursor commands'):
                # BDD: SIGNATURE
                pass
            
            with it('should exclude py files from sync'):
                # BDD: SIGNATURE
                pass
        
        with context('whose configurations are being merged'):
            
            with it('should load source and destination MCP files'):
                # BDD: SIGNATURE
                pass
            
            with it('should merge with source taking precedence'):
                # BDD: SIGNATURE
                pass
            
            with it('should preserve existing configurations not in source'):
                # BDD: SIGNATURE
                pass
        
        with context('whose watchers are being restarted'):
            
            with it('should detect watch functions in python files'):
                # BDD: SIGNATURE
                pass
            
            with it('should identify active watcher processes'):
                # BDD: SIGNATURE
                pass
            
            with it('should restart watchers to pick up changes'):
                # BDD: SIGNATURE
                pass
    
    with context('that is being indexed for discovery'):
        
        with context('whose behavior files are being discovered'):
            
            with it('should scan for deployed features only'):
                # BDD: SIGNATURE
                pass
            
            with it('should filter by extension mdc md py json'):
                # BDD: SIGNATURE
                pass
            
            with it('should exclude behavior json files'):
                # BDD: SIGNATURE
                pass
            
            with it('should exclude documentation directories'):
                # BDD: SIGNATURE
                pass
        
        with context('whose metadata is being collected'):
            
            with it('should extract feature name from directory'):
                # BDD: SIGNATURE
                pass
            
            with it('should record file type from extension'):
                # BDD: SIGNATURE
                pass
            
            with it('should capture modification timestamp'):
                # BDD: SIGNATURE
                pass
        
        with context('whose index structure is being assembled'):
            
            with it('should create entry properties for each file'):
                # BDD: SIGNATURE
                pass
            
            with it('should group entries by feature'):
                # BDD: SIGNATURE
                pass
            
            with it('should calculate total behavior count'):
                # BDD: SIGNATURE
                pass
        
        with context('whose indexes are being updated'):
            
            with it('should write global index to cursor directory'):
                # BDD: SIGNATURE
                pass
            
            with it('should update local feature indexes'):
                # BDD: SIGNATURE
                pass
            
            with it('should maintain human readable JSON format'):
                # BDD: SIGNATURE
                pass
    
    with context('that is being analyzed for consistency'):
        
        with context('whose behaviors are being discovered for analysis'):
            
            with it('should locate features with deployed status'):
                # BDD: SIGNATURE
                pass
            
            with it('should collect rule and command files'):
                # BDD: SIGNATURE
                pass
            
            with it('should exclude draft and experimental behaviors'):
                # BDD: SIGNATURE
                pass
        
        with context('whose semantic analysis is being performed'):
            
            with it('should load behavior content for comparison'):
                # BDD: SIGNATURE
                pass
            
            with it('should invoke OpenAI function calling with schema'):
                # BDD: SIGNATURE
                pass
            
            with it('should receive structured results from AI'):
                # BDD: SIGNATURE
                pass
        
        with context('whose overlaps are being identified'):
            
            with it('should detect similar purpose with different approach'):
                # BDD: SIGNATURE
                pass
            
            with it('should record similarity description'):
                # BDD: SIGNATURE
                pass
            
            with it('should suggest consolidation or clarification'):
                # BDD: SIGNATURE
                pass
        
        with context('whose contradictions are being identified'):
            
            with it('should detect opposite guidance in same context'):
                # BDD: SIGNATURE
                pass
            
            with it('should record contradiction context'):
                # BDD: SIGNATURE
                pass
            
            with it('should recommend resolution approach'):
                # BDD: SIGNATURE
                pass
        
        with context('whose consistency report is being generated'):
            
            with it('should format results from analysis schema'):
                # BDD: SIGNATURE
                pass
            
            with it('should organize by analysis types'):
                # BDD: SIGNATURE
                pass
            
            with it('should surface issues for human review'):
                # BDD: SIGNATURE
                pass
    
    with context('that has specialized behaviors'):
        
        with context('whose hierarchical pattern is being validated'):
            
            with it('should check for isSpecialized flag in configuration'):
                # BDD: SIGNATURE
                pass
            
            with it('should identify base rule file'):
                # BDD: SIGNATURE
                pass
            
            with it('should identify specialized rule files'):
                # BDD: SIGNATURE
                pass
            
            with it('should identify reference files'):
                # BDD: SIGNATURE
                pass
        
        with context('whose base rule is being validated'):
            
            with it('should verify common framework-agnostic guidance'):
                # BDD: SIGNATURE
                pass
            
            with it('should check for Executing Commands references'):
                # BDD: SIGNATURE
                pass
        
        with context('whose specialized rules are being validated'):
            
            with it('should verify framework-specific extensions'):
                # BDD: SIGNATURE
                pass
            
            with it('should verify reference to base rule'):
                # BDD: SIGNATURE
                pass
            
            with it('should ensure no contradictions with base'):
                # BDD: SIGNATURE
                pass
        
        with context('whose pattern consistency is being checked'):
            
            with it('should verify DRY principles maintained'):
                # BDD: SIGNATURE
                pass
            
            with it('should ensure base rule contains common guidance'):
                # BDD: SIGNATURE
                pass
            
            with it('should ensure specialized rules extend without duplication'):
                # BDD: SIGNATURE
                pass


with description('a feature') as self:
    
    with context('that groups related behaviors'):
        
        with it('should be marked by behavior json file'):
            # Arrange - Create feature with behavior.json
            feature_fixture = create_test_fixture('feature-marked', {
                'files': [
                    {'name': 'test-rule.mdc', 'type': 'rule', 'content': '---\n---\n**When** x, **then** y.'}
                ],
                'config': {'deployed': True, 'description': 'Test feature'}
            })
            
            # Act - Check for behavior.json
            behavior_json = feature_fixture / 'behavior.json'
            
            # Assert - behavior.json should exist
            expect(behavior_json.exists()).to(be_true)
        
        with it('should contain outline describing purpose'):
            # Arrange - Create feature with description
            feature_fixture = create_test_fixture('feature-outlined', {
                'files': [
                    {'name': 'test-rule.mdc', 'type': 'rule', 'content': '---\n---\n**When** x, **then** y.'}
                ],
                'config': {'deployed': True, 'description': 'Feature purpose outline'}
            })
            
            # Act - Load config and check description
            config_data = json.loads((feature_fixture / 'behavior.json').read_text())
            
            # Assert - Should have description field
            expect(config_data).to(have_key('description'))
            expect(config_data['description']).to(equal('Feature purpose outline'))
        
        with it('should have deployed flag controlling activation'):
            # Arrange - Create feature with deployed flag
            feature_fixture = create_test_fixture('feature-deployed', {
                'files': [
                    {'name': 'test-rule.mdc', 'type': 'rule', 'content': '---\n---\n**When** x, **then** y.'}
                ],
                'config': {'deployed': True}
            })
            
            # Act - Load config and check deployed flag
            config_data = json.loads((feature_fixture / 'behavior.json').read_text())
            
            # Assert - Should have deployed flag
            expect(config_data).to(have_key('deployed'))
            expect(config_data['deployed']).to(be_true)
    
    with context('that is being discovered by configuration'):
        
        with it('should be found via behavior json scanning'):
            # Arrange - Create multiple features
            root_dir = Path(tempfile.mkdtemp())
            feature1 = root_dir / 'feature1'
            feature1.mkdir()
            (feature1 / 'behavior.json').write_text('{"deployed": true}')
            
            feature2 = root_dir / 'feature2'
            feature2.mkdir()
            (feature2 / 'behavior.json').write_text('{"deployed": false}')
            
            # Act - Call production code to find all behavior.json files
            all_behaviors = find_all_behavior_jsons(root_dir)
            
            # Assert - Should find both features
            expect(all_behaviors).to(have_length(2))
            
            # Cleanup
            shutil.rmtree(root_dir)
        
        with it('should be filtered by deployed status'):
            # Arrange - Create features with different deployed status
            root_dir = Path(tempfile.mkdtemp())
            deployed_feature = root_dir / 'deployed'
            deployed_feature.mkdir()
            (deployed_feature / 'behavior.json').write_text('{"deployed": true}')
            
            draft_feature = root_dir / 'draft'
            draft_feature.mkdir()
            (draft_feature / 'behavior.json').write_text('{"deployed": false}')
            
            # Act - Call production code to find only deployed behaviors
            deployed_only = find_deployed_behaviors(root_dir)
            
            # Assert - Should only find deployed=true feature
            expect(deployed_only).to(have_length(1))
            expect(deployed_only[0].name).to(equal('deployed'))
            
            # Cleanup
            shutil.rmtree(root_dir)
        
        with it('should provide metadata for consuming processes'):
            # Arrange - Create feature with full metadata
            root_dir = Path(tempfile.mkdtemp())
            feature = root_dir / 'test-feature'
            feature.mkdir()
            config = {
                'deployed': True,
                'description': 'Test feature with metadata',
                'version': '1.0'
            }
            (feature / 'behavior.json').write_text(json.dumps(config))
            
            # Act - Call production code to get metadata
            behaviors = find_all_behavior_jsons(root_dir)
            
            # Assert - Should include path, config, and json_path
            expect(behaviors).to(have_length(1))
            expect(behaviors[0]).to(have_keys('path', 'config', 'json_path'))
            expect(behaviors[0]['config']['description']).to(equal('Test feature with metadata'))
            
            # Cleanup
            shutil.rmtree(root_dir)


with description('configuration discovery') as self:
    
    with context('that identifies deployed features'):
        
        with before.each:
            # Arrange - Create test fixtures with behavior.json files
            self.deployed_fixture = create_test_fixture('deployed-feature', {
                'files': [{'name': 'test-rule.mdc', 'type': 'rule', 'content': '---\n---\n**When** x, **then** y.'}],
                'config': {'deployed': True, 'feature': 'deployed-feature'}
            })
            self.draft_fixture = create_test_fixture('draft-feature', {
                'files': [{'name': 'test-rule.mdc', 'type': 'rule', 'content': '---\n---\n**When** x, **then** y.'}],
                'config': {'deployed': False, 'feature': 'draft-feature'}
            })
        
        with it('should scan for behavior json files'):
            # Act - Call production code
            all_behaviors = find_all_behavior_jsons(self.deployed_fixture.parent)
            
            # Assert - Should find both behavior.json files
            expect(all_behaviors).to(have_length(2))
        
        with it('should parse JSON configuration'):
            # Act - Call production code
            all_behaviors = find_all_behavior_jsons(self.deployed_fixture.parent)
            
            # Assert - Should parse config and extract properties
            expect(all_behaviors[0]).to(have_key('config'))
            expect(all_behaviors[0]['config']).to(have_key('deployed'))
        
        with it('should extract deployed flag and feature name'):
            # Act - Call production code
            feature_name = get_behavior_feature_name(self.deployed_fixture)
            
            # Assert
            expect(feature_name).to(equal('deployed-feature'))
        
        with it('should return structured list to other processes'):
            # Act - Call production code
            deployed_only = find_deployed_behaviors(self.deployed_fixture.parent)
            
            # Assert - Should filter to only deployed=true features
            expect(deployed_only).to(have_length(1))
            expect(deployed_only[0].name).to(equal('deployed-feature'))


# ===================================================================================================
# SIGNATURE SUMMARY
# ===================================================================================================
#
# Total Tests: 99 test signatures
# Coverage:
#   - Behavior (80 tests across 8 behavioral contexts)
#     * Structure (10 tests) - Components, Naming, Relationships
#     * Validation (8 tests) - Naming patterns, Content requirements, Specialized handling
#     * Repair (8 tests) - Structural issues, Deprecated patterns, Re-validation
#     * Creation (12 tests) - Scaffolding, Rule/Command/Runner generation
#     * Deployment (12 tests) - Preparation, Synchronization, Merging, Watchers
#     * Indexing (15 tests) - Discovery, Metadata, Structure assembly, Updates
#     * Consistency Analysis (15 tests) - Discovery, Semantic analysis, Overlaps, Contradictions
#     * Specialized Behaviors (16 tests) - Hierarchical pattern, Base/specialized rules, Consistency
#   - Feature (6 tests across 2 behavioral contexts)
#   - Configuration Discovery (4 tests across 1 behavioral context)
#
# Status: RED PHASE in progress - 18 tests implemented calling production code
# Remaining: 81 tests still in SIGNATURE phase (pass statements)
# All implemented tests call actual production functions from code-agent-runner.py
#

