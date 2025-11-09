"""BDD Feature Tests - BDD-Specific Domain Model"""
# type: ignore  # noqa: E402, F401
# pylint: disable=all
# mypy: ignore-errors
# pyright: reportUndefinedVariable=false
# pyright: reportMissingImports=false
# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportCallIssue=false
# pyright: reportAssignmentType=false
# pyright: reportOperatorIssue=false
# pyright: reportUnboundVariable=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownLambdaType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false
# pyright: reportMissingParameterType=false
# pyright: reportMissingTypeArgument=false
# pyright: reportOptionalMemberAccess=false
# pyright: reportOptionalOperand=false
# pyright: reportOptionalSubscript=false
# pyright: typeCheckingMode=off
# fmt: off

from mamba import description, context, it, before
from expects import expect, equal, be_true, be_false, contain, have_length, be_none
from unittest.mock import Mock, patch, MagicMock
import json
from pathlib import Path

# Import domain classes
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from common_command_runner.common_command_runner import (
    Content,
    BaseRule,
    FrameworkSpecializingRule,
    SpecializedRule,
    Principle,
    Example,
    CodeHeuristic,
    Violation,
    ViolationReport,
    Run,
    RunHistory,
    Command,
    CodeAugmentedCommand,
    SpecializingRuleCommand,
    IncrementalCommand,
    WorkflowPhaseCommand,
    Workflow,
    PhaseState,
    IncrementalState
)

# Import BDD-specific classes
# Note: bdd-runner.py uses hyphen, so we import via importlib
import importlib.util
bdd_runner_path = Path(__file__).parent / 'bdd-runner.py'
spec = importlib.util.spec_from_file_location("bdd_runner", bdd_runner_path)
bdd_runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bdd_runner)

BDDRule = bdd_runner.BDDRule
BDDRunState = bdd_runner.BDDRunState
BDDIncrementalCommand = bdd_runner.BDDIncrementalCommand
BDDCommand = bdd_runner.BDDCommand
BDDWorkflowPhaseCommand = bdd_runner.BDDWorkflowPhaseCommand
create_bdd_workflow = bdd_runner.create_bdd_workflow
RunStatus = bdd_runner.RunStatus
StepType = bdd_runner.StepType
WorkflowStepTemplate = bdd_runner.WorkflowStepTemplate
DomainScaffolder = bdd_runner.DomainScaffolder
SignatureGenerator = bdd_runner.SignatureGenerator
RedExecutor = bdd_runner.RedExecutor
GreenExecutor = bdd_runner.GreenExecutor
RefactorExecutor = bdd_runner.RefactorExecutor
BDDWorkflowState = bdd_runner.BDDWorkflowState
BDDPhase = bdd_runner.BDDPhase
detect_framework_from_file = bdd_runner.detect_framework_from_file
parse_test_structure = bdd_runner.parse_test_structure

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_content(file_path='test.py', file_extension='.py'):
    """Create Content object for testing"""
    return Content(file_path=file_path, file_extension=file_extension)

def create_bdd_base_rule_content():
    """Helper for BDD base rule content with five principles"""
    return """---
description: BDD Test rule
---

## 1. Business Readable Language
Use plain English that business stakeholders can understand.

**[DO]:**
```python
with description('a power item'):
    with it('should display fire descriptor when power type is fire'):
        pass
```

**[DON'T]:**
```python
with description('PowerItem'):
    with it('test_getDescriptor_returnsFire'):
        pass
```

## 2. Comprehensive and Brief Coverage
Cover all behaviors but keep tests focused.

**[DO]:**
```python
with it('should display fire descriptor when power type is fire'):
    pass
with it('should display ice descriptor when power type is ice'):
    pass
```

**[DON'T]:**
```python
with it('should handle all power types correctly'):
    pass
```

## 3. Balance Context Sharing
Extract common setup to beforeEach, but keep tests readable.

**[DO]:**
```python
with before.each:
    self.power_item = PowerItem(mock_power)
```

**[DON'T]:**
```python
# Duplicate setup in every test
```

## 4. Cover All Layers
Test front-end, business logic, and data layers appropriately.

## 5. Unit Tests Front-End
Front-end tests should focus on user interactions, not implementation.

**[DO]:**
```python
with it('should show animation when user hovers over token'):
    pass
```

**[DON'T]:**
```python
with it('should call animation.start() when mouse event fires'):
    pass
```
"""

def create_bdd_specialized_rule_content(framework='mamba'):
    """Helper for BDD specialized rule content - matches actual rule files"""
    if framework == 'mamba':
        return """---
description: BDD testing practices for Mamba/Python
---

## 1. Business Readable Language
Write `describe`/`it` so that inner/outer sentences create natural sentence. Use nouns for `describe` (concepts, states). Start each `it()` with "should …". Nest from broad → specific; each child adds context. Use plain behavioral language. Prefer domain terms over technical jargon. Connect base business concept to more specific concepts using linking words: "that is/that has" "that has been"

**✅ DO:**
```python
with description('a ranged damage power'):
    with context('that has targeted and resulted in a successful attack'):
        with it('should apply damage based on degrees of failure'):
            expect(result.injuries).to(equal(2))
```

**❌ DON'T:**
```python
with description('when attacking Target'):
with description('Power.execute()'):
with context('retrieved attack'):
with it('sets is_submitting flag'):
```

## 2. Comprehensive and Brief
Test observable behavior, not hidden internals. Cover state, validation, rules, and interactions. Cover normal, edge, and failure paths. Keep tests short, expressive, readable. Keep tests independent, deterministic, and fast.

**✅ DO:**
```python
with description('a damage power'):
    with before.each:
        self.mock_target = {'dodge': 15, 'injury': 0}
    
    with it('should be a ranged attack'):
        expect(attack.is_ranged).to(equal(True))
    
    with it('should calculate DC from targets dodge'):
        expect(attack.execute(self.mock_target).DC).to(equal(20))
```

**❌ DON'T:**
```python
with it('calls _validate()'):
    expect(form._flag).to(be_true)
    expect(form._validate).to(have_been_called)
with it('handles attack'):
```

## 3. Balance Context Sharing with Localization
Nest parent context, don't repeat it. Provide expected data via helper factories/builders. Extract complex logic into helpers. Reuse helpers/factories where possible.

**✅ DO:**
```python
def create_power(o=None):
    return Power({**{'name': 'Test', 'rank': 10}, **(o or {})})

with description('a Power'):
    with before.each:
        self.factory = MockFactory()
        self.factory.reset()
        self.power = create_power()
```

**❌ DON'T:**
```python
with description('Power'):
    with context('created from actor'):
        with before.each:
            self.actor = {'id': '123'}
    with context('that is ranged'):
        with before.each:
            self.actor = {'id': '123'}
```

## 4. Cover All Layers of the System
Include separate front end, business logic, integration, and data access tests. Isolate across architecture boundaries with mocks and stubs.

## 5. Unit Tests the Front-End
Mock services, business logic, and routing. Stub user events and verify resulting state or view.

**✅ DO:**
```python
with description('an attack power display'):
    with before.each:
        self.mock_service = Mock()
        self.context = prepare_context(self.actor)
    
    with it('should include attack bonus in context'):
        expect(self.context['attack_powers'][0]['bonus']).to(equal(8))
```

**❌ DON'T:**
```python
with it('renders bonus'):
    expect(html).to(contain('value="8"'))
    expect(html).to(contain('color: blue'))
    requests.get('http://api.com')
with it('calls _on_mount()'):
    expect(component._on_mount).to(have_been_called)
```
"""
    else:  # jest
        return """---
description: BDD testing practices for Jest/JavaScript
---

## 1. Business Readable Language
Write `describe`/`it` so that inner/outer sentences create natural sentence. Use nouns for `describe` (concepts, states). Start each `it()` with "should …". Nest from broad → specific; each child adds context. Use plain behavioral language. Prefer domain terms over technical jargon.

**✅ DO:**
```javascript
describe('a ranged damage power', () => {
  describe('that has targeted and resulted in a successful attack', () => {
    it('should apply damage based on degrees of failure', () => {
      expect(result.injuries).toBe(2);
    });
  });
});
```

**❌ DON'T:**
```javascript
describe('when Attack.targetToken()', () => {});
describe('retrieved attack', () => {});
it('sets isSubmitting flag', () => {});
```

## 2. Comprehensive and Brief
Test observable behavior, not hidden internals. Cover state, validation, rules, and interactions.

**✅ DO:**
```javascript
describe('a damage power', () => {
  beforeEach(() => {
    mockTarget = { dodge: 15, injury: 0 };
  });
  
  it('should be a ranged attack', () => {
    expect(attack.isRanged).toBe(true);
  });
  
  it('should calculate DC from targets dodge', () => {
    expect(attack.execute(mockTarget).DC).toBe(20);
  });
});
```

**❌ DON'T:**
```javascript
it('calls _validateCredentials()', () => {
  expect(form._internal_flag).toBe(true);
  expect(form._validateCredentials).toHaveBeenCalled();
});
```

## 3. Balance Context Sharing with Localization
Nest parent context, don't repeat it. Provide expected data via helper factories/builders.

**✅ DO:**
```javascript
const createPower = (o = {}) => ({ name: 'Test', rank: 10, ...o });

describe('a Power', () => {
  beforeEach(() => {
    power = createPower();
  });
});
```

**❌ DON'T:**
```javascript
describe('with an attached macro', () => {
  it('should return animation with type "attached"', () => {
    const mockMacro = { name: 'Custom', execute: jest.fn() };
    const mockItem = createMockItem({ getFlag: jest.fn().mockReturnValue('id') });
    const powerItem = new PowerItem(mockItem);
  });
  
  it('should provide macro name as animation name', () => {
    const mockMacro = { name: 'Custom', execute: jest.fn() };
    const mockItem = createMockItem({ getFlag: jest.fn().mockReturnValue('id') });
    const powerItem = new PowerItem(mockItem);
  });
});
```

## 4. Cover All Layers of the System
Include separate front end, business logic, integration, and data access tests.

## 5. Unit Tests the Front-End
Mock services, business logic, and routing. Stub user events and verify resulting state or view.

**✅ DO:**
```javascript
describe('an attack power display', () => {
  beforeEach(() => {
    mockService = jest.fn();
    context = prepareContext(actor);
  });
  
  it('should include attack bonus in context', () => {
    expect(context.attackPowers[0].bonus).toBe(8);
  });
});
```

**❌ DON'T:**
```javascript
it('renders bonus', () => {
  expect(html).toContain('value="8"');
  expect(html).toContain('color: blue');
  await fetch('http://api.com');
});
it('calls _onMount()', () => {
  expect(component._onMount).toHaveBeenCalled();
});
```
"""

def create_bdd_specializing_rule(base_rule_file_name='bdd-rule.mdc'):
    """
    Create BDD rule - uses BDDRule production class.
    
    BDDRule implements framework specialization for:
    - Mamba: Python test files (*_test.py, test_*.py)
    - Jest: JavaScript/TypeScript test files (*.test.js, *.spec.js, *.test.ts, etc.)
    """
    return BDDRule(base_rule_file_name)

def create_bdd_command_with_specialized_rule(content, framework='mamba', instructions=None, generate=False):
    """Helper to create BDD command with specialized rule setup"""
    test_base_rule_content = create_bdd_base_rule_content()
    test_specialized_rule_content = create_bdd_specialized_rule_content(framework)
    
    def read_file_side_effect(file_path):
        """Return appropriate content based on file path"""
        file_str = str(file_path)
        if framework in file_str or f'bdd-rule-{framework}' in file_str:
            return test_specialized_rule_content
        return test_base_rule_content
    
    with patch.object(BaseRule, '_read_file_content', side_effect=read_file_side_effect):
        specializing_rule = create_bdd_specializing_rule('bdd-rule.mdc')
        # Manually create specialized rule since file discovery won't find it when mocking
        specialized_rule = SpecializedRule(rule_file_name=f'bdd-rule-{framework}.mdc', parent=specializing_rule)
        specializing_rule.specialized_rules[framework] = specialized_rule
        base_rule = specializing_rule.base_rule
        if generate:
            base_command = Command(content, base_rule, generate_instructions=instructions or "Please build test according to BDD rules")
        else:
            base_command = Command(content, base_rule, validate_instructions=instructions or "Please validate test as specified by BDD rules")
        return SpecializingRuleCommand(base_command, specializing_rule)

def create_bdd_run_state(test_file='test_test.py', state_data=None):
    """Create BDDRunState with optional state data"""
    if state_data is None:
        state_data = {
            "runs": [],
            "current_run_id": None,
            "phase": "signatures",
            "scope": "describe",
            "created_at": "2024-01-01T00:00:00"
        }
    
    # Mock the file system operations
    run_state = BDDRunState(test_file)
    run_state.state = state_data
    return run_state

def test_bdd_heuristic(content_lines, file_name, expected_violations, principle_number, framework='mamba'):
    """
    Helper function to test a BDD heuristic with specific content and expected violations.
    
    Args:
        content_lines: List of code lines to test (full content)
        file_name: Name of test file (e.g., 'test_test.py' or 'test.test.js')
        expected_violations: List of dicts with 'line', 'message_contains', and 'offending_content' keys
                           Example: [{'line': 1, 'message_contains': 'technical jargon', 'offending_content': 'PowerItem'}]
        principle_number: Which BDD principle to test (1-5)
        framework: 'mamba' or 'jest'
    
    Returns:
        (command, violations_found, principle) tuple for further assertions
    """
    # Create content
    content = Content(file_name, '.py' if framework == 'mamba' else '.js', content_lines=content_lines)
    
    # Setup rule content
    test_base_rule_content = create_bdd_base_rule_content()
    test_specialized_rule_content = create_bdd_specialized_rule_content(framework)
    
    def read_file_side_effect(file_path):
        """Return appropriate content based on file path"""
        file_str = str(file_path)
        if framework in file_str or f'bdd-rule-{framework}' in file_str:
            return test_specialized_rule_content
        return test_base_rule_content
    
    with patch.object(BaseRule, '_read_file_content', side_effect=read_file_side_effect):
        # Import BDDCommand - it automatically loads BDD heuristics
        import importlib.util
        bdd_runner_path = Path(__file__).parent / 'bdd-runner.py'
        spec = importlib.util.spec_from_file_location("bdd_runner", bdd_runner_path)
        bdd_runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bdd_runner)
        BDDCommand = bdd_runner.BDDCommand
        
        # Create command - heuristics are automatically loaded
        command = BDDCommand(content, 'bdd-rule.mdc')
        
        # Access violations property - this triggers scanning automatically
        violations = command.violations
        
        # Get target principle
        principles = command.principles
        target_principle = next((p for p in principles if p.principle_number == principle_number), None)
        
        # Assert - violations found at expected lines with expected offending content
        expect(isinstance(violations, list)).to(be_true)
        expect(target_principle.number).to(equal(principle_number))
        
        # Assert - violations match expected lines and contain offending content
        violation_lines = [v.line_number for v in violations]
        for expected in expected_violations:
            expected_line = expected['line']
            expect(expected_line in violation_lines).to(be_true)  # Violation found at expected line
            
            # Find violation at this line
            violation = next((v for v in violations if v.line_number == expected_line), None)
            expect(violation.line_number).to(equal(expected_line))
            
            # Assert violation message contains expected text
            if 'message_contains' in expected:
                expect(violation.message.lower()).to(contain(expected['message_contains'].lower()))
            
            # Assert violation code_snippet contains expected offending content
            if 'offending_content' in expected:
                offending = expected['offending_content']
                expect(violation.code_snippet).to(contain(offending))  # Offending content found in snippet
            
            # Assert violation has all required properties
            expect(violation.principle).to(equal(target_principle))
            expect(violation.principle.number).to(equal(principle_number))
            expect(violation.principle.name).to(equal(target_principle.name))
            expect(hasattr(violation, 'severity')).to(be_true)
        
        return (command, violations, target_principle)

# ============================================================================
# BDD-SPECIFIC TESTS
# ============================================================================

with description('a test file'):
    """BDD-specific: test file processing with BDD principles"""
    
    with context('that is being processed by a BDD command'):
        with before.each:
            self.content = Content('test_test.py', '.py')
        
        with context('that implements specializing rules for test frameworks (mamba and jest)'):
            with before.each:
                test_base_rule_content = create_bdd_base_rule_content()
                test_specialized_rule_content = create_bdd_specialized_rule_content('mamba')
                
                def read_file_side_effect(file_path):
                    file_str = str(file_path)
                    if 'mamba' in file_str or 'bdd-rule-mamba' in file_str:
                        return test_specialized_rule_content
                    return test_base_rule_content
                
                with patch.object(BaseRule, '_read_file_content', side_effect=read_file_side_effect):
                    self.specializing_rule = create_bdd_specializing_rule('bdd-rule.mdc')
                    self.mamba_specialized = SpecializedRule(rule_file_name='bdd-rule-mamba.mdc', parent=self.specializing_rule)
                    self.specializing_rule.specialized_rules['mamba'] = self.mamba_specialized
            
            with it('should select appropriate specialized rule based on file extension (mamba for .py, jest for .js/.ts)'):
                # Arrange
                base_rule = self.specializing_rule.base_rule
                base_command = Command(self.content, base_rule)
                command = SpecializingRuleCommand(base_command, self.specializing_rule)
                
                # Act
                selected_specialized = command.specialized_rule
                
                # Assert - BDDRule implements mamba (.py) and jest (.js/.ts) specialization
                # For .py files, should select mamba rule
                expect(selected_specialized).to(equal(self.mamba_specialized))
                expect(self.content.file_extension).to(equal('.py'))
            
            with it('should include BDD principles from base rule (applies to both mamba and jest)'):
                # Arrange
                base_rule = self.specializing_rule.base_rule
                base_command = Command(self.content, base_rule)
                command = SpecializingRuleCommand(base_command, self.specializing_rule)
                
                # Act
                principles = command.principles
                
                # Assert - BDDRule loads base BDD principles that apply to both mamba and jest
                # Should have 5 BDD principles
                expect(principles).to(have_length(5))
                expect(principles[0].principle_name).to(contain("Business Readable Language"))
                expect(principles[1].principle_name).to(contain("Comprehensive"))
                expect(principles[2].principle_name).to(contain("Balance Context"))
                expect(principles[3].principle_name).to(contain("Cover All Layers"))
                expect(principles[4].principle_name).to(contain("Unit Tests Front-End"))
            
            with context('and the specializing rule has been loaded'):
                with before.each:
                    # self.content and self.specializing_rule inherited from parent
                    pass
                
                with it('should have access to base rule with five principles'):
                    # Arrange
                    base_rule = self.specializing_rule.base_rule
                    
                    # Act
                    principles = base_rule.principles
                    
                    # Assert
                    expect(principles).to(have_length(5))
                    expect(principles[0].principle_number).to(equal(1))
                    expect(principles[4].principle_number).to(equal(5))
                
                with it('should provide access to specialized DO/DON\'T examples for each principle (mamba-specific or jest-specific)'):
                    # Arrange
                    base_rule = self.specializing_rule.base_rule
                    base_command = Command(self.content, base_rule)
                    command = SpecializingRuleCommand(base_command, self.specializing_rule)
                    
                    # Act
                    specialized = command.specialized_rule
                    principles = specialized.principles if specialized else []
                    examples = []
                    for principle in principles:
                        examples.extend(principle.examples)
                    
                    # Assert - BDDRule provides framework-specific examples
                    # Mamba examples use 'with description'/'with context' syntax
                    # Jest examples use 'describe'/'it' syntax
                    expect(examples).to(have_length(be_true))  # At least some examples
                    # Each example contains both DO and DON'T
                    expect(len(examples)).to(be_true)
                    for example in examples:
                        expect(hasattr(example, 'do_code')).to(be_true)
                        expect(hasattr(example, 'dont_code')).to(be_true)
                        expect(len(example.do_code) > 0 or len(example.dont_code) > 0).to(be_true)
            
            with context('that is being validated against BDD principles'):
                with before.each:
                    test_base_rule_content = create_bdd_base_rule_content()
                    with patch.object(BaseRule, '_read_file_content', return_value=test_base_rule_content):
                        self.base_rule = BaseRule('bdd-rule.mdc')
                
                with it('should load test code heuristics specific to the language (mamba or jest), for each principle from specialized rule'):
                    # Arrange
                    # BDDRule implements mamba and jest specialization
                    command = create_bdd_command_with_specialized_rule(self.content, 'mamba')
                    
                    # Act - specialized rule should provide principles with heuristics
                    specialized_rule = command.specialized_rule
                    principles = specialized_rule.principles if specialized_rule else []
                
                    expect(principles).to(have_length(5))
     
                    for principle in principles:
                        expect(principle.heuristics).not_to(be_none)  # Structure exists
                
            with context('that uses real BDD heuristics to detect violations'):
                # Test cases for each BDD principle
                heuristic_test_cases = [
                    {
                        'name': '§1 violations (Business Readable Language) - technical jargon and missing "should"',
                        'content_lines': [
                            "with description('PowerItem'):\n",  # Technical jargon - violates §1
                            "    with it('test_getDescriptor'):\n",  # Missing "should", technical naming - violates §1
                            "        pass\n"
                        ],
                        'file_name': 'bad_test.py',
                        'expected_violations': [
                            {'line': 1, 'message_contains': 'technical jargon', 'offending_content': 'PowerItem'},
                            {'line': 2, 'message_contains': 'should', 'offending_content': 'test_getDescriptor'}
                        ],
                        'principle_number': 1,
                        'framework': 'mamba',
                        'principle_name_contains': 'Business Readable Language',
                        'message_keywords': ['technical jargon', 'should'],
                        'expected_do_text': '',
                        'expected_do_code': "with description('a ranged damage power'):\n    with context('that has targeted and resulted in a successful attack'):\n        with it('should apply damage based on degrees of failure'):\n            expect(result.injuries).to(equal(2))",
                        'expected_dont_text': '',
                        'expected_dont_code': "with description('when attacking Target'):\nwith description('Power.execute()'):\nwith context('retrieved attack'):\nwith it('sets is_submitting flag'):"
                    },
                    {
                        'name': '§2 violations (Comprehensive and Brief) - internal assertions',
                        'content_lines': [
                            "with description('a user'):\n",
                            "    with it('should authenticate'):\n",
                            "        mock_service.toHaveBeenCalled()\n",  # Tests internal calls - violates §2
                            "        expect(mock_service.mock.calls).to(equal(1))\n"  # Mock internals - violates §2
                        ],
                        'file_name': 'bad_test.py',
                        'expected_violations': [
                            {'line': 3, 'message_contains': 'internal', 'offending_content': 'toHaveBeenCalled'},
                            {'line': 4, 'message_contains': 'internal', 'offending_content': 'mock.calls'}
                        ],
                        'principle_number': 2,
                        'framework': 'mamba',
                        'principle_name_contains': 'Comprehensive',
                        'message_keywords': ['internal', 'observable'],
                        'expected_do_text': '',
                        'expected_do_code': "with description('a damage power'):\n    with before.each:\n        self.mock_target = {'dodge': 15, 'injury': 0}\n    \n    with it('should be a ranged attack'):\n        expect(attack.is_ranged).to(equal(True))\n    \n    with it('should calculate DC from targets dodge'):\n        expect(attack.execute(self.mock_target).DC).to(equal(20))",
                        'expected_dont_text': '',
                        'expected_dont_code': "with it('calls _validate()'):\n    expect(form._flag).to(be_true)\n    expect(form._validate).to(have_been_called)\nwith it('handles attack'):"
                    },
                    {
                        'name': '§3 violations (Balance Context Sharing) - duplicate code in siblings',
                        'content_lines': [
                            "with description('a power item'):\n",
                            "    with it('should display fire descriptor'):\n",
                            "        power = create_power('fire')\n",  # Duplicate setup
                            "        expect(power.descriptor).to(equal('Fire'))\n",
                            "    with it('should display ice descriptor'):\n",
                            "        power = create_power('ice')\n",  # Duplicate setup
                            "        expect(power.descriptor).to(equal('Ice'))\n",
                            "    with it('should display water descriptor'):\n",
                            "        power = create_power('water')\n",  # Duplicate setup (3+ siblings)
                            "        expect(power.descriptor).to(equal('Water'))\n"
                        ],
                        'file_name': 'bad_test.py',
                        'expected_violations': [
                            {'line': 2, 'message_contains': 'duplicate', 'offending_content': 'create_power'}
                        ],
                        'principle_number': 3,
                        'framework': 'mamba',
                        'principle_name_contains': 'Balance Context',
                        'message_keywords': ['duplicate'],
                        'expected_do_text': '',
                        'expected_do_code': "def create_power(o=None):\n    return Power({**{'name': 'Test', 'rank': 10}, **(o or {})})\n\nwith description('a Power'):\n    with before.each:\n        self.factory = MockFactory()\n        self.factory.reset()\n        self.power = create_power()",
                        'expected_dont_text': '',
                        'expected_dont_code': "with description('Power'):\n    with context('created from actor'):\n        with before.each:\n            self.actor = {'id': '123'}\n    with context('that is ranged'):\n        with before.each:\n            self.actor = {'id': '123'}"
                    },
                    {
                        'name': '§4 violations (Cover All Layers) - excessive mocking',
                        'content_lines': [
                            "with description('a service'):\n",
                            "    with it('should process request'):\n",
                            "        jest.mock('dependency1')\n",  # Excessive mocking
                            "        jest.mock('dependency2')\n",
                            "        jest.mock('dependency3')\n",  # 3+ mocks suggests wrong focus
                            "        service.process()\n"
                        ],
                        'file_name': 'bad_test.js',
                        'expected_violations': [
                            {'line': 5, 'message_contains': 'dependencies', 'offending_content': 'jest.mock'}
                        ],
                        'principle_number': 4,
                        'framework': 'jest',
                        'principle_name_contains': 'Cover All Layers',
                        'message_keywords': ['dependencies', 'mock'],
                        'expected_do_text': '',
                        'expected_do_code': '',
                        'expected_dont_text': '',
                        'expected_dont_code': ''
                    },
                    {
                        'name': '§5 violations (Unit Tests Front-End) - implementation details',
                        'content_lines': [
                            "describe('a component', () => {\n",
                            "    it('should render', () => {\n",
                            "        const wrapper = mount(<Component />)\n",
                            "        expect(wrapper.state().isVisible).toBe(true)\n",  # Tests state - violates §5
                            "        expect(wrapper.instance().props).toEqual({})\n"  # Tests instance - violates §5
                        ],
                        'file_name': 'component.test.jsx',
                        'expected_violations': [
                            {'line': 4, 'message_contains': 'implementation', 'offending_content': 'state()'},
                            {'line': 5, 'message_contains': 'implementation', 'offending_content': 'instance()'}
                        ],
                        'principle_number': 5,
                        'framework': 'jest',
                        'principle_name_contains': 'Front-End',
                        'message_keywords': ['implementation'],
                        'expected_do_text': '',
                        'expected_do_code': "with description('an attack power display'):\n    with before.each:\n        self.mock_service = Mock()\n        self.context = prepare_context(self.actor)\n    \n    with it('should include attack bonus in context'):\n        expect(self.context['attack_powers'][0]['bonus']).to(equal(8))",
                        'expected_dont_text': '',
                        'expected_dont_code': "with it('renders bonus'):\n    expect(html).to(contain('value=\"8\"'))\n    expect(html).to(contain('color: blue'))\n    requests.get('http://api.com')\nwith it('calls _on_mount()'):\n    expect(component._on_mount).to(have_been_called)"
                    }
                ]
                
                # Parameterized test - runs same logic for each test case
                for test_case in heuristic_test_cases:
                    with it(f'should detect {test_case["name"]}'):
                        # Act - test heuristic using helper
                        command, violations, principle = test_bdd_heuristic(
                            test_case['content_lines'],
                            test_case['file_name'],
                            test_case['expected_violations'],
                            test_case['principle_number'],
                            test_case['framework']
                        )
                        
                        # Assert - violations found (helper already validates offending content)
                        expect(command.violations).to(have_length(be_true))  # Violations property populated
                        expect(violations).to(equal(command.violations))  # Same violations from property
                        
                        # Assert - violations are associated with principle
                        expect(principle.number).to(equal(test_case['principle_number']))
                        expect(principle.name).to(contain(test_case['principle_name_contains']))
                        
                        # Assert - principle has examples with exact DO and DON'T text and code
                        expect(principle.examples).to(have_length(be_true))  # At least one example
                        for example in principle.examples:
                            expect(hasattr(example, 'do_text')).to(be_true)
                            expect(hasattr(example, 'do_code')).to(be_true)
                            expect(hasattr(example, 'dont_text')).to(be_true)
                            expect(hasattr(example, 'dont_code')).to(be_true)
                            
                            # Assert exact values if expected
                            if test_case.get('expected_do_text') is not None:
                                expect(example.do_text).to(equal(test_case['expected_do_text']))
                            if test_case.get('expected_do_code'):
                                expect(example.do_code).to(contain(test_case['expected_do_code']))
                            if test_case.get('expected_dont_text') is not None:
                                expect(example.dont_text).to(equal(test_case['expected_dont_text']))
                            if test_case.get('expected_dont_code'):
                                expect(example.dont_code).to(contain(test_case['expected_dont_code']))
                        
                        # Assert - violations have all required properties (helper validates exact values)
                        for violation in violations:
                            expect(violation.principle.number).to(equal(test_case['principle_number']))
                            expect(violation.principle.name).to(contain(test_case['principle_name_contains']))
                            expect(violation.principle).to(equal(principle))  # Principle object matches
                        
                        # Assert - violation messages contain expected keywords
                        if violations and test_case.get('message_keywords'):
                            messages = [v.message.lower() for v in violations]
                            has_keyword = any(keyword.lower() in msg for keyword in test_case['message_keywords'] for msg in messages)
                            expect(has_keyword).to(be_true)
                
                with it('should assemble related violations, principles, and examples into checklist report'):
                    # Arrange
                    violations = [Violation(1, "Test uses technical jargon"), Violation(2, "Test name doesn't use 'should'")]
                    principles = self.base_rule.principles[:2]
                    report = ViolationReport(violations=violations, principles=principles, report_format='CHECKLIST')
                    
                    # Act
                    violations_count = len(report.violations)
                    principles_count = len(report.principles)
                    
                    # Assert
                    expect(violations_count).to(equal(2))
                    expect(principles_count).to(equal(2))
                    expect(report.report_format).to(equal('CHECKLIST'))
        
        with context('that is executed through incremental runs'):
            with before.each:
                self.max_sample_size = 18
                # Create a temporary test file with describe/it blocks
                # This structure tests the algorithm with multiple nesting levels:
                # - Top level: 'a power system' (describe)
                #   - Level 1: 'that manages power items' (context)
                #     - Level 2: 'that has fire type' (context) - 5 it blocks (lowest level)
                #     - Level 2: 'that has water type' (context) - 3 it blocks
                #   - Level 1: 'that manages power effects' (context)
                #     - Level 2: 'that applies damage' (context) - 4 it blocks
                #   - Level 1: 'that validates power usage' (context) - 2 it blocks (direct)
                # The algorithm should find 'that has fire type' as lowest-level (highest indent) with 5 it blocks
                self.test_file = Path(__file__).parent / 'test_bdd_sample.py'
                test_file_content = """from mamba import description, context, it
from expects import expect, equal

with description('a power system'):
    with context('that manages power items'):
        with context('that has fire type'):
            with it('should display fire descriptor'):
                pass
            with it('should apply fire damage'):
                pass
            with it('should resist water attacks'):
                pass
            with it('should increase fire resistance'):
                pass
            with it('should trigger fire effects'):
                pass
        with context('that has water type'):
            with it('should display water descriptor'):
                pass
            with it('should apply water damage'):
                pass
            with it('should resist fire attacks'):
                pass
    with context('that manages power effects'):
        with context('that applies damage'):
            with it('should calculate base damage'):
                pass
            with it('should apply damage modifiers'):
                pass
            with it('should respect damage resistance'):
                pass
            with it('should trigger damage events'):
                pass
    with context('that validates power usage'):
        with it('should check power availability'):
            pass
        with it('should validate power requirements'):
            pass
"""
                self.test_file.write_text(test_file_content, encoding='utf-8')
                
                test_base_rule_content = create_bdd_base_rule_content()
                test_specialized_rule_content = create_bdd_specialized_rule_content('mamba')
                
                def read_file_side_effect_for_incremental(file_path):
                    """Return appropriate content based on file path"""
                    file_str = str(file_path)
                    if 'mamba' in file_str or 'bdd-rule-mamba' in file_str:
                        return test_specialized_rule_content
                    return test_base_rule_content
                
                with patch.object(BaseRule, '_read_file_content', side_effect=read_file_side_effect_for_incremental):
                    self.base_rule = BaseRule('bdd-rule.mdc')
                    bdd_command = BDDCommand(self.content, 'bdd-rule.mdc')
                    self.command = BDDIncrementalCommand(bdd_command, self.base_rule, str(self.test_file), self.max_sample_size)
            
            with it('should calculate sample size by parsing BDD test file and counting it blocks in lowest-level describe block'):
                # Arrange
                command = self.command
                
                # Act
                sample_size = command.sample_size
                
                # Assert
                expect(sample_size).to(equal(5))  # 'that has fire type' has 5 it blocks
            
            with it('should cap sample size at max_sample_size when parsed sample is bigger'):
                # Arrange - create a test file with more than max_sample_size 'it' blocks
                large_test_file = Path(__file__).parent / 'test_bdd_large_sample.py'
                large_test_content = """from mamba import description, context, it
from expects import expect, equal

with description('a large test suite'):
    with context('that has many tests'):
"""
                # Add 25 'it' blocks (more than max_sample_size of 18)
                for i in range(25):
                    large_test_content += f"        with it('should test behavior {i}'):\n            pass\n"
                large_test_file.write_text(large_test_content, encoding='utf-8')
                
                test_base_rule_content = create_bdd_base_rule_content()
                test_specialized_rule_content = create_bdd_specialized_rule_content('mamba')
                
                def read_file_side_effect_large(file_path):
                    file_str = str(file_path)
                    if 'mamba' in file_str or 'bdd-rule-mamba' in file_str:
                        return test_specialized_rule_content
                    return test_base_rule_content
                
                with patch.object(BaseRule, '_read_file_content', side_effect=read_file_side_effect_large):
                    base_rule = BaseRule('bdd-rule.mdc')
                    bdd_command = BDDCommand(self.content, 'bdd-rule.mdc')
                    large_command = BDDIncrementalCommand(bdd_command, base_rule, str(large_test_file), self.max_sample_size)
                
                # Act
                sample_size = large_command.sample_size
                
                # Assert
                expect(sample_size).to(equal(18))  # Capped at max_sample_size, not 25
                
                # Cleanup
                if large_test_file.exists():
                    large_test_file.unlink()
        
        with context('that has started the BDD workflow'):
            with before.each:
                test_base_rule_content = create_bdd_base_rule_content()
                with patch.object(BaseRule, '_read_file_content', return_value=test_base_rule_content):
                    bdd_command = BDDCommand(self.content, 'bdd-rule.mdc')
                    self.test_file = 'test_test.py'
                    self.framework = 'mamba'
                    self.workflow = create_bdd_workflow(bdd_command, self.test_file, self.framework)
            
            with it('should create workflow with phases in correct order'):
                # Arrange
                workflow = self.workflow
                
                # Assert
                expect(len(workflow.phases)).to(equal(5))
                expect(workflow.phases[0].name).to(contain("Domain Scaffolding"))
                expect(workflow.phases[1].name).to(contain("Build Test Signatures"))
                expect(workflow.phases[2].name).to(contain("RED"))
                expect(workflow.phases[3].name).to(contain("GREEN"))
                expect(workflow.phases[4].name).to(contain("REFACTOR"))
            
            
            with it('should wrap BDDCommand with IncrementalCommand in workflow phases'):
                # Arrange
                workflow = self.workflow
                phase = workflow.phases[0]
                
                # Assert - verify the wrapping chain: BDDWorkflowPhaseCommand → WorkflowPhaseCommand → IncrementalCommand → BDDCommand
                # The phase_command should be a WorkflowPhaseCommand
                expect(phase.phase_command).not_to(be_none)
                expect(isinstance(phase.phase_command, WorkflowPhaseCommand)).to(be_true)
                
                # The WorkflowPhaseCommand should wrap an IncrementalCommand
                inner_command = phase.phase_command._inner_command
                expect(inner_command).not_to(be_none)
                expect(isinstance(inner_command, IncrementalCommand)).to(be_true)
                
                # Verify IncrementalCommand has max_sample_size attribute
                expect(hasattr(inner_command, 'max_sample_size')).to(be_true)
                
                # The IncrementalCommand should wrap a BDDCommand
                bdd_command = inner_command._inner_command
                expect(bdd_command).not_to(be_none)
                expect(isinstance(bdd_command, BDDCommand)).to(be_true)
                
                # The BDDCommand should wrap a CodeAugmentedCommand
                code_augmented_command = bdd_command._inner_command
                expect(code_augmented_command).not_to(be_none)
                expect(isinstance(code_augmented_command, CodeAugmentedCommand)).to(be_true)
            
            with it('should delegate generate() to wrapped command through IncrementalCommand'):
                # Arrange - create a mock BDDCommand to verify delegation
                test_base_rule_content = create_bdd_base_rule_content()
                with patch.object(BaseRule, '_read_file_content', return_value=test_base_rule_content):
                    mock_bdd_command = MagicMock(spec=BDDCommand)
                    mock_bdd_command.generate.return_value = 'generated instructions'
                    mock_bdd_command.content = self.content
                    mock_bdd_command.base_rule = BaseRule('bdd-rule.mdc')
                    
                    # Create workflow with mocked command
                    test_workflow = create_bdd_workflow(mock_bdd_command, self.test_file, self.framework)
                    phase = test_workflow.phases[0]
                    
                    # Act
                    result = phase.generate()
                    
                    # Assert - verify generate was called on the wrapped BDDCommand (through IncrementalCommand)
                    expect(mock_bdd_command.generate.called).to(be_true)
                    expect(result).to(equal('generated instructions'))
            
            with it('should delegate validate() to wrapped command'):
                # Arrange - create a mock BDDCommand to verify delegation
                mock_bdd_command = MagicMock(spec=BDDCommand)
                mock_bdd_command.validate.return_value = 'validation report'
                mock_bdd_command.content = self.content
                
                # Create workflow with mocked command
                test_workflow = create_bdd_workflow(mock_bdd_command, self.test_file, self.framework)
                phase = test_workflow.phases[0]
                
                # Act
                result = phase.validate()
                
                # Assert - verify validate was called on the wrapped command
                expect(mock_bdd_command.validate.called).to(be_true)
                expect(result).to(equal('validation report'))
            
            with it('should delegate validate() with report_format parameter'):
                # Arrange - create a mock BDDCommand to verify delegation
                mock_bdd_command = MagicMock(spec=BDDCommand)
                mock_bdd_command.validate.return_value = 'detailed report'
                mock_bdd_command.content = self.content
                
                # Create workflow with mocked command
                test_workflow = create_bdd_workflow(mock_bdd_command, self.test_file, self.framework)
                phase = test_workflow.phases[0]
                
                # Act
                result = phase.validate(report_format='DETAILED')
                
                # Assert - verify validate was called with correct parameter
                expect(mock_bdd_command.validate.called).to(be_true)
                expect(mock_bdd_command.validate.call_args[1]['report_format']).to(equal('DETAILED'))
                expect(result).to(equal('detailed report'))
            
            with context('that verifies command wrapping chain structure'):
                with it('should have correct wrapping chain for all phases'):
                    # Arrange
                    workflow = self.workflow
                    
                    # Assert - verify all phases have the correct wrapping chain
                    for phase in workflow.phases:
                        # BDDWorkflowPhaseCommand wraps WorkflowPhaseCommand
                        expect(phase.phase_command).not_to(be_none)
                        expect(isinstance(phase.phase_command, WorkflowPhaseCommand)).to(be_true)
                        
                        # WorkflowPhaseCommand wraps IncrementalCommand
                        incremental_cmd = phase.phase_command._inner_command
                        expect(incremental_cmd).not_to(be_none)
                        expect(isinstance(incremental_cmd, IncrementalCommand)).to(be_true)
                        
                        # IncrementalCommand wraps BDDCommand
                        bdd_cmd = incremental_cmd._inner_command
                        expect(bdd_cmd).not_to(be_none)
                        expect(isinstance(bdd_cmd, BDDCommand)).to(be_true)
                        
                        # BDDCommand wraps CodeAugmentedCommand
                        code_augmented_cmd = bdd_cmd._inner_command
                        expect(code_augmented_cmd).not_to(be_none)
                        expect(isinstance(code_augmented_cmd, CodeAugmentedCommand)).to(be_true)
                
                with it('should delegate generate() through entire wrapping chain'):
                    # Arrange - use real commands (not mocks) to test actual delegation
                    workflow = self.workflow
                    phase = workflow.phases[0]
                    
                    # Mock the innermost CodeAugmentedCommand's generate method
                    code_augmented_cmd = phase.phase_command._inner_command._inner_command._inner_command
                    original_generate = code_augmented_cmd.generate
                    code_augmented_cmd.generate = MagicMock(return_value='generated content')
                    
                    try:
                        # Act
                        result = phase.generate()
                        
                        # Assert - verify generate was called on the innermost command
                        expect(code_augmented_cmd.generate.called).to(be_true)
                        expect(result).to(equal('generated content'))
                    finally:
                        # Restore original method
                        code_augmented_cmd.generate = original_generate
                
                with it('should delegate validate() through entire wrapping chain'):
                    # Arrange - use real commands (not mocks) to test actual delegation
                    workflow = self.workflow
                    phase = workflow.phases[0]
                    
                    # Mock the innermost CodeAugmentedCommand's validate method
                    code_augmented_cmd = phase.phase_command._inner_command._inner_command._inner_command
                    original_validate = code_augmented_cmd.validate
                    code_augmented_cmd.validate = MagicMock(return_value='validation report')
                    
                    try:
                        # Act
                        result = phase.validate(report_format='CHECKLIST')
                        
                        # Assert - verify validate was called on the innermost command
                        expect(code_augmented_cmd.validate.called).to(be_true)
                        expect(result).to(equal('validation report'))
                    finally:
                        # Restore original method
                        code_augmented_cmd.validate = original_validate
                
                with it('should preserve IncrementalCommand max_sample_size through wrapping'):
                    # Arrange
                    workflow = self.workflow
                    phase = workflow.phases[0]
                    
                    # Act - get the IncrementalCommand
                    incremental_cmd = phase.phase_command._inner_command
                    
                    # Assert - verify max_sample_size is accessible
                    expect(hasattr(incremental_cmd, 'max_sample_size')).to(be_true)
                    expect(incremental_cmd.max_sample_size).to(equal(18))  # Default value
                
                with it('should preserve BDDCommand test_file and framework through wrapping'):
                    # Arrange
                    workflow = self.workflow
                    phase = workflow.phases[0]
                    
                    # Act - get the BDDCommand
                    bdd_cmd = phase.phase_command._inner_command._inner_command
                    
                    # Assert - verify BDDCommand attributes are accessible
                    expect(hasattr(bdd_cmd, 'test_file')).to(be_true)
                    expect(hasattr(bdd_cmd, 'framework')).to(be_true)
                    expect(bdd_cmd.test_file).to(equal(self.test_file))
                    expect(bdd_cmd.framework).to(equal(self.framework))

