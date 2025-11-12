"""Clean Code Runner Tests"""
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
from expects import expect, equal, be_true, be_false, contain, have_length, be_none, be_empty
from unittest.mock import Mock, patch, MagicMock
import json
from pathlib import Path

# Import domain classes
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from common_command_runner.common_command_runner import (
    Content,
    CodeHeuristic,
    Violation
)

# Import clean-code runner
import importlib.util
runner_path = Path(__file__).parent / 'clean-code-runner.py'
spec = importlib.util.spec_from_file_location("clean_code_runner", runner_path)
clean_code_runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clean_code_runner)

CleanCodeRule = clean_code_runner.CleanCodeRule
CleanCodeCommand = clean_code_runner.CleanCodeCommand
DeepNestingHeuristic = clean_code_runner.DeepNestingHeuristic
MagicNumberHeuristic = clean_code_runner.MagicNumberHeuristic
SingleLetterVariableHeuristic = clean_code_runner.SingleLetterVariableHeuristic
CommentedCodeHeuristic = clean_code_runner.CommentedCodeHeuristic
LargeFunctionHeuristic = clean_code_runner.LargeFunctionHeuristic
TooManyParametersHeuristic = clean_code_runner.TooManyParametersHeuristic
LargeClassHeuristic = clean_code_runner.LargeClassHeuristic
extract_functions_from_content = clean_code_runner.extract_functions_from_content
extract_classes_from_content = clean_code_runner.extract_classes_from_content


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_content(file_path='test.py', content_lines=None):
    """Create Content object for testing"""
    return Content(
        file_path=file_path,
        file_extension=Path(file_path).suffix,
        content_lines=content_lines
    )


# ============================================================================
# TESTS
# ============================================================================

with description('CleanCodeRule') as self:
    with context('when detecting framework from file'):
        with it('detects Python from .py extension'):
            result = CleanCodeRule.detect_framework_from_file('test.py')
            expect(result).to(equal('python'))
        
        with it('detects Python from .pyi extension'):
            result = CleanCodeRule.detect_framework_from_file('test.pyi')
            expect(result).to(equal('python'))
        
        with it('detects JavaScript from .js extension'):
            result = CleanCodeRule.detect_framework_from_file('test.js')
            expect(result).to(equal('javascript'))
        
        with it('detects JavaScript from .mjs extension'):
            result = CleanCodeRule.detect_framework_from_file('test.mjs')
            expect(result).to(equal('javascript'))
        
        with it('detects JavaScript from .ts extension'):
            result = CleanCodeRule.detect_framework_from_file('test.ts')
            expect(result).to(equal('javascript'))
        
        with it('detects JavaScript from .tsx extension'):
            result = CleanCodeRule.detect_framework_from_file('test.tsx')
            expect(result).to(equal('javascript'))
        
        with it('returns None for unsupported extensions'):
            result = CleanCodeRule.detect_framework_from_file('test.rb')
            expect(result).to(be_none)


with description('DeepNestingHeuristic') as self:
    with before.each:
        self.heuristic = DeepNestingHeuristic()
    
    with context('when detecting deep nesting'):
        with it('detects critical nesting (7+ levels)'):
            lines = [
                'def test():\n',
                '    if a:\n',
                '        if b:\n',
                '            if c:\n',
                '                if d:\n',
                '                    if e:\n',
                '                        if f:\n',
                '                            if g:\n',  # Level 7
                '                                pass\n'
            ]
            content = create_content('test.py', lines)
            violations = self.heuristic.detect_violations(content)
            
            expect(violations).not_to(be_none)
            expect(violations).to(have_length(1))
            expect(violations[0].severity).to(equal('critical'))
            expect(violations[0].principle).to(equal('1.4 Simple Control Flow'))
        
        with it('detects important nesting (4-6 levels)'):
            lines = [
                'def test():\n',
                '    if a:\n',
                '        if b:\n',
                '            if c:\n',
                '                if d:\n',  # Level 4
                '                    pass\n'
            ]
            content = create_content('test.py', lines)
            violations = self.heuristic.detect_violations(content)
            
            expect(violations).not_to(be_none)
            expect(violations[0].severity).to(equal('important'))
        
        with it('detects suggested nesting (3 levels)'):
            lines = [
                'def test():\n',
                '    if a:\n',
                '        if b:\n',
                '            if c:\n',  # Level 3
                '                pass\n'
            ]
            content = create_content('test.py', lines)
            violations = self.heuristic.detect_violations(content)
            
            expect(violations).not_to(be_none)
            expect(violations[0].severity).to(equal('suggested'))


with description('MagicNumberHeuristic') as self:
    with before.each:
        self.heuristic = MagicNumberHeuristic()
    
    with context('when detecting magic numbers'):
        with it('detects numeric literals'):
            lines = [
                'total = subtotal * 1.13\n'
            ]
            content = create_content('test.py', lines)
            violations = self.heuristic.detect_violations(content)
            
            expect(violations).not_to(be_none)
            expect(violations).to(have_length(1))
            expect(violations[0].principle).to(equal('2.3 Meaningful Context'))
        
        with it('ignores common patterns like range()'):
            lines = [
                'for i in range(100):\n'
            ]
            content = create_content('test.py', lines)
            violations = self.heuristic.detect_violations(content)
            
            expect(violations).to(be_none)
        
        with it('ignores single-digit numbers'):
            lines = [
                'total = subtotal * 2\n'
            ]
            content = create_content('test.py', lines)
            violations = self.heuristic.detect_violations(content)
            
            expect(violations).to(be_none)


with description('SingleLetterVariableHeuristic') as self:
    with before.each:
        self.heuristic = SingleLetterVariableHeuristic()
    
    with context('when detecting single-letter variables'):
        with it('detects single-letter variables'):
            lines = [
                'd = calculate_total()\n'
            ]
            content = create_content('test.py', lines)
            violations = self.heuristic.detect_violations(content)
            
            expect(violations).not_to(be_none)
            expect(violations).to(have_length(1))
            expect(violations[0].principle).to(equal('2.1 Intention-Revealing Names'))
        
        with it('ignores loop variables'):
            lines = [
                'for i in items:\n'
            ]
            content = create_content('test.py', lines)
            violations = self.heuristic.detect_violations(content)
            
            expect(violations).to(be_none)


with description('CommentedCodeHeuristic') as self:
    with before.each:
        self.heuristic = CommentedCodeHeuristic()
    
    with context('when detecting commented code'):
        with it('detects commented Python code'):
            lines = [
                '# def old_function():\n'
            ]
            content = create_content('test.py', lines)
            violations = self.heuristic.detect_violations(content)
            
            expect(violations).not_to(be_none)
            expect(violations).to(have_length(1))
            expect(violations[0].principle).to(equal('7.3 Bad Comments'))
        
        with it('detects commented JavaScript code'):
            lines = [
                '// function oldFunction() {\n'
            ]
            content = create_content('test.js', lines)
            violations = self.heuristic.detect_violations(content)
            
            expect(violations).not_to(be_none)
            expect(violations).to(have_length(1))


with description('LargeFunctionHeuristic') as self:
    with before.each:
        self.heuristic = LargeFunctionHeuristic()
    
    with context('when detecting large functions'):
        with it('detects critical large functions (>50 lines)'):
            lines = ['def test():\n'] + ['    pass\n'] * 60
            content = create_content('test.py', lines)
            violations = self.heuristic.detect_violations(content)
            
            expect(violations).not_to(be_none)
            expect(violations[0].severity).to(equal('critical'))
            expect(violations[0].principle).to(equal('1.2 Small and Focused Functions'))
        
        with it('detects important large functions (21-50 lines)'):
            lines = ['def test():\n'] + ['    pass\n'] * 25
            content = create_content('test.py', lines)
            violations = self.heuristic.detect_violations(content)
            
            expect(violations).not_to(be_none)
            expect(violations[0].severity).to(equal('important'))


with description('TooManyParametersHeuristic') as self:
    with before.each:
        self.heuristic = TooManyParametersHeuristic()
    
    with context('when detecting too many parameters'):
        with it('detects functions with >3 parameters'):
            lines = [
                'def test(a, b, c, d):\n',
                '    pass\n'
            ]
            content = create_content('test.py', lines)
            violations = self.heuristic.detect_violations(content)
            
            expect(violations).not_to(be_none)
            expect(violations).to(have_length(1))
            expect(violations[0].principle).to(equal('1.3 Clear Parameters'))
            expect('4 parameters').to(be_in(violations[0].message))


with description('LargeClassHeuristic') as self:
    with before.each:
        self.heuristic = LargeClassHeuristic()
    
    with context('when detecting large classes'):
        with it('detects critical large classes (>300 lines)'):
            lines = ['class Test:\n'] + ['    pass\n'] * 350
            content = create_content('test.py', lines)
            violations = self.heuristic.detect_violations(content)
            
            expect(violations).not_to(be_none)
            expect(violations[0].severity).to(equal('critical'))
            expect(violations[0].principle).to(equal('6.2 Small and Compact Classes'))
        
        with it('detects important large classes (201-300 lines)'):
            lines = ['class Test:\n'] + ['    pass\n'] * 220
            content = create_content('test.py', lines)
            violations = self.heuristic.detect_violations(content)
            
            expect(violations).not_to(be_none)
            expect(violations[0].severity).to(equal('important'))


with description('extract_functions_from_content') as self:
    with context('when extracting Python functions'):
        with it('extracts function name and parameters'):
            lines = [
                'def test_function(param1, param2):\n',
                '    pass\n'
            ]
            content = create_content('test.py', lines)
            functions = extract_functions_from_content(content)
            
            expect(functions).to(have_length(1))
            expect(functions[0]['name']).to(equal('test_function'))
            expect(functions[0]['param_count']).to(equal(2))
        
        with it('calculates function length'):
            lines = [
                'def test_function():\n',
                '    pass\n',
                '    pass\n',
                '    pass\n'
            ]
            content = create_content('test.py', lines)
            functions = extract_functions_from_content(content)
            
            expect(functions[0]['length']).to(be_above(0))
    
    with context('when extracting JavaScript functions'):
        with it('extracts function name and parameters'):
            lines = [
                'function testFunction(param1, param2) {\n',
                '  return true;\n',
                '}\n'
            ]
            content = create_content('test.js', lines)
            functions = extract_functions_from_content(content)
            
            expect(functions).to(have_length(1))
            expect(functions[0]['name']).to(equal('testFunction'))
            expect(functions[0]['param_count']).to(equal(2))
        
        with it('extracts arrow functions'):
            lines = [
                'const testFunction = (param1, param2) => {\n',
                '  return true;\n',
                '};\n'
            ]
            content = create_content('test.js', lines)
            functions = extract_functions_from_content(content)
            
            expect(functions).to(have_length(1))
            expect(functions[0]['name']).to(equal('testFunction'))


with description('extract_classes_from_content') as self:
    with context('when extracting Python classes'):
        with it('extracts class name'):
            lines = [
                'class TestClass:\n',
                '    pass\n'
            ]
            content = create_content('test.py', lines)
            classes = extract_classes_from_content(content)
            
            expect(classes).to(have_length(1))
            expect(classes[0]['name']).to(equal('TestClass'))
        
        with it('calculates class length'):
            lines = [
                'class TestClass:\n',
                '    def __init__(self):\n',
                '        pass\n',
                '    def method(self):\n',
                '        pass\n'
            ]
            content = create_content('test.py', lines)
            classes = extract_classes_from_content(content)
            
            expect(classes[0]['length']).to(be_above(0))
    
    with context('when extracting JavaScript classes'):
        with it('extracts class name'):
            lines = [
                'class TestClass {\n',
                '  constructor() {}\n',
                '}\n'
            ]
            content = create_content('test.js', lines)
            classes = extract_classes_from_content(content)
            
            expect(classes).to(have_length(1))
            expect(classes[0]['name']).to(equal('TestClass'))


with description('CleanCodeCommand') as self:
    with before.each:
        self.command = CleanCodeCommand()
    
    with context('when initializing'):
        with it('has correct command name'):
            expect(self.command.command_name).to(equal('clean-code'))
        
        with it('has correct actions'):
            expect(self.command.actions).to(equal(['generate', 'validate', 'correct']))
    
    with context('when getting heuristics'):
        with it('returns list of heuristics'):
            heuristics = self.command.get_heuristics()
            
            expect(heuristics).not_to(be_empty)
            expect(len(heuristics)).to(equal(7))

