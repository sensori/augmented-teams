# Missing File: common_command_runner.py

## Status
The `common_command_runner.py` file is **missing** from the repository but is referenced by `bdd-runner.py`.

## Expected Location
Based on imports in `bdd-runner.py` (line 31):
```
agile_bot/legacy_code/bdd_bot/common_command_runner/common_command_runner.py
```

## Required Classes (based on usage)

The file should export these classes that are imported by `bdd-runner.py`:

### Core Classes
- `Content` - Content wrapper with file_path and _content_lines
- `BaseRule` - Base rule class
- `FrameworkSpecializingRule` - Rule that specializes by framework
- `SpecializedRule` - Specialized rule
- `Command` - Base command class
- `SpecializingRuleCommand` - Command that uses specializing rules
- `CodeAugmentedCommand` - Command wrapper that uses heuristic scanners for pre-code validation
- `IncrementalCommand` - Command for incremental execution
- `WorkflowPhaseCommand` - Command for workflow phases
- `Workflow` - Workflow management

### Heuristic System Classes
- `CodeHeuristic` - Base class for all heuristics
  - Must have `__init__(detection_pattern: str)`
  - Must have `detect_violations(content)` method
  - Returns `List[Violation]` or `None`

- `Violation` - Violation object
  - Constructor: `Violation(line_number: int, message: str, principle: Optional[str] = None)`
  - Attributes: `line_number`, `message`, `principle`

### Supporting Classes
- `Principle` - Rule principle
- `Example` - Example from rules
- `ViolationReport` - Report of violations
- `Run` - Test run information
- `RunHistory` - History of test runs
- `PhaseState` - State of workflow phase
- `IncrementalState` - State of incremental execution
- `RunStatus` - Enum for run status
- `StepType` - Enum for step types

## Key Functionality

### CodeAugmentedCommand
This is the main class that implements heuristic scanning:

1. **Initialization**: Takes an inner command and base rule
2. **_get_heuristic_map()**: Returns mapping of principle numbers to heuristic classes (implemented by subclasses like BDDCommand)
3. **_load_heuristics()**: Loads heuristics from the map and attaches them to rule principles
4. **validate()**: Runs all heuristics to scan code before execution
   - Scans `content._content_lines` (list of code lines)
   - Returns violation report

### CodeHeuristic Base Class
```python
class CodeHeuristic:
    def __init__(self, detection_pattern: str):
        self.detection_pattern = detection_pattern
    
    def detect_violations(self, content) -> Optional[List[Violation]]:
        """
        Scan content for violations.
        
        Args:
            content: Content object with _content_lines attribute
            
        Returns:
            List of Violation objects, or None if no violations
        """
        raise NotImplementedError
```

## Usage Pattern

From `bdd-runner.py`:
```python
# BDDCommand extends CodeAugmentedCommand
class BDDCommand(CodeAugmentedCommand):
    def _get_heuristic_map(self):
        return {
            1: BDDRule.BDDJargonHeuristic,
            2: BDDRule.BDDComprehensiveHeuristic,
            # ... more heuristics
        }
    
    def __init__(self, content: Content, base_rule_file_name: str = 'bdd-rule.mdc'):
        self.rule = BDDRule(base_rule_file_name)
        inner_command = Command(content, self.rule.base_rule)
        super().__init__(inner_command, self.rule.base_rule)
```

## Files That Reference It
- `agile_bot/legacy_code/bdd_bot/src/bdd-runner.py` (line 31-51)
- `agile_bot/legacy_code/bdd_bot/src/bdd_runner_test.py` (line 35-55)

## Note
The actual implementation of `common_command_runner.py` is not in the repository. It may have been:
- Never committed
- Removed/deleted
- In a different location
- Part of a separate package

To use the BDD runner code, you would need to either:
1. Reconstruct `common_command_runner.py` based on the usage patterns
2. Find it in another repository or backup
3. Refactor the code to remove the dependency






















