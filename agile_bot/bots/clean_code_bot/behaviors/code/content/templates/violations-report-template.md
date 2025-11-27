# Violations Report: {file}

**Language:** {language}  
**Generated:** {generated_date}

## Summary

- **Critical:** {summary_critical}
- **Important:** {summary_important}
- **Suggested:** {summary_suggested}
- **Total Violations:** {summary_total}

---

## Violations

### Overview

This section lists all violations found, grouped by severity. Each violation includes:
- **Line numbers** with code snippets showing the problematic area
- **Function/Class name** where the violation occurs
- **Principle violated** (e.g., "1.2 Small and Focused", "1.3 Control Flow")
- **Specific issue description** explaining what's wrong
- **Recommendation** with before/after code examples showing how to fix it

### Example Violation Format

Each violation should follow this format:

**Line 482-490** (critical) - Deep Nesting (7 levels)
**Function:** `_deploy_to_global()`
**Principle:** 1.3 Control Flow - Simple Control Flow

**Current Code:**
```python
480|    if condition1:
481|        if condition2:
482|            if condition3:
483|                if condition4:
484|                    if condition5:
485|                        if condition6:
486|                            if condition7:
487|                                result = process()
```

**Issue:** Deep nesting makes code hard to read and maintain. Each nested level increases cognitive load and makes testing difficult.

**Recommendation:** Extract nested logic into separate functions with guard clauses:
```python
def _should_process_deployment(self, condition1, condition2):
    if not condition1:
        return False
    if not condition2:
        return False
    return True

def _deploy_to_global(self):
    if not self._should_process_deployment(condition1, condition2):
        return
    result = self._process_deployment()
```

**Benefits:** 
- Guard clauses flatten the structure, making code easier to understand
- Each function has a single responsibility
- Easier to test individual conditions
- Reduced cognitive complexity

### Critical Violations

{violations_critical}

### Important Violations

{violations_important}

### Suggested Violations

{violations_suggested}

### All Violations (Complete List)

{violations_list}

---

## Code Design

### Architecture

{code_design_architecture}

### Layers

{code_design_layers}

### Domain Objects

{code_design_domain_objects}

### Functions

{code_design_functions}

### Classes

{code_design_classes}

### Dependencies

{code_design_dependencies}

### Error Handling Strategy

{code_design_error_handling_strategy}

### Integration Points

{code_design_integration_points}

---

## Code Structure

### Overview

- **Total Functions:** {code_structure_functions}
- **Total Classes:** {code_structure_classes}
- **Total Lines:** {code_structure_total_lines}

### Functions Detail

{code_structure_functions_detail}

### Classes Detail

{code_structure_classes_detail}

---

## Heuristics

### Deep Nesting

{heuristics_deep_nesting}

### Magic Numbers

{heuristics_magic_numbers}

### Single Letter Variables

{heuristics_single_letter_variables}

### Commented Code

{heuristics_commented_code}

### Large Functions

{heuristics_large_functions}

### Too Many Parameters

{heuristics_too_many_parameters}

### Large Classes

{heuristics_large_classes}

---

## Inputs from Previous Phases

### Stories

{inputs_stories}

### Domain Objects

{inputs_domain_objects}

### BDD Tests

{inputs_bdd_tests}

### Existing Code

{inputs_existing_code}

---

## AI Analysis

{ai_analysis}

---

## Recommendations

### Priority Actions

{recommendations_priority}

### Example Refactorings

{recommendations_examples}

### Complete Recommendations List

{recommendations_list}

### Refactoring Examples with Code

Each example below shows:
1. **Current Code** - The problematic code with line numbers
2. **Issue** - What's wrong and why it violates clean code principles
3. **Recommended Code** - How to fix it with improved version
4. **Benefits** - Why this change improves code quality

{recommendations_refactoring_examples}

