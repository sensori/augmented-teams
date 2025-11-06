### Command: `ddd-analyze`

**Purpose:** Analyze code, text, or diagrams to extract domain structure following DDD principles (outcome verbs, user mental model ordering, domain-first organization, functional focus).

**Usage:**
* `\ddd-analyze` — Analyze currently open file to extract domain structure
* `\ddd-analyze <file-path>` — Analyze specific file
* `\ddd-analyze <directory-path>` — Analyze entire directory/module

**Rule:**
* `\ddd-structure-analysis-rule` — DDD structure analysis principles

**Valid Input:**
* **Documentation**: `["**/*.md", "**/*.txt", "**/*.mdc"]`
* **Code**: `["**/*.js", "**/*.ts", "**/*.py", "**/*.mjs", "**/*.jsx", "**/*.tsx"]`
* **Diagrams**: Any structured text representation of systems
* **Any text blob**: Plain text describing a system

**Steps:**

1. **User** invokes analysis via `\ddd-analyze` or `\ddd-analyze <path>`

2. **MANDATORY: AI Agent reads the rule file** (ddd-structure-analysis-rule.mdc):
   - Read § 1-7 to understand all DDD principles
   - Review DO/DON'T examples for each principle
   - NO EXCEPTIONS - cannot analyze without reading rules

3. **AI Agent** reads source material:
   - Read file(s) or scan directory contents
   - Understand code structure and purpose
   - Identify entry points and business flows

4. **AI Agent** identifies domain concepts:
   - Core business concepts (entities, values, services)
   - Domain capabilities and features
   - System infrastructure components
   - Relationships between concepts

5. **AI Agent** applies DDD principles:
   - § 1: Use outcome verbs, not communication verbs
   - § 2: Integrate system support under domain concepts
   - § 3: Order by user mental model (foundation → features)
   - § 4: Organize domain-first (domains before infrastructure)
   - § 5: Focus on functional accomplishment
   - § 6: Maximize integration of related concepts
   - § 7: Disambiguate similar concepts with precise verbs

6. **AI Agent** builds domain structure:
   - Start with functional purpose
   - Group concepts into domains
   - Order concepts by user mental model
   - Nest related concepts and implementation details
   - Embed relationships in each concept
   - Place infrastructure last

7. **AI Agent** validates against checklist:
   - [ ] Functional purpose at top
   - [ ] All verbs are outcome-focused (§1)
   - [ ] System support integrated under domains (§2)
   - [ ] Concepts ordered by user mental model (§3)
   - [ ] Domains before infrastructure (§4)
   - [ ] Functional purpose focused on accomplishment (§5)
   - [ ] Related concepts maximally integrated (§6)
   - [ ] Domain concepts are nouns, behaviors are verbs (§7)
   - [ ] Behaviors assigned to the concept that performs them (§8)
   - [ ] No noun redundancy in domain or concept names (§9)
   - [ ] Relationships embedded in each concept

8. **AI Agent** creates domain map file:
   - Creates `<name>-domain-map.txt` in same folder as source
   - Outputs text-based hierarchical structure
   - Uses tabs for nesting levels

9. **User** reviews and refines domain map

**Output Format:**

```
FUNCTIONAL PURPOSE: <what this accomplishes>

DOMAIN NAME 1
	<what this domain does>
	
	RELATIONSHIPS:
		USES: Infrastructure Component Y
	
	Foundation Concept A
		<what it does, properties, operations>
		
		RELATIONSHIPS:
			USES: Foundation Concept B
			CONTAINS: Nested Concept C
		
		Nested Concept C
			<details>
	
	Foundation Concept B
		<foundation concept>

SYSTEM INFRASTRUCTURE
	<technical systems>
	
	RELATIONSHIPS:
		SERVES: All domains
```

**Example Session:**

```
User: \ddd-analyze mm3e-effects-section.mjs

AI: Reading ddd-structure-analysis-rule.mdc to understand DDD principles...
    Reading mm3e-effects-section.mjs to analyze code structure...
    
    Identifying domain concepts:
    - PowerItem, Animation Resolution, Descriptor Sequence
    - Attack Result Indicators, Text Animation System
    - Movement Detection, Movement Type Detection
    - Sequence Runner Editor, Script Generation
    
    Grouping into domains:
    1. POWER ACTIVATION ANIMATION
    2. COMBAT OUTCOME FEEDBACK  
    3. MOVEMENT ANIMATION
    4. ANIMATION CUSTOMIZATION
    
    Applying DDD principles:
    ✓ § 1: Using outcome verbs (Animation, Feedback, Detection)
    ✓ § 2: Integrating system support (PowerItem under domain)
    ✓ § 3: Ordering by user model (PowerItem before Resolution)
    ✓ § 4: Domains before infrastructure
    ✓ § 5: Functional purpose (make powers feel distinct)
    ✓ § 6: Related concepts integrated
    ✓ § 7: Domain concepts are nouns (Animation, not Animation Resolution)
    ✓ § 8: Behaviors on performer (Resolution under PowerItem, not Animation)
    ✓ § 9: No noun redundancy (Power Animation + Animation Editor, not 3x Animation)
    
    Creating mm3e-animations-domain-map.txt...
    
    FUNCTIONAL PURPOSE: Make superhero powers feel distinct and combat outcomes immediately clear
    
    POWER ACTIVATION ANIMATION
        Animated visual effects when powers are used
        
        RELATIONSHIPS:
            USES: Foundry VTT Integration
            USES: Sequencer Library
        
        Power Item (PowerItem class)
            Wrapper for power providing characteristics needed for animation
            Stores descriptor, effect type, range, area shape
            ...
    
    ✓ Domain map created successfully!
```

**Validation After Analysis:**

After generating the structure, the AI Agent must validate:

1. **Verb Check** (§1): Are all concept names using outcome verbs?
   - ❌ "Visualizing X" → ✅ "X Animation"
   - ❌ "Showing Y" → ✅ "Y Indicators"

2. **Integration Check** (§2): Is system support integrated?
   - ✅ PowerItem nested under Power domain (not separate)
   - ✅ Text Animation System nested under indicators

3. **Order Check** (§3): Are concepts ordered by user mental model?
   - ✅ PowerItem comes before features that use it
   - ✅ Foundation concepts before built-on concepts

4. **Domain-First Check** (§4): Do domains come before infrastructure?
   - ✅ POWER ACTIVATION, COMBAT, CUSTOMIZATION before INFRASTRUCTURE

5. **Functional Check** (§5): Is purpose functionally focused?
   - ✅ "Make powers feel distinct" vs ❌ "Render visual effects"

6. **Relatedness Check** (§6): Are related concepts integrated?
   - ✅ Related concepts nested together (same goal)

7. **Noun Concept Check** (§7): Are domain concepts nouns, not verbs?
   - ✅ "Animation" (noun) with "Resolves" and "Executes" behaviors
   - ❌ "Animation Resolution" and "Animation Execution" (verb-based)
   - ✅ "Power Item" (noun) with "Stores" and "Generates" behaviors
   - ❌ "Power Item Storage" (verb-based)

8. **Relationships Check**: Are relationships embedded?
   - ✅ RELATIONSHIPS section in each concept
   - ❌ Separate "Key Relationships" section

**Common Issues:**

| Issue | Solution |
|-------|----------|
| Generic verbs ("showing", "displaying") | Replace with outcome ("animation", "feedback", "indicators") |
| Verb-based concepts ("Animation Resolution", "Data Extraction") | Use nouns with behaviors ("Animation" that resolves, "Data" that extracts) |
| Separate SYSTEM SUPPORT sections | Integrate under domain concepts they serve |
| Code-ordered concepts | Reorder by user mental model |
| System concepts first | Put domains first, infrastructure last |
| Technical framing | Reframe with functional purpose |
| Artificial separation | Integrate related concepts |
| Relationships in separate section | Embed in each concept |
| Duplicate nouns in domains ("X Animation", "Y Animation") | Integrate or use distinct nouns ("X Animation", "Y Editor") |
| Behaviors on wrong concept (resolution on result) | Move to performer (who does the behavior) |

**File Naming and Location:**

* Domain map file placed in **same folder as source material**
* Naming pattern: `<descriptive-name>-domain-map.txt`
* Example: For `mm3e-effects-section.mjs` → create `mm3e-animations-domain-map.txt`
* Text format with tab-based nesting

**Tips for AI Agent:**

* Read the rule file thoroughly before starting
* Look for user-facing features and capabilities first
* Identify foundation objects before features using them
* Group related concepts together
* Use domain/business terminology, not code terminology
* Name concepts as nouns (what they ARE), describe behaviors with verbs (what they DO)
* Check for noun redundancy: list all domain/concept names, look for duplicates
* Validate against all 9 principles before finishing
* If uncertain about ordering, ask "What does user encounter first?"
* If concept name sounds like a verb, ask "What noun does this create or represent?"
* If multiple domains share a noun, ask "Can these be integrated or renamed?"

---

**See Also:**
* `\ddd-validate` — Validate existing domain structure against principles
* `\ddd-interactions` — Create interaction analysis after domain map
* `\ddd-structure-analysis-rule` — Full DDD analysis principles with examples

