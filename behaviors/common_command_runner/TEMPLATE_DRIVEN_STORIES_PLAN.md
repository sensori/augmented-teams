# Template-Driven Stories Refactoring Plan

## Overview

Refactor stories behavior to use template-loading approach instead of hardcoded content in Python code and prompts. Current outputs are excellent - this refactoring maintains exact functionality while moving logic from code/prompts into reusable templates.

---

## Problem Statement

Currently, content generation logic is split across:
1. **Hardcoded in Python** - `StoryArrangeCommand.generate()` line 372 creates story files with f-string template
2. **Hardcoded in Prompts** - Shape and exploration commands have detailed formatting instructions in generate_instructions
3. **Unused Template Files** - 7 template files exist but aren't loaded by code

**Result:** Logic scattered, hard to maintain, templates don't match what code generates.

---

## Solution: Template Loading Infrastructure

Make commands **load actual templates** and fill placeholders, rather than hardcoding content.

### Design Principle
- ✅ Code loads template file
- ✅ Template contains structure + placeholders
- ✅ Code fills placeholders with values
- ✅ Same output as current (no functional changes)
- ❌ Don't hardcode content in Python f-strings
- ❌ Don't put detailed formatting in prompts

---

## Phase 1: Analyze Current Outputs

### 1.1 Capture Current Story File Output

**Source:** `stories_runner.py` line 372-395 (StoryArrangeCommand.generate())

**Current hardcoded template:**
```python
story_content = f"""# 📝 {story_name}

**Epic:** {epic_name}
**Feature:** {feature_name}

## Story Description

{story_name}

## Acceptance Criteria

- [ ] 

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

"""
```

**Action:** Extract to `templates/story-doc-template.md` with placeholders

### 1.2 Capture Current Feature Overview Output

**Source:** Exploration command generates Feature Overview docs

**Current approach:** AI generates based on instructions in `StoryExploreCommand.generate_instructions`

**Current instructions include:**
- Domain AC structure (Core Concepts → Behaviors → Rules)
- Feature-scoped domain perspective
- Story acceptance criteria in When/Then format
- Consolidation decisions section
- Source material tracking

**Action:** Create `templates/feature-overview-template.md` that matches actual demo/mm3e/ outputs

### 1.3 Capture Current Epic/Sub-Epic Output

**Source:** Discovery/Exploration generates epic/sub-epic docs

**Current approach:** AI generates based on instructions

**Action:** Create templates matching actual outputs in demo/mm3e/

### 1.4 Capture Story Map Outputs

**Source:** Shape command generates story map files

**Current approach:** AI generates based on detailed instructions in `StoryShapeCommand.generate_instructions`

**Includes:**
- Tree structure with emojis (🎯 📂 ⚙️ 📝)
- Legend section
- Epic/Feature/Story hierarchy
- Story counting (~X stories)
- Source Material section

**Action:** Create templates for both story-map.md and story-map-increments.md

---

## Phase 2: Create Template Loading Infrastructure

### 2.1 Add Template Loader to Base Command

**File:** `behaviors/common_command_runner/common_command_runner.py`

**Add:**
```python
class Command:
    def load_template(self, template_path: str) -> str:
        """Load template file content"""
        template_file = Path(template_path)
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        return template_file.read_text(encoding='utf-8')
    
    def fill_template(self, template_content: str, **kwargs) -> str:
        """Fill template placeholders with values"""
        # Support both {placeholder} and {{placeholder}} formats
        # Use simple string format for now, could upgrade to Jinja2 later
        return template_content.format(**kwargs)
    
    def load_and_fill_template(self, template_path: str, **kwargs) -> str:
        """Load template and fill placeholders in one step"""
        template_content = self.load_template(template_path)
        return self.fill_template(template_content, **kwargs)
```

**Design Decision:**
- Use simple `str.format()` with `{placeholder}` syntax
- Could upgrade to Jinja2 later if needed (conditionals, loops)
- Keep it simple for now since our templates are mostly static

### 2.2 Update StoryArrangeCommand to Use Template

**File:** `behaviors/stories/stories_runner.py`

**Current code (line 372-395):**
```python
story_content = f"""# 📝 {story_name}
**Epic:** {epic_name}
...
"""
```

**Refactor to:**
```python
# Load template
template_path = Path(__file__).parent / "templates" / "story-doc-template.md"
story_content = self.load_and_fill_template(
    str(template_path),
    story_name=story_name,
    epic_name=epic_name,
    feature_name=feature_name
)
```

**Template file:**
```markdown
# 📝 {story_name}

**Epic:** {epic_name}
**Feature:** {feature_name}

## Story Description

{story_name}

## Acceptance Criteria

- [ ] 

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase
```

---

## Phase 3: Extract Templates from Actual Outputs

### 3.1 Story Map Decomposition Template

**Extract from:** Actual demo/mm3e/ story map files

**Source:** `demo/mm3e/docs/stories/map/mm3e-character-creator-story-map.md`

**Create:** `templates/story-map-decomposition-template.md`

**Placeholders:**
- `{product_name}` - Product name
- `{system_purpose}` - High-level purpose
- `{epic_hierarchy}` - Epic/feature/story tree structure
- `{source_material}` - Source tracking section

**Structure:**
```markdown
# Story Map: {product_name}

## System Purpose
{system_purpose}

---

## Legend
- 🎯 **Epic** - High-level capability
- 📂 **Sub-Epic** - Sub-capability (when epic has > 9 features)
- ⚙️ **Feature** - Cohesive set of functionality
- 📝 **Story** - Small increment of behavior (3-12d)

---

## Story Map

{epic_hierarchy}

---

## Source Material

{source_material}
```

### 3.2 Story Map Increments Template

**Extract from:** Actual demo/mm3e/ increments file

**Source:** `demo/mm3e/docs/stories/increments/mm3e-character-creator-story-map-increments.md`

**Create:** `templates/story-map-increments-template.md`

**Placeholders:**
- `{product_name}`
- `{system_purpose}`
- `{increments_organized}` - NOW/NEXT/LATER structure
- `{source_material}`

### 3.3 Feature Overview Template

**Extract from:** Actual demo/mm3e/ feature documents

**Source:** 
- `demo/mm3e/docs/stories/map/🎯 Create Character/⚙️ Allocate Abilities/⚙️ Allocate Abilities - Feature Overview.md`
- `demo/mm3e/docs/stories/map/🎯 Persist Character Data/⚙️ Save Character/⚙️ Save Character - Feature Overview.md`

**Create:** `templates/feature-overview-template.md` (update existing)

**Placeholders:**
- `{feature_name}`
- `{epic_name}`
- `{feature_purpose}`
- `{domain_ac}` - Core Concepts + Behaviors + Rules
- `{stories_with_ac}` - All stories with their AC
- `{consolidation_decisions}`
- `{domain_rules_referenced}`
- `{source_material}`

### 3.4 Epic Overview Template

**Extract from:** What AI should generate

**Create:** `templates/epic-overview-template.md` (update existing)

**Placeholders:**
- `{epic_name}`
- `{epic_purpose}`
- `{shared_domain_concepts}` - Concepts used by multiple features
- `{features_list}` - Features in this epic
- `{source_material}`

### 3.5 Sub-Epic Overview Template

**Extract from:** What AI should generate

**Create:** `templates/sub-epic-overview-template.md` (update existing)

**Placeholders:**
- `{sub_epic_name}`
- `{epic_name}`
- `{sub_epic_purpose}`
- `{shared_domain_concepts}`
- `{features_list}`
- `{source_material}`

---

## Phase 4: Update Commands to Load Templates

### 4.1 Update StoryArrangeCommand

**File:** `behaviors/stories/stories_runner.py` line 370-398

**Current:** Hardcoded f-string template

**Change to:**
```python
# Load template for story files
template_path = Path(__file__).parent / "templates" / "story-doc-template.md"
story_content = self.load_and_fill_template(
    str(template_path),
    story_name=story_name,
    epic_name=epic_name,
    feature_name=feature_name
)
```

### 4.2 Update StoryShapeCommand

**File:** `behaviors/stories/stories_runner.py` line 30-72

**Current:** Long generate_instructions with detailed formatting requirements

**Change to:**
```python
def __init__(self, content: Content, base_rule: BaseRule):
    # Simplified instructions - detailed structure comes from templates
    generate_instructions = """Generate story map using templates.

Load templates:
- Story map template: behaviors/stories/templates/story-map-decomposition-template.md
- Increments template: behaviors/stories/templates/story-map-increments-template.md

Fill placeholders:
- {product_name}: Infer from context or ask user
- {system_purpose}: Extract from requirements
- {epic_hierarchy}: Build from analysis (see principles)
- {increments_organized}: Identify value increments (NOW/NEXT/LATER)
- {source_material}: Track source document and sections used

Follow principles from rule file for hierarchy structure, business language, etc.
"""
    super().__init__(content, base_rule, generate_instructions=generate_instructions)
```

**Remove from instructions:** Detailed formatting (emoji structure, tree characters, etc.) - that's in the template now

**Keep in instructions:** High-level logic (what to generate, which principles apply, decision-making)

### 4.3 Update StoryExploreCommand

**File:** `behaviors/stories/stories_runner.py` line 741-774

**Current:** Detailed instructions about Feature Overview structure

**Change to:**
```python
def __init__(self, content: Content, base_rule: BaseRule):
    generate_instructions = """Write acceptance criteria using Feature Overview template.

Load templates based on scope:
- Feature: behaviors/stories/templates/feature-overview-template.md
- Epic: behaviors/stories/templates/epic-overview-template.md (if creating epic-level Domain AC)
- Sub-Epic: behaviors/stories/templates/sub-epic-overview-template.md (if sub-epic exists)

Fill placeholders:
- {feature_name}, {epic_name}: From story structure
- {feature_purpose}: Extract from story descriptions
- {domain_ac}: Write Domain AC (Core Concepts → Behaviors → Rules)
- {stories_with_ac}: Write AC for each story (When/Then format)
- {consolidation_decisions}: Document consolidate/separate decisions with reasoning
- {source_material}: Track sections referenced

CRITICAL - CONSOLIDATION REVIEW:
Present consolidation questions to user BEFORE finalizing.
Document assumptions about same/different logic.

Follow principles from rule file for feature-scoped domain perspective and AC format.
"""
    super().__init__(content, base_rule, generate_instructions=generate_instructions)
```

**Remove from instructions:** Detailed markdown structure (headings, sections, formatting) - that's in template

**Keep in instructions:** Logic decisions (consolidation review, domain perspective, what content to include)

---

## Phase 5: Validate Template Consistency

### 5.1 Compare Template to Current Outputs

**For each template, verify:**
1. Load actual generated file from demo/mm3e/
2. Compare structure to template
3. Ensure all sections present
4. Verify placeholder positions correct
5. Test that filling placeholders produces identical output

**Files to validate against:**
- `demo/mm3e/docs/stories/map/🎯 Create Character/⚙️ Allocate Abilities/⚙️ Allocate Abilities - Feature Overview.md`
- `demo/mm3e/docs/stories/map/🎯 Create Character/⚙️ Allocate Abilities/📝 User increases ability rank.md`
- `demo/mm3e/docs/stories/map/mm3e-character-creator-story-map.md`
- `demo/mm3e/docs/stories/increments/mm3e-character-creator-story-map-increments.md`

### 5.2 Test Template Loading

**Create test script:** `behaviors/stories/test_template_loading.py`

**Test cases:**
1. Load story-doc-template, fill with sample data, verify output matches current hardcoded format
2. Load feature-overview-template, fill with sample data, verify structure
3. Load story-map-decomposition-template, verify can produce same output
4. Load story-map-increments-template, verify can produce same output

### 5.3 Regression Testing

**Run existing tests:**
```bash
python behaviors/stories/stories_runner_test.py
```

**Verify:**
- All tests still pass
- Generated content matches expected format
- No regressions in validation heuristics

---

## Phase 6: Update Prompts to Reference Templates

### 6.1 Update Shape Prompts

**File:** `behaviors/stories/shape/story-shape-prompts.md`

**Current:** Detailed formatting instructions embedded in prompts

**Change to:**
```markdown
## Generate Action Prompts

### Load Templates

**MANDATORY**: Load these template files:
1. `behaviors/stories/templates/story-map-decomposition-template.md`
2. `behaviors/stories/templates/story-map-increments-template.md`

### Fill Placeholders

**From context/user:**
- `{product_name}`: Product or feature name (infer from context or ask)
- `{system_purpose}`: High-level purpose (extract from requirements)

**Generate from analysis:**
- `{epic_hierarchy}`: Build epic/feature/story tree following principles
  - Apply §1.1 (Story Map Hierarchy)
  - Apply §1.2 (Business Language - [Verb] [Noun])
  - Apply §1.4 (Story Counting - ~X stories for unexplored)
  - Apply §1.5 (7±2 Sizing)
  
- `{increments_organized}`: Identify marketable value increments
  - Apply §1.5 (Marketable Increments)
  - Use NOW/NEXT/LATER priorities
  - Include relative sizing notes

- `{source_material}`: Track source document and sections referenced

### Template Structure

DO NOT override template structure - templates define:
- Section headings (## System Purpose, ## Legend, etc.)
- Emoji usage (🎯 📂 ⚙️ 📝)
- Tree characters (│ ├─ └─)
- Markdown formatting

YOU define:
- Content for each placeholder
- Epic/feature/story names and relationships
- Story counts and priorities
```

**Remove:** All detailed formatting instructions (emoji lists, tree character usage, exact heading structure) - moved to template

**Keep:** Logic instructions (which principles apply, what decisions to make, how to analyze)

### 6.2 Update Exploration Prompts

**File:** `behaviors/stories/exploration/ac-consolidation-prompts.md` or inline in StoryExploreCommand

**Current:** Instructions describe Feature Overview structure in detail

**Change to:**
```markdown
## Generate Action Prompts

### Load Template

**MANDATORY**: Load template file:
- `behaviors/stories/templates/feature-overview-template.md`

### Fill Placeholders

**From story structure:**
- `{feature_name}`: Feature being explored
- `{epic_name}`: Parent epic name

**Generate from analysis:**
- `{feature_purpose}`: Extract from story descriptions

- `{domain_ac}`: Write Domain AC following structure in template
  - Core Domain Concepts (what exists)
  - Domain Behaviors (what operations)
  - Domain Rules (formulas, constraints)
  - Apply §3.1 (Feature-Scoped Domain Perspective)
  
- `{stories_with_ac}`: Write acceptance criteria for each story
  - Use When/Then format (NO Given clauses)
  - Apply §3.1a (Domain AC), §3.1b (Behavioral AC)
  
- `{consolidation_decisions}`: Document consolidate/separate decisions
  - Apply §3.2 (Consolidation Review)
  - Present questions to user BEFORE finalizing
  
- `{domain_rules_referenced}`: Extract formulas/rules from source

- `{source_material}`: Inherit from story map, add exploration details

### Template Structure

Template defines all section headings and structure.
YOU define content for each placeholder.
```

---

## Phase 7: Rebuild Templates from Current Outputs

### 7.1 Story Doc Template (Already Good Structure)

**File:** `behaviors/stories/templates/story-doc-template.md`

**Current template is PERFECT** - matches hardcoded output exactly

**Action:** Keep as-is, just update code to load it

### 7.2 Feature Overview Template

**File:** `behaviors/stories/templates/feature-overview-template.md`

**Current template has good structure BUT:**
- Needs to match EXACT output from demo/mm3e/ files
- Check all sections present
- Verify section order correct
- Ensure all placeholders identified

**Action:** 
1. Read 3-5 actual Feature Overview files from demo/mm3e/
2. Extract common structure
3. Identify variable content → make placeholders
4. Update template to match actual outputs exactly

**Key sections to verify:**
```markdown
# ⚙️ {feature_name} - Feature Overview

**File Name**: `⚙️ {feature_name} - Feature Overview.md`
**Epic:** {epic_name}

## Feature Purpose
{feature_purpose}

---

## Domain AC (Feature Level)

### Core Domain Concepts
{domain_concepts}

---

### Domain Behaviors
{domain_behaviors}

---

### Domain Rules
{domain_rules}

---

## Stories ({story_count} total)

{stories_with_ac}

---

## Consolidation Decisions

{consolidation_decisions}

---

## Domain Rules Referenced

{domain_rules_referenced}

---

## Source Material

{source_material}
```

### 7.3 Story Map Decomposition Template

**File:** `behaviors/stories/templates/story-map-decomposition-template.md`

**Extract from:** `demo/mm3e/docs/stories/map/mm3e-character-creator-story-map.md`

**Verify template has:**
1. Exact heading structure from actual outputs
2. Legend section with emoji definitions
3. Tree structure examples showing proper indentation
4. Story counting examples (~X stories)
5. Source Material section at bottom

**Key structure:**
```markdown
# Story Map: {product_name}

**File Name**: `{product_name}-story-map.md`
**Location**: `{solution_folder}/docs/stories/map/{product_name}-story-map.md`

## System Purpose
{system_purpose}

---

## Legend
- 🎯 **Epic** - High-level capability
- 📂 **Sub-Epic** - Sub-capability (when epic has > 9 features)
- ⚙️ **Feature** - Cohesive functionality
- 📝 **Story** - Small increment (3-12d)

---

## Story Map

{epic_hierarchy}

---

## Source Material

{source_material}
```

### 7.4 Story Map Increments Template

**File:** `behaviors/stories/templates/story-map-increments-template.md`

**Extract from:** `demo/mm3e/docs/stories/increments/mm3e-character-creator-story-map-increments.md`

**Verify template has:**
1. Value Increment structure (🚀 NOW/NEXT/LATER)
2. Story organization under increments
3. Relative sizing notes
4. Source Material tracking

### 7.5 Epic Overview Template

**File:** `behaviors/stories/templates/epic-overview-template.md`

**Extract from:** What SHOULD be generated (may not exist yet in demo/mm3e/)

**Structure based on:** Template guidance + sub-epic template pattern

### 7.6 Sub-Epic Overview Template

**File:** `behaviors/stories/templates/sub-epic-overview-template.md`

**Current template structure** looks reasonable - verify against any actual sub-epic docs if they exist

---

## Phase 8: Update Command Instructions

### 8.1 Simplify Shape Instructions

**Current instructions (line 30-72 in stories_runner.py):** ~42 lines of detailed formatting

**New instructions:** ~15 lines focusing on logic

```python
generate_instructions = """Generate story map using templates.

TEMPLATES TO LOAD:
- behaviors/stories/templates/story-map-decomposition-template.md
- behaviors/stories/templates/story-map-increments-template.md

PLACEHOLDERS TO FILL:
- {product_name}: Infer from context (recently viewed files, open files, pwd)
- {system_purpose}: Extract from requirements/vision
- {epic_hierarchy}: Build epic/feature/story tree
- {increments_organized}: Identify value increments with priorities
- {source_material}: Track source document sections used

APPLY PRINCIPLES:
- §1.1 Story Map Hierarchy (4 levels with emojis)
- §1.2 Business Language ([Verb] [Noun] format)
- §1.3 User AND System Activities
- §1.4 Story Counting (~X stories for unexplored areas)
- §1.5 7±2 Sizing thresholds
- §1.5 Marketable Increments (NOW/NEXT/LATER)

Template defines structure and formatting.
YOU define content following principles."""
```

**Reduction:** Formatting details moved to template, logic instructions remain

### 8.2 Simplify Exploration Instructions

**Current instructions (line 741-774):** ~33 lines with detailed structure

**New instructions:** ~20 lines focusing on logic

```python
generate_instructions = """Write acceptance criteria using Feature Overview template.

TEMPLATE TO LOAD:
- behaviors/stories/templates/feature-overview-template.md

PLACEHOLDERS TO FILL:
- {feature_name}, {epic_name}: From story structure
- {feature_purpose}: Extract from story descriptions
- {domain_ac}: Write Domain AC (Core Concepts → Behaviors → Rules)
  - Apply §3.1 Feature-Scoped Domain Perspective
  - Only facets THIS feature operates on
- {stories_with_ac}: Write AC for each story
  - Apply §3.1b When/Then format (NO Given)
- {consolidation_decisions}: Document with reasoning
  - Apply §3.2 Consolidation Review
  - PRESENT to user BEFORE finalizing
- {source_material}: Inherit from map, add exploration details

CRITICAL - CONSOLIDATION REVIEW:
Present consolidation matrix to user with questions.
Wait for user answers before finalizing.

Template defines section structure.
YOU define content following principles."""
```

---

## Phase 9: Testing and Validation

### 9.1 Template Loading Tests

**Create:** `behaviors/stories/test_template_loading.py`

```python
def test_load_story_template():
    """Verify story template loads and fills correctly"""
    cmd = StoryArrangeCommand(content, base_rule)
    result = cmd.load_and_fill_template(
        "behaviors/stories/templates/story-doc-template.md",
        story_name="User increases ability rank",
        epic_name="Create Character",
        feature_name="Allocate Abilities"
    )
    assert "# 📝 User increases ability rank" in result
    assert "**Epic:** Create Character" in result
    assert "## Acceptance Criteria" in result

def test_load_feature_template():
    """Verify feature template loads and fills correctly"""
    # Similar test for feature-overview-template
    pass
```

### 9.2 Output Comparison Tests

**For each template:**
1. Generate using NEW template-loading code
2. Compare to EXISTING output from demo/mm3e/
3. Verify structure matches exactly
4. Verify content sections in same order
5. Verify formatting identical

**Files to compare:**
- Generated story file vs `demo/mm3e/docs/stories/map/🎯 Create Character/⚙️ Allocate Abilities/📝 User increases ability rank.md`
- Generated feature file vs `demo/mm3e/docs/stories/map/🎯 Create Character/⚙️ Allocate Abilities/⚙️ Allocate Abilities - Feature Overview.md`

### 9.3 Integration Tests

**Run full workflow:**
```bash
# Test shape with templates
python behaviors/stories/stories_runner.py story-shape generate

# Test arrange with templates  
python behaviors/stories/stories_runner.py story-arrange generate

# Test explore with templates
python behaviors/stories/stories_runner.py story-explore generate
```

**Verify:** All commands work, outputs match current quality

---

## Phase 10: Cleanup

### 10.1 Remove Duplicate Templates

**After confirming new templates work:**

Delete old/unused templates:
- `feature-doc-template.md` (superseded by feature-overview-template.md)

**Keep:**
- `story-doc-template.md` (used by arrange)
- `feature-overview-template.md` (used by explore)
- `epic-overview-template.md` (used by explore for epic-level)
- `sub-epic-overview-template.md` (used by explore for sub-epics)
- `story-map-decomposition-template.md` (used by shape)
- `story-map-increments-template.md` (used by shape)
- `scenario-template.md` (used by specification)

### 10.2 Update Documentation

**File:** `behaviors/common_command_runner/TEMPLATE_USAGE.md`

**Document:**
- How to create new templates
- Placeholder syntax ({placeholder})
- How commands load templates
- Template file naming conventions
- Where templates live (behaviors/{feature}/templates/)

---

## Success Criteria

- ✅ Base Command class has `load_template()` and `fill_template()` methods
- ✅ StoryArrangeCommand loads story-doc-template instead of hardcoding
- ✅ StoryShapeCommand references templates in simplified instructions
- ✅ StoryExploreCommand references templates in simplified instructions
- ✅ All templates match EXACT current output format
- ✅ Prompts contain LOGIC, not FORMATTING
- ✅ All existing tests pass
- ✅ Output quality unchanged (verified against demo/mm3e/ files)
- ✅ Code is shorter (formatting moved to templates)
- ✅ Templates are actually used (not orphaned)

---

## Benefits

1. **Maintainability**: Formatting changes happen in templates, not scattered across code/prompts
2. **Consistency**: All outputs use same template structure
3. **Separation of Concerns**: 
   - Templates = Structure & Formatting
   - Code = Logic & Orchestration
   - Prompts = Decision-Making & Principles
4. **Reusability**: Templates can be used by multiple commands
5. **Quality**: Current excellent outputs preserved exactly
6. **Clarity**: Easier to understand what's being generated

---

## Implementation Order

1. **Phase 2** - Add template loading to base Command (30 min)
2. **Phase 3** - Extract templates from demo/mm3e/ actual outputs (2-3 hours)
3. **Phase 5** - Validate templates match current outputs (1 hour)
4. **Phase 4** - Update commands to load templates (1-2 hours)
5. **Phase 6** - Simplify prompts (remove formatting, keep logic) (1 hour)
6. **Phase 9** - Test everything (1-2 hours)
7. **Phase 10** - Cleanup and documentation (30 min)

**Total estimated time:** 1-2 days

---

## Risk Mitigation

### Risk: Templates don't match current outputs
**Mitigation:** Extract templates FROM actual demo/mm3e/ files, not from old unused templates

### Risk: Template loading breaks existing workflow
**Mitigation:** Add template loading as NEW capability, keep backward compatibility (allow direct strings)

### Risk: Tests fail after refactoring
**Mitigation:** Run tests after each phase, revert if failures

### Risk: Output quality degrades
**Mitigation:** Side-by-side comparison of old vs new outputs, verify identical before committing

---

## Key Design Decisions

### Why Not Jinja2?
- Current templates are simple substitution
- No conditionals or loops needed yet
- Keep it simple with `str.format()`
- Can upgrade later if complexity increases

### Why Keep Logic in Prompts?
- Prompts guide AI decision-making
- Templates are for structure, not decisions
- Example: "Should we consolidate?" = prompt logic
- Example: "Where does ## Domain AC go?" = template structure

### Why Extract from demo/mm3e/ not Old Templates?
- demo/mm3e/ files are **current working outputs**
- Old templates may not match current workflow
- Extract from reality, not outdated documentation

