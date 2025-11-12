### Command: /story-specification-scenarios validate

**[Purpose]:**
Validate scenario specifications for structure, completeness, and adherence to behavioral language principles.

**[Parent Command]:**
`/story-specification-scenarios` - Delegates to this command for validation action

**[Rule]:**
- `behaviors/stories/stories-rule.mdc` - Story writing practices and standards
- Applies principles: Universal (0.1, 0.2), Phase 4 Specification Scenarios (4.1)

---

## Validation Process

### Step 1: Structure Validation

**Check for**:
- ✅ Scenarios section exists in story document
- ✅ Proper Given/When/Then structure in each scenario
- ✅ Background used correctly (only Given/And steps)
- ✅ Scenario Outline has Examples table (if present)
- ✅ Proper Gherkin keyword usage

**Violations**:
- `MISSING_SCENARIOS` - Story document missing Scenarios section
- `INCOMPLETE_SCENARIO` - Scenario missing When...Then structure
- `INVALID_BACKGROUND` - Background contains non-Given steps
- `SCENARIO_OUTLINE_WITHOUT_EXAMPLES` - Scenario Outline missing Examples table

### Step 2: Content Validation

**Check for**:
- ✅ Behavioral language (not technical/code)
- ✅ Covers all acceptance criteria
- ✅ Happy path included
- ✅ Edge cases considered
- ✅ Error cases included
- ✅ Scenarios describe observable behavior

**Violations**:
- `MISSING_COVERAGE` - Not all acceptance criteria covered by scenarios
- `TECHNICAL_LANGUAGE` - Scenarios contain code patterns or technical terms
- `MISSING_HAPPY_PATH` - No happy path scenario present
- `MISSING_EDGE_CASES` - No edge cases considered
- `MISSING_ERROR_CASES` - No error handling scenarios

### Step 3: Gherkin Validation

**Check for**:
- ✅ Given: Sets up context/state
- ✅ When: Describes action or event
- ✅ Then: Describes expected outcome
- ✅ And: Continues previous keyword level
- ✅ But: Negative assertion (should NOT happen)
- ✅ Background: Only Given/And steps
- ✅ Scenario Outline: Uses <parameter> syntax
- ✅ Examples: Proper | table | format |

**Violations**:
- `INVALID_GHERKIN` - Improper keyword usage
- `PARAMETERS_WITHOUT_TABLE` - Scenario Outline has <parameters> but no Examples table
- `TABLE_FORMAT_ERROR` - Examples table not in proper | column | format
- `BACKGROUND_MISUSE` - Background contains When/Then steps

### Step 4: Apply Heuristics

**Use**: `StorySpecificationScenariosHeuristic` class

**Checks**:
1. `validate_scenarios(spec_content)` - Validate scenario structure
2. `validate_gherkin_keywords(spec_content)` - Validate keyword usage
3. `validate_coverage(scenarios, acceptance_criteria)` - Validate AC coverage
4. `validate_behavioral_language(spec_content)` - Check for technical language

### Step 5: Present Validation Results

**Format**:
```
Validation Results: [PASS/FAIL]

Violations Found: [count]

ERROR: MISSING_COVERAGE
- Message: Scenarios do not cover all acceptance criteria
- Suggestion: Add scenarios for AC2, AC3
- Slide Reference: Slide 16

WARNING: TECHNICAL_LANGUAGE
- Message: Scenario contains technical term "database"
- Suggestion: Focus on observable behavior, not implementation
- Slide Reference: Slide 14

INFO: MISSING_EDGE_CASES
- Message: Consider adding edge case scenarios
- Suggestion: Add boundary condition scenarios
```

---

## Validation Severity Levels

### ERROR (Must Fix)
- Missing scenarios section
- Incomplete scenario structure (missing When...Then)
- Technical language in scenarios
- Missing coverage of acceptance criteria
- Invalid Gherkin syntax

### WARNING (Should Fix)
- Missing edge cases
- Missing error cases
- Background misuse
- Overly complex scenarios

### INFO (Consider)
- Could use Background for repeated Given steps
- Could use Scenario Outline for parameterized scenarios
- Could split large scenarios

---

## Decision Points

### If validation fails (ERROR level)
**Action**: User must fix errors before proceeding

### If validation has warnings
**Action**: User can choose to fix or accept

### If validation passes
**Action**: Scenarios are ready, can proceed to `/story-specification-examples`

---

## Heuristic Examples

### Example 1: Missing When...Then Pattern
```markdown
### Scenario: Invalid scenario
**Given** user is logged in
**And** user has items in cart
```

**Violation**: `INCOMPLETE_SCENARIO` - Missing When action and Then outcome

**Fix**: Add When and Then steps
```markdown
### Scenario: Checkout with items
**Given** user is logged in
**And** user has items in cart
**When** user clicks checkout button
**Then** user is taken to payment page
```

### Example 2: Technical Language
```markdown
### Scenario: Save order
**When** order.save() is called
**Then** database record is created
```

**Violation**: `TECHNICAL_LANGUAGE` - Contains code patterns and technical terms

**Fix**: Use behavioral language
```markdown
### Scenario: Save order
**When** customer confirms order
**Then** order is saved and confirmation displayed
```

### Example 3: Scenario Outline Without Examples
```markdown
### Scenario Outline: Add items
**Given** cart has <start> items
**When** user adds <value> items
**Then** cart has <expected> items
```

**Violation**: `PARAMETERS_WITHOUT_TABLE` - Missing Examples table

**Fix**: Add Examples table
```markdown
### Scenario Outline: Add items
**Given** cart has <start> items
**When** user adds <value> items
**Then** cart has <expected> items

**Examples**:
| start | value | expected |
|-------|-------|----------|
| 0     | 1     | 1        |
| 5     | 3     | 8        |
```

---

## PowerPoint References
- Slide 16: Scenario specification principles
- Slides 149-154: Scenario patterns
- Slide 154: Purchase Textbook example (proper structure)
- Slide 14: Behavioral vs technical language


