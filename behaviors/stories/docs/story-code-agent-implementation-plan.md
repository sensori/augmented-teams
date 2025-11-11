# Story Code Agent Implementation Plan

## Overview
Build a complete story code agent feature following the code-agent pattern, with rules, commands, runners, templates, and heuristics based on the Story Writing Training PowerPoint content.

## PowerPoint Analysis Summary

### Major Stages Identified (3 stages):

1. **Story Shaping** (formerly "Idea Shaping")
   - Story Shaping in a Nutshell
   - Introduction To Story Mapping
   - Identifying Marketable Increments Of Value

2. **Discovery**
   - Discovery in a Nutshell
   - Refining Marketable Increments of Value on Your Story Map
   - Story Mapping Practices to Encourage & Avoid
   - Planning, Scheduling, & Forecasting

3. **Story Exploration**
   - Story Exploration in a Nutshell
   - Writing Story Acceptance Criteria
   - Refining Your Story Map During Story Exploration
   - Defining System Level Stories
   - Story Specification
   - Story Testing

## DO/DON'T Principles Analysis

**Analysis Source**: Extracted from `behaviors/stories/docs/story-training-content.md` (PowerPoint content)

## AI Agent Analysis: Missing Semantic/Structural Patterns

**Analysis**: As an AI agent, I need more semantic and structural guidance beyond the high-level DO/DON'T principles. The current principles are abstract and don't provide enough concrete patterns for validation and generation.

### What's Missing for AI Agents:

**1. Story Map Structure Patterns**
- **Missing**: Exact format/structure of a story map
- **Need**: 
  - What does an Epic/Feature/Story hierarchy look like structurally?
  - How are increments marked/identified in the map?
  - What's the exact format for representing user vs system activities?
  - How do I detect if a story map has both user AND system activities?

**2. Story Structure Patterns**
- **Missing**: Exact format for individual stories
- **Need**:
  - Required fields: title, acceptance criteria, summary (optional)?
  - Exact format for story titles (verb/noun pattern examples)
  - How to detect if a story is "action-oriented" vs "task-oriented"?
  - Structural indicators of story size (3-12 days)

**3. Acceptance Criteria Format Patterns**
- **Missing**: Exact format specifications
- **Need**:
  - Exact "When...then..." format with examples
  - Variations allowed (e.g., "Given...when...then...")
  - How to detect "behavior form" vs "technical/task-oriented language"
  - Required elements in acceptance criteria

**4. Language Pattern Detection**
- **Missing**: Specific patterns to detect violations
- **Need**:
  - What makes language "business language" vs "technical IT concepts"?
  - Specific patterns for "generic functions, verbs, nouns without context"
  - How to detect "static functional concepts" vs "active behavioral language"
  - Examples of "verb/noun language" that emphasizes "performing an operation on an explicit thing"

**5. Activity Type Detection**
- **Missing**: How to distinguish activity types
- **Need**:
  - How to detect "user activity" vs "system activity" vs "task"?
  - Patterns that indicate "behavior" vs "task" vs "capability"
  - Examples of each type with structural indicators

**6. Size and Scope Indicators**
- **Missing**: Structural indicators of story size
- **Need**:
  - How to detect if a story is "too large" vs "too small"?
  - Indicators of "fine-grained" vs "testable/valuable" balance
  - How to detect "3-12 day effort range" from story content?

**7. Increment Identification Patterns**
- **Missing**: How to identify marketable increments
- **Need**:
  - Structural markers for increments in story maps
  - How to detect if increments are "well-defined"
  - Patterns for increment boundaries

**8. Validation Patterns for Heuristics**
- **Missing**: Specific patterns for code heuristics to detect
- **Need**:
  - Regex patterns or structural checks for each principle
  - Examples of violations that heuristics should catch
  - Clear yes/no criteria for validation

### Recommendation: Add Semantic/Structural Pattern Section

**Add to Rule File**: A new section after principles with semantic/structural patterns:

- **Story Map Structure**: Exact format, hierarchy patterns, increment markers
- **Story Format**: Required fields, title patterns, structural indicators
- **Acceptance Criteria Format**: Exact format with examples, variations
- **Language Patterns**: Specific patterns for business vs technical language
- **Activity Detection**: Patterns to distinguish user/system/task
- **Size Indicators**: Structural indicators of story size
- **Validation Patterns**: Specific patterns for heuristics to detect violations

**Format**: Similar to BDD rule file which has:
- Structural patterns (describe/it format, linking words)
- Semantic patterns (state-oriented vs action-oriented)
- Validation patterns (regex patterns, structural checks)
- Concrete examples (DO/DON'T with code examples)

This will enable:
1. **Better Generation**: AI knows exact structure to generate
2. **Better Validation**: Heuristics have specific patterns to detect
3. **Consistency**: All stories follow same structural patterns
4. **Automation**: Code can validate structure without AI interpretation

## Semantic/Structural Patterns Extracted from PowerPoint

### 1. Story Map Structure Patterns

**Epic/Feature/Story Hierarchy Format:**
```
Epic: [Epic Name]
  Feature: [Feature Name]
    Story: [Story Title]
    Story: [Story Title]
  Feature: [Feature Name]
    Story: [Story Title]
```

**Increment Markers:**
- Increments are typically marked as horizontal slices across features
- Format: `Increment 1: [Increment Name]` or `MVI 1: [Marketable Value Increment Name]`
- Increments span multiple features/stories that deliver value together

**User vs System Activity Indicators:**
- **User Activity Patterns**: 
  - ✅ "User [verb] [noun]" (e.g., "User submits order", "User views dashboard")
  - ✅ "[Actor] [action] [object]" (e.g., "Customer places order", "Admin reviews report")
  - ✅ Starts with user/actor perspective
- **System Activity Patterns** (System Stories - ✅ ACCEPTABLE):
  - ✅ "System [verb] [noun]" (e.g., "System validates payment", "System sends notification")
  - ✅ "[System component/service] [behavioral action]" (e.g., "Payment processor validates payment", "Email service sends confirmation")
  - ✅ Describes observable system behavior in response to user action
  - ✅ Uses behavioral language: "validates", "sends", "processes", "displays", "notifies"
  - ✅ Focuses on what the system does (observable behavior), not how it's implemented
- **Technical Story Patterns** (❌ NOT ACCEPTABLE - System Internals):
  - ❌ "Implement [feature]" (development task)
  - ❌ "Create [component]" (development task)
  - ❌ "Set up [infrastructure]" (technical task)
  - ❌ "Write [code]" (development task)
  - ❌ "Refactor [code]" (development task)
  - ❌ "Optimize [performance]" (low-level technical concern)
  - ❌ "Fix [bug]" (development task)
  - ❌ Describes system internals (how it's built, not what it does)
  - ❌ Focuses on implementation details, not observable behavior

**Detection Patterns:**
- **Has User Activities**: Contains patterns like "User", "Customer", "[Actor] [verb]"
- **Has System Activities** (System Stories): Contains patterns like "System [behavioral verb]", "[Service/Component] [behavioral verb]", describes observable behavior
- **Technical Stories** (System Internals - avoid): Contains development task verbs ("implement", "create", "refactor", "optimize", "fix"), focuses on implementation details
- **Missing System Activities**: Only user activities present, no system behavior described
- **Task-Oriented**: Contains words like "implement", "create", "set up", "write", "develop", "build", "refactor", "optimize", "fix"

**Key Distinction: System Story vs Technical Story:**
- **System Story** (✅): "System validates payment" - describes observable behavior, what system does
- **System Story** (✅): "Payment service processes transaction" - behavioral, observable outcome
- **Technical Story** (❌): "Implement payment validation" - development task, how to build
- **Technical Story** (❌): "Refactor payment service code" - system internals, implementation detail
- **Technical Story** (❌): "Optimize database queries" - low-level technical concern, not behavioral

### 2. Story Structure Patterns

**Story Format (When Story Maps Present):**
```
Title: [Verb/Noun - Action on Explicit Thing]
Acceptance Criteria:
  When [condition], then [outcome]
  When [condition], then [outcome]
```

**Story Format (When Story Maps NOT Present):**
```
As a [User]
I want to [Perform Action]
So that [I Receive Value]

Acceptance Criteria:
  When [condition], then [outcome]
  When [condition], then [outcome]
```

**Required Fields:**
- **Title**: Required (verb/noun pattern)
- **Acceptance Criteria**: Required (behavior form)
- **Summary/Description**: Optional (provides context only)

**Title Patterns (Verb/Noun Language):**
- ✅ **DO**: "[Verb] [Noun]" (e.g., "Submit order", "View dashboard", "Process payment")
- ✅ **DO**: "[Actor] [verb] [object]" (e.g., "Customer places order", "System validates payment")
- ✅ **DO**: Emphasizes performing operation on explicit thing
- ❌ **DON'T**: Generic verbs without context (e.g., "Process", "Handle", "Manage")
- ❌ **DON'T**: Generic nouns without action (e.g., "Order", "Dashboard", "Payment")
- ❌ **DON'T**: Technical function names (e.g., "getOrder()", "validatePayment()", "processTransaction()")

**Action-Oriented vs Task-Oriented Detection:**
- **Action-Oriented** (✅):
  - Describes user/system interaction
  - Uses behavioral language ("submits", "views", "validates", "sends")
  - Focuses on observable behavior
  - Patterns: "[Actor] [action] [object]", "System [verb] [noun]"
- **Task-Oriented** (❌):
  - Describes implementation steps
  - Uses development language ("implement", "create", "build", "set up")
  - Focuses on how to build, not what behavior
  - Patterns: "Implement [feature]", "Create [component]", "Set up [system]"

**Size Indicators (3-12 Day Range):**
- **Too Small** (< 3 days): 
  - Single field/form element
  - Very narrow scope
  - No independent value
- **Appropriate** (3-12 days):
  - Complete user/system interaction flow
  - Delivers measurable value
  - Can be tested independently
- **Too Large** (> 12 days):
  - Multiple user flows
  - Multiple system components
  - Requires multiple stories to deliver value
  - Indicators: Multiple "and" statements, multiple acceptance criteria covering different flows

### 3. Acceptance Criteria Format Patterns

**Standard Format:**
```
When [user/system action or condition]
Then [expected outcome/behavior]
```

**Variations Allowed:**
- `Given [context], When [action], Then [outcome]`
- `When [condition], Then [outcome]`
- `If [condition], Then [outcome]`

**Behavior Form Patterns** (✅):
- ✅ "When user submits order, then system validates payment"
- ✅ "When payment is valid, then system sends confirmation email"
- ✅ "When user views dashboard, then system displays recent orders"
- ✅ Uses behavioral language describing interactions
- ✅ Observable outcomes

**Technical/Task-Oriented Patterns** (❌):
- ❌ "When payment.validate() is called, then return true"
- ❌ "When database query executes, then return results"
- ❌ "When API endpoint is hit, then return JSON"
- ❌ Uses implementation details
- ❌ Focuses on code/technical behavior

**Required Elements:**
- **Condition**: What triggers the behavior (user action, system state, etc.)
- **Outcome**: Observable result or behavior
- **Testability**: Can be verified through testing

**Detection Patterns:**
- **Has Behavior Form**: Contains "When...then..." or "Given...when...then..."
- **Uses Behavioral Language**: Describes user/system interactions, not implementation
- **Testable**: Describes observable outcomes that can be verified
- **Technical Language**: Contains code patterns (function calls, API endpoints, database queries)

### 3.5. Specification Scenarios and Examples Patterns ⚠️ Commands: story-specification-scenarios, story-specification-examples

**Specification Scenarios Structure:**
- **Purpose**: Detailed narrative descriptions of specific interactions between users and the system
- **Format**: Narrative flow describing sequence of events, user actions, and system responses
- **Relationship to Stories**: Scenarios provide detailed context and flow that can be broken down into multiple user stories
- **Relationship to Acceptance Criteria**: Scenarios inform acceptance criteria by providing concrete examples of behavior

**Scenario Format:**
```
Scenario: [Scenario Name]
Given [initial context/state]
When [user/system action]
Then [expected outcome]
And [additional outcome/verification]
```

**Scenario Examples** (✅):
- ✅ "Scenario: User resets password
  Given a user has forgotten their password
  When the user clicks 'Forgot Password' link
  Then the system sends a password reset email
  And the user receives email with reset link
  When the user clicks the reset link
  Then the system displays password reset form
  When the user enters new password
  Then the system updates password and logs user in"

**Story-to-Scenario Relationship:**
- **One Story → Multiple Scenarios**: A single story can have multiple scenarios covering different paths (happy path, edge cases, error cases)
- **Scenario → Acceptance Criteria**: Scenarios inform acceptance criteria by providing concrete examples
- **Scenario → Examples**: Scenarios contain examples (normal or parameterized) that demonstrate the behavior

**Normal Examples vs Parameterized Examples:**

**Normal Examples** (Concrete, Specific):
- **Format**: Specific data points, concrete values
- **Purpose**: Illustrate typical use cases with exact data
- **Structure**: 
  ```
  Example: [Example Name]
  Given [specific context with concrete values]
  When [action with specific inputs]
  Then [expected outcome with specific values]
  ```
- **Example**:
  ```
  Example: Successful login
  Given user email is "john.doe@example.com"
  And password is "password123"
  When user submits login form
  Then system displays dashboard
  And user session is created
  ```

**Parameterized Examples** (Template, Multiple Cases):
- **Format**: Template with variables/parameters that can be tested with multiple data sets
- **Purpose**: Define template for testing various inputs and outputs, allowing multiple test cases from single example
- **Structure**:
  ```
  Example: [Example Name] (Parameterized)
  Given [context with <parameter>]
  When [action with <parameter>]
  Then [outcome with <parameter>]
  
  Examples:
  | parameter1 | parameter2 | expected_outcome |
  | value1     | value2     | result1          |
  | value3     | value4     | result2          |
  ```
- **Example**:
  ```
  Example: Login validation (Parameterized)
  Given user email is "<email>"
  And password is "<password>"
  When user submits login form
  Then system response is "<response>"
  
  Examples:
  | email                  | password    | response              |
  | john@example.com       | correct123  | dashboard displayed   |
  | invalid@example.com    | any         | error: email not found|
  | john@example.com        | wrongpass   | error: invalid password|
  ```

**When to Use Normal vs Parameterized Examples:**
- **Normal Examples** (✅): 
  - Single, specific use case
  - Clear, concrete demonstration
  - Easy to understand for stakeholders
  - Good for happy path and critical paths
- **Parameterized Examples** (✅):
  - Multiple similar cases with different data
  - Testing variations of same behavior
  - Edge cases and boundary conditions
  - Validation rules with multiple inputs
  - When you have 3+ similar examples that differ only in data

**Scenario-to-Example Relationship:**
- **One Scenario → Multiple Examples**: A scenario can have multiple examples (normal and/or parameterized)
- **Examples Demonstrate Scenarios**: Examples provide concrete demonstrations of scenario behavior
- **Normal Examples**: One example = one concrete case
- **Parameterized Examples**: One example = multiple test cases via data table

**Story → Scenario → Example Hierarchy:**
```
Story: User can reset password
  Scenario 1: Successful password reset
    Example 1: Reset with valid email (Normal)
    Example 2: Reset with different email formats (Parameterized)
      | email format           | result           |
      | user@example.com       | email sent       |
      | user.name@example.com  | email sent       |
      | invalid-email         | error displayed  |
  Scenario 2: Password reset link expires
    Example: Link expires after 24 hours (Normal)
  Scenario 3: User enters weak password
    Example: Password validation (Parameterized)
      | password      | result              |
      | weak          | error: too weak     |
      | Strong123!    | password accepted   |
```

**Specification Structure Patterns:**

**Complete Specification Format:**
```
Story: [Story Title]

Acceptance Criteria:
  When [condition], then [outcome]
  When [condition], then [outcome]

Scenarios:
  Scenario 1: [Scenario Name]
    Given [context]
    When [action]
    Then [outcome]
    
    Examples:
      Example 1: [Normal Example Name]
        Given [specific context]
        When [specific action]
        Then [specific outcome]
      
      Example 2: [Parameterized Example Name]
        Given [context with <param>]
        When [action with <param>]
        Then [outcome with <param>]
        
        Examples Table:
        | param1 | param2 | expected |
        | value1 | value2 | result1  |
        | value3 | value4 | result2  |
```

**Detection Patterns:**
- **Has Scenarios**: Contains "Scenario:" markers, Given/When/Then structure
- **Has Normal Examples**: Contains "Example:" with concrete values, no parameter tables
- **Has Parameterized Examples**: Contains "Example:" with `<parameter>` placeholders and Examples table
- **Story-Scenario Link**: Scenarios reference story title or acceptance criteria
- **Scenario-Example Link**: Examples are nested under scenarios

**Validation Patterns:**
- **Scenario Completeness**: Each scenario has Given/When/Then
- **Example Completeness**: Each example has concrete values (normal) or parameter table (parameterized)
- **Parameterized Table Format**: Parameterized examples have Examples table with matching column names
- **Story Coverage**: Stories have scenarios covering happy path, edge cases, error cases

### 4. Language Pattern Detection

**Business Language Patterns** (✅):
- ✅ Domain-specific terms (e.g., "order", "customer", "payment", "inventory")
- ✅ Verb/noun combinations with context (e.g., "place order", "view dashboard", "process payment")
- ✅ Action-oriented language (e.g., "submits", "views", "receives")
- ✅ Plain English that business stakeholders understand

**Technical IT Language Patterns** (❌ - Technical Stories, NOT System Stories):
- ❌ Generic functions without context (e.g., "process", "handle", "manage", "get", "set")
- ❌ Development task verbs (e.g., "implement", "create", "refactor", "optimize", "fix", "build")
- ❌ Code patterns (e.g., "getOrder()", "validatePayment()", "processTransaction()")
- ❌ Implementation details (e.g., "query database", "call API", "update table", "refactor code")
- ❌ System internals (e.g., "optimize performance", "fix memory leak", "update dependencies")
- ❌ Low-level technical concerns that don't describe observable behavior

**System Story Language** (✅ - ACCEPTABLE):
- ✅ "System [behavioral verb] [noun]" (e.g., "System validates payment", "System sends notification")
- ✅ "[Service/Component] [behavioral verb] [noun]" (e.g., "Payment service validates payment", "Email service sends confirmation")
- ✅ Describes observable system behavior in response to user action
- ✅ Uses behavioral language: "validates", "sends", "processes", "displays", "notifies"
- ✅ Focuses on what the system does (observable), not how it's implemented

**Key Distinction:**
- **System Story** (✅): Describes observable system behavior - "System validates payment", "Payment service processes transaction"
- **Technical Story** (❌): Describes development activity or system internals - "Implement payment validation", "Refactor payment service", "Optimize database queries"

**Generic Function/Verb/Noun Patterns** (❌):
- ❌ Single verbs without context: "Process", "Handle", "Manage", "Get", "Set"
- ❌ Single nouns without action: "Order", "Payment", "User"
- ❌ Generic combinations: "Process data", "Handle request", "Manage users"

**Specific Verb/Noun Patterns** (✅):
- ✅ "[Actor] [specific verb] [specific noun]": "Customer places order", "Admin reviews report"
- ✅ "[System] [specific verb] [specific noun]": "System validates payment", "System sends notification"
- ✅ Emphasizes performing operation on explicit thing

**Static Functional Concepts** (❌):
- ❌ "Order Management" (static capability)
- ❌ "Payment Processing" (static function)
- ❌ "User Administration" (static capability)

**Active Behavioral Language** (✅):
- ✅ "Place order" (active behavior)
- ✅ "Validate payment" (active behavior)
- ✅ "Review report" (active behavior)

**Detection Regex Patterns:**
- **Business Language**: Domain terms, verb/noun with context, action-oriented
- **System Story Language** (✅): `\b(System|\w+\s+service|\w+\s+component)\s+\b(validates|sends|processes|displays|notifies|receives|transforms)\b` - Observable behavioral language
- **Technical Story Language** (❌): `\b(implement|create|refactor|optimize|fix|build|develop|set up|write|update|delete)\b` - Development task verbs
- **Technical Implementation** (❌): `\b(API|database|endpoint|query|call|update|table|code|performance|memory|dependencies)\b` - Implementation details
- **Code Patterns** (❌): `\w+\(\)` - Function call syntax
- **Generic Patterns**: `^\s*(Process|Handle|Manage|Get|Set)\s*$`, `^\s*\w+\s*$` (single word)
- **Action-Oriented**: `\b(submit|view|place|receive|validate|send|display)\b\s+\w+`

### 5. Activity Type Detection Patterns

**User Activity Indicators:**
- Starts with user/actor: "User", "Customer", "Admin", "[Role]"
- User actions: "submits", "views", "places", "receives", "selects"
- Pattern: `^(User|Customer|Admin|\w+)\s+\w+`

**System Activity Indicators** (System Stories - ✅ ACCEPTABLE):
- Starts with "System" or system component/service: "System", "Payment service", "Email service", "[Component] service"
- System behavioral actions: "validates", "sends", "processes", "displays", "notifies", "receives", "transforms"
- Describes observable system behavior in response to user action
- Pattern: `^(System|\w+\s+service|\w+\s+component)\s+\b(validates|sends|processes|displays|notifies|receives|transforms)\b`
- Focus: What the system does (observable behavior), not how it's implemented

**Technical Story Indicators** (System Internals - ❌ NOT ACCEPTABLE):
- Development task verbs: "implement", "create", "refactor", "optimize", "fix", "build", "set up", "write", "develop", "update", "delete"
- System internals focus: "optimize performance", "fix memory leak", "update dependencies", "refactor code"
- Implementation details: "query database", "call API", "update table", "write tests"
- Pattern: `\b(implement|create|refactor|optimize|fix|build|set up|write|develop|update|delete)\b`
- Focus: How to build or fix (implementation), not what observable behavior results

**Behavior vs Task Detection:**
- **System Behavior** (System Story - ✅): Describes what the system does (observable behavior in response to user action)
- **Technical Task** (Technical Story - ❌): Describes how to build or fix (implementation steps, system internals)

### 6. Size and Scope Indicators

**Story Size Detection Patterns:**

**Too Small Indicators** (< 3 days):
- Single field/form element focus
- Very narrow scope (e.g., "Change button color")
- No independent value
- Single acceptance criterion covering one small thing

**Appropriate Size Indicators** (3-12 days):
- Complete user/system interaction flow
- Multiple acceptance criteria (2-5 typically)
- Delivers measurable value independently
- Can be tested as complete unit
- Story title describes complete behavior

**Too Large Indicators** (> 12 days):
- Multiple "and" statements in title
- Multiple user flows in one story
- Multiple system components involved
- 6+ acceptance criteria
- Requires multiple stories to deliver value
- Title contains multiple behaviors

**Fine-Grained vs Testable/Valuable Balance:**
- **Too Fine-Grained**: Single element, no value, can't test independently
- **Appropriate**: Small enough for frequent feedback, large enough to be valuable
- **Too Large**: Multiple flows, can't deliver quickly, hard to test

### 7. Increment Identification Patterns

**Increment Markers:**
- Format: `Increment 1: [Name]` or `MVI 1: [Marketable Value Increment Name]`
- Horizontal slices across features
- Groups stories that deliver value together

**Well-Defined Increment Indicators:**
- Clear boundaries (start/end stories identified)
- Delivers measurable value
- Stories are sized appropriately
- Dependencies identified

**Increment Boundary Detection:**
- Stories grouped under increment marker
- Stories span multiple features
- Stories deliver value together
- Can be released independently

### 8. Validation Patterns for Heuristics

**Principle 0.1 (Action-Oriented) - Detection Patterns:**
- ✅ Contains user/system interaction language
- ✅ Uses behavioral verbs (submit, view, validate, send) - describes observable behavior
- ✅ System stories describe observable system behavior (e.g., "System validates payment")
- ❌ Contains development task verbs (implement, create, refactor, optimize, fix, build)
- ❌ Contains system internals (database queries, API calls, code refactoring, performance optimization)
- **Key Distinction**: System stories (✅) describe what system does (observable), technical stories (❌) describe how to build/fix (implementation)

**Principle 1.1 (User AND System Activities) - Detection Patterns:**
- ✅ Contains both user activity patterns AND system activity patterns
- ❌ Only user activities (missing system activities)
- ❌ Only system activities (missing user activities)
- ❌ Contains task patterns (not activities)

**Principle 1.3 (Business Language) - Detection Patterns:**
- ✅ Uses domain-specific terms
- ✅ Verb/noun with context
- ❌ Generic functions (process, handle, manage)
- ❌ Technical IT concepts (API, database, endpoint)
- ❌ Code patterns (function names with parentheses)

**Principle 3.1 (Acceptance Criteria) - Detection Patterns:**
- ✅ Contains "When...then..." or "Given...when...then..."
- ✅ Uses behavioral language
- ✅ Describes observable outcomes
- ❌ Missing acceptance criteria
- ❌ Uses technical/task-oriented language
- ❌ Focuses on implementation details

**Principle 3.5 (Story Format) - Detection Patterns:**
- ✅ Has title (verb/noun pattern)
- ✅ Has acceptance criteria (main focus)
- ✅ Optional summary (provides context)
- ❌ Missing acceptance criteria
- ❌ Summary is main focus (acceptance criteria should be primary)
- ❌ Title doesn't follow verb/noun pattern

### 9. Concrete Examples from PowerPoint

**Story Sizing Examples** (from Slide 1):
- 15D (15 days) - Too large, should be broken down
- 7d (7 days) - Appropriate size
- 5d (5 days) - Appropriate size
- **Pattern**: Most stories should be 3-12 days

**Story Format Example** (from Slide 15):
- Format: "As A <User> I Want To <Perform Action> So That <I Receive Value>"
- **Example**: "As a customer, I want to place an order so that I can purchase items"
- **Note**: With story maps, simple title is sufficient: "Place order"

**Acceptance Criteria Examples** (from Slide 13):
- Behavior form: "When user submits order, then system validates payment and sends confirmation"
- Domain-oriented form: "Order is placed when payment is valid and inventory is available"

**Language Examples:**

**Business Language** (✅):
- ✅ "Customer places order"
- ✅ "System validates payment"
- ✅ "User views dashboard"
- ✅ "Admin reviews report"

**System Story Language** (✅ - ACCEPTABLE):
- ✅ "System validates payment" (observable behavior)
- ✅ "Payment service processes transaction" (behavioral, observable)
- ✅ "Email service sends confirmation" (system behavior in response to user action)

**Technical Story Language** (❌ - NOT ACCEPTABLE):
- ❌ "Process order" (generic, no context)
- ❌ "Handle payment" (generic, no context)
- ❌ "getOrder()" (code pattern, implementation detail)
- ❌ "Query database for orders" (implementation detail, system internals)
- ❌ "Implement payment validation" (development task)
- ❌ "Refactor payment service" (system internals, implementation)
- ❌ "Optimize database queries" (low-level technical concern)

**Activity Examples:**

**User Activity** (✅):
- ✅ "User submits order"
- ✅ "Customer views products"
- ✅ "Admin reviews reports"

**System Activity** (System Story - ✅ ACCEPTABLE):
- ✅ "System validates payment" (observable behavior)
- ✅ "System sends confirmation email" (observable behavior)
- ✅ "Payment service processes transaction" (behavioral, observable)
- ✅ "Email service sends notification" (system behavior in response to user action)

**Technical Story** (❌ - NOT ACCEPTABLE - System Internals):
- ❌ "Implement order submission" (development task)
- ❌ "Create payment validation" (development task)
- ❌ "Set up email service" (infrastructure task)
- ❌ "Refactor payment service code" (system internals)
- ❌ "Optimize database performance" (low-level technical concern)
- ❌ "Fix memory leak in payment service" (system internals, bug fix)

### Section 0: Universal Principles ⚠️ Universal

**Principle 0.1: Stories Are Action-Oriented and Describe Interactions**
- **Source**: Slides 12, 14, 15
- **[DO]** (Agent-Relevant):
  - Focus stories on user interactions and how the system behaves as observed by users
  - Describe interactions between users and systems
  - Write stories so they can be tested
  - Ensure stories can be developed and tested in a matter of days
  - Make stories action-oriented statements of user and system behavior
  - Use behavioral language: "submits", "views", "validates", "sends", "displays"
  - Describe observable behavior: "User submits order", "System validates payment"
- **[DON'T]** (Agent-Relevant):
  - Focus on delivery or development tasks required to build a system
  - Focus on system internals (technical stories)
  - Write stories that don't represent a small increment of system behavior in response to an end user action
  - Use development task language: "implement", "create", "refactor", "optimize", "fix", "build", "set up"
  - Use technical implementation details: "query database", "call API", "update table", "refactor code"
  - Write technical stories that describe low-level internal behavior we don't care about
- **[Structural Patterns]**:
  - **Action-Oriented Pattern**: `[Actor] [action] [object]` or `System [behavioral verb] [noun]`
  - **System Story Pattern** (✅): `System [validates|sends|processes|displays] [noun]` or `[Service] [behavioral verb] [noun]` - Observable behavior
  - **Technical Story Pattern** (❌): `[implement|create|refactor|optimize|fix|build] [component]` - Development task or system internals
  - **Detection**: Contains behavioral verbs (submit, view, validate, send) vs development task verbs (implement, create, refactor, optimize, fix)
- **[Examples]**:
  - ✅ **DO** (User/System Stories): "Customer places order", "System validates payment", "User views dashboard", "Payment service processes transaction"
  - ❌ **DON'T** (Technical Stories): "Implement order placement", "Create payment validation", "Build dashboard view", "Refactor payment service", "Optimize database queries"

**Principle 0.2: INVEST Principles**
- **Source**: Slide 12
- **[DO]** (Agent-Relevant):
  - Ensure stories are Negotiable, Testable, Valuable, Estimate-able, Small, and Independent
  - Write stories that are a unit of scope and value
  - Deliver stories in features and increments
  - Write stories so they can be tested
  - Ensure stories can be developed and tested in a matter of days
- **[DON'T]** (Agent-Relevant):
  - Create stories that violate INVEST principles
  - Write stories that are too large or interdependent
- **[Structural Patterns]**:
  - **Small**: 3-12 day effort range, complete interaction flow, 2-5 acceptance criteria
  - **Independent**: Can be delivered without other stories, no blocking dependencies
  - **Testable**: Has acceptance criteria in behavior form, observable outcomes
  - **Valuable**: Delivers measurable value independently
  - **Negotiable**: Details can be discussed (not over-specified)
  - **Estimate-able**: Team can assess effort/complexity
- **[Examples]**:
  - ✅ **DO**: Story with 3-5 acceptance criteria, complete flow, independent value
  - ❌ **DON'T**: Story with 8+ acceptance criteria, multiple flows, requires other stories
- **[Further Recommendations for Humans]** (Show after agent completes step):
  - Ensure stories are worked on by the entire team (requires team assignment)
  - Use stories as placeholders for conversations and collaboration (requires team interaction)

### Section 0.5: All Phases Principles ⚠️ All Phases

**Principle 0.5.1: Epic/Feature/Story Hierarchy**
- **[DO]** (Agent-Relevant):
  - Use Epic, Feature, Story hierarchy structure
  - Organize stories within features and features within epics
- **[DON'T]** (Agent-Relevant):
  - Skip hierarchy levels without justification
  - Mix hierarchy levels inconsistently
- **[Structural Patterns]**:
  - **Format**: Epic → Feature → Story (nested hierarchy)
  - **Epic**: High-level business capability or initiative
  - **Feature**: Cohesive set of functionality within epic
  - **Story**: Small increment of behavior within feature
  - **Detection**: Check for proper nesting, consistent level naming
- **[Examples]**:
  - ✅ **DO**: 
    ```
    Epic: Order Management
      Feature: Order Placement
        Story: Customer places order
        Story: System validates payment
      Feature: Order Fulfillment
        Story: System processes order
    ```
  - ❌ **DON'T**: Stories at epic level, features missing, inconsistent structure

### Section 1: Story Shaping Principles ⚠️ Stage: Story Shaping

**Principle 1.1: Focus Story Maps on User AND System Activities**
- **Source**: Slides 1, 4
- **[DO]** (Agent-Relevant):
  - Focus story maps on both user AND system activities
  - Use story maps to outline user and system behavior
  - Break/group stories so that most fall into a 3-12 day effort range
  - Enable frequent feedback by decomposing the work into smaller items
  - Enable high quality feedback by grouping work into meaningful chunks
  - Include both user activity patterns ("User submits", "Customer places") AND system activity patterns ("System validates", "System sends")
- **[DON'T]** (Agent-Relevant):
  - Arbitrarily decompose stories to a functional level, regardless of size
  - Focus only on user activities (ignore system activities)
  - Focus only on tasks (instead of activities)
  - Arbitrarily decompose stories to a functional level, regardless of size, whenever some content is available
- **[Structural Patterns]**:
  - **User Activity Detection**: Contains patterns like `^(User|Customer|Admin|\w+)\s+\w+` with user actions (submits, views, places)
  - **System Activity Detection**: Contains patterns like `^(System|\w+)\s+(validates|sends|processes|displays|notifies)`
  - **Task Detection** (avoid): Contains `\b(implement|create|build|set up|write|develop)\b`
  - **Validation**: Story map must contain BOTH user activity patterns AND system activity patterns
- **[Examples]**:
  - ✅ **DO**: 
    - User activities: "User submits order", "Customer views products"
    - System activities: "System validates payment", "System sends confirmation"
  - ❌ **DON'T**: 
    - Only user activities: "User submits order", "User views products" (missing system activities)
    - Only tasks: "Implement order submission", "Create payment validation" (not activities)
- **[Further Recommendations for Humans]** (Show after agent completes step):
  - Ask "how big or small are the stories in the map?" when promoted to production
  - **DON'T**: Build the map in absence of the people who can estimate the work

**Principle 1.2: Balance Fine-Grained with Testable/Valuable**
- **Source**: Slide 2
- **[DO]** (Agent-Relevant):
  - Balance fine-grained stories with testable/valuable stories
  - Ensure stories are fine-grained enough to enable frequent feedback
  - Ensure stories are grouped into meaningful chunks for high quality feedback
  - Validate that a business expert can understand the language of most of the stories
  - Focus the language on the business domain
  - Create a common artifact that serves a wide variety of stakeholders
  - Create lightweight but precise documentation over a tome of illegible content
- **[DON'T]** (Agent-Relevant):
  - Create stories that are too fine-grained without being testable or valuable
  - Create stories that are too large to be testable or deliverable quickly
  - Use generic function, verbs, nouns without context
  - Use overly technical, IT concepts, unless core to domain being discussed
- **[Structural Patterns]**:
  - **Too Fine-Grained**: Single element, no value, can't test independently, 1 acceptance criterion
  - **Appropriate**: Complete interaction flow, 2-5 acceptance criteria, delivers value, testable independently
  - **Too Large**: Multiple flows, 6+ acceptance criteria, multiple components, requires multiple stories
  - **Language Check**: Uses domain terms, verb/noun with context, business language
- **[Examples]**:
  - ✅ **DO**: "Customer places order" (complete flow, testable, valuable)
  - ❌ **DON'T**: "Change button color" (too fine-grained, no value)
  - ❌ **DON'T**: "Customer places order and views history and updates profile" (too large, multiple flows)

**Principle 1.3: Use Business Language That is Specific and Precise**
- **Source**: Slide 3
- **[DO]** (Agent-Relevant):
  - Ground the map in business language that is specific and precise
  - Focus the language on the business domain
  - Use verb/noun language
  - Use language that emphasizes performing an operation on an explicit thing
  - Make the map easy to walk through (it tells a story)
  - Make gaps in flow easier to spot where the solution may be incomplete
  - Use domain-specific terms: "order", "customer", "payment", "inventory"
  - Use specific verb/noun combinations: "[Actor] [specific verb] [specific noun]"
- **[DON'T]** (Agent-Relevant):
  - Use generic functions, verbs, nouns without context
  - Use overly technical IT concepts, unless core to domain being discussed
  - Use static functional concepts
- **[Structural Patterns]**:
  - **Business Language Pattern**: `[Actor] [specific verb] [specific noun]` (e.g., "Customer places order")
  - **Generic Pattern** (avoid): `^\s*(Process|Handle|Manage|Get|Set)\s*$` or single word
  - **Technical Pattern** (avoid): `\b(API|database|endpoint|service|component|query|call|update)\b`, `\w+\(\)`
  - **Static Functional** (avoid): "[Noun] Management", "[Noun] Processing", "[Noun] Administration"
  - **Active Behavioral** (prefer): "[Verb] [noun]" (e.g., "Place order", "Validate payment")
- **[Examples]**:
  - ✅ **DO**: "Customer places order", "System validates payment", "User views dashboard"
  - ❌ **DON'T**: "Process order" (generic), "Order Management" (static), "getOrder()" (code pattern)
  - ❌ **DON'T**: "Query database" (technical), "Handle request" (generic)

**Principle 1.4: Use Active Behavioral Language**
- **[DO]** (Agent-Relevant):
  - Favor active behavioral language over functional/capability breakup
  - Use story maps to outline user and system behavior (NOT tasks)
  - Use action verbs: "submits", "views", "validates", "sends", "displays"
  - Describe behaviors: "[Actor] [action] [object]"
- **[DON'T]** (Agent-Relevant):
  - Use functional or capability-based language instead of behavioral language
  - Focus on tasks instead of behaviors
  - Use capability nouns: "Management", "Processing", "Administration"
  - Use task verbs: "implement", "create", "build", "set up"
- **[Structural Patterns]**:
  - **Behavioral Pattern**: `\b(submit|view|place|receive|validate|send|display)\b\s+\w+`
  - **Capability Pattern** (avoid): `\w+\s+(Management|Processing|Administration)`
  - **Task Pattern** (avoid): `\b(implement|create|build|set up|write|develop)\b`
- **[Examples]**:
  - ✅ **DO**: "Place order" (active behavior), "Validate payment" (active behavior)
  - ❌ **DON'T**: "Order Management" (capability), "Payment Processing" (capability)
  - ❌ **DON'T**: "Implement order placement" (task), "Create payment validation" (task)

**Principle 1.5: Identifying Marketable Increments of Value**
- **Source**: Slide 10
- **[DO]:**
  - Identify marketable increments of value during Story Shaping
  - Do just enough story mapping to extrapolate how many epics, features, and stories make up an increment
  - Continually identify and refine marketable increments
  - During Idea Shaping and Discovery, continually identify and refine Marketable Increments
- **[DON'T]:**
  - Over-elaborate story mapping during shaping
  - Skip increment identification

**Principle 1.6: Relative Sizing Upstream**
- **Source**: Slide 10
- **[DO]:**
  - Use relative sizing upstream for larger buckets of scope
  - Compare and contrast new work against previously completed work
  - Relatively size increments and initiatives against each other
  - Relatively size against previously delivered increments of value that are similar in platform and team skills
  - Conduct relative sizing where size actually matters (upstream and for larger buckets of scope)
  - At any point, assess work by comparing and contrasting it to work previously completed
  - Relatively size new initiatives against previously completed ones (as long as work is similar from platform and team perspective)
  - Use relative sizing at initiative and increment level for accelerated and surprisingly accurate estimate of size
- **[DON'T]:**
  - Use relative sizing only at story level (should be upstream at initiative/increment level)
  - Size work without comparing to similar previously completed work

### Section 2: Discovery Principles ⚠️ Stage: Discovery

**Principle 2.1: Refining Marketable Increments on Story Map**
- **[DO]:**
  - Refine marketable increments on story map during Discovery
  - Update story map based on discovery insights
  - Ensure increments are well-defined
  - Continually identify and refine marketable increments
- **[DON'T]:**
  - Skip increment refinement during discovery
  - Ignore discovery insights when updating story map

**Principle 2.2: Story Mapping Practices (Encourage & Avoid)**
- **[DO]** (Agent-Relevant):
  - Focus on user AND system activities (not just user activities or tasks)
  - Balance fine-grained stories with testable/valuable stories (3-12 day range where applicable)
  - Use business language that is specific, precise, and behavioral
  - Use active behavioral language to describe story activities
- **[DON'T]** (Agent-Relevant):
  - Arbitrarily decompose stories regardless of size whenever some content is available
  - Use generic functions, verbs, nouns without context
  - Use overly technical IT concepts
  - Use static functional concepts
- **[Further Recommendations for Humans]** (Show after agent completes step):
  - **DON'T**: Build map without people who can estimate

**Principle 2.3: Story Mapping Estimation and Counting**
- **Source**: Slides 5, 6, 7, 8, 9, 11
- **[DO]** (Agent-Relevant - Mapping Context):
  - Add story counts to epics and features where exact stories are unknown (extrapolation)
  - Use story counts instead of detailed story lists when completing the full map is not desired
  - Mark extrapolated story counts (e.g., "~X stories" or "Extrapolated: ~X stories") in the story map
  - Use relative sizing upstream (initiative/increment level) for mapping purposes
  - Switch from estimating story details to simply counting stories in the map
  - Add story counts to help understand scope without fully decomposing every story
  - Add story counts during story shaping where decomposition isn't needed
  - Use story counts to indicate scope without requiring complete story decomposition
- **[DON'T]** (Agent-Relevant - Mapping Context):
  - Require complete story decomposition before adding counts to the map
  - Estimate only at story level (should add counts upstream at epic/feature level)
  - Focus on detailed story estimation when mapping (use counts instead)
  - Complete the entire map before marking extrapolated story counts
  - Require full story details when story counts are sufficient for mapping purposes

**Principle 2.4: Story Grooming**
- **Source**: Slide 11
- **[DO]** (Agent-Relevant):
  - Identify stories that are too ambiguous
  - Split work into smaller stories before accepting
  - Ensure stories are small (can be completed quickly)
  - Identify stories that can be completed quickly
  - Ensure stories are small
- **[DON'T]** (Agent-Relevant):
  - Accept stories that are too ambiguous
  - Accept stories that are too large
- **[Further Recommendations for Humans]** (Show after agent completes step):
  - Use story grooming to reject stories that are too ambiguous
  - Use sprint planning and story grooming as opportunity to reject stories that are too ambiguous
  - Split work into smaller stories before accepting them
  - Only accept stories that can be completed quickly
  - Size enough work based on actual throughput
  - Keep enough work to keep the team supplied
  - Size enough work based on actual throughput to keep team supplied
  - Create predictable performance numbers
  - **DON'T**: Size work without considering actual throughput

### Section 3: Story Exploration Principles ⚠️ Stage: Story Exploration

**Principle 3.1: Writing Story Acceptance Criteria**
- **Source**: Slides 13, 16
- **[DO]** (Agent-Relevant):
  - Define acceptance criteria for every story in next feature/slice
  - Write acceptance criteria in behavior form or domain-oriented form
  - Use "When...then..." format or similar behavioral language
  - Ensure criteria are testable and define clear boundaries
  - Make acceptance criteria the main focus (story summary provides context)
  - Write acceptance criteria that describe conditions story must meet to be accepted as complete by Product Owner
  - Use acceptance criteria to share a clear boundary to the scope of a story
  - Use acceptance criteria to help describe to a team the conditions under which a story can be considered done
  - Define acceptance criteria for every story inside the next feature/slice to start
- **[DON'T]** (Agent-Relevant):
  - Skip acceptance criteria for stories
  - Write acceptance criteria in technical or task-oriented language
  - Make story summary the main focus (acceptance criteria should be primary)
- **[Structural Patterns]**:
  - **Format**: `When [condition], then [outcome]` or `Given [context], When [action], Then [outcome]`
  - **Behavior Form**: Uses behavioral language, describes user/system interactions, observable outcomes
  - **Technical Form** (avoid): Uses code patterns, implementation details, function calls
  - **Required Elements**: Condition (trigger), Outcome (observable result), Testability
  - **Detection**: Contains "When...then..." pattern, uses behavioral language, describes observable outcomes
- **[Examples]**:
  - ✅ **DO**: 
    - "When user submits order, then system validates payment and sends confirmation"
    - "When payment is valid, then system sends confirmation email"
    - "When user views dashboard, then system displays recent orders"
  - ❌ **DON'T**: 
    - "When payment.validate() is called, then return true" (code pattern)
    - "When database query executes, then return results" (technical)
    - "When API endpoint is hit, then return JSON" (implementation detail)
- **[Further Recommendations for Humans]** (Show after agent completes step):
  - Share common understanding of the next feature/slice starting delivery (requires team collaboration)

**Principle 3.2: Refining Story Map During Exploration**
- **Source**: Slide 16
- **[DO]:**
  - Refine/merge/split stories as necessary during exploration
  - Ensure stories expressed at small/similar level of details
  - Update story map based on exploration insights
  - Keep focus on completeness from user/system behavior perspective
  - Refine/merge/split stories as necessary to ensure they are expressed at a small/similar level of details
  - Keep focus of story writing on completeness from a user/system behavior perspective
- **[DON'T]:**
  - Skip story refinement during exploration
  - Leave stories at inconsistent levels of detail
  - Lose focus on user/system behavior completeness

**Principle 3.3: Defining System Level Stories**
- **[DO]:**
  - Identify and define system-level stories (not just user-facing)
  - Ensure system behavior is captured
  - Focus on how system behaves in response to user interactions
  - Document system activities alongside user activities
- **[DON'T]:**
  - Focus only on user-facing stories
  - Ignore system behavior
  - Skip system-level story definition

**Principle 3.4: Story Specification**
- **Source**: Slide 16
- **[DO]** (Agent-Relevant):
  - Refine understanding of stories and their solution
  - Document story specifications with scenarios and examples
  - Create specification scenarios that describe detailed interactions between users and system
  - Use normal examples for concrete, specific use cases
  - Use parameterized examples when multiple similar cases differ only in data
  - Link scenarios to stories (one story can have multiple scenarios)
  - Link examples to scenarios (scenarios contain examples)
  - Cover happy path, edge cases, and error cases in scenarios
  - Explore remaining key risks/unknowns/assumptions
  - Refine understanding of stories & their solution for a feature or thin slice
  - Explore remaining key risks/unknowns/assumptions for upcoming to be delivered Stories
  - Complete supporting design and definition activities necessary to laying out how the stories will be delivered (e.g. UX, Domain Design, etc.)
  - Use other helpful agile artifacts: Planning Game, UX, Architecture Modeling, Spec By Example, Domain Driven Design
  - Go relatively deep on smallest part of solution that team can deliver on quickly together
- **[DON'T]** (Agent-Relevant):
  - Skip supporting design activities
  - Leave key risks/unknowns/assumptions unexplored
  - Skip documenting story specifications
  - Create scenarios without examples
  - Use parameterized examples when normal examples would be clearer
  - Create examples without linking them to scenarios
  - Skip scenarios for stories (scenarios provide detailed context)
- **[Structural Patterns]**:
  - **Story → Scenario Relationship**: One story can have multiple scenarios (happy path, edge cases, error cases)
  - **Scenario → Example Relationship**: Scenarios contain examples (normal and/or parameterized)
  - **Normal Example Format**: Concrete values, specific data points, no parameter tables
  - **Parameterized Example Format**: `<parameter>` placeholders with Examples table containing multiple data rows
  - **Scenario Format**: Given/When/Then structure with narrative flow
  - **Complete Specification**: Story → Acceptance Criteria → Scenarios → Examples (normal/parameterized)
- **[Examples]**:
  - ✅ **DO**: 
    - Story with multiple scenarios covering different paths
    - Scenarios with normal examples for concrete cases
    - Parameterized examples for validation rules with multiple inputs
    - Clear hierarchy: Story → Scenarios → Examples
  - ❌ **DON'T**: 
    - Stories without scenarios
    - Scenarios without examples
    - Parameterized examples when normal examples would be clearer
    - Examples not linked to scenarios
- **[Further Recommendations for Humans]** (Show after agent completes step):
  - Ensure subset of team takes ownership, estimates, commits to start
  - Perform enough definition and design so that a small cross-functional team collectively understands the what, the how, and the who of delivery for the next sprint (or maybe two)
  - Ensure subset of team have taken ownership of delivering the work, estimated it, and committed to start in the next couple of days
  - Gain deep shared understanding of the outcomes and work required for team to execute delivery activities together for a short period of time
  - **DON'T**: Start work without team ownership and commitment

**Principle 3.5: Story Format and Structure**
- **Source**: Slide 15
- **[DO]** (Agent-Relevant):
  - Use simple title to convey meaning (when story maps are in place)
  - Make acceptance criteria the main focus
  - Use story summary only to provide context
  - Write stories that represent a small increment of system behavior in response to an end user action
  - Use story format that provides reason for system behavior to exist (in absence of higher-level context)
  - Ensure each card represents a small change in the system's behavior
  - Use simple title to convey meaning when story maps are in place
  - Make main focus of story the acceptance criteria (story summary only provides context)
- **[DON'T]** (Agent-Relevant):
  - Use typical agile story template without understanding its purpose
  - Write "stories" that don't represent a small increment of system behavior in response to an end user action
  - Make story summary the main focus (acceptance criteria should be primary)
  - Use story template redundantly when story maps are in place
  - Use typical preconceived agile story template without understanding its purpose
  - Write a "story" that doesn't represent a small increment of system behavior in response to an end user action
  - Mis-use format and attempt to apply it to work that does not require any of the above outcomes to be successful
- **[Structural Patterns]**:
  - **With Story Maps**: Simple title format: `[Verb] [Noun]` (e.g., "Place order")
  - **Without Story Maps**: Full format: `As a [User] I want to [Action] So that [Value]`
  - **Required Fields**: Title (verb/noun), Acceptance Criteria (behavior form)
  - **Optional Fields**: Summary/Description (provides context only)
  - **Title Pattern**: `[Verb] [Noun]` or `[Actor] [verb] [object]` (e.g., "Submit order", "Customer places order")
  - **Detection**: Has title matching verb/noun pattern, has acceptance criteria, acceptance criteria is main content
- **[Examples]**:
  - ✅ **DO** (With Story Maps):
    ```
    Title: Place order
    Acceptance Criteria:
      When user submits order, then system validates payment
      When payment is valid, then system sends confirmation
    ```
  - ✅ **DO** (Without Story Maps):
    ```
    As a customer
    I want to place an order
    So that I can purchase items
    
    Acceptance Criteria:
      When user submits order, then system validates payment
      When payment is valid, then system sends confirmation
    ```
  - ❌ **DON'T**: Missing acceptance criteria, summary is main focus, title doesn't follow verb/noun pattern
- **[Further Recommendations for Humans]** (Show after agent completes step):
  - Use format that gives team insight into mind of end user to help make better design decisions with end user goal in mind (requires team discussion)

### Key Principles Summary by Stage:

**Story Shaping:**
- Focus on user AND system activities
- Balance fine-grained with testable/valuable (3-12 day range)
- Use business language (specific, precise, behavioral)
- Use active behavioral language
- Identify marketable increments
- Use relative sizing upstream

**Discovery:**
- Refine marketable increments
- Apply story mapping practices (DO/DON'T from Principle 2.2)
- Use throughput/volume planning
- Groom stories for next increment

**Story Exploration:**
- Write acceptance criteria (behavior form)
- Refine story map during exploration
- Define system level stories
- Complete story specification
- Share common understanding

## Phase 1: Rule Creation

### 1.1 Create Base Story Rule
- **File**: `behaviors/stories/stories-rule.mdc`
- **Structure**: Follow `code-agent-rule.mdc` pattern with frontmatter, conventions, 5 major principle sections
- **Content**: 
  - **Section 0: Universal Principles** (applies to ALL commands across ALL stages)
    - Principles that apply across all story writing stages and all commands
    - Examples: Business language usage, user/system focus, INVEST principles
    - Marked as: ⚠️ **Universal** or ⚠️ **All Commands**
  
  - **Section 0.5: All Phases Principles** (applies to ALL commands across Story Shaping, Discovery, and Exploration)
    - Principles that apply across all three major stages but may not be universal to all story writing contexts
    - Examples: Story map refinement practices, epic/feature/story hierarchy concepts
    - Marked as: ⚠️ **All Phases** or ⚠️ **All Stages**
  
  - **Section 1: Story Shaping principles**
    - Introduction to Story Mapping
      - Mark applicable commands: `story-shape`
    - Identifying Marketable Increments of Value
      - Mark applicable commands: `story-market-increments`
    - Each principle marked with: ⚠️ **Commands: [command-list]**, ⚠️ **All Phases**, ⚠️ **Stage: Story Shaping**, or ⚠️ **Universal**
  
  - **Section 2: Discovery principles**
    - Refining Marketable Increments on Story Map
      - Mark applicable commands: `story-discovery`
    - Story Mapping Practices (Encourage & Avoid) ⚠️ **Stage: Discovery**
      - **Principle**: Apply story mapping practices that encourage good practices and avoid anti-patterns when refining story maps, planning, and grooming stories.
      - **Practices documented as DO/DON'T examples** (NOT a command - practices guide Discovery commands):
        - **[DO]:**
          * Focus on user AND system activities (not just user activities or tasks)
          * Balance fine-grained stories with testable/valuable stories (3-12 day range where applicable)
          * Use business language that is specific, precise, and behavioral
          * Use active behavioral language to describe story activities
        - **[DON'T]:**
          * Arbitrarily decomposing stories regardless of size whenever some content is available
          * Building map without people who can estimate
          * Using generic functions, verbs, nouns without context
          * Using overly technical IT concepts
          * Using static functional concepts
      - Mark applicable commands: ⚠️ **Stage: Discovery** (applies to `story-discovery` command)
    - Planning, Scheduling, & Forecasting
      - **Note**: May be deferred - calculation-heavy (not a separate command)
    - Story Grooming
      - Mark applicable commands: `story-discovery`
    - Each principle marked with: ⚠️ **Commands: [command-list]**, ⚠️ **All Phases**, ⚠️ **Stage: Discovery**, or ⚠️ **Universal**
  
  - **Section 3: Story Exploration principles**
    - **Outcome**: Sharing Common Understanding (goal of stage, not a command)
      - **Agent-Relevant**: Share common understanding of next feature/slice starting delivery (via documentation and specifications)
      - **Further Recommendations for Humans** (Show after agent completes step):
        - Ensure cross-functional team understands what, how, and who (requires team collaboration)
        - Align team on next sprint (or maybe two) scope (requires team discussion)
      - Mark applicable commands: ⚠️ **Stage: Story Exploration** (all exploration commands contribute to this outcome)
    - Writing Story Acceptance Criteria
      - Mark applicable commands: `story-explore`
      - Contributes to shared understanding of what needs to be delivered
    - Refining Story Map During Exploration
      - Mark applicable commands: `story-explore`
      - Contributes to shared understanding of scope and structure
    - Defining System Level Stories
      - Mark applicable commands: `story-explore`
      - Contributes to shared understanding of system behavior
    - Story Specification
      - Mark applicable commands: `story-specification-scenarios`, `story-specification-examples`
      - **Agent-Relevant**: Contributes to shared understanding of how to implement (via documentation)
      - **Further Recommendations for Humans** (Show after agent completes step): Contributes to team ownership (requires team assignment and commitment)
    - Story Testing and INVEST Principles
      - **NOT a command** - validated through principles/heuristics throughout all commands
      - Ensure stories are testable (INVEST principle)
      - Ensure stories can be developed and tested in matter of days
      - Validate stories follow INVEST principles (Negotiable, Testable, Valuable, Estimate-able, Small, Independent)
      - Ensure stories are action-oriented and describe user/system interactions
      - Mark applicable commands: ⚠️ **Stage: Story Exploration** (applies to all exploration commands)
    - Each principle marked with: ⚠️ **Commands: [command-list]**, ⚠️ **All Phases**, ⚠️ **Stage: Story Exploration**, or ⚠️ **Universal**

- **Command Applicability Format**:
  - Universal principles: ⚠️ **Universal** or ⚠️ **All Commands** (applies to ALL commands across ALL stages)
  - All phases/stages: ⚠️ **All Phases** or ⚠️ **All Stages** (applies to ALL commands across Story Shaping, Discovery, and Exploration)
  - Stage-specific: ⚠️ **Stage: Story Shaping** (applies to all commands within Story Shaping stage)
  - Command-specific: ⚠️ **Commands: story-shape, story-market-increments** (applies to specific commands)
  - Multiple commands: ⚠️ **Commands: story-discovery, story-explore** (applies to multiple specific commands)
  - Helps AI focus on relevant principles when generating/validating for specific commands

- **DO/DON'T Examples**: Extract from PowerPoint for each section, marked with command applicability
  - **Important**: Practices (encourage/avoid lists) should be documented as DO/DON'T examples in principles, NOT as separate commands
  - **Format**: Follow BDD rule file structure:
    - **[DO]:** followed by bullet points (or code blocks if applicable) - **Agent-Relevant** items only
    - **[DON'T]:** followed by bullet points (or code blocks if applicable) - **Agent-Relevant** items only
    - **[Further Recommendations for Humans]:** (Optional section) - Human team guidance shown after agent completes step
  - **Agent vs Human Separation**: 
    - **Agent-Relevant**: Things the AI agent can do/validate (documentation, analysis, generation, validation)
    - **Further Recommendations for Humans**: Things requiring human teams/collaboration (team ownership, estimation, commitment, sprint planning, team discussions)
  - **Example**: "Story Mapping Practices" principle in Section 2 has DO/DON'T examples documenting practices to encourage and avoid - these guide Discovery commands but are NOT a separate command

**Important Notes on Command Applicability**:
- **Purpose**: Helps AI focus on relevant principles when generating/validating for specific commands
- **AI Usage**: When command specified, AI emphasizes principles in priority order:
  1. Universal principles (⚠️ **Universal**) - applies to all commands across all stages
  2. All Phases principles (⚠️ **All Phases**) - applies to all commands across Story Shaping, Discovery, and Exploration
  3. Stage-specific principles (⚠️ **Stage: [stage-name]**) - applies to all commands within that stage
  4. Command-specific principles (⚠️ **Commands: [command-list]**) - applies to specific commands
- **Heuristic Loading**: Each command has its own heuristic class (standard pattern)
- **Separation of Concerns**:
  - Rule file markers = AI guidance (which principles/examples to emphasize)
  - Code heuristic mapping = Automated validation (which heuristics to run)
- **Example**: When validating `story-shape` command (Story Shaping stage):
  - AI focuses on: Universal principles + All Phases principles + Stage: Story Shaping principles + Commands: story-shape principles
  - Code runs: `StoryShapeHeuristic` (one heuristic per command)

### 1.2 Create Rule Command Files
- `behaviors/stories/rule/stories-rule-cmd.md` - Main command
- `behaviors/stories/rule/stories-rule-generate-cmd.md` - Generate delegate
- `behaviors/stories/rule/stories-rule-validate-cmd.md` - Validate delegate

## Shared Implementation: Common Runner Enhancement

### Add Prompting Questions Concept to Common Runner
- **File**: `behaviors/common_command_runner/common_command_runner.py`
- **New Concept**: Prompting Questions - Prerequisite context validation
- **Purpose**: Ensure required context is available before plan/generate runs
- **Implementation**:
  - Add `prompting_questions` attribute to `Command` class (list of question strings)
  - Add `check_prompting_questions()` method to `CodeAugmentedCommand` class
  - Method checks if questions are answered in the provided context
  - If not answered: AI generates prompts to ask user those questions
  - If answered: Proceeds with normal flow
  - **Workflow Integration**:
    - `generate()` and `plan()` methods check prompting questions FIRST
    - Only proceed if questions are answered (or after asking them)
    - Questions are command-specific (defined per command)
- **API**: See Phase 3.1 below for full API details

### Update Stories Runner Base
- **File**: `behaviors/stories/stories_runner.py`
- **Base**: Extend from `common_command_runner` framework
- **Structure**: Follow `behaviors/bdd/bdd-runner.py` pattern
- **No OperationCommand needed** - using standard Command pattern

---

## Stage 1: Story Shaping Implementation

### Commands (2 commands)

#### Command 1.1: Story Shape Command
- **Main**: `behaviors/stories/shape/story-shape-cmd.md`
- **Delegates**: `story-shape-generate-cmd.md`, `story-shape-validate-cmd.md`
- **Purpose**: Create story map shell and elaborate/extrapolate scope
- **Command Name**: `/story-shape`
- **Combines**: First 2 steps from Idea Shaping (Create Story Map Shell + Elaborate and Extrapolate Scope)
- **Prompting Questions**:
  - What is the product or feature vision?
  - Who are the target users or stakeholders?
  - What are the main user goals or outcomes?
  - What is the scope boundary (what's in/out)?
- **Content**:
  - Create initial epic/feature/story hierarchy structure
  - Focus on user AND system activities (not tasks)
  - Establish high-level structure
  - Use business language (verb/noun, specific and precise)
  - Elaborate on the shell to understand full scope
  - Extrapolate how many epics, features, and stories make up increments
  - Balance fine-grained with testable/valuable
  - Ensure stories are sized appropriately (3-12 day range where applicable)
- **Heuristics**: 
  - Check for epic/feature/story hierarchy structure
  - Validate user/system focus (not tasks)
  - Check business language usage
  - Validate scope extrapolation and story sizing

#### Command 1.2: Story Market Increments Command
- **Main**: `behaviors/stories/market-increments/story-market-increments-cmd.md`
- **Delegates**: `story-market-increments-generate-cmd.md`, `story-market-increments-validate-cmd.md`
- **Purpose**: Identify marketable increments of value
- **Command Name**: `/story-market-increments`
- **Prompting Questions**:
  - Is there an existing story map shell to work with?
  - What are the business priorities or strategic goals?
  - What are the market constraints or deadlines?
  - Are there any dependencies between increments?
- **Content**:
  - Identify marketable increments of value
  - Place increments around the story map
  - Prioritize increments
  - Perform relative sizing at initiative/increment level (compare against previous work)
- **Heuristics**:
  - Validate marketable increment identification
  - Check relative sizing approach
  - Validate increment prioritization

---

## Stage 2: Discovery Implementation

### Commands (1 command)

#### Command 2.1: Story Discovery Command
- **Main**: `behaviors/stories/discovery/story-discovery-cmd.md`
- **Delegates**: `story-discovery-generate-cmd.md`, `story-discovery-validate-cmd.md`
- **Purpose**: Guide through discovery stage for next market increment
- **Command Name**: `/story-discovery`
- **Prompting Questions**:
  - Which market increment are we focusing on for discovery?
  - What new information or insights have been discovered?
  - Are there any changes to business priorities or constraints?
  - What is the target delivery timeline for this increment?
- **Content**:
  - Refine marketable increments on story map
  - Update story map based on discovery insights
  - Ensure increments are well-defined
  - Continually identify and refine marketable increments
  - Apply story mapping practices (from principles)
  - Groom stories for next increment
- **Heuristics**: 
  - Check story map refinement
  - Validate story mapping practices (via principles)
  - Check story grooming practices

---

## Stage 3: Story Exploration Implementation

### Commands (4 commands)

#### Command 3.1: Story Explore Command
- **Main**: `behaviors/stories/explore/story-explore-cmd.md`
- **Delegates**: `story-explore-generate-cmd.md`, `story-explore-validate-cmd.md`
- **Purpose**: Guide through story exploration stage
- **Command Name**: `/story-explore`
- **Outcome**: Share common understanding of next feature/slice starting delivery
- **Prompting Questions**:
  - Which feature or slice are we exploring?
  - Which stories need acceptance criteria?
  - Are there any system-level concerns or technical constraints?
  - Who are the stakeholders that need to share understanding?
- **Content**:
  - Write story acceptance criteria
  - Refine story map during exploration
  - Define system level stories
- **Heuristics**:
  - Check acceptance criteria presence and quality
  - Validate story map refinement during exploration
  - Check system level story definition

#### Command 3.2: Story Specification Scenarios Command
- **Main**: `behaviors/stories/specification-scenarios/story-specification-scenarios-cmd.md`
- **Delegates**: `story-specification-scenarios-generate-cmd.md`, `story-specification-scenarios-validate-cmd.md`
- **Purpose**: Create story specification scenarios
- **Command Name**: `/story-specification-scenarios`
- **Prompting Questions**:
  - Which stories need scenario-based specifications?
  - What are the main user flows or system flows to document?
  - Are there any edge cases or alternative paths to consider?
- **Content**:
  - Create scenario-based specifications for stories
  - Document story scenarios and flows
- **Heuristics**:
  - Validate scenario completeness
  - Check scenario structure and flow

#### Command 3.3: Story Specification Examples Command
- **Main**: `behaviors/stories/specification-examples/story-specification-examples-cmd.md`
- **Delegates**: `story-specification-examples-generate-cmd.md`, `story-specification-examples-validate-cmd.md`
- **Purpose**: Create story specification examples
- **Command Name**: `/story-specification-examples`
- **Prompting Questions**:
  - Which stories need example-based specifications?
  - What are the key examples or test cases to document?
  - Are there boundary conditions or edge cases to cover?
- **Content**:
  - Create example-based specifications for stories
  - Document concrete examples and edge cases
- **Heuristics**:
  - Validate example completeness
  - Check example clarity and coverage

#### Command 3.4: Story Discovery Explore Command
- **Main**: `behaviors/stories/discovery-explore/story-discovery-explore-cmd.md`
- **Delegates**: `story-discovery-explore-generate-cmd.md`, `story-discovery-explore-validate-cmd.md`
- **Purpose**: Combined discovery and exploration workflow
- **Command Name**: `/story-discovery-explore`
- **Prompting Questions**:
  - Which market increment are we focusing on?
  - What new information or insights have been discovered?
  - Which feature or slice are we exploring?
  - Are there any system-level concerns or technical constraints?
- **Content**:
  - Combines discovery and exploration activities
  - Refines increments and explores stories in one workflow
- **Heuristics**:
  - Combines discovery and exploration heuristics

### Runner Implementation

**For each command in this stage:**
- **Inner Class**: `[CommandName]Command(Command)` - Business logic
  - Standard Command methods: `generate()`, `validate()`
  - **Prompting Questions**: Define command-specific questions as class attribute or in command file
    - Questions identify required context/information before command can run
    - Example: `prompting_questions = ["What is the product vision?", "Who are the target users?"]`
  - Uses heuristics for validation
  
- **CLI Wrapper Class**: `CodeAugmented[CommandName]Command(CodeAugmentedCommand)` - CLI integration
  - `handle_cli()` method - Processes CLI arguments
  - Creates inner command instance with prompting questions
  - `generate_instructions` - Prompt for AI agent generation
  - `validate_instructions` - Prompt for AI agent validation
  - **Prompting Questions Check**: Automatically runs before generate/plan via CodeAugmentedCommand

**Commands to implement:**
- `StoryShapeCommand` + `CodeAugmentedStoryShapeCommand`
- `StoryMarketIncrementsCommand` + `CodeAugmentedStoryMarketIncrementsCommand`

### Heuristics Implementation

#### Heuristic 1.1: StoryShapeHeuristic
- Validates story shape command
- Validates epic/feature/story hierarchy structure
- Validates user/system focus (not tasks)
- Checks business language usage
- Validates scope extrapolation and story sizing (3-12 day range)
- Checks fine-grained/testable balance

#### Heuristic 1.2: StoryMarketIncrementsHeuristic
- Validates market increments command
- Validates marketable increment identification
- Checks increment prioritization
- Validates relative sizing approach at initiative/increment level

### Templates

#### Template 1.1: Story Map Template
- **File**: `behaviors/stories/map/story-map-template.md`
- **Content**: Epic/feature/story hierarchy structure
- **Used by**: Story Shape command

---

## Stage 2: Discovery Implementation

### Commands (1 command)

#### Command 2.1: Story Discovery Command

**For each command:**
- **Inner Class**: `[CommandName]Command(Command)` - Business logic
  - Standard Command methods: `generate()`, `validate()`
  - **Prompting Questions**: Define command-specific questions as class attribute or in command file
    - Questions identify required context/information before command can run
    - Example: `prompting_questions = ["What is the product vision?", "Who are the target users?"]`
  - Uses heuristics for validation
  - **Calculation Commands**: May use code runners for calculations, prompt users for input, return structured JSON
  
- **CLI Wrapper Class**: `CodeAugmented[CommandName]Command(CodeAugmentedCommand)` - CLI integration
  - `handle_cli()` method - Processes CLI arguments
  - Creates inner command instance with prompting questions
  - `generate_instructions` - Prompt for AI agent generation
  - `validate_instructions` - Prompt for AI agent validation
  - **Prompting Questions Check**: Automatically runs before generate/plan via CodeAugmentedCommand

### 3.3 CLI Entry Points
- Add CLI handlers for each command:
  - `execute-shape` - Execute command (generates if first call, validates if second call)
  - `generate-shape` - Generate only
  - `validate-shape` - Validate only
  
  - `execute-market-increments` - Execute command
  - `generate-market-increments` - Generate only
  - `validate-market-increments` - Validate only
  
  - `execute-discovery` - Execute command
  - `generate-discovery` - Generate only
  - `validate-discovery` - Validate only
  
  - `execute-explore` - Execute command
  - `generate-explore` - Generate only
  - `validate-explore` - Validate only
  
  - `execute-specification-scenarios` - Execute command
  - `generate-specification-scenarios` - Generate only
  - `validate-specification-scenarios` - Validate only
  
  - `execute-specification-examples` - Execute command
  - `generate-specification-examples` - Generate only
  - `validate-specification-examples` - Validate only
  
  - `execute-discovery-explore` - Execute command (combined workflow)
  - `generate-discovery-explore` - Generate only
  - `validate-discovery-explore` - Validate only
  
- Plus: `execute-rule`, `generate-rule`, `validate-rule`

**Usage Examples:**
- `/story-shape` → Generates story map shell and scope (first call)
- `/story-shape` → Validates story map shell and scope (second call)
- `/story-market-increments` → Generates marketable increments identification (first call)
- `/story-market-increments` → Validates marketable increments (second call)

### Runner Implementation

**For each command in this stage:**
- **Inner Class**: `StoryDiscoveryCommand(Command)` - Business logic
- **CLI Wrapper Class**: `CodeAugmentedStoryDiscoveryCommand(CodeAugmentedCommand)` - CLI integration

### Heuristics Implementation

#### Heuristic 2.1: StoryDiscoveryHeuristic
- Validates discovery command
   - Validates increment refinement and story map updates
   - Checks story mapping practices (via principles)
   - Validates story grooming practices
   - Checks story sizing and ambiguity detection

---

## Stage 3: Story Exploration Implementation

### Commands (4 commands)

#### Command 3.1: Story Explore Command


## Phase 6: Integration & Configuration

### 6.1 Update behavior.json
- **File**: `behaviors/stories/behavior.json`
- Set `deployed: true`
- Add description: "Story writing practices and standards for agile teams"
- Add workflows if multi-stage workflow exists

### 6.2 Update code-agent-index.json
- **File**: `behaviors/stories/code-agent-index.json` (create if needed)
- Add all story artifacts (rules, commands, runners)
- Follow pattern from `behaviors/bdd/code-agent-index.json`

### 6.3 Update feature-outline.md
- **File**: `behaviors/stories/feature-outline.md`
- Document all 7 commands and their purposes
- List commands and their relationships to stages
- Document workflow patterns (sequential and iterative)
- Document command-to-heuristic mapping

## Naming Conventions

### Rules
- **Main feature rule**: `stories-rule.mdc` (e.g., `behaviors/stories/stories-rule.mdc`)
- **Rule command files**: `stories-rule-cmd.md`, `stories-rule-generate-cmd.md`, `stories-rule-validate-cmd.md`
- **Rule file location**: `behaviors/stories/stories-rule.mdc`

### Commands
- **Main command**: `<command-name>-cmd.md` (e.g., `story-shape-cmd.md`)
- **Delegate commands**: `<command-name>-generate-cmd.md`, `<command-name>-validate-cmd.md`
- **Command directory**: `behaviors/stories/<command-name>/` (e.g., `behaviors/stories/shape/`)
- **Command file locations**:
  - Main: `behaviors/stories/<command-name>/<command-name>-cmd.md`
  - Generate: `behaviors/stories/<command-name>/<command-name>-generate-cmd.md`
  - Validate: `behaviors/stories/<command-name>/<command-name>-validate-cmd.md`

### Runners
- **Runner file**: `behaviors/stories/stories_runner.py`
- **Test file**: `behaviors/stories/stories_runner_test.py`
- **Command class**: `<CommandName>Command` (PascalCase, e.g., `StoryShapeCommand`)
- **Wrapper class**: `CodeAugmented<CommandName>Command` (e.g., `CodeAugmentedStoryShapeCommand`)
- **Config class**: `<CommandName>Config` (e.g., `StoryShapeConfig`)

### Templates
- **Story-specific templates**: `behaviors/stories/<template-type>/<template-name>.md`
- **Common templates**: `behaviors/stories/feature/<template-name>.md` (if shared)

## File Structure Requirements

### Rule File Structure (`stories-rule.mdc`)
1. **Frontmatter** (YAML):
   - `description`: Story writing practices and standards for agile teams
   - `globs`: List of file patterns this rule applies to
   - `alwaysApply`: false (or true if needed)
2. **When/then statement**: `**When** writing user stories for agile development, **then** follow these principles...`
3. **Executing Commands section**: Quick reference to commands that use this rule
4. **Conventions section**: Naming conventions, file locations, structural conventions (before principles)
5. **Principles section**: Numbered principles (## 1. Principle Name) with DO/DON'T examples
6. **Templates section** (if applicable): Templates used for generating files
7. **Commands section** (at end): Detailed list of commands that implement or use this rule

### Command File Structure (`<command-name>-cmd.md`)
1. **Header**: `### Command: /<command-name>`
2. **Purpose section**: `**[Purpose]:**` - What the command does
3. **Rule section**: `**[Rule]:**` - Reference to rule file (`stories-rule.mdc`)
4. **Runner section**: `**Runner:**` - CLI commands and runner path
5. **Action 1: GENERATE** - Steps with performers (User, AI Agent, Runner, Code)
6. **Action 2: GENERATE FEEDBACK** - User review steps
7. **Action 3: VALIDATE** - Validation steps with performers
8. **Action 4: VALIDATE FEEDBACK** - User review of validation results

### Runner File Structure (`stories_runner.py`)
1. **Imports**: From `common_command_runner` and feature-specific modules
2. **Inner Command Classes**: One per command, extends `Command` or `CodeAgentCommand`
   - Implements `generate()` and `validate()` methods
   - Uses templates for generation
   - Contains core business logic
3. **Outer Wrapper Classes**: One per command, extends `CodeAugmentedCommand`
   - Wraps inner command instance
   - Implements `handle_cli()` class method
   - Adds AI validation with heuristics
4. **CLI Entry Point**: `main()` function with command handlers
   - Registers all commands in handler dictionary
   - Maps command names to wrapper's `handle_cli()` method

## Test-Driven Development Workflow

**CRITICAL**: All implementation must follow BDD TDD workflow using the BDD behavior commands: **Domain Models → Domain Scaffold → Build Test Signatures → Write Tests → Write Code**

### Phase -1: Domain Models (DDD Analysis)

**Purpose**: Generate domain structure and interaction models that will be used by BDD scaffold command  
**Location**: All domain model files go in `behaviors/stories/docs/` folder  
**DDD Commands**: `/ddd-structure` and `/ddd-interaction`

**Process**:
1. **Generate Domain Structure**:
   - **Generate structure**: Run `/ddd-structure stories_runner.py` (or `/ddd-structure-generate stories_runner.py`)
     - Analyzes `stories_runner.py` (or other source files) to extract domain structure
     - Generates hierarchical domain map following DDD principles (Sections 1-10)
     - **Output location**: `behaviors/stories/docs/stories_runner-domain-map.txt`
   - **User reviews and edits** domain map file as needed
   - **Validate structure**: Run `/ddd-structure-validate behaviors/stories/docs/stories_runner-domain-map.txt` (or `/ddd-structure stories_runner.py` again)
     - Validates domain map against DDD principles (Sections 1-10)
   - **Fix violations** and re-validate until structure passes

2. **Generate Domain Interactions**:
   - **Generate interactions**: Run `/ddd-interaction stories_runner.py` (or `/ddd-interaction-generate stories_runner.py`)
     - Reads domain map file (`stories_runner-domain-map.txt`) from same directory
     - Analyzes source code for business flows and interactions
     - Documents transformations, lookups, and business rules
     - Maintains domain-level abstraction (no implementation details)
     - **Output location**: `behaviors/stories/docs/stories_runner-domain-interactions.txt`
   - **User reviews and edits** interactions file as needed
   - **Validate interactions**: Run `/ddd-interaction-validate behaviors/stories/docs/stories_runner-domain-interactions.txt` (or `/ddd-interaction stories_runner.py` again)
     - Validates interactions against DDD principles (Section 11)
   - **Fix violations** and re-validate until interactions pass

3. **Proceed to Phase 0** when both domain models are generated and validated

**Note**: The BDD scaffold command will discover these domain model files (`*domain-map*.txt`, `*domain-interactions*.txt`) in the `docs` folder and use them to generate the test scaffold.

### Phase 0: Domain Scaffold
- **Purpose**: Create domain scaffold representing what we want to build
- **File**: `behaviors/stories/docs/stories_runner_test-hierarchy.txt` (or `stories_runner_test.scaffold.txt`)
- **BDD Command**: `/bdd-scaffold`
- **Process**:
  1. **Generate scaffold**: Run `/bdd-scaffold stories_runner_test.py` (or `/bdd-scaffold-generate stories_runner_test.py`)
     - Command discovers domain maps (`*domain-map*.txt`, `*interaction-map*.txt`, `*domain-interactions*.txt`) in `behaviors/stories/docs/` folder
     - Uses `stories_runner-domain-map.txt` and `stories_runner-domain-interactions.txt` from Phase -1
     - Creates plain English hierarchy file: `behaviors/stories/docs/stories_runner_test-hierarchy.txt` (or `stories_runner_test.scaffold.txt`)
     - Focus on **what** the command should do, not how
     - Include describe blocks for each command class (behavioral descriptions)
     - Include tests for generation, validation, execution behaviors
     - Include tests for prompting questions integration
  2. **User reviews and edits** scaffold file as needed
  3. **Validate scaffold**: Run `/bdd-scaffold-validate stories_runner_test.py` (or `/bdd-scaffold stories_runner_test.py` again)
     - Validates domain map alignment (if domain map found)
     - Validates plain English only (no code syntax)
     - Validates BDD principles (Sections 1, 2, 7)
  4. **Fix violations** and re-validate until scaffold passes
  5. **Proceed to Phase 1** when scaffold validation passes

### Phase 1: Build Test Signatures
- **Purpose**: Convert scaffold to test code structure with empty test bodies
- **File**: `behaviors/stories/stories_runner_test.py`
- **BDD Command**: `/bdd-signature`
- **Process**:
  1. **Generate signatures**: Run `/bdd-signature stories_runner_test.py mamba` (or `/bdd-signature-generate stories_runner_test.py mamba`)
     - Command discovers scaffold file (`stories_runner_test-hierarchy.txt`)
     - Converts plain English scaffold to Mamba test syntax
     - Creates/updates test file with empty test bodies marked `# BDD: SIGNATURE`
     - Uses incremental approach (~18 describe blocks per iteration)
  2. **User reviews and edits** test signatures as needed
  3. **Validate signatures**: Run `/bdd-signature-validate stories_runner_test.py mamba` (or `/bdd-signature stories_runner_test.py mamba` again)
     - Validates scaffold alignment (if scaffold found)
     - Validates proper framework syntax (Mamba)
     - Validates base BDD principles (Sections 1, 2)
  4. **Fix violations** and re-validate until signatures pass
  5. **Continue iteration** if more signatures needed (incremental approach)
  6. **Proceed to Phase 2** when all signatures complete and validation passes

### Phase 2: Write Tests (RED)
- **Purpose**: Implement test bodies with Arrange-Act-Assert logic (tests should fail)
- **BDD Command**: `/bdd-test`
- **Process**:
  1. **Generate tests**: Run `/bdd-test stories_runner_test.py mamba` (or `/bdd-test-generate stories_runner_test.py mamba`)
     - Command finds signatures with `# BDD: SIGNATURE` markers
     - Implements test bodies following BDD patterns (Arrange-Act-Assert)
     - Uses incremental approach (~18 describe blocks per iteration)
     - **Mocking Strategy**: Mock ONLY file I/O operations (Path.read_text, Path.write_text, Path.exists, etc.)
     - **DO NOT mock**: Internal classes (BaseRule, Command, etc.) - use real instances
     - Test observable behavior (prompts returned, files created), not internal implementation
     - Use helper functions for common setup
     - Move duplicate Arrange code to `before.each`
  2. **User reviews and edits** test implementations as needed
  3. **Validate tests**: Run `/bdd-test-validate stories_runner_test.py mamba` (or `/bdd-test stories_runner_test.py mamba` again)
     - Validates implementation completeness (all signatures implemented)
     - Validates test structure quality (Arrange-Act-Assert, proper mocking)
     - Validates base BDD principles (Sections 1, 2, 3, 8)
  4. **Fix violations** and re-validate until tests pass validation
  5. **Verify tests fail** as expected (RED state - tests should fail because production code doesn't exist yet)
  6. **Continue iteration** if more tests needed (incremental approach)
  7. **Proceed to Phase 3** when all tests complete, validation passes, and tests fail as expected

### Phase 3: Write Code (GREEN)
- **Purpose**: Implement command files and runners to make tests pass
- **BDD Command**: `/bdd-code`
- **Process**:
  1. **Generate code**: Run `/bdd-code stories_runner_test.py mamba` (or `/bdd-code-generate stories_runner_test.py mamba`)
     - Command identifies failing tests (tests calling non-existent production code)
     - Implements minimal code to make tests pass
     - Implements command classes in `stories_runner.py`
     - Implements wrapper classes
     - Adds CLI handlers in `main()` function
     - **Apply Clean Code Principles** (run `/clean-code-validate` early and often):
     - Use parameter objects (dataclasses) instead of many parameters
     - Decompose large methods into smaller private methods
     - Use guard clauses to reduce nesting
     - Maximize reuse of base classes
  2. **User reviews and edits** production code as needed
  3. **Validate code**: Run `/bdd-code-validate stories_runner_test.py mamba` (or `/bdd-code stories_runner_test.py mamba` again)
     - **Primary Check**: Tests pass (run tests and verify)
     - **Secondary Check**: Code minimalism (no extra features, simple structures)
     - **Tertiary Check**: No regressions (all tests still pass)
  4. **Fix violations** and re-validate until code passes validation
  5. **Run tests** until all pass (GREEN state)
  6. **Continue iteration** if more failing tests remain
  7. **Workflow complete** when all tests pass and validation passes (refactoring happens through validation at every phase)

## Implementation Order

1. Extract PowerPoint content (DONE - saved to `docs/story-training-content.md`)
2. Analyze command structure (DONE - identified 8 commands)

---

## Common/Shared Implementation

### Phase 1: Common Runner Enhancement
3. **Add Prompting Questions concept to common_command_runner**
   - Add `prompting_questions` attribute to `Command` class
   - Add `check_prompting_questions()` method to `CodeAugmentedCommand` class
   - Integrate prompting check into `generate()` and `plan()` methods
   - Use AI to check if questions are answered in context
   - If not answered, generate prompts to ask user
   
   **✅ Verification Checkpoint**: Review PowerPoint content and verify prompting questions concept aligns with story writing workflow needs

### Phase 2: Rules Creation (BDD TDD Workflow)

**Step 1: Create Rule Infrastructure**
4. **Generate initial rule infrastructure**:
   - Run `/code-agent-rule-generate stories stories-rule "Story writing practices and standards for agile teams" base` to create initial rule files
   - This creates the basic rule structure files (`stories-rule-cmd.md`, `stories-rule-generate-cmd.md`, `stories-rule-validate-cmd.md`)
   - Validate: Run `/code-agent-rule-validate stories stories-rule`

**Step 2: Domain Models (DDD Analysis)**
5. **Generate domain models** for rule command:
   - **Generate domain structure**: Run `/ddd-structure stories_runner.py` (or `/ddd-structure-generate stories_runner.py`)
     - Analyzes `stories_runner.py` to extract domain structure
     - **Output location**: `behaviors/stories/docs/stories_runner-domain-map.txt`
   - **User reviews and edits** domain map file as needed
   - **Validate structure**: Run `/ddd-structure-validate behaviors/stories/docs/stories_runner-domain-map.txt`
   - **Fix violations** and re-validate until structure passes
   - **Generate domain interactions**: Run `/ddd-interaction stories_runner.py` (or `/ddd-interaction-generate stories_runner.py`)
     - Reads domain map from `behaviors/stories/docs/stories_runner-domain-map.txt`
     - Analyzes source code for business flows
     - **Output location**: `behaviors/stories/docs/stories_runner-domain-interactions.txt`
   - **User reviews and edits** interactions file as needed
   - **Validate interactions**: Run `/ddd-interaction-validate behaviors/stories/docs/stories_runner-domain-interactions.txt`
   - **Fix violations** and re-validate until interactions pass

**Step 3: Domain Scaffold (BDD Phase 0)**
6. **Create domain scaffold** for rule command tests:
   - **Generate scaffold**: Run `/bdd-scaffold stories_runner_test.py` (or `/bdd-scaffold-generate stories_runner_test.py`)
     - Command discovers domain maps in `behaviors/stories/docs/` folder (`stories_runner-domain-map.txt`, `stories_runner-domain-interactions.txt`)
     - Creates/extends `behaviors/stories/docs/stories_runner_test-hierarchy.txt`
   - Add describe blocks for `RuleCommand` and `CodeAugmentedRuleCommand`
   - Focus on behavioral descriptions (what the rule command should do)
   - Include tests for rule generation, validation, and execution
   - **User reviews and edits** scaffold file as needed
   - **Validate scaffold**: Run `/bdd-scaffold-validate stories_runner_test.py` (or `/bdd-scaffold stories_runner_test.py` again)
   - **Fix violations** and re-validate until scaffold passes

**Step 4: Build Test Signatures (BDD Phase 1)**
7. **Convert scaffold to signatures**:
   - **Generate signatures**: Run `/bdd-signature stories_runner_test.py mamba` (or `/bdd-signature-generate stories_runner_test.py mamba`)
     - Converts scaffold to Mamba test syntax in `stories_runner_test.py`
   - Empty test bodies marked `# BDD: SIGNATURE`
   - **User reviews and edits** test signatures as needed
   - **Validate signatures**: Run `/bdd-signature-validate stories_runner_test.py mamba` (or `/bdd-signature stories_runner_test.py mamba` again)
   - **Fix violations** and re-validate until signatures pass

**Step 5: Write Tests (BDD Phase 2 - RED)**
8. **Implement tests**:
   - **Generate tests**: Run `/bdd-test stories_runner_test.py mamba` (or `/bdd-test-generate stories_runner_test.py mamba`)
     - Implements test bodies with Arrange-Act-Assert logic
   - Mock ONLY file I/O operations
   - Test observable behavior (prompts returned, rule file structure)
   - **User reviews and edits** test implementations as needed
   - **Validate tests**: Run `/bdd-test-validate stories_runner_test.py mamba` (or `/bdd-test stories_runner_test.py mamba` again)
   - **Verify tests fail** as expected (RED state - tests should fail because rule command doesn't exist yet)
   - **Fix violations** and re-validate until tests pass validation

**Step 6: Write Code (BDD Phase 3 - GREEN)**
9. **Create base rule file** (`stories-rule.mdc`) with proper structure:
   - **Frontmatter**: description, globs, alwaysApply
   - **When/then statement**: Context and behavior description
   - **Executing Commands section**: List commands that use this rule
   - **Conventions section**: Naming conventions, file locations, structural conventions
   - **5 major principle sections**:
     - Section 0: Universal principles (apply to all commands)
     - Section 0.5: All Phases principles (apply to commands across Story Shaping, Discovery, and Exploration)
     - Sections 1-3: Stage-specific principles with command applicability markers
   - Each principle marked with: ⚠️ **Universal**, ⚠️ **All Phases**, ⚠️ **Stage: [stage-name]**, or ⚠️ **Commands: [command-list]**
   - **Templates section** (if applicable): Templates used for generating files
   - **Commands section** (at end): Detailed list of commands that implement or use this rule
10. **Create rule command files** (rule/stories-rule-*.md):
   - `stories-rule-cmd.md` - Main command file
   - `stories-rule-generate-cmd.md` - Generate delegate
   - `stories-rule-validate-cmd.md` - Validate delegate
11. **Implement rule command classes** in `stories_runner.py`:
    - **Generate code**: Run `/bdd-code stories_runner_test.py mamba` (or `/bdd-code-generate stories_runner_test.py mamba`)
      - Implements `RuleCommand` class (inner command)
      - Implements `CodeAugmentedRuleCommand` class (outer wrapper)
      - Adds CLI handlers in `main()` function
      - Applies clean code principles (parameter objects, method decomposition, guard clauses)
    - **User reviews and edits** production code as needed
    - **Validate code**: Run `/bdd-code-validate stories_runner_test.py mamba` (or `/bdd-code stories_runner_test.py mamba` again)
      - **Primary Check**: Tests pass (run tests and verify)
      - **Secondary Check**: Code minimalism (no extra features, simple structures)
      - **Tertiary Check**: No regressions (all tests still pass)
    - **Run tests** until all pass (GREEN state)
    - **Fix violations** and re-validate until code passes validation
   
   **✅ Verification Checkpoint**: 
   - Review PowerPoint content (`docs/story-training-content.md`)
   - Verify all principles from PowerPoint are captured in rule file
   - Verify principle sections align with PowerPoint structure (Story Shaping, Discovery, Story Exploration)
   - Verify DO/DON'T examples match PowerPoint guidance
   - Verify command applicability markers are correct
   - Verify rule file follows required structure (frontmatter, When/then, Conventions, Principles, Commands)

---

## Story Shaping Implementation

**Commands**: `story-shape`, `story-market-increments`  
**Stage**: Story Shaping  
**Templates**: `story-map-template.md`, `market-increments-template.md`, `market-increment-template.md`, `epic-template.md`

### Story Shaping: Command Creation (BDD TDD Workflow)

**For each Story Shaping command (`story-shape`, `story-market-increments`), follow BDD TDD workflow:**

**Step 1: Create Command Infrastructure**
- **story-shape**: Run `/code-agent-command-generate stories story-shape "Create story map shell and elaborate/extrapolate scope" "story"`
- **story-market-increments**: Run `/code-agent-command-generate stories story-market-increments "Identify marketable increments of value" "story"`
- **Validate**: Run `/code-agent-command-validate stories <command-name>`

**Step 2: Domain Models (DDD Analysis)**
- **Generate domain structure**: Run `/ddd-structure stories_runner.py` (or `/ddd-structure-generate stories_runner.py`)
  - Analyzes `stories_runner.py` to extract domain structure
  - **Output location**: `behaviors/stories/docs/stories_runner-domain-map.txt`
- **User reviews and edits** domain map file as needed
- **Validate structure**: Run `/ddd-structure-validate behaviors/stories/docs/stories_runner-domain-map.txt`
- **Fix violations** and re-validate until structure passes
- **Generate domain interactions**: Run `/ddd-interaction stories_runner.py` (or `/ddd-interaction-generate stories_runner.py`)
  - Reads domain map from `behaviors/stories/docs/stories_runner-domain-map.txt`
  - Analyzes source code for business flows
  - **Output location**: `behaviors/stories/docs/stories_runner-domain-interactions.txt`
- **User reviews and edits** interactions file as needed
- **Validate interactions**: Run `/ddd-interaction-validate behaviors/stories/docs/stories_runner-domain-interactions.txt`
- **Fix violations** and re-validate until interactions pass

**Step 3: Domain Scaffold (BDD Phase 0)**
- **Generate scaffold**: Run `/bdd-scaffold stories_runner_test.py` (or `/bdd-scaffold-generate stories_runner_test.py`)
  - Command discovers domain maps in `behaviors/stories/docs/` folder (`stories_runner-domain-map.txt`, `stories_runner-domain-interactions.txt`)
  - Extends `behaviors/stories/docs/stories_runner_test-hierarchy.txt`
   - Add describe blocks for `<CommandName>Command` and `CodeAugmented<CommandName>Command`
   - Focus on behavioral descriptions (what the command should do)
   - Include tests for generation, validation, execution, and prompting questions integration
- **User reviews and edits** scaffold file as needed
- **Validate scaffold**: Run `/bdd-scaffold-validate stories_runner_test.py` (or `/bdd-scaffold stories_runner_test.py` again)
- **Fix violations** and re-validate until scaffold passes

**Step 4: Build Test Signatures (BDD Phase 1)**
- **Generate signatures**: Run `/bdd-signature stories_runner_test.py mamba` (or `/bdd-signature-generate stories_runner_test.py mamba`)
  - Converts scaffold to Mamba test syntax in `stories_runner_test.py`
   - Empty test bodies marked `# BDD: SIGNATURE`
- **User reviews and edits** test signatures as needed
- **Validate signatures**: Run `/bdd-signature-validate stories_runner_test.py mamba` (or `/bdd-signature stories_runner_test.py mamba` again)
- **Fix violations** and re-validate until signatures pass

**Step 5: Write Tests (BDD Phase 2 - RED)**
- **Generate tests**: Run `/bdd-test stories_runner_test.py mamba` (or `/bdd-test-generate stories_runner_test.py mamba`)
  - Implements test bodies with Arrange-Act-Assert logic
  - Mock ONLY file I/O operations
   - Test observable behavior (prompts returned, files created, prompting questions checked)
- **User reviews and edits** test implementations as needed
- **Validate tests**: Run `/bdd-test-validate stories_runner_test.py mamba` (or `/bdd-test stories_runner_test.py mamba` again)
- **Verify tests fail** as expected (RED state - tests should fail because command classes don't exist yet)
- **Fix violations** and re-validate until tests pass validation

**Step 6: Write Code (BDD Phase 3 - GREEN)**
- **Generate code**: Run `/bdd-code stories_runner_test.py mamba` (or `/bdd-code-generate stories_runner_test.py mamba`)
  - Creates command files (`<command-name>-cmd.md`, `-generate-cmd.md`, `-validate-cmd.md`)
  - Implements command classes in `stories_runner.py`
  - Applies clean code principles
- **User reviews and edits** production code as needed
- **Validate code**: Run `/bdd-code-validate stories_runner_test.py mamba` (or `/bdd-code stories_runner_test.py mamba` again)
  - **Primary Check**: Tests pass (run tests and verify)
  - **Secondary Check**: Code minimalism (no extra features, simple structures)
  - **Tertiary Check**: No regressions (all tests still pass)
- **Run tests** until all pass (GREEN state)
- **Fix violations** and re-validate until code passes validation
   
   **✅ Verification Checkpoint**: 
- Review PowerPoint Story Shaping content
- Verify commands align with Story Shaping activities
- Verify prompting questions are appropriate
   - Verify command workflows match PowerPoint guidance

### Story Shaping: Heuristics Implementation (BDD TDD Workflow)

**For each Story Shaping command, implement heuristics:**

**Step 1: Domain Models (DDD Analysis)**
- **Generate domain structure**: Run `/ddd-structure stories_runner.py` (or `/ddd-structure-generate stories_runner.py`)
  - Analyzes `stories_runner.py` to extract domain structure
  - **Output location**: `behaviors/stories/docs/stories_runner-domain-map.txt`
- **User reviews and edits** domain map file as needed
- **Validate structure**: Run `/ddd-structure-validate behaviors/stories/docs/stories_runner-domain-map.txt`
- **Fix violations** and re-validate until structure passes
- **Generate domain interactions**: Run `/ddd-interaction stories_runner.py` (or `/ddd-interaction-generate stories_runner.py`)
  - Reads domain map from `behaviors/stories/docs/stories_runner-domain-map.txt`
  - Analyzes source code for business flows
  - **Output location**: `behaviors/stories/docs/stories_runner-domain-interactions.txt`
- **User reviews and edits** interactions file as needed
- **Validate interactions**: Run `/ddd-interaction-validate behaviors/stories/docs/stories_runner-domain-interactions.txt`
- **Fix violations** and re-validate until interactions pass

**Step 2: Domain Scaffold (BDD Phase 0)**
- **Generate scaffold**: Run `/bdd-scaffold stories_runner_test.py` (or `/bdd-scaffold-generate stories_runner_test.py`)
  - Command discovers domain maps in `behaviors/stories/docs/` folder (`stories_runner-domain-map.txt`, `stories_runner-domain-interactions.txt`)
   - Add describe blocks for `<CommandName>Heuristic` classes
   - Focus on behavioral descriptions (what the heuristic should validate)
- **User reviews and edits** scaffold file as needed
- **Validate scaffold**: Run `/bdd-scaffold-validate stories_runner_test.py` (or `/bdd-scaffold stories_runner_test.py` again)
- **Fix violations** and re-validate until scaffold passes

**Step 3: Build Test Signatures (BDD Phase 1)**
- **Generate signatures**: Run `/bdd-signature stories_runner_test.py mamba` (or `/bdd-signature-generate stories_runner_test.py mamba`)
  - Converts to Mamba test syntax in `stories_runner_test.py`
  - Empty test bodies marked `# BDD: SIGNATURE`
- **User reviews and edits** test signatures as needed
- **Validate signatures**: Run `/bdd-signature-validate stories_runner_test.py mamba` (or `/bdd-signature stories_runner_test.py mamba` again)
- **Fix violations** and re-validate until signatures pass

**Step 4: Write Tests (BDD Phase 2 - RED)**
- **Generate tests**: Run `/bdd-test stories_runner_test.py mamba` (or `/bdd-test-generate stories_runner_test.py mamba`)
  - Implements test bodies for heuristic validation
  - Tests that heuristics catch violations correctly
- **User reviews and edits** test implementations as needed
- **Validate tests**: Run `/bdd-test-validate stories_runner_test.py mamba` (or `/bdd-test stories_runner_test.py mamba` again)
- **Verify tests fail** as expected (RED state - tests should fail because heuristics don't exist yet)
- **Fix violations** and re-validate until tests pass validation

**Step 5: Write Code (BDD Phase 3 - GREEN)**
- **Generate code**: Run `/bdd-code stories_runner_test.py mamba` (or `/bdd-code-generate stories_runner_test.py mamba`)
    - **StoryShapeHeuristic**: Validates story shape command
      - Checks epic/feature/story hierarchy structure
      - Validates user/system focus (not tasks)
      - Checks business language usage
      - Validates scope extrapolation and story sizing
    - **StoryMarketIncrementsHeuristic**: Validates market increments command
      - Validates marketable increment identification
      - Checks increment prioritization
      - Validates relative sizing approach
  - Implements heuristic mapping in wrapper classes
- **User reviews and edits** production code as needed
- **Validate code**: Run `/bdd-code-validate stories_runner_test.py mamba` (or `/bdd-code stories_runner_test.py mamba` again)
  - **Primary Check**: Tests pass (run tests and verify)
  - **Secondary Check**: Code minimalism (no extra features, simple structures)
  - **Tertiary Check**: No regressions (all tests still pass)
- **Run tests** until all pass (GREEN state)
- **Fix violations** and re-validate until code passes validation

**✅ Verification Checkpoint**: 
- Verify heuristics check for all Story Shaping validation criteria
- Verify heuristics align with Story Shaping principles
- Verify heuristics catch violations of PowerPoint guidance

### Story Shaping: Templates Creation

- **story-map-template.md**: Complete hierarchy of actor personas, epics, features, and stories
- **market-increments-template.md**: Story map broken down by market increment
- **market-increment-template.md**: Single market increment with stories and acceptance criteria
- **epic-template.md**: Epic slice view showing features with their stories

**✅ Verification Checkpoint**: 
- Verify templates match PowerPoint Story Shaping guidance
- Verify templates include all required elements
- Verify templates align with Story Shaping principles

---

## Discovery Implementation

**Commands**: `story-discovery`  
**Stage**: Discovery  
**Templates**: `feature-template.md` (updated during discovery)

### Discovery: Command Creation (BDD TDD Workflow)

**For Discovery command (`story-discovery`), follow BDD TDD workflow:**

**Step 1: Create Command Infrastructure**
- Run `/code-agent-command-generate stories story-discovery "Refine increments, apply practices, groom stories" "story"`
- Validate: Run `/code-agent-command-validate stories story-discovery`

**Step 2-6: Follow BDD TDD Workflow** (Domain Models → Domain Scaffold → Build Test Signatures → Write Tests → Write Code)
- **Step 2**: Domain Models - Run `/ddd-structure stories_runner.py` (output to `behaviors/stories/docs/stories_runner-domain-map.txt`), then `/ddd-interaction stories_runner.py` (output to `behaviors/stories/docs/stories_runner-domain-interactions.txt`)
- **Step 3**: Domain Scaffold - Run `/bdd-scaffold stories_runner_test.py`, validate with `/bdd-scaffold-validate stories_runner_test.py`
- **Step 4**: Build Test Signatures - Run `/bdd-signature stories_runner_test.py mamba`, validate with `/bdd-signature-validate stories_runner_test.py mamba`
- **Step 5**: Write Tests - Run `/bdd-test stories_runner_test.py mamba`, validate with `/bdd-test-validate stories_runner_test.py mamba`
- **Step 6**: Write Code - Run `/bdd-code stories_runner_test.py mamba`, validate with `/bdd-code-validate stories_runner_test.py mamba`
- Focus on Discovery-specific activities (increment refinement, story mapping practices, story grooming)

**✅ Verification Checkpoint**: 
- Review PowerPoint Discovery content
- Verify command aligns with Discovery activities
- Verify prompting questions are appropriate
- Verify command workflows match PowerPoint guidance

### Discovery: Heuristics Implementation (BDD TDD Workflow)

**For Discovery command, implement heuristics:**

**Step 1-5: Follow BDD TDD Workflow** (Domain Models → Domain Scaffold → Build Test Signatures → Write Tests → Write Code)
- **Step 1**: Domain Models - Run `/ddd-structure stories_runner.py` (output to `behaviors/stories/docs/stories_runner-domain-map.txt`), then `/ddd-interaction stories_runner.py` (output to `behaviors/stories/docs/stories_runner-domain-interactions.txt`)
- **Step 2**: Domain Scaffold - Run `/bdd-scaffold stories_runner_test.py`, validate with `/bdd-scaffold-validate stories_runner_test.py`
- **Step 3**: Build Test Signatures - Run `/bdd-signature stories_runner_test.py mamba`, validate with `/bdd-signature-validate stories_runner_test.py mamba`
- **Step 4**: Write Tests - Run `/bdd-test stories_runner_test.py mamba`, validate with `/bdd-test-validate stories_runner_test.py mamba`
- **Step 5**: Write Code - Run `/bdd-code stories_runner_test.py mamba`, validate with `/bdd-code-validate stories_runner_test.py mamba`
  - **StoryDiscoveryHeuristic**: Validates discovery command
      - Validates increment refinement and story map updates
      - Checks story mapping practices (via principles)
      - Validates story grooming practices
    - Validates story mapping estimation and counting

**✅ Verification Checkpoint**: 
- Verify heuristics check for all Discovery validation criteria
- Verify heuristics align with Discovery principles
- Verify heuristics catch violations of PowerPoint guidance

### Discovery: Templates Creation

- **feature-template.md**: Feature view with stories and their acceptance criteria (updated during discovery)

**✅ Verification Checkpoint**: 
- Verify templates match PowerPoint Discovery guidance
- Verify templates include all required elements
- Verify templates align with Discovery principles

---

## Story Exploration Implementation

**Commands**: `story-explore`, `story-specification-scenarios`, `story-specification-examples`  
**Stage**: Story Exploration  
**Templates**: `story-template.md`, `acceptance-criteria-template.md`

### Story Exploration: Command Creation (BDD TDD Workflow)

**For each Story Exploration command (`story-explore`, `story-specification-scenarios`, `story-specification-examples`), follow BDD TDD workflow:**

**Step 1: Create Command Infrastructure**
- **story-explore**: Run `/code-agent-command-generate stories story-explore "Write acceptance criteria, refine map, define system stories" "story"`
- **story-specification-scenarios**: Run `/code-agent-command-generate stories story-specification-scenarios "Create scenario-based specifications" "story"`
- **story-specification-examples**: Run `/code-agent-command-generate stories story-specification-examples "Create example-based specifications" "story"`
- Validate: Run `/code-agent-command-validate stories <command-name>`

**Step 2-6: Follow BDD TDD Workflow** (Domain Models → Domain Scaffold → Build Test Signatures → Write Tests → Write Code)
- **Step 2**: Domain Models - Run `/ddd-structure stories_runner.py` (output to `behaviors/stories/docs/stories_runner-domain-map.txt`), then `/ddd-interaction stories_runner.py` (output to `behaviors/stories/docs/stories_runner-domain-interactions.txt`)
- **Step 3**: Domain Scaffold - Run `/bdd-scaffold stories_runner_test.py`, validate with `/bdd-scaffold-validate stories_runner_test.py`
- **Step 4**: Build Test Signatures - Run `/bdd-signature stories_runner_test.py mamba`, validate with `/bdd-signature-validate stories_runner_test.py mamba`
- **Step 5**: Write Tests - Run `/bdd-test stories_runner_test.py mamba`, validate with `/bdd-test-validate stories_runner_test.py mamba`
- **Step 6**: Write Code - Run `/bdd-code stories_runner_test.py mamba`, validate with `/bdd-code-validate stories_runner_test.py mamba`
- Focus on Story Exploration-specific activities (acceptance criteria, story specification, system stories)

**✅ Verification Checkpoint**: 
- Review PowerPoint Story Exploration content
- Verify commands align with Story Exploration activities
- Verify prompting questions are appropriate
- Verify command workflows match PowerPoint guidance

### Story Exploration: Heuristics Implementation (BDD TDD Workflow)

**For each Story Exploration command, implement heuristics:**

**Step 1-5: Follow BDD TDD Workflow** (Domain Models → Domain Scaffold → Build Test Signatures → Write Tests → Write Code)
- **Step 1**: Domain Models - Run `/ddd-structure stories_runner.py` (output to `behaviors/stories/docs/stories_runner-domain-map.txt`), then `/ddd-interaction stories_runner.py` (output to `behaviors/stories/docs/stories_runner-domain-interactions.txt`)
- **Step 2**: Domain Scaffold - Run `/bdd-scaffold stories_runner_test.py`, validate with `/bdd-scaffold-validate stories_runner_test.py`
- **Step 3**: Build Test Signatures - Run `/bdd-signature stories_runner_test.py mamba`, validate with `/bdd-signature-validate stories_runner_test.py mamba`
- **Step 4**: Write Tests - Run `/bdd-test stories_runner_test.py mamba`, validate with `/bdd-test-validate stories_runner_test.py mamba`
- **Step 5**: Write Code - Run `/bdd-code stories_runner_test.py mamba`, validate with `/bdd-code-validate stories_runner_test.py mamba`
  - **StoryExploreHeuristic**: Validates explore command
      - Validates acceptance criteria presence, behavior form, testability
      - Checks story map refinement during exploration
      - Validates system-level story definition
    - **StorySpecificationScenariosHeuristic**: Validates specification scenarios command
      - Validates scenario completeness
      - Checks scenario structure and flow
    - **StorySpecificationExamplesHeuristic**: Validates specification examples command
      - Validates example completeness
      - Checks example clarity and coverage
   
   **✅ Verification Checkpoint**: 
- Verify heuristics check for all Story Exploration validation criteria
- Verify heuristics align with Story Exploration principles
   - Verify heuristics catch violations of PowerPoint guidance

### Story Exploration: Templates Creation

- **story-template.md**: Individual story specification (one document per story)
- **acceptance-criteria-template.md**: Acceptance criteria format (stored in feature documents)
   
   **✅ Verification Checkpoint**: 
- Verify templates match PowerPoint Story Exploration guidance
- Verify templates include all required elements
- Verify templates align with Story Exploration principles

---

## Cross-Stage Implementation

**Commands**: `story-discovery-explore`, `story-synchronize`  
**Stages**: Combines Discovery and Exploration, applies to all stages

### Cross-Stage: Command Creation (BDD TDD Workflow)

**For cross-stage commands, follow BDD TDD workflow:**

**story-discovery-explore**: Combined discovery and exploration workflow
- Run `/code-agent-command-generate stories story-discovery-explore "Combined discovery and exploration workflow" "story"`

**story-synchronize**: Synchronize all artifacts (decomposition, increments, folders, documents)
- Run `/code-agent-command-generate stories story-synchronize "Synchronize all artifacts" "story"`

**Step 2-6: Follow BDD TDD Workflow** (Domain Models → Domain Scaffold → Build Test Signatures → Write Tests → Write Code)
- **Step 2**: Domain Models - Run `/ddd-structure stories_runner.py` (output to `behaviors/stories/docs/stories_runner-domain-map.txt`), then `/ddd-interaction stories_runner.py` (output to `behaviors/stories/docs/stories_runner-domain-interactions.txt`)
- **Step 3**: Domain Scaffold - Run `/bdd-scaffold stories_runner_test.py`, validate with `/bdd-scaffold-validate stories_runner_test.py`
- **Step 4**: Build Test Signatures - Run `/bdd-signature stories_runner_test.py mamba`, validate with `/bdd-signature-validate stories_runner_test.py mamba`
- **Step 5**: Write Tests - Run `/bdd-test stories_runner_test.py mamba`, validate with `/bdd-test-validate stories_runner_test.py mamba`
- **Step 6**: Write Code - Run `/bdd-code stories_runner_test.py mamba`, validate with `/bdd-code-validate stories_runner_test.py mamba`
- Focus on cross-stage activities

**✅ Verification Checkpoint**: 
- Verify commands support cross-stage workflows
- Verify prompting questions are appropriate
- Verify command workflows match PowerPoint guidance

### Cross-Stage: Heuristics Implementation (BDD TDD Workflow)

**For cross-stage commands, implement heuristics:**

**Step 1-5: Follow BDD TDD Workflow** (Domain Models → Domain Scaffold → Build Test Signatures → Write Tests → Write Code)
- **Step 1**: Domain Models - Run `/ddd-structure stories_runner.py` (output to `behaviors/stories/docs/stories_runner-domain-map.txt`), then `/ddd-interaction stories_runner.py` (output to `behaviors/stories/docs/stories_runner-domain-interactions.txt`)
- **Step 2**: Domain Scaffold - Run `/bdd-scaffold stories_runner_test.py`, validate with `/bdd-scaffold-validate stories_runner_test.py`
- **Step 3**: Build Test Signatures - Run `/bdd-signature stories_runner_test.py mamba`, validate with `/bdd-signature-validate stories_runner_test.py mamba`
- **Step 4**: Write Tests - Run `/bdd-test stories_runner_test.py mamba`, validate with `/bdd-test-validate stories_runner_test.py mamba`
- **Step 5**: Write Code - Run `/bdd-code stories_runner_test.py mamba`, validate with `/bdd-code-validate stories_runner_test.py mamba`
  - **StoryDiscoveryExploreHeuristic**: Combines discovery and exploration heuristics
  - **StorySynchronizeHeuristic**: Validates synchronization of artifacts

**✅ Verification Checkpoint**: 
- Verify heuristics check for all cross-stage validation criteria
- Verify heuristics align with relevant principles

---

## Final Integration & Configuration

### Phase 6: Runner Integration (Final)

**Note**: Runner implementation happens during TDD GREEN phase for each command. This phase is for final integration and validation.

- Each command class extends `Command` (standard pattern)
- Define `prompting_questions` as class attribute or load from command file
- Standard `generate()` and `validate()` methods
- CLI wrapper uses `CodeAugmentedCommand` (standard pattern)
- Prompting questions check runs automatically before generate/plan
- All commands registered in `main()` function

**✅ Verification Checkpoint**: 
- Verify command classes implement correct workflow logic
- Verify prompting questions integration works correctly
- Verify CLI entry points match command structure
- Verify all 8 commands are properly integrated

### Phase 7: Configuration & Testing

- Update configuration files (`behavior.json`, `code-agent-index.json`, `feature-outline.md`)
- Test all commands, prompting questions, heuristics, and workflows
- Test end-to-end workflows for each stage:
  - Story Shaping workflow (story-shape → story-market-increments)
  - Discovery workflow (story-discovery)
  - Story Exploration workflow (story-explore → story-specification-scenarios → story-specification-examples)
  - Cross-stage workflows (story-discovery-explore, story-synchronize)
   
   **✅ Final Verification Checkpoint**: 
   - Review PowerPoint content (`docs/story-training-content.md`)
   - Verify complete implementation aligns with PowerPoint training material
   - Verify all stages from PowerPoint are properly supported
   - Verify all practices and principles from PowerPoint are enforced
   - Verify end-to-end workflow matches PowerPoint guidance
- Verify stage-specific implementations are complete

## Files to Create

### Rules:
- `behaviors/stories/stories-rule.mdc`
- `behaviors/stories/rule/stories-rule-cmd.md`
- `behaviors/stories/rule/stories-rule-generate-cmd.md`
- `behaviors/stories/rule/stories-rule-validate-cmd.md`

### Commands (7 commands × 3 files = 21 files):
- `behaviors/stories/shape/story-shape-cmd.md` (+ generate, validate)
  - Command name: `/story-shape`
- `behaviors/stories/market-increments/story-market-increments-cmd.md` (+ generate, validate)
  - Command name: `/story-market-increments`
- `behaviors/stories/discovery/story-discovery-cmd.md` (+ generate, validate)
  - Command name: `/story-discovery`
- `behaviors/stories/explore/story-explore-cmd.md` (+ generate, validate)
  - Command name: `/story-explore`
- `behaviors/stories/specification-scenarios/story-specification-scenarios-cmd.md` (+ generate, validate)
  - Command name: `/story-specification-scenarios`
- `behaviors/stories/specification-examples/story-specification-examples-cmd.md` (+ generate, validate)
  - Command name: `/story-specification-examples`
- `behaviors/stories/discovery-explore/story-discovery-explore-cmd.md` (+ generate, validate)
  - Command name: `/story-discovery-explore`

### Runner:
- `behaviors/stories/stories_runner.py` (full implementation with 8 command classes: rule + 7 commands)
  - 7 command classes (one per command)
  - 7 heuristic classes (one per command)
  - Standard Command pattern (no OperationCommand decorator needed)

### Templates:
**Story-Specific Templates**:
- `behaviors/stories/map/story-map-template.md`
- `behaviors/stories/write/story-template.md`
- `behaviors/stories/acceptance/acceptance-criteria-template.md`

### Configuration:
- `behaviors/stories/behavior.json` (update)
- `behaviors/stories/code-agent-index.json` (create/update)
- `behaviors/stories/feature-outline.md` (update)

## Dependencies
- `common_command_runner` framework (needs enhancement: Prompting Questions concept)
- Existing code-agent patterns and templates
- PowerPoint content analysis (DONE)
- Command structure analysis (DONE - 7 commands identified)

## Verification Process

### Verification Checkpoints
At the end of each implementation phase, perform a verification checkpoint:

1. **Review Source Material**: Read `behaviors/stories/docs/story-training-content.md` (extracted PowerPoint content)
2. **Compare Implementation**: Check if created artifacts (rules, commands, heuristics, templates) align with PowerPoint guidance
3. **Identify Gaps**: Look for missing principles, practices, or guidance from PowerPoint
4. **Verify Completeness**: Ensure all stages, activities, and practices from PowerPoint are covered
5. **Check Alignment**: Verify that implementation matches the intent and structure of the PowerPoint training material

### Verification Questions for Each Checkpoint
- **Rules Checkpoint**: 
  - Are all principles from PowerPoint captured?
  - Are DO/DON'T examples from PowerPoint included?
  - Do principle sections match PowerPoint structure?
  
- **Commands Checkpoint**: 
  - Do commands cover all major activities from PowerPoint?
  - Are prompting questions appropriate for each command?
  - Do command workflows match PowerPoint guidance?
  
- **Heuristics Checkpoint**: 
  - Do heuristics validate all criteria mentioned in PowerPoint?
  - Are violations of PowerPoint guidance caught?
  - Do heuristics align with principles?
  
- **Templates Checkpoint**: 
  - Do templates match PowerPoint guidance on structure?
  - Are all required elements from PowerPoint included?
  - Do templates support PowerPoint workflows?

### Verification Workflow
1. **AI Agent Task**: "Review the PowerPoint content (`docs/story-training-content.md`) and verify that [current phase artifacts] align with the training material. Check for missing principles, practices, or guidance."
2. **Comparison**: Compare created artifacts against PowerPoint content
3. **Gap Analysis**: Identify any missing or misaligned content
4. **Correction**: Update artifacts to align with PowerPoint guidance
5. **Documentation**: Note any decisions or deviations from PowerPoint (if intentional)

## Complexity Analysis: Simplified Command Structure

**Complexity Level**: Low-Medium

**Why Simplified**:
- Using standard Command pattern (no decorator needed)
- Each command is self-contained
- No operation state tracking or ordering enforcement
- No heuristic filtering complexity
- Standard CodeAugmentedCommand wrapper pattern
- Each command has its own heuristic class

**Components Needed**:
1. **Command Classes**: 7 command classes extending Command
2. **Heuristic Classes**: 7 heuristic classes (one per command)
3. **CLI Wrappers**: 7 CodeAugmentedCommand wrappers
4. **CLI Entry Points**: Standard generate/validate/execute handlers

**Reusability**: Standard pattern - follows existing code-agent command structure

**Implementation Approach**:
- Create 7 command classes following standard Command pattern
- Define prompting questions for each command (command-specific context requirements)
- Create 7 heuristic classes for validation
- Create 7 CLI wrapper classes using CodeAugmentedCommand
- Add CLI entry points for each command
- Prompting questions check runs automatically before generate/plan via CodeAugmentedCommand
- No special decorators or operation handling needed

## Command Summary

### Commands (7 total):
1. **story-shape** - Create story map shell and elaborate/extrapolate scope
2. **story-market-increments** - Identify marketable increments of value
3. **story-discovery** - Refine increments, apply practices, groom stories
4. **story-explore** - Write acceptance criteria, refine map, define system stories
5. **story-specification-scenarios** - Create scenario-based specifications
6. **story-specification-examples** - Create example-based specifications
7. **story-discovery-explore** - Combined discovery and exploration workflow

**Heuristic Mapping**:
- Each command has its own heuristic class
- Heuristics validate command-specific content
- Standard CodeAugmentedCommand pattern for heuristic application

**Rule File Structure**:
- Rule file (`stories-rule.mdc`) marks each principle with command applicability
- Formats:
  - ⚠️ **Universal** - applies to all commands
  - ⚠️ **All Phases** - applies to commands across Story Shaping, Discovery, and Exploration
  - ⚠️ **Stage: [stage-name]** - applies to commands within a specific stage
  - ⚠️ **Commands: [command-list]** - applies to specific commands
- Helps AI focus on relevant principles when generating/validating for specific commands
- AI prioritizes: Universal → All Phases → Stage-specific → Command-specific

