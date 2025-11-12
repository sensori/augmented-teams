# Story Shape Prompts

## Generate Action Prompts

### Load Templates

**MANDATORY**: Load these template files:
1. `behaviors/stories/templates/story-map-decomposition-template.md`
2. `behaviors/stories/templates/story-map-increments-template.md`

### Fill Placeholders

**Infer from context (or ask if missing):**
- `{product_name}`: Product name (e.g., "MM3E Online Character Creator")
- `{product_name_slug}`: Filename version (e.g., "mm3e-character-creator")
- `{solution_folder}`: Detected from recently viewed files, open files, or current directory
  - Example: User viewing `demo/mm3e/HeroesHandbook.pdf` → Use `demo/mm3e/`
  - Example: At workspace root → Create new folder
- `{system_purpose}`: High-level purpose and user goals

**Generate from analysis:**
- `{epic_hierarchy}`: Build epic/feature/story tree structure
  - Apply §1.1 Story Map Hierarchy (4 levels with emojis: 🎯 📂 ⚙️ 📝)
  - Apply §1.2 Business Language ([Verb] [Noun] format, NO "Epic:" prefix)
  - Apply §1.3 User AND System Activities (both perspectives)
  - Apply §1.4 Story Counting (~X stories for unexplored, 10-20% identified)
  - Apply §1.5 7±2 Sizing (Epic: 4-9 features, Feature: 4-9 stories)
  - Use tree characters: │ ├─ └─ for hierarchy
  
- `{increments_organized}`: Identify marketable value increments
  - Apply §1.5 Marketable Increments
  - Use NOW/NEXT/LATER priorities
  - Include relative sizing notes (compared to previous work)
  - Format: 🚀 **Value Increment X: [Name] - [Priority]**

- `{source_material}`: Track source document and sections referenced
  - Include primary source location
  - List sections/pages referenced
  - Add date generated
  - Add context note for Discovery phase

### Template Structure

**DO NOT override template structure** - templates define:
- File header format and metadata
- Section headings (## System Purpose, ## Legend, etc.)
- Legend content (emoji definitions)
- Source Material section placement

**YOU define:**
- Content for each placeholder
- Epic/feature/story names following [Verb] [Noun] format
- Story counts and priorities
- Tree hierarchy relationships

---

## Validate Action Prompts

### Template Usage Validation

**Verify templates were loaded:**
- Are TWO files created from templates:
  - `[solution-folder]/docs/stories/map/[product-name]-story-map.md`
  - `[solution-folder]/docs/stories/increments/[product-name]-story-map-increments.md`
- Do files follow template structure (headings, sections, legend)?
- Are all placeholders filled (no {placeholder} text remaining)?

### Structure Validation
- Does `[solution-folder]/docs/stories/increments/` folder exist?
- Is the 🎯 Epic → 📂 Sub-Epic → ⚙️ Feature → 📝 Story hierarchy present?
- Are tree characters (│ ├─ └─) used correctly?
- Is the Legend at the top of both files?
- Are NO epic/feature documents created (those are created in Discovery/Exploration)?
- Are NO epic/feature folders created (those are created by `/story-arrange`)?

### Content Quality
- Are user AND system activities both present?
- Is business language used (verb/noun, not tasks)?
- Are ALL levels using [Verb] [Noun] *[optional clarifier]* format (including Sub-Epics)?
- Are stories action-oriented (not capabilities or implementation)?
- Are emojis used correctly (🎯 📂 ⚙️ 📝)?
- Are NO "Epic:", "Feature:", "Story:" prefixes anywhere (just emoji + name)?

### Sizing
- Are stories sized in 3-12d range (where detailed)?
- Are hierarchy levels within 7±2 thresholds?
  - Epics: 4-9 features (use Sub-Epics if > 9)
  - Features: 4-9 stories (split if > 9)
  - Stories: 2-9 AC (split if > 9)

### Scope and Counting
- Are only 10-20% of stories fully identified?
- Are story counts (~X stories) used for unexplored areas?
- Are areas marked as IDENTIFIED vs (~X stories)?
- When showing example features within epic/sub-epic, is remaining count displayed as "└─ ⚙️ ~X more features"?
- When showing example stories within feature, is remaining count displayed as "└─ 📝 ~X more stories"?

### Increments
- Are potential increments organized in `increments/[product-name]-story-map-increments.md`?
- Are increments using NOW/NEXT/LATER priorities?
- Does `docs/stories/increments/` folder exist (contains story-map-increments.md, individual increment docs added in Discovery)?

---

## Common Issues to Check

### Anti-Patterns
- Stories that are tasks (implement, develop, configure, build, set up)
- Stories without system activities (only user activities)
- Over-identification during shaping (> 20% identified)
- Missing story counts for unexplored areas
- Missing "~X more features" line when showing example features within epic/sub-epic
- Missing "~X more stories" line when showing example stories within feature
- Using "MVI" instead of "Value Increment"
- Increments using High/Medium/Low instead of NOW/NEXT/LATER
- Using "Epic:", "Feature:", "Story:" prefixes anywhere
- Sub-Epics not using verb/noun format
- Missing tree characters or emojis
- Epics with > 9 features (should use Sub-Epics 📂)
- Features with > 9 stories (should split)
- Creating epic/feature documents during Shape (should be created in Discovery/Exploration)

### Missing Elements
- Missing `[inferred-location]/docs/stories/map/` folder structure
- Missing `[inferred-location]/docs/stories/increments/` folder
- Missing `[product-name]-story-map.md` file in map/
- Missing `[product-name]-story-map-increments.md` file in increments/
- No story counting for unexplored areas
- Missing user OR system activities
- Missing Legend at top
- Missing tree characters (│ ├─ └─)
- Missing emojis (🎯 📂 ⚙️ 📝)

Note: Epic/feature folder structure (`epic-[name]/feature-[name]/`) is NOT created during Shape - it's created by `/story-arrange` command

---

## Notes
- Prompts ensure all context is gathered before generation
- Validation prompts ensure quality and completeness
- Common issues help identify and prevent anti-patterns

