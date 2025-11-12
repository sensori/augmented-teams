# Stories Workflow Test Plan - MM3E Refactor Test

## Test Objective

Validate the complete template-driven stories workflow end-to-end in a fresh test environment.

---

## Test Scope

**Product:** Mutants & Masterminds 3rd Edition Character Creator (Simplified Test Version)
**Location:** `demo/mm3e/refactor-test/`
**Source Material:** `demo/mm3e/HeroesHandbook.pdf`

---

## Workflow Steps

### Step 1: Shape (/story-shape)
**Command:**
```bash
python behaviors/stories/stories_runner.py story-shape generate demo/mm3e/HeroesHandbook.pdf
```

**What it does:**
- Outputs instructions telling AI to load templates:
  - `story-map-decomposition-template.md`
  - `story-map-increments-template.md`
- AI then creates TWO files:
  - `demo/mm3e/refactor-test/docs/stories/map/mm3e-test-story-map.md`
  - `demo/mm3e/refactor-test/docs/stories/increments/mm3e-test-story-map-increments.md`

**Expected output:**
- Epic/feature/story hierarchy (10-20% identified, rest as ~X stories)
- Value increments with NOW/NEXT/LATER priorities
- Source material tracking

**Status:** ✅ Command outputs correct template references

---

### Step 2: Arrange (/story-arrange)
**Command:**
```bash
python behaviors/stories/stories_runner.py story-arrange generate demo/mm3e/refactor-test/docs/stories/map/mm3e-test-story-map.md
```

**What it does:**
- Parses story map
- Creates epic/feature folder structure in `map/`
- Creates story files using `story-doc-template.md`
- Archives obsolete folders

**Expected output:**
- Folder structure: `map/🎯 [Epic]/⚙️ [Feature]/`
- Story files: `📝 [Story].md` (created from template)

**Status:** ⏳ Pending

---

### Step 3: Discovery (/story-discovery)
**Command:**
```bash
python behaviors/stories/stories_runner.py story-discovery generate demo/mm3e/refactor-test/docs/stories/map/mm3e-test-story-map.md
```

**What it does:**
- Refines marketable increments
- Decomposes increment in focus 100% (all stories listed)
- Other increments stay as story counts (~X stories)
- Grooms stories (identifies ambiguous/complex)

**Expected output:**
- Updated story map with refined increments
- Increment in focus fully decomposed
- Grooming notes for complex stories
- Updated source material with Discovery Refinements

**Status:** ⏳ Pending

---

### Step 4: Explore (/story-explore)
**Command (choose one feature):**
```bash
python behaviors/stories/stories_runner.py story-explore generate demo/mm3e/refactor-test/docs/stories/map/mm3e-test-story-map.md
```

**Scope:** Choose ONE feature from increment in focus (e.g., "Allocate Abilities")

**What it does:**
- Outputs instructions telling AI to load `feature-overview-template.md`
- AI creates Feature Overview document with:
  - Domain AC (Core Concepts → Behaviors → Rules)
  - Acceptance Criteria for each story (When/Then format)
  - Consolidation decisions
  - Source material references

**Expected output:**
- `map/🎯 [Epic]/⚙️ [Feature]/⚙️ [Feature] - Feature Overview.md` (from template)
- Story files updated to reference feature document for AC

**Status:** ⏳ Pending

---

### Step 5: Specification (/story-specification)
**Command (choose subset of stories from explored feature):**
```bash
python behaviors/stories/stories_runner.py story-specification generate demo/mm3e/refactor-test/docs/stories/map/mm3e-test-story-map.md
```

**Scope:** Choose 2-3 stories from the explored feature

**What it does:**
- Outputs instructions (optionally referencing `scenario-template.md`)
- AI creates scenario specifications with:
  - Background (if repeated setup)
  - Happy path scenarios
  - Edge case scenarios
  - Error case scenarios
  - Scenario Outline with Examples (when warranted)

**Expected output:**
- Story files updated with Scenarios section filled
- Given/When/Then structure
- Examples tables for formulas/calculations

**Status:** ⏳ Pending

---

## Success Criteria

### Template Usage
- ✅ All commands reference templates correctly
- ✅ Story files created from story-doc-template.md
- ✅ Feature Overview created from feature-overview-template.md
- ✅ Story map files use templates for structure

### Output Quality
- ✅ Story files match expected format exactly
- ✅ Feature documents have proper Domain AC structure
- ✅ Scenarios follow Gherkin format
- ✅ All placeholders filled (no {placeholder} text remaining)

### Workflow Continuity
- ✅ Each phase builds on previous phase
- ✅ Source material tracking works across phases
- ✅ Folder structure consistent
- ✅ No regressions from pre-template version

---

## Notes

**Why CLI Commands Output Instructions:**
The stories commands are designed to output instructions that guide the AI agent on what to generate. This is by design - the commands coordinate the workflow and provide guidance, while the AI agent does the actual content generation following those instructions.

**Template References Working:**
- Shape command correctly references story-map templates
- Explore command correctly references feature-overview template  
- Arrange command loads and uses story-doc template (verified working)

**Next Actions:**
The user can either:
1. Follow the CLI output instructions manually to generate content
2. Use the commands in interactive mode where AI generates based on instructions
3. Create script to automate the workflow

