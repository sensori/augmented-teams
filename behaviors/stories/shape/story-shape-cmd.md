### Command: `/story-shape`

**[Purpose]:** Create story map shell with epic/feature/story hierarchy. Generates TWO artifacts:
- `[product-name]-story-map.md` - Hierarchical tree view (Epic > Sub-Epic > Feature > Story)
- `[product-name]-story-map-increments.md` - Increment organized view

This command shapes stories by establishing structure, focusing on user AND system activities, using business language, counting unexplored areas (~X stories). Only 10-20% of stories are identified during Shape. Individual increment documents and epic/feature documents are created later during Discovery/Exploration.

**[Rule]:**
* `/stories-rule` — Story writing practices:
  - Section 0: Universal Principles (Action-oriented, INVEST)
  - Section 0.5: All Phases Principles (Epic/Feature/Story Hierarchy)
  - Section 1: Story Shaping Principles (User AND System Activities, Business Language, Sizing)

**Runner:**
* CLI: `python behaviors/stories/stories_runner.py generate-shape [content-file]` — Generate story map structure
* CLI: `python behaviors/stories/stories_runner.py validate-shape [content-file]` — Validate story map follows principles
* CLI: `python behaviors/stories/stories_runner.py execute-shape [content-file]` — Execute workflow (generate if first call, validate if second call)

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/story-shape` and generate has not been called for this command
OR
1. **User** explicitly invokes command via `/story-shape-generate`

2. **AI Agent** infers solution folder from current working context and asks only if critical information is missing
   - **CRITICAL LOCATION INFERENCE**:
     - **FROM CONTEXT**: Check recently viewed files, open files, and current directory
     - **SOLUTION FOLDER DETECTION**:
       - If recently viewed files from project subfolder (e.g., `demo/mm3e/`), use that as solution folder
       - If current directory is in project subfolder, use that as solution folder
       - If at workspace root, create new solution folder (e.g., `<product-name>/`)
     - **EXACT STRUCTURE** (ALWAYS use this structure):
       ```
       <solution-folder>/
       └── docs/
           └── stories/
               ├── map/
               │   ├── [product-name]-story-map.md
               │   └── 🎯 Epic folders/ (created by /story-arrange)
               └── increments/
                   └── [product-name]-story-map-increments.md
       ```
     - **EXAMPLES**:
       - Context: `demo/mm3e/` → Create at `demo/mm3e/docs/stories/map/` and `demo/mm3e/docs/stories/increments/`
       - Context: workspace root → Create at `<product-name>/docs/stories/map/` and `<product-name>/docs/stories/increments/`

3. **AI Agent** references rule files to understand how to create story maps:
   - `/stories-rule.mdc` Section 0 for universal principles
   - `/stories-rule.mdc` Section 0.5 for hierarchy structure
   - `/stories-rule.mdc` Section 1 for Story Shaping principles
   - `/stories-rule.mdc` Section 1.7.1 for End-to-End Value Increments (CRITICAL for increment planning)

4. **Runner** (`StoryShapeCommand.generate()`) generates instructions for AI agent:
   - **Location Structure** (MANDATORY):
     - Story map file: `<solution-folder>/docs/stories/map/[product-name]-story-map.md`
     - Increments file: `<solution-folder>/docs/stories/increments/[product-name]-story-map-increments.md`
     - Epic folders: `<solution-folder>/docs/stories/map/🎯 Epic Name/` (created by `/story-arrange`)
   - Create TWO artifact files with meaningful names based on product:
     1. `<solution-folder>/docs/stories/map/[product-name]-story-map.md` - Hierarchical tree view
     2. `<solution-folder>/docs/stories/increments/[product-name]-story-map-increments.md` - Value Increment organized view
   - **Format**: Use tree structure with emojis for visual hierarchy:
     - 🎯 Epic - High-level capability
     - 📂 Sub-Epic - Sub-capability (when epic has > 9 features)
     - ⚙️ Feature - Cohesive functionality  
     - 📝 Story - Small increment
     - Tree characters: │ ├─ └─ for hierarchy
     - Legend at top of each file
   - Create `<solution-folder>/docs/stories/map/` and `<solution-folder>/docs/stories/increments/` folders
   - **NO epic/feature folder creation during Shape** - Epic/feature folders created later by `/story-arrange` inside `map/`
   - Request epic/feature/story hierarchy structure (Epic > Sub-Epic > Feature > Story)
   - **ALL levels use [Verb] [Noun] *[optional clarifier]* format** (including Sub-Epics)
   - Focus on user AND system activities (not tasks)
   - Require business language (verb/noun, specific and precise)
   - Only identify 10-20% of stories (critical/unique/architecturally significant)
   - Use story counting (~X stories) at feature level
   - When showing example stories (2-3), add final line "└─ 📝 ~X more stories" showing remaining count
   - Identify marketable value increments
   - **CRITICAL: Design increments as VERTICAL SLICES** (end-to-end flows across multiple epics/features, NOT horizontal layers)
   - Each increment MUST deliver complete working flow from start to finish
   - Include PARTIAL features from MULTIPLE epics in each increment
   - Layer increments: simple first (basic user, happy path), then add complexity (more users, edge cases)
   - Use "Value Increment" (not "MVI") with NOW/NEXT/LATER priorities
   - Include relative sizing notes for increments
   - Require fine-grained balanced with testable/valuable
   - **NO "Epic:", "Feature:", "Story:" prefixes** - just emoji and name
   - **NO story estimates during Shape** (added in Discovery phase)
   - **NO discovery status during Shape** (added in Discovery phase)
   - **NO epic/feature docs during Shape** (created in Discovery/Exploration phase)
   - **SOURCE TRACKING**: Add "Source Material" section at bottom with:
     - Primary source document/content used
     - Specific sections/pages referenced
     - Context note for Discovery phase to reference same source

5. **AI Agent** creates story map content following the instructions
   - **ADD SOURCE TRACKING** at bottom of BOTH artifacts:
     ```markdown
     ---
     ## Source Material
     
     **Primary Source**: [Document/Content used to generate this story map]
     - Location: [path or description]
     - Sections Referenced: [specific pages, chapters, or sections used]
     - Date Generated: [timestamp]
     
     **Context for Discovery**: When proceeding to Discovery phase, reference the same source material and sections to elaborate stories.
     ```

6. **AI Agent** presents generation results to user:
   - **Location**: `<solution-folder>/docs/stories/`
   - TWO files created:
     - `<solution-folder>/docs/stories/map/[product-name]-story-map.md`
     - `<solution-folder>/docs/stories/increments/[product-name]-story-map-increments.md`
   - Folders created:
     - `<solution-folder>/docs/stories/map/` (will contain story map file and epic folders after `/story-arrange`)
     - `<solution-folder>/docs/stories/increments/` (contains increments.md, individual increment docs added in Discovery)
   - Epic/Feature/Story hierarchy established in documents
   - User and system activities identified
   - Business language used
   - 10-20% stories identified, rest as counts
   - Potential increments noted informally
   - NO estimates or status included (added in Discovery phase)
   - NO individual increment documents (created in Discovery)
   - NO epic/feature documents (created in Discovery/Exploration)
   - NO epic/feature folder structure yet (created by `/story-arrange` inside `map/`)
   - NO story stub files yet (created by `/story-specification` when writing scenarios)
   - Next steps (review content, proceed to `/story-arrange` then `/story-discovery`)

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews generated artifacts and edits content:
   - Verify files exist:
     - `<solution-folder>/docs/stories/map/[product-name]-story-map.md`
     - `<solution-folder>/docs/stories/increments/[product-name]-story-map-increments.md`
   - Verify folder structure:
     - `<solution-folder>/docs/stories/map/` exists (epic folders added by `/story-arrange`)
     - `<solution-folder>/docs/stories/increments/` exists
   - Verify epic/feature/story hierarchy structure in documents (including Sub-Epic if present)
   - Check user AND system activities are present
   - Verify business language usage (verb/noun patterns)
   - Check 10-20% stories identified, rest as story counts
   - Verify NO "Epic:", "Feature:", "Story:" prefixes (just emoji + name)
   - Verify NO estimates or discovery status included (added later)
   - Verify NO individual increment documents yet (created in Discovery)
   - Verify NO epic/feature documents yet (created in Discovery/Exploration)
   - Verify NO epic/feature folders exist yet (created by `/story-arrange` inside `map/`)
   - Edit content as needed

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation (implicit when calling `/story-shape` again, or explicit `/story-shape-validate`)

2. **AI Agent** references rule files to validate story map:
   - `/stories-rule.mdc` Section 1 for Story Shaping validation criteria
   - `/stories-rule.mdc` Section 1.7.1 for End-to-End Value Increments validation (CRITICAL)

3. **Runner** (`CodeAugmentedStoryShapeCommand.validate()`) validates story map:
   - Checks files exist:
     - `<solution-folder>/docs/stories/map/[product-name]-story-map.md`
     - `<solution-folder>/docs/stories/increments/[product-name]-story-map-increments.md`
   - Validates folder structure:
     - `<solution-folder>/docs/stories/map/` exists (should NOT contain epic folders yet)
     - `<solution-folder>/docs/stories/increments/` exists
   - Checks epic/feature/story hierarchy structure in documents (including Sub-Epic)
   - Validates user/system focus (not tasks)
   - Checks business language usage
   - Validates story counting patterns (~X stories notation)
   - Validates NO "Epic:", "Feature:", "Story:" prefixes (just emoji + name)
   - Validates NO individual increment documents present (created in Discovery)
   - Validates NO epic/feature documents present (created in Discovery/Exploration)
   - Validates NO epic/feature folders present in `map/` (created by `/story-arrange`)
   - Validates scope extrapolation
   - Scans content using StoryShapeHeuristic and MarketIncrementHeuristic
   - Enhances violations with principle info and code snippets

4. **Runner** displays validation report with violations (if any)

5. **AI Agent** presents validation results:
   - Validation status (pass/fail)
   - List of violations (if any) with line numbers and messages
   - Recommendations for fixing violations
   - Next steps (fix violations and re-validate, or proceed to `/story-arrange` then `/story-discovery`)

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** fixes violations (if any) and re-invokes validation
2. **User** proceeds to `/story-arrange` command to create folder structure
3. **User** proceeds to `/story-discovery` command when validation passes

