# Answer Questions Before Creating

## Rule

When the user asks a question (not a command), ANSWER the question FIRST. Do NOT automatically proceed to create, modify, or implement anything. ASK the user if they want you to proceed before making changes.

## Pattern Recognition

### User Asks Question
If user message:
- Asks "how does X work?"
- Asks "what is Y?"
- Asks "why does Z happen?"
- Asks "can you explain...?"
- Asks "is there a way to...?"
- Asks for your opinion or recommendation
- Contains question mark and seeks information

### Response Pattern
1. **ANSWER the question** - Provide clear, complete answer
2. **ASK before proceeding** - "Would you like me to implement this?" or "Should I proceed with this change?"
3. **WAIT for user confirmation** - Don't assume user wants implementation

## Examples

### ✅ CORRECT: Answer, then ask

**User:** "Is there a reason why the action execute template method couldn't handle the parts of the code that every action executes?"

**Assistant:** 
"You're absolutely right! Steps 1 and 2 are completely generic and repeated in EVERY action. This violates DRY principle. 

We could refactor this so the execute_action template method handles:
1. Setting the state machine
2. Saving workflow state
3. Instantiating the action
4. Executing and wrapping in BotResult

This would reduce each action method from ~20 lines to ~2 lines.

**Would you like me to refactor the code to use this template method pattern?**"

---

### ❌ WRONG: Immediately create without asking

**User:** "Is there a reason why the action execute template method couldn't handle the parts of the code that every action executes?"

**Assistant:** 
"You're right! Let me refactor..."
[Immediately starts modifying code without asking]

---

### ✅ CORRECT: Explain, then confirm

**User:** "Can we add a rule to not try to write code that supports legacy structure and new?"

**Assistant:**
"Yes, absolutely! When refactoring, you should:
- Replace old pattern completely with new pattern
- Delete old code, don't support both
- Update all call sites at once
- Fix tests to match new implementation

This prevents technical debt from compatibility layers.

**Should I create this as a clean code rule in the clean_code_bot/rules folder?**"

---

### ❌ WRONG: Create without confirming

**User:** "Can we add a rule to not try to write code that supports legacy structure and new?"

**Assistant:**
[Immediately creates the rule file without asking]

---

## Exceptions

### User Gives Direct Command
If user clearly commands (not asks):
- "fix this"
- "implement X"
- "refactor Y" 
- "proceed"
- "do it"
- "create Z"

**Then:** Proceed without asking (user already commanded)

### User Asks Informational Question
If user just wants information:
- "what does this do?"
- "how does X work?"
- "explain Y"

**Then:** Answer only, don't offer to implement anything

## Key Point

**The rule is simple:** 
- Question → Answer → Ask → Wait
- Command → Execute

Don't blur the line between answering and implementing. Make the user's intent explicit before proceeding with changes.






























