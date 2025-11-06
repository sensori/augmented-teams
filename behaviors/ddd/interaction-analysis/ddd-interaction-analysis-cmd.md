### Command: `ddd-interaction-analysis-cmd.md`

**Purpose:** Create domain interaction analysis documenting business flows between domain concepts at the same abstraction level as the domain map.

**Usage:**
* `\ddd-interactions` — Create interaction analysis for currently open file
* `\ddd-interactions <file-path>` — Create interaction analysis for specific file
* `\ddd-interactions <domain-map-path>` — Create interaction analysis from existing domain map

**Rule:**
* `\ddd-interaction-analysis-rule` — Domain interaction analysis principles (references `\ddd-structure-analysis-rule` for core DDD principles)

**Prerequisites:**
* Domain map should exist first (create via `\ddd-analyze` if needed)
* Source code accessible for flow analysis
* Understanding of system's business scenarios

**Output:**
* Creates `<name>-domain-interactions.txt` in same folder as source and domain map
* Documents 5-10 key business scenarios
* Shows domain concept interactions at business logic level
* Includes cross-domain interaction summary

**Steps:**

1. **User** invokes `\ddd-interactions` or `\ddd-interactions <path>`

2. **AI Agent** locates domain map
   - Searches for `*-domain-map.txt` in same directory as source
   - If not found: Suggests running `\ddd-analyze` first
   - Reads domain map to learn concept names

3. **AI Agent** reads interaction analysis rule
   - Loads ddd-interaction-analysis-rule.mdc
   - Understands abstraction level requirements
   - Reviews DO/DON'T examples

4. **AI Agent** identifies business scenarios
   - Analyzes code for entry points (user actions, platform hooks)
   - Identifies complete business flows
   - Groups related interactions into scenarios
   - Selects 5-10 most important scenarios

5. **AI Agent** documents each scenario
   - Names scenario from business perspective
   - Identifies trigger (user action or system event)
   - Lists participating domain concepts (actors)
   - Maps business flow steps
   - Extracts business rules
   - States business outcome

6. **AI Agent** maintains domain abstraction
   - Uses concept names from domain map
   - Describes transformations (Concept A → Concept B)
   - Describes lookups (searches by X, finds Y)
   - States business rules (not code conditionals)
   - Mentions platform APIs at high level only
   - Avoids all implementation details

7. **AI Agent** documents cross-domain interactions
   - Shows concept reuse between domains
   - Describes specialized behavior added
   - States coordination rules
   - Keeps brief (details in scenarios)

8. **AI Agent** validates output
   - Verifies concept names match domain map
   - Checks abstraction level (no code details)
   - Ensures all scenarios follow template
   - Confirms file location and naming

9. **AI Agent** creates interaction file
   - Writes to `<name>-domain-interactions.txt`
   - Places in same directory as domain map and source
   - Formats using scenario template

10. **User** reviews interaction documentation

**Scenario Template:**

```
SCENARIO N: [BUSINESS SCENARIO NAME]

TRIGGER: [User action or system event]

ACTORS:
- [Domain Concept from map]
- [Another Domain Concept]

FLOW:

1. [Business event description]
   [Domain concept action]
   [Business transformation/lookup]

2. [Next business step]
   [Domain concept interaction]
   [Business outcome]

BUSINESS RULES:
- [Domain constraint]
- [Priority order]
- [Special cases]

RESULT: [Business outcome]
```

**Abstraction Guidelines:**

**DO - Domain Level:**
* ✅ "PowerItem transforms power into animation characteristics"
* ✅ "Animation Resolution searches macros by priority"
* ✅ "Movement Type Detection maps mode to animation type"
* ✅ "Foundry triggers rollAttack hook"
* ✅ "Text Animation System creates floating text"

**DON'T - Implementation Level:**
* ❌ "READS: item.getFlag('mm3e-animations', 'descriptorMacro')"
* ❌ "QUERIES: html.find('.header-button').length"
* ❌ "CREATES: style = { fill: color, fontSize: 32 }"
* ❌ "PARSES: match(/vs.*?(\d+)/)"
* ❌ "CALLS: canvas.tokens.get(tokenId)"

**Common Scenarios to Document:**

1. **Primary Business Flow** - Main user journey
2. **Alternative Flows** - Different paths through system
3. **Configuration/Customization** - User setup scenarios
4. **Feedback/Display** - Information presentation to user
5. **Error/Edge Cases** - Special business rules
6. **Cross-Domain Coordination** - How domains work together

**Validation Checklist:**

Before completing, verify:

- [ ] Domain map exists and was read
- [ ] All concept names match domain map exactly
- [ ] No code details (fields, APIs, syntax, HTML, CSS)
- [ ] Transformations stated clearly (A → B)
- [ ] Lookups described as business criteria
- [ ] Business rules stated, not code conditionals
- [ ] Platform APIs mentioned at high level only
- [ ] Each scenario follows template structure
- [ ] File in same folder as domain map
- [ ] File named `<name>-domain-interactions.txt`

**Example Scenarios:**

See `demo/mm3e-animations/mm3e-animations-domain-interactions.txt` for reference examples showing:
- Power activation from attack (primary flow)
- Descriptor-based animation generation (fallback logic)
- Combat outcome feedback (visual indicators)
- Save result feedback (complex data extraction)
- Movement-based animation (specialized flow)
- Animation customization (user configuration)
- Manual replay from chat (alternative trigger)
- UI label display (informational flow)

**Tips:**

* Start with domain map review to internalize concept names
* Trace code for business flows, not implementation details
* Think "what business concept does what" not "what code executes"
* Use domain terminology consistently
* Keep cross-domain section brief (scenarios have details)
* If introducing new concepts, add to domain map first

---

**See Also:**
* `\ddd-analyze` — Create domain map first
* `\ddd-validate` — Validate domain map before interactions
* `\ddd-interaction-analysis-rule` — Full interaction analysis principles

