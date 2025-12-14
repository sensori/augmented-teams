"""Generate full validation report with ALL violations."""
import json
from datetime import datetime
from pathlib import Path

# Read the validation results
input_file = Path(r'C:\Users\thoma\.cursor\projects\c-dev-augmented-teams\agent-tools\8abc0cfa-6f9d-4020-9856-8cec4601337c.txt')
output_file = Path('c:/dev/augmented-teams/agile_bot/bots/base_bot/docs/stories/validation-report.md')

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

violations = data.get('data', {}).get('violations', [])

# Group violations by rule
violations_by_rule = {}
for violation in violations:
    rule_file = violation.get('rule_file', 'Unknown')
    if rule_file not in violations_by_rule:
        violations_by_rule[rule_file] = []
    violations_by_rule[rule_file].append(violation)

# Generate report
report_lines = [
    "# Validation Report - 7 Write Tests",
    "",
    f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    "**Project:** base_bot",
    "**Behavior:** 7_write_tests",
    "**Action:** validate_rules",
    "",
    "## Summary",
    "",
    f"Validated test files against **{len(violations_by_rule)} validation rules**.",
    "",
    f"- **Total Violations Found:** {len(violations)}",
    f"- **Rules Checked:** {len(violations_by_rule)}",
    "",
    "## Content Validated",
    "",
    "- **Test Files Scanned:** 22 test file(s)",
    "",
    "## Validation Rules Checked",
    ""
]

# Add each rule with ALL violations (no truncation)
for rule_file, rule_violations in sorted(violations_by_rule.items(), key=lambda x: len(x[1]), reverse=True):
    rule_name = rule_file.replace('rules\\', '').replace('.json', '').replace('_', ' ').title()
    
    report_lines.extend([
        f"### Rule: {rule_name}",
        f"**Violations:** {len(rule_violations)}",
        "",
        "**Violations Found:**",
        ""
    ])
    
    # Include ALL violations, not just first 10
    for i, violation in enumerate(rule_violations, 1):
        location = violation.get('location', 'Unknown')
        message = violation.get('violation_message', 'No message')
        severity = violation.get('severity', 'unknown')
        line_num = violation.get('line_number', 'N/A')
        
        location_display = Path(location).name if location and location != 'Unknown' and location else 'N/A'
        report_lines.append(f"{i}. **{severity.upper()}** - `{location_display}`")
        if line_num and line_num != 'N/A' and line_num is not None:
            report_lines.append(f"   - Line: {line_num}")
        report_lines.append(f"   - Message: {message}")
        report_lines.append("")
    
    report_lines.append("")

# Add summary section
report_lines.extend([
    "## Violations Summary",
    "",
    f"**Total Violations:** {len(violations)}",
    "",
    "### Violations by Rule:",
    ""
])

for rule_file, rule_violations in sorted(violations_by_rule.items(), key=lambda x: len(x[1]), reverse=True):
    rule_name = rule_file.replace('rules\\', '').replace('.json', '')
    report_lines.append(f"- **{rule_name}**: {len(rule_violations)} violation(s)")

report_lines.extend([
    "",
    "## Recommendations",
    ""
])

if len(violations) == 0:
    report_lines.append("✅ **All validation rules passed!** No violations found.")
else:
    report_lines.append("Review violations above and address them according to the rule descriptions.")
    report_lines.append("")
    report_lines.append("**Key Areas to Address:**")
    
    # Count by severity
    error_count = sum(1 for v in violations if v.get('severity') == 'error')
    warning_count = sum(1 for v in violations if v.get('severity') == 'warning')
    
    if error_count > 0:
        report_lines.append(f"- **Errors ({error_count}):** Address these immediately as they violate critical rules")
    if warning_count > 0:
        report_lines.append(f"- **Warnings ({warning_count}):** Review and consider addressing to improve code quality")

# Write report
output_file.parent.mkdir(parents=True, exist_ok=True)
output_file.write_text('\n'.join(report_lines), encoding='utf-8')
print(f"Validation report written to: {output_file}")
print(f"Total violations: {len(violations)}")
print(f"Report includes ALL violations (no truncation)")
