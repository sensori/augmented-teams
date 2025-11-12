"""
BDD Workflow - Test-Code Cycle
Guides developers through true BDD (Behavior-Driven Development) with Test-Code cycle.

Division of Labor:
- Code: Parse files, run tests, track state, identify relationships, ENFORCE workflow
- AI Agent: 
  * Identify SAMPLE SIZE (lowest-level describe block, ~18 tests)
  * Write test signatures/implementations
  * Run /bdd-validate after EVERY step
  * Fix ALL violations before proceeding
  * Learn from violations and iterate

CODE ENFORCEMENT:
- Check run state before/after every step
- Block if run not complete (started → ai_verified → human_approved → completed)
- Validate AI ran /bdd-validate
- Require human approval
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import sys
# RunStatus and StepType are now imported from common_command_runner
common_runner_path = Path(__file__).parent.parent / "common_command_runner" / "common_command_runner.py"
import importlib.util
spec = importlib.util.spec_from_file_location("common_command_runner", common_runner_path)
common_runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common_runner)

# Import needed classes
Content = common_runner.Content
BaseRule = common_runner.BaseRule
FrameworkSpecializingRule = common_runner.FrameworkSpecializingRule
SpecializedRule = common_runner.SpecializedRule
Command = common_runner.Command
SpecializingRuleCommand = common_runner.SpecializingRuleCommand
CodeAugmentedCommand = common_runner.CodeAugmentedCommand
IncrementalCommand = common_runner.IncrementalCommand
WorkflowPhaseCommand = common_runner.WorkflowPhaseCommand
Workflow = common_runner.Workflow
CodeHeuristic = common_runner.CodeHeuristic
Violation = common_runner.Violation
RunStatus = common_runner.RunStatus
StepType = common_runner.StepType


class BDDRule(FrameworkSpecializingRule):
    
    def __init__(self, base_rule_file_name: str = 'bdd-rule.mdc'):
        super().__init__(base_rule_file_name)
    
    @staticmethod
    def detect_framework_from_file(file_path: str) -> Optional[str]:
        path_obj = Path(file_path)
        file_extension = path_obj.suffix.lower()
        
        if file_extension == '.py':
            return 'mamba'
        elif file_extension in ['.js', '.ts', '.jsx', '.tsx', '.mjs']:
            return 'jest'
        
        return None
    
    def load_framework_rule_file(self, framework: str) -> Optional[Dict[str, Any]]:
        rule_files = {
            'jest': 'bdd-jest-rule.mdc',
            'mamba': 'bdd-mamba-rule.mdc'
        }
        
        rule_file = rule_files.get(framework)
        if not rule_file:
            return None
        
        rule_path = Path("behaviors/bdd") / rule_file
        if not rule_path.exists():
            return None
        
        content = rule_path.read_text(encoding='utf-8')
        
        return {
            "rule_path": str(rule_path),
            "content": content,
            "framework": framework
        }
    
    def extract_dos_and_donts(self, rule_content: str) -> Dict[str, Dict[str, List[str]]]:
        sections = {}
        current_section = None
        
        lines = rule_content.split('\n')
        for i, line in enumerate(lines):
            section_match = re.match(r'^##\s+(\d+)\.\s+(.+)$', line)
            if section_match:
                section_num = section_match.group(1)
                section_name = section_match.group(2).strip()
                current_section = f"{section_num}. {section_name}"
                sections[current_section] = {"dos": [], "donts": []}
            
            if '**✅ DO:**' in line or '**DO:**' in line:
                code_block = []
                in_code = False
                for j in range(i+1, min(i+50, len(lines))):
                    if lines[j].strip().startswith('```') and not in_code:
                        in_code = True
                        continue
                    elif lines[j].strip().startswith('```') and in_code:
                        break
                    elif in_code:
                        code_block.append(lines[j])
                
                if code_block and current_section:
                    sections[current_section]["dos"].append('\n'.join(code_block))
            
            if '**❌ DON\'T:**' in line or '**DON\'T:**' in line or "**DON'T:**" in line:
                code_block = []
                in_code = False
                for j in range(i+1, min(i+50, len(lines))):
                    if lines[j].strip().startswith('```') and not in_code:
                        in_code = True
                        continue
                    elif lines[j].strip().startswith('```') and in_code:
                        break
                    elif in_code:
                        code_block.append(lines[j])
                
                if code_block and current_section:
                    sections[current_section]["donts"].append('\n'.join(code_block))
        
        return sections


    class BDDJargonHeuristic(CodeHeuristic):
        """Heuristic for §1: Detects technical jargon and missing 'should' in test names"""
        def __init__(self):
            super().__init__("bdd_jargon")
        
        def detect_violations(self, content):
            """Detect violations of Business Readable Language principle"""
            violations = []
            if not hasattr(content, '_content_lines') or not content._content_lines:
                return None
            
            for i, line in enumerate(content._content_lines, 1):
                # Detect technical jargon patterns
                technical_patterns = [
                    r'\b(get|set|is|has|can|will|do)[A-Z]\w+',  # getDescriptor, isActive
                    r'\b[A-Z][a-z]+(Item|Object|Entity|Class|Type|Manager|Handler|Service)',  # PowerItem, UserManager
                    r'\btest_\w+',  # test_getDescriptor
                    r'\bdescribe\([\'"]\w+[A-Z]',  # describe('PowerItem')
                ]
                
                for pattern in technical_patterns:
                    if re.search(pattern, line):
                        violations.append(Violation(i, "Uses technical jargon instead of domain language"))
                        break
                
                # Detect missing "should" in it() blocks
                if re.search(r"with it\(['\"]", line) or re.search(r"it\(['\"]", line):
                    if "should" not in line.lower() and "test_" in line.lower():
                        violations.append(Violation(i, "Test name doesn't start with 'should' and uses technical naming"))
            
            return violations if violations else None
    
    class BDDComprehensiveHeuristic(CodeHeuristic):
        """Heuristic for §2: Detects overly broad tests and internal assertions"""
        def __init__(self):
            super().__init__("bdd_comprehensive")
        
        def detect_violations(self, content):
            """Detect violations of Comprehensive and Brief principle"""
            violations = []
            if not hasattr(content, '_content_lines') or not content._content_lines:
                return None
            
            for i, line in enumerate(content._content_lines, 1):
                # Detect assertions on internal calls/framework logic
                internal_patterns = [
                    r'\.toHaveBeenCalled',  # Jest mock assertions
                    r'\.assert_called',  # Python mock assertions
                    r'\.mock\.',  # Mock internals
                    r'\.spyOn\(',  # Spy creation
                ]
                
                for pattern in internal_patterns:
                    if re.search(pattern, line):
                        violations.append(Violation(i, "Tests internal calls or framework logic instead of observable behavior"))
                        break
            
            return violations if violations else None
    
    class BDDDuplicateCodeHeuristic(CodeHeuristic):
        """Heuristic for §3: Detects duplicate code using string similarity"""
        def __init__(self):
            super().__init__("bdd_duplicate_code")
            try:
                from difflib import SequenceMatcher
                self.SequenceMatcher = SequenceMatcher
            except ImportError:
                self.SequenceMatcher = None
        
        def _calculate_similarity(self, str1: str, str2: str) -> float:
            """Calculate similarity ratio between two strings"""
            if not self.SequenceMatcher:
                # Fallback: simple character overlap
                return len(set(str1) & set(str2)) / max(len(set(str1) | set(str2)), 1)
            return self.SequenceMatcher(None, str1, str2).ratio()
        
        def detect_violations(self, content):
            """Detect violations of Balance Context Sharing principle"""
            violations = []
            if not hasattr(content, '_content_lines') or not content._content_lines:
                return None
            
            # Detect framework to provide framework-specific recommendations
            framework = None
            if hasattr(content, 'file_path') and content.file_path:
                framework = BDDRule.detect_framework_from_file(content.file_path)
            is_mamba = framework == 'mamba'
            
            lines = content._content_lines
            # Look for sibling blocks (3+ consecutive it() or context() blocks)
            sibling_groups = []
            current_group = []
            
            for i, line in enumerate(lines):
                # Detect test blocks
                is_test_block = bool(re.search(r"with it\(|it\(|with context\(|describe\(", line))
                
                if is_test_block:
                    current_group.append((i + 1, line))  # Store line number and content
                else:
                    if len(current_group) >= 3:  # 3+ siblings
                        sibling_groups.append(current_group)
                    current_group = []
            
            # Check last group
            if len(current_group) >= 3:
                sibling_groups.append(current_group)
            
            # For each group, check for duplicate code in bodies
            for group in sibling_groups:
                # Extract bodies (next few lines after each block start)
                bodies = []
                for line_num, line in group:
                    body_lines = []
                    # Get next 5-10 lines as body
                    start_idx = line_num - 1  # Convert to 0-based
                    for j in range(start_idx + 1, min(start_idx + 11, len(lines))):
                        if re.search(r"^\s*(with |it\(|describe\(|})", lines[j]):  # Next block or closing
                            break
                        body_lines.append(lines[j])
                    bodies.append((line_num, '\n'.join(body_lines)))
                
                # Compare bodies for similarity
                for i in range(len(bodies)):
                    for j in range(i + 1, len(bodies)):
                        similarity = self._calculate_similarity(bodies[i][1], bodies[j][1])
                        if similarity > 0.7:  # 70% similarity threshold
                            # Framework-specific violation message
                            if is_mamba:
                                violation_msg = (
                                    f"§ 3 Violation: {len(group)} sibling `it()` blocks with {similarity:.0%} similar Arrange code. "
                                    f"Mamba does NOT support moving `before.each` to parent `describe` blocks. "
                                    f"FIX: Extract duplicate setup to a helper function and call it in each test. "
                                    f"Example: `def setup_common_mocks(context_self): ...` then call `setup_common_mocks(self)` in each test."
                                )
                            else:
                                violation_msg = (
                                    f"§ 3 Violation: {len(group)} sibling blocks with {similarity:.0%} similar Arrange code. "
                                    f"FIX: Move shared Arrange code to `beforeEach()`/`before_each()` in parent context."
                                )
                            
                            violations.append(Violation(
                                bodies[i][0],
                                violation_msg
                            ))
                            break  # Only report once per group
            
            return violations if violations else None
    
    class BDDLayerFocusHeuristic(CodeHeuristic):
        """Heuristic for §4: Detects wrong layer focus (testing dependencies instead of code under test)"""
        def __init__(self):
            super().__init__("bdd_layer_focus")
        
        def detect_violations(self, content):
            """Detect violations of Cover All Layers principle"""
            violations = []
            if not hasattr(content, '_content_lines') or not content._content_lines:
                return None
            
            for i, line in enumerate(content._content_lines, 1):
                # Detect excessive mocking of dependencies
                mock_patterns = [
                    r'mock\(.*\)\.mock',  # Chained mocks
                    r'jest\.mock\(.*\)',  # Jest module mocks
                    r'@patch\(',  # Python decorator mocks
                ]
                
                mock_count = sum(1 for pattern in mock_patterns if re.search(pattern, line))
                if mock_count > 2:  # Too many mocks suggests wrong focus
                    violations.append(Violation(i, "Focuses on dependencies rather than code under test"))
                    break
            
            return violations if violations else None
    
    class BDDFrontEndHeuristic(CodeHeuristic):
        """Heuristic for §5: Detects implementation details in front-end tests"""
        def __init__(self):
            super().__init__("bdd_frontend")
        
        def detect_violations(self, content):
            """Detect violations of Unit Tests Front-End principle"""
            violations = []
            if not hasattr(content, '_content_lines') or not content._content_lines:
                return None
            
            # Only check if this is a front-end test file
            file_path = getattr(content, 'file_path', '')
            if not any(ext in file_path for ext in ['.jsx', '.tsx', '.test.jsx', '.test.tsx', '.spec.jsx', '.spec.tsx']):
                return None  # Not a front-end test
            
            for i, line in enumerate(content._content_lines, 1):
                # Detect implementation detail assertions
                impl_patterns = [
                    r'\.state\.',  # React state access
                    r'\.props\.',  # React props access
                    r'\.instance\(\)',  # Component instance
                    r'\.debug\(\)',  # Debug output
                ]
                
                for pattern in impl_patterns:
                    if re.search(pattern, line):
                        violations.append(Violation(i, "Tests implementation details instead of user-visible behavior"))
                        break
            
            return violations if violations else None

    class BDDUnicodeHeuristic(CodeHeuristic):
        """Heuristic for §10: Detects unicode characters in test code"""
        def __init__(self):
            super().__init__("bdd_unicode")
        
        def detect_violations(self, content):
            """Detect unicode characters in test code"""
            violations = []
            if not hasattr(content, '_content_lines') or not content._content_lines:
                return None
            
            # Common unicode symbols that cause problems
            unicode_symbols = ['✓', '✅', '❌', '→', '←', '↓', '↑', '⚠', '✔', '✖', '►', '◄', '•', '‣', 
                             '🎯', '📂', '⚙️', '📝', '│', '├', '└', '─']  # Added emojis and tree chars
            
            for i, line in enumerate(content._content_lines, 1):
                # Skip comments that are just explaining domain concepts (not actual test code)
                if line.strip().startswith('#') and 'Example:' in line:
                    continue
                
                # Check for any unicode symbols in the line
                for symbol in unicode_symbols:
                    if symbol in line:
                        violations.append(Violation(
                            line_number=i,
                            message=f"Unicode character '{symbol}' in test code (use ASCII alternatives like PASS, SUCCESS, ERROR, Next, or describe in comments not literals)",
                            principle=None
                        ))
                        break  # Only report once per line
            
            return violations if violations else None

class BDDScaffoldBaseHeuristic(CodeHeuristic):
    """Base class for scaffold heuristics - provides common scaffold parsing and domain map utilities"""
    
    def __init__(self, detection_pattern: str):
        super().__init__(detection_pattern)
        self._scaffold_structure_cache = None
        self._domain_map_cache = None
    
    def _validate_content(self, content):
        """Common validation check for scaffold content"""
        if not hasattr(content, '_content_lines') or not content._content_lines:
            return False
        return True
    
    def _get_scaffold_file_path(self, content):
        """Get the scaffold hierarchy file path from content file path"""
        if not content or not hasattr(content, 'file_path'):
            return None
        
        test_path = Path(content.file_path)
        hierarchy_file = test_path.parent / f"{test_path.stem}-hierarchy.txt"
        return hierarchy_file
    
    def _load_scaffold_file(self, content):
        """Load scaffold hierarchy file content if it exists"""
        hierarchy_file = self._get_scaffold_file_path(content)
        if hierarchy_file and hierarchy_file.exists():
            return hierarchy_file.read_text(encoding='utf-8')
        return None
    
    def _parse_scaffold_structure(self, content):
        """Parse scaffold structure into a common format: describe blocks and it statements with hierarchy"""
        if self._scaffold_structure_cache is not None:
            return self._scaffold_structure_cache
        
        if not self._validate_content(content):
            return None
        
        structure = {
            'describe_blocks': [],
            'it_statements': [],
            'max_depth': 0
        }
        
        describe_blocks = []
        
        for i, line in enumerate(content._content_lines, 1):
            stripped = line.lstrip()
            if not stripped:
                continue
            
            indent_level = len(line) - len(stripped)
            structure['max_depth'] = max(structure['max_depth'], indent_level)
            
            # Check if this is a describe block (must use "describe" keyword, not "when")
            if re.match(r'^\s*describe\s+', line, re.IGNORECASE):
                has_that = 'that' in stripped.lower()
                block_info = {
                    'line': i,
                    'indent': indent_level,
                    'has_that': has_that,
                    'has_it_child': False,
                    'text': stripped,
                    'children': []
                }
                describe_blocks.append(block_info)
                structure['describe_blocks'].append(block_info)
            # Also detect "when" as a violation (should be "describe")
            elif re.match(r'^\s*when\s+', line, re.IGNORECASE):
                # This is a violation - scaffold should use "describe" not "when"
                # We'll add this violation through a separate heuristic
                pass
            
            # Check if this is an it statement
            elif re.match(r'^\s*it\s+', line, re.IGNORECASE):
                it_info = {
                    'line': i,
                    'indent': indent_level,
                    'text': stripped,
                    'parent': None
                }
                
                # Find the parent describe block (closest describe with less indent)
                for desc in reversed(describe_blocks):
                    if desc['indent'] < indent_level:
                        desc['has_it_child'] = True
                        desc['children'].append(it_info)
                        it_info['parent'] = desc
                        break
                
                structure['it_statements'].append(it_info)
        
        self._scaffold_structure_cache = structure
        return structure
    
    def _discover_domain_maps(self, content):
        """Discover and load domain maps from the test file directory"""
        if self._domain_map_cache is not None:
            return self._domain_map_cache
        
        if not content or not hasattr(content, 'file_path'):
            return {"found": False, "domain_map": None, "domain_interactions": None}
        
        test_path = Path(content.file_path)
        test_dir = test_path.parent
        
        domain_map = None
        domain_interactions = None
        
        for file_path in test_dir.glob("*domain-map*.txt"):
            domain_map = {
                "path": str(file_path),
                "content": file_path.read_text(encoding='utf-8'),
                "lines": file_path.read_text(encoding='utf-8').split('\n')
            }
            break
        
        for file_path in test_dir.glob("*domain-interactions*.txt"):
            domain_interactions = {
                "path": str(file_path),
                "content": file_path.read_text(encoding='utf-8')
            }
            break
        
        result = {
            "found": domain_map is not None or domain_interactions is not None,
            "domain_map": domain_map,
            "domain_interactions": domain_interactions
        }
        
        self._domain_map_cache = result
        return result
    
    def _calculate_domain_map_depth(self, domain_map):
        """Calculate maximum nesting depth of domain map"""
        if not domain_map or not domain_map.get('lines'):
            return 0
        
        max_depth = 0
        for line in domain_map['lines']:
            if not line.strip():
                continue
            indent_level = len(line) - len(line.lstrip())
            max_depth = max(max_depth, indent_level)
        
        return max_depth
    
    def _calculate_scaffold_depth(self, scaffold_structure):
        """Calculate maximum nesting depth of scaffold"""
        if not scaffold_structure:
            return 0
        return scaffold_structure.get('max_depth', 0)

class BDDScaffoldCodeSyntaxHeuristic(BDDScaffoldBaseHeuristic):
    """Heuristic for §7: Plain English with Test Structure Keywords - detects code syntax violations"""
    def __init__(self):
        super().__init__("bdd_scaffold_code_syntax")
    
    def detect_violations(self, content):
        """Detect code syntax violations in scaffold files"""
        violations = []
        if not self._validate_content(content):
            return None
        
        # Scaffolding should include `describe` and `it` keywords (without parentheses)
        # But should NOT include function call syntax, arrow functions, etc.
        code_syntax_patterns = [
            r'=>',    # Arrow functions
            r'describe\s*\(',  # Function call syntax (describe() - forbidden)
            r'it\s*\(',  # Function call syntax (it() - forbidden)
            r'function\s+\w+\s*\(',  # Function declarations
            r'const\s+\w+\s*=\s*\(',  # Arrow function assignments
            r'class\s+\w+',  # Class declarations
            r'\w+\s*\([^)]*\)\s*=>',  # Arrow function calls
            r'\{\s*\}',  # Empty code blocks
            r'\w+\([^)]*\)\s*\{',  # Function calls with blocks
        ]
        # Note: `describe` and `it` keywords WITHOUT parentheses are allowed (e.g., "describe Character", "it should have stats")
        
        for i, line in enumerate(content._content_lines, 1):
            for pattern in code_syntax_patterns:
                if re.search(pattern, line):
                    violations.append(Violation(i, "Scaffold contains code syntax - must be plain English only"))
                    break
        
        return violations if violations else None

class BDDScaffoldKeywordHeuristic(BDDScaffoldBaseHeuristic):
    """Heuristic for §7: Plain English with Test Structure Keywords - detects use of 'when' instead of 'describe'"""
    def __init__(self):
        super().__init__("bdd_scaffold_keyword")
    
    def detect_violations(self, content):
        """Detect use of 'when' keyword instead of 'describe'"""
        violations = []
        if not self._validate_content(content):
            print(f"[DEBUG BDDScaffoldKeywordHeuristic] Content validation failed")
            return None
        
        print(f"[DEBUG BDDScaffoldKeywordHeuristic] Checking {len(content._content_lines)} lines")
        # Scaffold must use "describe" keyword, not "when"
        for i, line in enumerate(content._content_lines, 1):
            if re.match(r'^\s*when\s+', line, re.IGNORECASE):
                violations.append(Violation(i, "Scaffold uses 'when' instead of 'describe' - must use 'describe [concept] that [state]' format (e.g., 'describe StoryShapeCommand that is generating story map')"))
        
        print(f"[DEBUG BDDScaffoldKeywordHeuristic] Found {len(violations)} violations")
        return violations if violations else []

class BDDScaffoldStructureHeuristic(BDDScaffoldBaseHeuristic):
    """Heuristic for §7: Plain English with Test Structure Keywords - detects describe blocks without it statements"""
    def __init__(self):
        super().__init__("bdd_scaffold_structure")
    
    def detect_violations(self, content):
        """Detect describe blocks without it statements"""
        violations = []
        if not self._validate_content(content):
            return None
        
        # Use common scaffold structure parsing
        scaffold_structure = self._parse_scaffold_structure(content)
        if not scaffold_structure:
            return None
        
        # DISABLED: Top-level organizational describes are valid without direct it statements
        # All describes are valid as long as they eventually have it statements in descendants
        # for desc in scaffold_structure['describe_blocks']:
        #     if not desc['has_it_child']:
        #         # Exception: "with [noun]" describes inherit context and don't need direct it statements
        #         if re.match(r'^\s*describe\s+with\s+', desc['text'], re.IGNORECASE):
        #             continue  # "with [noun]" is valid without direct it statements
        #         
        #         message = f"Describe block without it statement: '{desc['text']}'"
        #         if desc['has_that']:
        #             message += " (CRITICAL: describe blocks with 'that' statements MUST have at least one it statement)"
        #         violations.append(Violation(desc['line'], message))
        
        return violations if violations else None

class BDDScaffoldStateOrientedHeuristic(BDDScaffoldBaseHeuristic):
    """Heuristic for §7: Output Format - Validates describe blocks use state-oriented language (not 'it should' statements)"""
    def __init__(self):
        super().__init__("bdd_scaffold_state_oriented")
    
    def detect_violations(self, content):
        """Check describe blocks for state-oriented language (skip 'it should' statements - all verb forms valid there)"""
        violations = []
        if not self._validate_content(content):
            return None
        
        # Action-oriented patterns in describe blocks (should be state-oriented instead)
        # These patterns suggest completed actions rather than states
        action_patterns = [
            (r'\bthat\s+(\w+ed)\b', "action-oriented past tense"),  # e.g., "that clicked", "that navigated"
            (r'\bis\s+on\s+the\b', "implies navigation action"),     # e.g., "is on the screen"
            (r'\bwent\s+to\b', "navigation action"),                 # e.g., "went to page"
            (r'\bclicked\b', "action verb"),                         # e.g., "that clicked button"
            (r'\bnavigated\b', "action verb"),                       # e.g., "that navigated"
            (r'\bsubmitted\b', "action verb in describe"),           # e.g., "that submitted" (OK in 'it should' but not describe)
        ]
        
        # Valid state patterns (from Section 2) - for reference/suggestions
        # "that has been [past participle]" - completed states
        # "that is being [verb]" - ongoing states
        # "that is [adjective/noun]" - current states
        # "that has [noun]" - possession states
        
        for i, line in enumerate(content._content_lines, 1):
            # Only check describe blocks (skip 'it should' statements)
            if re.match(r'^\s*describe\s+', line, re.IGNORECASE):
                for pattern, description in action_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Suggest state-oriented alternative
                        suggestion = ""
                        if "is on the" in line.lower():
                            suggestion = " - Try: 'screen is displayed' instead of 'is on screen'"
                        elif "navigated" in line.lower():
                            suggestion = " - Try: 'page is displayed' instead of 'navigated to page'"
                        elif "clicked" in line.lower():
                            suggestion = " - Try: state after click (e.g., 'button has been activated')"
                        
                        violations.append(Violation(i, f"Describe block uses {description} - should use state-oriented language (e.g., 'that has been created', 'that is being edited', 'that is displayed'){suggestion}"))
                        break  # Only report first violation per line
        
        return violations if violations else []

class BDDScaffoldExternalFocusHeuristic(BDDScaffoldBaseHeuristic):
    """Heuristic for §7: User-Oriented Flow - detects internal operation focus instead of external state changes"""
    def __init__(self):
        super().__init__("bdd_scaffold_external_focus")
    
    def detect_violations(self, content):
        """Detect internal operation language instead of external state changes"""
        violations = []
        if not self._validate_content(content):
            return None
        
        # Patterns that indicate internal operations focus (should be external state focus)
        internal_patterns = [
            (r'\bReport\b', "Report"),
            (r'\bOperation\b', "Operation"),
            (r'\bProcessing\b', "Processing"),
            (r'\bGenerator\b', "Generator"),
            (r'\bParser\b', "Parser"),
            (r'\bCreator\b', "Creator"),
            (r'\bBuilder\b', "Builder"),
            (r'\bHandler\b', "Handler"),
            (r'\bManager\b', "Manager"),
            (r'\bProcessor\b', "Processor"),
        ]
        
        for i, line in enumerate(content._content_lines, 1):
            # Only check describe blocks
            if re.match(r'^\s*describe\s+', line, re.IGNORECASE):
                for pattern, keyword in internal_patterns:
                    if re.search(pattern, line):
                        violations.append(Violation(i, f"Describe uses internal operation focus ('{keyword}') - should describe external state changes (e.g., 'that has been validated' not 'Validation Report')"))
                        break
        
        return violations if violations else []

class BDDScaffoldSubjectHeuristic(BDDScaffoldBaseHeuristic):
    """Heuristic for §2: Subject Clarity - detects missing subjects in test names"""
    def __init__(self):
        super().__init__("bdd_scaffold_subject")
    
    def detect_violations(self, content):
        """Detect missing subject in test names - checks parent describe blocks for subject"""
        violations = []
        if not self._validate_content(content):
            return None
        
        # Build hierarchy to track parent describe blocks
        describe_stack = []  # Stack of (indent_level, line_number, line_text)
        
        for i, line in enumerate(content._content_lines, 1):
            # Calculate indentation level
            stripped = line.lstrip()
            if not stripped:
                continue
            indent_level = len(line) - len(stripped)
            
            # Update describe stack based on indentation
            while describe_stack and describe_stack[-1][0] >= indent_level:
                describe_stack.pop()
            
            # Check if this is a describe block
            if re.match(r'^\s*describe\s+', line, re.IGNORECASE):
                describe_stack.append((indent_level, i, stripped))
            
            # Check if this is an "it" statement
            if re.match(r'^\s*it\s+should\s+', line, re.IGNORECASE):
                # Check if any parent describe block has a subject (domain concept)
                has_subject = False
                for parent_indent, parent_line_num, parent_text in describe_stack:
                    # Parent describe should have a noun subject (not just keywords)
                    # Look for domain concept patterns after "describe"
                    if re.match(r'^describe\s+[A-Z][a-zA-Z\s]+', parent_text):
                        has_subject = True
                        break
                
                if not has_subject:
                    violations.append(Violation(i, "Test name missing subject - should include domain concept (e.g., 'Character that has been created should...')"))
        
        return violations if violations else None

class BDDScaffoldTechnicalJargonHeuristic(BDDScaffoldBaseHeuristic):
    """Heuristic for §1: Business Readable Language - detects technical jargon in scaffold files"""
    def __init__(self):
        super().__init__("bdd_scaffold_technical_jargon")
    
    def detect_violations(self, content):
        """Detect technical jargon (function/module names) in scaffold files"""
        violations = []
        if not self._validate_content(content):
            return None
        
        # Detect technical jargon (function/module names as describes)
        technical_patterns = [
            r'[A-Z][a-z]+\w*\(',  # Function names like PowerItem()
            r'get[A-Z]\w+\(',  # Getter functions
            r'set[A-Z]\w+\(',  # Setter functions
        ]
        
        for i, line in enumerate(content._content_lines, 1):
            for pattern in technical_patterns:
                if re.search(pattern, line):
                    violations.append(Violation(i, "Scaffold uses technical function/module names - use domain concepts instead"))
                    break
        
        return violations if violations else None

class BDDScaffoldDomainMapAlignmentHeuristic(BDDScaffoldBaseHeuristic):
    """Heuristic for §7: Domain Map Preservation - detects scaffold misalignment with domain map"""
    def __init__(self):
        super().__init__("bdd_scaffold_domain_map_alignment")
    
    def detect_violations(self, content):
        """Detect scaffold misalignment with domain map (nesting depth, concepts)"""
        violations = []
        if not self._validate_content(content):
            return None
        
        # Discover domain maps
        domain_maps = self._discover_domain_maps(content)
        if not domain_maps['found'] or not domain_maps['domain_map']:
            # No domain map found - this is a warning but not a violation
            # (scaffold can be created without domain map, but it's better to have one)
            return None
        
        domain_map = domain_maps['domain_map']
        
        # Parse scaffold structure
        scaffold_structure = self._parse_scaffold_structure(content)
        if not scaffold_structure:
            return None
        
        # Nesting depth check DISABLED - scaffold depth is flexible based on story flow
        # domain_map_depth = self._calculate_domain_map_depth(domain_map)
        # scaffold_depth = self._calculate_scaffold_depth(scaffold_structure)
        
        # Check concept alignment (simplified - could be enhanced)
        # Extract domain concepts from domain map (lines that are not empty and not indented too much)
        domain_concepts = []
        for line in domain_map['lines']:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                indent = len(line) - len(line.lstrip())
                if indent == 0:  # Top-level concepts
                    domain_concepts.append(stripped)
        
        # Extract scaffold concepts (top-level describe blocks)
        scaffold_concepts = []
        for desc in scaffold_structure['describe_blocks']:
            if desc['indent'] == 0:  # Top-level describe blocks
                # Extract concept name (remove "describe" keyword)
                concept_text = desc['text']
                concept_match = re.match(r'describe\s+(.+?)(?:\s+that|$)', concept_text, re.IGNORECASE)
                if concept_match:
                    scaffold_concepts.append(concept_match.group(1).strip())
        
        # Check if scaffold concepts match domain concepts
        if domain_concepts and scaffold_concepts:
            domain_set = set(concept.lower() for concept in domain_concepts)
            scaffold_set = set(concept.lower() for concept in scaffold_concepts)
            
            missing_in_scaffold = domain_set - scaffold_set
            extra_in_scaffold = scaffold_set - domain_set
            
            if missing_in_scaffold:
                violations.append(Violation(1, f"Scaffold missing domain concepts: {', '.join(missing_in_scaffold)}"))
            if extra_in_scaffold:
                violations.append(Violation(1, f"Scaffold has extra concepts not in domain map: {', '.join(extra_in_scaffold)}"))
        
        return violations if violations else None

class BDDScaffoldRule(BDDRule):
    """BDD Rule specifically for scaffolding - injects scaffold-specific heuristics into principles"""
    
    def __init__(self, base_rule_file_name: str = 'bdd-rule.mdc'):
        # Resolve rule file path relative to this file's directory
        if not Path(base_rule_file_name).is_absolute():
            rule_dir = Path(__file__).parent
            base_rule_file_name = str(rule_dir / base_rule_file_name)
        print(f"[DEBUG BDDScaffoldRule] Loading rule from: {base_rule_file_name}")
        super().__init__(base_rule_file_name)
        self._inject_scaffold_heuristics()
        print(f"[DEBUG BDDScaffoldRule] Initialized with {len(self.base_rule.principles)} principles")
    
    @property
    def principles(self):
        """Return principles with injected scaffold heuristics"""
        print(f"[DEBUG BDDScaffoldRule.principles] Returning {len(self.base_rule.principles) if self.base_rule and hasattr(self.base_rule, 'principles') else 0} principles")
        return self.base_rule.principles if self.base_rule and hasattr(self.base_rule, 'principles') else []
    
    def _inject_scaffold_heuristics(self):
        """Inject scaffold-specific heuristics into the appropriate principles
        
        CRITICAL: This method wires all scaffold heuristic EXTENSIONS (not the base class) to principles.
        BDDScaffoldBaseHeuristic is NEVER instantiated - it's only a base class providing utilities.
        
        Heuristic Wiring:
        - Principle 1: BDDScaffoldTechnicalJargonHeuristic (scaffold-specific technical jargon detection)
        - Principle 2: BDDScaffoldSubjectHeuristic (scaffold-specific subject clarity detection)
        - Principle 7: All scaffold heuristics:
            * BDDScaffoldCodeSyntaxHeuristic (detects code syntax violations)
            * BDDScaffoldKeywordHeuristic (detects "when" instead of "describe")
            * BDDScaffoldStructureHeuristic (detects describe blocks without it statements, allows "with" pattern)
            * BDDScaffoldStateOrientedHeuristic (DISABLED - all verb forms are valid)
            * BDDScaffoldExternalFocusHeuristic (detects internal operation focus - Report, Generator, Parser, etc.)
            * BDDScaffoldDomainMapAlignmentHeuristic (validates domain map alignment)
        
        All scaffold heuristics extend BDDScaffoldBaseHeuristic which provides common utilities
        but is never instantiated directly.
        """
        for principle in self.base_rule.principles:
            if principle.principle_number == 1:
                # Section 1: Add scaffold-specific technical jargon heuristic
                if not hasattr(principle, 'heuristics') or not principle.heuristics:
                    principle.heuristics = []
                principle.heuristics.append(BDDScaffoldTechnicalJargonHeuristic())
            
            elif principle.principle_number == 2:
                # Section 2: Add scaffold-specific subject clarity heuristic
                if not hasattr(principle, 'heuristics') or not principle.heuristics:
                    principle.heuristics = []
                principle.heuristics.append(BDDScaffoldSubjectHeuristic())
            
            elif principle.principle_number == 7:
                # Section 7: Add all scaffold-specific heuristics
                if not hasattr(principle, 'heuristics') or not principle.heuristics:
                    principle.heuristics = []
                principle.heuristics.extend([
                    BDDScaffoldCodeSyntaxHeuristic(),
                    BDDScaffoldKeywordHeuristic(),  # Detect "when" instead of "describe"
                    BDDScaffoldStructureHeuristic(),
                    BDDScaffoldStateOrientedHeuristic(),  # DISABLED
                    BDDScaffoldExternalFocusHeuristic(),  # User-oriented flow and external state changes
                    BDDScaffoldDomainMapAlignmentHeuristic(),  # Domain map preservation validation
                ])

class BDDCommand(CodeAugmentedCommand):
    
    def __init__(self, content: Content, base_rule_file_name: str = 'bdd-rule.mdc'):
        self.rule = BDDRule(base_rule_file_name)
        
        inner_command = Command(content, self.rule.base_rule)
        
        super().__init__(inner_command, self.rule.base_rule)
    
    def _get_heuristic_map(self):
        return {
            1: BDDRule.BDDJargonHeuristic,
            2: BDDRule.BDDComprehensiveHeuristic,
            3: BDDRule.BDDDuplicateCodeHeuristic,
            4: BDDRule.BDDLayerFocusHeuristic,
            5: BDDRule.BDDFrontEndHeuristic,
            10: BDDRule.BDDUnicodeHeuristic,
            # Note: Scaffold-specific heuristics are injected by BDDScaffoldRule, not mapped here
        }
    
    def run(self, test_file_path: Optional[str] = None, framework: Optional[str] = None, single_test_line: Optional[int] = None) -> Dict[str, Any]:
        """
        Run tests for the test file associated with this command.
        Detects framework from specializing rule if available, otherwise from file extension.
        
        Args:
            test_file_path: Path to test file (if None, uses self.content.file_path)
            framework: Framework to use ('mamba' or 'jest'). If None, auto-detects from file or specializing rule
            single_test_line: If provided, run only test at this line
        
        Returns: {"success": bool, "output": str, "passed": int, "failed": int, "error": Optional[str]}
        """
        # Determine test file path
        if test_file_path is None:
            test_file_path = self.content.file_path if hasattr(self.content, 'file_path') else None
        
        if not test_file_path:
            return {"success": False, "error": "No test file path provided", "output": "", "passed": 0, "failed": 0}
        
        # Detect framework if not provided
        if framework is None:
            # First, try to detect from specializing rule
            framework = self._detect_framework_from_specializing_rule()
            
            # If not found in specializing rule, detect from file extension
            if framework is None:
                framework = BDDRule.detect_framework_from_file(test_file_path)
        
        if framework is None:
            return {"success": False, "error": "Could not detect framework. Please specify 'mamba' or 'jest'", "output": "", "passed": 0, "failed": 0}
        
        # Run tests using BDDWorkflow.run_tests
        return BDDWorkflow.run_tests(test_file_path, framework, single_test_line)
    
    def _detect_framework_from_specializing_rule(self) -> Optional[str]:
        """
        Detect framework from specializing rule if one is loaded.
        Checks if bdd-mamba-rule.mdc or bdd-jest-rule.mdc is loaded.
        """
        # Check if rule has specialized_rules dict with framework-specific rules loaded
        if hasattr(self.rule, 'specialized_rules') and self.rule.specialized_rules:
            # Check for mamba or jest specialized rules
            if 'mamba' in self.rule.specialized_rules:
                return 'mamba'
            elif 'jest' in self.rule.specialized_rules:
                return 'jest'
        
        # Also check if we can detect from content file extension
        if hasattr(self.content, 'file_extension'):
            return BDDRule.detect_framework_from_file(self.content.file_path if hasattr(self.content, 'file_path') else '')
        
        return None

class BDDScaffoldCommand(BDDCommand):
    """BDD Command specifically for scaffolding - uses BDDScaffoldRule instead of BDDRule"""
    
    def __init__(self, content: Content, base_rule_file_name: str = 'bdd-rule.mdc'):
        # Use BDDScaffoldRule instead of BDDRule
        self.rule = BDDScaffoldRule(base_rule_file_name)
        
        inner_command = Command(content, self.rule.base_rule)
        
        # Call CodeAugmentedCommand directly (not BDDCommand) to avoid double initialization
        # CRITICAL: Use self.rule (with injected heuristics) not self.rule.base_rule (without them)
        CodeAugmentedCommand.__init__(self, inner_command, self.rule)
    
    def run(self, test_file_path: Optional[str] = None, framework: Optional[str] = None, single_test_line: Optional[int] = None) -> Dict[str, Any]:
        """
        Run method is not implemented for scaffold command.
        Scaffold phase does not run tests.
        """
        return {"success": False, "error": "Run method not implemented for scaffold command. Scaffold phase does not run tests.", "output": "", "passed": 0, "failed": 0}
    
    def _get_heuristic_map(self):
        # BDDScaffoldRule injects heuristics directly into principles, so we don't need a heuristic map here
        # But we still need the base heuristics for non-scaffold validation
        return {
            1: BDDRule.BDDJargonHeuristic,
            2: BDDRule.BDDComprehensiveHeuristic,
            3: BDDRule.BDDDuplicateCodeHeuristic,
            4: BDDRule.BDDLayerFocusHeuristic,
            5: BDDRule.BDDFrontEndHeuristic,
            10: BDDRule.BDDUnicodeHeuristic,
            # Scaffold-specific heuristics are injected by BDDScaffoldRule._inject_scaffold_heuristics()
        }
    
    def _load_heuristics(self):
        """Override to preserve scaffold-specific heuristics injected by BDDScaffoldRule"""
        # BDDScaffoldRule already injected scaffold-specific heuristics into principles 1, 2, and 7
        # For scaffold validation, we use ONLY scaffold-specific heuristics for principles 1, 2, and 7
        # Base heuristics are only added for principles that don't have scaffold heuristics (3, 4, 5, 10)
        heuristic_map = self._get_heuristic_map()
        if not heuristic_map:
            return
        
        # Principles that have scaffold-specific heuristics (should NOT get base heuristics)
        scaffold_principle_numbers = {1, 2, 7}
        
        for principle in self.base_rule.principles:
            heuristic_class = heuristic_map.get(principle.principle_number)
            if heuristic_class:
                # Initialize heuristics list if it doesn't exist
                if not hasattr(principle, 'heuristics') or not principle.heuristics:
                    principle.heuristics = []
                
                # Skip adding base heuristics for principles that have scaffold-specific heuristics
                # These principles (1, 2, 7) should ONLY use scaffold heuristics for scaffold validation
                if principle.principle_number in scaffold_principle_numbers:
                    # Verify scaffold heuristics are present (they should be from BDDScaffoldRule injection)
                    has_scaffold_heuristic = any(
                        isinstance(h, (BDDScaffoldTechnicalJargonHeuristic, BDDScaffoldSubjectHeuristic,
                                     BDDScaffoldCodeSyntaxHeuristic, BDDScaffoldKeywordHeuristic,
                                     BDDScaffoldStructureHeuristic, BDDScaffoldStateOrientedHeuristic,
                                     BDDScaffoldExternalFocusHeuristic, BDDScaffoldDomainMapAlignmentHeuristic))
                        for h in principle.heuristics
                    )
                    if not has_scaffold_heuristic:
                        print(f"[WARNING] Principle {principle.principle_number} should have scaffold heuristics but none found")
                    # Skip adding base heuristic - scaffold heuristics take precedence
                    continue
                
                # For principles without scaffold heuristics (3, 4, 5, 10), add base heuristics
                # Check if base heuristic already exists
                base_heuristic_exists = any(
                    isinstance(h, heuristic_class) for h in principle.heuristics
                )
                if not base_heuristic_exists:
                    principle.heuristics.append(heuristic_class())
    
    def correct(self, chat_context: str) -> str:
        """
        Correct scaffold file based on validation errors and chat context.
        Overrides base Command.correct() to correct scaffold content, not rules.
        """
        scaffold_file_path = self.content.file_path if hasattr(self.content, 'file_path') else None
        
        if not scaffold_file_path or not Path(scaffold_file_path).exists():
            return f"[ERROR] Scaffold file not found: {scaffold_file_path}"
        
        # Get validation errors first
        validation_result = self.validate()
        violations = getattr(self, 'violations', [])
        
        # Read current scaffold content
        scaffold_content = Path(scaffold_file_path).read_text(encoding='utf-8')
        
        # Build correction instructions for AI
        instructions = f"""You are correcting a BDD scaffold hierarchy file based on validation errors and chat context.

**SCAFFOLD FILE:** {scaffold_file_path}

**CHAT CONTEXT:**
{chat_context}

**VALIDATION ERRORS:**
"""
        if violations:
            for v in violations:
                instructions += f"- Line {v.line_number}: {v.message}\n"
        else:
            instructions += "- No validation errors found (correction based on chat context only)\n"
        
        instructions += f"""
**CURRENT SCAFFOLD CONTENT:**
```
{scaffold_content}
```

**YOUR TASK: Correct the Scaffold File**

1. **Read the chat context** - Understand what changes are needed
2. **Review validation errors** - Fix any violations found
3. **Apply corrections** - Update the scaffold to reflect the chat context requirements
4. **Ensure BDD compliance** - Follow BDD principles from Sections 1, 2, and 7:
   - Section 1: Business Readable Language (plain English, domain language, natural sentences)
   - Section 2: Fluency, Hierarchy, and Storytelling (hierarchy patterns, domain map mapping, natural language fluency)
   - Section 7: Scaffold-specific requirements (plain English only, all verb forms valid for 'it should', complete behaviors)

**KEY REQUIREMENTS:**
- Tests should be written from the code's perspective
- Tests should verify what the code generates (prompts/instructions) rather than what AI/human does with them
- Use clear test names: "should [verb]", "should [verb] [noun]", "should have [noun]", "should be [state]" - all forms are valid
- Every describe block must have at least one it statement
- Preserve domain map hierarchy structure

**OUTPUT FORMAT:**
Provide the corrected scaffold content in the same format as the input (plain text hierarchy with indentation).
Do not include explanations or markdown - just the corrected scaffold content.

**CORRECTED SCAFFOLD:**
"""
        
        return instructions
    
    def discover_domain_maps(self) -> Dict[str, Any]:
        """Discover domain maps and domain interaction files in the test file directory"""
        if not self.content or not hasattr(self.content, 'file_path'):
            return {"found": False, "domain_map": None, "interaction_map": None, "domain_interactions": None}
        
        test_path = Path(self.content.file_path)
        test_dir = test_path.parent
        
        domain_map = None
        interaction_map = None
        domain_interactions = None
        
        for file_path in test_dir.glob("*domain-map*.txt"):
            domain_map = {
                "path": str(file_path),
                "content": file_path.read_text(encoding='utf-8')
            }
            break
        
        for file_path in test_dir.glob("*interaction-map*.txt"):
            interaction_map = {
                "path": str(file_path),
                "content": file_path.read_text(encoding='utf-8')
            }
            break
        
        for file_path in test_dir.glob("*domain-interactions*.txt"):
            domain_interactions = {
                "path": str(file_path),
                "content": file_path.read_text(encoding='utf-8')
            }
            break
        
        return {
            "found": domain_map is not None or interaction_map is not None or domain_interactions is not None,
            "domain_map": domain_map,
            "interaction_map": interaction_map,
            "domain_interactions": domain_interactions
        }


class BDDIncrementalCommand(IncrementalCommand):
    
    def __init__(self, inner_command, base_rule, test_file: str, max_sample_size: int = 18):
        # Calculate sample size before calling super().__init__
        calculated_size = self._calculate_sample_size_pre_init(test_file, max_sample_size, base_rule)
        
        # Use calculated size as max_sample_size if available
        effective_max_sample_size = calculated_size if calculated_size is not None else max_sample_size
        
        super().__init__(inner_command, base_rule, effective_max_sample_size, command_file_path=test_file)
        
        self.test_file = test_file
        self.max_sample_size = max_sample_size
    
    def _calculate_sample_size_pre_init(self, test_file: str, max_sample_size: int, base_rule) -> Optional[int]:
        """Calculate sample size before initialization - static version for constructor"""
        if not Path(test_file).exists():
            return None
        
        try:
            content = Content(file_path=test_file)
            framework = base_rule.extract_match_key(content) if hasattr(base_rule, 'extract_match_key') else 'mamba'
            blocks = self.parse_test_structure(test_file, framework)
            
            describe_blocks = [b for b in blocks if b["type"] == "describe"]
            if not describe_blocks:
                it_blocks = [b for b in blocks if b["type"] == "it"]
                count = len(it_blocks)
            else:
                lowest_describe = max(describe_blocks, key=lambda b: b["indent"])
                describe_indent = lowest_describe["indent"]
                describe_line = lowest_describe["line"]
                
                end_line = float('inf')
                for block in blocks:
                    if (block["line"] > describe_line and 
                        block["type"] == "describe" and 
                        block["indent"] <= describe_indent):
                        end_line = block["line"]
                        break
                
                it_blocks = [
                    b for b in blocks 
                    if b["type"] == "it" 
                    and describe_line < b["line"] < end_line
                ]
                count = len(it_blocks)
            
            return min(count, max_sample_size) if count > 0 else None
            
        except Exception:
            return None
    
    @staticmethod
    def _detect_test_implementation(lines: List[str], test_line_index: int, framework: str) -> bool:
        """
        Detect if test has actual implementation or just TODO/empty body.
    
    Args:
            lines: All file lines
            test_line_index: Line number of test (1-indexed)
            framework: 'jest' or 'mamba'
        
        Returns: True if test has implementation, False if signature only
        """
        # Look ahead ~20 lines for test body
        start = test_line_index  # Already 1-indexed, but we need 0-indexed
        end = min(start + 20, len(lines))
        
        test_body_lines = lines[start:end]
        
        # Check for TODO markers
        for line in test_body_lines[:5]:  # Check first few lines
            if 'TODO' in line or 'FIXME' in line or 'BDD: SIGNATURE' in line:
                return False
        
        # Check for empty body (just braces/pass)
        non_empty_lines = [l.strip() for l in test_body_lines if l.strip() and not l.strip().startswith('//')]
        
        if framework == 'jest':
            # Jest: look for actual test code (expect, assertions, etc.)
            has_code = any('expect(' in l or 'assert' in l or 'const ' in l or 'let ' in l 
                           for l in non_empty_lines)
            return has_code
        
        elif framework == 'mamba':
            # Mamba: look for actual test code (expect, assertions, etc.)
            has_code = any('expect(' in l or 'assert' in l or '=' in l 
                           for l in non_empty_lines if not l.startswith('pass'))
            return has_code
        
        return False
    
    @staticmethod
    def parse_test_structure(test_file_path: str, framework: str) -> List[Dict[str, Any]]:
        """
        Parse test file and extract describe/it blocks with status.
        
        Returns: [{"line": int, "type": "describe|it", "text": str, "indent": int, 
                   "status": TestStatus, "has_implementation": bool}]
        """
        content = Path(test_file_path).read_text(encoding='utf-8')
        lines = content.split('\n')
        
        blocks = []
        for i, line in enumerate(lines, 1):
            indent = len(line) - len(line.lstrip())
            
            if framework == 'jest':
                # Extract describe blocks
                if 'describe(' in line:
                    match = re.search(r"describe\(['\"]([^'\"]+)['\"]", line)
                    if match:
                        blocks.append({
                            "line": i,
                            "type": "describe",
                            "text": match.group(1),
                            "indent": indent,
                            "status": None,  # describe blocks don't have status
                            "has_implementation": True  # describes are containers
                        })
                
                # Extract it/test blocks
                elif 'it(' in line or 'test(' in line:
                    match = re.search(r"(?:it|test)\(['\"]([^'\"]+)['\"]", line)
                    if match:
                        # Detect if test has implementation (not just TODO or empty)
                        has_impl = BDDIncrementalCommand._detect_test_implementation(lines, i, framework)
                        status = TestStatus.IMPLEMENTED if has_impl else TestStatus.SIGNATURE
                        
                        blocks.append({
                            "line": i,
                            "type": "it",
                            "text": match.group(1),
                            "indent": indent,
                            "status": status.value,
                            "has_implementation": has_impl
                        })
            
            elif framework == 'mamba':
                # Extract describe blocks (description and context)
                if 'with description(' in line or 'with describe(' in line or 'with context(' in line:
                    match = re.search(r"with (?:description|describe|context)\(['\"]([^'\"]+)['\"]", line)
                    if match:
                        blocks.append({
                            "line": i,
                            "type": "describe",
                            "text": match.group(1),
                            "indent": indent,
                            "status": None,
                            "has_implementation": True
                        })
                
                # Extract it blocks
                elif 'with it(' in line:
                    match = re.search(r"with it\(['\"]([^'\"]+)['\"]", line)
                    if match:
                        has_impl = BDDIncrementalCommand._detect_test_implementation(lines, i, framework)
                        status = TestStatus.IMPLEMENTED if has_impl else TestStatus.SIGNATURE
                        
                        blocks.append({
                            "line": i,
                            "type": "it",
                            "text": match.group(1),
                            "indent": indent,
                            "status": status.value,
                            "has_implementation": has_impl
                        })
        
        return blocks

    @staticmethod
    def extract_test_structure_chunks(test_file_path: str, framework: str) -> List[Dict[str, Any]]:
        """Extract test structure in chunks"""
        blocks = BDDIncrementalCommand.parse_test_structure(test_file_path, framework)
        if not blocks:
            return []
        
        chunks = []
        current_chunk = {"structure": "", "context": None}
        
        for block in blocks:
            block_line = f"Line {block['line']}: {block['type']}('{block['text']}')"
            current_chunk["structure"] += block_line + "\n"
        
        if current_chunk["structure"]:
            chunks.append(current_chunk)
        
        return chunks if chunks else [{"structure": "", "context": None}]


# TestStatus enum
class TestStatus(Enum):
    """Test implementation status"""
    SIGNATURE = "signature"
    IMPLEMENTED = "implemented"

# BDD Phase enum - must be defined before use
class BDDPhase(Enum):
    """BDD workflow phases"""
    DOMAIN_SCAFFOLD = "domain_scaffold"
    SIGNATURES = "signatures"
    TEST = "test"
    CODE = "code"


class BDDWorkflow(Workflow):
    """
    BDD-specific workflow that extends Workflow with BDD phases.
    
    Creates all BDD phases in constructor:
    - Phase 0: Domain Scaffolding
    - Phase 1: Build Test Signatures
    - Phase 2: Write Tests
    - Phase 3: Write Code
    
    Wrapping chain: BDDWorkflowPhaseCommand → IncrementalCommand → CodeAugmentedCommand → SpecializingRuleCommand → Command
    """
    
    def __init__(self, content: Content, test_file: str, framework: str, max_sample_size: int = 18, base_rule_file_name: str = 'bdd-rule.mdc'):
        """
        Args:
            content: Content to process (test file content)
            test_file: Test file path
            framework: Test framework ('mamba' or 'jest')
            max_sample_size: Maximum sample size for incremental runs (default: 18)
            base_rule_file_name: Name of BDD base rule file (default: 'bdd-rule.mdc')
        """
        super().__init__()
        
        # Build command chain directly: Command → SpecializingRuleCommand → CodeAugmentedCommand
        # Create base rule
        base_rule = BaseRule(base_rule_file_name) if BaseRule else None
        
        # Create BDD rule for framework detection
        bdd_rule = BDDRule(base_rule_file_name) if FrameworkSpecializingRule else None
        specializing_rule = bdd_rule if bdd_rule else None
        
        # Create phases in order, each with its own command instance, instructions, and name set
        # Phase 0: Domain Scaffolding
        phase_0 = self._create_phase_command(
            content, base_rule, specializing_rule, max_sample_size,
            0, "Phase 0: Domain Scaffolding", test_file, framework, BDDPhase.DOMAIN_SCAFFOLD,
            self._get_domain_scaffold_instructions(test_file)
        )
        
        # Phase 1: Build Test Signatures
        phase_1 = self._create_phase_command(
            content, base_rule, specializing_rule, max_sample_size,
            1, "Phase 1: Build Test Signatures", test_file, framework, BDDPhase.SIGNATURES,
            self._get_signature_instructions(test_file, framework)
        )
        
        # Phase 2: Write Tests
        phase_2 = self._create_phase_command(
            content, base_rule, specializing_rule, max_sample_size,
            2, "Phase 2: Write Tests", test_file, framework, BDDPhase.TEST,
            self._get_test_instructions()
        )
        
        # Phase 3: Write Code
        phase_3 = self._create_phase_command(
            content, base_rule, specializing_rule, max_sample_size,
            3, "Phase 3: Write Code", test_file, framework, BDDPhase.CODE,
            self._get_code_instructions()
        )
        
        self.phases = [phase_0, phase_1, phase_2, phase_3]
    
    def _create_phase_command(self, content, base_rule, specializing_rule, max_sample_size,
                              phase_number, phase_name, test_file, framework, bdd_phase, generate_instructions):
        """Create a phase command with phase-specific instructions"""
        specializing_command = SpecializingRuleCommand(content, base_rule, specializing_rule, generate_instructions=generate_instructions)
        
        # For Phase 0 (Domain Scaffolding), use BDDScaffoldCommand which loads BDDScaffoldRule
        # BDDScaffoldRule injects scaffold-specific heuristics into principles
        if phase_number == 0:
            # Create BDDScaffoldRule which injects scaffold heuristics into principles
            scaffold_rule = BDDScaffoldRule(base_rule_file_name='bdd-rule.mdc')
            # Use BDDScaffoldCommand with the specializing command
            code_augmented_command = BDDScaffoldCommand(content, base_rule_file_name='bdd-rule.mdc')
            # Replace the inner command to use our specializing command
            code_augmented_command._inner_command = specializing_command
            # Update the base_rule to use scaffold_rule's base_rule (which has heuristics injected)
            code_augmented_command.base_rule = scaffold_rule.base_rule
        else:
            # For other phases, use standard CodeAugmentedCommand
            code_augmented_command = CodeAugmentedCommand(specializing_command, base_rule)
        
        incremental_command = BDDIncrementalCommand(code_augmented_command, base_rule, test_file, max_sample_size)
        incremental_command.name = phase_name
        
        return BDDWorkflowPhaseCommand(
            incremental_command, self, phase_number, phase_name,
            test_file, framework, bdd_phase
        )
    
    def _get_domain_scaffold_instructions(self, test_file: str) -> str:
        """Get domain scaffold phase instructions"""
        test_path = Path(test_file)
        hierarchy_file = test_path.parent / f"{test_path.stem}-hierarchy.txt"
        
        return f"""STAGE 0: DOMAIN SCAFFOLDING

Create plain English hierarchy text file: {hierarchy_file.name}

Discover domain maps and domain interaction files:
- Look for *domain-map*.txt files (provides structure and hierarchy)
- Look for *domain-interactions*.txt files (if present, can enhance with sequencing and function hints)

Write plain English hierarchy following patterns:
- NO code syntax (), =>, {{}} - just plain English text
- NEVER flatten - preserve ALL nesting from domain map
- Follow temporal lifecycle progression (created → played → edited → saved)
- Use complete end-to-end behaviors

If domain interaction files are present, you can leverage them to enhance:
- Test ordering: Use scenario order to determine test ordering (scenarios provide correct storytelling sequence)
- Test sequence: Use flow steps to determine test sequence within describe blocks (flow shows order of domain concept interactions)
- Test cases: Use business rules to generate specific it blocks (each rule becomes a test case)
- Function hints: Use transformations and lookups to inform what individual it blocks should test (transformations tell you what object functions will be)
- Concept relationships: Use actors to identify concept relationships and co-testing opportunities

Domain map provides primary structure; domain interactions enhance with sequencing and function hints when present.

This is a TEXT file (.txt), separate from the test code file.
Run /bdd-domain-scaffold-verify when ready."""
    
    def _get_signature_instructions(self, test_file: str, framework: str) -> str:
        """Get signature phase instructions"""
        return """STAGE 1: CREATE TEST HIERARCHY & SIGNATURES

1. CREATE test hierarchy from domain map:
   - Preserve ALL nesting levels from domain map
   - Top-level describes = DOMAINS from map
   - Nested describes = CONCEPTS under domain
   - Deep nesting = SUB-CONCEPTS under concept
2. Convert to proper code syntax:
   - describe('...', () => {})
   - it('should...', () => {})
3. Keep test bodies EMPTY - no mocks, no stubs, no helpers
4. Mark with // BDD: SIGNATURE comments
5. ~18 describe/it blocks for Sample 1

⚠️  CRITICAL: NEVER flatten hierarchy - preserve domain map depth!
Run /bdd-signature-verify when ready"""
    
    def _get_test_instructions(self) -> str:
        """Get test implementation phase instructions"""
        return """STAGE 2: Write Tests - Implement Full Test Code

1. Find ~18 test signatures marked with # BDD: SIGNATURE
2. Implement with Arrange-Act-Assert structure:
   - Arrange: Set up test data and mocks
   - Act: Call production code directly
   - Assert: Verify expected outcomes
3. Mock only external boundaries (file I/O, network, database)
4. Extract duplicate setup to helper functions or beforeEach()
5. Call production code directly - NO commenting out code
6. If production code doesn't exist, tests fail naturally
   Example: NameError: name 'PowerItem' is not defined
7. This shows exactly what to implement next

Run /bdd-test-validate when ready"""
    
    def _get_code_instructions(self) -> str:
        """Get code implementation phase instructions"""
        return """STAGE 3: Write Code - Implement Production Code

1. Implement complete, functional production code for ~18 tests
2. **CRITICAL**: Code must be fully functional, not placeholders or stubs
3. Make tests pass with simplest solution - but implement it completely
4. Avoid over-factoring for reuse - but write complete functionality
5. Resist adding features no test demands
6. Use simple data structures before classes - but still implement complete functionality
7. Verify tests now PASS
8. Check for regressions in existing tests

Minimalism means simple and straightforward, NOT incomplete. Write complete, working code that tests demand.

Run /bdd-code-validate when ready"""
    
    # REFACTOR phase removed - refactoring happens through validation at every phase
    # def _get_refactor_instructions(self) -> str:
    #     """Get REFACTOR phase instructions"""
    #     return """STAGE 4: REFACTOR - Improve Code Quality"""
    
    @staticmethod
    def run_tests(test_file_path: str, framework: str, single_test_line: Optional[int] = None) -> Dict[str, Any]:
        """
        Run tests and capture results with framework-specific commands and proper directory context.
        Used by TEST and CODE phases, and by the run action.
        
        Args:
            test_file_path: Path to test file (absolute or relative)
            framework: 'jest' or 'mamba'
            single_test_line: If provided, run only test at this line
        
        Returns: {"success": bool, "output": str, "passed": int, "failed": int, "error": Optional[str]}
        """
        try:
            test_path = Path(test_file_path).resolve()
            if not test_path.exists():
                return {"success": False, "error": f"Test file not found: {test_file_path}", "output": "", "passed": 0, "failed": 0}
            
            # Determine working directory and command based on framework
            if framework == 'jest':
                # Jest runs from project root (where package.json is located)
                # Find project root by looking for package.json
                project_root = test_path.parent
                while project_root.parent != project_root:
                    if (project_root / 'package.json').exists():
                        break
                    project_root = project_root.parent
                
                cmd = ['npm', 'test', '--', str(test_path.relative_to(project_root))]
                if single_test_line:
                    # Jest can run specific test by line number
                    cmd.extend(['-t', str(single_test_line)])
                cwd = str(project_root)
            
            elif framework == 'mamba':
                # Mamba runs from test file's directory (ensures proper Python imports)
                # Use python -m mamba.cli format (as used in conftest.py)
                cmd = [sys.executable, '-m', 'mamba.cli', str(test_path.name)]
                if single_test_line:
                    # Mamba runs specific test by line
                    cmd.extend(['--line', str(single_test_line)])
                cwd = str(test_path.parent)
            
            else:
                return {"success": False, "error": f"Unknown framework: {framework}", "output": "", "passed": 0, "failed": 0}
            
            # Run tests from the correct directory
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=cwd)
            
            # Parse output for pass/fail counts
            output = result.stdout + result.stderr
            passed = len(re.findall(r'✓|PASS|passed', output, re.IGNORECASE))
            failed = len(re.findall(r'✗|FAIL|failed', output, re.IGNORECASE))
            
            return {
                "success": result.returncode == 0,
                "output": output,
                "passed": passed,
                "failed": failed,
                "error": None if result.returncode == 0 else "Tests failed"
            }
        
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Test execution timed out", "output": "", "passed": 0, "failed": 0}
        except Exception as e:
            return {"success": False, "error": str(e), "output": "", "passed": 0, "failed": 0}


class BDDWorkflowPhaseCommand:
    """
    BDD-specific workflow phase command that combines WorkflowPhaseCommand with BDD phase logic.
    
    Extends WorkflowPhaseCommand with:
    - BDD phase types (DOMAIN_SCAFFOLD, SIGNATURES, TEST, CODE)
    """
    
    def __init__(self, inner_command, workflow: Workflow, phase_number: int, phase_name: str, 
                 test_file: str, framework: str, bdd_phase: BDDPhase):
        """
        Args:
            inner_command: Inner command (typically IncrementalCommand wrapping BDDCommand)
            workflow: Workflow containing phases
            phase_number: Phase number
            phase_name: Phase name
            test_file: Test file path
            framework: Test framework ('mamba' or 'jest')
            bdd_phase: BDD phase enum
        """
        # Store phase metadata for direct access
        self.phase_number = phase_number
        self.phase_name = phase_name
        
        # Wrap with WorkflowPhaseCommand for common workflow functionality
        if WorkflowPhaseCommand:
            self.phase_command = WorkflowPhaseCommand(inner_command, workflow, phase_number, phase_name)
        else:
            self.phase_command = None
        
        # BDD-specific
        self.test_file = test_file
        self.framework = framework
        self.bdd_phase = bdd_phase
    
    @property
    def name(self):
        """Get phase name"""
        return self.phase_name
    
    @property
    def content(self):
        """Delegate to phase command"""
        return self.phase_command.content if self.phase_command else None
    
    @property
    def current_phase(self):
        """Get current phase number"""
        return self.phase_command.current_phase if self.phase_command else self.phase_number
    
    def start(self):
        """Start the phase"""
        if self.phase_command:
            self.phase_command.start()
    
    def approve(self):
        """Approve current phase"""
        if self.phase_command:
            self.phase_command.approve()
    
    def proceed_to_next_phase(self):
        """Move to next phase in workflow"""
        if self.phase_command:
            self.phase_command.proceed_to_next_phase()
    
    def __getattr__(self, name):
        """Delegate unknown attributes to phase command"""
        if self.phase_command:
            return getattr(self.phase_command, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    @staticmethod
    def generate_cross_section_prompt(all_violations: List) -> str:
        """Generate final prompt for cross-section validation"""
        return f"""
FINAL CROSS-SECTION VALIDATION

You've validated across Sections 1-5.

Now check for issues that span MULTIPLE sections:

[] Do violations in different sections indicate systemic issues?
  (e.g., jargon in Section 1 + implementation details in Section 4 = not domain-focused)

[] Are there patterns across sections suggesting missing abstractions?
  (e.g., duplicate setup in Section 3 + testing internals in Section 2 = need helper)

[] Do Section 4 layer violations conflict with Section 1 readability?
  (e.g., "front-end" tests using business logic language)

RESPOND: cross_section_issues: [list any found]
"""
    
    @staticmethod
    def validate_section_iterative(blocks: List[Dict], section_num: str, 
                                   section_rules: Dict, chunk_size: int,
                                   domain_map: Dict) -> List:
        """Validate all blocks for one section in chunks"""
        print(f"\n{'='*60}")
        print(f"Section {section_num}: {section_rules['title']}")
        print(f"{'='*60}\n")
        
        violations = []
        total_chunks = (len(blocks) + chunk_size - 1) // chunk_size
        
        for chunk_idx in range(total_chunks):
            start = chunk_idx * chunk_size
            end = min(start + chunk_size, len(blocks))
            chunk = blocks[start:end]
            
            print(f"\n[Chunk {chunk_idx+1}/{total_chunks}] {len(chunk)} blocks:\n")
            
            for i, block in enumerate(chunk, start=start+1):
                prompt = BDDIncrementalCommand.generate_section_prompt(block, section_num, section_rules, domain_map)
                print(f"Block {i}/{len(blocks)}: Line {block['line']}")
                print(prompt)
                print()
            
            print("-"*60)
            print(f"AI: Validate above {len(chunk)} blocks against Section {section_num}")
            print(f"    Report violations in chat")
            print("-"*60 + "\n")
            
            if chunk_idx < total_chunks - 1:
                input("   Press ENTER to continue to next chunk... ")
        
        print(f"\n[DONE] Section {section_num} Complete\n")
        return violations

    @staticmethod
    def identify_code_relationships(test_file_path: str) -> Dict[str, List[str]]:
        """
        Identify code under test and other test files related to this test.
        Used by TEST and CODE phases.
        
        Returns: {"code_under_test_files": [...], "related_tests": [...]}
        """
        test_path = Path(test_file_path)
        test_content = test_path.read_text(encoding='utf-8')
        
        # Extract imports
        imports = re.findall(r"import .+ from ['\"]([^'\"]+)['\"]", test_content)
        imports += re.findall(r"require\(['\"]([^'\"]+)['\"]\)", test_content)
        
        code_under_test_files = []
        related_tests = []
        
        for imp in imports:
            # Skip node_modules
            if imp.startswith('.'):
                # Relative import
                resolved = (test_path.parent / imp).resolve()
                
                # Try common extensions
                for ext in ['.js', '.ts', '.mjs', '.jsx', '.tsx', '.py']:
                    candidate = Path(str(resolved) + ext)
                    if candidate.exists():
                        if any(pattern in candidate.name for pattern in ['test', 'spec', '_test', 'test_']):
                            related_tests.append(str(candidate))
                        else:
                            code_under_test_files.append(str(candidate))
                        break
        
        return {
            "code_under_test_files": code_under_test_files,
            "related_tests": related_tests
        }






# ============================================================================
# ENHANCED VALIDATOR - Rule Parsing & Iterative Validation
# ============================================================================

class RuleParser:
    """Parse BDD rule files to extract validation checklists"""
    
    def __init__(self):
        self._cache = {}
    
    def get_checklist(self, framework: str) -> Dict[str, Any]:
        """Parse rule file and return validation checklist (cached)"""
        if framework in self._cache:
            return self._cache[framework]
        
        bdd_rule = BDDRule()
        rule_data = bdd_rule.load_framework_rule_file(framework)
        if not rule_data:
            return {}
        
        sections = self._parse_rule_file(rule_data['content'])
        self._cache[framework] = sections
        return sections
    
    def _parse_rule_file(self, content: str) -> Dict[str, Dict[str, Any]]:
        """Parse entire rule file into sections with checklists"""
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            section_match = re.match(r'^##\s+(\d+)\.\s+(.+)$', line)
            if section_match:
                if current_section:
                    sections[current_section['num']] = self._parse_section_content(
                        current_section['title'],
                        '\n'.join(current_content)
                    )
                current_section = {
                    'num': section_match.group(1),
                    'title': section_match.group(2).strip()
                }
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section['num']] = self._parse_section_content(
                current_section['title'],
                '\n'.join(current_content)
            )
        
        return sections
    
    def _parse_section_content(self, title: str, content: str) -> Dict[str, Any]:
        """Extract principle, checks, and examples from section content"""
        principle_lines = []
        for line in content.split('\n'):
            if '**✅ DO:**' in line or '**❌ DON\'T:**' in line or line.startswith('##'):
                break
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                principle_lines.append(stripped)
        
        principle = ' '.join(principle_lines)
        do_examples = self._extract_code_blocks(content, '**✅ DO:**')
        dont_examples = self._extract_code_blocks(content, '**❌ DON\'T:**')
        checks = self._generate_checks_from_donts(dont_examples, do_examples)
        
        return {
            'title': title,
            'principle': principle,
            'checks': checks,
            'dos': do_examples,
            'donts': dont_examples
        }
    
    def _extract_code_blocks(self, content: str, marker: str) -> List[str]:
        """Extract code blocks after a specific marker"""
        blocks = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            if marker in lines[i]:
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    i += 1
                
                if i < len(lines):
                    i += 1
                    code_lines = []
                    while i < len(lines) and not lines[i].strip().startswith('```'):
                        code_lines.append(lines[i])
                        i += 1
                    
                    if code_lines:
                        blocks.append('\n'.join(code_lines))
            i += 1
        
        return blocks
    
    def _generate_checks_from_donts(self, dont_examples: List[str], do_examples: List[str]) -> List[Dict[str, Any]]:
        """Auto-generate validation checks from DON'T examples"""
        checks = []
        
        all_jargon = set()
        for dont in dont_examples:
            jargon = self._extract_jargon_keywords(dont)
            all_jargon.update(jargon)
        
        if all_jargon:
            checks.append({
                'question': 'Contains technical jargon?',
                'keywords': sorted(list(all_jargon)),
                'example_dont': dont_examples[0] if dont_examples else '',
                'example_do': do_examples[0] if do_examples else ''
            })
        
        verbs = self._extract_action_verbs(dont_examples)
        if verbs:
            checks.append({
                'question': 'Uses nouns (not verbs)?',
                'keywords': verbs,
                'example_dont': next((d for d in dont_examples if any(v in d for v in verbs)), ''),
                'example_do': do_examples[0] if do_examples else ''
            })
        
        if any('omit "should"' in d.lower() or 'missing "should"' in d.lower() for d in dont_examples):
            checks.append({
                'question': 'Starts with "should" (for it() blocks)?',
                'keywords': [],
                'example_dont': next((d for d in dont_examples if 'should' not in d.lower() and 'it(' in d), ''),
                'example_do': next((d for d in do_examples if 'should' in d.lower() and 'it(' in d), '')
            })
        
        return checks
    
    def _extract_jargon_keywords(self, code_example: str) -> List[str]:
        """Extract problematic technical words from code example"""
        jargon_words = []
        tech_verbs = ['extract', 'parse', 'serialize', 'deserialize', 'get', 'set',
                      'fetch', 'retrieve', 'call', 'return', 'handle', 'process']
        tech_nouns = ['flag', 'id', 'hook', 'handler', 'callback', 'listener',
                      'message', 'event', 'data', 'payload', 'api', 'endpoint',
                      'request', 'response', 'function', 'method', 'class', 'module']
        
        matches = re.findall(r"(?:describe|it)\(['\"]([^'\"]+)['\"]", code_example)
        
        for match in matches:
            words = match.split()
            for word in words:
                word_lower = word.lower().strip('(),;')
                if re.match(r'^[a-z]+[A-Z]', word):
                    jargon_words.append(word)
                elif word_lower in tech_verbs:
                    jargon_words.append(word_lower)
                elif word_lower in tech_nouns:
                    jargon_words.append(word_lower)
        
        paren_matches = re.findall(r'\(([^)]+)\)', code_example)
        for match in paren_matches:
            if 'don\'t' in code_example.lower()[:code_example.find(match)]:
                words = re.split(r'[,/\s]+', match)
                jargon_words.extend([w.strip().lower() for w in words if w.strip()])
        
        return list(set(jargon_words))
    
    def _extract_action_verbs(self, dont_examples: List[str]) -> List[str]:
        """Extract action verbs from DON'T examples"""
        verbs = set()
        common_verbs = ['when', 'calls', 'gets', 'sets', 'returns', 'fetches',
                        'creates', 'updates', 'deletes', 'handles', 'processes']
        
        for dont in dont_examples:
            matches = re.findall(r"describe\(['\"]([^'\"]+)['\"]", dont)
            for match in matches:
                first_word = match.split()[0].lower() if match.split() else ''
                if first_word in common_verbs:
                    verbs.add(first_word)
        
        return sorted(list(verbs))


# Global parser instance
_rule_parser = RuleParser()


# ============================================================================
# BDD TEST FILE VALIDATION (Legacy - kept for backward compatibility)
# ============================================================================

# Note: Helper functions (detect_framework_from_file, discover_domain_maps, 
# load_rule_file, extract_dos_and_donts, extract_test_structure_chunks, etc.)
# are defined earlier in this file (around line 815+)

def bdd_validate_test_file(file_path: Optional[str] = None, thorough: bool = False, phase: str = 'signatures'):
    """
    Main function to validate a BDD test file.
    
    Args:
        file_path: Path to test file to validate
        thorough: Load detailed reference examples
        phase: 'signatures' (Phase 0) or 'implementation' (Phase 1+)
               - signatures: Only validate § 1 (Business Readable Language)
               - implementation: Validate all sections (§ 1-5)
    
    Steps:
    1. Get file path (from arg or current file)
    2. Detect framework from file path
    3. Load framework-specific rule
    4. Extract DO/DON'T examples by section (filtered by phase)
    5. Perform static checks
    6-9. AI evaluates test against each section's DO/DON'Ts
    10. Compile results
    11. Generate report
    12. Ask user for action
    """
    
    print("\n=== BDD Validation Starting ===")
    
    # Step 1: Get file path
    if not file_path:
        print("❌ No file path provided. Use: \\bdd-validate <file-path>")
        return {"error": "No file path provided"}
    
    print(f"Step 1: File path: {file_path}")
    
    test_path = Path(file_path)
    if not test_path.exists():
        print(f"❌ File not found: {file_path}")
        return {"error": "File not found"}
    
    print(f"✅ File exists: {test_path.name}")
    
    # Step 2: Detect framework
    print(f"Step 2: Detecting framework...")
    framework = BDDRule.detect_framework_from_file(file_path)
    if not framework:
        print(f"❌ File doesn't match BDD test patterns: {file_path}")
        print("   Expected: *.test.js, *.spec.ts, test_*.py, etc.")
        return {"error": "Not a BDD test file"}
    
    print(f"✅ Detected framework: {framework.upper()}")
    
    # Step 2.5: Discover domain maps
    print(f"Step 2.5: Discovering domain maps in test directory...")
    test_content = Content(file_path)
    bdd_command = BDDCommand(test_content)
    domain_maps = bdd_command.discover_domain_maps()
    
    if domain_maps["found"]:
        if domain_maps["domain_map"]:
            map_name = Path(domain_maps["domain_map"]["path"]).name
            print(f"✅ Found domain map: {map_name}")
        if domain_maps["interaction_map"]:
            map_name = Path(domain_maps["interaction_map"]["path"]).name
            print(f"✅ Found interaction map: {map_name}")
    else:
        print(f"⚠️  No domain maps found in {test_path.parent}")
        print(f"   Recommendation:")
        print(f"   1. Run: \\ddd-analyze <source-file>")
        print(f"   2. Run: \\ddd-interactions <source-file>")
        print(f"   Domain maps provide primary source for test structure and naming.")
    
    # Step 3: Load rule file
    print(f"Step 3: Loading {framework} rule file...")
    rule_data = load_rule_file(framework)
    if not rule_data:
        print(f"❌ Could not load rule file for {framework}")
        return {"error": "Rule file not found"}
    
    print(f"✅ Loaded rule: {rule_data['rule_path']}")
    
    # Step 4: Extract DO/DON'T examples - ALWAYS use ALL sections
    print("Step 4: Extracting DO/DON'T examples...")
    bdd_rule = BDDRule()
    sections = bdd_rule.extract_dos_and_donts(rule_data['content'])
    print(f"   Validating all sections (§ 1-5) - rules apply at all phases")
    
    total_dos = sum(len(s['dos']) for s in sections.values())
    total_donts = sum(len(s['donts']) for s in sections.values())
    print(f"✅ Extracted {total_dos} DO examples and {total_donts} DON'T examples from {len(sections)} sections")
    
    # Step 5: Extract test structure in manageable chunks
    print("Step 5: Extracting test structure (chunked by describe blocks)...")
    chunks = BDDIncrementalCommand.extract_test_structure_chunks(file_path, framework)
    total_blocks = sum(len(chunk['structure'].split('\n')) for chunk in chunks)
    print(f"   Extracted {total_blocks} test blocks in {len(chunks)} chunk(s)")
    
    # Step 5b: Static checks on all chunks
    print("Step 5b: Running static analysis...")
    static_issues = []
    for chunk in chunks:
        chunk_issues = perform_static_checks(chunk['structure'], framework)
        static_issues.extend(chunk_issues)
    
    if static_issues:
        print(f"   Found {len(static_issues)} static issues")
    else:
        print(f"   No static issues found")
    
    # Step 5c: Detect § 3 violations (duplicate code in siblings)
    print("Step 5c: Detecting § 3 violations (duplicate code in 3+ siblings)...")
    section3_violations = detect_section3_violations(file_path, framework)
    
    if section3_violations:
        print(f"   Found {len(section3_violations)} § 3 violation groups")
        # Convert to static issues format
        for v in section3_violations:
            violation_type = "Decorator Pattern" if v['type'] == 'decorator_pattern' else "Duplicate Arrange"
            static_issues.append({
                "line": v['parent_line'],
                "issue": f"{violation_type}: {v['sibling_count']} sibling {v['sibling_type']}() blocks with {v['similarity']:.0%} similar code (lines: {', '.join(map(str, v['sibling_lines']))})",
                "type": "error",
                "rule": "3. Balance Context Sharing with Localization",
                "details": v
            })
    else:
        print(f"   No § 3 violations found")
    
    # Step 6: Load reference examples if thorough mode
    reference_examples = {}
    if thorough:
        print("Step 6: Loading reference examples (THOROUGH MODE)...")
        reference_examples = load_relevant_reference_examples(framework, list(sections.keys()))
        print(f"   Loaded {len(reference_examples)} reference sections")
    
    # Step 7: Show static issues if found
    if static_issues:
        print("\n" + "="*80)
        print("STATIC VIOLATIONS DETECTED")
        print("="*80)
        for issue in static_issues:
            print(f"Line {issue['line']}: {issue['issue']}")
            print(f"   Rule: {issue['rule']}")
        print("="*80)
    
    # Step 8: Print FULL RULE FILE for AI Agent
    print("\n" + "="*80)
    print("FULL BDD RULE FILE - READ THIS")
    print("="*80)
    print(f"Phase: {phase.upper()}")
    print(f"Framework: {framework.upper()}")
    print(f"Rule File: {rule_data['rule_path']}")
    print("="*80)
    print(rule_data['content'])
    print("="*80)
    
    # Show domain maps if found
    if domain_maps["found"]:
        print("\n" + "="*80)
        print("DOMAIN MAPS FOUND - USE AS PRIMARY SOURCE")
        print("="*80)
        if domain_maps["domain_map"]:
            print("\nDOMAIN MAP:")
            print("-" * 80)
            print(domain_maps["domain_map"]["content"])
        if domain_maps["interaction_map"]:
            print("\nINTERACTION MAP:")
            print("-" * 80)
            print(domain_maps["interaction_map"]["content"])
        print("="*80)
    
    # Show test code to validate
    print("\n" + "="*80)
    print("YOUR TEST CODE TO VALIDATE")
    print("="*80)
    for chunk in chunks:
        if chunk.get('context'):
            print(f"\nContext: {chunk['context']}")
        print(chunk['structure'])
    
    # Simple instruction
    print("\n" + "="*80)
    print("AI AGENT: VALIDATE ALL TESTS WITH THESE RULES AND EXAMPLES!")
    print("="*80)
    print("1. Compare every describe/it against the DO/DON'T examples in rule")
    if domain_maps["found"]:
        print("2. Verify test structure aligns with domain map hierarchy")
        print("3. Check test names use domain concept terminology")
        print("4. Validate helpers/mocks align with domain concepts")
        print("5. Find violations")
        print("6. Fix violations")
        print("7. Re-run until zero violations")
    else:
        print("2. Find violations")
        print("3. Fix violations")
        print("4. Re-run until zero violations")
    print("="*80)
    
    # Return data for AI Agent to analyze
    validation_data = {
        "test_file": file_path,
        "framework": framework,
        "phase": phase,
        "rule_content": rule_data['content'],
        "test_chunks": chunks,
        "total_blocks": total_blocks,
        "static_issues": static_issues,
        "domain_maps": domain_maps  # Include discovered domain maps
    }
    
    return validation_data


# ============================================================================
# HELPER FUNCTIONS FOR VALIDATION
# ============================================================================

def load_rule_file(framework: str) -> Optional[Dict[str, Any]]:
    """Load framework-specific rule file"""
    bdd_rule = BDDRule()
    return bdd_rule.load_framework_rule_file(framework)

def perform_static_checks(structure: str, framework: str) -> List[Dict[str, Any]]:
    """Perform static checks on test structure"""
    return []

def detect_section3_violations(file_path: str, framework: str) -> List[Dict[str, Any]]:
    """Detect § 3 violations (duplicate code in siblings)"""
    return []

def load_relevant_reference_examples(framework: str, sections: List[str]) -> Dict[str, Any]:
    """Load reference examples for validation"""
    return {}

def bdd_workflow(file_path: str, scope: str = "describe", phase: Optional[str] = None, 
                 cursor_line: Optional[int] = None, auto: bool = False) -> Dict[str, Any]:
    """Create and return BDD workflow data"""
    content = Content(file_path)
    framework = BDDRule.detect_framework_from_file(file_path) or "mamba"
    workflow = BDDWorkflow(content, file_path, framework)
    
    return {
        "phase": phase or "signatures",
        "scope": scope,
        "test_structure": {
            "scoped_tests": []
        }
    }

def validate_iterative_mode(file_path: str, framework: str, chunk_size: int):
    """Validate in iterative mode"""
    print(f"Validating {file_path} in iterative mode (chunk size: {chunk_size})")

def validate_batch_mode(file_path: str, framework: str):
    """Validate in batch mode"""
    print(f"Validating {file_path} in batch mode")


# ============================================================================
# ENHANCED VALIDATOR - Rule Parsing & Iterative Validation
# ============================================================================

class RuleParser:
    """Parse BDD rule files to extract validation checklists"""
    
    def __init__(self):
        self._cache = {}
    
    def get_checklist(self, framework: str) -> Dict[str, Any]:
        """Parse rule file and return validation checklist (cached)"""
        if framework in self._cache:
            return self._cache[framework]
        
        bdd_rule = BDDRule()
        rule_data = bdd_rule.load_framework_rule_file(framework)
        if not rule_data:
            return {}
        
        sections = self._parse_rule_file(rule_data['content'])
        self._cache[framework] = sections
        return sections
    
    def _parse_rule_file(self, content: str) -> Dict[str, Dict[str, Any]]:
        """Parse entire rule file into sections with checklists"""
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            section_match = re.match(r'^##\s+(\d+)\.\s+(.+)$', line)
            if section_match:
                if current_section:
                    sections[current_section['num']] = self._parse_section_content(
                        current_section['title'],
                        '\n'.join(current_content)
                    )
                current_section = {
                    'num': section_match.group(1),
                    'title': section_match.group(2).strip()
                }
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section['num']] = self._parse_section_content(
                current_section['title'],
                '\n'.join(current_content)
            )
        
        return sections
    
    def _parse_section_content(self, title: str, content: str) -> Dict[str, Any]:
        """Extract principle, checks, and examples from section content"""
        principle_lines = []
        for line in content.split('\n'):
            if '**✅ DO:**' in line or '**❌ DON\'T:**' in line or line.startswith('##'):
                break
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                principle_lines.append(stripped)
        
        principle = ' '.join(principle_lines)
        do_examples = self._extract_code_blocks(content, '**✅ DO:**')
        dont_examples = self._extract_code_blocks(content, '**❌ DON\'T:**')
        checks = self._generate_checks_from_donts(dont_examples, do_examples)
        
        return {
            'title': title,
            'principle': principle,
            'checks': checks,
            'dos': do_examples,
            'donts': dont_examples
        }
    
    def _extract_code_blocks(self, content: str, marker: str) -> List[str]:
        """Extract code blocks after a specific marker"""
        blocks = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            if marker in lines[i]:
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    i += 1
                
                if i < len(lines):
                    i += 1
                    code_lines = []
                    while i < len(lines) and not lines[i].strip().startswith('```'):
                        code_lines.append(lines[i])
                        i += 1
                    
                    if code_lines:
                        blocks.append('\n'.join(code_lines))
            i += 1
        
        return blocks
    
    def _generate_checks_from_donts(self, dont_examples: List[str], do_examples: List[str]) -> List[Dict[str, Any]]:
        """Auto-generate validation checks from DON'T examples"""
        checks = []
        
        all_jargon = set()
        for dont in dont_examples:
            jargon = self._extract_jargon_keywords(dont)
            all_jargon.update(jargon)
        
        if all_jargon:
            checks.append({
                'question': 'Contains technical jargon?',
                'keywords': sorted(list(all_jargon)),
                'example_dont': dont_examples[0] if dont_examples else '',
                'example_do': do_examples[0] if do_examples else ''
            })
        
        verbs = self._extract_action_verbs(dont_examples)
        if verbs:
            checks.append({
                'question': 'Uses nouns (not verbs)?',
                'keywords': verbs,
                'example_dont': next((d for d in dont_examples if any(v in d for v in verbs)), ''),
                'example_do': do_examples[0] if do_examples else ''
            })
        
        if any('omit "should"' in d.lower() or 'missing "should"' in d.lower() for d in dont_examples):
            checks.append({
                'question': 'Starts with "should" (for it() blocks)?',
                'keywords': [],
                'example_dont': next((d for d in dont_examples if 'should' not in d.lower() and 'it(' in d), ''),
                'example_do': next((d for d in do_examples if 'should' in d.lower() and 'it(' in d), '')
            })
        
        return checks
    
    def _extract_jargon_keywords(self, code_example: str) -> List[str]:
        """Extract problematic technical words from code example"""
        jargon_words = []
        tech_verbs = ['extract', 'parse', 'serialize', 'deserialize', 'get', 'set',
                      'fetch', 'retrieve', 'call', 'return', 'handle', 'process']
        tech_nouns = ['flag', 'id', 'hook', 'handler', 'callback', 'listener',
                      'message', 'event', 'data', 'payload', 'api', 'endpoint',
                      'request', 'response', 'function', 'method', 'class', 'module']
        
        matches = re.findall(r"(?:describe|it)\(['\"]([^'\"]+)['\"]", code_example)
        
        for match in matches:
            words = match.split()
            for word in words:
                word_lower = word.lower().strip('(),;')
                if re.match(r'^[a-z]+[A-Z]', word):
                    jargon_words.append(word)
                elif word_lower in tech_verbs:
                    jargon_words.append(word_lower)
                elif word_lower in tech_nouns:
                    jargon_words.append(word_lower)
        
        paren_matches = re.findall(r'\(([^)]+)\)', code_example)
        for match in paren_matches:
            if 'don\'t' in code_example.lower()[:code_example.find(match)]:
                words = re.split(r'[,/\s]+', match)
                jargon_words.extend([w.strip().lower() for w in words if w.strip()])
        
        return list(set(jargon_words))
    
    def _extract_action_verbs(self, dont_examples: List[str]) -> List[str]:
        """Extract action verbs from DON'T examples"""
        verbs = set()
        common_verbs = ['when', 'calls', 'gets', 'sets', 'returns', 'fetches',
                        'creates', 'updates', 'deletes', 'handles', 'processes']
        
        for dont in dont_examples:
            matches = re.findall(r"describe\(['\"]([^'\"]+)['\"]", dont)
            for match in matches:
                first_word = match.split()[0].lower() if match.split() else ''
                if first_word in common_verbs:
                    verbs.add(first_word)
        
        return sorted(list(verbs))


# Global parser instance
_rule_parser = RuleParser()


# ============================================================================
# RUNNER GUARD UTILITY
# ============================================================================

def require_command_invocation(command_name: str):
    """
    Guard to prevent direct runner execution.
    
    Checks if runner was invoked with --from-command flag (set by Cursor commands).
    If not, displays helpful message directing user to proper slash command.
    
    Args:
        command_name: The slash command name (e.g., "bdd-validate")
    """
    if "--from-command" not in sys.argv and "--no-guard" not in sys.argv:
        print(f"\n⚠️  Please use the Cursor slash command instead:\n")
        print(f"    /{command_name}\n")
        print(f"This ensures the full AI workflow and validation is triggered.\n")
        print(f"(For testing/debugging, use --no-guard flag to bypass this check)\n")
        sys.exit(1)


# ============================================================================
# MAIN ENTRY POINT - Dispatcher for all BDD commands
# ============================================================================

if __name__ == "__main__":
    import sys
    import io
    
    # Fix Windows console encoding
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    if len(sys.argv) < 2:
        print("Usage: python bdd-runner.py <command> [args...]")
        print("\nCommands:")
        print("  workflow <file_path> [scope] [phase] [cursor_line] [--auto]")
        print("  validate <file_path> [--thorough] [--phase=<phase>]")
        print("  validate-scaffold <test_file_path>")
        print("  correct-scaffold <scaffold-file-path> [chat-context]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "workflow":
        # Guard check (and remove --no-guard from argv if present)
        if '--no-guard' in sys.argv:
            sys.argv.remove('--no-guard')
        else:
            require_command_invocation("bdd-workflow")
        
        # Parse workflow arguments
        if len(sys.argv) < 3:
            print("Error: file_path required for workflow command")
            sys.exit(1)
        
        file_path = sys.argv[2]
        scope = sys.argv[3] if len(sys.argv) > 3 else "describe"
        phase = sys.argv[4] if len(sys.argv) > 4 else None
        cursor_line = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5].isdigit() else None
        auto = "--auto" in sys.argv
        
        try:
            workflow_data = bdd_workflow(file_path, scope, phase, cursor_line, auto)
            
            if "error" in workflow_data:
                print(f"\nError: {workflow_data['error']}")
                sys.exit(1)
            
            print("\nWorkflow Data Ready:")
            print(f"  Phase: {workflow_data['phase']}")
            print(f"  Scope: {workflow_data['scope']}")
            print(f"  Tests in scope: {len(workflow_data['test_structure']['scoped_tests'])}")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    elif command == "validate-scaffold":
        # Guard check (and remove --no-guard from argv if present)
        if '--no-guard' in sys.argv:
            sys.argv.remove('--no-guard')
        else:
            require_command_invocation("bdd-scaffold-validate")
        
        if len(sys.argv) < 3:
            print("Usage: python bdd-runner.py validate-scaffold <scaffold-file-path>")
            sys.exit(1)
        
        scaffold_file = sys.argv[2]
        
        if not Path(scaffold_file).exists():
            print(f"[ERROR] File not found: {scaffold_file}")
            sys.exit(1)
        
        try:
            # Create content pointing directly to scaffold file
            content = Content(scaffold_file)
            cmd = BDDScaffoldCommand(content)
            result = cmd.validate()
            print(result)
            
            if hasattr(cmd, 'violations') and cmd.violations:
                print(f"\n[VIOLATIONS] Found {len(cmd.violations)} violations:")
                for v in cmd.violations:
                    print(f"  Line {v.line_number}: {v.message}")
                sys.exit(1)
            else:
                print("\n[OK] No violations found - scaffold is valid!")
                sys.exit(0)
                
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    elif command == "validate":
        # Guard check (and remove --no-guard from argv if present)
        if '--no-guard' in sys.argv:
            sys.argv.remove('--no-guard')
        else:
            require_command_invocation("bdd-validate")
        
        print("BDD Enhanced Validator Starting...")
        
        # Parse validate arguments
        if len(sys.argv) < 3:
            print("Usage: python bdd-runner.py validate <test-file-path> [options]")
            print("\nOptions:")
            print("  --batch              Batch mode (all sections at once)")
            print("  --chunk-size N       Blocks per chunk in iterative mode (default: 10)")
            print("  --no-guard           Skip command invocation guard")
            print("\nModes:")
            print("  Default: Iterative validation (section-by-section in chunks)")
            print("  --batch: Batch validation (all sections at once)")
            sys.exit(1)
        
        file_path = sys.argv[2]
        batch_mode = '--batch' in sys.argv
        chunk_size = 10
        
        # Check for --chunk-size flag
        for arg in sys.argv:
            if arg.startswith('--chunk-size='):
                chunk_size = int(arg.split('=')[1])
            elif arg.startswith('--chunk-size'):
                idx = sys.argv.index(arg)
                if idx + 1 < len(sys.argv):
                    chunk_size = int(sys.argv[idx + 1])
        
        # Check file exists
        if not Path(file_path).exists():
            print(f"[ERROR] File not found: {file_path}")
            sys.exit(1)
        
        # Detect framework
        print(f"Analyzing {file_path}...")
        framework = BDDRule.detect_framework_from_file(file_path)
        
        if not framework:
            print(f"[ERROR] Could not detect test framework from file path")
            print(f"        Expected Jest (.test.js, .spec.js, etc.) or Mamba (_test.py, test_*.py)")
            sys.exit(1)
        
        print(f"[OK] Detected framework: {framework}\n")
        
        try:
            # Run enhanced validation in selected mode
            if batch_mode:
                validate_batch_mode(file_path, framework)
            else:
                validate_iterative_mode(file_path, framework, chunk_size)
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    elif command == "correct-scaffold":
        # Guard check (and remove --no-guard from argv if present)
        if '--no-guard' in sys.argv:
            sys.argv.remove('--no-guard')
        else:
            require_command_invocation("bdd-scaffold-correct")
        
        if len(sys.argv) < 3:
            print("Usage: python bdd-runner.py correct-scaffold <scaffold-file-path> [chat-context]")
            sys.exit(1)
        
        scaffold_file = sys.argv[2]
        chat_context = sys.argv[3] if len(sys.argv) > 3 else "User requested scaffold correction based on current chat context"
        
        if not Path(scaffold_file).exists():
            print(f"[ERROR] File not found: {scaffold_file}")
            sys.exit(1)
        
        try:
            # Create content pointing directly to scaffold file
            content = Content(scaffold_file)
            cmd = BDDScaffoldCommand(content)
            
            # Call correct method with chat context
            if hasattr(cmd, 'correct'):
                result = cmd.correct(chat_context)
                print(result)
                print("\n[INFO] Review the corrected scaffold above and update the file if needed.")
                print(f"[INFO] Scaffold file: {scaffold_file}")
            else:
                print("[ERROR] Correct method not available on BDDScaffoldCommand")
                sys.exit(1)
                
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    elif command == "run":
        # Guard check (and remove --no-guard from argv if present)
        if '--no-guard' in sys.argv:
            sys.argv.remove('--no-guard')
        else:
            require_command_invocation("bdd-run")
        
        if len(sys.argv) < 3:
            print("Usage: python bdd-runner.py run [test-file] [framework]")
            sys.exit(1)
        
        test_file = sys.argv[2]
        framework = sys.argv[3] if len(sys.argv) > 3 else None
        
        # Auto-detect framework if not provided
        if not framework:
            # Use BDDRule's framework detection
            bdd_rule = BDDRule('bdd-rule.mdc')
            framework = bdd_rule.detect_framework_from_file(test_file)
            if not framework:
                print("[ERROR] Could not detect framework. Please specify: mamba or jest")
                sys.exit(1)
        
        if not Path(test_file).exists():
            print(f"[ERROR] Test file not found: {test_file}")
            sys.exit(1)
        
        try:
            # Run tests using BDDWorkflow.run_tests (static method)
            results = BDDWorkflow.run_tests(test_file, framework)
            
            # Display results
            print("\n" + "="*60)
            print("TEST EXECUTION RESULTS")
            print("="*60)
            print(f"Framework: {framework}")
            print(f"Test File: {test_file}")
            print(f"Status: {'PASSED' if results['success'] else 'FAILED'}")
            print(f"Passed: {results['passed']}")
            print(f"Failed: {results['failed']}")
            
            if results['error']:
                print(f"Error: {results['error']}")
            
            print("\n" + "-"*60)
            print("TEST OUTPUT:")
            print("-"*60)
            print(results['output'])
            print("="*60)
            
            # Exit with appropriate code
            sys.exit(0 if results['success'] else 1)
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
