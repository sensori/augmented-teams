"""Run specific acceptance test scenarios."""
import sys
from pathlib import Path

from .test_acceptance import AcceptanceTestRunner

def main():
    """Run only the three specific scenarios."""
    print("="*80)
    print("Running 3 Specific Scenarios")
    print("="*80)
    
    # Setup paths
    input_dir = acceptance_dir / "input"
    outputs_dir = acceptance_dir / "outputs"
    
    # Create runner
    runner = AcceptanceTestRunner(outputs_dir)
    
    # Run only these three scenarios
    scenarios = [
        'incomplete_with_estimates',
        'with_acceptance_criteria',
        'with_increments'
    ]
    
    print(f"\nRunning {len(scenarios)} scenario(s):")
    for scenario in scenarios:
        print(f"  - {scenario}")
    
    # Run each scenario
    for scenario in scenarios:
        story_graph_path = input_dir / f"{scenario}_story_graph.json"
        layout_path = input_dir / f"{scenario}_layout.json" if (input_dir / f"{scenario}_layout.json").exists() else None
        
        runner.run_scenario(
            scenario_name=scenario,
            story_graph_path=story_graph_path,
            layout_path=layout_path
        )
    
    # Generate summary
    print(f"\n{'='*80}")
    print("Test Summary")
    print(f"{'='*80}")
    
    summary = runner.generate_summary()
    print(f"\nTotal scenarios: {summary['total_scenarios']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"\nSummary saved to: {outputs_dir / 'test_summary.json'}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()





