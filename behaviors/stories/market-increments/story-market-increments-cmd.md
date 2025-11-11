### Command: `/story-market-increments`

**[Purpose]:** Identify marketable increments of value by analyzing story map, prioritizing increments, and performing relative sizing at initiative/increment level.

**[Rule]:**
* `/stories-rule` — Story writing practices:
  - Section 0: Universal Principles (Action-oriented, INVEST)
  - Section 0.5: All Phases Principles (Epic/Feature/Story Hierarchy)
  - Section 1: Story Shaping Principles (Marketable Increments, Relative Sizing)

**Runner:**
* CLI: `python behaviors/stories/stories_runner.py generate-market-increments [content-file]` — Generate increment identification
* CLI: `python behaviors/stories/stories_runner.py validate-market-increments [content-file]` — Validate increments follow principles
* CLI: `python behaviors/stories/stories_runner.py execute-market-increments [content-file]` — Execute workflow (generate if first call, validate if second call)

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/story-market-increments` and generate has not been called for this command
OR
1. **User** explicitly invokes command via `/story-market-increments-generate`

2. **AI Agent** checks prompting questions before proceeding:
   - Is there an existing story map shell to work with?
   - What are the business priorities or strategic goals?
   - What are the market constraints or deadlines?
   - Are there any dependencies between increments?

3. **AI Agent** references rule files to understand how to identify increments:
   - `/stories-rule.mdc` Section 1.5 for Marketable Increments principles
   - `/stories-rule.mdc` Section 1.6 for Relative Sizing principles

4. **Runner** (`StoryMarketIncrementsCommand.generate()`) generates instructions for AI agent:
   - Request marketable increments of value identification
   - Request increments placement around the story map
   - Request increment prioritization based on business priorities
   - Request relative sizing at initiative or increment level
   - Request comparison against previous similar work

5. **AI Agent** identifies and documents marketable increments

6. **AI Agent** presents generation results to user:
   - Marketable increments identified
   - Increments placed around story map
   - Increments prioritized by business value
   - Relative sizing performed
   - Next steps (review content, proceed to validation)

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews identified increments and edits content:
   - Verify increments are marketable (deliver value)
   - Check increment placement on story map
   - Verify prioritization aligns with business priorities
   - Check relative sizing approach
   - Edit content as needed

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation (implicit when calling `/story-market-increments` again, or explicit `/story-market-increments-validate`)

2. **AI Agent** references rule files to validate increments:
   - `/stories-rule.mdc` Section 1.5 for Marketable Increments validation
   - `/stories-rule.mdc` Section 1.6 for Relative Sizing validation

3. **Runner** (`CodeAugmentedStoryMarketIncrementsCommand.validate()`) validates increments:
   - Validates marketable increment identification
   - Checks increment prioritization
   - Validates relative sizing approach
   - Scans content using StoryMarketIncrementsHeuristic
   - Enhances violations with principle info and code snippets

4. **Runner** displays validation report with violations (if any)

5. **AI Agent** presents validation results:
   - Validation status (pass/fail)
   - List of violations (if any) with line numbers and messages
   - Recommendations for fixing violations
   - Next steps (fix violations and re-validate, or proceed to Discovery stage)

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** fixes violations (if any) and re-invokes validation
2. **User** proceeds to Discovery stage (`/story-discovery`) when validation passes

