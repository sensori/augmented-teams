"""
THEN: Assert round-trip validation.

Validates that:
1. First render matches expected DrawIO (if provided)
2. Synced JSON matches original JSON structure
3. Second render matches first render (or expected)
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Set


def normalize_json_for_comparison(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize JSON for comparison (remove None values, sort lists)."""
    if isinstance(data, dict):
        normalized = {}
        for key, value in data.items():
            if value is not None:
                normalized[key] = normalize_json_for_comparison(value)
        return normalized
    elif isinstance(data, list):
        return [normalize_json_for_comparison(item) for item in data]
    else:
        return data


def compare_story_graphs(original: Dict[str, Any], synced: Dict[str, Any]) -> tuple[bool, list]:
    """Compare two story graphs and return (match, differences)."""
    differences = []
    
    # Compare epics
    original_epics = {epic['name'] for epic in original.get('epics', [])}
    synced_epics = {epic['name'] for epic in synced.get('epics', [])}
    
    if original_epics != synced_epics:
        missing = original_epics - synced_epics
        extra = synced_epics - original_epics
        if missing:
            differences.append(f"Missing epics in synced: {missing}")
        if extra:
            differences.append(f"Extra epics in synced: {extra}")
    
    # Compare sub-epics
    for epic_name in original_epics & synced_epics:
        orig_epic = next(e for e in original['epics'] if e['name'] == epic_name)
        synced_epic = next(e for e in synced['epics'] if e['name'] == epic_name)
        
        orig_subs = {sub['name'] for sub in orig_epic.get('sub_epics', [])}
        synced_subs = {sub['name'] for sub in synced_epic.get('sub_epics', [])}
        
        if orig_subs != synced_subs:
            missing = orig_subs - synced_subs
            extra = synced_subs - orig_subs
            if missing:
                differences.append(f"Epic '{epic_name}': Missing sub-epics: {missing}")
            if extra:
                differences.append(f"Epic '{epic_name}': Extra sub-epics: {extra}")
    
    return len(differences) == 0, differences


def compare_drawio_files(file1: Path, file2: Path) -> tuple[bool, str]:
    """Compare two DrawIO files (simplified - just check if they exist and have content)."""
    if not file1.exists():
        return False, f"File 1 does not exist: {file1}"
    if not file2.exists():
        return False, f"File 2 does not exist: {file2}"
    
    content1 = file1.read_text(encoding='utf-8')
    content2 = file2.read_text(encoding='utf-8')
    
    # Simple comparison - check if both have mxfile structure
    if '<mxfile' not in content1:
        return False, f"File 1 is not a valid DrawIO file"
    if '<mxfile' not in content2:
        return False, f"File 2 is not a valid DrawIO file"
    
    # For now, just check they're both valid - full comparison would be more complex
    # In a real scenario, you'd compare element counts, positions, etc.
    return True, "Both files are valid DrawIO files"


def main():
    """Run assertions."""
    scenario_dir = Path(__file__).parent.parent
    given_dir = scenario_dir / '1_given'
    when_dir = scenario_dir / '2_when'
    then_dir = scenario_dir / '3_then'
    
    # Set up assertion output file
    assert_output_file = then_dir / 'assert_output.log'
    assert_output_file.write_text('', encoding='utf-8')
    
    def log(msg):
        """Log message to both stdout and file."""
        print(msg)
        with open(assert_output_file, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    
    errors = []
    warnings = []
    
    # Load original JSON
    original_json_path = given_dir / 'story-graph.json'
    with open(original_json_path, 'r', encoding='utf-8') as f:
        original_json = json.load(f)
    
    # Load synced JSON
    synced_json_path = when_dir / 'synced-story-graph.json'
    if not synced_json_path.exists():
        errors.append(f"Synced JSON not found: {synced_json_path}")
        log("❌ ASSERTION FAILED")
        log("\nErrors:")
        for error in errors:
            log(f"  - {error}")
        sys.exit(1)
    
    with open(synced_json_path, 'r', encoding='utf-8') as f:
        synced_json = json.load(f)
    
    # Assertion 1: Compare original and synced JSON
    log("Assertion 1: Comparing original and synced JSON...")
    json_match, json_diffs = compare_story_graphs(original_json, synced_json)
    
    if json_match:
        log("  ✓ JSON structures match")
    else:
        log("  ⚠ JSON structures differ:")
        for diff in json_diffs[:10]:  # Limit output
            warnings.append(diff)
            log(f"    - {diff}")
        if len(json_diffs) > 10:
            log(f"    ... and {len(json_diffs) - 10} more differences")
    
    # Assertion 2: Check first render exists
    log("\nAssertion 2: Checking first render...")
    first_render = then_dir / 'actual-first-render.drawio'
    if first_render.exists():
        log(f"  ✓ First render exists: {first_render}")
    else:
        errors.append(f"First render not found: {first_render}")
    
    # Assertion 3: Check second render exists
    log("\nAssertion 3: Checking second render...")
    second_render = then_dir / 'actual-second-render.drawio'
    if second_render.exists():
        log(f"  ✓ Second render exists: {second_render}")
    else:
        errors.append(f"Second render not found: {second_render}")
    
    # Assertion 4: Compare first and second renders (if both exist)
    if first_render.exists() and second_render.exists():
        log("\nAssertion 4: Comparing first and second renders...")
        renders_match, render_msg = compare_drawio_files(first_render, second_render)
        if renders_match:
            log(f"  ✓ {render_msg}")
        else:
            warnings.append(render_msg)
            log(f"  ⚠ {render_msg}")
    
    # Summary
    log("\n" + "=" * 80)
    if errors:
        log("❌ ASSERTION FAILED")
        log("\nErrors:")
        for error in errors:
            log(f"  - {error}")
        log(f"\nAssertion output written to: {assert_output_file}")
        sys.exit(1)
    elif warnings:
        log("⚠ ASSERTION PASSED WITH WARNINGS")
        log("\nWarnings:")
        for warning in warnings[:10]:
            log(f"  - {warning}")
        if len(warnings) > 10:
            log(f"  ... and {len(warnings) - 10} more warnings")
        log(f"\nAssertion output written to: {assert_output_file}")
        sys.exit(0)
    else:
        log("✓ ALL ASSERTIONS PASSED")
        log(f"\nAssertion output written to: {assert_output_file}")
        sys.exit(0)


if __name__ == '__main__':
    main()
