#!/usr/bin/env python3
"""
DDD Domain Model Validation Runner

Validates domain maps against DDD principles with automatic violation detection.

Usage:
    python behaviors/ddd/ddd-validate-runner.py <file-path> --no-guard [--thorough] [--fix]
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional


def extract_key_nouns(names: List[str]) -> Dict[str, List[str]]:
    """
    Extract key nouns from domain/concept names.
    Returns dict of {noun: [names containing it]}
    """
    noun_map = {}
    
    # Common key nouns to check for redundancy
    key_words = ['Animation', 'Sequence', 'Script', 'Editor', 'Detection', 
                 'Configuration', 'System', 'Manager', 'Service', 'Handler',
                 'Feedback', 'Result', 'Data', 'Extraction', 'Generation',
                 'Execution', 'Resolution', 'Processing', 'Management',
                 'Controller', 'Provider', 'Factory', 'Builder', 'Repository',
                 'View', 'Model', 'Component', 'Module', 'Engine', 'Framework']
    
    for name in names:
        # Split camelCase/PascalCase and Title Case
        words = re.findall(r'[A-Z][a-z]*|[a-z]+', name)
        # Also split on spaces and hyphens
        words.extend(re.split(r'[\s\-]+', name))
        
        for word in words:
            if word in key_words:
                if word not in noun_map:
                    noun_map[word] = []
                if name not in noun_map[word]:
                    noun_map[word].append(name)
    
    # Return only nouns that appear in multiple names
    return {k: v for k, v in noun_map.items() if len(v) > 1}


def detect_noun_redundancy(content: str) -> List[Dict]:
    """
    Auto-detect noun redundancy violations in domain/concept names.
    Returns list of violations with confidence scores.
    """
    violations = []
    lines = content.split('\n')
    
    # Extract domain names (all caps lines at start, not FUNCTIONAL PURPOSE or RELATIONSHIPS)
    domains = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if (stripped and 
            stripped.isupper() and 
            not stripped.startswith('FUNCTIONAL PURPOSE') and
            not stripped.startswith('RELATIONSHIPS') and
            not stripped.startswith('USES:') and
            not stripped.startswith('SERVES:') and
            not stripped.startswith('CREATES:') and
            not stripped.startswith('CONTAINS:') and
            not stripped.startswith('TRIGGERED BY:') and
            not stripped.startswith('CREATED BY:')):
            domains.append({'name': stripped, 'line': i})
    
    # Extract concept names (Title Case at indentation level 1, not all caps)
    concepts = []
    for i, line in enumerate(lines, 1):
        if line.startswith('\t') and not line.startswith('\t\t'):
            stripped = line.strip()
            # Skip property lines and relationship keywords
            if (stripped and 
                not stripped.isupper() and
                not stripped.startswith('RELATIONSHIPS:') and
                not any(stripped.startswith(kw) for kw in ['USES:', 'SERVES:', 'CREATES:', 'CONTAINS:', 'TRIGGERED BY:', 'CREATED BY:'])):
                # Extract concept name (before parentheses or end of line)
                if '(' in stripped:
                    name = stripped.split('(')[0].strip()
                else:
                    # Take first capitalized phrase
                    words = stripped.split()
                    if words and words[0][0].isupper():
                        name = words[0]
                    else:
                        name = ''
                if name and len(name) > 2:  # Avoid single letters
                    concepts.append({'name': name, 'line': i})
    
    # Check for domain noun redundancy
    if domains:
        domain_names = [d['name'] for d in domains]
        domain_nouns = extract_key_nouns(domain_names)
        
        for noun, affected_names in domain_nouns.items():
            if len(affected_names) >= 3:
                # High confidence - 3+ domains with same noun
                violations.append({
                    'type': 'DOMAIN_NOUN_REDUNDANCY',
                    'principle': '§ 9',
                    'confidence': 'HIGH',
                    'score': 95,
                    'noun': noun,
                    'occurrences': affected_names,
                    'lines': [d['line'] for d in domains if d['name'] in affected_names],
                    'message': f"Domain noun '{noun}' appears in {len(affected_names)} domains: {', '.join(affected_names[:3])}{'...' if len(affected_names) > 3 else ''}"
                })
            elif len(affected_names) == 2:
                # Medium confidence - 2 domains with same noun
                violations.append({
                    'type': 'DOMAIN_NOUN_REDUNDANCY',
                    'principle': '§ 9',
                    'confidence': 'MEDIUM',
                    'score': 70,
                    'noun': noun,
                    'occurrences': affected_names,
                    'lines': [d['line'] for d in domains if d['name'] in affected_names],
                    'message': f"Domain noun '{noun}' appears in 2 domains: {', '.join(affected_names)}"
                })
    
    # Check for concept noun collisions
    if concepts:
        concept_names = [c['name'] for c in concepts]
        concept_nouns = extract_key_nouns(concept_names)
        
        for noun, affected_names in concept_nouns.items():
            if len(affected_names) >= 2:
                violations.append({
                    'type': 'CONCEPT_NOUN_COLLISION',
                    'principle': '§ 9',
                    'confidence': 'MEDIUM',
                    'score': 65,
                    'noun': noun,
                    'occurrences': affected_names,
                    'lines': [c['line'] for c in concepts if c['name'] in affected_names],
                    'message': f"Concept noun '{noun}' appears in {len(affected_names)} concepts: {', '.join(affected_names[:3])}{'...' if len(affected_names) > 3 else ''}"
                })
    
    return violations


def detect_verb_based_concepts(content: str) -> List[Dict]:
    """
    Detect concept names that use verb-based nouns (violates § 7).
    """
    violations = []
    lines = content.split('\n')
    
    # Verb-based noun patterns
    verb_patterns = [
        (r'\b\w+tion\b', 'tion'),  # Generation, Extraction, Resolution, Execution
        (r'\b\w+ing\b', 'ing'),     # Processing, Rendering, Managing
        (r'\bSaving\b', 'Saving'),  # Saving
    ]
    
    for i, line in enumerate(lines, 1):
        if line.startswith('\t') and not line.startswith('\t\t'):
            stripped = line.strip()
            if stripped and not stripped.isupper():
                # Extract concept name
                name = stripped.split('(')[0].strip() if '(' in stripped else stripped.split()[0] if stripped.split() else ''
                
                for pattern, suffix in verb_patterns:
                    if re.search(pattern, name):
                        violations.append({
                            'type': 'VERB_BASED_CONCEPT',
                            'principle': '§ 7',
                            'confidence': 'HIGH',
                            'score': 85,
                            'name': name,
                            'pattern': suffix,
                            'line': i,
                            'message': f"Concept '{name}' uses verb-based noun (ends with '{suffix}'). Should be noun with behavior."
                        })
                        break  # Only flag once per concept
    
    return violations


def detect_enablement_verbs(content: str) -> List[Dict]:
    """
    Detect vague enablement verbs in behaviors (violates § 1).
    """
    violations = []
    lines = content.split('\n')
    
    enablement_verbs = ['Provides', 'Enables', 'Allows', 'Permits', 'Supports']
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        for verb in enablement_verbs:
            if stripped.startswith(verb + ' '):
                violations.append({
                    'type': 'ENABLEMENT_VERB',
                    'principle': '§ 1',
                    'confidence': 'MEDIUM',
                    'score': 70,
                    'verb': verb,
                    'line': i,
                    'text': stripped[:80],
                    'message': f"Line uses vague enablement verb '{verb}'. Use specific outcome verb instead."
                })
                break
    
    return violations


def load_rule_file() -> str:
    """Load the DDD structure analysis rule file"""
    rule_path = Path(__file__).parent / 'ddd-structure-analysis-rule.mdc'
    try:
        with open(rule_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Rule file not found. Using AI knowledge of DDD principles."


def validate_domain_model(file_path: str, thorough: bool = False, fix_mode: bool = False):
    """
    Validate domain model file against DDD principles with auto-detection.
    """
    
    # Load domain map
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1
    
    # Load rule file
    rule_content = load_rule_file()
    
    # AUTO-DETECT violations
    auto_violations = []
    
    # Detect noun redundancy (§ 9)
    auto_violations.extend(detect_noun_redundancy(content))
    
    # Detect verb-based concepts (§ 7)
    auto_violations.extend(detect_verb_based_concepts(content))
    
    # Detect enablement verbs (§ 1)
    auto_violations.extend(detect_enablement_verbs(content))
    
    # Sort by line number
    auto_violations.sort(key=lambda v: v.get('line', v.get('lines', [0])[0]))
    
    # Present results
    print("=" * 70)
    print(f"DDD Domain Map Validation: {os.path.basename(file_path)}")
    print("=" * 70)
    print()
    
    if auto_violations:
        print("AUTO-DETECTED VIOLATIONS:")
        print("-" * 70)
        
        for v in auto_violations:
            confidence_label = f"{v['confidence']} ({v['score']}%)"
            lines_str = f"Line {v['line']}" if 'line' in v else f"Lines {', '.join(map(str, v['lines']))}"
            
            print(f"\n[X] {v['principle']} Violation: {v['type']} [{confidence_label}]")
            print(f"   {lines_str}")
            print(f"   {v['message']}")
            
            if 'occurrences' in v:
                print(f"   Affected names: {', '.join(v['occurrences'][:5])}{'...' if len(v['occurrences']) > 5 else ''}")
            
            if 'text' in v:
                print(f"   Text: {v['text']}")
        
        print()
        print("-" * 70)
        print(f"Total auto-detected violations: {len(auto_violations)}")
        print()
    else:
        print("[OK] No automatic violations detected")
        print()
    
    print("=" * 70)
    print("AI AGENT VALIDATION REQUIRED")
    print("=" * 70)
    print()
    print("The AI Agent must now:")
    print("1. VERIFY auto-detected violations above")
    print("2. VALIDATE against all 9 DDD principles manually:")
    print("   § 1: Outcome verbs (not communication verbs)")
    print("   § 2: System support integrated under domains")
    print("   § 3: Concepts ordered by user mental model")
    print("   § 4: Domain-first organization")
    print("   § 5: Functional purpose stated")
    print("   § 6: Related concepts integrated")
    print("   § 7: Domain concepts are nouns, behaviors are verbs")
    print("   § 8: Behaviors assigned to performer")
    print("   § 9: No noun redundancy in domain/concept names")
    print("3. REPORT all violations (auto + manual)")
    print("4. SUGGEST fixes using DO examples from rule file")
    print()
    
    if thorough:
        print("THOROUGH MODE: AI will provide detailed analysis and suggestions")
        print()
    
    if fix_mode:
        print("FIX MODE: AI will apply corrections automatically")
        print()
    
    print("=" * 70)
    print("DOMAIN MAP CONTENT:")
    print("=" * 70)
    print(content)
    print()
    
    if thorough:
        print("=" * 70)
        print("DDD PRINCIPLES (Rule File):")
        print("=" * 70)
        # Show just the principle headers for space
        for line in rule_content.split('\n'):
            if line.startswith('## ') and any(c.isdigit() for c in line[:10]):
                print(line)
        print()
        print("(Full rule file available - AI will reference for DO/DON'T examples)")
        print()
    
    return 0


def main():
    """Main entry point"""
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print("Usage: python ddd-validate-runner.py <file-path> --no-guard [--thorough] [--fix]")
        print()
        print("Validates domain map files against DDD principles.")
        print()
        print("Arguments:")
        print("  <file-path>    Path to domain map file (*-domain-map.txt)")
        print("  --no-guard     Skip guard check (required for command-line use)")
        print("  --thorough     Detailed analysis with full rule file")
        print("  --fix          Apply fixes automatically (AI mode)")
        print()
        print("Examples:")
        print("  python behaviors/ddd/ddd-validate-runner.py demo/mm3e-animations/mm3e-animations-domain-map.txt --no-guard")
        print("  python behaviors/ddd/ddd-validate-runner.py my-domain-map.txt --no-guard --thorough")
        print()
        return 0
    
    file_path = sys.argv[1]
    thorough = "--thorough" in sys.argv
    fix_mode = "--fix" in sys.argv
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return 1
    
    return validate_domain_model(file_path, thorough, fix_mode)


if __name__ == "__main__":
    sys.exit(main())
