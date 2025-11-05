"""
BDD Test File Validation
Validates actual test files against BDD principles using AI semantic analysis.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

# Step 2: Detect framework from file path
def detect_framework_from_file(file_path: str) -> Optional[str]:
    """
    Match file path against rule glob patterns to determine framework.
    Returns: 'jest', 'mamba', or None
    """
    file_path_lower = file_path.lower()
    
    # Jest patterns
    jest_patterns = ['.test.js', '.spec.js', '.test.ts', '.spec.ts', 
                     '.test.jsx', '.spec.jsx', '.test.tsx', '.spec.tsx',
                     '.test.mjs', '.spec.mjs']  # ES modules
    
    # Mamba patterns  
    mamba_patterns = ['_test.py', 'test_', '_spec.py', 'spec_', 
                      '_test.pyi', 'test_.pyi', '_spec.pyi', 'spec_.pyi']
    
    for pattern in jest_patterns:
        if file_path_lower.endswith(pattern):
            return 'jest'
    
    for pattern in mamba_patterns:
        if pattern in file_path_lower:
            return 'mamba'
    
    return None


# Step 3: Load framework-specific rule file
def load_rule_file(framework: str) -> Dict[str, Any]:
    """
    Load the appropriate framework-specific rule file.
    Returns: {"rule_path": Path, "content": str, "framework": str}
    """
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


# Step 4: Extract DO and DON'T examples by section
def extract_dos_and_donts(rule_content: str) -> Dict[str, Dict[str, List[str]]]:
    """
    Extract DO and DON'T examples from each section (§1-5) of the rule.
    Returns: {"section_name": {"dos": [...], "donts": [...]}}
    """
    import re
    
    sections = {}
    current_section = None
    
    lines = rule_content.split('\n')
    for i, line in enumerate(lines):
        # Detect section headers (## 1. Section Name)
        section_match = re.match(r'^##\s+(\d+)\.\s+(.+)$', line)
        if section_match:
            section_num = section_match.group(1)
            section_name = section_match.group(2).strip()
            current_section = f"{section_num}. {section_name}"
            sections[current_section] = {"dos": [], "donts": []}
        
        # Extract DO examples
        if '**✅ DO:**' in line or '**DO:**' in line:
            # Find code block after this
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
        
        # Extract DON'T examples
        if '**❌ DON\'T:**' in line or '**DON\'T:**' in line or "**DON'T:**" in line:
            # Find code block after this
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


def load_rule_examples(test_file_path: str) -> Dict[str, Any]:
    """
    Master function: Load rule file and extract DO/DON'T examples for a test file.
    
    Combines: detect_framework_from_file() + load_rule_file() + extract_dos_and_donts()
    
    Args:
        test_file_path: Path to test file
        
    Returns:
        {
            "framework": "jest" or "mamba",
            "rule_file": "bdd-jest-rule.mdc" or "bdd-mamba-rule.mdc",
            "examples": {"section_name": {"dos": [...], "donts": [...]}}
        }
    """
    # Step 1: Detect framework
    framework = detect_framework_from_file(test_file_path)
    if not framework:
        return {"error": "Could not detect framework from file path"}
    
    # Step 2: Load rule file
    rule_data = load_rule_file(framework)
    if not rule_data:
        return {"error": f"Could not load rule file for framework: {framework}"}
    
    # Step 3: Extract DO/DON'T examples
    examples = extract_dos_and_donts(rule_data["content"])
    
    return {
        "framework": framework,
        "rule_file": rule_data["rule_path"],
        "examples": examples
    }


# Step 4b: Load reference file for thorough mode
def load_reference_file(framework: str) -> Optional[str]:
    """
    Load detailed examples from reference file for thorough validation.
    Returns: reference file content or None
    """
    reference_files = {
        'jest': 'bdd-jest-reference.md',
        'mamba': 'bdd-mamba-reference.md'
    }
    
    ref_file = reference_files.get(framework)
    if not ref_file:
        return None
    
    ref_path = Path("behaviors/bdd") / ref_file
    if not ref_path.exists():
        return None
    
    return ref_path.read_text(encoding='utf-8')


# Step 5: Extract test structure and chunk by describe blocks
def extract_test_structure_chunks(test_file_path: str, framework: str, max_chunk_size: int = 8000) -> List[Dict[str, Any]]:
    """
    Extract test structure and chunk by describe blocks for manageable AI processing.
    
    Strategy:
    - Start at top-level describe blocks
    - If a describe block is too large, chunk its children
    - Each chunk includes context (parent describes) + content
    
    Returns: [{"start_line": int, "end_line": int, "context": str, "structure": str}]
    """
    import re
    
    content = Path(test_file_path).read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # First pass: extract all describe/it blocks with nesting level
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
                        "full_line": line
                    })
            
            # Extract it/test blocks
            elif 'it(' in line or 'test(' in line:
                match = re.search(r"(?:it|test)\(['\"]([^'\"]+)['\"]", line)
                if match:
                    blocks.append({
                        "line": i,
                        "type": "it",
                        "text": match.group(1),
                        "indent": indent,
                        "full_line": line
                    })
    
    # Group blocks into describe sections
    chunks = []
    current_chunk = []
    current_describes = []  # Stack of active describe contexts
    chunk_start_line = 1
    
    for block in blocks:
        # Manage describe stack based on indentation
        while current_describes and block["indent"] <= current_describes[-1]["indent"]:
            current_describes.pop()
        
        if block["type"] == "describe":
            current_describes.append(block)
            
            # Check if we should start a new chunk at this describe
            if len(current_chunk) > 0 and block["indent"] == 0:  # Top-level describe
                # Save current chunk
                chunk_text = '\n'.join([f"Line {b['line']}: {' ' * b['indent']}{b['type']}('{b['text']}', ...)" for b in current_chunk])
                if len(chunk_text) < max_chunk_size or len(chunks) == 0:
                    context = ' > '.join([d['text'] for d in current_describes[:-1]]) if len(current_describes) > 1 else ''
                    chunks.append({
                        "start_line": chunk_start_line,
                        "end_line": current_chunk[-1]["line"] if current_chunk else chunk_start_line,
                        "context": context,
                        "structure": chunk_text
                    })
                
                # Start new chunk
                current_chunk = [block]
                chunk_start_line = block["line"]
            else:
                current_chunk.append(block)
        else:
            current_chunk.append(block)
    
    # Add final chunk
    if current_chunk:
        chunk_text = '\n'.join([f"Line {b['line']}: {' ' * b['indent']}{b['type']}('{b['text']}', ...)" for b in current_chunk])
        context = ' > '.join([d['text'] for d in current_describes[:-1]]) if len(current_describes) > 1 else ''
        chunks.append({
            "start_line": chunk_start_line,
            "end_line": current_chunk[-1]["line"] if current_chunk else chunk_start_line,
            "context": context,
            "structure": chunk_text
        })
    
    return chunks


# Step 5b: Perform minimal static checks
def perform_static_checks(test_structure: str, framework: str) -> List[Dict[str, Any]]:
    """
    Perform MINIMAL static analysis - only obvious violations.
    Returns: [{"line": int, "issue": str, "type": "error|warning"}]
    """
    issues = []
    import re
    
    for line in test_structure.split('\n'):
        if not line.strip():
            continue
        
        # Extract line number
        line_match = re.match(r'Line (\d+):', line)
        if not line_match:
            continue
        
        line_num = int(line_match.group(1))
        
        # Check for camelCase identifiers in describe() (very obvious technical violation)
        if 'describe(' in line:
            desc_match = re.search(r"describe\(['\"]([^'\"]+)['\"]", line)
            if desc_match:
                desc_text = desc_match.group(1)
                if re.search(r'[a-z]+[A-Z]', desc_text):  # has camelCase
                    issues.append({
                        "line": line_num,
                        "issue": f"describe() uses camelCase (technical identifier): '{desc_text}'",
                        "type": "error",
                        "rule": "1. Business Readable Language"
                    })
        
        # Check for missing "should" in it()
        if framework == 'jest':
            if "it('" in line or 'it("' in line:
                match = re.search(r"it\(['\"]([^'\"]+)['\"]", line)
                if match:
                    desc = match.group(1)
                    if not desc.strip().lower().startswith('should'):
                        issues.append({
                            "line": line_num,
                            "issue": f"it() missing 'should' prefix: '{desc}'",
                            "type": "error",
                            "rule": "1. Business Readable Language"
                        })
        
        elif framework == 'mamba':
            if "with it(" in line:
                match = re.search(r"with it\(['\"]([^'\"]+)['\"]", line)
                if match:
                    desc = match.group(1)
                    if not desc.strip().lower().startswith('should'):
                        issues.append({
                            "line": line_num,
                            "issue": f"it() missing 'should' prefix: '{desc}'",
                            "type": "error",
                            "rule": "1. Business Readable Language"
                        })
    
    return issues


# Step 6-7: Load reference examples for thorough mode
def load_relevant_reference_examples(framework: str, sections_to_check: List[str]) -> Dict[str, str]:
    """
    Load specific sections from reference file for detailed validation.
    
    Args:
        framework: 'jest' or 'mamba'
        sections_to_check: List of section names to extract
    
    Returns: {"section_name": "reference_content"}
    """
    ref_content = load_reference_file(framework)
    if not ref_content:
        return {}
    
    import re
    
    # Extract specific sections from reference
    section_examples = {}
    lines = ref_content.split('\n')
    current_section = None
    section_content = []
    
    for line in lines:
        # Check for section headers
        header_match = re.match(r'^##\s+(.+)$', line)
        if header_match:
            # Save previous section
            if current_section and section_content:
                section_examples[current_section] = '\n'.join(section_content)
            
            current_section = header_match.group(1).strip()
            section_content = [line]
        elif current_section:
            section_content.append(line)
    
    # Save final section
    if current_section and section_content:
        section_examples[current_section] = '\n'.join(section_content)
    
    return section_examples


# Main validation orchestrator
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
    framework = detect_framework_from_file(file_path)
    if not framework:
        print(f"❌ File doesn't match BDD test patterns: {file_path}")
        print("   Expected: *.test.js, *.spec.ts, test_*.py, etc.")
        return {"error": "Not a BDD test file"}
    
    print(f"✅ Detected framework: {framework.upper()}")
    
    # Step 3: Load rule file
    print(f"Step 3: Loading {framework} rule file...")
    rule_data = load_rule_file(framework)
    if not rule_data:
        print(f"❌ Could not load rule file for {framework}")
        return {"error": "Rule file not found"}
    
    print(f"✅ Loaded rule: {rule_data['rule_path']}")
    
    # Step 4: Extract DO/DON'T examples - ALWAYS use ALL sections
    print("Step 4: Extracting DO/DON'T examples...")
    sections = extract_dos_and_donts(rule_data['content'])
    print(f"   Validating all sections (§ 1-5) - rules apply at all phases")
    
    total_dos = sum(len(s['dos']) for s in sections.values())
    total_donts = sum(len(s['donts']) for s in sections.values())
    print(f"✅ Extracted {total_dos} DO examples and {total_donts} DON'T examples from {len(sections)} sections")
    
    # Step 5: Extract test structure in manageable chunks
    print("Step 5: Extracting test structure (chunked by describe blocks)...")
    chunks = extract_test_structure_chunks(file_path, framework)
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
        "static_issues": static_issues
    }
    
    return validation_data


if __name__ == "__main__":
    import sys
    import io
    
    # Guard: Require command invocation
    from runner_guard import require_command_invocation
    
    # Allow --no-guard flag for testing
    if '--no-guard' not in sys.argv:
        require_command_invocation("bdd-validate")
    else:
        sys.argv.remove('--no-guard')
    
    # Fix Windows console encoding
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print("BDD Validation Tool Starting...")
    
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    thorough = '--thorough' in sys.argv
    phase = 'implementation'  # Default to full validation
    
    # Check for --phase flag
    for arg in sys.argv:
        if arg.startswith('--phase='):
            phase = arg.split('=')[1]
    
    if not file_path:
        print("Usage: python behaviors/bdd/bdd-validate-runner.py <test-file-path> [--phase=signatures|implementation] [--thorough]")
        print("\nPhases:")
        print("  --phase=signatures      Phase 0: Only validate § 1 (Business Readable Language)")
        print("  --phase=implementation  Phase 1+: Validate all sections (§ 1-5) [DEFAULT]")
        print("\nExamples:")
        print("  python behaviors/bdd/bdd-validate-runner.py test.js --phase=signatures")
        print("  python behaviors/bdd/bdd-validate-runner.py test.js --phase=implementation")
        print("  python behaviors/bdd/bdd-validate-runner.py test.py --thorough")
        sys.exit(1)
    
    print(f"Validating: {file_path}")
    
    try:
        validation_data = bdd_validate_test_file(file_path, thorough, phase)
        
        if "error" in validation_data:
            print(f"\n❌ Validation failed: {validation_data['error']}")
            sys.exit(1)
        
        # Validation complete - AI has the rules and test code above
        print(f"\n✅ Validation runner complete")
        print(f"   Static issues found: {len(validation_data['static_issues'])}")
        print(f"   AI Agent: Review rules above and validate all tests")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
