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

