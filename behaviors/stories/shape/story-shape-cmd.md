### Command: `/story-shape`

**[Purpose]:** Create story map shell with epic/feature/story hierarchy and elaborate/extrapolate scope. This command helps shape stories by establishing structure, focusing on user AND system activities, using business language, and sizing stories appropriately (3-12 day range).

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

2. **AI Agent** checks prompting questions before proceeding:
   - What is the product or feature vision?
   - Who are the target users or stakeholders?
   - What are the main user goals or outcomes?
   - What is the scope boundary (what's in/out)?

3. **AI Agent** references rule files to understand how to create story maps:
   - `/stories-rule.mdc` Section 0 for universal principles
   - `/stories-rule.mdc` Section 0.5 for hierarchy structure
   - `/stories-rule.mdc` Section 1 for Story Shaping principles

4. **Runner** (`StoryShapeCommand.generate()`) generates instructions for AI agent:
   - Request epic/feature/story hierarchy structure creation
   - Focus on user AND system activities (not tasks)
   - Require business language (verb/noun, specific and precise)
   - Request shell elaboration to understand full scope
   - Request epics/features/stories extrapolation for increments
   - Require fine-grained balanced with testable/valuable
   - Require stories sized appropriately in 3-12 day range

5. **AI Agent** creates story map content following the instructions

6. **AI Agent** presents generation results to user:
   - Story map with epic/feature/story hierarchy
   - User and system activities identified
   - Business language used
   - Stories sized appropriately
   - Next steps (review content, proceed to validation)

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews generated story map and edits content:
   - Verify epic/feature/story hierarchy structure
   - Check user AND system activities are present
   - Verify business language usage (verb/noun patterns)
   - Check story sizing (3-12 day range where applicable)
   - Edit content as needed

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation (implicit when calling `/story-shape` again, or explicit `/story-shape-validate`)

2. **AI Agent** references rule files to validate story map:
   - `/stories-rule.mdc` Section 1 for Story Shaping validation criteria

3. **Runner** (`CodeAugmentedStoryShapeCommand.validate()`) validates story map:
   - Checks epic/feature/story hierarchy structure
   - Validates user/system focus (not tasks)
   - Checks business language usage
   - Validates scope extrapolation and story sizing
   - Scans content using StoryShapeHeuristic
   - Enhances violations with principle info and code snippets

4. **Runner** displays validation report with violations (if any)

5. **AI Agent** presents validation results:
   - Validation status (pass/fail)
   - List of violations (if any) with line numbers and messages
   - Recommendations for fixing violations
   - Next steps (fix violations and re-validate, or proceed to next command)

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** fixes violations (if any) and re-invokes validation
2. **User** proceeds to `/story-market-increments` command when validation passes

