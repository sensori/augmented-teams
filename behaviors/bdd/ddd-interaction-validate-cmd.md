### Command: `/ddd-interaction-validate`

**Purpose:** Validate domain interaction model files against interaction pattern principles (property-based access, nesting, dashes, scaffold hierarchy, etc.)

**Usage:**
* `/ddd-interaction-validate` — Validate currently open interaction model file
* `/ddd-interaction-validate <file-path>` — Validate specific interaction model file

**When invoked, this command MUST:**
1. Run: `python behaviors/bdd/ddd-interaction-validate-runner.py <file-path> --cursor`
2. Parse the interaction model structure
3. Validate against interaction pattern checklist
4. Report violations with line numbers
5. Suggest fixes using DO examples from rule

**Rule Files:**
* `ddd-interaction-patterns-rule.mdc` — Interaction modeling patterns and practices

**Valid Files:**
* `["**/ddd-detailed-interactions.txt", "**/*-interactions.txt", "**/ddd-detailed-model.txt"]`

---

## Steps

1. **User** invokes `/ddd-interaction-validate` or `/ddd-interaction-validate <file-path>`

2. **Code** function `detect_interaction_file()` — detects interaction model file type, returns file type

3. **Code** function `parse_interaction_rules()` — loads ddd-interaction-patterns-rule.mdc, extracts 10 section principles and checklists, returns rules dict

4. **Code** function `parse_interaction_structure(file)` — parses interaction file, extracts:
   - Function/property calls with nested code
   - Dash usage under functions/properties
   - Nesting levels and indentation
   - Property-based vs method-based access patterns
   - Scaffold hierarchy references
   - State management patterns
   - Abbreviation patterns

5. **Code** displays all 10 section rules as summary:
   ```
   § 1: Property-Based Access Over Verbose Method Calls
   § 2: Nesting Groups Code Under Functions/Properties
   § 3: Show Details Only on First Call
   § 4: Dashes Under Functions and Properties
   § 5: Follow Scaffold Hierarchy
   § 6: State Management Through Properties
   § 7: Comments Explain Logic, Not Replicate Code
   § 8: Domain Concept Organization
   § 9: Abbreviate Repeated Patterns
   § 10: Interaction Flow Summary
   ```

6. **Code** for each section §1-§10:
   - Outputs validation prompts in chunks
   - Each prompt includes: code section, line numbers, mandatory checklist, DO/DON'T examples

7. **AI Agent** for each chunk validates against checklist:
   - □ § 1: Uses property access, not verbose method calls?
   - □ § 2: Code properly nested under functions/properties?
   - □ § 3: Details shown only on first call, abbreviated on repeats?
   - □ § 4: Dashes used under functions/properties with nested code?
   - □ § 5: Follows scaffold hierarchy structure?
   - □ § 6: State set before accessing computed properties?
   - □ § 7: Comments explain logic, don't replicate code?
   - □ § 8: Interactions organized by domain concept?
   - □ § 9: Repeated patterns abbreviated with clear references?
   - □ § 10: Flow summaries provided for major patterns?

8. **AI Agent** reports violations with line numbers and suggested fixes using DO examples from rules

9. **Code** outputs cross-section validation prompt

10. **AI Agent** checks for systemic issues spanning multiple sections:
    - Inconsistent nesting levels
    - Missing dashes where needed
    - Property access patterns mixed with method calls
    - Scaffold hierarchy violations

11. **AI Agent** applies fixes using search_replace tool if violations found

---

## Validation Checklist (AI must check ALL)

### § 1: Property-Based Access
- [ ] Property access used instead of verbose method signatures
- [ ] No parameter types or return types shown in calls
- [ ] Logic hidden in property getters/setters
- [ ] State properties set before accessing computed properties

### § 2: Nesting
- [ ] All code under function/property is indented
- [ ] Consistent indentation levels
- [ ] Code clearly grouped under parent function/property
- [ ] No unrelated code at same indentation level

### § 3: Details on First Call Only
- [ ] Full details shown first time function/property called
- [ ] Subsequent calls abbreviated with `// (details shown above)` or similar
- [ ] Clear reference to where details were first shown
- [ ] No duplicate full implementations

### § 4: Dashes Under Functions/Properties
- [ ] Dashes placed directly under function/property names with nested code
- [ ] Dash length approximately matches name length
- [ ] Consistent dash formatting
- [ ] Dashes used for both functions and properties

### § 5: Scaffold Hierarchy
- [ ] Structure follows scaffold hierarchy exactly
- [ ] Scaffold comments used: `// that implements a specializing rule`
- [ ] Behaviors in scaffold order
- [ ] Nested structure preserved from scaffold

### § 6: State Management
- [ ] State properties set before accessing: `this.rule.fileExtension = content.fileExtension`
- [ ] State dependencies documented in comments
- [ ] State flow shown clearly
- [ ] No properties accessed without required state

### § 7: Comments
- [ ] Comments explain WHY/WHAT, not replicate code
- [ ] Internal logic documented when hidden
- [ ] Relationships and dependencies explained
- [ ] Comments concise and meaningful

### § 8: Domain Concept Organization
- [ ] Interactions organized by domain concept
- [ ] Related interactions grouped together
- [ ] Inheritance relationships shown: `CodeGuidingCommand : Command`
- [ ] Domain model structure used as guide

### § 9: Abbreviate Patterns
- [ ] Full pattern shown once, then abbreviated
- [ ] Clear comments indicate abbreviation: `// Same as base validation`
- [ ] Reference to where full pattern shown
- [ ] Abbreviations clear and consistent

### § 10: Flow Summary
- [ ] Summary sections provided for major flows
- [ ] Common patterns documented as reusable flows
- [ ] Shows how multiple interactions combine
- [ ] Appropriate abstraction level

---

## Example Violations and Fixes

### Violation: Verbose Method Call
```javascript
// ❌ VIOLATION: Verbose method signature
specializedRule = this.specializingRule.selectSpecializedRule(content.fileExtension: string): SpecializedRule

// ✅ FIX: Property-based access
this.rule.fileExtension = content.fileExtension
specializedRule = this.rule.specializedRule
```

### Violation: Missing Dashes
```javascript
// ❌ VIOLATION: No dashes under function
commandRunner.validate(content)
  this.content = content

// ✅ FIX: Dashes under function
commandRunner.validate(content)
-------------------------------
  this.content = content
```

### Violation: Missing Nesting
```javascript
// ❌ VIOLATION: Code not nested under function
commandRunner.validate(content)
this.content = content
rule = this.rule
this.loadRuleFromRuleFile()

// ✅ FIX: Proper nesting
commandRunner.validate(content)
-------------------------------
  this.content = content
  rule = this.rule
    this.loadRuleFromRuleFile()
    ----------------------------------
      this.principles = base.principles
```

### Violation: Repeated Details
```javascript
// ❌ VIOLATION: Full details repeated
specializedRule = this.rule.specializedRule
  // full implementation details...
// ...later...
specializedRule = this.rule.specializedRule
  // full implementation details again...

// ✅ FIX: Abbreviate second call
specializedRule = this.rule.specializedRule
  // full implementation details...
// ...later...
specializedRule = this.rule.specializedRule  // (details shown above)
```

### Violation: Missing State
```javascript
// ❌ VIOLATION: Property accessed without setting state
detectedViolations = heuristic.violations
  // (content not set - unclear)

// ✅ FIX: Set state first
heuristic.content = content
detectedViolations = heuristic.violations
  // property getter uses content state
```


















