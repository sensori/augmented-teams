#!/usr/bin/env python3
"""
Create expected files from actual outputs for tests that are missing expected files.
"""
import sys
import json
import shutil
from pathlib import Path

scenarios_dir = Path(__file__).parent

def create_expected_files(scenario_name):
    """Create expected files from actual outputs."""
    scenario_dir = scenarios_dir / scenario_name
    then_dir = scenario_dir / "3_then"
    
    if not then_dir.exists():
        print(f"[SKIP] {scenario_name}: No 3_then directory")
        return False
    
    created = []
    
    # Check for actual JSON files
    for actual_json in then_dir.glob("actual*.json"):
        expected_name = actual_json.name.replace("actual", "expected")
        expected_path = then_dir / expected_name
        
        if not expected_path.exists():
            # Copy actual to expected
            shutil.copy2(actual_json, expected_path)
            created.append(f"JSON: {expected_name}")
            print(f"[CREATED] {scenario_name}: {expected_name}")
    
    # Check for actual DrawIO files
    for actual_drawio in then_dir.glob("actual*.drawio"):
        expected_name = actual_drawio.name.replace("actual", "expected")
        expected_path = then_dir / expected_name
        
        if not expected_path.exists():
            # Copy actual to expected
            shutil.copy2(actual_drawio, expected_path)
            created.append(f"DrawIO: {expected_name}")
            print(f"[CREATED] {scenario_name}: {expected_name}")
    
    # Also check 2_when for synced JSON that might need to be expected
    when_dir = scenario_dir / "2_when"
    if when_dir.exists():
        synced_json = when_dir / "synced-story-graph.json"
        if synced_json.exists():
            expected_synced = then_dir / "expected-synced-story-graph.json"
            if not expected_synced.exists():
                shutil.copy2(synced_json, expected_synced)
                created.append(f"JSON: expected-synced-story-graph.json")
                print(f"[CREATED] {scenario_name}: expected-synced-story-graph.json")
    
    return len(created) > 0

def main():
    """Main function."""
    print("\n" + "="*80)
    print("CREATING EXPECTED FILES FROM ACTUAL OUTPUTS")
    print("="*80 + "\n")
    
    # Find all scenarios
    scenarios = []
    for item in scenarios_dir.iterdir():
        if item.is_dir() and not item.name.startswith('_') and item.name != '__pycache__':
            test_file = item / "test_render_sync_render_round_trip.py"
            if test_file.exists():
                scenarios.append(item.name)
    
    created_count = 0
    for scenario_name in sorted(scenarios):
        if create_expected_files(scenario_name):
            created_count += 1
    
    print(f"\n{'='*80}")
    print(f"Created expected files for {created_count} scenarios")
    print("="*80)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

