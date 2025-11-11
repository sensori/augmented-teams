### Command: `ddd-detailed-model`

**Purpose:** Extract detailed object model with concepts, relationships, and inheritance from domain documents (scaffolds, maps, interactions) following DDD detailed modeling principles.

**Usage:**
* `\ddd-detailed-model` — Extract model from currently open file
* `\ddd-detailed-model <file-path>` — Extract from specific file
* `\ddd-detailed-model <domain-scaffold.txt>` — Extract from scaffold file

**Rule:**
* `\ddd-detailed-model-rule` — DDD detailed model extraction principles

**Valid Input:**
* **BDD Domain Scaffolds**: `["**/*-domain-scaffold.txt", "**/bdd.domain.scaffold.txt"]`
* **Domain Maps**: `["**/*-domain-map.txt"]`
* **Domain Interactions**: `["**/*-domain-interactions.txt"]`
* **Documentation**: `["**/*.md", "**/*.txt"]`
* **Any structured domain description**

**Steps:**

1. **User** invokes extraction via `\ddd-detailed-model` or `\ddd-detailed-model <path>`

2. **MANDATORY: AI Agent reads the rule file** (ddd-detailed-model-rule.mdc):
   - Read § 1-5 to understand all detailed modeling principles
   - Review DO/DON'T examples for each principle
   - NO EXCEPTIONS - cannot extract without reading rules

3. **AI Agent** reads source material:
   - Read domain document (scaffold, map, or interactions)
   - Understand hierarchical structure
   - Identify behavioral descriptions and relationships

4. **AI Agent** applies § 1: Identify First-Order Concepts:
   - Extract all major nouns as potential concepts
   - From scaffolds: "describe" subjects and nested concepts
   - From maps: domain concepts
   - From interactions: actors and artifacts
   - Create list of all concepts found

5. **AI Agent** applies § 2: Map Relationships Using Natural Language:
   - For each concept, find relationship statements in source
   - Use exact phrasing: "is being processed by", "provides principled guidance"
   - Preserve conditional language: "may be", "can implement"
   - Determine cardinalities from context: (1:1), (1:*), (0:1)
   - Keep direction clear with arrows: `-->`

6. **AI Agent** applies § 3: Identify Inheritance Hierarchies:
   - Look for specialization patterns: "Command that implements..."
   - Group parent with children
   - Use `: ParentClass` notation
   - Note abstract base concepts
   - Verify no upward references

7. **AI Agent** applies § 4: Remove Implementation Details:
   - Remove all ID fields (conceptId, ruleId, etc.)
   - Use `ex:` instead of `enum:`
   - No section headers like "// Fields"
   - Keep only domain-meaningful attributes

8. **AI Agent** applies § 5: Create ASCII Diagram:
   - Design visual overview with major concepts
   - Use box drawing: ┌─┐│└┘├┤┬┴
   - Show key relationships with arrows
   - Include cardinalities
   - Add inheritance connections
   - Keep focused and readable

9. **AI Agent** builds detailed model:
   - Start with ASCII diagram at top
   - Define each concept with fields
   - Add relationships using natural language
   - Group parent/child classes together
   - Add relationship summary at end

10. **AI Agent** validates against checklist:
    - [ ] ASCII diagram shows major concepts
    - [ ] All first-order concepts identified (§1)
    - [ ] Relationships use natural language from source (§2)
    - [ ] Inheritance properly identified with `: ParentClass` (§3)
    - [ ] No ID fields or unnecessary headers (§4)
    - [ ] ASCII diagram is clear and focused (§5)
    - [ ] No upward references
    - [ ] Unidirectional where appropriate

11. **AI Agent** creates detailed model file:
    - Creates `<name>-detailed-model.txt` or `ddd-detailed-model.txt` in same folder
    - Outputs ASCII diagram first
    - Then detailed concept definitions
    - Then relationship summary

12. **User** reviews and refines detailed model

**Output Format:**

```
// ============================================================================
// DOMAIN CLASS DIAGRAM (ASCII)
// ============================================================================
/*
                        ┌──────────────┐
                        │   Content    │
                        ├──────────────┤
                        │ filePath     │
                        └──────┬───────┘
                               │ 1:1
                               │ processes
                               ▼
    ┌────────────┐       ┌──────────────┐
    │  BaseRule  │       │   Command    │
    ├────────────┤       ├──────────────┤
    │ ruleName   │       │ commandName  │
    └─────┬──────┘       └──────┬───────┘
          │ 1:*                 │
          │ has                 │ inherits
          ▼                     ▼
    ┌────────────┐        ┌──────────┐
    │ Principle  │        │   Code   │
    └────────────┘        │  Guiding │
                          └──────────┘

LEGEND:
  →  Association
  1:1  One-to-One
  1:*  One-to-Many
*/

// ============================================================================
// DOMAIN MODEL DETAILS
// ============================================================================

Content {
  filePath: string
  fileExtension: string
  contentType: ContentType (ex: CODE, TEST, DOCUMENTATION)
  
  - is being processed by --> Command (1:1)
  - has violations detected in it --> Violation[] (1:*)
}

Command {
  commandName: string
  status: CommandStatus (ex: PENDING, IN_PROGRESS, COMPLETE)
  
  - processes --> Content (1:1)
  - implements --> SpecializingRule (1:1)
}

CodeGuidingCommand : Command {
  validationMode: ValidationMode (ex: STRICT, LENIENT)
  
  - performs code augmented AI guidance
  - generates --> ViolationReport (1:1)
}

BaseRule {
  ruleName: string
  description: string
  
  - provides principled guidance through --> Principle[] (1:*)
}

SpecializingRule : BaseRule {
  fileExtensionPattern: string
  
  - selects appropriate specialized rule based on --> file extension pattern
}

// ============================================================================
// RELATIONSHIP SUMMARY
// ============================================================================

/*
INHERITANCE RELATIONSHIPS (IS-A):
- CodeGuidingCommand : Command
- SpecializingRule : BaseRule

COMPOSITION RELATIONSHIPS (HAS-A, STRONG):
- BaseRule HAS Principle[] (1:*)

ASSOCIATION RELATIONSHIPS:
- Content <-> Command (1:1)
- Command <-> SpecializingRule (1:1)
*/
```

**Example Session:**

```
User: \ddd-detailed-model bdd.domain.scaffold.txt

AI: Reading ddd-detailed-model-rule.mdc to understand detailed modeling principles...
    Reading bdd.domain.scaffold.txt to analyze domain structure...
    
    Step 4 - Identifying first-order concepts (§1):
    - Content (from "describe a piece of content")
    - Command (from "being processed by a command")
    - SpecializingRule (from "implements a specializing rule")
    - SpecializedRule (from "select appropriate specialized rule")
    - BaseRule (from "include base rule principles")
    - Principle (from "base rule principles")
    - Example (from "specialized examples with Dos and Donts")
    - CodeHeuristic (from "code heuristics for each principle")
    - Violation (from "analyze content for violations")
    - ViolationReport (from "assemble related violations")
    - CodeGuidingCommand (from "performs code augmented AI guidance")
    - IncrementalCommand (from "implements incremental runs")
    - Run (from "has completed a run")
    - RunHistory (from "save run to history")
    - PhaseCommand (from "is a phase in a workflow")
    - Workflow (from "phase in a workflow")
    - AIGuidanceSystem (from "send violation report to AI")
    - FixSuggestion (from "apply fix suggestions from AI")
    
    Step 5 - Mapping relationships using natural language (§2):
    - Content: "is being processed by" → Command
    - BaseRule: "provides principled guidance through" → Principle[]
    - SpecializingRule: "includes principles from" → BaseRule
    - Violation: "violates" → Principle
    - ViolationReport: "assembles related" → Violation[]
    
    Step 6 - Identifying inheritance (§3):
    - Command ← CodeGuidingCommand, IncrementalCommand, PhaseCommand
    - BaseRule ← SpecializingRule ← SpecializedRule
    
    Step 7 - Removing implementation details (§4):
    - Removing: commandId, ruleId, principleId, etc.
    - Converting: enum: → ex:
    - Removing: // Fields and // Relationships headers
    
    Step 8 - Creating ASCII diagram (§5):
    - Major concepts: Content, Command hierarchy, Rule hierarchy
    - Key relationships with cardinalities
    - Inheritance trees
    
    Applying all § 1-5 principles...
    
    Validating model:
    ✓ ASCII diagram clear and focused
    ✓ All first-order concepts identified
    ✓ Natural language preserved from source
    ✓ Inheritance properly shown with : notation
    ✓ No ID fields or unnecessary headers
    ✓ No upward references
    ✓ Unidirectional relationships appropriate
    
    Creating ddd-detailed-model.txt...
    
    ✓ Detailed model created successfully!
```

**Validation After Extraction:**

After generating the model, the AI Agent must validate:

1. **Concept Check** (§1): Are all major nouns extracted?
   - Check source for any missed concepts
   - Verify no implementation concepts added

2. **Language Check** (§2): Is natural language preserved?
   - ✅ "is being processed by" not "has" or "uses"
   - ✅ "provides principled guidance through" not "contains"

3. **Inheritance Check** (§3): Are hierarchies correct?
   - ✅ Uses `: ParentClass` notation
   - ✅ No upward references
   - ✅ Parent and children grouped together

4. **Clean Model Check** (§4): Are implementation details removed?
   - ✅ No ID fields (ruleId, commandId, etc.)
   - ✅ No "// Fields" headers
   - ✅ Using `ex:` not `enum:`

5. **Diagram Check** (§5): Is ASCII diagram effective?
   - ✅ Shows architectural overview
   - ✅ Relationships labeled
   - ✅ Readable and focused

**Common Issues:**

| Issue | Solution |
|-------|----------|
| Missed concepts | Re-scan source for all nouns |
| Generic "has"/"uses" | Go back to source, use exact phrasing |
| ID fields present | Remove all *Id fields |
| Base knows subclasses | Remove upward references |
| Complex diagram | Focus on architectural view only |
| Section headers present | Remove // Fields and // Relationships |
| enum: instead of ex: | Replace all enum: with ex: |
| Bidirectional when uni | Check if both directions needed |

**File Naming and Location:**

* Detailed model file placed in **same folder as source material**
* Naming pattern: `<descriptive-name>-detailed-model.txt` or `ddd-detailed-model.txt`
* Example: For `bdd.domain.scaffold.txt` → create `ddd-detailed-model.txt`
* Text format with ASCII diagrams

**Tips for AI Agent:**

* Read the rule file thoroughly before starting
* Extract ALL nouns - don't skip "small" concepts
* Use exact quotes from source for relationships
* Check for specialization keywords: "that implements", "that specializes"
* Remove ID fields systematically
* Keep ASCII diagram focused on architecture
* Validate against all 5 principles before finishing
* If concept seems like implementation detail, check source - is it really there?
* If relationship sounds generic, go back to source for exact wording
* Group related concepts (parent/children) together in output

---

**See Also:**
* `\ddd-analyze` — Extract domain structure first (recommended before detailed model)
* `\ddd-interactions` — Analyze domain interactions
* `\ddd-detailed-model-validate` — Validate existing detailed model
* `\ddd-detailed-model-rule` — Full detailed modeling principles with examples

