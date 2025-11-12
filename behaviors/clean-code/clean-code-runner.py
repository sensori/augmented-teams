"""
Clean Code Behavior Runner

Validates code quality and suggests refactorings based on clean code principles.
Uses static analysis (heuristics) combined with AI-powered semantic analysis.

Architecture:
- Inherits from CodeAugmentedCommand for standard action workflow
- Uses FrameworkSpecializingRule for Python vs JavaScript rules  
- Implements heuristics for automated static analysis
- Actions: generate, validate, correct
"""

import sys
import re
import json
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime

# Import common command runner
common_runner_path = Path(__file__).parent.parent / "common_command_runner" / "common_command_runner.py"
import importlib.util
spec = importlib.util.spec_from_file_location("common_command_runner", common_runner_path)
common_runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common_runner)

# Import needed classes
Content = common_runner.Content
FrameworkSpecializingRule = common_runner.FrameworkSpecializingRule
CodeAugmentedCommand = common_runner.CodeAugmentedCommand
CodeHeuristic = common_runner.CodeHeuristic
Violation = common_runner.Violation


# ============================================================================
# CLEAN CODE RULE - Language Detection and Specialization
# ============================================================================

class CleanCodeRule(FrameworkSpecializingRule):
    """Rule handler for clean code principles with language-specific specialization"""
    
    def __init__(self, base_rule_file_name: str = 'clean-code-rule.mdc'):
        super().__init__(base_rule_file_name)
    
    @staticmethod
    def detect_framework_from_file(file_path: str) -> Optional[str]:
        """
        Detect language from file extension.
        Returns: 'python' or 'javascript'
        """
        path_obj = Path(file_path)
        file_extension = path_obj.suffix.lower()
        
        if file_extension in ['.py', '.pyi']:
            return 'python'
        elif file_extension in ['.js', '.mjs', '.ts', '.tsx', '.jsx']:
            return 'javascript'
        
        return None
    
    def load_framework_rule_file(self, framework: str) -> Optional[Dict[str, Any]]:
        """
        Load language-specific rule file.
        framework: 'python' or 'javascript'
        """
        rule_files = {
            'python': 'clean-code-python-rule.mdc',
            'javascript': 'clean-code-js-rule.mdc'
        }
        
        rule_file = rule_files.get(framework)
        if not rule_file:
            return None
        
        rule_path = Path("behaviors/clean-code") / rule_file
        if not rule_path.exists():
            return None
        
        content = rule_path.read_text(encoding='utf-8')
        
        return {
            "rule_path": str(rule_path),
            "content": content,
            "framework": framework
        }


# ============================================================================
# HEURISTICS - Static Analysis Checks
# ============================================================================

class DeepNestingHeuristic(CodeHeuristic):
    """Detect deep nesting (>3 levels)"""
    
    def __init__(self):
        super().__init__("deep_nesting")
    
    def detect_violations(self, content: Content) -> Optional[List[Violation]]:
        """Detect excessive nesting depth"""
        if not content._content_lines:
            return None
        
        violations = []
        nesting_keywords = ['if', 'for', 'while', 'try', 'with', 'switch', 'catch']
        
        for i, line in enumerate(content._content_lines, 1):
            indent = len(line) - len(line.lstrip())
            stripped = line.strip()
            
            if any(stripped.startswith(keyword) for keyword in nesting_keywords):
                # Detect indent unit (2 or 4 spaces)
                indent_unit = 4 if indent >= 8 and indent % 4 == 0 else 2
                depth = indent // indent_unit
                
                if depth >= 7:
                    violations.append(Violation(
                        line=i,
                        severity='critical',
                        principle='1.4 Simple Control Flow',
                        message=f'Excessive nesting (depth {depth})',
                        suggestion='Extract nested blocks into separate functions; use guard clauses',
                        code_snippet=content.get_code_snippet(i, 3)
                    ))
                elif depth >= 4:
                    violations.append(Violation(
                        line=i,
                        severity='important',
                        principle='1.4 Simple Control Flow',
                        message=f'Deep nesting (depth {depth})',
                        suggestion='Consider extracting nested logic or using guard clauses',
                        code_snippet=content.get_code_snippet(i, 3)
                    ))
                elif depth == 3:
                    violations.append(Violation(
                        line=i,
                        severity='suggested',
                        principle='1.4 Simple Control Flow',
                        message=f'Moderate nesting (depth {depth})',
                        suggestion='Consider simplifying if adding more complexity',
                        code_snippet=content.get_code_snippet(i, 3)
                    ))
        
        return violations if violations else None


class MagicNumberHeuristic(CodeHeuristic):
    """Detect magic numbers (unexplained numeric literals)"""
    
    def __init__(self):
        super().__init__("magic_numbers")
    
    def detect_violations(self, content: Content) -> Optional[List[Violation]]:
        """Detect magic numbers in code"""
        if not content._content_lines:
            return None
        
        violations = []
        
        for i, line in enumerate(content._content_lines, 1):
            # Skip comments and strings
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//'):
                continue
            
            # Find numeric literals (2+ digits)
            if re.search(r'[^a-zA-Z_0-9]\d{2,}', line):
                # Ignore common patterns
                if not re.search(r'(range\(|sleep\(|setTimeout\(|version|20\d{2}|line|column)', line, re.IGNORECASE):
                    violations.append(Violation(
                        line=i,
                        severity='important',
                        principle='2.3 Meaningful Context',
                        message='Magic number detected',
                        suggestion='Replace with named constant',
                        code_snippet=content.get_code_snippet(i, 2)
                    ))
        
        return violations if violations else None


class SingleLetterVariableHeuristic(CodeHeuristic):
    """Detect single-letter variables (not in loops)"""
    
    def __init__(self):
        super().__init__("single_letter_vars")
    
    def detect_violations(self, content: Content) -> Optional[List[Violation]]:
        """Detect single-letter variable names"""
        if not content._content_lines:
            return None
        
        violations = []
        
        for i, line in enumerate(content._content_lines, 1):
            # Match single-letter variables (d-z, excluding common loop counters i,j,k)
            if re.search(r'\b([d-z])\s*=\s*', line):
                # Ignore loop counters
                if not re.search(r'\bfor\s+\w+\s+in\b', line) and not re.search(r'for\s*\(\s*\w+\s*=', line):
                    violations.append(Violation(
                        line=i,
                        severity='suggested',
                        principle='2.1 Intention-Revealing Names',
                        message='Single-letter variable name',
                        suggestion='Use descriptive name that reveals intent',
                        code_snippet=content.get_code_snippet(i, 2)
                    ))
        
        return violations if violations else None


class CommentedCodeHeuristic(CodeHeuristic):
    """Detect commented-out code"""
    
    def __init__(self):
        super().__init__("commented_code")
    
    def detect_violations(self, content: Content) -> Optional[List[Violation]]:
        """Detect commented-out code blocks"""
        if not content._content_lines:
            return None
        
        violations = []
        
        for i, line in enumerate(content._content_lines, 1):
            # Python or JavaScript commented code patterns
            if re.search(r'^\s*#.*\b(def|class|import|return)\b', line) or \
               re.search(r'^\s*//.*\b(function|const|import|return)\b', line):
                violations.append(Violation(
                    line=i,
                    severity='important',
                    principle='7.3 Bad Comments',
                    message='Commented-out code detected',
                    suggestion="Remove (it's in git history)",
                    code_snippet=content.get_code_snippet(i, 2)
                ))
        
        return violations if violations else None


class LargeFunctionHeuristic(CodeHeuristic):
    """Detect large functions"""
    
    def __init__(self):
        super().__init__("large_functions")
    
    def detect_violations(self, content: Content) -> Optional[List[Violation]]:
        """Detect functions that are too large"""
        if not content._content_lines:
            return None
        
        violations = []
        functions = extract_functions_from_content(content)
        
        for func in functions:
            if func['length'] > 50:
                violations.append(Violation(
                    line=func['start_line'],
                    severity='critical',
                    principle='1.2 Small and Focused Functions',
                    message=f"Function '{func['name']}' is too large ({func['length']} lines)",
                    suggestion='Extract into smaller, focused functions',
                    code_snippet=content.get_code_snippet(func['start_line'], 3)
                ))
            elif func['length'] > 20:
                violations.append(Violation(
                    line=func['start_line'],
                    severity='important',
                    principle='1.2 Small and Focused Functions',
                    message=f"Function '{func['name']}' is large ({func['length']} lines)",
                    suggestion='Consider extracting helper functions',
                    code_snippet=content.get_code_snippet(func['start_line'], 3)
                ))
        
        return violations if violations else None


class TooManyParametersHeuristic(CodeHeuristic):
    """Detect functions with too many parameters"""
    
    def __init__(self):
        super().__init__("too_many_parameters")
    
    def detect_violations(self, content: Content) -> Optional[List[Violation]]:
        """Detect functions with >3 parameters"""
        if not content._content_lines:
            return None
        
        violations = []
        functions = extract_functions_from_content(content)
        
        for func in functions:
            if func['param_count'] > 3:
                violations.append(Violation(
                    line=func['start_line'],
                    severity='important',
                    principle='1.3 Clear Parameters',
                    message=f"Function '{func['name']}' has {func['param_count']} parameters",
                    suggestion='Use parameter object or split function',
                    code_snippet=content.get_code_snippet(func['start_line'], 3)
                ))
        
        return violations if violations else None


class LargeClassHeuristic(CodeHeuristic):
    """Detect large classes"""
    
    def __init__(self):
        super().__init__("large_classes")
    
    def detect_violations(self, content: Content) -> Optional[List[Violation]]:
        """Detect classes that are too large"""
        if not content._content_lines:
            return None
        
        violations = []
        classes = extract_classes_from_content(content)
        
        for cls in classes:
            if cls['length'] > 300:
                violations.append(Violation(
                    line=cls['start_line'],
                    severity='critical',
                    principle='6.2 Small and Compact Classes',
                    message=f"Class '{cls['name']}' is too large ({cls['length']} lines)",
                    suggestion='Split into smaller, focused classes',
                    code_snippet=content.get_code_snippet(cls['start_line'], 3)
                ))
            elif cls['length'] > 200:
                violations.append(Violation(
                    line=cls['start_line'],
                    severity='important',
                    principle='6.2 Small and Compact Classes',
                    message=f"Class '{cls['name']}' is large ({cls['length']} lines)",
                    suggestion='Consider splitting responsibilities',
                    code_snippet=content.get_code_snippet(cls['start_line'], 3)
                ))
        
        return violations if violations else None


# ============================================================================
# CODE STRUCTURE EXTRACTION UTILITIES
# ============================================================================

def extract_functions_from_content(content: Content) -> List[Dict[str, Any]]:
    """
    Extract all functions from content with their structure.
    Returns: [{"name": str, "start_line": int, "end_line": int, "length": int, "param_count": int}]
    """
    if not content._content_lines:
        return []
    
    functions = []
    language = 'python' if content.file_extension == '.py' else 'javascript'
    
    for i, line in enumerate(content._content_lines, 1):
        func_name = None
        params = ''
        
        if language == 'python':
            match = re.search(r'^\s*def\s+(\w+)\s*\(([^)]*)\)', line)
            if match:
                func_name = match.group(1)
                params = match.group(2)
        else:  # javascript
            # Try multiple patterns
            match = re.search(r'^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)', line)
            if not match:
                match = re.search(r'^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>', line)
            if not match:
                match = re.search(r'^\s*(\w+)\s*\(([^)]*)\)\s*{', line)
            
            if match:
                func_name = match.group(1)
                params = match.group(2)
        
        if func_name:
            param_count = len([p.strip() for p in params.split(',') if p.strip()])
            
            # Find function end (approximate)
            func_start = i
            indent = len(line) - len(line.lstrip())
            func_end = i
            
            # Find end of function (next line with same or less indent that starts something new)
            for j in range(i, min(i + 200, len(content._content_lines))):
                next_line = content._content_lines[j]
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # Found next function or class at same/lower indent
                if j > i and next_indent <= indent and next_line.strip():
                    if re.search(r'^\s*(?:def|class|function|const|let|var)\s+', next_line):
                        func_end = j
                        break
            else:
                func_end = min(i + 100, len(content._content_lines))
            
            functions.append({
                'name': func_name,
                'start_line': func_start,
                'end_line': func_end,
                'length': func_end - func_start,
                'param_count': param_count
            })
    
    return functions


def extract_classes_from_content(content: Content) -> List[Dict[str, Any]]:
    """
    Extract all classes from content.
    Returns: [{"name": str, "start_line": int, "length": int}]
    """
    if not content._content_lines:
        return []
    
    classes = []
    language = 'python' if content.file_extension == '.py' else 'javascript'
    
    if language == 'python':
        pattern = r'^\s*class\s+(\w+)'
    else:  # javascript
        pattern = r'^\s*(?:export\s+)?class\s+(\w+)'
    
    for i, line in enumerate(content._content_lines, 1):
        match = re.search(pattern, line)
        if match:
            class_name = match.group(1)
            class_start = i
            indent = len(line) - len(line.lstrip())
            
            # Find class end
            class_end = i
            for j in range(i, min(i + 500, len(content._content_lines))):
                next_line = content._content_lines[j]
                next_indent = len(next_line) - len(next_line.lstrip())
                
                if j > i and next_indent <= indent and next_line.strip():
                    if re.search(r'^\s*class\s+', next_line):
                        class_end = j
                        break
            else:
                class_end = min(i + 500, len(content._content_lines))
            
            classes.append({
                'name': class_name,
                'start_line': class_start,
                'length': class_end - class_start
            })
    
    return classes


# ============================================================================
# CLEAN CODE COMMAND
# ============================================================================

class CleanCodeCommand:
    """
    Clean code validation and improvement command.
    
    Actions:
    - generate: Analyze code and generate violations report
    - validate: Validate generated report against rules
    - correct: Apply fixes based on validated violations
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.rule = CleanCodeRule()
        
        # Detect language and load rule
        language = self.rule.detect_framework_from_file(file_path)
        if not language:
            raise ValueError(f"Unsupported file type: {file_path}")
        
        # Load rule content
        rule_data = self.rule.load_framework_rule_file(language)
        if not rule_data:
            raise ValueError(f"Could not load rules for {language}")
        
        self.language = language
        self.rule_data = rule_data
        
        # Create content object
        file_ext = Path(file_path).suffix
        with open(file_path, 'r', encoding='utf-8') as f:
            content_lines = f.readlines()
        
        self.content = Content(
            file_path=file_path,
            file_extension=file_ext,
            content_lines=content_lines
        )
    
    def get_heuristics(self) -> List[CodeHeuristic]:
        """Return list of heuristic functions for static analysis"""
        return [
            DeepNestingHeuristic(),
            MagicNumberHeuristic(),
            SingleLetterVariableHeuristic(),
            CommentedCodeHeuristic(),
            LargeFunctionHeuristic(),
            TooManyParametersHeuristic(),
            LargeClassHeuristic()
        ]
    
    def action_generate(self, **kwargs) -> Dict[str, Any]:
        """
        Generate violations report for code file.
        
        Steps:
        1. Detect language
        2. Load specialized rule
        3. Extract code structure
        4. Run heuristics
        5. Present to AI for deeper semantic analysis
        6. Generate violations report
        """
        print("=" * 80)
        print("CLEAN CODE - GENERATE VIOLATIONS REPORT")
        print("=" * 80)
        print(f"\nFile: {self.file_path}\n")
        print(f"✅ Detected language: {self.language.upper()}")
        print(f"✅ Loaded rule: {self.rule_data['rule_path']}\n")
        
        # Extract code structure
        print("Extracting code structure...")
        functions = extract_functions_from_content(self.content)
        classes = extract_classes_from_content(self.content)
        print(f"✅ Found {len(functions)} functions, {len(classes)} classes\n")
        
        # Run heuristics
        print("Running heuristics (static analysis)...")
        heuristic_violations = []
        for heuristic in self.get_heuristics():
            violations = heuristic.detect_violations(self.content)
            if violations:
                heuristic_violations.extend(violations)
        
        print(f"✅ Heuristics detected {len(heuristic_violations)} violations\n")
        
        # Present to AI for deeper analysis
        print("=" * 80)
        print("AI AGENT: PERFORM DEEP SEMANTIC ANALYSIS")
        print("=" * 80)
        print("\n📋 RULE FILE:")
        print("=" * 80)
        print(self.rule_data['content'])
        print("=" * 80)
        
        print("\n📊 CODE STRUCTURE:")
        print(f"  Functions: {len(functions)}")
        print(f"  Classes: {len(classes)}")
        print(f"  Total lines: {len(self.content._content_lines)}")
        
        print("\n⚠️  HEURISTIC VIOLATIONS:")
        for v in heuristic_violations:
            print(f"\n  Line {v.line} [{v.severity.upper()}]: {v.message}")
            print(f"  Principle: {v.principle}")
            print(f"  Suggestion: {v.suggestion}")
        
        print("\n" + "=" * 80)
        print("TASK: Generate Complete Violations Report")
        print("=" * 80)
        print("\n1. Review ALL code against clean code principles")
        print("2. Go beyond heuristics - find semantic issues:")
        print("   - Single Responsibility violations")
        print("   - Side effects mixed with pure logic")
        print("   - Poor encapsulation")
        print("   - Code duplication")
        print("   - Unclear naming")
        print("   - Mixed abstraction levels")
        print("\n3. Generate violations report (JSON):")
        print("""
{
  "file": "path/to/file",
  "language": "python|javascript",
  "violations": [
    {
      "line": 42,
      "function": "function_name",
      "severity": "critical|important|suggested",
      "principle": "X.Y Principle Name",
      "issue": "Specific description of what's wrong",
      "suggestion": "Actionable fix"
    }
  ],
  "summary": {
    "critical": N,
    "important": N,
    "suggested": N,
    "total": N
  }
}
""")
        print("=" * 80)
        
        return {
            "file": self.file_path,
            "language": self.language,
            "rule": self.rule_data['rule_path'],
            "functions": len(functions),
            "classes": len(classes),
            "heuristic_violations": len(heuristic_violations),
            "status": "awaiting_ai_analysis"
        }
    
    def action_validate(self, **kwargs) -> Dict[str, Any]:
        """
        Validate generated violations report.
        
        Checks each violation for:
        - Correct identification
        - Appropriate severity
        - Actionable suggestions
        """
        print("=" * 80)
        print("CLEAN CODE - VALIDATE VIOLATIONS REPORT")
        print("=" * 80)
        
        # Load generated violations report
        violations_file = Path(self.file_path).stem + "-clean-code-violations.json"
        if not Path(violations_file).exists():
            return {"error": f"Violations report not found: {violations_file}"}
        
        with open(violations_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        print(f"\nValidating report for: {report['file']}")
        print(f"Total violations: {report['summary']['total']}\n")
        
        print("=" * 80)
        print("AI AGENT: VALIDATE EACH VIOLATION")
        print("=" * 80)
        print("\n📋 RULE FILE (for reference):")
        print(self.rule_data['content'][:1000] + "...\n")
        
        print("VIOLATIONS TO VALIDATE:")
        for v in report['violations']:
            print(f"\n  Line {v['line']} [{v['severity'].upper()}]")
            print(f"  Principle: {v['principle']}")
            print(f"  Issue: {v['issue']}")
            print(f"  Suggestion: {v['suggestion']}")
        
        print("\n" + "=" * 80)
        print("VALIDATION CHECKLIST:")
        print("=" * 80)
        print("\nFor each violation, check:")
        print("1. Is it correctly identified?")
        print("2. Does it truly violate the stated principle?")
        print("3. Is severity appropriate?")
        print("4. Is suggestion actionable?")
        print("\nIdentify:")
        print("- False positives")
        print("- Incorrect principle attribution")
        print("- Missing context")
        print("- Severity mismatches")
        print("\nOutput validation feedback with corrections needed.")
        print("=" * 80)
        
        return {
            "file": file_path,
            "report": violations_file,
            "violations_count": report['summary']['total'],
            "status": "awaiting_validation"
        }
    
    def action_correct(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Apply corrections to violations report based on validation.
        """
        print("=" * 80)
        print("CLEAN CODE - CORRECT VIOLATIONS REPORT")
        print("=" * 80)
        
        violations_file = Path(file_path).stem + "-clean-code-violations.json"
        
        print(f"\nApplying corrections to: {violations_file}")
        print("\n" + "=" * 80)
        print("AI AGENT: APPLY CORRECTIONS")
        print("=" * 80)
        print("\n1. Remove false positives")
        print("2. Adjust severities as indicated by validation")
        print("3. Improve suggestions where needed")
        print("4. Ensure correct principle attribution")
        print("\nOutput final corrected violations report.")
        print("=" * 80)
        
        return {
            "file": file_path,
            "report": violations_file,
            "status": "awaiting_corrections"
        }


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for clean-code command"""
    
    if len(sys.argv) < 2:
        print("Usage: clean-code-runner.py <file> [--action generate|validate|correct]")
        print("\nExamples:")
        print("  clean-code-runner.py src/module.py")
        print("  clean-code-runner.py src/module.py --action generate")
        print("  clean-code-runner.py src/module.py --action validate")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Parse action
    action = "generate"  # default
    if "--action" in sys.argv:
        action_index = sys.argv.index("--action")
        if action_index + 1 < len(sys.argv):
            action = sys.argv[action_index + 1]
    
    # Create command and execute action
    command = CleanCodeCommand()
    
    if action == "generate":
        result = command.action_generate(file_path)
    elif action == "validate":
        result = command.action_validate(file_path)
    elif action == "correct":
        result = command.action_correct(file_path)
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
    
    if "error" in result:
        print(f"\n❌ Error: {result['error']}")
        sys.exit(1)
    
    print("\n✅ Complete")
    sys.exit(0)


if __name__ == "__main__":
    # Fix Windows console encoding for emoji support
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    main()

