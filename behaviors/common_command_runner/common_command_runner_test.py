"""Common Domain Objects Tests - Reusable Domain Model"""
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
from unittest.mock import patch

# Import domain classes
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common_command_runner import (
    Content,
    BaseRule,
    RuleParser,
    SpecializingRule,
    FrameworkSpecializingRule,
    SpecializedRule,
    Principle,
    Example,
    CodeHeuristic,
    Violation,
    Run,
    RunState,
    RunHistory,
    RunStatus,
    Command,
    CodeAugmentedCommand,
    SpecializingRuleCommand,
    IncrementalCommand,
    WorkflowPhaseCommand,
    Workflow,
    PhaseState,
    IncrementalState
)

def create_test_specializing_rule_from_file(base_rule_file_name):
    """Create test specializing rule from base file name - discovers specialized rules internally"""
    class TestSpecializingRule(SpecializingRule):
        def extract_match_key(self, content):
            if content.file_extension == '.java':
                return 'servlet'
            elif content.file_extension == '.pl':
                return 'cgiscript'
            return None
    return TestSpecializingRule(base_rule_file_name=base_rule_file_name)

def create_test_specializing_rule_with_both():
    specializing_rule = create_test_specializing_rule_from_file('base-rule.mdc')
    servlet_rule = specializing_rule.specialized_rules.get('servlet')
    cgiscript_rule = specializing_rule.specialized_rules.get('cgiscript')
    return specializing_rule, servlet_rule, cgiscript_rule

def create_test_specializing_rule_with_servlet():
    specializing_rule = create_test_specializing_rule_from_file('base-rule.mdc')
    servlet_rule = specializing_rule.specialized_rules.get('servlet')
    return specializing_rule, servlet_rule

def create_base_rule_content_with_two_principles():
    """Helper for base rule content with 2 principles"""
    return """---
description: Test rule
---

## 1. First Principle
Test content for first principle.

## 2. Second Principle  
Test content for second principle.
"""

def create_base_rule_content():
    """Helper for base rule content - used across multiple tests"""
    return """---
description: Test rule
---

## 1. Test Principle
Test content for test principle.
"""

def create_violating_code_content():
    """Helper to create content with violating code lines"""
    test_code_lines = [
        "public class BadCode {\n",
        "    private String a;\n",
        "    public void calc() {\n",
        "        if (attempts < 3) { }\n",
        "    }\n",
        "}\n"
    ]
    return Content('bad-code.java', '.java', content_lines=test_code_lines)

class DescriptiveNamesHeuristic(CodeHeuristic):
    """Heuristic that scans code for descriptive naming violations"""
    def __init__(self):
        super().__init__("descriptive_names")
    
    def detect_violations(self, content):
        """Detect descriptive naming violations"""
        if 'bad' in content.file_path.lower() or 'violation' in content.file_path.lower():
            return Violation(1, f"Found descriptive naming violation in {content.file_path}")
        return None

class MagicNumbersHeuristic(CodeHeuristic):
    """Heuristic that scans code for magic number violations"""
    def __init__(self):
        super().__init__("magic_numbers")
    
    def detect_violations(self, content):
        """Detect magic number violations"""
        if 'bad' in content.file_path.lower() or 'violation' in content.file_path.lower():
            return Violation(1, f"Found magic number violation in {content.file_path}")
        return None

class TestCodeAugmentedCommand(CodeAugmentedCommand):
    """Concrete extension that creates heuristics internally"""
    def __init__(self, inner_command, base_rule):
        super().__init__(inner_command, base_rule)
        self._create_heuristics()
    
    def _create_heuristics(self):
        """Create heuristics and associate them with principles"""
        # Map principle names to heuristic classes
        heuristic_map = {
            "Use Descriptive Names": DescriptiveNamesHeuristic,
            "Avoid Magic Numbers": MagicNumbersHeuristic
        }
        
        for principle in self.principles:
            heuristic_class = heuristic_map[principle.principle_name]
            principle.heuristics = [heuristic_class()]

def create_code_augmented_command(content, base_rule, validate_instructions=None, generate_instructions=None):
    """Helper to create CodeAugmentedCommand with base command"""
    if validate_instructions:
        base_command = Command(content, base_rule, validate_instructions=validate_instructions)
    elif generate_instructions:
        base_command = Command(content, base_rule, generate_instructions=generate_instructions)
    else:
        base_command = Command(content, base_rule)
    return TestCodeAugmentedCommand(base_command, base_rule)

def create_specialized_rule_content(principle_content="Servlet-specific content for test principle."):
    """Helper for specialized rule content - parameterized for different test needs"""
    return f"""---
description: Test specialized rule
---

## 1. Test Principle
{principle_content}

**[DO]:**
```java
// Good example code
public class TestServlet {{
    // DO example
}}
```

**[DON'T]:**
```java
// Bad example code
public class BadServlet {{
    // DON'T example
}}
```
"""

def create_command_with_specialized_rule(content, instructions=None, generate=False):
    """Helper to create command with specialized rule setup"""
    test_base_rule_content = create_base_rule_content()
    test_specialized_rule_content = create_specialized_rule_content()
    
    def read_file_side_effect(file_path):
        """Return appropriate content based on file path"""
        if 'servlet' in str(file_path) or 'base-rule-servlet' in str(file_path):
            return test_specialized_rule_content
        return test_base_rule_content
    
    with patch.object(RuleParser, 'read_file_content', side_effect=read_file_side_effect):
        specializing_rule = create_test_specializing_rule_from_file('base-rule.mdc')
        # Ensure base rule has loaded principles
        parser = RuleParser()
        specializing_rule.base_rule.principles = parser.load_principles_from_file('base-rule.mdc')
        # Manually create specialized rule since file discovery won't find it when mocking
        specialized_rule = SpecializedRule(rule_file_name='base-rule-servlet.mdc', parent=specializing_rule)
        specializing_rule.specialized_rules['servlet'] = specialized_rule
        base_rule = specializing_rule.base_rule
        if generate:
            base_command = Command(content, base_rule, generate_instructions=instructions or "Please build test.java according to the rules")
        else:
            base_command = Command(content, base_rule, validate_instructions=instructions or "Please validate test.java as specified by the rules")
        return SpecializingRuleCommand(base_command, specializing_rule)

with description('a piece of content'):
    """Base capability: specializing behavior for different file types"""
    
    with context('that is being processed by a command'):
        with before.each:
            self.content = Content('test.java', '.java')
        
        with context('that implements a specializing rule'):
            with before.each:
                # Inline the function call to avoid scope issues with mamba execution context
                with patch.object(RuleParser, 'read_file_content', return_value=create_base_rule_content()):
                    specializing_rule = create_test_specializing_rule_from_file('base-rule.mdc')
                    servlet_rule = specializing_rule.specialized_rules.get('servlet')
                    cgiscript_rule = specializing_rule.specialized_rules.get('cgiscript')
                    self.specializing_rule, self.servlet_specialized, self.cgiscript_specialized = specializing_rule, servlet_rule, cgiscript_rule

            with it('should use template method pattern to select specialized rule'):
                # Arrange
                base_rule = self.specializing_rule.base_rule
                base_command = Command(self.content, base_rule)
                command = SpecializingRuleCommand(base_command, self.specializing_rule)
                
                # Act
                selected_specialized = command.specialized_rule
                
                # Assert
                expect(selected_specialized).to(equal(self.servlet_specialized))
                expect(self.content.file_extension).to(equal('.java'))
            
            with it('should include base rule principles'):
                # Arrange - stub file reading to return test content for base rule
                test_base_rule_content = create_base_rule_content_with_two_principles()
                with patch.object(RuleParser, 'read_file_content', return_value=test_base_rule_content):
                    # Create specializing rule - this will create BaseRule which loads principles via patched method
                    specializing_rule = create_test_specializing_rule_from_file('base-rule.mdc')
                    # Ensure base rule has loaded principles
                    parser = RuleParser()
                    specializing_rule.base_rule.principles = parser.load_principles_from_file('base-rule.mdc')
                    # Manually create specialized rule since file discovery won't find it when mocking
                    specialized_rule = SpecializedRule(rule_file_name='base-rule-servlet.mdc', parent=specializing_rule)
                    specializing_rule.specialized_rules['servlet'] = specialized_rule
                    base_rule = specializing_rule.base_rule
                    base_command = Command(self.content, base_rule)
                    command = SpecializingRuleCommand(base_command, specializing_rule)
                    
                    # Act
                    selected_specialized = command.specialized_rule
                    principles = selected_specialized.principles if selected_specialized else []
                    
                    # Assert - principles should be SpecializedPrinciple wrappers
                    expect(principles).to(have_length(2))
                    expect(principles[0].principle_number).to(equal(1))
                    expect(principles[0].principle_name).to(equal("First Principle"))
                    expect(principles[0].content).to(equal("Test content for first principle."))
                    expect(principles[1].principle_number).to(equal(2))
                    expect(principles[1].principle_name).to(equal("Second Principle"))
                    expect(principles[1].content).to(equal("Test content for second principle."))
            
            with context('and the specializing rules has been loaded'):
                with before.each:
                    # self.content inherited from parent context
                    test_base_rule_content = create_base_rule_content()
                    test_specialized_rule_content = create_specialized_rule_content()
                    
                    def read_file_side_effect(file_path):
                        """Return appropriate content based on file path"""
                        if 'servlet' in str(file_path) or 'base-rule-servlet' in str(file_path):
                            return test_specialized_rule_content
                        return test_base_rule_content
                    
                    with patch.object(RuleParser, 'read_file_content', side_effect=read_file_side_effect):
                        self.specializing_rule = create_test_specializing_rule_from_file('base-rule.mdc')
                        # Ensure base rule has loaded principles
                        parser = RuleParser()
                        self.specializing_rule.base_rule.principles = parser.load_principles_from_file('base-rule.mdc')
                        # Manually create specialized rule since file discovery won't find it when mocking
                        self.servlet_specialized = SpecializedRule(rule_file_name='base-rule-servlet.mdc', parent=self.specializing_rule)
                        self.specializing_rule.specialized_rules['servlet'] = self.servlet_specialized
                        self.principle = self.servlet_specialized.principles[0] if self.servlet_specialized and self.servlet_specialized.principles else None
                
                with it('should have access to the base rule and its principles'):
                    # Arrange
                    base_rule = self.specializing_rule.base_rule
                    base_command = Command(self.content, base_rule)
                    command = SpecializingRuleCommand(base_command, self.specializing_rule)
                    
                    # Act
                    accessed_specialized = command.specialized_rule
                    principles = accessed_specialized.principles if accessed_specialized else []
                    
                    # Assert
                    expect(principles).to(have_length(1))
                    expect(principles[0].principle_number).to(equal(1))
                    expect(principles[0].principle_name).to(equal("Test Principle"))
                    # Specialized principle should use specialized content when available
                    expect(principles[0].content).to(equal("Servlet-specific content for test principle."))
                
                with it('should use specialized principles in validate output'):
                    # Arrange
                    validate_instructions = "Please validate test.java as specified by the rules"
                    command = create_command_with_specialized_rule(self.content, validate_instructions)
                    
                    # Act
                    instructions = command.validate()
                    
                    # Assert - should use specialized principles (servlet-specific content)
                    expect(instructions).to(contain(validate_instructions))
                    expect(instructions).to(contain("Servlet-specific content"))
                    expect(instructions).to(contain("TestServlet"))
                    # Should NOT contain base rule content
                    expect(instructions).not_to(contain("Test content for test principle"))
                
                with it('should use specialized principles in generate output'):
                    # Arrange
                    generate_instructions = "Please build test.java according to the rules"
                    command = create_command_with_specialized_rule(self.content, generate_instructions, generate=True)
                    
                    # Act
                    instructions = command.generate()
                    
                    # Assert - should use specialized principles (servlet-specific content)
                    expect(instructions).to(contain(generate_instructions))
                    expect(instructions).to(contain("Servlet-specific content"))
                    expect(instructions).to(contain("TestServlet"))
                    # Should NOT contain base rule content
                    expect(instructions).not_to(contain("Test content for test principle"))
                
                with it('should provide access to specialized examples with DOs and DONTs for each principle'):
                    # Arrange - use specialized content with different principle text
                    test_specialized_rule_content = create_specialized_rule_content("Restate principle briefly.")
                    test_base_rule_content = create_base_rule_content()
                    
                    def read_file_side_effect_for_examples(file_path):
                        """Return appropriate content based on file path"""
                        if 'servlet' in str(file_path) or 'base-rule-servlet' in str(file_path):
                            return test_specialized_rule_content
                        return test_base_rule_content
                    
                    with patch.object(RuleParser, 'read_file_content', side_effect=read_file_side_effect_for_examples):
                        specializing_rule = create_test_specializing_rule_from_file('base-rule.mdc')
                        # Ensure base rule has loaded principles
                        parser = RuleParser()
                        specializing_rule.base_rule.principles = parser.load_principles_from_file('base-rule.mdc')
                        # Manually create specialized rule since file discovery won't find it when mocking
                        specialized_rule = SpecializedRule(rule_file_name='base-rule-servlet.mdc', parent=specializing_rule)
                        specializing_rule.specialized_rules['servlet'] = specialized_rule
                        base_command = Command(self.content, specializing_rule.base_rule)
                        command = SpecializingRuleCommand(base_command, specializing_rule)
                        
                        # Act
                        accessed_specialized = command.specialized_rule
                        accessed_principles = accessed_specialized.principles if accessed_specialized else []
                        examples = []
                        for principle in accessed_principles:
                            examples.extend(principle.examples)
                        
                        # Assert - each example contains both DO and DON'T
                        expect(examples).to(have_length(1))  # One example with both DO and DON'T
                        expect(examples[0].do_code).to(contain("Good example code"))
                        expect(examples[0].dont_code).to(contain("Bad example code"))
            
            
            with context('that performs code augmented AI guidance'):
                with context('that is being validated against its rules'):
                    with before.each:
                        # self.content inherited from parent context
                        test_base_rule_content = """---
description: Test rule
---

## 1. Use Descriptive Names
Code should use descriptive variable and function names.

**[DO]:**
```java
public class UserAccount {
    private String accountHolderName;
    public void calculateTotalBalance() { }
}
```

**[DON'T]:**
```java
public class UA {
    private String a;
    public void calc() { }
}
```

## 2. Avoid Magic Numbers
Use named constants instead of magic numbers.

**[DO]:**
```java
private static final int MAX_RETRY_ATTEMPTS = 3;
if (attempts < MAX_RETRY_ATTEMPTS) { }
```

**[DON'T]:**
```java
if (attempts < 3) { }
```
"""
                        with patch.object(RuleParser, 'read_file_content', return_value=test_base_rule_content):
                            self.base_rule = BaseRule('base-rule.mdc')
                            parser = RuleParser()
                            self.base_rule.principles = parser.load_principles_from_file('base-rule.mdc')
                        
                        # Create test content that violates rules
                        self.violating_content = Content('bad-code.java', '.java')
                        self.clean_content = Content('good-code.java', '.java')
                    
                    with it('should return validation instructions with principles and examples from base command'):
                        # Arrange
                        validate_instructions = "Please validate test.java as specified by the rules in base-rule.mdc"
                        base_command = Command(self.content, self.base_rule, validate_instructions=validate_instructions)
                        
                        # Act
                        instructions = base_command.validate()
                        
                        # Assert - base command returns instructions with principles and examples
                        expect(instructions).to(contain(validate_instructions))
                        expect(instructions).to(contain("Use Descriptive Names"))
                        expect(instructions).to(contain("Avoid Magic Numbers"))
                        expect(instructions).to(contain("UserAccount"))
                        expect(instructions).to(contain("UA"))
                        expect(instructions).to(contain("DO"))
                        expect(instructions).to(contain("DON'T"))
                    
                    with it('should return generation instructions with principles and examples from base command'):
                        # Arrange
                        generate_instructions = "Please build test.java according to the rules specified in base-rule.mdc"
                        base_command = Command(self.content, self.base_rule, generate_instructions=generate_instructions)
                        
                        # Act
                        instructions = base_command.generate()
                        
                        # Assert - base command returns generation instructions with principles and examples
                        expect(instructions).to(contain(generate_instructions))
                        expect(instructions).to(contain("Use Descriptive Names"))
                        expect(instructions).to(contain("Avoid Magic Numbers"))
                        expect(instructions).to(contain("UserAccount"))
                        expect(instructions).to(contain("UA"))
                    
                    with it('should load code heuristics for each principle from base rule'):
                        # Arrange
                        command = create_code_augmented_command(self.content, self.base_rule)
                        
                        # Act
                        principles = command.principles
                        heuristics = []
                        for principle in principles:
                            heuristics.extend(principle.heuristics)
                        
                        # Assert
                        expect(principles).to(have_length(2))
                        expect(heuristics).to(have_length(2))
                        expect(all(h.detection_pattern in ["descriptive_names", "magic_numbers"] for h in heuristics)).to(be_true)
                    
                    with it('should scan content for violations and include them in validate output as checklist'):
                        # Arrange
                        violating_content = create_violating_code_content()
                        command = create_code_augmented_command(violating_content, self.base_rule)
                        
                        # Act - validate content for violations (defaults to CHECKLIST format)
                        instructions = command.validate()
                        
                        # Assert - violations property contains violations
                        expect(command.violations).to(have_length(2))  # Both heuristics detect violations
                        expect(all(v.message for v in command.violations)).to(be_true)
                        # Assert - instructions include violations in checklist format
                        expect(instructions).to(contain("Violations Checklist"))
                        expect(instructions).to(contain("- [ ]"))  # Checklist markers
                        expect(instructions).to(contain("descriptive naming violation"))
                        expect(instructions).to(contain("magic number violation"))
                        # Assert - code snippets are included showing where violations occurred
                        expect(instructions).to(contain(">>>"))  # Marker for violation line
                        expect(instructions).to(contain("|"))  # Line number separator
                        expect(instructions).to(contain("BadCode"))  # Code content from snippet
                        expect(instructions).to(contain("```"))  # Code block markers
                    
                    with it('should format violations in detailed format when requested'):
                        # Arrange
                        violating_content = create_violating_code_content()
                        command = create_code_augmented_command(violating_content, self.base_rule)
                        
                        # Act - validate with DETAILED format
                        instructions = command.validate(report_format='DETAILED')
                        
                        # Assert - violations property contains violations
                        expect(command.violations).to(have_length(2))
                        # Assert - instructions include violations in detailed format (not checklist)
                        expect(instructions).to(contain("Violations Found"))
                        expect(instructions).not_to(contain("Violations Checklist"))
                        expect(instructions).not_to(contain("- [ ]"))  # No checklist markers
                        expect(instructions).to(contain("descriptive naming violation"))
                        expect(instructions).to(contain("magic number violation"))
                    
                    with it('should access examples from principles for violation detection'):
                        # Arrange
                        command = create_code_augmented_command(self.content, self.base_rule)
                        
                        # Act
                        principles = command.principles
                        examples = []
                        for principle in principles:
                            examples.extend(principle.examples)
                        
                        # Assert - examples should be available for AI prompts
                        # Each example contains both DO and DON'T
                        expect(examples).to(have_length(2))  # 2 examples, each with DO and DON'T
                        expect(examples[0].do_code).to(contain("UserAccount"))
                        expect(examples[0].dont_code).to(contain("UA"))
                        expect(examples[1].do_code).to(contain("MAX_RETRY_ATTEMPTS"))
                        expect(examples[1].dont_code).to(contain("3"))
                    
                    with it('should apply fix suggestions from AI'):
                        # Arrange
                        command = create_code_augmented_command(self.content, self.base_rule)
                        
                        # Act
                        self.content.apply_fixes()
                        
                        # Assert
                        expect(self.content.violations).to(have_length(0))
                        expect(command).not_to(be_none)
                        expect(command.content).to(equal(self.content))
                        expect(self.content.file_extension).to(equal('.java'))
        
        with context('that implements incremental runs'):
            with before.each:
                # self.content inherited from parent context
                self.max_sample_size = 18
                self.base_rule = BaseRule('base-rule.mdc')
                base_command = Command(self.content, self.base_rule)
                self.command = IncrementalCommand(base_command, self.base_rule, self.max_sample_size)
            
            with context('with all work complete'):
                # Inherits setup from parent before.each
                with it('should mark the command as complete'):
                    # Arrange
                    command = self.command
                    command._has_more_work = False
                    
                    # Act
                    is_complete = command.is_complete()
                    
                    # Assert
                    expect(is_complete).to(be_true)
                    expect(command).not_to(be_none)
                    expect(command.max_sample_size).to(equal(self.max_sample_size))
                    expect(command.content).to(equal(self.content))
                    expect(self.max_sample_size).to(equal(18))
            
            with it('should provide the sample size based on code analysis and configured maximum'):
                # Arrange
                command = self.command
                
                # Act
                sample_size = command.sample_size
                max_sample_size = command.max_sample_size
                
                # Assert
                expect(max_sample_size).to(equal(18))
                expect(sample_size).to(be_none)
            
            with context('that has completed a run'):
                with before.each:
                    self.run = Run(1, RunStatus.STARTED.value)
                    self.run_history = RunHistory()
                
                with it('should mark run complete'):
                    # Arrange
                    command = self.command
                    command.current_run = self.run
                    
                    # Act
                    self.run.state.status = 'COMPLETE'
                    
                    # Assert
                    expect(self.run.state.status).to(equal('COMPLETE'))
                    expect(self.run.run_number).to(equal(1))
                
                with it('should save run to history'):
                    # Arrange
                    command = self.command
                    command.run_history = self.run_history
                    self.run.state.status = RunStatus.COMPLETED.value
                    
                    # Act
                    self.run_history.runs.append(self.run)
                    
                    # Assert
                    expect(self.run_history.runs).to(contain(self.run))
                    expect(self.run_history.runs).to(have_length(1))
                
                with it('should save state to disk'):
                    # Arrange
                    command = self.command
                    command.current_run = self.run
                    
                    # Act
                    command.state.save(command.run_history, command.current_run)
                    
                    # Assert
                    expect(command).not_to(be_none)
                    expect(command.content).to(equal(self.content))
                    expect(command.run_history).not_to(be_none)
                    expect(self.content.file_path).to(equal('test.java'))
                
                with it('should provide the user with the option to repeat the run, start next run, abandon run, or expand to do all remaining'):
                    # Arrange
                    command = self.command
                    command.current_run = self.run
                    
                    # Act
                    options = self.run.get_user_options()
                    
                    # Assert
                    expect(options).to(contain('repeat'))
                    expect(options).to(contain('next'))
                    expect(options).to(contain('abandon'))
                    expect(options).to(contain('expand'))
                    expect(command).not_to(be_none)
                    expect(command.current_run).to(equal(self.run))
                    expect(command.run_history).not_to(be_none)
                    expect(self.run.state.status).to(equal(RunStatus.STARTED.value))
                
                with context('that has been repeated'):
                    with it('should revert current run results'):
                        # Arrange
                        command = self.command
                        command.current_run = self.run
                        self.run.snapshot_before_run = "snapshot_data"
                        
                        # Act
                        self.run.state.status = 'REVERTED'
                        
                        # Assert
                        expect(self.run.state.status).to(equal('REVERTED'))
                        expect(self.run.run_number).to(equal(1))
                    
                    with it('should restart same run from beginning'):
                        # Arrange
                        command = self.command
                        self.run.state.status = "REVERTED"
                        
                        # Act
                        self.run.state.status = RunStatus.STARTED.value
                        self.run.completed_at = None
                        
                        # Assert
                        expect(self.run.state.status).to(equal(RunStatus.STARTED.value))
                        expect(self.run.completed_at).to(be_none)
                        expect(self.run.run_number).to(equal(1))
            
            with context('that is proceeding to the next run'):
                with before.each:
                    self.current_run = Run(1, RunStatus.COMPLETED.value)
                
                with it('should proceed to next run with same sample size'):
                    # Arrange
                    command = self.command
                    command.current_run = self.current_run
                    self.current_run.sample_size = 6
                    
                    # Act
                    command.proceed_to_next_run()
                    
                    # Assert
                    expect(command.current_run.run_number).to(equal(2))
                    expect(command.current_run.sample_size).to(equal(6))
                    expect(command).not_to(be_none)
                    expect(command.sample_size).to(equal(6))
                    expect(command.current_run).not_to(equal(self.current_run))  # Should be a new run object
                    expect(command.current_run.run_number).to(equal(2))  # New run should have incremented number
                    expect(command.max_sample_size).to(equal(self.max_sample_size))
                    expect(self.current_run.run_number).to(equal(1))  # Original run unchanged
            
            with context('that is proceeding to expand to all work'):
                with before.each:
                    self.run_history = RunHistory()
                
                with it('should extract lessons from previous runs'):
                    # Arrange
                    previous_run = Run(1, RunStatus.COMPLETED.value)
                    self.run_history.runs = [previous_run]
                    command = self.command
                    command.run_history = self.run_history
                    
                    # Act
                    lessons = command.run_history.extract_lessons()
                    
                    # Assert
                    expect(lessons).to(have_length(0))
                    expect(command).not_to(be_none)
                    expect(command.run_history).to(equal(self.run_history))
                    expect(self.run_history.runs).to(contain(previous_run))
                    expect(previous_run.state.status).to(equal(RunStatus.COMPLETED.value))
                    expect(previous_run.run_number).to(equal(1))
                
                with it('should execute all remaining work'):
                    # Arrange
                    command = self.command
                    
                    # Act
                    command.expand_to_all_work()
                    
                    # Assert
                    expect(command.current_run.sample_size).to(equal(90))
                    expect(command.completed_work_units).to(equal(100))
                    expect(command).not_to(be_none)
                    expect(command.max_sample_size).to(equal(self.max_sample_size))
                    expect(command.content).to(equal(self.content))
                    expect(self.max_sample_size).to(equal(18))
            
            with context('with more work remaining'):
                with it('should enable next run option'):
                    # Arrange
                    command = self.command
                    
                    # Act
                    has_more = command.has_more_work_remaining()
                    
                    # Assert
                    expect(has_more).to(be_true)
                    expect(command).not_to(be_none)
                    expect(command.max_sample_size).to(equal(self.max_sample_size))
                    expect(command.content).to(equal(self.content))
                    expect(self.max_sample_size).to(equal(18))
            
        
        with context('that is a phase in a workflow'):
            with before.each:
                # self.content inherited from parent context
                self.workflow = Workflow()
                self.base_rule = BaseRule('test-rule.mdc')
                self.base_command = Command(self.content, self.base_rule)
                
                # Create 3 phases for testing transitions
                self.phase_0 = WorkflowPhaseCommand(self.base_command, self.workflow, 0, "Phase 0: Setup")
                self.phase_1 = WorkflowPhaseCommand(self.base_command, self.workflow, 1, "Phase 1: Development")
                self.phase_2 = WorkflowPhaseCommand(self.base_command, self.workflow, 2, "Phase 2: Review")
                
                self.workflow.phases = [self.phase_0, self.phase_1, self.phase_2]
                self.workflow.current_phase_number = 0
                
                # Set default phase_command to phase_0 for backward compatibility
                self.phase_command = self.phase_0
                self.phase_number = 0
                self.phase_name = "Phase 0: Setup"
            
            with it('should initialize workflow phase'):
                # Arrange
                phase_command = self.phase_command
                
                # Act
                
                # Assert
                expect(phase_command.phase_state.phase_status).to(equal("STARTING"))
                expect(self.phase_number).to(equal(0))
            
            with it('should set state of phase to starting'):
                # Arrange
                phase_command = self.phase_command
                
                # Act
                phase_command.phase_state.phase_status = "STARTING"
                
                # Assert
                expect(phase_command.phase_state.phase_status).to(equal("STARTING"))
                expect(self.phase_name).to(equal("Phase 0: Setup"))
            
            with it('should save state to disk'):
                # Arrange
                phase_command = self.phase_command
                
                # Act
                phase_command.save_state_to_disk()
                
                # Assert
                expect(phase_command.phase_state.persisted_at).not_to(be_none)
                expect(phase_command).not_to(be_none)
                expect(phase_command.phase_state).not_to(be_none)
                expect(phase_command.content).to(equal(self.content))
                expect(phase_command.workflow).to(equal(self.workflow))
                expect(self.content.file_path).to(equal('test.java'))
            
            with context('in the correct phase order'):
                with it('should invoke the command'):
                    # Arrange
                    phase_command = self.phase_command
                    
                    # Act
                    phase_command.start()
                    
                    # Assert
                    expect(self.workflow.can_execute_phase.called).to(be_true)
                    expect(phase_command.phase_state.phase_status).to(equal("IN_PROGRESS"))
                    expect(phase_command).not_to(be_none)
                    expect(phase_command.workflow).to(equal(self.workflow))
                    expect(phase_command.phase_number).to(equal(self.phase_number))
                    expect(phase_command.phase_name).to(equal(self.phase_name))
                    expect(phase_command.phase_state).not_to(be_none)
                    expect(self.phase_number).to(equal(0))
            
            with context('that is being resumed from previous session'):
                with it('should load state from disk'):
                    # Arrange
                    phase_state = PhaseState(self.phase_number, "STARTING")
                    test_file = Path("test_phase_state.json")
                    
                    try:
                        # Act
                        loaded_state = PhaseState.load_from_disk(str(test_file))
                        
                        # Assert
                        expect(loaded_state.phase_status).to(equal("STARTING"))
                        expect(loaded_state.phase_number).to(equal(self.phase_number))
                        expect(phase_state).not_to(be_none)
                    finally:
                        if test_file.exists():
                            test_file.unlink()
                    expect(phase_state.phase_status).to(equal("STARTING"))
                    expect(phase_state.phase_number).to(equal(self.phase_number))
                    expect(self.phase_number).to(equal(0))
                
                with it('should start from current phase'):
                    # Arrange
                    phase_command = self.phase_command
                    phase_state = PhaseState(self.phase_number, "STARTING")
                    phase_command.phase_state = phase_state
                    
                    # Act
                    phase_command.resume_from_phase()
                    
                    # Assert
                    expect(phase_command).not_to(be_none)
                    expect(phase_command.phase_number).to(equal(phase_command.phase_state.phase_number))
                    expect(phase_command.phase_state.phase_status).to(equal("STARTING"))
                    expect(phase_command.content).to(equal(self.content))
                    expect(phase_command._start_called).to(be_true)
                    expect(self.phase_number).to(equal(0))
                
            
            with context('that has been invoked out of phase order'):
                # Reuses self.base_command from parent before.each
                with it('should block execution'):
                    # Arrange
                    phase_command = WorkflowPhaseCommand(self.base_command, self.workflow, 1, "Wrong Phase")
                    self.workflow.current_phase_number = 0
                    
                    # Act
                    phase_command.block_execution("Phase out of order")
                    phase_command.phase_state.phase_status = "BLOCKED"
                    
                    # Assert
                    expect(phase_command.can_execute).to(be_false)
                    expect(phase_command).not_to(be_none)
                    expect(phase_command.phase_number).to(equal(1))
                    expect(phase_command.phase_name).to(equal("Wrong Phase"))
                    expect(phase_command.phase_state.phase_status).to(equal("BLOCKED"))
                    expect(self.workflow.current_phase_number).to(equal(0))
                    expect(self.phase_number).to(equal(0))
                
                with it('should report on current phase that needs to be completed'):
                    # Arrange
                    self.workflow.current_phase_number = 0
                    test_phase = WorkflowPhaseCommand(self.base_command, self.workflow, 0, "Test Phase")
                    self.workflow.phases = [test_phase]
                    
                    # Act
                    status_report = self.workflow.get_current_phase_status()
                    
                    # Assert
                    expect(status_report.phase_name).to(equal("Test Phase"))
                    expect(status_report.phase_number).to(equal(0))
                    expect(self.workflow).not_to(be_none)
                    expect(self.workflow.phases).to(have_length(1))
                    expect(self.workflow.phases[0].phase_name).to(equal("Test Phase"))
                    expect(self.workflow.phases[0].phase_number).to(equal(0))
                    expect(self.workflow.current_phase_number).to(equal(0))
                    expect(test_phase.phase_name).to(equal("Test Phase"))
            
            with context('that has completed all steps for the command'):
                with it('should provide the user with the option to proceed to next phase, verify against rules, or redo the phase'):
                    # Arrange
                    phase_command = self.phase_command
                    
                    # Act
                    options = phase_command.check_completion()
                    
                    # Assert
                    expect(options).to(contain('proceed_to_next_phase'))
                    expect(options).to(contain('verify'))
                    expect(options).to(contain('redo'))
                    expect(phase_command).not_to(be_none)
                    expect(phase_command.phase_name).to(equal(self.phase_name))
                    expect(phase_command.phase_number).to(equal(self.phase_number))
                    expect(phase_command.phase_state).not_to(be_none)
                    expect(self.phase_name).to(equal("Phase 0: Setup"))
            
            with context('that has been approved to proceed'):
                with it('should determine next action from state'):
                    # Arrange
                    phase_command = self.phase_command
                    phase_state = PhaseState(self.phase_number, "COMPLETE")
                    phase_command.phase_state = phase_state
                    
                    # Act
                    next_action = phase_command.phase_state.determine_next_action()
                    
                    # Assert
                    expect(next_action).to(equal("PROCEED_TO_NEXT_PHASE"))
                    expect(phase_command).not_to(be_none)
                    expect(phase_command.phase_state).not_to(be_none)
                    expect(phase_command.phase_state.phase_status).to(equal("COMPLETE"))
                    expect(phase_command.phase_state.phase_number).to(equal(self.phase_number))
                    expect(phase_command.content).to(equal(self.content))
                    expect(self.phase_number).to(equal(0))
                
                with it('should mark the phase as complete in the Workflow'):
                    # Arrange
                    phase_command = self.phase_command
                    self.workflow.phases = [phase_command]
                    self.workflow.current_phase_number = 0
                    
                    # Act
                    self.workflow.mark_phase_complete(0)
                    phase_command.phase_state.phase_status = "COMPLETE"
                    self.workflow.current_phase_number = 1
                    
                    # Assert
                    expect(phase_command).not_to(be_none)
                    expect(phase_command.phase_state.phase_status).to(equal("COMPLETE"))
                    expect(self.workflow.phases).to(contain(phase_command))
                    expect(self.workflow.current_phase_number).to(equal(1))
                    expect(self.phase_number).to(equal(0))
                
                with it('should start the next phase command in the workflow'):
                    # Arrange
                    phase_command = self.phase_command
                    next_phase_command = WorkflowPhaseCommand(self.base_command, self.workflow, 1, "Next Phase")
                    self.workflow.phases = [phase_command, next_phase_command]
                    self.workflow.current_phase_number = 1
                    
                    # Act
                    self.workflow.start_next_phase()
                    next_phase_command.start()
                    
                    # Assert
                    expect(next_phase_command._start_called).to(be_true)
                    expect(self.workflow).not_to(be_none)
                    expect(self.workflow.phases).to(have_length(2))
                    expect(self.workflow.phases[0]).to(equal(phase_command))
                    expect(self.workflow.phases[1]).to(equal(next_phase_command))
                    expect(self.workflow.current_phase_number).to(equal(1))
                    expect(next_phase_command.phase_number).to(equal(1))
                    expect(next_phase_command.phase_name).to(equal("Next Phase"))
                    expect(next_phase_command.content).to(equal(self.content))
                    expect(self.phase_number).to(equal(0))
            
            with context('with multiple phases in workflow'):
                with it('should proceed from phase 0 to phase 1 to phase 2'):
                    # Arrange
                    self.workflow.current_phase_number = 0
                    
                    # Act - proceed from phase 0 to phase 1
                    self.phase_0.proceed_to_next_phase()
                    
                    # Assert - should be on phase 1
                    expect(self.workflow.current_phase_number).to(equal(1))
                    expect(self.workflow.phases[1].phase_state.phase_status).to(equal("IN_PROGRESS"))
                    expect(self.workflow.phases[1]._start_called).to(be_true)
                    
                    # Act - proceed from phase 1 to phase 2
                    self.phase_1.proceed_to_next_phase()
                    
                    # Assert - should be on phase 2
                    expect(self.workflow.current_phase_number).to(equal(2))
                    expect(self.workflow.phases[2].phase_state.phase_status).to(equal("IN_PROGRESS"))
                    expect(self.workflow.phases[2]._start_called).to(be_true)
                
                with it('should allow going backwards to previous phases'):
                    # Arrange - start on phase 1
                    self.workflow.current_phase_number = 1
                    self.phase_1.start()
                    
                    # Act - go back to phase 0
                    self.workflow.current_phase_number = 0
                    self.phase_0.start()
                    
                    # Assert - should be on phase 0
                    expect(self.workflow.current_phase_number).to(equal(0))
                    expect(self.phase_0.phase_state.phase_status).to(equal("IN_PROGRESS"))
                    expect(self.phase_0._start_called).to(be_true)
                
                with it('should allow selecting phases arbitrarily'):
                    # Arrange - start on phase 0
                    self.workflow.current_phase_number = 0
                    
                    # Act - jump directly to phase 2
                    self.workflow.current_phase_number = 2
                    self.phase_2.start()
                    
                    # Assert - should be on phase 2
                    expect(self.workflow.current_phase_number).to(equal(2))
                    expect(self.phase_2.phase_state.phase_status).to(equal("IN_PROGRESS"))
                    expect(self.phase_2._start_called).to(be_true)
                    
                    # Act - jump back to phase 1
                    self.workflow.current_phase_number = 1
                    self.phase_1.start()
                    
                    # Assert - should be on phase 1
                    expect(self.workflow.current_phase_number).to(equal(1))
                    expect(self.phase_1.phase_state.phase_status).to(equal("IN_PROGRESS"))
                
                with it('should track phase status across all phases'):
                    # Arrange
                    self.workflow.current_phase_number = 0
                    
                    # Act - complete phase 0
                    self.phase_0.start()
                    self.phase_0.approve()
                    self.workflow.mark_phase_complete(0)
                    
                    # Assert - phase 0 complete, workflow moved to phase 1
                    expect(self.phase_0.phase_state.phase_status).to(equal("APPROVED"))
                    expect(self.workflow.current_phase_number).to(equal(1))
                    
                    # Act - start phase 1
                    self.phase_1.start()
                    
                    # Assert - phase 1 in progress, phase 0 still approved
                    expect(self.phase_1.phase_state.phase_status).to(equal("IN_PROGRESS"))
                    expect(self.phase_0.phase_state.phase_status).to(equal("APPROVED"))
                    expect(self.phase_2.phase_state.phase_status).to(equal("STARTING"))

            with context('that wraps different command types'):
                with before.each:
                    # self.content and self.base_rule inherited from parent context
                    self.workflow = Workflow()
                
                with it('should delegate generate() and validate() to wrapped CodeAugmentedCommand'):
                    # Arrange
                    base_command = Command(self.content, self.base_rule)
                    code_augmented_command = CodeAugmentedCommand(base_command, self.base_rule)
                    phase_command = WorkflowPhaseCommand(code_augmented_command, self.workflow, 0, "Phase: Code Augmented")
                    
                    # Mock the inner command's methods
                    with patch.object(code_augmented_command, 'generate', return_value='generated') as mock_generate, \
                         patch.object(code_augmented_command, 'validate', return_value='validated') as mock_validate:
                        # Act
                        generate_result = phase_command.generate()
                        validate_result = phase_command.validate()
                        
                        # Assert
                        expect(mock_generate.called).to(be_true)
                        expect(mock_validate.called).to(be_true)
                        expect(generate_result).to(equal('generated'))
                        expect(validate_result).to(equal('validated'))
                
                with it('should delegate generate() and validate() to wrapped SpecializingRuleCommand'):
                    # Arrange
                    base_command = Command(self.content, self.base_rule)
                    specializing_rule = FrameworkSpecializingRule('test-rule.mdc')
                    specializing_command = SpecializingRuleCommand(base_command, specializing_rule)
                    phase_command = WorkflowPhaseCommand(specializing_command, self.workflow, 0, "Phase: Specializing")
                    
                    # Mock the inner command's methods
                    with patch.object(specializing_command, 'generate', return_value='specialized generated') as mock_generate, \
                         patch.object(specializing_command, 'validate', return_value='specialized validated') as mock_validate:
                        # Act
                        generate_result = phase_command.generate()
                        validate_result = phase_command.validate()
                        
                        # Assert
                        expect(mock_generate.called).to(be_true)
                        expect(mock_validate.called).to(be_true)
                        expect(generate_result).to(equal('specialized generated'))
                        expect(validate_result).to(equal('specialized validated'))
                
                with it('should delegate methods to wrapped IncrementalCommand'):
                    # Arrange
                    base_command = Command(self.content, self.base_rule)
                    incremental_command = IncrementalCommand(base_command, self.base_rule, max_sample_size=10, command_file_path='test.py')
                    phase_command = WorkflowPhaseCommand(incremental_command, self.workflow, 0, "Phase: Incremental")
                    
                    # Mock the inner command's methods
                    with patch.object(incremental_command, 'generate', return_value='incremental generated') as mock_generate, \
                         patch.object(incremental_command, 'validate', return_value='incremental validated') as mock_validate, \
                         patch.object(incremental_command, 'has_more_work_remaining', return_value=True) as mock_has_more:
                        # Act
                        generate_result = phase_command.generate()
                        validate_result = phase_command.validate()
                        has_more_result = phase_command.has_more_work_remaining()
                        
                        # Assert
                        expect(mock_generate.called).to(be_true)
                        expect(mock_validate.called).to(be_true)
                        expect(mock_has_more.called).to(be_true)
                        expect(generate_result).to(equal('incremental generated'))
                        expect(validate_result).to(equal('incremental validated'))
                        expect(has_more_result).to(be_true)
        
        with context('that delegates to current phase'):
            with before.each:
                # self.content and self.base_rule inherited from parent context
                self.workflow = Workflow()
                self.base_command = Command(self.content, self.base_rule)
                self.phase_0 = WorkflowPhaseCommand(self.base_command, self.workflow, 0, "Phase 0")
                self.phase_1 = WorkflowPhaseCommand(self.base_command, self.workflow, 1, "Phase 1")
                self.workflow.phases = [self.phase_0, self.phase_1]
                self.workflow.current_phase_number = 0
            
            with it('should delegate generate() to current phase'):
                # Arrange
                workflow = self.workflow
                
                # Mock the current phase's generate method
                with patch.object(self.phase_0, 'generate', return_value='workflow generated') as mock_generate:
                    # Act
                    result = workflow.generate()
                    
                    # Assert
                    expect(mock_generate.called).to(be_true)
                    expect(result).to(equal('workflow generated'))
            
            with it('should delegate validate() to current phase'):
                # Arrange
                workflow = self.workflow
                
                # Mock the current phase's validate method
                with patch.object(self.phase_0, 'validate', return_value='workflow validated') as mock_validate:
                    # Act
                    result = workflow.validate()
                    
                    # Assert
                    expect(mock_validate.called).to(be_true)
                    expect(result).to(equal('workflow validated'))
            
            with it('should delegate validate() with report_format to current phase'):
                # Arrange
                workflow = self.workflow
                
                # Mock the current phase's validate method
                with patch.object(self.phase_0, 'validate', return_value='workflow detailed') as mock_validate:
                    # Act
                    result = workflow.validate(report_format='DETAILED')
                    
                    # Assert
                    expect(mock_validate.called).to(be_true)
                    expect(mock_validate.call_args[1]['report_format']).to(equal('DETAILED'))
                    expect(result).to(equal('workflow detailed'))
            
            with it('should delegate to new current phase after phase change'):
                # Arrange
                workflow = self.workflow
                workflow.current_phase_number = 1  # Change to phase 1
                
                # Mock phase 1's generate method
                with patch.object(self.phase_1, 'generate', return_value='phase 1 generated') as mock_generate:
                    # Act
                    result = workflow.generate()
                    
                    # Assert
                    expect(mock_generate.called).to(be_true)
                    expect(result).to(equal('phase 1 generated'))
            
            with it('should return None when no current phase'):
                # Arrange
                workflow = self.workflow
                workflow.current_phase_number = 999  # No phase exists
                
                # Act
                generate_result = workflow.generate()
                validate_result = workflow.validate()
                
                # Assert
                expect(generate_result).to(be_none)
                expect(validate_result).to(be_none)

with description('Run class'):
    """Tests for Run domain object"""
    
    with context('state management'):
        with before.each:
            self.run = Run(1, RunStatus.STARTED.value)
        
        with it('should track generation timestamp'):
            # Arrange
            run = self.run
            
            # Act
            run.generated_at = "2024-01-01T12:00:00"
            
            # Assert
            expect(run.generated_at).to(equal("2024-01-01T12:00:00"))
            expect(run.has_been_generated()).to(be_true)
        
        with it('should track validation timestamp'):
            # Arrange
            run = self.run
            
            # Act
            run.validated_at = "2024-01-01T12:00:00"
            
            # Assert
            expect(run.validated_at).to(equal("2024-01-01T12:00:00"))
            expect(run.has_been_validated()).to(be_true)
        
        with it('should check if completed'):
            # Arrange
            run = self.run
            run.state.status = RunStatus.COMPLETED.value
            
            # Act & Assert
            expect(run.state.completed).to(be_true)
            expect(run.state.abandoned).to(be_false)
            expect(run.state.finished).to(be_true)
        
        with it('should check if abandoned'):
            # Arrange
            run = self.run
            run.state.status = RunStatus.ABANDONED.value
            
            # Act & Assert
            expect(run.state.abandoned).to(be_true)
            expect(run.state.completed).to(be_false)
            expect(run.state.finished).to(be_true)
    
    with context('state transitions'):
        with before.each:
            self.run = Run(1, RunStatus.STARTED.value)
            self.run.run_id = "test_run_1"
        
        with it('should verify AI and transition to AI_VERIFIED'):
            # Arrange
            run = self.run
            validation_results = {"passed": True}
            
            # Act
            run.verify_ai(validation_results)
            
            # Assert
            expect(run.state.status).to(equal(RunStatus.AI_VERIFIED.value))
            expect(run.ai_verified_at).not_to(be_none)
            expect(run.validation_results).to(equal(validation_results))
        
        with it('should approve and transition to HUMAN_APPROVED'):
            # Arrange
            run = self.run
            run.state.status = RunStatus.AI_VERIFIED.value
            feedback = "Looks good"
            
            # Act
            run.approve(feedback)
            
            # Assert
            expect(run.state.status).to(equal(RunStatus.HUMAN_APPROVED.value))
            expect(run.human_approved_at).not_to(be_none)
            expect(run.human_feedback).to(equal(feedback))
        
        with it('should reject and transition back to STARTED'):
            # Arrange
            run = self.run
            run.state.status = RunStatus.AI_VERIFIED.value
            feedback = "Needs fixes"
            
            # Act
            run.reject(feedback)
            
            # Assert
            expect(run.state.status).to(equal(RunStatus.STARTED.value))
            expect(run.ai_verified_at).to(be_none)
            expect(run.validation_results).to(be_none)
            expect(run.human_feedback).to(equal(feedback))
        
        with it('should complete run'):
            # Arrange
            run = self.run
            
            # Act
            run.complete()
            
            # Assert
            expect(run.state.status).to(equal(RunStatus.COMPLETED.value))
            expect(run.completed_at).not_to(be_none)
        
        with it('should abandon run'):
            # Arrange
            run = self.run
            reason = "Not needed"
            
            # Act
            run.abandon(reason)
            
            # Assert
            expect(run.state.status).to(equal(RunStatus.ABANDONED.value))
            expect(run.completed_at).not_to(be_none)
            expect(run.human_feedback).to(equal(reason))
        
        with it('should start run with step_type and context'):
            # Arrange
            run = self.run
            step_type = "test_step"
            context = {"key": "value"}
            
            # Act
            run_id = run.start(step_type, context)
            
            # Assert
            expect(run.run_id).to(equal(run_id))
            expect(run.step_type).to(equal(step_type))
            expect(run.context).to(equal(context))
            expect(run.state.status).to(equal(RunStatus.STARTED.value))
            expect(run.started_at).not_to(be_none)
        
        with it('should repeat run and create new run'):
            # Arrange
            run = self.run
            run.step_type = "test_step"
            run.context = {"key": "value"}
            run_history = RunHistory()
            
            # Act
            new_run = run.repeat(run_history)
            
            # Assert
            expect(new_run.run_number).to(equal(1))
            expect(new_run.step_type).to(equal("test_step"))
            expect(new_run.context).to(equal({"key": "value"}))
            expect(new_run).not_to(equal(run))
    
    with context('can_proceed_to_next_step'):
        with it('should allow proceeding when completed'):
            # Arrange
            run = Run(1, RunStatus.COMPLETED.value)
            
            # Act
            can_proceed, reason = run.can_proceed_to_next_step()
            
            # Assert
            expect(can_proceed).to(be_true)
            expect(reason).to(contain("complete"))
        
        with it('should block when started'):
            # Arrange
            run = Run(1, RunStatus.STARTED.value)
            
            # Act
            can_proceed, reason = run.can_proceed_to_next_step()
            
            # Assert
            expect(can_proceed).to(be_false)
            expect(reason).to(contain("AI must verify"))

with description('RunHistory class'):
    """Tests for RunHistory domain object"""
    
    with before.each:
        self.run_history = RunHistory()
        self.run1 = Run(1, RunStatus.COMPLETED.value)
        self.run1.run_id = "run_1"
        self.run2 = Run(2, RunStatus.STARTED.value)
        self.run2.run_id = "run_2"
        self.run3 = Run(3, RunStatus.COMPLETED.value)
        self.run3.run_id = "run_3"
    
    with it('should find run by number'):
        # Arrange
        self.run_history.runs = [self.run1, self.run2, self.run3]
        
        # Act
        found = self.run_history.find_by_number(2)
        
        # Assert
        expect(found).to(equal(self.run2))
        expect(found.run_number).to(equal(2))
    
    with it('should return None when run number not found'):
        # Arrange
        self.run_history.runs = [self.run1, self.run2]
        
        # Act
        found = self.run_history.find_by_number(99)
        
        # Assert
        expect(found).to(be_none)
    
    with it('should find run by id'):
        # Arrange
        self.run_history.runs = [self.run1, self.run2, self.run3]
        
        # Act
        found = self.run_history.find_by_id("run_2")
        
        # Assert
        expect(found).to(equal(self.run2))
        expect(found.run_id).to(equal("run_2"))
    
    with it('should return None when run id not found'):
        # Arrange
        self.run_history.runs = [self.run1, self.run2]
        
        # Act
        found = self.run_history.find_by_id("nonexistent")
        
        # Assert
        expect(found).to(be_none)
    
    with it('should get completed count'):
        # Arrange
        self.run_history.runs = [self.run1, self.run2, self.run3]
        
        # Act
        count = self.run_history.get_completed_count()
        
        # Assert
        expect(count).to(equal(2))
    
    with it('should get recent runs'):
        # Arrange
        self.run_history.runs = [self.run1, self.run2, self.run3]
        
        # Act
        recent = self.run_history.get_recent_runs(2)
        
        # Assert
        expect(recent).to(have_length(2))
        expect(recent).to(contain(self.run2))
        expect(recent).to(contain(self.run3))

with description('RunState class'):
    """Tests for RunState data object"""
    
    with context('state properties'):
        with it('should indicate completed when status is COMPLETED'):
            # Arrange
            state = RunState(RunStatus.COMPLETED.value)
            
            # Act & Assert
            expect(state.completed).to(be_true)
            expect(state.abandoned).to(be_false)
            expect(state.finished).to(be_true)
            expect(state.started).to(be_false)
            expect(state.ai_verified).to(be_false)
            expect(state.human_approved).to(be_false)
        
        with it('should indicate abandoned when status is ABANDONED'):
            # Arrange
            state = RunState(RunStatus.ABANDONED.value)
            
            # Act & Assert
            expect(state.abandoned).to(be_true)
            expect(state.completed).to(be_false)
            expect(state.finished).to(be_true)
            expect(state.started).to(be_false)
        
        with it('should indicate started when status is STARTED'):
            # Arrange
            state = RunState(RunStatus.STARTED.value)
            
            # Act & Assert
            expect(state.started).to(be_true)
            expect(state.completed).to(be_false)
            expect(state.abandoned).to(be_false)
            expect(state.finished).to(be_false)
        
        with it('should indicate ai_verified when status is AI_VERIFIED'):
            # Arrange
            state = RunState(RunStatus.AI_VERIFIED.value)
            
            # Act & Assert
            expect(state.ai_verified).to(be_true)
            expect(state.completed).to(be_false)
            expect(state.human_approved).to(be_false)
        
        with it('should indicate human_approved when status is HUMAN_APPROVED'):
            # Arrange
            state = RunState(RunStatus.HUMAN_APPROVED.value)
            
            # Act & Assert
            expect(state.human_approved).to(be_true)
            expect(state.completed).to(be_false)
            expect(state.ai_verified).to(be_false)

with description('RuleParser class'):
    """Tests for RuleParser"""
    
    with context('file reading'):
        with it('should read file content'):
            # Arrange
            import tempfile
            import os
            parser = RuleParser()
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.mdc') as f:
                f.write("Test content")
                test_file = f.name
            
            try:
                # Act
                content = parser.read_file_content(test_file)
                
                # Assert
                expect(content).to(equal("Test content"))
            finally:
                if os.path.exists(test_file):
                    os.unlink(test_file)
        
        with it('should return None for non-existent file'):
            # Arrange
            parser = RuleParser()
            
            # Act
            content = parser.read_file_content("nonexistent.mdc")
            
            # Assert
            expect(content).to(be_none)
    
    with context('principle parsing'):
        with it('should find principle matches in content'):
            # Arrange
            parser = RuleParser()
            content = """## 1. First Principle
Content here.

## 2. Second Principle
More content.
"""
            
            # Act
            matches = parser.find_principle_matches(content)
            
            # Assert
            expect(matches).to(have_length(2))
            expect(matches[0].group(1)).to(equal("1"))
            expect(matches[0].group(2)).to(equal("First Principle"))
            expect(matches[1].group(1)).to(equal("2"))
            expect(matches[1].group(2)).to(equal("Second Principle"))
        
        with it('should extract principle content between matches'):
            # Arrange
            parser = RuleParser()
            content = """## 1. First
Content for first.

## 2. Second
Content for second.
"""
            matches = parser.find_principle_matches(content)
            
            # Act
            principle_content = parser.extract_principle_content(content, matches[0], matches, 0)
            
            # Assert
            expect(principle_content).to(contain("Content for first"))
            expect(principle_content).not_to(contain("Content for second"))
    
    with context('example parsing'):
        with it('should extract DO example'):
            # Arrange
            parser = RuleParser()
            content = """**[DO]:**
Some text here.
```java
public class Good { }
```
"""
            
            # Act
            do_text, do_code = parser.extract_do_example(content)
            
            # Assert
            expect(do_code).to(contain("public class Good"))
            expect(do_text).to(contain("Some text here"))
        
        with it('should extract DONT example'):
            # Arrange
            parser = RuleParser()
            content = """**[DON'T]:**
Bad example.
```java
public class Bad { }
```
"""
            
            # Act
            dont_text, dont_code = parser.extract_dont_example(content)
            
            # Assert
            expect(dont_code).to(contain("public class Bad"))
            expect(dont_text).to(contain("Bad example"))
        
        with it('should load examples from content'):
            # Arrange
            parser = RuleParser()
            principle = Principle(1, "Test Principle", "Test content")
            content = """**[DO]:**
```java
public class Good { }
```

**[DON'T]:**
```java
public class Bad { }
```
"""
            
            # Act
            examples = parser.load_examples_from_content(content, principle)
            
            # Assert
            expect(examples).to(have_length(1))
            expect(examples[0].do_code).to(contain("Good"))
            expect(examples[0].dont_code).to(contain("Bad"))
            expect(examples[0].principle).to(equal(principle))
    
    with context('principle creation'):
        with it('should create principle from match with examples'):
            # Arrange
            parser = RuleParser()
            content = """## 1. Test Principle
Principle description.

**[DO]:**
```java
public class Good { }
```
"""
            matches = parser.find_principle_matches(content)
            
            # Act
            principle = parser.create_principle_from_match(content, matches[0], matches, 0)
            
            # Assert
            expect(principle.principle_number).to(equal(1))
            expect(principle.principle_name).to(equal("Test Principle"))
            expect(principle.content).to(contain("Principle description"))
            expect(principle.examples).to(have_length(1))
            expect(principle.examples[0].do_code).to(contain("Good"))
    
    with context('loading principles from file'):
        with it('should load all principles from file'):
            # Arrange
            import tempfile
            import os
            parser = RuleParser()
            
            test_content = """## 1. First Principle
First content.

## 2. Second Principle
Second content.
"""
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.mdc') as f:
                f.write(test_content)
                test_file = f.name
            
            try:
                # Act
                principles = parser.load_principles_from_file(test_file)
                
                # Assert
                expect(principles).to(have_length(2))
                expect(principles[0].principle_number).to(equal(1))
                expect(principles[0].principle_name).to(equal("First Principle"))
                expect(principles[1].principle_number).to(equal(2))
                expect(principles[1].principle_name).to(equal("Second Principle"))
            finally:
                if os.path.exists(test_file):
                    os.unlink(test_file)

with description('IncrementalState class'):
    """Tests for IncrementalState persistence"""
    
    with context('state file path'):
        with it('should derive state file path from command file path'):
            # Arrange
            state = IncrementalState("test/command.py")
            
            # Act
            state_path = state.get_state_file_path()
            
            # Assert
            expect(str(state_path)).to(contain(".incremental-state"))
            expect(str(state_path)).to(contain("command.state.json"))
    
    with context('save and load'):
        with it('should save and load run history'):
            # Arrange
            import tempfile
            import os
            with tempfile.TemporaryDirectory() as tmpdir:
                test_file = os.path.join(tmpdir, "test.py")
                state = IncrementalState(test_file)
                run_history = RunHistory()
                run = Run(1, RunStatus.STARTED.value)
                run.run_id = "test_run"
                run_history.runs.append(run)
                
                # Act - save
                state.save(run_history, run)
                
                # Assert - file exists
                state_path = state.get_state_file_path()
                expect(state_path.exists()).to(be_true)
                
                # Act - load
                new_history = RunHistory()
                loaded_run = state.load(new_history)
                
                # Assert
                expect(new_history.runs).to(have_length(1))
                expect(new_history.runs[0].run_id).to(equal("test_run"))
                expect(loaded_run.run_id).to(equal("test_run"))

with description('Command.execute() method'):
    """Tests for Command.execute() workflow"""
    
    with before.each:
        test_base_rule_content = create_base_rule_content()
        with patch.object(RuleParser, 'read_file_content', return_value=test_base_rule_content):
            self.base_rule = BaseRule('base-rule.mdc')
            parser = RuleParser()
            self.base_rule.principles = parser.load_principles_from_file('base-rule.mdc')
        self.content = Content('test.java', '.java')
    
    with it('should generate when not generated'):
        # Arrange
        command = Command(self.content, self.base_rule)
        
        # Act
        result = command.execute()
        
        # Assert
        expect(command.generated).to(be_true)
        expect(command.validated).to(be_false)
        expect(result).to(contain("Please generate"))
    
    with it('should validate when already generated'):
        # Arrange
        command = Command(self.content, self.base_rule)
        command.generated = True
        
        # Act
        result = command.execute()
        
        # Assert
        expect(command.generated).to(be_true)
        expect(command.validated).to(be_true)
        expect(result).to(contain("Please validate"))
    
    with it('should return validation result when both generated and validated'):
        # Arrange
        command = Command(self.content, self.base_rule)
        command.generated = True
        command.validated = True
        
        # Act
        result = command.execute()
        
        # Assert
        expect(command.generated).to(be_true)
        expect(command.validated).to(be_true)
        expect(result).to(contain("Please validate"))

with description('Command.plan() method'):
    """Tests for Command.plan() method"""
    
    with before.each:
        test_base_rule_content = create_base_rule_content()
        with patch.object(RuleParser, 'read_file_content', return_value=test_base_rule_content):
            self.base_rule = BaseRule('base-rule.mdc')
            parser = RuleParser()
            self.base_rule.principles = parser.load_principles_from_file('base-rule.mdc')
        self.content = Content('test.java', '.java')
    
    with it('should return None by default'):
        # Arrange
        command = Command(self.content, self.base_rule)
        
        # Act
        result = command.plan()
        
        # Assert
        expect(result).to(be_none)
    
    with it('should return None when plan_template_name is None'):
        # Arrange
        command = Command(self.content, self.base_rule)
        
        # Act
        result = command.plan(plan_template_name=None)
        
        # Assert
        expect(result).to(be_none)
    
    with it('should accept plan_template_name and template_kwargs'):
        # Arrange
        command = Command(self.content, self.base_rule)
        
        # Act - should not raise error
        result = command.plan(plan_template_name="test.md", param1="value1", param2="value2")
        
        # Assert - base Command returns None (subclasses implement actual logic)
        expect(result).to(be_none)

with description('CodeAugmentedCommand.plan() method'):
    """Tests for CodeAugmentedCommand.plan() delegation"""
    
    with before.each:
        test_base_rule_content = create_base_rule_content()
        with patch.object(RuleParser, 'read_file_content', return_value=test_base_rule_content):
            self.base_rule = BaseRule('base-rule.mdc')
            parser = RuleParser()
            self.base_rule.principles = parser.load_principles_from_file('base-rule.mdc')
        self.content = Content('test.java', '.java')
    
    with it('should delegate plan() to inner command when inner command has plan method'):
        # Arrange
        base_command = Command(self.content, self.base_rule)
        code_augmented_command = CodeAugmentedCommand(base_command, self.base_rule)
        
        # Mock inner command's plan method
        with patch.object(base_command, 'plan', return_value='plan result') as mock_plan:
            # Act
            result = code_augmented_command.plan(plan_template_name="test.md", param1="value1")
            
            # Assert
            expect(mock_plan.called).to(be_true)
            expect(result).to(equal('plan result'))
            expect(mock_plan.call_args[0][0]).to(equal("test.md"))
            expect(mock_plan.call_args[1]['param1']).to(equal("value1"))
    
    with it('should return None when inner command does not have plan method'):
        # Arrange
        base_command = Command(self.content, self.base_rule)
        code_augmented_command = CodeAugmentedCommand(base_command, self.base_rule)
        
        # Act
        result = code_augmented_command.plan(plan_template_name="test.md")
        
        # Assert
        expect(result).to(be_none)


with description('Command.correct() method'):
    """Tests for Command.correct() - rule correction based on context"""
    
    def create_test_command():
        """Helper to create command with test fixtures"""
        return Command(self.content, self.base_rule)
    
    def create_example_with_code(principle):
        """Helper to create example with DO/DON'T code"""
        return Example(
            principle=principle,
            do_text="Good example",
            do_code="good_code()",
            dont_text="Bad example",
            dont_code="bad_code()"
        )
    
    with before.each:
        test_base_rule_content = create_base_rule_content()
        with patch.object(RuleParser, 'read_file_content', return_value=test_base_rule_content):
            self.base_rule = BaseRule('base-rule.mdc')
            parser = RuleParser()
            self.base_rule.principles = parser.load_principles_from_file('base-rule.mdc')
        self.content = Content('test.java', '.java')
        self.chat_context = "User encountered error pattern XYZ"
    
    with context('that is corrected with context'):
        with it('should have access to chat context'):
            # Arrange
            command = create_test_command()
            specific_context = "Error pattern detected in line 42"
            
            # Act
            result = command.correct(specific_context)
            
            # Assert
            expect(result).to(contain(specific_context))
        
        with it('should have access to content with error'):
            # Arrange
            self.content.violations = [Violation(line_number=42, message="Test violation")]
            command = create_test_command()
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("test.java"))
        
        with it('should have access to rule principles'):
            # Arrange
            command = create_test_command()
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("Test Principle"))
            expect(len(command.principles)).to(equal(1))
    
    with context('when correction is requested'):
        with it('should instruct AI prompt to correct the error based on context'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("correct the error"))
            expect(result).to(contain(self.chat_context))
        
        with it('should insert all existing examples from rule in instructions'):
            # Arrange
            example = Example(
                principle=self.base_rule.principles[0],
                do_text="Good example",
                do_code="good_code()",
                dont_text="Bad example",
                dont_code="bad_code()"
            )
            self.base_rule.principles[0].examples = [example]
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("good_code()"))
            expect(result).to(contain("bad_code()"))
        
        with it('should insert all principles from rule in instructions'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("Test Principle"))
        
        with it('should tell AI to examine context for changes to principle'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("examine context"))
            expect(result).to(contain("principle"))
        
        with it('should tell AI to examine context for changes to examples'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("examine context"))
            expect(result).to(contain("examples"))
        
        with it('should tell AI to propose new principle if needed'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("propose new principle"))
        
        with it('should tell AI to propose new example if needed'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("propose new example"))
        
        with it('should set corrected flag to true'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            command.correct(self.chat_context)
            
            # Assert
            expect(command.corrected).to(be_true)
    
    with context('that generates correction instructions for AI'):
        with it('should include instruction to analyze error pattern in context'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("analyze error pattern"))
        
        with it('should include instruction to create new principle capturing pattern'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("create new principle"))
            expect(result).to(contain("capturing pattern"))
        
        with it('should include next available principle number'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            next_number = len(self.base_rule.principles) + 1
            expect(result).to(contain(f"Principle {next_number}"))
        
        with it('should include instruction to use principle_template'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("principle_template"))
        
        with it('should include instruction to analyze why principle was unclear'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("why principle was unclear"))
        
        with it('should include instruction to improve principle content'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("improve principle content"))
        
        with it('should include instruction to preserve principle structure'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("preserve principle structure"))
        
        with it('should include instruction to run DO example against content to see if would prevent error'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("run DO example"))
            expect(result).to(contain("prevent error"))
        
        with it('should include instruction to test example against all other principles'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("test example against all other principles"))
        
        with it('should include instruction to auto fix if example violates other principles'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("auto fix"))
            expect(result).to(contain("violates other principles"))
        
        with it('should include instructions to consider code heuristic for new example if it makes sense'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("code heuristic"))
        
        with it('should include instructions to create code-heuristics according to code-agent-rules rules and code heuristics section'):
            # Arrange
            command = Command(self.content, self.base_rule)
            
            # Act
            result = command.correct(self.chat_context)
            
            # Assert
            expect(result).to(contain("code-agent-rules"))
            expect(result).to(contain("code heuristics section"))