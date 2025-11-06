### Command: `ddd-validate-cmd.md`

**Purpose:** Validate existing domain model (JSON or text) against DDD domain analysis principles.

**Usage:**
* `\ddd-validate` — Validate currently open domain model file
* `\ddd-validate <file-path>` — Validate specific domain model file
* AI-driven only — No Python runner implementation needed for this validation

**Rule:**
* `\ddd-structure-analysis-rule` — DDD structure analysis principles (§1-9)

**Valid Files:**
* **JSON domain models**: `["**/*-domain.json", "**/*-domain-model.json", "**/domain-*.json"]`
* **Text domain maps**: `["**/*-domain-map.txt", "**/*-domain-map.md", "**/domain-map.*"]`

**Division of Labor:**
* **Code** loads and presents:
  - Domain model (JSON or text)
  - DDD principles from rule file
  - DO/DON'T examples organized by principle
  - **AUTO-DETECTED violations** (pre-identified by pattern matching):
    * § 9 noun redundancy (multiple domains/concepts with same root noun)
    * § 7 verb-based concepts (names ending in "-tion", "-ing")
    * § 1 enablement verbs ("Provides", "Enables", "Allows")
* **AI Agent** (chat in conversation) has TWO validation modes:
  - **Mode 1 - Verify Code-Detected Violations**: 
    * Review auto-detected § 1, 7, 9 violations from code
    * Confirm line numbers and patterns are accurate
    * Apply fixes immediately using search_replace
  - **Mode 2 - Semantic Analysis** (§ 1-9):
    * Manually validate against all 9 principles
    * Identify violations requiring human-like understanding
    * Suggest fixes using DO examples as templates
  - **MUST fix ALL violations** (both code-detected and AI-detected)
  - Reports findings to user

**Steps:**

1. **User** invokes validation via `\ddd-validate` or `\ddd-validate <file-path>`
2. **Code** loads domain model file (JSON or text)
3. **Code** loads ddd-structure-analysis-rule.mdc
4. **Code** runs static checks and AUTO-DETECTS violations:
   - `detect_noun_redundancy()` → finds duplicate nouns in domain names (§ 9)
   - `detect_noun_redundancy()` → finds duplicate nouns in concept names (§ 9)
   - `detect_verb_based_concepts()` → finds "-ing" or "-tion" concept names (§ 7)
   - `detect_enablement_verbs()` → finds "provides", "enables" in behaviors (§ 1)
   - **Outputs PRE-IDENTIFIED violations** with confidence scores to AI
5. **Code** presents domain map, principles, and **auto-detected violations** to AI
6. **MANDATORY: AI Agent MUST read the rule file**:
   - Read § 1-9 to understand all DDD principles
   - NO EXCEPTIONS - cannot validate without reading rules
7. **AI validates in TWO MODES:**
   - **Mode 1**: VERIFY code-detected violations, then FIX immediately
   - **Mode 2**: MANUALLY ANALYZE against § 1-9, IDENTIFY semantic violations, then FIX
8. **AI Agent** reports findings:
   - List ALL violations by principle (auto-detected + manually found)
   - Provide specific locations (line numbers)
   - Suggest fixes using DO examples
9. **Optional: AI Agent fixes violations** (if user requests)
10. **User** reviews results

**Validation Checklist:**

The AI Agent must verify:

- [ ] **§1 Outcome Verbs**: All concept names use outcome/artifact verbs, not communication verbs
  - ❌ "Visualizing X", "Showing Y", "Displaying Z", "Provides X"
  - ✅ "X Animation", "Y Indicators", "Z Feedback"

- [ ] **§2 Integration**: System support integrated under domain concepts
  - ❌ Separate "SYSTEM SUPPORT FOR X" section
  - ✅ "Technical Implementation" nested under X

- [ ] **§3 User Ordering**: Concepts ordered by user mental model
  - ❌ Features before objects they operate on
  - ✅ Foundation objects → Features → Infrastructure

- [ ] **§4 Domain-First**: Domain concepts before system infrastructure
  - ❌ "RENDERING SYSTEM" → "Powers" → "Combat"
  - ✅ "POWERS" → "COMBAT" → "SYSTEM INFRASTRUCTURE"

- [ ] **§5 Functional Purpose**: Purpose states functional accomplishment
  - ❌ "Render visual effects"
  - ✅ "Make powers feel distinct through animation"

- [ ] **§6 Concept Integration**: Related concepts maximally integrated
  - ❌ Animation Resolution in separate section from Matching
  - ✅ Animation Resolution nested under Matching

- [ ] **§7 Noun Concepts**: Domain concepts are nouns, behaviors are verbs
  - ❌ "Animation Resolution", "Data Extraction", "Script Generation"
  - ✅ "Animation" (noun) with "Resolves" behavior, "Script" with "Generates" behavior

- [ ] **§8 Behavior Assignment**: Behaviors assigned to the concept that performs them
  - ❌ Resolution logic under Animation (the result)
  - ✅ Resolution logic under PowerItem (who does it)

- [ ] **§9 No Noun Redundancy**: No duplicate root nouns in domain/concept names
  - ❌ "POWER ANIMATION", "MOVEMENT ANIMATION", "ANIMATION CUSTOMIZATION" (separate domains)
  - ✅ **INTEGRATE FIRST**: Nest "Movement-Triggered Animation" and "Animation Customization" UNDER "Power Activation Animation"
  - ✅ Only rename if integration impossible: "POWER ANIMATION" vs "COMBAT FEEDBACK" (truly distinct)

**Example Output:**

```
======================================================================
DDD Domain Map Validation: mm3e-animations-domain-map.txt
======================================================================

AUTO-DETECTED VIOLATIONS:
----------------------------------------------------------------------

❌ § 9 Violation: DOMAIN_NOUN_REDUNDANCY [HIGH (95%)]
   Lines 3, 212, 249
   Domain noun 'ANIMATION' appears in 3 domains: POWER ACTIVATION ANIMATION, MOVEMENT ANIMATION, ANIMATION CUSTOMIZATION
   Affected names: POWER ACTIVATION ANIMATION, MOVEMENT ANIMATION, ANIMATION CUSTOMIZATION
   **FIX**: INTEGRATE related domains under parent, DO NOT just rename

❌ § 7 Violation: VERB_BASED_CONCEPT [HIGH (85%)]
   Line 173
   Concept 'Combat Data Extraction' uses verb-based noun (ends with 'tion'). Should be noun with behavior.

❌ § 1 Violation: ENABLEMENT_VERB [MEDIUM (70%)]
   Line 17
   Line uses vague enablement verb 'Provides'. Use specific outcome verb instead.
   Text: Provides a generated Animation from multiple sources through priority sy...

----------------------------------------------------------------------
Total auto-detected violations: 3

======================================================================
AI AGENT VALIDATION REQUIRED
======================================================================

Manual Validation Results:
=========================================

✗ § 1 Outcome Verbs: 1 VIOLATION (1 auto-detected verified)
  Line 17: "Provides" → Should be "Resolves"

✓ § 2 Integration: PASS
  System support properly integrated under domains

✓ § 3 User Ordering: PASS
  PowerItem comes before features that use it

✓ § 4 Domain-First: PASS
  Domains before SYSTEM INFRASTRUCTURE

✓ § 5 Functional Purpose: PASS
  Purpose is functionally focused

✓ § 6 Concept Integration: PASS
  Related concepts properly nested

✗ § 7 Noun Concepts: 2 VIOLATIONS (1 auto-detected verified + 1 additional)
  Line 173: "Combat Data Extraction" → Should be "Combat Result" with extraction behaviors
  Line 298: "Script Generation" → Should be "Sequencer Script" with generation behaviors

✓ § 8 Behavior Assignment: PASS
  Behaviors correctly assigned to performers

✗ § 9 No Noun Redundancy: 1 VIOLATION (1 auto-detected verified)
  Lines 3, 161, 198: Three domains use "ANIMATION"
  **FIX APPROACH**: INTEGRATE domains, do NOT rename
  → Nest "Movement Animation" and "Animation Customization" UNDER "Power Activation Animation"

TOTAL: 4 violations found (3 auto-detected + 1 manual)

Suggested Fixes:
----------------

1. **§ 9 Integration Fix** - Integrate domains sharing same noun:
   
   BEFORE (WRONG - separate domains):
   ```
   POWER ACTIVATION ANIMATION
     ...
   
   MOVEMENT ANIMATION
     Movement Detection
     Movement Type Detection
   
   ANIMATION CUSTOMIZATION
     Sequence Runner Editor
   ```
   
   AFTER (CORRECT - integrated):
   ```
   POWER ACTIVATION ANIMATION
     ... existing concepts ...
     
     Movement-Triggered Animation
       Movement Detector
       Movement Type Detector
       Movement Power Resolver
     
     Animation Customization
       Sequence Runner Editor
       Sequencer Script
   ```
   **Why**: Movement and Customization exist ONLY for power animations
   **Result**: Single cohesive domain instead of artificial separation

2. **§ 7 Noun Concepts Fix** - Use agent nouns instead of verb nouns:
   ```
   "Animation Resolution" → "Animation Resolver"
   "Combat Data Extraction" → "Combat Data Extractor"
   "Movement Detection" → "Movement Detector"
   ```

Apply fixes? (y/n)
```

**Common Validation Issues:**

| Violation | Principle | Fix |
|-----------|-----------|-----|
| "Visualizing X", "Provides Y" | §1 | Rename to "X Animation", "Resolves Y" |
| "Showing Y" | §1 | Rename to "Y Indicators" |
| Separate SYSTEM SUPPORT section | §2 | Integrate under domain |
| Features before objects | §3 | Reorder: objects → features |
| "UI Layer" before domains | §4 | Move domains first |
| "Render effects" purpose | §5 | Reframe functionally |
| Separated related concepts | §6 | Nest/integrate together |
| "Animation Resolution", "Data Extraction" | §7 | Use agent nouns: "Animation Resolver", "Data Extractor" |
| Resolution logic under result concept | §8 | Move to performer (who does it) |
| Multiple domains with same noun | §9 | **INTEGRATE domains first** (90%), only rename if truly distinct (10%) |

**Validation Modes:**

* **Quick** (default): Validates structure and naming
* **Thorough** (`--thorough`): Validates + suggests specific improvements
* **Fix** (`--fix`): Validates + applies fixes automatically

**Note:** Currently AI-only. Future automation will parse JSON/text and perform structural checks.

---

**See Also:**
* `\ddd-analyze` — Extract domain model from code/text
* `\ddd-structure-analysis-rule` — Full DDD principles

