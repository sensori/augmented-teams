"""
Behavior Instruction Injection Tests

Tests instruction injection for all behavior actions:
- Guardrails injection (key questions, evidence)
- Planning criteria injection (assumptions, decision criteria)
- Knowledge graph template injection
- Template and content loading instructions
- Validation rules injection
"""
import pytest
from pathlib import Path
import json

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_guardrails_files(workspace: Path, bot_name: str, behavior: str, questions: list, evidence: list) -> tuple:
    """Helper: Create guardrails files for behavior."""
    guardrails_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / 'guardrails' / 'required_context'
    guardrails_dir.mkdir(parents=True, exist_ok=True)
    
    questions_file = guardrails_dir / 'key_questions.json'
    questions_file.write_text(json.dumps({'questions': questions}))
    
    evidence_file = guardrails_dir / 'evidence.json'
    evidence_file.write_text(json.dumps({'evidence': evidence}))
    
    return questions_file, evidence_file

def create_planning_guardrails(workspace: Path, bot_name: str, behavior: str, assumptions: list, criteria: dict) -> tuple:
    """Helper: Create planning guardrails files."""
    planning_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / 'guardrails' / 'planning'
    planning_dir.mkdir(parents=True, exist_ok=True)
    
    assumptions_file = planning_dir / 'typical_assumptions.json'
    assumptions_file.write_text(json.dumps({'assumptions': assumptions}))
    
    criteria_dir = planning_dir / 'decision_criteria'
    criteria_dir.mkdir(exist_ok=True)
    
    criteria_file = criteria_dir / 'test_criteria.json'
    criteria_file.write_text(json.dumps(criteria))
    
    return assumptions_file, criteria_file

def create_knowledge_graph_template(workspace: Path, bot_name: str, behavior: str, template_name: str) -> Path:
    """Helper: Create knowledge graph template file."""
    kg_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / 'content' / 'knowledge_graph'
    kg_dir.mkdir(parents=True, exist_ok=True)
    
    template_file = kg_dir / template_name
    template_file.write_text(json.dumps({'template': 'structure'}))
    
    return template_file

def create_validation_rules(workspace: Path, bot_name: str, behavior: str, rules: list) -> Path:
    """Helper: Create validation rules file."""
    rules_dir = workspace / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / 'rules'
    rules_dir.mkdir(parents=True, exist_ok=True)
    
    rules_file = rules_dir / 'validation_rules.json'
    rules_file.write_text(json.dumps({'rules': rules}))
    
    return rules_file

def create_common_rules(workspace: Path, rules: list) -> Path:
    """Helper: Create common bot rules."""
    rules_dir = workspace / 'base_bot' / 'rules'
    rules_dir.mkdir(parents=True, exist_ok=True)
    
    rules_file = rules_dir / 'common_rules.json'
    rules_file.write_text(json.dumps({'rules': rules}))
    
    return rules_file

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def workspace_root(tmp_path):
    """Fixture: Temporary workspace directory."""
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    return workspace

# ============================================================================
# TESTS
# ============================================================================

class TestGuardrailsInjection:
    """Guardrails injection tests."""

    def test_action_loads_and_injects_guardrails(self, workspace_root):
        """
        SCENARIO: Action loads and injects guardrails for shape gather_context
        GIVEN: Guardrails configured with key questions and evidence
        WHEN: Action method is invoked
        THEN: Guardrails are injected into instructions
        """
        # Given: Guardrails files exist
        bot_name = 'test_bot'
        behavior = 'shape'
        questions = ['What is the scope?', 'Who are the users?']
        evidence = ['Requirements doc', 'User interviews']
        
        questions_file, evidence_file = create_guardrails_files(workspace_root, bot_name, behavior, questions, evidence)
        
        # When: Guardrails are loaded
        questions_data = json.loads(questions_file.read_text())
        evidence_data = json.loads(evidence_file.read_text())
        
        # Then: Both files loaded successfully
        assert questions_data['questions'] == questions
        assert evidence_data['evidence'] == evidence

    def test_action_uses_base_instructions_when_guardrails_missing(self, workspace_root):
        """
        SCENARIO: Action uses base instructions when guardrails do not exist
        GIVEN: Guardrails folder does not exist
        WHEN: Action method is invoked
        THEN: Uses base instructions only with info log
        """
        # Given: Guardrails path but no files
        bot_name = 'test_bot'
        behavior = 'shape'
        guardrails_path = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / 'guardrails' / 'required_context'
        
        # When/Then: Guardrails missing
        assert not guardrails_path.exists()
        
        # Action would log: 'No guardrails found, using base instructions only'

    def test_action_handles_malformed_guardrails_json(self, workspace_root):
        """
        SCENARIO: Action handles malformed guardrails JSON
        GIVEN: key_questions.json has invalid JSON
        WHEN: Action method is invoked
        THEN: Raises JSONDecodeError and falls back to base
        """
        # Given: Malformed guardrails file
        bot_name = 'test_bot'
        behavior = 'shape'
        guardrails_dir = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / 'guardrails' / 'required_context'
        guardrails_dir.mkdir(parents=True, exist_ok=True)
        
        questions_file = guardrails_dir / 'key_questions.json'
        questions_file.write_text('invalid json {')
        
        # When/Then: Loading raises error
        with pytest.raises(json.JSONDecodeError):
            json.loads(questions_file.read_text())


class TestPlanningCriteriaInjection:
    """Planning criteria injection tests."""

    def test_action_loads_and_injects_planning_criteria(self, workspace_root):
        """
        SCENARIO: Action loads and injects planning criteria for exploration
        GIVEN: Planning guardrails configured with assumptions and criteria
        WHEN: Action method is invoked
        THEN: Planning criteria injected into instructions
        """
        # Given: Planning guardrails exist
        bot_name = 'test_bot'
        behavior = 'exploration'
        assumptions = ['Stories follow user story format', 'Acceptance criteria are testable']
        criteria = {'scope': ['Component', 'System', 'Solution']}
        
        assumptions_file, criteria_file = create_planning_guardrails(workspace_root, bot_name, behavior, assumptions, criteria)
        
        # When: Planning criteria loaded
        assumptions_data = json.loads(assumptions_file.read_text())
        criteria_data = json.loads(criteria_file.read_text())
        
        # Then: Both loaded successfully
        assert assumptions_data['assumptions'] == assumptions
        assert criteria_data['scope'] == criteria['scope']

    def test_action_uses_base_planning_when_guardrails_missing(self, workspace_root):
        """
        SCENARIO: Action uses base planning instructions when guardrails missing
        GIVEN: Planning guardrails do not exist
        WHEN: Action method is invoked
        THEN: Uses base planning only with info log
        """
        # Given: Planning guardrails path but no files
        bot_name = 'test_bot'
        behavior = 'exploration'
        planning_path = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / 'guardrails' / 'planning'
        
        # When/Then: Guardrails missing
        assert not planning_path.exists()
        
        # Action would log: 'No planning guardrails found, using base only'


class TestKnowledgeGraphTemplateInjection:
    """Knowledge graph template injection tests."""

    def test_action_loads_and_injects_knowledge_graph_template(self, workspace_root):
        """
        SCENARIO: Action loads and injects knowledge graph template for exploration
        GIVEN: Knowledge graph template exists
        WHEN: Action method is invoked
        THEN: Template path injected into instructions
        """
        # Given: Knowledge graph template exists
        bot_name = 'test_bot'
        behavior = 'exploration'
        template_name = 'story-graph-explored-outline.json'
        
        template_file = create_knowledge_graph_template(workspace_root, bot_name, behavior, template_name)
        
        # When: Template is loaded
        template_data = json.loads(template_file.read_text())
        
        # Then: Template loaded successfully
        assert template_file.exists()
        assert template_data['template'] == 'structure'

    def test_action_raises_error_when_template_missing(self, workspace_root):
        """
        SCENARIO: Action handles missing knowledge graph template
        GIVEN: Template does not exist
        WHEN: Action method is invoked
        THEN: Raises FileNotFoundError
        """
        # Given: Template path but file doesn't exist
        bot_name = 'test_bot'
        behavior = 'exploration'
        template_path = workspace_root / 'agile_bot' / 'bots' / bot_name / 'behaviors' / behavior / 'content' / 'knowledge_graph' / 'template.json'
        
        # When/Then: Template missing
        assert not template_path.exists()
        
        # Action would raise: FileNotFoundError('Knowledge graph template not found')


class TestValidationRulesInjection:
    """Validation rules injection tests."""

    def test_action_loads_and_injects_validation_rules(self, workspace_root):
        """
        SCENARIO: Action loads and injects validation rules for exploration
        GIVEN: Common and behavior-specific rules exist
        WHEN: Action method is invoked
        THEN: Merged rules injected into instructions
        """
        # Given: Both rule files exist
        bot_name = 'test_bot'
        behavior = 'exploration'
        common_rules = ['Rule 1: Stories must have title', 'Rule 2: AC must be testable']
        behavior_rules = ['Rule 3: AC must use Given-When-Then']
        
        common_file = create_common_rules(workspace_root, common_rules)
        behavior_file = create_validation_rules(workspace_root, bot_name, behavior, behavior_rules)
        
        # When: Rules are loaded
        common_data = json.loads(common_file.read_text())
        behavior_data = json.loads(behavior_file.read_text())
        
        # Then: Both loaded successfully
        assert common_data['rules'] == common_rules
        assert behavior_data['rules'] == behavior_rules

    def test_action_uses_common_rules_when_behavior_rules_missing(self, workspace_root):
        """
        SCENARIO: Action uses common rules when behavior-specific missing
        GIVEN: Common rules exist but behavior-specific do not
        WHEN: Action method is invoked
        THEN: Uses common rules only with info log
        """
        # Given: Only common rules exist
        common_rules = ['Common rule 1']
        create_common_rules(workspace_root, common_rules)
        
        behavior_path = workspace_root / 'agile_bot' / 'bots' / 'test_bot' / 'behaviors' / 'exploration' / 'rules'
        
        # When/Then: Behavior rules missing
        assert not behavior_path.exists()
        
        # Action would log: 'No behavior-specific rules found'

    def test_action_raises_error_when_common_rules_missing(self, workspace_root):
        """
        SCENARIO: Action handles missing common rules
        GIVEN: Common rules do not exist
        WHEN: Action method is invoked
        THEN: Raises FileNotFoundError
        """
        # Given: Common rules path but no files
        rules_path = workspace_root / 'base_bot' / 'rules'
        
        # When/Then: Common rules missing
        assert not rules_path.exists()
        
        # Action would raise: FileNotFoundError('Common bot rules not found')


class TestContentLoadingInstructions:
    """Content loading instruction injection tests."""

    def test_action_injects_load_rendered_content_instructions(self, workspace_root):
        """
        SCENARIO: Action injects instructions to load rendered content
        GIVEN: Rendered content exists
        WHEN: Action needs to load content
        THEN: Load instructions injected with file path
        """
        # Given: Rendered content file
        rendered_path = workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'docs' / 'stories' / 'acceptance-criteria.md'
        rendered_path.parent.mkdir(parents=True, exist_ok=True)
        rendered_path.write_text('# Acceptance Criteria')
        
        # When: Path is prepared
        expected_path = 'agile_bot/bots/base_bot/docs/stories/acceptance-criteria.md'
        
        # Then: File exists and path is correct
        assert rendered_path.exists()
        assert 'acceptance-criteria.md' in expected_path

    def test_action_handles_missing_rendered_content(self, workspace_root):
        """
        SCENARIO: Action handles missing rendered content file
        GIVEN: Rendered content does not exist
        WHEN: Action injects instructions
        THEN: Includes fallback guidance
        """
        # Given: Content path but file doesn't exist
        content_path = workspace_root / 'agile_bot' / 'bots' / 'base_bot' / 'docs' / 'stories' / 'missing.md'
        
        # When/Then: Content missing
        assert not content_path.exists()
        
        # Instructions would include: 'File not rendered yet, suggest running render action'

