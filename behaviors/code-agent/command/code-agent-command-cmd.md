---
execution:
  registry_key: code-agent-command
  python_import: behaviors.code-agent.code_agent_runner.CommandCommand
  cli_runner: behaviors/code-agent/code-agent_runner.py
  actions:
    generate:
      cli: generate-command
      method: generate
    validate:
      cli: validate-command
      method: validate
    correct:
      cli: correct-command
      method: correct
  working_directory: workspace_root
---

### Command: `/code-agent-command`

**[Purpose]:** Generate and validate a new command within a feature following the standard 4 actions: Generate → User Feedback → Validate → User Feedback

**[Rule]:**
* `/code-agent-rule` — [Rule] file containing [principle]s regarding what is a valid code-agent-behavior, including the valid content, structure and relationships between all artifacts, including code agent commands

**Runner:**
* CLI: `python behaviors/code-agent/code_agent_runner.py execute-command [feature-name] [command-name] [command-purpose] [target-entity]` — Execute full workflow (Generate → User Changes → Validate)
* CLI: `python behaviors/code-agent/code_agent_runner.py generate-command [feature-name] [command-name] [command-purpose] [target-entity]` — Generate only
* CLI: `python behaviors/code-agent/code_agent_runner.py validate-command [feature-name] [command-name]` — Validate only
* CLI: `python behaviors/code-agent/code_agent_runner.py plan-command [feature-name] [command-name] [command-purpose] [target-entity]` — Generate implementation plan (optional)
* CLI: `python behaviors/code-agent/code_agent_runner.py correct-command [feature-name] [command-name] [command-purpose] [target-entity] [chat-context]` — Correct command based on errors and chat context

**Action 0: PLAN** (Optional - only if user requests)
**Steps:**
1. **User** optionally invokes plan via `/code-agent-command-plan` or `plan-command` CLI
2. **Runner** (`CommandCommand.plan()`) loads `command_plan_template.md` and fills with [feature-name], [command-name], [command-purpose], [target-entity], and other template parameters
3. **Runner** which returns filled-out plan for user review
4. **AI Agent** presents plan to user for review before proceeding to generation

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/code-agent-command` and generate has not been called for this command, command CLI invokes generate action
OR
1. **User** explicitly invokes command via `/code-agent-command-generate`

2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("code-agent-command", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **AI Agent** references `/code-agent-rule.mdc` to understand how to generate a command that follows all the [principle]s specified in the [rule-file]
4. **Runner** (`CommandCommand.generate()`) generates the command according to the [principle]s specified in `code-agent-rule.mdc`:
   - Creates command directory at `behaviors/[feature-name]/[command-name]/`
   - Generates `[command-name]-cmd.md` using `command_template.md` with placeholders filled
   - Generates `[command-name]-generate-cmd.md` that delegates to main command's generate action
   - Generates `[command-name]-validate-cmd.md` that delegates to main command's validate action
   - Updates runner file (`[feature-name]_runner.py`) with command class implementation
   - Updates rule file (`[feature-name]-rule.mdc`) with command reference in "Executing Commands" section
5. **Runner** which displays list of generated files with relative paths
6. **AI Agent** presents generation results to user:
   - List of files created with paths
   - [feature-name] and [command-name]
   - Next step after human feedback (regenerate, proceed to validation)

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews generated files and adds/edits content:
   - Edits [command-name], [command-purpose], and/or [target-entity] in `[command-name]-cmd.md` 
   - Updates command class implementation in runner file if needed
   - Updates command reference in rule file if needed

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation (implicit when calling `/code-agent-command` again, or explicit `/code-agent-command-validate`)
2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("code-agent-command", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **Runner** (`CodeAugmentedCommandCommand.validate()`) validates if the command follows the [principle]s specified in `code-agent-rule.mdc`:
   - Scans content using heuristics in runner
   - Checks `[command-name]-cmd.md` has required structure and placeholders filled
   - Validates command directory exists and contains required files
   - Validates runner file has command class added correctly
   - Validates rule file has command reference added to "Executing Commands" section
   - Returns list of [violation]s, associated [principle]s, [example]s and [suggested-fix]es with line numbers
4. **AI Agent** presents validation results to user: summary of validation status, list of [violation]s to fix (if any), confirmation when validation passes, and next steps (implement command logic, create more commands, etc.)

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** reviews validation results and fixes [violation]s if needed
2. **User** optionally calls execute, generate, or validate as needed

**ACTION 5: CORRECT**
**Steps:**
1. **User** invokes correction via `/code-agent-command-correct [feature-name] [command-name] [command-purpose] [target-entity] [chat-context]` when command has validation errors or needs updates based on chat context

2. **AI Agent** uses `behaviors/code-agent/utils/command_executor.py` to execute the command automatically:
   - Calls `execute_command("code-agent-command", "generate", **params)` where params are determined from user input or context
   - The executor automatically parses execution metadata, tries Python import first, falls back to CLI if needed
   - **AI Agent MUST use the executor - DO NOT manually parse CLI commands or run terminal commands**
3. **AI Agent** references `/code-agent-rule.mdc` to understand how to correct command based on:
   - Validation violations (if any) with line numbers and messages
   - Chat context provided by user
   - Code agent principles from rule file

4. **AI Agent** corrects the command:
   - Fixes validation violations (if any)
   - Applies corrections based on chat context
   - Ensures command follows code agent principles
   - Updates command files directly (command-cmd.md, runner file, rule file)

5. **AI Agent** presents correction results to user:
   - List of corrections made
   - Updated command file paths
   - Next steps (re-validate, implement command logic, create more commands)

