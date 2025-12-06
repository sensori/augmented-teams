---
execution:
  registry_key: code-agent-feature
  python_import: behaviors.code-agent.code_agent_runner.FeatureCommand
  cli_runner: behaviors/code-agent/code-agent_runner.py
  actions:
    generate:
      cli: generate-feature
      method: generate
    validate:
      cli: validate-feature
      method: validate
    correct:
      cli: correct-feature
      method: correct
  working_directory: workspace_root
---

### Command: `/code-agent-feature`

**[Purpose]:** Generate and validate a new Code Agent feature following the standard 4 actions: Generate → User Feedback → Validate → User Feedback

**[Rule]:**
* `/code-agent-rule` — [Rule] file containing [principle]s regarding what is a valid code-agent-behavior, including the valid content, structure and relationships between all artifacts, including code agent features

**Runner:**
* CLI: `python behaviors/code-agent/code_agent_runner.py execute-feature [feature-name] [location] [feature-purpose]` — Execute full workflow (Generate → User Changes → Validate)
* CLI: `python behaviors/code-agent/code_agent_runner.py generate-feature [feature-name] [location] [feature-purpose]` — Generate only
* CLI: `python behaviors/code-agent/code_agent_runner.py validate-feature [feature-name] [location]` — Validate only
* CLI: `python behaviors/code-agent/code_agent_runner.py correct-feature [feature-name] [location] [feature-purpose] [chat-context]` — Correct feature based on errors and chat context

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/code-agent-feature` and generate has not been called for this command, command CLI invokes generate action
OR
1. **User** explicitly invokes command via `/code-agent-feature-generate`

2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("code-agent-feature", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **AI Agent** references `/code-agent-rule.mdc` to understand how to generate a feature that follows all the [principle]s specified in the [rule-file]
4. **Runner** (`CodeAgentFeatureCommand.generate()`) which generates the feature according to the [principle]s specified in `code-agent-rule.mdc`:
   - Creates feature directory and generates `behavior.json` with required fields
   - Generates runner file (`[feature-name]_runner.py`) using `runner_template.py`
   - Generates `feature-outline.md` using `feature_outline_template.md`
5. **Runner** which displays list of generated files with relative paths
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
2. **AI Agent** determines parameters from user input or context 3. **Runner** (`CodeAgentFeatureCommand.validate()`) which validates if the feature follows the [principle]s specified in `code-agent-rule.mdc`:
   - Scans content using heuristics in runner
   - Checks `behavior.json` has required fields and `feature-outline.md` has [feature-purpose] section
   - Validates file names and locations are correct
   - Returns list of [violation]s, associated [principle]s, [example]s and [suggested-fix]es with line numbers
4. **AI Agent** presents validation results to user: summary of validation status, list of [violation]s to fix (if any), confirmation when validation passes, and next steps (deploy feature, create behaviors, etc.)

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** reviews validation results and fixes [violation]s if needed
2. **User** optionally calls execute, generate, or validate as needed

**ACTION 5: CORRECT**
**Steps:**
1. **User** invokes correction via `/code-agent-feature-correct [feature-name] [location] [feature-purpose] [chat-context]` when feature has validation errors or needs updates based on chat context

2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("code-agent-feature", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **AI Agent** references `/code-agent-rule.mdc` to understand how to correct feature based on:
   - Validation violations (if any) with line numbers and messages
   - Chat context provided by user
   - Code agent principles from rule file

4. **AI Agent** corrects the feature:
   - Fixes validation violations (if any)
   - Applies corrections based on chat context
   - Ensures feature follows code agent principles
   - Updates feature files directly (behavior.json, feature-outline.md, runner file)

5. **AI Agent** presents correction results to user:
   - List of corrections made
   - Updated feature file paths
   - Next steps (re-validate, deploy feature, create behaviors)
