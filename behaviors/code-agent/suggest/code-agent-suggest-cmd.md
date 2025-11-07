### Command: `behavior-suggest-cmd.md`

**Purpose:** When doing repetitive tasks, suggest creating new behaviors to capture patterns. Help users decide if suggestions belong in an existing behavior-feature, a new behavior-feature, or the current feature being worked on.

**Usage:**
* `\behavior-suggest` — Analyze current session for repetitive patterns and suggest new behaviors

**Rule:**
* `\behavior-suggest-rule` — Rule that triggers behavior suggestions when repetitive patterns are detected

**Steps:**
1. **AI Agent** analyzes current session/conversation for repetitive patterns
2. **AI Agent** identifies common tasks, code structures, or operations being repeated
3. **AI Agent** generates suggestion with context about the repetitive pattern
4. **AI Agent** presents suggestion to user in natural language
5. **User** provides confirmation or rejection
6. **AI Agent** asks user where behavior should be placed (existing behavior-feature, new behavior-feature, or current feature)
7. **AI Agent** uses `/code-agent-structure create <feature> <behavior-name>` to scaffold the new behavior after user confirmation
8. **AI Agent** suggests running `/code-agent-index` and `/code-agent-structure validate` after creation
