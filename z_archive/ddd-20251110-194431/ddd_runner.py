"""
DDD Runner - Domain-Driven Design Analysis Commands

Implements commands for extracting domain structures and documenting interactions.
"""

from pathlib import Path
import sys
from typing import Optional, List, Dict

# Add common_command_runner to path
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
    """Base command for DDD operations"""
    
    def __init__(self, content: Content, base_rule_file_name: str = 'ddd-rule.mdc'):
        base_rule = BaseRule(base_rule_file_name)
        super().__init__(content, base_rule)


class DDDStructureCommand(DDDCommand):
    """Command for extracting domain structure from code/text/diagrams"""
    
    def __init__(self, source_file_path: str):
        content = Content(file_path=source_file_path)
        super().__init__(content)
        self.source_file_path = source_file_path
    
    def generate(self) -> str:
        """Returns prompts/instructions for AI to analyze and extract domain structure"""
        return """Analyze the source file to extract domain structure following DDD principles:

**Apply These Principles (ddd-rule.mdc §1-10):**

§1: Use outcome verbs, not communication verbs
- Use verbs describing artifacts/outcomes: "Animation", "Feedback", "Configuration"
- Avoid: "showing", "displaying", "visualizing", "presenting", "providing"

§2: Integrate system support under domain concepts
- Nest technical implementation under the domain concept it serves
- Don't create separate "SYSTEM SUPPORT" sections

§3: Order by user mental model, not code structure
- Put foundational objects BEFORE features that use them
- Order: core objects → operations → supporting infrastructure

§4: Organize domain-first, system support second
- Lead with domain-specific concepts
- Put system infrastructure at the end

§5: Focus on functional accomplishment
- Frame by what it accomplishes for users
- Ask: "What does this enable the user to do?"

§6: Maximize integration of related concepts
- Group concepts the user sees as one capability
- Eliminate artificial boundaries

§7: Domain concepts are nouns, behaviors are verbs
- Name concepts as nouns: "Animation", "Power Item"
- Describe behaviors on concepts

§8: Assign behaviors to the concept that performs them
- Place behavior under concept that contains the logic
- Check the code: which class has the method?

§9: Avoid noun redundancy in domain names
- Don't repeat same noun at domain level
- Prefer integration over renaming

§10: Organize by domain concepts, not file structure
- Group by functional capability, not by file types

**Output Format:**
Generate hierarchical domain map as text file: `<name>-domain-map.txt`

Structure:
```
FUNCTIONAL PURPOSE: <what this accomplishes>

DOMAIN 1
\t<what this domain does>
\t
\tConcept A
\t\t<what concept does>
\t\t<properties>
\t\t
\t\tRELATIONSHIPS:
\t\t\tUSES: Concept B

SYSTEM INFRASTRUCTURE
\t<technical systems>
```

Analyze the source file and generate the domain map."""
    
    def validate(self) -> str:
        """Returns validation prompts/instructions for AI"""
        return """Validate the domain structure against DDD principles (§1-10):

Check for violations:
- §1: Communication verbs (showing, displaying, providing)
- §2: Separated system support sections
- §3: Code structure ordering instead of user mental model
- §4: System concepts before domain concepts
- §5: Technical framing instead of functional outcomes
- §6: Artificial separation of related concepts
- §7: Verb-based concept names
- §8: Behaviors on wrong concepts
- §9: Noun redundancy in domain names
- §10: File structure organization

Report any violations found."""


class DDDInteractionCommand(DDDCommand):
    """Command for documenting domain concept interactions"""
    
    def __init__(self, source_file_path: str):
        content = Content(file_path=source_file_path)
        super().__init__(content)
        self.source_file_path = source_file_path
    
    def generate(self) -> str:
        """Returns prompts/instructions for AI to document domain interactions"""
        return """Document domain concept interactions following DDD principles (§11):

**Find Domain Map:**
Look for `*-domain-map.txt` file in the same directory as source code.

**Apply These Principles (ddd-rule.mdc §11):**

§11.1: Maintain domain abstraction level
- Refer to domain concepts by name from map
- Describe business transformations, lookups, rules
- Avoid: field names, code syntax, API parameters

§11.2: Use scenario structure
- TRIGGER, ACTORS, FLOW, BUSINESS RULES, RESULT
- Show domain concept interactions
- End with business outcome

§11.3: Describe transformations clearly
- Pattern: [Source] → [Logic] → [Target]
- No constructor calls or object creation code

§11.4: Describe lookups as business logic
- Search strategy, matching criteria
- No database queries or iteration code

§11.5: State business rules clearly
- Priorities as ordered lists
- No if/else code structure

§11.6: Show cross-domain reuse
- What's reused, what's added
- No code inheritance details

**Output Format:**
Generate scenario-based flows: `<name>-domain-interactions.txt`

Place in same directory as domain map."""
    
    def validate(self) -> str:
        """Returns validation prompts/instructions for AI"""
        return """Validate domain interactions against §11 principles:

Check for violations:
- §11.1: Implementation details (field names, code syntax)
- §11.2: Missing scenario structure elements
- §11.3: Constructor calls in transformations
- §11.4: Database queries in lookups
- §11.5: Code conditionals in business rules
- §11.6: Code reuse details in cross-domain

Report any violations found."""


# Wrapper classes for CLI integration
class CodeAugmentedDDDStructureCommand(CodeAugmentedCommand):
    """Wraps DDDStructureCommand with heuristic validation"""
    
    def __init__(self, source_file_path: str):
        inner_command = DDDStructureCommand(source_file_path)
        base_rule = BaseRule('ddd-rule.mdc')
        super().__init__(inner_command, base_rule)
    
    @classmethod
    def handle_cli(cls, action: str, args: List[str]):
        """CLI handler"""
        if not args:
            print("Usage: ddd_runner.py {action}-structure <source-file-path>")
            sys.exit(1)
        
        source_file_path = args[0]
        command = cls(source_file_path)
        
        if action == "generate":
            result = command.generate()
            print(result)
        elif action == "validate":
            result = command.validate()
            print(result)
        elif action == "execute":
            print("Execute: generate then validate")
            print(command.generate())
            print("\n" + "="*60 + "\n")
            print(command.validate())


class CodeAugmentedDDDInteractionCommand(CodeAugmentedCommand):
    """Wraps DDDInteractionCommand with heuristic validation"""
    
    def __init__(self, source_file_path: str):
        inner_command = DDDInteractionCommand(source_file_path)
        base_rule = BaseRule('ddd-rule.mdc')
        super().__init__(inner_command, base_rule)
    
    @classmethod
    def handle_cli(cls, action: str, args: List[str]):
        """CLI handler"""
        if not args:
            print("Usage: ddd_runner.py {action}-interaction <source-file-path>")
            sys.exit(1)
        
        source_file_path = args[0]
        command = cls(source_file_path)
        
        if action == "generate":
            result = command.generate()
            print(result)
        elif action == "validate":
            result = command.validate()
            print(result)
        elif action == "execute":
            print("Execute: generate then validate")
            print(command.generate())
            print("\n" + "="*60 + "\n")
            print(command.validate())


def main():
    """CLI entry point"""
    # Fix Windows console encoding
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    if len(sys.argv) < 2:
        print("Usage: python ddd_runner.py <command> [args...]")
        print("\nCommands:")
        print("  execute-structure <source-file>")
        print("  generate-structure <source-file>")
        print("  validate-structure <source-file>")
        print("  execute-interaction <source-file>")
        print("  generate-interaction <source-file>")
        print("  validate-interaction <source-file>")
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command in ["execute-structure", "generate-structure", "validate-structure"]:
        action = command.replace("-structure", "")
        CodeAugmentedDDDStructureCommand.handle_cli(action, args)
    elif command in ["execute-interaction", "generate-interaction", "validate-interaction"]:
        action = command.replace("-interaction", "")
        CodeAugmentedDDDInteractionCommand.handle_cli(action, args)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

