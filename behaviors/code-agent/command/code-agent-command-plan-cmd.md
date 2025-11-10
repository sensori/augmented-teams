### Command: `/code-agent-command-plan`

**Purpose:** Generate an implementation plan for a new command. Delegates to main command with explicit plan action.

**Usage:**
* `/code-agent-command-plan [feature-name] [command-name] [command-purpose] [target-entity]` — Generate command plan (AI determines parameters if not provided)

**Steps:**
1. **Code** Execute the plan action in `/code-agent-command`
