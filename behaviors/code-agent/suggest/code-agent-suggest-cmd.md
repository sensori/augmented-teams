### Command: `behavior-suggest-cmd.md`

**Purpose:** When doing repetitive tasks, suggest creating new behaviors to capture patterns. Help users decide if suggestions belong in an existing behavior-feature, a new behavior-feature, or the current feature being worked on.

**Usage:**
* `\behavior-suggest` — Analyze current session for repetitive patterns and suggest new behaviors

**Rule:**
* `\behavior-suggest-rule` — Rule that triggers behavior suggestions when repetitive patterns are detected

**Steps:**
1. The AI agent analyzes current session/conversation for repetitive patterns
2. The AI agent identifies common tasks, code structures, or operations being repeated
3. The AI agent generates suggestion with context about the repetitive pattern
4. The AI agent presents suggestion to user in natural language
5. The user provides confirmation or rejection
6. The AI agent asks user where behavior should be placed (existing behavior-feature, new behavior-feature, or current feature)
7. After user confirmation, the AI agent uses `\behavior-structure create` to scaffold the new behavior
