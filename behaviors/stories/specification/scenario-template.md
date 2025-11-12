# Story Specification: [Story Title]

## Story Information
**Feature**: [Feature Name]
**Epic**: [Epic Name]
**Status**: [Scenarios Added / In Progress / Complete]

---

## Acceptance Criteria Reference
**Source**: From story document or feature document

[Brief list of acceptance criteria this specification covers]
- AC1: [Brief description]
- AC2: [Brief description]
- AC3: [Brief description]

---

## Background (Optional)

**Purpose**: Move repeated Given steps to background section. Background runs before each scenario, providing shared context.

**Use when**: Same Given steps repeat in 3+ scenarios

**Given** [common STATE that applies to all scenarios]
**And** [additional STATE]
**And** [yet another STATE if needed]

**Note**: Background should ONLY contain Given/And steps (no When/Then)

**CRITICAL - Given Statements Describe STATES**:
- Given statements describe states, not actions already completed
- Use state patterns (borrowed from BDD principles):
  - "that has been [past participle]" - completed states (e.g., "character has been created")
  - "that is being [verb]" - ongoing states (e.g., "character is being edited")
  - "that is [adjective/noun]" - current states (e.g., "screen is displayed", "user is authenticated")
  - "that has [noun]" - possession states (e.g., "character has invalid data")
- ✅ DO: "Given character is being edited", "Given login screen is displayed", "Given user is authenticated"
- ❌ DON'T: "Given user is on the login screen" (implies navigation action), "Given user navigated to screen" (action, not state)

---

## Scenarios

### Scenario 1: [Happy Path - Primary Success Flow]

**Purpose**: Describe the main success path that most users will follow

**Given** [initial STATE - not action]
**And** [additional STATE]
**And** [yet another STATE]
**When** [user/system ACTION that triggers behavior]
**Then** [expected outcome - what user/system observes]
**And** [additional outcome]
**But** [should NOT happen - negative assertion]

**Acceptance Criteria Covered**: AC1, AC2

**State Examples**:
- ✅ "Given character is being edited" (state)
- ✅ "Given identity fields are displayed" (state)
- ✅ "Given user is authenticated" (completed state)
- ❌ "Given user is on screen" (implies navigation - use "Given screen is displayed")

---

### Scenario 2: [Edge Case - Boundary Condition]

**Purpose**: Test behavior at boundaries or special conditions

**Given** [context at boundary condition]
**And** [additional boundary context]
**When** [action at boundary]
**Then** [expected boundary handling]
**And** [additional verification]
**But** [should NOT happen]

**Acceptance Criteria Covered**: AC1

---

### Scenario 3: [Edge Case - Alternative Path]

**Purpose**: Test alternative success path or variation

**Given** [context for alternative]
**And** [additional context]
**When** [alternative action]
**Then** [expected alternative outcome]
**And** [additional verification]

**Acceptance Criteria Covered**: AC2

---

### Scenario 4: [Error Case - Invalid Input]

**Purpose**: Test error handling for invalid inputs or data

**Given** [context with invalid condition]
**And** [additional context]
**When** [action with invalid input]
**Then** [error handling outcome]
**And** [error message or feedback displayed]
**But** [system should NOT proceed with invalid data]

**Acceptance Criteria Covered**: AC3

---

### Scenario 5: [Error Case - Failed Operation]

**Purpose**: Test error handling when operation fails

**Given** [context]
**And** [condition that will cause failure]
**When** [action that triggers failure]
**Then** [graceful failure handling]
**And** [user feedback about failure]
**And** [system recovers or maintains consistency]

**Acceptance Criteria Covered**: AC3

---

## Scenario Outline (Optional)

**Purpose**: Test same behavior with multiple value combinations (use when 3+ similar cases)

**Use when**: 
- Testing same behavior with different data
- Validation rules with multiple examples
- Boundary testing with multiple values
- Parameterized scenarios

### Scenario Outline: [Parameterized Scenario Name]

**Given** there are <start> [items/entities]
**And** [context with <parameter>]
**When** I [action] <value> [items/entities]
**Then** [outcome] should be <expected> [items/entities]
**And** [additional verification with <parameter>]
**But** [should NOT have <invalid> result]

**Examples**:

| start | value | expected | invalid | description              |
|-------|-------|----------|---------|--------------------------|
| 12    | 5     | 7        | 5       | Normal case              |
| 20    | 5     | 15       | 5       | Larger numbers           |
| 5     | 5     | 0        | 5       | Boundary - reaches zero  |
| 0     | 5     | -5       | 0       | Edge case - negative     |

**Acceptance Criteria Covered**: AC1, AC2

**Note**: Scenario Outline runs once for each row in Examples table, substituting <parameter> values

---

## Gherkin Keywords Reference

### Core Keywords
- **Given**: Describe initial STATE (not actions) - **CRITICAL: States, not actions**
- **When**: Action or event that triggers behavior
- **Then**: Expected outcome (what should happen)
- **And**: Additional step at same level as previous keyword
- **But**: Negative assertion (what should NOT happen)

### Advanced Keywords
- **Background**: Shared Given steps for all scenarios (runs before each scenario)
- **Scenario Outline**: Parameterized scenario (runs multiple times with Examples table)
- **Examples**: Table of values for Scenario Outline (uses | column | format)

### Keyword Usage Rules
1. **Given** - Use for:
   - **CRITICAL**: Describing STATES, not actions
   - Establishing current state or context
   - Defining preconditions as states
   - Authentication/authorization state (e.g., "user is authenticated", NOT "user logged in")
   - State patterns:
     - ✅ "character is being edited" (ongoing state)
     - ✅ "screen is displayed" (current state)
     - ✅ "user is authenticated" (completed state)
     - ✅ "field is empty" (current state)
     - ✅ "character has been created" (completed state)
     - ❌ "user is on the screen" (implies navigation action)
     - ❌ "user clicked button" (action, not state)
     - ❌ "user navigated to page" (action, not state)

2. **When** - Use for:
   - User actions (clicks, submits, selects)
   - System events (time passes, notification arrives)
   - Triggers that cause behavior

3. **Then** - Use for:
   - Observable outcomes
   - What user sees/experiences
   - System state changes
   - Verifiable results

4. **And** - Use for:
   - Additional steps at same level
   - Continues previous keyword
   - Improves readability

5. **But** - Use for:
   - Negative assertions
   - What should NOT happen
   - Clarifies boundaries

### Background Rules
- ONLY use Given/And keywords in Background
- NO When/Then in Background
- Background runs before EACH scenario
- Use when 3+ scenarios share same Given steps

### Scenario Outline Rules
- Use <parameter> syntax for placeholders
- Must have Examples table with matching column names
- Use | pipes | to format table
- Each row in Examples creates one scenario execution

---

## Writing Guidelines

### DO
- ✅ Use behavioral language (user actions, system responses)
- ✅ Describe observable behavior (what users see/experience)
- ✅ Cover happy path, edge cases, and error cases
- ✅ Use Background for repeated Given steps (3+ scenarios)
- ✅ Use Scenario Outline for parameterized scenarios (3+ cases)
- ✅ Link scenarios to acceptance criteria
- ✅ Write scenarios that can be understood by non-technical stakeholders
- ✅ Use specific, concrete language
- ✅ Focus on WHAT happens, not HOW it's implemented

### DON'T
- ❌ Use technical language (database, API, function calls)
- ❌ Describe implementation details
- ❌ Use code patterns (function(), object.method())
- ❌ Write scenarios that require technical knowledge to understand
- ❌ Skip edge cases or error cases
- ❌ Create overly complex scenarios (split into multiple scenarios instead)
- ❌ Mix multiple unrelated behaviors in one scenario

---

## Scenario Coverage Checklist

### Required Coverage
- [ ] **Happy Path**: Main success flow covered
- [ ] **Edge Cases**: Boundary conditions covered
- [ ] **Error Cases**: Failure conditions and error handling covered
- [ ] **All AC**: Every acceptance criterion has at least one scenario

### Optional Coverage
- [ ] **Alternative Paths**: Alternative success flows (if applicable)
- [ ] **Platform Variations**: Different platform behaviors (if applicable)
- [ ] **Permission Levels**: Different user roles or permissions (if applicable)

### Structure Checklist
- [ ] **Background**: Used if 3+ scenarios share Given steps
- [ ] **Scenario Outline**: Used if 3+ similar cases with different data
- [ ] **Gherkin Keywords**: Proper keyword usage (Given/When/Then/And/But)
- [ ] **Behavioral Language**: No technical terms or code patterns
- [ ] **Linked to AC**: Each scenario references which AC it covers

---

## Examples from PowerPoint

### Example 1: Purchase Textbook (Slide 154 - Updated with State-oriented Given)

**Scenario**: Successful textbook purchase

**Given** student is authenticated (STATE - not "logged in to")
**And** textbook exists in catalog (STATE)
**And** textbook is in stock (STATE - not "is not out of stock")
**When** the student selects that textbook for purchase
**And** the student specifies shipping information (shipping method, billing address, shipping address)
**And** the student confirms purchase
**Then** the system sends payment information to 3rd party
**And** the system sends Order Details to bookstore application
**And** success message is displayed to student

---

### Example 2: Trading Alert (Updated with State-oriented Given)

**Background**
**Given** stock alert monitoring is enabled (STATE)
**And** trader is authenticated (STATE)

**Scenario 1**: Trader is not alerted below threshold
**Given** alert threshold is set (STATE)
**When** stock is traded below threshold
**Then** alert status is OFF
**But** alert message is not sent

**Scenario 2**: Trader is alerted above threshold
**Given** alert threshold is set (STATE)
**When** stock is traded at or above threshold
**Then** alert status is ON
**And** alert message is sent to trader

---

### Example 3: Bill Generation (Updated with State-oriented Given)

**Scenario Outline**: Generate bills for different preferences

**Given** Customer has billing preferences set to <format> (STATE - describes current configuration)
**And** Billing Period has been completed (STATE - completed state)
**When** the System generates a Customer Bill
**Then** the bill is rendered in <format> format
**And** the bill includes all Chargeable Activities for the period

**Examples**:
| format | 
|--------|
| PDF    |
| HTML   |
| Email  |

---

## Notes

- This template is filled in during Phase 4 (Specification Scenarios)
- Examples are added in Phase 5 (Specification Examples) - separate phase
- This template focuses ONLY on scenario structure (Given/When/Then)
- Each scenario should be understandable by business stakeholders
- Scenarios are living documentation - update as stories evolve

---

## PowerPoint References
- Slide 16: Story specification guidance
- Slides 149-154: Scenario patterns and examples
- Slide 154: Purchase Textbook (concrete example)


