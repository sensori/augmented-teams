### Command: `/[command-name]`

**[Purpose]:** [command-purpose]

**[Rule]:**
* `/[rule-name]` — [Rule] file containing [principle]s regarding [rule-description], including [rule-scope]

**Runner:**
* CLI: `python [runner-path] [execute-action] [command-parameters]` — Execute full workflow ([action-list])
* CLI: `python [runner-path] [generate-action] [command-parameters]` — Generate only
* CLI: `python [runner-path] [validate-action] [command-parameters]` — Validate only

**Action 1: GENERATE**
**Steps:**
1. **User** invokes command via `/[command-name]` and generate has not been called for this command, command cli invokes generate action
OR
1. **User** explicitly invokes command via `/[command-name]-generate`

2. **AI Agent** (using `[CommandClass].generate()`) determines the [command-parameters] [parameter-list] (from user input or context) 
3. **AI Agent** references `/[rule-name].mdc` to understand how to generate [target-entity] that follows all the [principle]s specified in the [rule-file]
4. **Runner** (`[CommandClass].generate()`) generates the [target-entity] according to the [principle]s specified in the [rule-file] `[rule-file-name]`, specifically the following [command-generation-logic]
[command-generation-logic] include
   *- [generation-step-1]*
   *- [generation-step-2]*
   *- [generation-step-3]*
5. **Runner** displays list of generated files with relative paths
6. **AI Agent** presents [generation-results] to user:
[generation-results] include
   *- [result-item-1]*
   *- [result-item-2]*
   *- [result-item-3]*

**Action 2: GENERATE FEEDBACK**
**Steps:**
1. **User** reviews generated files and adds/edits content:
   - [user-edit-action-1]
   - [user-edit-action-2]
   - [user-edit-action-3]

**ACTION 3: VALIDATE**
**Steps:**
1. **User** invokes validation (implicit when calling `/[command-name]` again, or explicit `/[command-name]-validate`)
3. **AI Agent** references `/[rule-name].mdc` to validate if [target-entity] follows all the [principle]s specified in the [rule-file]
4. **Runner** (`[CommandClass].validate()`) validates if the [target-entity] follows the [principle]s specified in the [rule-file] `[rule-file-name]`
    - scans content using [command-validation-heuristics] in runner
        *- [validation-check-1]*
        *- [validation-check-2]*
        *- [validation-check-3]*
5. **AI Agent** presents validation results to user: summary of validation status, list of [violation]s to fix (if any), confirmation when validation passes, and next steps ([next-step-list])

**ACTION 4: VALIDATE FEEDBACK**
**Steps:**
1. **User** reviews validation results and fixes [violation]s if needed
2. **User** optionally calls execute, generate, or validate as needed




