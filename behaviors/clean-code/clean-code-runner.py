"""
Clean Code Behavior Runner

Validates code quality and suggests refactorings based on clean code principles.
Follows the same pattern as BDD runner - parses rules, generates checklists, validates iteratively.
"""

import sys
import re
import json
from pathlib import Path
from typing import Optional, Dict, List, Any

def require_command_invocation(command_name: str):
    """Guard to prevent direct execution"""
    if "--from-command" not in sys.argv and "--no-guard" not in sys.argv:
        print(f"\n⚠️  Please use the Cursor slash command instead:\n")
        print(f"    /{command_name}\n")
        print(f"This ensures the full AI workflow and validation is triggered.\n")
        print(f"(For testing/debugging, use --no-guard flag to bypass this check)\n")
        sys.exit(1)


# ============================================================================
# FRAMEWORK DETECTION
# ============================================================================

def detect_language(file_path: str) -> Optional[str]:
    """
    Detect programming language from file extension.
    Returns: 'python', 'javascript', or None
    """
    file_path_lower = file_path.lower()
    
    if file_path_lower.endswith(('.py', '.pyi')):
        return 'python'
    elif file_path_lower.endswith(('.js', '.mjs', '.ts', '.tsx', '.jsx')):
        return 'javascript'
    
    return None


# ============================================================================
# RULE FILE LOADING
# ============================================================================

def load_rule_file(language: str) -> Optional[Dict[str, Any]]:
    """
    Load the appropriate language-specific rule file.
    Returns: {"rule_path": str, "content": str, "language": str}
    """
    rule_files = {
        'python': 'clean-code-python-rule.mdc',
        'javascript': 'clean-code-js-rule.mdc'
    }
    
    rule_file = rule_files.get(language)
    if not rule_file:
        return None
    
    rule_path = Path("behaviors/clean-code") / rule_file
    if not rule_path.exists():
        return None
    
    content = rule_path.read_text(encoding='utf-8')
    
    return {
        "rule_path": str(rule_path),
        "content": content,
        "language": language
    }


# ============================================================================
# RULE PARSER - Extract DO/DON'T examples and create checklists
# ============================================================================

class CleanCodeRuleParser:
    """Parse clean code rule files to extract validation checklists"""
    
    def __init__(self):
        self._cache = {}
    
    def get_checklist(self, language: str) -> Dict[str, Any]:
        """Parse rule file and return validation checklist (cached)"""
        if language in self._cache:
            return self._cache[language]
        
        rule_data = load_rule_file(language)
        if not rule_data:
            return {}
        
        sections = self._parse_rule_file(rule_data['content'])
        self._cache[language] = sections
        return sections
    
    def _parse_rule_file(self, content: str) -> Dict[str, Dict[str, Any]]:
        """Parse entire rule file into sections with checklists"""
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            # Match section headers like "## 1. Functions"
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
        # Extract subsections (### 1.1, ### 1.2, etc.)
        subsections = {}
        lines = content.split('\n')
        current_subsection = None
        current_subsection_content = []
        
        for line in lines:
            # Match subsection headers like "### 1.1 Single Responsibility"
            subsection_match = re.match(r'^###\s+(\d+\.\d+)\s+(.+)$', line)
            if subsection_match:
                if current_subsection:
                    subsections[current_subsection['num']] = self._parse_subsection_content(
                        current_subsection['title'],
                        '\n'.join(current_subsection_content)
                    )
                current_subsection = {
                    'num': subsection_match.group(1),
                    'title': subsection_match.group(2).strip()
                }
                current_subsection_content = []
            elif current_subsection:
                current_subsection_content.append(line)
        
        if current_subsection:
            subsections[current_subsection['num']] = self._parse_subsection_content(
                current_subsection['title'],
                '\n'.join(current_subsection_content)
            )
        
        return {
            'title': title,
            'subsections': subsections
        }
    
    def _parse_subsection_content(self, title: str, content: str) -> Dict[str, Any]:
        """Extract principle and examples from subsection"""
        principle_lines = []
        for line in content.split('\n'):
            if '**✅ DO:**' in line or '**❌ DON\'T:**' in line:
                break
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('**'):
                principle_lines.append(stripped)
        
        principle = ' '.join(principle_lines)
        do_examples = self._extract_code_blocks(content, '**✅ DO:**')
        dont_examples = self._extract_code_blocks(content, '**❌ DON\'T:**')
        checks = self._generate_checks_from_examples(title, dont_examples, do_examples)
        
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
                # Skip to next code block
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    i += 1
                
                if i < len(lines):
                    i += 1  # Skip opening ```
                    code_lines = []
                    while i < len(lines) and not lines[i].strip().startswith('```'):
                        code_lines.append(lines[i])
                        i += 1
                    
                    if code_lines:
                        blocks.append('\n'.join(code_lines))
            i += 1
        
        return blocks
    
    def _generate_checks_from_examples(self, title: str, dont_examples: List[str], do_examples: List[str]) -> List[Dict[str, Any]]:
        """Auto-generate validation checks based on title and examples"""
        checks = []
        title_lower = title.lower()
        
        # Generate context-specific checks based on subsection title
        if 'parameter' in title_lower or 'signature' in title_lower:
            checks.append({
                'question': 'Does function have more than 3 parameters?',
                'example_dont': dont_examples[0] if dont_examples else '',
                'example_do': do_examples[0] if do_examples else ''
            })
        
        if 'flag' in title_lower or 'boolean' in title_lower:
            checks.append({
                'question': 'Does function use boolean flag parameters?',
                'keywords': ['bool', 'boolean', 'flag', 'is_', 'has_'],
                'example_dont': dont_examples[0] if dont_examples else '',
                'example_do': do_examples[0] if do_examples else ''
            })
        
        if 'nesting' in title_lower or 'control flow' in title_lower:
            checks.append({
                'question': 'Is nesting deeper than 3 levels?',
                'example_dont': dont_examples[0] if dont_examples else '',
                'example_do': do_examples[0] if do_examples else ''
            })
        
        if 'magic number' in title_lower or 'constant' in title_lower:
            checks.append({
                'question': 'Are there unexplained numeric literals?',
                'example_dont': dont_examples[0] if dont_examples else '',
                'example_do': do_examples[0] if do_examples else ''
            })
        
        if 'duplication' in title_lower or 'dry' in title_lower:
            checks.append({
                'question': 'Is there duplicated logic?',
                'example_dont': dont_examples[0] if dont_examples else '',
                'example_do': do_examples[0] if do_examples else ''
            })
        
        if 'side effect' in title_lower or 'separation' in title_lower or 'pure' in title_lower:
            checks.append({
                'question': 'Does function mix pure logic with side effects?',
                'keywords': ['print', 'console.log', 'logging', 'db.', 'email.', 'file.'],
                'example_dont': dont_examples[0] if dont_examples else '',
                'example_do': do_examples[0] if do_examples else ''
            })
        
        if 'mutable' in title_lower or 'state' in title_lower or 'global' in title_lower:
            checks.append({
                'question': 'Does code use mutable global state?',
                'keywords': ['global ', 'let ', 'var '],
                'example_dont': dont_examples[0] if dont_examples else '',
                'example_do': do_examples[0] if do_examples else ''
            })
        
        if 'encapsulation' in title_lower or 'private' in title_lower:
            checks.append({
                'question': 'Are implementation details exposed publicly?',
                'example_dont': dont_examples[0] if dont_examples else '',
                'example_do': do_examples[0] if do_examples else ''
            })
        
        # If no specific checks matched, create generic check
        if not checks:
            checks.append({
                'question': f'Does code follow {title} principle?',
                'example_dont': dont_examples[0] if dont_examples else '',
                'example_do': do_examples[0] if do_examples else ''
            })
        
        return checks


# Global parser instance
_rule_parser = CleanCodeRuleParser()


# ============================================================================
# CODE STRUCTURE EXTRACTION
# ============================================================================

def extract_functions_from_file(file_path: str, language: str) -> List[Dict[str, Any]]:
    """
    Extract all functions from file with their structure.
    Returns: [{"name": str, "start_line": int, "end_line": int, "code": str, "params": int, "nesting_depth": int}]
    """
    content = Path(file_path).read_text(encoding='utf-8')
    lines = content.split('\n')
    
    functions = []
    
    for i, line in enumerate(lines, 1):
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
            
            # Find function end (next function or end of file)
            func_start = i
            func_end = i
            indent = len(line) - len(line.lstrip())
            
            # Find end of function (next line with same or less indent that starts something new)
            for j in range(i, min(i + 200, len(lines))):
                next_line = lines[j]
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # Found next function or class at same/lower indent
                if j > i and next_indent <= indent and next_line.strip():
                    if re.search(r'^\s*(?:def|class|function|const|let|var)\s+', next_line):
                        func_end = j
                        break
            else:
                func_end = min(i + 100, len(lines))
            
            # Extract function code
            func_code = '\n'.join(lines[func_start-1:func_end])
            
            # Calculate max nesting depth
            max_depth = calculate_max_nesting_depth(func_code)
            
            functions.append({
                'name': func_name,
                'start_line': func_start,
                'end_line': func_end,
                'length': func_end - func_start,
                'param_count': param_count,
                'nesting_depth': max_depth,
                'code': func_code
            })
    
    return functions


def calculate_max_nesting_depth(code: str) -> int:
    """Calculate maximum nesting depth in code block"""
    lines = code.split('\n')
    max_depth = 0
    nesting_keywords = ['if', 'for', 'while', 'try', 'with', 'switch', 'catch']
    
    for line in lines:
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        
        if any(stripped.startswith(keyword) for keyword in nesting_keywords):
            # Detect indent unit (2 or 4 spaces)
            indent_unit = 4 if indent >= 8 and indent % 4 == 0 else 2
            depth = indent // indent_unit
            max_depth = max(max_depth, depth)
    
    return max_depth


def extract_classes_from_file(file_path: str, language: str) -> List[Dict[str, Any]]:
    """
    Extract all classes from file.
    Returns: [{"name": str, "start_line": int, "length": int, "method_count": int}]
    """
    content = Path(file_path).read_text(encoding='utf-8')
    lines = content.split('\n')
    
    classes = []
    
    if language == 'python':
        pattern = r'^\s*class\s+(\w+)'
    else:  # javascript
        pattern = r'^\s*(?:export\s+)?class\s+(\w+)'
    
    for i, line in enumerate(lines, 1):
        match = re.search(pattern, line)
        if match:
            class_name = match.group(1)
            class_start = i
            indent = len(line) - len(line.lstrip())
            
            # Find class end
            class_end = i
            for j in range(i, min(i + 500, len(lines))):
                next_line = lines[j]
                next_indent = len(next_line) - len(next_line.lstrip())
                
                if j > i and next_indent <= indent and next_line.strip():
                    if re.search(r'^\s*class\s+', next_line):
                        class_end = j
                        break
            else:
                class_end = min(i + 500, len(lines))
            
            # Count methods
            class_code = '\n'.join(lines[class_start-1:class_end])
            method_pattern = r'^\s+def\s+' if language == 'python' else r'^\s+\w+\s*\('
            method_count = len(re.findall(method_pattern, class_code, re.MULTILINE))
            
            classes.append({
                'name': class_name,
                'start_line': class_start,
                'length': class_end - class_start,
                'method_count': method_count,
                'code': class_code
            })
    
    return classes


# ============================================================================
# VALIDATION ENGINE - Iterate through code with rule checklists
# ============================================================================

def validate_file(file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate file against clean code principles using rule-based checklists.
    
    Similar to bdd-runner's validate pattern:
    1. Parse rule file to extract DO/DON'T examples
    2. Extract code structure (functions, classes)
    3. Generate validation prompts with checklists
    4. Present to AI for validation
    
    Returns: {"violations": List, "score": int, "summary": Dict}
    """
    file = Path(file_path)
    if not file.exists():
        return {"error": f"File not found: {file_path}"}
    
    # Detect language
    if not language:
        language = detect_language(file_path)
    
    if not language:
        return {"error": f"Unsupported file type: {file_path}"}
    
    print("=" * 60)
    print("CLEAN CODE VALIDATION")
    print("=" * 60)
    print(f"\nFile: {file_path}")
    print(f"Language: {language.upper()}\n")
    
    # Load and parse rule file
    print("Step 1: Loading clean code rules...")
    rule_data = load_rule_file(language)
    if not rule_data:
        return {"error": f"Could not load rules for {language}"}
    
    print(f"✅ Loaded rule: {rule_data['rule_path']}")
    
    # Parse rules into checklist
    print("Step 2: Parsing rules into validation checklists...")
    rules = _rule_parser.get_checklist(language)
    print(f"✅ Parsed {len(rules)} sections with checklists\n")
    
    # Extract code structure
    print("Step 3: Extracting code structure...")
    functions = extract_functions_from_file(file_path, language)
    classes = extract_classes_from_file(file_path, language)
    
    print(f"✅ Found {len(functions)} functions")
    print(f"✅ Found {len(classes)} classes\n")
    
    # Perform static analysis
    print("Step 4: Running static analysis...")
    static_violations = perform_static_analysis(file_path, language, functions, classes)
    print(f"✅ Found {len(static_violations)} static violations\n")
    
    # Present full rule file for AI
    print("=" * 80)
    print("FULL CLEAN CODE RULE FILE - READ THIS")
    print("=" * 80)
    print(f"Language: {language.upper()}")
    print(f"Rule File: {rule_data['rule_path']}")
    print("=" * 80)
    print(rule_data['content'])
    print("=" * 80)
    
    # Present code structure for validation
    print("\n" + "=" * 80)
    print("CODE TO VALIDATE")
    print("=" * 80)
    
    if static_violations:
        print("\n⚠️  STATIC VIOLATIONS DETECTED:")
        for v in static_violations:
            print(f"\n  Line {v['line']}: {v['message']}")
            print(f"  Principle: {v['principle']}")
            print(f"  Suggestion: {v['suggestion']}")
    
    # Show functions for detailed validation
    print("\n" + "=" * 80)
    print("FUNCTIONS TO VALIDATE AGAINST RULES")
    print("=" * 80)
    
    for func in functions[:10]:  # Show first 10 functions
        print(f"\nFunction: {func['name']} (Line {func['start_line']})")
        print(f"  Length: {func['length']} lines")
        print(f"  Parameters: {func['param_count']}")
        print(f"  Max nesting depth: {func['nesting_depth']}")
        
        # Generate checklist for this function
        relevant_sections = []
        if func['length'] > 20:
            relevant_sections.append("1.2 Small and Focused")
        if func['param_count'] > 3:
            relevant_sections.append("1.3 Clear Parameters")
        if func['nesting_depth'] > 3:
            relevant_sections.append("1.4 Simple Control Flow")
        
        if relevant_sections:
            print(f"  ⚠️  Review against: {', '.join(relevant_sections)}")
    
    # Show classes for detailed validation
    if classes:
        print("\n" + "=" * 80)
        print("CLASSES TO VALIDATE AGAINST RULES")
        print("=" * 80)
        
        for cls in classes:
            print(f"\nClass: {cls['name']} (Line {cls['start_line']})")
            print(f"  Length: {cls['length']} lines")
            print(f"  Methods: {cls['method_count']}")
            
            if cls['length'] > 300:
                print(f"  ⚠️  Review against: 6.2 Small and Compact")
            if cls['method_count'] > 10:
                print(f"  ⚠️  Review against: 6.1 Single Responsibility")
    
    # AI validation instructions
    print("\n" + "=" * 80)
    print("AI AGENT: VALIDATE CODE AGAINST ALL RULES")
    print("=" * 80)
    print("\nFor each function and class:")
    print("1. Compare against relevant DO/DON'T examples from rules above")
    print("2. Check for violations of clean code principles")
    print("3. List violations with:")
    print("   - Location (line number, function/class name)")
    print("   - Principle violated")
    print("   - Specific issue")
    print("   - Suggested fix")
    print("4. Categorize by severity (critical/important/suggested)")
    print("\nReport ALL violations found.")
    print("=" * 80)
    
    return {
        "file": file_path,
        "language": language,
        "rules": rules,
        "functions": functions,
        "classes": classes,
        "static_violations": static_violations
    }


def perform_static_analysis(file_path: str, language: str, functions: List[Dict], classes: List[Dict]) -> List[Dict]:
    """Run static analysis checks that don't require AI"""
    violations = []
    content = Path(file_path).read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Check 1: Deep nesting (3 levels)
    for i, line in enumerate(lines, 1):
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        nesting_keywords = ['if', 'for', 'while', 'try', 'with', 'switch', 'catch']
        
        if any(stripped.startswith(keyword) for keyword in nesting_keywords):
            indent_unit = 4 if indent >= 8 and indent % 4 == 0 else 2
            depth = indent // indent_unit
            
            if depth >= 7:
                violations.append({
                    'line': i,
                    'type': 'critical',
                    'principle': '1.4 Simple Control Flow - Keep nesting minimal',
                    'message': f'Excessive nesting (depth {depth})',
                    'suggestion': 'Extract nested blocks into separate functions; use guard clauses'
                })
            elif depth >= 4:
                violations.append({
                    'line': i,
                    'type': 'important',
                    'principle': '1.4 Simple Control Flow - Keep nesting minimal',
                    'message': f'Deep nesting (depth {depth})',
                    'suggestion': 'Consider extracting nested logic or using guard clauses'
                })
            elif depth == 3:
                violations.append({
                    'line': i,
                    'type': 'suggested',
                    'principle': '1.4 Simple Control Flow - Keep nesting minimal',
                    'message': f'Moderate nesting (depth {depth})',
                    'suggestion': 'Consider simplifying if adding more complexity'
                })
    
    # Check 2: Magic numbers
    for i, line in enumerate(lines, 1):
        # Skip comments and strings
        if line.strip().startswith('#') or line.strip().startswith('//'):
            continue
        
        # Find numeric literals (2+ digits)
        if re.search(r'[^a-zA-Z_0-9]\d{2,}', line):
            # Ignore common patterns
            if not re.search(r'(range\(|sleep\(|setTimeout\(|version|20\d{2}|line|column)', line, re.IGNORECASE):
                violations.append({
                    'line': i,
                    'type': 'important',
                    'principle': '2.3 Meaningful Context - Replace magic numbers',
                    'message': 'Magic number detected',
                    'suggestion': 'Replace with named constant'
                })
    
    # Check 3: Single-letter variables (not in loops)
    for i, line in enumerate(lines, 1):
        if re.search(r'\b([d-z])\s*=\s*', line):
            # Ignore loop counters
            if not re.search(r'\bfor\s+\w+\s+in\b', line) and not re.search(r'for\s*\(\s*\w+\s*=', line):
                violations.append({
                    'line': i,
                    'type': 'suggested',
                    'principle': '2.1 Intention-Revealing Names',
                    'message': 'Single-letter variable name',
                    'suggestion': 'Use descriptive name that reveals intent'
                })
    
    # Check 4: Commented-out code
    for i, line in enumerate(lines, 1):
        if re.search(r'^\s*#.*\b(def|class|import|return)\b', line) or \
           re.search(r'^\s*//.*\b(function|const|import|return)\b', line):
            violations.append({
                'line': i,
                'type': 'important',
                'principle': '7.3 Bad Comments - Delete commented-out code',
                'message': 'Commented-out code detected',
                'suggestion': 'Remove (it\'s in git history)'
            })
    
    # Check 5: Large functions
    for func in functions:
        if func['length'] > 50:
            violations.append({
                'line': func['start_line'],
                'type': 'critical',
                'principle': '1.2 Small and Focused Functions',
                'message': f"Function '{func['name']}' is too large ({func['length']} lines)",
                'suggestion': 'Extract into smaller, focused functions'
            })
        elif func['length'] > 20:
            violations.append({
                'line': func['start_line'],
                'type': 'important',
                'principle': '1.2 Small and Focused Functions',
                'message': f"Function '{func['name']}' is large ({func['length']} lines)",
                'suggestion': 'Consider extracting helper functions'
            })
    
    # Check 6: Too many parameters
    for func in functions:
        if func['param_count'] > 3:
            violations.append({
                'line': func['start_line'],
                'type': 'important',
                'principle': '1.3 Clear Parameters',
                'message': f"Function '{func['name']}' has {func['param_count']} parameters",
                'suggestion': 'Use parameter object or split function'
            })
    
    # Check 7: Large classes
    for cls in classes:
        if cls['length'] > 300:
            violations.append({
                'line': cls['start_line'],
                'type': 'critical',
                'principle': '6.2 Small and Compact Classes',
                'message': f"Class '{cls['name']}' is too large ({cls['length']} lines)",
                'suggestion': 'Split into smaller, focused classes'
            })
        elif cls['length'] > 200:
            violations.append({
                'line': cls['start_line'],
                'type': 'important',
                'principle': '6.2 Small and Compact Classes',
                'message': f"Class '{cls['name']}' is large ({cls['length']} lines)",
                'suggestion': 'Consider splitting responsibilities'
            })
    
    return violations


# ============================================================================
# REFACTORING ENGINE
# ============================================================================

def refactor_file(file_path: str, apply: bool = False, language: Optional[str] = None) -> Dict[str, Any]:
    """
    Suggest or apply refactorings based on clean code principles.
    Similar pattern to validation but focused on fixes.
    """
    if not language:
        language = detect_language(file_path)
    
    if not language:
        return {"error": f"Unsupported file type: {file_path}"}
    
    print("=" * 60)
    print("CLEAN CODE REFACTORING")
    print("=" * 60)
    print(f"\nFile: {file_path}")
    print(f"Language: {language.upper()}")
    print(f"Mode: {'AUTO-APPLY' if apply else 'SUGGEST'}\n")
    
    # Run validation first to get violations
    validation_result = validate_file(file_path, language)
    
    if "error" in validation_result:
        return validation_result
    
    static_violations = validation_result.get('static_violations', [])
    
    # Categorize refactorings by safety
    safe_refactorings = [v for v in static_violations if v['type'] in ['suggested', 'important'] 
                        and any(pattern in v['message'] for pattern in ['magic number', 'single-letter', 'commented-out'])]
    suggested_refactorings = [v for v in static_violations if v['type'] in ['important', 'critical'] 
                             and any(pattern in v['message'] for pattern in ['large', 'nesting', 'parameters'])]
    
    print("\n" + "=" * 80)
    print("REFACTORING PLAN")
    print("=" * 80)
    print(f"\n✅ Safe Automated: {len(safe_refactorings)}")
    print(f"⚠️  Suggested (Review): {len(suggested_refactorings)}")
    
    if safe_refactorings:
        print("\n--- Safe Automated Refactorings ---")
        for ref in safe_refactorings:
            print(f"  Line {ref['line']}: {ref['message']}")
            print(f"    → {ref['suggestion']}")
    
    if suggested_refactorings:
        print("\n--- Suggested Refactorings (Need Review) ---")
        for ref in suggested_refactorings:
            print(f"  Line {ref['line']}: {ref['message']}")
            print(f"    → {ref['suggestion']}")
    
    if apply:
        print("\n⚠️  AUTO-APPLY mode not yet implemented")
        print("    Manual refactoring recommended")
    else:
        print("\n💡 Use --apply flag to auto-apply safe refactorings")
    
    print("=" * 80)
    
    return {
        "file": file_path,
        "safe_refactorings": safe_refactorings,
        "suggested_refactorings": suggested_refactorings,
        "total": len(safe_refactorings) + len(suggested_refactorings)
    }


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Main entry point for clean-code runner"""
    
    if len(sys.argv) < 2:
        print("Usage: clean-code-runner.py [validate|refactor] <file> [options]")
        print("\nCommands:")
        print("  validate <file>           Validate code against clean code principles")
        print("  refactor <file> [--apply] Suggest or apply refactorings")
        print("\nOptions:")
        print("  --no-guard               Skip command invocation guard")
        print("  --apply                  Auto-apply safe refactorings (refactor only)")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "validate":
        if len(sys.argv) < 3:
            print("Error: validate requires file path")
            sys.exit(1)
        
        file_path = sys.argv[2]
        result = validate_file(file_path)
        
        if "error" in result:
            print(f"\n❌ Error: {result['error']}")
            sys.exit(1)
        
        # Validation results are printed by validate_file
        sys.exit(0)
    
    elif action == "refactor":
        if len(sys.argv) < 3:
            print("Error: refactor requires file path")
            sys.exit(1)
        
        file_path = sys.argv[2]
        apply_mode = "--apply" in sys.argv
        
        result = refactor_file(file_path, apply=apply_mode)
        
        if "error" in result:
            print(f"\n❌ Error: {result['error']}")
            sys.exit(1)
        
        # Refactoring results are printed by refactor_file
        sys.exit(0)
    
    else:
        print(f"Unknown action: {action}")
        print("Valid actions: validate, refactor")
        sys.exit(1)


if __name__ == "__main__":
    # Fix Windows console encoding for emoji support
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    require_command_invocation("clean-code-validate")
    main()
