# Domain Model Description: Build Bot

**File Name**: `build-bot-domain-model-description.md`
**Location**: `docs/stories/build-bot-domain-model-description.md`

## Solution Purpose
This document describes the domain model for Build Bot, capturing the key concepts, their responsibilities, and relationships.

---

## Domain Model Descriptions

### Base Bot

**Responsibilities:**
- Executes Actions (collaborates with: Workflow, Behavior, Action)
- Track activity (collaborates with: Behavior, Action)
- Route to behaviors and actions (collaborates with: Router, Trigger Words)
- Persist content (collaborates with: Content)
- Manage Project State (collaborates with: Project)
- Render

### Specific Bot

**Responsibilities:**
- Provide Behavior config (collaborates with: Bot Config, Behavior)
- Provide MCP config (collaborates with: MCP Config)
- Provide Renderers
- Provide Extractors
- Provide Synchronizer
- Provide Trigger Words

### Router

**Responsibilities:**
- Match trigger patterns (collaborates with: Trigger Words, Route)
- Route to MCP bot tool (collaborates with: Base Bot, Trigger Words)
- Route to behavior tool (collaborates with: Behavior, Trigger Words)
- Route to action tool (collaborates with: Action, Trigger Words)
- Forward to behavior (collaborates with: Behavior, Base Bot)
- Forward to action (collaborates with: Action, Behavior)
- Forward to current behavior and action (collaborates with: Behavior, Action, Base Bot)

### Workflow State

**Responsibilities:**
- Track current action (collaborates with: Action)
- Track completed actions (collaborates with: Action, Activity Log)
- Determine next action (collaborates with: Action, Behavior)
- Pause workflow (collaborates with: Human, AI Chat)
- Resume workflow (collaborates with: Human, AI Chat)

### Project

**Responsibilities:**
- Move project to working area (collaborates with: Working Directory)
- Save project in context (collaborates with: Working Directory, Workflow State)
- Update project area (collaborates with: Working Directory, Content)

### Behavior

**Responsibilities:**
- Perform Configured Actions (collaborates with: Actions)
- Invoke On Trigger Words (collaborates with: List)
- Inject Instructions (collaborates with: Text)
- Provide Guardrails (collaborates with: GuardRails)
- Provide Rules (collaborates with: Rule, Validation)
- Provide Content Specs (collaborates with: Content)

### Base Action

**Responsibilities:**
- Inject Instructions (collaborates with: Behavior)
- Load Relevant Content + Inject Into Instructions (collaborates with: Content)
- Save content changes (collaborates with: Content)

### Behavior Workflow

**Responsibilities:**
- Determine next Action (collaborates with: Behavior, Action, State)
- Track state (collaborates with: Behavior, Action, State)

### GatherContextAction

**Responsibilities:**
- Inject gather context instructions (collaborates with: Behavior, Guardrails, Required Clarifications)
- Inject questions and evidence (collaborates with: Behavior, Guardrails, Key Questions, Evidence)

### Guardrails

**Responsibilities:**
- Provide required context (collaborates with: Key Questions, Evidence)
- Guide planning decisions (collaborates with: Decision Criteria, Assumptions)
- Define recommended human activity (collaborates with: Human, Instructions)

### PlanningAction

**Responsibilities:**
- Inject planning instructions (collaborates with: Behavior, Guardrails, Planning)
- Inject decision criteria and assumptions (collaborates with: Behavior, Guardrails, Decision Criteria, Assumptions, Recommended Human Activity)

### BuildKnowledgeAction

**Responsibilities:**
- Inject knowledge graph template (collaborates with: Behavior, Content, Knowledge Graph Spec, Knowledge Graph)
- Inject builder instructions (collaborates with: Behavior, Content, Build Instructions)
- Save Knowledge graph (collaborates with: Behavior, Content, Knowledge Graph)

### Content

**Responsibilities:**
- Render outputs (collaborates with: Template, Renderer, Render Spec)
- Synchronize formats (collaborates with: Synchronizer, Extractor, Synchronizer Spec)
- Save knowledge graph (collaborates with: Knowledge Graph)
- Load rendered content (collaborates with: na)
- Present rendered content (collaborates with: na)

### RenderOutputAction

**Responsibilities:**
- Inject render output instructions (collaborates with: Behavior, Content, Render Spec, Renderer)
- Inject templates (collaborates with: Behavior, Content, Render Spec, Template)
- Inject transformers (collaborates with: Behavior, Content, Transformer)
- Load + inject structured content (collaborates with: Behavior, Content, Knowledge Graph)

### Renderer

**Responsibilities:**
- Render complex output (collaborates with: Template, Knowledge Graph, Transformer)
- Render outputs using components in context (collaborates with: AI Chat, Template, Content)

### Template

**Responsibilities:**
- Define output structure (collaborates with: Placeholder)
- Transform content (collaborates with: Transformer, Content)
- Load template (collaborates with: Behavior, Content)

### ValidateRulesAction

**Responsibilities:**
- Inject common bot rules (collaborates with: Base Bot, Rules, Common Rules)
- Inject behavior specific rules (collaborates with: Behavior, Rules, Behavior Rules)
- Load + inject content for validation (collaborates with: Behavior, Content, Knowledge Graph, Rendered Outputs)

### Rule

**Responsibilities:**
- Validate content (collaborates with: Knowledge Graph, Violations)
- Find behavior specific rules from context (collaborates with: Behavior)
- Find common bot rules from context (collaborates with: Base Bot)
- Load + inject diagnostics results (collaborates with: AI Chat, Violations, Corrections)
- Suggest corrections (collaborates with: Violations, Suggestions, Fixes)
- Provide examples - Do (collaborates with: Example, Description)
- Provide examples - Dont (collaborates with: Example, Description)
- Specialized examples (collaborates with: Language, Framework, Pattern)

### CorrectBotAction

**Responsibilities:**
- Inject correct bot instructions (collaborates with: Behavior, Correct Bot Instructions)
- Load + inject diagnostics results (collaborates with: Content, Diagnostic Report, Violations, Suggestions)


---

## Source Material

- Source: story-graph.json
- Generated from domain_concepts in epics and sub-epics
