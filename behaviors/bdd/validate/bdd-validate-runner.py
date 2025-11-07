#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BDD Test Validator with Iterative Semantic Analysis

Validates test files against BDD principles with two modes:
- Iterative (default): Section-by-section validation in chunks with AI feedback
- Batch (--batch): All sections at once for comprehensive review

Features:
- Dynamic rule parsing to generate validation checklists
- Auto-extraction of technical jargon from DON'T examples
- Mandatory structured prompts for AI validation
- Cross-section validation for systemic issues
"""

import re
import sys
import io
from pathlib import Path
from typing import Dict, List, Optional, Any

# Set UTF-8 encoding for stdout on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Import existing utilities from bdd-runner.py (using importlib for hyphenated name)
import importlib.util

_runner_path = Path(__file__).parent.parent / "bdd-runner.py"
_spec = importlib.util.spec_from_file_location("bdd_runner", _runner_path)
_bdd_runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bdd_runner)

# Import functions
detect_framework_from_file = _bdd_runner.detect_framework_from_file
discover_domain_maps = _bdd_runner.discover_domain_maps
load_rule_file = _bdd_runner.load_rule_file
extract_dos_and_donts = _bdd_runner.extract_dos_and_donts
extract_test_structure_chunks = _bdd_runner.extract_test_structure_chunks


# ============================================================================
# RULE PARSING - Generate validation checklists from .mdc files
# ============================================================================

class RuleParser:
    """Parse BDD rule files to extract validation checklists"""
    
    def __init__(self):
        self._cache = {}
    
    def get_checklist(self, framework: str) -> Dict[str, Any]:
        """Parse rule file and return validation checklist (cached)"""
        if framework in self._cache:
            return self._cache[framework]
        
        # Load rule file content (reuse existing function)
        rule_data = load_rule_file(framework)
        if not rule_data:
            return {}
        
        sections = self._parse_rule_file(rule_data['content'])
        
        self._cache[framework] = sections
        return sections
    
    def _parse_rule_file(self, content: str) -> Dict[str, Dict[str, Any]]:
        """Parse entire rule file into sections with checklists"""
        import re
        
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            # Detect section headers (## 1. Section Name)
            section_match = re.match(r'^##\s+(\d+)\.\s+(.+)$', line)
            if section_match:
                # Save previous section
                if current_section:
                    sections[current_section['num']] = self._parse_section_content(
                        current_section['title'],
                        '\n'.join(current_content)
                    )
                
                # Start new section
                current_section = {
                    'num': section_match.group(1),
                    'title': section_match.group(2).strip()
                }
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section['num']] = self._parse_section_content(
                current_section['title'],
                '\n'.join(current_content)
            )
        
        return sections
    
    def _parse_section_content(self, title: str, content: str) -> Dict[str, Any]:
        """Extract principle, checks, and examples from section content"""
        
        # Extract principle (first paragraph before DO/DON'T)
        principle_lines = []
        for line in content.split('\n'):
            if '**✅ DO:**' in line or '**❌ DON\'T:**' in line or line.startswith('##'):
                break
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                principle_lines.append(stripped)
        
        principle = ' '.join(principle_lines)
        
        # Extract DO and DON'T examples
        do_examples = self._extract_code_blocks(content, '**✅ DO:**')
        dont_examples = self._extract_code_blocks(content, '**❌ DON\'T:**')
        
        # Generate checks from DON'T examples
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
                # Find code block after this marker
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    i += 1
                
                if i < len(lines):
                    # Start of code block
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
        
        # Extract jargon keywords from all DON'T examples
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
        
        # Check for action verbs
        verbs = self._extract_action_verbs(dont_examples)
        if verbs:
            checks.append({
                'question': 'Uses nouns (not verbs)?',
                'keywords': verbs,
                'example_dont': next((d for d in dont_examples if any(v in d for v in verbs)), ''),
                'example_do': do_examples[0] if do_examples else ''
            })
        
        # Check for missing "should"
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
        
        # Technical verbs
        tech_verbs = ['extract', 'parse', 'serialize', 'deserialize', 'get', 'set',
                      'fetch', 'retrieve', 'call', 'return', 'handle', 'process']
        
        # Technical nouns
        tech_nouns = ['flag', 'id', 'hook', 'handler', 'callback', 'listener',
                      'message', 'event', 'data', 'payload', 'api', 'endpoint',
                      'request', 'response', 'function', 'method', 'class', 'module']
        
        # Extract from describe/it strings
        matches = re.findall(r"(?:describe|it)\(['\"]([^'\"]+)['\"]", code_example)
        
        for match in matches:
            words = match.split()
            for word in words:
                word_lower = word.lower().strip('(),;')
                
                # Check for camelCase (implementation detail)
                if re.match(r'^[a-z]+[A-Z]', word):
                    jargon_words.append(word)
                
                # Check for technical verbs
                elif word_lower in tech_verbs:
                    jargon_words.append(word_lower)
                
                # Check for technical nouns
                elif word_lower in tech_nouns:
                    jargon_words.append(word_lower)
        
        # Also look in comments for examples in parentheses
        # e.g., "DON'T: Include technical jargon (flags/IDs)"
        paren_matches = re.findall(r'\(([^)]+)\)', code_example)
        for match in paren_matches:
            if 'don\'t' in code_example.lower()[:code_example.find(match)]:
                words = re.split(r'[,/\s]+', match)
                jargon_words.extend([w.strip().lower() for w in words if w.strip()])
        
        return list(set(jargon_words))
    
    def _extract_action_verbs(self, dont_examples: List[str]) -> List[str]:
        """Extract action verbs from DON'T examples"""
        verbs = set()
        
        # Common action verbs in tests
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
# BLOCK EXTRACTION - Parse test file structure
# ============================================================================

def parse_structure_to_blocks(chunk: Dict[str, Any]) -> List[Dict[str, str]]:
    """Convert structure chunk to list of block dicts"""
    blocks = []
    
    structure_lines = chunk.get('structure', '').split('\n')
    for line in structure_lines:
        # Parse lines like:
        # Jest: "  Line 123: describe('something', () => {"
        # Mamba: "  Line 123: with description('something'):"
        jest_match = re.match(r'\s*Line (\d+):\s+(describe|it)\(["\']([^"\']+)', line)
        mamba_match = re.match(r'\s*Line (\d+):\s+with\s+(description|context|it)\(["\']([^"\']+)', line)
        
        if jest_match:
            blocks.append({
                'line': int(jest_match.group(1)),
                'type': jest_match.group(2),
                'text': jest_match.group(3)
            })
        elif mamba_match:
            block_type = 'describe' if mamba_match.group(1) in ['description', 'context'] else 'it'
            blocks.append({
                'line': int(mamba_match.group(1)),
                'type': block_type,
                'text': mamba_match.group(3)
            })
    
    return blocks


# ============================================================================
# PROMPT GENERATION - Structured AI validation prompts
# ============================================================================

def generate_section_prompt(block: Dict[str, str], section_num: str, 
                           section_rules: Dict[str, Any], domain_map: Optional[Dict] = None) -> str:
    """Generate structured prompt with mandatory checklist"""
    
    prompt = f"""
Block: Line {block['line']} - "{block['text']}"

VALIDATE AGAINST § {section_num}: {section_rules['title']}

Principle: {section_rules['principle'][:200]}...

MANDATORY CHECKLIST (answer ALL):
"""
    
    for check in section_rules.get('checks', []):
        prompt += f"\n□ {check['question']}"
        if check.get('keywords'):
            keywords = check['keywords'][:8]
            prompt += f"\n  Keywords to avoid: {', '.join(keywords)}"
        
        if check.get('example_dont'):
            dont_snippet = check['example_dont'].replace('\n', ' ')[:120]
            prompt += f"\n  ❌ DON'T: {dont_snippet}..."
        
        if check.get('example_do'):
            do_snippet = check['example_do'].replace('\n', ' ')[:120]
            prompt += f"\n  ✅ DO: {do_snippet}..."
    
    if domain_map and domain_map.get('found'):
        if domain_map.get('domain_map'):
            # Extract a few concepts from domain map
            map_content = domain_map['domain_map'].get('content', '')
            concepts = re.findall(r'^[A-Z][A-Za-z\s]+(?=:|\n)', map_content, re.MULTILINE)[:5]
            if concepts:
                prompt += f"\n\nDomain Terms Available: {', '.join(concepts)}"
    
    prompt += "\n\nRESPOND: violations: [list any found]"
    return prompt


def generate_cross_section_prompt(all_violations: List) -> str:
    """Generate final prompt for cross-section validation"""
    
    prompt = f"""
FINAL CROSS-SECTION VALIDATION

You've validated across §1-§5.

Now check for issues that span MULTIPLE sections:

□ Do violations in different sections indicate systemic issues?
  (e.g., jargon in §1 + implementation details in §4 = not domain-focused)

□ Are there patterns across sections suggesting missing abstractions?
  (e.g., duplicate setup in §3 + testing internals in §2 = need helper)

□ Do §4 layer violations conflict with §1 readability?
  (e.g., "front-end" tests using business logic language)

RESPOND: cross_section_issues: [list any found]
"""
    return prompt


# ============================================================================
# VALIDATION MODES
# ============================================================================

def validate_iterative(test_file: str, framework: str, chunk_size: int = 10, cursor_mode: bool = False) -> List:
    """
    Iterative mode (DEFAULT):
    - Validate section-by-section (§1-§5)
    - Process chunks of blocks at a time
    - Pause for AI response between chunks
    - Final cross-section validation
    """
    
    print("="*60)
    print("BDD VALIDATOR - ITERATIVE MODE")
    print("="*60)
    
    # Parse rules once
    print("\nParsing BDD rules...")
    rules = _rule_parser.get_checklist(framework)
    
    if not rules:
        print(f"[ERROR] Could not parse rules for {framework}")
        return []
    
    print(f"[OK] Parsed {len(rules)} sections with validation checklists")
    
    # Extract blocks
    print(f"\nExtracting test structure from {Path(test_file).name}...")
    chunks = extract_test_structure_chunks(test_file, framework)
    all_blocks = []
    for chunk in chunks:
        all_blocks.extend(parse_structure_to_blocks(chunk))
    
    print(f"[OK] Found {len(all_blocks)} test blocks")
    
    # Discover domain map
    domain_map = discover_domain_maps(test_file)
    if domain_map.get('found'):
        print("[OK] Found domain maps for context")
    
    print(f"\nValidating against {len(rules)} sections")
    print(f"Chunk size: {chunk_size} blocks\n")
    
    # NEW: Show ALL section rules as one-liners FIRST
    print("="*60)
    print("ALL SECTION RULES (Review BEFORE validating)")
    print("="*60)
    for section_num in sorted(rules.keys()):
        section = rules[section_num]
        principle = section.get('principle', 'N/A')
        # Truncate principle to first 80 chars
        principle_short = principle[:80] + "..." if len(principle) > 80 else principle
        
        print(f"\n§ {section_num}: {section['title']}")
        print(f"   Principle: {principle_short}")
        
        if section.get('checklist'):
            print(f"   Checklist items: {len(section['checklist'])}")
            # Show first 3 checklist items
            for i, item in enumerate(section['checklist'][:3]):
                item_short = item[:70] + "..." if len(item) > 70 else item
                print(f"     □ {item_short}")
            if len(section['checklist']) > 3:
                print(f"     ... ({len(section['checklist']) - 3} more)")
    
    print("\n" + "="*60)
    print("AI: Review all 5 sections above to understand full context")
    print("    This prevents fixing one section and violating another")
    print("="*60)
    
    if not cursor_mode:
        input("\nPress ENTER to begin section-by-section validation... ")
    else:
        print("\n[Cursor mode: Proceeding to section-by-section validation]\n")
    
    all_violations = []
    
    # Validate each section
    for section_num in sorted(rules.keys()):
        violations = validate_section_iterative(
            all_blocks, section_num, rules[section_num], 
            chunk_size, domain_map, cursor_mode
        )
        all_violations.extend(violations)
    
    # FINAL PASS: Cross-section validation
    print("\n" + "="*60)
    print("FINAL PASS: CROSS-SECTION VALIDATION")
    print("="*60 + "\n")
    
    cross_prompt = generate_cross_section_prompt(all_violations)
    print(cross_prompt)
    print("\nAI: Review all violations above for cross-section issues\n")
    
    if not cursor_mode:
        input("   Press ENTER when complete... ")
    
    print("\n" + "="*60)
    print("[COMPLETE] VALIDATION COMPLETE")
    print("="*60)
    return all_violations


def validate_section_iterative(blocks: List[Dict], section_num: str, 
                               section_rules: Dict, chunk_size: int,
                               domain_map: Dict, cursor_mode: bool = False) -> List:
    """Validate all blocks for one section in chunks"""
    
    print(f"\n{'='*60}")
    print(f"§ {section_num}: {section_rules['title']}")
    print(f"{'='*60}\n")
    
    violations = []
    total_chunks = (len(blocks) + chunk_size - 1) // chunk_size
    
    for chunk_idx in range(total_chunks):
        start = chunk_idx * chunk_size
        end = min(start + chunk_size, len(blocks))
        chunk = blocks[start:end]
        
        print(f"\n[Chunk {chunk_idx+1}/{total_chunks}] {len(chunk)} blocks:\n")
        
        for i, block in enumerate(chunk, start=start+1):
            prompt = generate_section_prompt(block, section_num, section_rules, domain_map)
            print(f"Block {i}/{len(blocks)}: Line {block['line']}")
            print(prompt)
            print()
        
        print("-"*60)
        print(f"AI: Validate above {len(chunk)} blocks against Section {section_num}")
        print(f"    Report violations in chat")
        print("-"*60 + "\n")
        
        if not cursor_mode and chunk_idx < total_chunks - 1:
            input("   Press ENTER to continue to next chunk... ")
    
    print(f"\n[DONE] Section {section_num} Complete\n")
    return violations


def validate_batch(test_file: str, framework: str) -> List:
    """
    Batch mode (via --batch flag):
    - Show ALL prompts at once
    - AI validates entire file in one response
    - Then cross-section validation
    """
    
    print("="*60)
    print("BDD VALIDATOR - BATCH MODE")
    print("="*60)
    
    # Parse rules
    print("\nParsing BDD rules...")
    rules = _rule_parser.get_checklist(framework)
    
    if not rules:
        print(f"[ERROR] Could not parse rules for {framework}")
        return []
    
    print(f"[OK] Parsed {len(rules)} sections")
    
    # Extract blocks
    print(f"\nExtracting test structure from {Path(test_file).name}...")
    chunks = extract_test_structure_chunks(test_file, framework)
    all_blocks = []
    for chunk in chunks:
        all_blocks.extend(parse_structure_to_blocks(chunk))
    
    print(f"[OK] Found {len(all_blocks)} test blocks\n")
    
    domain_map = discover_domain_maps(test_file)
    
    # Output all sections at once
    for section_num in sorted(rules.keys()):
        print(f"\n{'='*60}")
        print(f"§ {section_num}: {rules[section_num]['title']}")
        print(f"{'='*60}\n")
        
        for block in all_blocks:
            prompt = generate_section_prompt(block, section_num, rules[section_num], domain_map)
            print(prompt)
            print()
    
    # Final cross-section
    print("\n" + "="*60)
    print("FINAL: CROSS-SECTION VALIDATION")
    print("="*60 + "\n")
    print(generate_cross_section_prompt([]))
    
    print("\nAI: Validate all blocks against all sections above\n")
    
    return []


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='BDD Test Validator with Iterative Semantic Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Iterative mode (default) - validates section-by-section
  python bdd-validate-runner.py demo/mm3e-animations/mm3e-effects-section.test.mjs
  
  # Batch mode - all sections at once
  python bdd-validate-runner.py demo/mm3e-animations/mm3e-effects-section.test.mjs --batch
  
  # Custom chunk size
  python bdd-validate-runner.py my-test.mjs --chunk-size 5
        """
    )
    
    parser.add_argument('file_path', help='Test file to validate')
    parser.add_argument('--batch', action='store_true', 
                       help='Batch mode (all at once) instead of iterative')
    parser.add_argument('--chunk-size', type=int, default=10,
                       help='Blocks per chunk in iterative mode (default: 10)')
    parser.add_argument('--cursor', action='store_true',
                       help='Cursor mode (non-interactive, outputs all prompts at once)')
    parser.add_argument('--no-guard', action='store_true',
                       help='Skip file existence check')
    
    args = parser.parse_args()
    
    # Check file exists
    if not args.no_guard:
        test_path = Path(args.file_path)
        if not test_path.exists():
            print(f"[ERROR] File not found: {args.file_path}")
            sys.exit(1)
    
    # Detect framework
    print(f"Analyzing {args.file_path}...")
    framework = detect_framework_from_file(args.file_path)
    
    if not framework:
        print(f"[ERROR] Could not detect test framework from file path")
        print(f"        Expected Jest (.test.js, .spec.js, etc.) or Mamba (_test.py, test_*.py)")
        sys.exit(1)
    
    print(f"[OK] Detected framework: {framework}\n")
    
    # Run validation in selected mode
    if args.batch:
        validate_batch(args.file_path, framework)
    else:
        validate_iterative(args.file_path, framework, args.chunk_size, cursor_mode=args.cursor)


if __name__ == '__main__':
    main()

