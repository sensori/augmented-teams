### Command: `/code-agent-rule`

**[Purpose]:** Generate and validate a new rule within a feature following the standard 4 actions: Generate → User Feedback → Validate → User Feedback

**[Rule]:**
* Rule file containing [principle]s regarding valid behavior patterns, including the valid content, structure and relationships between all artifacts, including rules

**Runner:**
* CLI: `python behaviors/code-agent/code_agent_runner.py execute-rule [feature-name] [rule-name] [rule-purpose] [rule-type] [parent-rule-name]` — Execute full workflow (Generate → User Changes → Validate)
* CLI: `python behaviors/code-agent/code_agent_runner.py generate-rule [feature-name] [rule-name] [rule-purpose] [rule-type] [parent-rule-name]` — Generate only
* CLI: `python behaviors/code-agent/code_agent_runner.py validate-rule [feature-name] [rule-name]` — Validate only
* CLI: `python behaviors/code-agent/code_agent_runner.py plan-rule [feature-name] [rule-name] [rule-purpose] [rule-type] [parent-rule-name]` — Generate implementation plan (optional)
* CLI: `python behaviors/code-agent/code_agent_runner.py correct-rule [feature-name] [rule-name] [rule-purpose] [rule-type] [parent-rule-name] [chat-context]` — Correct rule based on errors and chat context

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/code-agent-rule` and generate has not been called for this rule, command CLI invokes generate action
OR
1. **User** explicitly invokes command via `/code-agent-rule-generate`

2. **AI Agent** (using `CodeAugmentedRuleCommand.generate()`) determines [feature-name], [rule-name], [rule-purpose], [rule-type], and [parent-rule-name] (from user input or context) 
3. **AI Agent** references rule file to understand how to generate a rule that follows all the [principle]s specified in the [rule-file]
4. **Runner** (`RuleCommand.generate()`) generates the rule according to the [principle]s specified in the [rule-file], specifically:
   - Creates rules directory at `behaviors/[feature-name]/rules/` if needed
   - Generates `[rule-name]-rule.mdc` using rule template with placeholders filled
   - Generates rule class file if custom logic is needed (extends BaseRule, SpecializingRule, or SpecializedRule)
5. **Runner** displays list of generated files with relative paths
6. **AI Agent** presents generation results to user:
   - List of files created with paths
   - [feature-name] and [rule-name]
   - Next step after human feedback (regenerate, proceed to validation)

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews generated files and adds/edits content:
   - Edits [rule-name], [rule-purpose], and/or [rule-type] in `[rule-name]-rule.mdc` 
   - Updates rule class implementation if needed
   - Updates rule references if needed

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation (implicit when calling `/code-agent-rule` again, or explicit `/code-agent-rule-validate`)
2. **AI Agent** references rule file to validate if a rule follows all the [principle]s specified in the [rule-file]
3. **Runner** (`CodeAugmentedRuleCommand.validate()`) validates if the rule follows the [principle]s specified in the rule file:
   - Scans content using heuristics in runner
   - Checks `[rule-name]-rule.mdc` has required structure (frontmatter, principles, examples)
   - Validates rules directory exists and contains required files
   - Validates rule instances can load examples
   - Returns list of [violation]s, associated [principle]s, [example]s and [suggested-fix]es with line numbers
4. **AI Agent** presents validation results to user: summary of validation status, list of [violation]s to fix (if any), confirmation when validation passes, and next steps (implement rule logic, create more rules, etc.)

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** reviews validation results and fixes [violation]s if needed
2. **User** optionally calls execute, generate, or validate as needed

**ACTION 5: CORRECT**
**Steps:**
1. **User** invokes correction via `/code-agent-rule-correct [feature-name] [rule-name] [rule-purpose] [rule-type] [parent-rule-name] [chat-context]` when rule has validation errors or needs updates based on chat context

2. **AI Agent** reads rule file and validation errors (if any), plus chat context provided by user

3. **AI Agent** references rule file to understand how to correct rule based on:
   - Validation violations (if any) with line numbers and messages
   - Chat context provided by user
   - Code agent principles from rule file

4. **AI Agent** corrects the rule:
   - Fixes validation violations (if any)
   - Applies corrections based on chat context
   - Ensures rule follows code agent principles (structure, principles, examples)
   - Updates rule file directly

5. **AI Agent** presents correction results to user:
   - List of corrections made
   - Updated rule file path
   - Next steps (re-validate, implement rule logic, create more rules)

