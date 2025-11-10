### Command: `/code-agent-feature`

**[Purpose]:** Generate and validate a new Code Agent feature following the standard 4 actions: Generate → User Feedback → Validate → User Feedback

**[Rule]:**
* `/code-agent-rule` — [Rule] file containing [principle]s regarding what is a valid code-agent-behavior, including the valid content, structure and relationships between all artifacts, including code agent features

**Runner:**
* CLI: `python behaviors/code-agent/code_agent_runner.py execute-feature [feature-name] [location] [feature-purpose]` — Execute full workflow (Generate → User Changes → Validate)
* CLI: `python behaviors/code-agent/code_agent_runner.py generate-feature [feature-name] [location] [feature-purpose]` — Generate only
* CLI: `python behaviors/code-agent/code_agent_runner.py validate-feature [feature-name] [location]` — Validate only

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/code-agent-feature` and generate has not been called for this command, command CLI invokes generate action
OR
1. **User** explicitly invokes command via `/code-agent-feature-generate`

2. **AI Agent** (using `CodeAgentFeatureCommand.generate()`) determines [feature-name], [location], and [feature-purpose] (from user input or context) 
3. **AI Agent** references `/code-agent-rule.mdc` to understand how to generate a feature that follows all the [principle]s specified in the [rule-file]
4. **Runner** (`CodeAgentFeatureCommand.generate()`) generates the feature according to the [principle]s specified in `code-agent-rule.mdc`:
   - Creates feature directory and generates `behavior.json` with required fields
   - Generates runner file (`[feature-name]_runner.py`) using `runner_template.py`
   - Generates `feature-outline.md` using `feature_outline_template.md`
5. **Runner** displays list of generated files with relative paths
6. **AI Agent** presents generation results to user:
   - List of files created with paths
   - [feature-name] and [location]
   - Next step after human feedback (regenerate, proceed to validation)

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews generated files and adds/edits content:
   - Edits [feature-name], moves [location], and/or edits [feature-purpose] in `feature-outline.md` 
   - Adds implementation logic to runner file if needed
   - Updates `behavior.json` description if needed

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation (implicit when calling `/code-agent-feature` again, or explicit `/code-agent-feature-validate`)
2. **AI Agent** references `/code-agent-rule.mdc` to validate if a feature follows all the [principle]s specified in the [rule-file]
3. **Runner** (`CodeAgentFeatureCommand.validate()`) validates if the feature follows the [principle]s specified in `code-agent-rule.mdc`:
   - Scans content using heuristics in runner
   - Checks `behavior.json` has required fields and `feature-outline.md` has [feature-purpose] section
   - Validates file names and locations are correct
   - Returns list of [violation]s, associated [principle]s, [example]s and [suggested-fix]es with line numbers
4. **AI Agent** presents validation results to user: summary of validation status, list of [violation]s to fix (if any), confirmation when validation passes, and next steps (deploy feature, create behaviors, etc.)

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** reviews validation results and fixes [violation]s if needed
2. **User** optionally calls execute, generate, or validate as needed
