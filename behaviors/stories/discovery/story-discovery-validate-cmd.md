### Command: /story-discovery validate

**[Purpose]:**
Validate discovery refinements against Discovery principles

**[Rule]:**
`behaviors/stories/stories-rule.mdc` - Section 2: Discovery Principles

**Runner:**
* CLI: `python behaviors/stories/stories_runner.py story-discovery validate [story-map-file]` — Validate discovery refinements against principles

---

## Validate Action

**Performer**: Runner + Heuristic

**Steps**:
1. Load original story map (before discovery)
2. Load updated story map (after discovery)
3. Run validation checks:
   - **Refinement Check**: Content changed from original
   - **Story Count Check**: Story counts added for unexplored areas
   - **Increment Check**: Increments are well-defined
   - **Refinement Check**: Ambiguous/large stories identified
4. Generate validation report
5. Return report to user

**Validation Checks**:

### Check 1: Refinement Occurred
- **Type**: CONTENT_COMPARISON
- **Severity**: WARNING if no change
- **Message**: "Story map appears unchanged during discovery"
- **Suggestion**: "Refine increments based on discovery insights"

### Check 2: Story Counts Added
- **Type**: PATTERN_DETECTION
- **Severity**: INFO if missing
- **Pattern**: `~\d+\s+stories` or `extrapolat`
- **Message**: "Story map missing story count extrapolations"
- **Suggestion**: "Add story counts (e.g., '~15 stories') to features not yet decomposed"

### Check 3: Increments Well-Defined
- **Type**: STRUCTURE_CHECK
- **Severity**: WARNING if unclear
- **Message**: "Increments lack clear definitions"
- **Suggestion**: "Add increment descriptions and priorities"

### Check 4: Grooming Applied
- **Type**: PATTERN_DETECTION
- **Severity**: INFO if missing
- **Pattern**: `ambiguous|complex|split|groom|multiple responsibilities|unclear scope`
- **Message**: "No grooming notes found"
- **Suggestion**: "Identify stories that are ambiguous or combine multiple responsibilities (based on description, not estimates)"

### Check 5: Consolidation Principle Applied
- **Type**: PATTERN_DETECTION
- **Severity**: WARNING if violations found
- **Patterns to Detect**:
  - Multiple "User enters [field]" stories with same save logic
  - Multiple "System validates [category] points" with same formula
  - Multiple "System calculates unspent [category] points" with same formula
  - Multiple "System groups/filters by [category]" with same algorithm
  - Multiple "User selects [enum]" with same dropdown logic
- **Message**: "Potential over-decomposition detected - same logic repeated across different data fields"
- **Suggestion**: "Review stories for consolidation per Principle 2.5: Same logic, different data, same data structure → ONE Story"
- **Examples**:
  - ❌ "User enters name" + "User enters concept" + "User enters description" → ✅ "User enters identity fields"
  - ❌ "System validates ability points" + "System validates skill points" → ✅ "System validates category points budget"
  - ❌ "System calculates unspent abilities" + "System calculates unspent skills" → ✅ "System calculates unspent points by category"

**Output**:
Validation report with:
- Overall status (PASS/FAIL)
- List of violations with severity
- Suggestions for remediation
- Slide references for principles

