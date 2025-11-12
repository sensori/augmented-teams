"""DDD Runner - Domain-Driven Design analysis commands"""

from pathlib import Path
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import common runner framework
common_runner_path = Path(__file__).parent.parent / "common_command_runner" / "common_command_runner.py"
import importlib.util
spec = importlib.util.spec_from_file_location("common_command_runner", common_runner_path)
common_runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common_runner)

Content = common_runner.Content
BaseRule = common_runner.BaseRule
Command = common_runner.Command
CodeAugmentedCommand = common_runner.CodeAugmentedCommand
CodeHeuristic = common_runner.CodeHeuristic
Violation = common_runner.Violation


class DDDCommand(Command):
    """Base class for DDD commands"""
    
    def __init__(self, content: Content, base_rule_file_name: str = 'ddd-rule.mdc'):
        base_rule = BaseRule(base_rule_file_name)
        super().__init__(content, base_rule)


class DDDStructureCommand(DDDCommand):
    """Command for analyzing domain structure"""
    
    def generate(self):
        """Generate domain structure analysis prompts"""
        return """Analyze the source file to extract domain structure following DDD principles.

Apply these principles from ddd-rule.mdc:
- §1: Use outcome verbs, not communication verbs
- §2: Integrate system support under domain concepts
- §3: Order by user mental model (foundation → features)
- §4: Organize domain-first, system infrastructure last
- §5: Focus on functional accomplishment
- §6: Maximize integration of related concepts
- §7: Domain concepts are nouns, behaviors are verbs
- §8: Assign behaviors to the concept that performs them
- §9: Avoid noun redundancy
- §10: Organize by domain concepts, not file structure

Output hierarchical domain map to <name>-domain-map.txt with:
- FUNCTIONAL PURPOSE at top
- Domains ordered before infrastructure
- Concepts ordered by user mental model
- Relationships embedded in each concept
- Tab indentation for nesting"""
    
    def validate(self):
        """Validate domain structure against DDD principles"""
        return """Validate the domain map follows DDD principles.

Check for violations:
- §1: Communication verbs (showing, displaying, visualizing)
- §2: Separated system support sections
- §3: Code-structure ordering
- §4: System-first organization
- §5: Technical/mechanism framing
- §6: Artificial separation of related concepts
- §7: Verb-based concept names
- §8: Behaviors on wrong concepts
- §9: Noun redundancy in domain names
- §10: File structure organization

Report any violations found."""


class DDDInteractionCommand(DDDCommand):
    """Command for documenting domain interactions"""
    
    def generate(self):
        """Generate domain interaction analysis prompts"""
        return """Document domain concept interactions and business flows.

First, discover the domain map file (*-domain-map.txt) in the same directory.

Apply these principles from ddd-rule.mdc §11:
- §11.1: Maintain domain-level abstraction (no implementation details)
- §11.2: Structure scenarios with trigger, actors, flow, rules, result
- §11.3: Describe transformations at business level (A → B)
- §11.4: Describe lookups as business strategy (priority, patterns)
- §11.5: State business rules as domain logic (not code conditionals)

Output scenario-based flows to <name>-domain-interactions.txt with:
- SCENARIO structure for each business flow
- Domain concept names from domain map
- Business-level transformations and lookups
- Business rules clearly stated
- No code syntax or implementation details"""
    
    def validate(self):
        """Validate domain interactions against DDD principles"""
        return """Validate the interaction flows follow DDD principles.

Check for violations:
- §11.1: Implementation details (field names, code syntax, API parameters)
- §11.2: Missing scenario structure elements
- §11.3: Code-level transformations (constructors, field mapping)
- §11.4: Implementation-level lookups (queries, filters)
- §11.5: Code conditionals instead of business rules

Report any violations found."""


class CodeAugmentedDDDStructureCommand(CodeAugmentedCommand):
    """Wrapper for DDDStructureCommand with validation"""
    
    def __init__(self, file_path: str):
        content = Content(file_path)
        inner_command = DDDStructureCommand(content)
        base_rule = BaseRule('ddd-rule.mdc')
        super().__init__(inner_command, base_rule)
    
    @classmethod
    def handle_cli(cls, action: str, args: list):
        """Handle CLI invocation"""
        if len(args) < 1:
            print("Usage: ddd_runner.py {action}-structure <file-path>")
            sys.exit(1)
        
        file_path = args[0]
        command = cls(file_path)
        
        if action == "generate":
            result = command.generate()
            print(result)
        elif action == "validate":
            result = command.validate()
            print(result)
        elif action == "execute":
            result = command.generate()
            print(result)
            print("\nAfter reviewing, run validate-structure to check against DDD principles")
        elif action == "correct":
            chat_context = args[1] if len(args) > 1 else "User requested DDD rule correction based on current chat context"
            result = command.correct(chat_context)
            print(result)


class CodeAugmentedDDDInteractionCommand(CodeAugmentedCommand):
    """Wrapper for DDDInteractionCommand with validation"""
    
    def __init__(self, file_path: str):
        content = Content(file_path)
        inner_command = DDDInteractionCommand(content)
        base_rule = BaseRule('ddd-rule.mdc')
        super().__init__(inner_command, base_rule)
    
    @classmethod
    def handle_cli(cls, action: str, args: list):
        """Handle CLI invocation"""
        if len(args) < 1:
            print("Usage: ddd_runner.py {action}-interaction <file-path>")
            sys.exit(1)
        
        file_path = args[0]
        command = cls(file_path)
        
        if action == "generate":
            result = command.generate()
            print(result)
        elif action == "validate":
            result = command.validate()
            print(result)
        elif action == "execute":
            result = command.generate()
            print(result)
            print("\nAfter reviewing, run validate-interaction to check against DDD principles")
        elif action == "correct":
            chat_context = args[1] if len(args) > 1 else "User requested DDD rule correction based on current chat context"
            result = command.correct(chat_context)
            print(result)


# DDD VALIDATION HEURISTICS (Reusable by other commands)

class DDDDomainLanguageHeuristic(CodeHeuristic):
    """Validate domain language vs technical language (DDD Principle 4)
    
    Reusable by: Story Exploration (Domain AC), Clean Code, etc.
    """
    
    def __init__(self):
        super().__init__(detection_pattern="ddd_domain_language")
    
    def scan(self, content):
        """Scan for technical terms that should be domain language"""
        violations = []
        if not hasattr(content, 'file_path'):
            return violations
        
        # Load content
        if not hasattr(content, '_content_lines') or content._content_lines is None:
            try:
                with open(content.file_path, 'r', encoding='utf-8') as f:
                    content._content_lines = f.readlines()
            except (FileNotFoundError, IOError):
                return violations
        
        if not content._content_lines:
            return violations
        
        # Technical terms that violate DDD Principle 4
        technical_terms = [
            'api', 'json', 'database', 'endpoint', 'schema', 
            'http', 'rest', 'request', 'response', 'table', 
            'query', 'transaction', 'dto', 'repository', 'service',
            'controller', 'model', 'view', 'crud'
        ]
        
        for line_num, line in enumerate(content._content_lines, start=1):
            line_lower = line.lower()
            # Skip code blocks and comments
            if line.strip().startswith('```') or line.strip().startswith('#'):
                continue
            
            for term in technical_terms:
                if term in line_lower and not self._is_acceptable_context(line_lower, term):
                    violations.append((line_num, f"Uses technical term '{term}' - use domain language (DDD Principle 4)"))
                    break  # Only report one violation per line
        
        return violations
    
    def _is_acceptable_context(self, line, term):
        """Check if technical term is in acceptable context (e.g., example of what NOT to do)"""
        # Allow in "DON'T" examples or negative examples
        if 'not' in line or "don't" in line or 'avoid' in line or 'instead of' in line:
            return True
        return False
    
    def scan_content(self, content):
        """Wrapper for scan_content interface"""
        violations = self.scan(content)
        violation_objects = []
        for line_num, message in violations:
            violation_objects.append(Violation(line_number=line_num, message=message))
        return violation_objects


class DDDConceptStructureHeuristic(CodeHeuristic):
    """Validate concepts are nouns, behaviors are verbs (DDD Principle 7)
    
    Reusable by: Story Exploration (Domain AC), Domain Modeling
    """
    
    def __init__(self):
        super().__init__(detection_pattern="ddd_concept_structure")
    
    def scan(self, content):
        """Scan for concept naming violations"""
        violations = []
        if not hasattr(content, 'file_path'):
            return violations
        
        # Load content
        if not hasattr(content, '_content_lines') or content._content_lines is None:
            try:
                with open(content.file_path, 'r', encoding='utf-8') as f:
                    content._content_lines = f.readlines()
            except (FileNotFoundError, IOError):
                return violations
        
        if not content._content_lines:
            return violations
        
        # Verb-based concept names that violate DDD Principle 7
        verb_forms = ['ing', 'tion', 'sion', 'ment', 'ance', 'ence']
        
        in_concepts_section = False
        for line_num, line in enumerate(content._content_lines, start=1):
            line_lower = line.lower()
            
            # Track if we're in Core Concepts section
            if '### core' in line_lower and 'concept' in line_lower:
                in_concepts_section = True
                continue
            elif line.startswith('###') or line.startswith('##'):
                in_concepts_section = False
            
            # Check concept names (lines starting with **)
            if in_concepts_section and line.strip().startswith('**') and ':' in line:
                concept_name = line.split('**')[1].split(':')[0].strip() if '**' in line else ''
                # Check for gerund forms (-ing)
                if concept_name.endswith('ing'):
                    violations.append((line_num, f"Concept '{concept_name}' uses verb form (-ing) - use noun instead (DDD Principle 7)"))
                # Check for process nouns (-tion, -sion, -ment)
                elif any(concept_name.lower().endswith(suffix) for suffix in ['tion', 'sion', 'ment']):
                    # These are acceptable IF they represent actual domain concepts (e.g., "Configuration", "Animation")
                    # Only flag if combined with processing/execution verbs
                    if any(word in concept_name.lower() for word in ['processing', 'execution', 'resolution']):
                        violations.append((line_num, f"Concept '{concept_name}' emphasizes process over thing - use noun form (DDD Principle 7)"))
        
        return violations
    
    def scan_content(self, content):
        """Wrapper for scan_content interface"""
        violations = self.scan(content)
        violation_objects = []
        for line_num, message in violations:
            violation_objects.append(Violation(line_number=line_num, message=message))
        return violation_objects


class DDDOutcomeVerbsHeuristic(CodeHeuristic):
    """Validate outcome verbs vs communication verbs (DDD Principle 1)
    
    Reusable by: Story Exploration (Domain Behaviors), Domain Modeling
    """
    
    def __init__(self):
        super().__init__(detection_pattern="ddd_outcome_verbs")
    
    def scan(self, content):
        """Scan for communication verbs that should be outcome verbs"""
        violations = []
        if not hasattr(content, 'file_path'):
            return violations
        
        # Load content
        if not hasattr(content, '_content_lines') or content._content_lines is None:
            try:
                with open(content.file_path, 'r', encoding='utf-8') as f:
                    content._content_lines = f.readlines()
            except (FileNotFoundError, IOError):
                return violations
        
        if not content._content_lines:
            return violations
        
        # Communication verbs that violate DDD Principle 1
        communication_verbs = [
            'showing', 'displaying', 'visualizing', 'presenting',
            'providing', 'enabling', 'allowing', 'offering'
        ]
        
        in_behaviors_section = False
        for line_num, line in enumerate(content._content_lines, start=1):
            line_lower = line.lower()
            
            # Track if we're in Domain Behaviors section
            if '### domain behavior' in line_lower:
                in_behaviors_section = True
                continue
            elif line.startswith('###') or line.startswith('##'):
                in_behaviors_section = False
            
            # Check for communication verbs
            if in_behaviors_section:
                for verb in communication_verbs:
                    if verb in line_lower:
                        violations.append((line_num, f"Uses communication verb '{verb}' - describe the outcome/artifact instead (DDD Principle 1)"))
                        break
        
        return violations
    
    def scan_content(self, content):
        """Wrapper for scan_content interface"""
        violations = self.scan(content)
        violation_objects = []
        for line_num, message in violations:
            violation_objects.append(Violation(line_number=line_num, message=message))
        return violation_objects


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python ddd_runner.py <command> [args...]")
        print("\nCommands:")
        print("  execute-structure <file-path>")
        print("  generate-structure <file-path>")
        print("  validate-structure <domain-map>")
        print("  correct-structure <file-path> [chat-context]")
        print("  execute-interaction <file-path>")
        print("  generate-interaction <file-path>")
        print("  validate-interaction <interactions-file>")
        print("  correct-interaction <file-path> [chat-context]")
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command in ["execute-structure", "generate-structure", "validate-structure", "correct-structure"]:
        action = command.replace("-structure", "").replace("execute", "generate")
        CodeAugmentedDDDStructureCommand.handle_cli(action, args)
    elif command in ["execute-interaction", "generate-interaction", "validate-interaction", "correct-interaction"]:
        action = command.replace("-interaction", "").replace("execute", "generate")
        CodeAugmentedDDDInteractionCommand.handle_cli(action, args)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

