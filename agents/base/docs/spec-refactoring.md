# JSON-First Command Architecture Plan

## Executive Summary

**Architectural Shift:** Move to **structured JSON as the source of truth** that the code reads to generate prompts. JSON contains all command definitions, rules, principles, and workflow patterns. From JSON, we **generate BOTH**:
1. **Prompts for AI** - What the code uses to instruct AI during command execution
2. **Markdown documentation** - Following the template standards from PROMPT_BASED_COMMAND_REFACTORING_PLAN.md for human consumption

The markdown files (commands, rules, prompts) still exist and follow our template standards - they're just **generated from JSON** rather than being the source that code reads. This gives us structured data for code + readable documentation for humans.

---

## Core Principles

### 1. **JSON as Source of Truth (Not Replacement for Markdown)**
- **JSON defines everything**: Commands, rules, principles, examples, workflow steps
- **Code reads JSON**: Python infrastructure loads JSON, generates prompts for AI
- **Markdown is generated FROM JSON**: Human-readable docs created following PROMPT_BASED_COMMAND_REFACTORING_PLAN.md templates
- **Both outputs from one source**: 
  - Python code uses JSON to build AI prompts
  - Markdown generator creates documentation files following template standards
- **Version control friendly**: Structured diffs in JSON, readable docs in markdown

### 2. **Built-In Workflow Infrastructure**
Common patterns are first-class concepts in the base infrastructure:
- **Assumptions**: Track what AI assumes during execution
- **Questions**: Prompting questions (pre-action) and clarifying questions (post-action)
- **Decisions**: Document consolidate/separate choices and other judgment calls
- **Clarifications**: Request user input on uncertain items
- **Checklists**: Validation checklists applied consistently
- **Templates**: Reusable workflow patterns

### 3. **Thoughtful CLI Design**
- **Natural command structure**: `python runner.py <entity> <action> [params]`
- **Fewer complex commands**: CLI handles common patterns automatically
- **Interactive mode**: Prompt for missing parameters instead of failing
- **Help built-in**: `--help` on any command shows context-aware guidance

### 4. **Template-Oriented Architecture**
- **Command templates**: Define once, reuse across features
- **Workflow templates**: Standard patterns (generate, validate, correct)
- **Rule templates**: Principle structure standardized
- **Output templates**: Consistent formatting

---

## Domain Model

### Base Agent
**Purpose:** Common infrastructure all agents inherit. Provides workflow orchestration, guidance application, rule validation, and content generation.

**Implementation:**
- **workflow**: Stage-based execution engine
  - `approveCurrent()`: Mark current stage complete
  - `nextStage()`: Advance to next stage
  - `skipCurrent()`: Skip current stage
  - `start(stage)`: Begin at specific stage
  - **stages**: Ordered behaviors with state (approved, next, skip, start)
  
- **applyGuidance**: Context validation and human interaction
  - `evaluateContextProvided`: Check if required context exists
  - `promptForKeyQuestionsDecisionCriteriaAndMissingCriticalContext`: Request missing info
  - `shareAssumptionsAndDecisionMakingAndProvideOptions`: Present AI reasoning
  - `promptForAndIntegrateHumanFeedback`: Collect user input
  
- **applyRules**: Validation and correction
  - `validateExamplesWithCodeDiagnostics`: Code-based checks
  - `validateExamplesAndViolationsWithAI`: AI-based validation
  - `mayApplyToABehaviorOrAllBehaviors`: Scope control
  - `incorporateCorrections`: Apply fixes
  
- **GenerateContent**: Content creation pipeline
  - `buildStructuredContent(json)`: Create JSON structure
  - `transformContent(using templates)`: Render to markdown/other formats

### Story Agent (extends Base Agent)
**Purpose:** Story-specific agent with shape/discovery/exploration/specification workflow.

**Implementation:**
- **specificWorkflow** (story_agent.json > workflow section)
  - Defines stage order: shape → prioritization → discovery → exploration → specification
  - Builders defined in story_agent.json content sections
  
- **rules** (story_agent.json > rules section)
  - Examples (do/don't patterns)
  - Diagnostic methods (verb/noun validation, etc.)
  
- **behaviors** (story_agent.json > behaviors section)
  - **MCP config**: Merged with deployable MCP server config
  - **guidelines**: Per-behavior requirements
    - **required context**: Key questions + evidence needed
    - **decision making criteria**: How to make choices
    - **typical assumptions**: Common AI assumptions
    - **recommended human activity**: When to involve user
  - **rules**: Behavior-specific validation
  - **actions**: plan, generate, validate, correct, opt-run
    - Each action has prompt template
  - **content**: Templates and builders
    - **templates**: Markdown templates (JSON + template files)
    - **transformer**: Converts structured data to rendered output
    - **builder**: Constructs structured data from inputs
    - All content types (story map, increments, epic, feature) have template + builder

### Project Output Structure
**Purpose:** Track agent activity and outputs per domain area.

**Implementation:**
- **project folder** / **domain area**
  - **activity**: Execution log
    - **status**: Current state
    - **inputs**: What was provided
    - **reasoning**: AI thought process
      - **context provided**: What user gave
      - **decisions made**: Choices + criteria used
      - **human intervention**: User corrections/guidance
  - **outputs**: Generated artifacts
    - **structured**: JSON data
    - **rendered**: Markdown/other formats

---

## Example Configuration Files and Templates

### Base Agent Configuration (Common)

**File:** `behaviors/common_command_runner/base_agent_config.json`

```json
{
  "prompt_templates": {
    "context_validation": {
      "context_sufficient": {
        "template": "Context validation complete. The following key questions were answered:\n{{key_questions_answered}}\n\nThe following evidence was provided:\n{{evidence_provided}}\n\nProceeding to planning stage.",
        "description": "Used when context is sufficient to proceed"
      },
      "context_insufficient": {
        "template": "Context validation indicates missing information. The following key questions still need answers:\n{{missing_key_questions}}\n\nThe following evidence is still required:\n{{missing_evidence}}\n\nPlease provide the missing information to proceed.",
        "description": "Used when context is insufficient and more information is needed"
      }
    },
    "planning": {
      "assumptions_and_criteria": {
        "template": "Planning Assessment:\n\n**Assumptions I will make:**\n{{assumptions_list}}\n\n**Decision Criteria Available:**\n{{decision_criteria_questions}}\n\n**Options for each criterion:**\n{{criteria_options}}\n\nPlease review the assumptions and select your preferred criteria/options.",
        "description": "Used to present assumptions and decision criteria to user"
      },
      "high_level_assessment": {
        "template": "Based on your selections, here's my approach:\n\n**Selected Criteria:**\n{{selected_criteria}}\n\n**High-Level Assessment:**\n{{high_level_assessment}}\n\n**Reasoning:**\n{{reasoning}}\n\nPlease confirm if this approach is correct, or provide feedback for adjustments.",
        "description": "Used to present high-level assessment after user selects criteria"
      }
    },
    "generate": {
      "initial_prompt": {
        "template": "Generate {{content_type}} with the following context:\n\n**Confirmed Assumptions:**\n{{confirmed_assumptions}}\n\n**Decision Criteria Applied:**\n{{applied_criteria}}\n\n**Approach:**\n{{approach_summary}}\n\n{{behavior_specific_instructions}}",
        "description": "Base prompt for generation, gets behavior-specific instructions injected"
      }
    },
    "validate": {
      "validation_results": {
        "template": "Validation Results:\n\n**Status:** {{validation_status}}\n\n**Violations Found:**\n{{violations_list}}\n\n**Suggested Corrections:**\n{{suggested_corrections}}\n\nYou may request a second validation pass with corrections applied.",
        "description": "Used to present validation results to user"
      }
    },
    "correct": {
      "correction_prompt": {
        "template": "Applying corrections based on:\n\n**Violations:**\n{{violations}}\n\n**User Feedback:**\n{{user_feedback}}\n\nRegenerating content with corrections applied.",
        "description": "Used when applying corrections"
      }
    }
  }
}
```

**Note:** These base prompt templates are injected with specific content from the agent's behavior configuration (key questions, evidence requirements, decision criteria, etc.) during execution.

### Story Agent Configuration (Specific)

**File:** `behaviors/stories/story_agent.json`

```json
{
  "workflow": {
    "stages": [
      "shape",
      "prioritization",
      "discovery",
      "exploration",
      "specification"
    ]
  },
  "rules": {
    "description": "Agent-level rules that apply to all behaviors (shape, discovery, exploration, specification)",
    "examples": {
      "do": [
        "Use verb-noun format for all story elements (epic names, feature names, story titles)",
        "Use verb-noun language in scenario sentences",
        "Maintain verb-noun consistency from epic → feature → story → scenario"
      ],
      "dont": [
        "Mix verb-noun with other formats",
        "Use technical implementation language in user-facing story elements"
      ]
    },
    "diagnostic": "story_agent_validate_verb_noun_consistency"
  },
  "behaviors": {
    "shape": {
      "guidelines": {
        "required_context": {
          "key_questions": [
            "What is the product or feature area?",
            "What are the primary user goals?",
            "What constraints exist?"
          ],
          "evidence": [
            "Product documentation",
            "User research",
            "Existing stories"
          ]
        },
        "decision_making_criteria": [
          {
            "question": "What areas of the story map do you want to explore more deeply as a part of shaping?",
            "outcome": "Determines which epics/stories get detailed breakdown",
            "options": [
              "Dig deep on business complexity",
              "Dig deep on system interactions",
              "Dig deep on architectural pieces",
              "Dig deep on user workflows",
              "High and wide across all epics",
              "Focus on highest value areas"
            ]
          },
          {
            "question": "How should stories be prioritized for discovery?",
            "outcome": "Determines story order and focus",
            "options": [
              "Smallest testable increment validating architecture",
              "Smallest piece of value testing value proposition",
              "Largest market share first",
              "Friendliest customers",
              "Geography-based",
              "Customer type-based",
              "Product-based"
            ]
          }
        ],
        "typical_assumptions": [
          "Focus on user flow over internal systems",
          "Cover the end-to-end scenario",
          "Prioritize customer-facing features",
          "Assume stories should be independently testable",
          "Assume each story delivers user value",
          "Assume technical infrastructure stories are implicit"
        ],
        "recommended_human_activity": [
          "Review epic breakdown",
          "Confirm story granularity"
        ]
      },
      "rules": {
        "description": "Behavior-specific rules for shape (applies only to shape behavior, in addition to agent-level rules)",
        "examples": {
          "do": [
            "Include acceptance criteria in story breakdown",
            "Create stories that map to single epic"
          ],
          "dont": [
            "Create stories that span multiple epics",
            "Include implementation details in story titles"
          ]
        },
        "diagnostic": "story_agent_validate_shape_story_granularity"
      },
      "actions": {
        "description": "Only include actions that override default base agent methods. Default actions (context-validation, planning, generate, validate, correct) use base agent methods unless overridden here."
      },
      "content": {
        "structured_content": {
          "schema": "story_graph.json",
          "description": "Shared structured content schema across all story behaviors"
        },
        "builder": "story_agent_build_story_map",
        "outputs": [
          {
            "name": "story_map",
            "transformer": "story_agent_transform_story_map_to_markdown",
            "template": "templates/story-map-template.md"
          },
          {
            "name": "epic",
            "transformer": "story_agent_transform_epic_to_markdown",
            "template": "templates/epic-template.md"
          },
          {
            "name": "feature",
            "transformer": "story_agent_transform_feature_to_markdown",
            "template": "templates/feature-template.md"
          }
        ]
      }
    },
    "prioritization": {
      "guidelines": { ... },
      "rules": { ... },
      "actions": {},
      "content": { ... }
    },
    "discovery": {
      "guidelines": { ... },
      "rules": {
        "description": "Behavior-specific rules for discovery (applies only to discovery behavior, in addition to agent-level rules)",
        "examples": { ... },
        "diagnostic": "story_agent_validate_discovery"
      },
      "actions": {},
      "content": { ... }
    },
    "specification": {
      "guidelines": { ... },
      "rules": {
        "description": "Behavior-specific rules for specification (applies only to specification behavior, in addition to agent-level rules)",
        "examples": {
          "do": [
            "Use Given-When-Then format for scenarios",
            "Use imperative mood in Given steps",
            "Use declarative statements in Then steps",
            "Specify exact data values and states"
          ],
          "dont": [
            "Use conditional language in Given steps",
            "Use vague assertions in Then steps",
            "Mix imperative and declarative in same scenario"
          ]
        },
        "diagnostic": "story_agent_validate_specification_language"
      },
      "actions": {},
      "content": {
        "structured_content": {
          "schema": "story_graph.json",
          "description": "Shares same structured content schema as other story behaviors"
        },
        "builder": "story_agent_build_story_map",
        "outputs": [
          {
            "name": "specification",
            "transformer": "story_agent_transform_specification_to_markdown",
            "template": "templates/specification-template.md"
          }
        ]
      }
    }
  }
}
```

### Base Agent Templates (Common)

**File:** `behaviors/common_command_runner/templates/planning-prompt-template.md`

```markdown
# Planning Stage Prompt

## Context
{{context_summary}}

## Decision Criteria
{{decision_criteria}}

## Assumptions
{{assumptions}}

## Options
{{options_list}}

Please confirm your approach.
```

### Story Agent Templates (Specific)

**File:** `behaviors/stories/templates/story-shape-generate-prompt.md`

```markdown
# Story Shape Generation

## Product Context
{{product_name}}
{{feature_area}}

## Decision Criteria Selected
{{selected_criteria}}
{{criteria_rationale}}

## Approach
{{high_level_assessment}}

## Instructions
Generate a story map with:
- Epics covering {{epic_scope}}
- Stories within each epic
- Focus on {{focus_areas}} based on selected criteria

Use verb-noun format for all story titles.
```

**File:** `behaviors/stories/templates/story-map-template.md`

```markdown
# Story Map: {{product_name}}

## Overview
{{overview}}

## Epics

{{#each epics}}
### {{epic_name}}
{{epic_description}}

#### Stories
{{#each stories}}
- **{{story_title}}** (verb-noun)
  - {{story_description}}
  - Acceptance Criteria:
    {{#each acceptance_criteria}}
    - {{this}}
    {{/each}}
{{/each}}
{{/each}}
```

### Story Graph Schema (Common Output Structure)

**File:** `behaviors/stories/story_graph.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "product_name": { "type": "string" },
    "epics": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "epic_name": { "type": "string" },
          "epic_description": { "type": "string" },
          "stories": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "story_title": { "type": "string" },
                "story_description": { "type": "string" },
                "acceptance_criteria": {
                  "type": "array",
                  "items": { "type": "string" }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## Interaction Flow

### Step 1: User Request via Chat
User sends message: "I want to shape stories for the onboarding feature"

### Step 2: MCP Server Receives Request
MCP server identifies:
- Agent: StoryAgent
- Behavior: shape
- Action: generate (default)
- Extracts parameters from message

### Step 3: Base Agent Loads Configuration
**Base Agent:** Loads configurations:
- **Base Agent** loads base_agent_config.json (base prompt templates)
- **Base Agent** loads story_agent.json (configuration file provided by Story Agent):
  - Reads common configuration section for the agent
  - Reads workflow section (stage order: shape → prioritization → discovery → exploration → specification)
  - Reads behaviors section → shape behavior configuration
  - Retrieves required context (key questions + evidence) from shape behavior guidelines
  - Looks up story-specific builder/transformer/validator method references from content section

### Step 4: Base Agent Starts Workflow
**Base Agent:** StoryAgent calls inherited `workflow.start('shape')`:
- Base Agent workflow engine begins execution
- First stage from config: context-validation

### Step 5: Context Validation Stage
**Base Agent:** Workflow executes context-validation stage:
- **Base Agent** calls `applyGuidance.evaluateContextProvided()`
- Uses key questions and evidence requirements from story_agent.json (shape behavior guidelines)
- Checks if key questions answered
- Verifies evidence provided
- Identifies missing critical context

### Step 5a: Context Incomplete → Request Information
If context missing:
- **Base Agent** calls `applyGuidance.promptForKeyQuestionsDecisionCriteriaAndMissingCriticalContext()`
- **Base Agent** loads base prompt template: `base_agent_config.json > prompt_templates > context_validation > context_insufficient`
- **Base Agent** injects specifics from story_agent.json:
  - `{{missing_key_questions}}` ← from shape behavior guidelines > required_context > key_questions (not answered)
  - `{{missing_evidence}}` ← from shape behavior guidelines > required_context > evidence (not provided)
- **Base Agent** renders prompt and returns to user via MCP
- User provides answers
- Workflow stays in context-validation stage, loops back to Step 5

### Step 5b: Context Complete → Next Stage
If context sufficient:
- **Base Agent** loads base prompt template: `base_agent_config.json > prompt_templates > context_validation > context_sufficient`
- **Base Agent** injects specifics:
  - `{{key_questions_answered}}` ← answered questions from shape behavior guidelines
  - `{{evidence_provided}}` ← provided evidence from shape behavior guidelines
- **Base Agent** presents confirmation to user via MCP
- **Base Agent** calls `workflow.nextStage()` (moves to planning stage)

### Step 6: Planning Stage - Assumptions and Decision Criteria
**Base Agent:** Workflow executes planning stage:
- **Base Agent** calls `applyGuidance.shareAssumptionsAndDecisionMakingAndProvideOptions()`
- **Base Agent** loads base prompt template: `base_agent_config.json > prompt_templates > planning > assumptions_and_criteria`
- **Base Agent** injects specifics from story_agent.json:
  - `{{assumptions_list}}` ← from shape behavior guidelines > typical_assumptions
  - `{{decision_criteria_questions}}` ← from shape behavior guidelines > decision_making_criteria > question
  - `{{criteria_options}}` ← from shape behavior guidelines > decision_making_criteria > options
- **Base Agent** renders prompt and presents to user via MCP

### Step 6a: User Reviews and Overrides Assumptions/Criteria
User reviews planning output:
- Reviews typical assumptions presented
- Can accept assumptions or say "no, use these assumptions instead" and provide alternatives
- Selects/confirms decision criteria and options

### Step 6b: AI Provides High-Level Assessment
**Base Agent:** Generates confirmation summary:
- **Base Agent** loads base prompt template: `base_agent_config.json > prompt_templates > planning > high_level_assessment`
- **Base Agent** injects specifics:
  - `{{selected_criteria}}` ← user-selected criteria
  - `{{high_level_assessment}}` ← AI-generated assessment (e.g., "We'll do high and wide across these epics, but drill down on those stories because of complexity, architectural pieces, and system interactions")
  - `{{reasoning}}` ← AI reasoning for the approach
- **Base Agent** renders prompt and presents summary to user via MCP

### Step 6c: User Agrees or Requests Changes
User reviews assessment:
- If agrees: **Base Agent** calls `workflow.nextStage()` (moves to generate stage)
- If wants changes: User provides feedback, agent updates planning, loops to Step 6

### Step 7: Generate Stage - Content Generation
**Base Agent + Story Agent:**
- **Base Agent** calls `GenerateContent.buildStructuredContent()`
- **Base Agent** loads base prompt template: `base_agent_config.json > prompt_templates > generate > initial_prompt`
- **Base Agent** injects specifics:
  - `{{content_type}}` ← "story map" (from shape behavior)
  - `{{confirmed_assumptions}}` ← user-confirmed assumptions from planning
  - `{{applied_criteria}}` ← selected decision criteria
  - `{{approach_summary}}` ← high-level assessment
  - `{{behavior_specific_instructions}}` ← from shape behavior > actions > generate > prompt_template (if exists) or default generation instructions
- **Base Agent** uses rendered prompt to generate content
- **Base Agent** looks up builder method reference from story_agent.json (shape behavior > content > builder)
- **Story Agent** executes story-specific builder method (implemented by Story Agent)
- Creates JSON structure following story_graph.json schema

### Step 7a: Present Generated Output and Review
**Base Agent:** Stops after generate, presents via MCP:
- Generated output (structured JSON)
- Decisions made (with criteria selected)
- Assumptions made
- Clarifications from user (from planning stage)
- User can review and optionally request corrections before validation

### Step 7b: User Reviews Generated Output
User reviews output:
- If satisfied: Proceeds to validation (Step 8)
- If corrections needed: User provides feedback, **Base Agent** calls `applyGuidance.promptForAndIntegrateHumanFeedback()`, workflow returns to generate stage, loops to Step 7

### Step 8: Validate Stage - Rule Validation
**Base Agent + Story Agent:** Calls `workflow.nextStage()` (moves to validate stage):
- **Base Agent** calls `applyRules.validateExamplesAndViolationsWithAI()`
- Uses rules from story_agent.json (shape behavior > rules section)
- **Base Agent** looks up diagnostic method reference from story_agent.json (shape behavior > rules > diagnostic)
- **Story Agent** executes story-specific diagnostic methods (implemented by Story Agent, e.g., verb/noun validation)
- Validates against behavior rules
- Identifies violations

### Step 8a: Present Validation Results
**Base Agent:** Presents validation results via MCP:
- **Base Agent** loads base prompt template: `base_agent_config.json > prompt_templates > validate > validation_results`
- **Base Agent** injects specifics:
  - `{{validation_status}}` ← "pass" or "fail"
  - `{{violations_list}}` ← list of violations found (if any)
  - `{{suggested_corrections}}` ← AI-suggested corrections based on violations
- **Base Agent** renders prompt and presents to user via MCP
- User can optionally request second validation pass

### Step 8b: Optional Second Validation Pass
If user requests second pass:
- **Base Agent** calls `applyRules.incorporateCorrections()` (if violations found)
- **Base Agent** calls `applyRules.validateExamplesAndViolationsWithAI()` again
- Presents updated validation results
- Loops back to Step 8a

### Step 8c: Validation Complete → Transform
If validation passes or user approves:
- **Base Agent** calls `workflow.nextStage()` (moves to transform stage)
- **Base Agent** calls `GenerateContent.transformContent()`
- **Base Agent** looks up transformer method reference from story_agent.json (shape behavior > content > transformer)
- **Story Agent** executes story-specific transformer method (implemented by Story Agent)
- Uses template from story_agent.json (shape behavior > content > templates)
- Renders markdown
- Saves structured (JSON) + rendered (markdown) outputs

### Step 9: Present Final Results
Agent returns via MCP:
- Rendered output (markdown)
- Assumptions made
- Decisions with criteria
- Validation results

### Step 10: User Review
User reviews output:
- If approved: **Base Agent** calls `workflow.approveCurrent()`, calls `workflow.nextStage()` (moves to next behavior stage, e.g., prioritization)
- If corrections needed: User provides feedback, **Base Agent** calls `applyGuidance.promptForAndIntegrateHumanFeedback()`, workflow returns to generate stage, loops to Step 7
- If skip: **Base Agent** calls `workflow.skipCurrent()`, calls `workflow.nextStage()` (moves to next behavior stage)

---

## Incremental Migration Plan

### Overview
Migrate from existing `behaviors/agent/commands` and `rules` approach to JSON-first architecture incrementally, starting with stories behavior. Use test-first approach with clear checkpoints for MCP worker setup.

### Folder Structure
- **New agents:** `agents/<agent-name>/` (e.g., `agents/stories/`, `agents/ddd/`)
- **Legacy behaviors:** `behaviors/` folder remains intact during migration
- **Archive/deprecate:** Legacy code moved to archive after successful migration

### Migration Strategy: Value Increments (Vertical Slices)

**Approach:** Deliver thin end-to-end working flows across multiple features in each increment, NOT complete one feature at a time. Each increment demonstrates complete flow: input → process → validate → persist → display.

**Increments Reference:** See `agents/docs/stories/increments/agent-architecture-story-map-increments.md` for the value-focused increment structure. The detailed implementation phases below are organized by these value increments.

**Value Increments:**
1. **Increment 1: Basic Agent Workflow** - Foundation, configuration, basic generation
2. **Increment 2: Context Clarification and Planning** - Guidance application
3. **Increment 3: Content Generation with Tools** - Tool-based building, transformation, markdown generation
4. **Increment 4: Validation and Correction** - Rule validation, correction
5. **Increment 5: Story Agent Configuration** - Complete integration, remaining behaviors
6. **Increment 6: Agent Builder** - Templatized agent creation
7. **Increment 7: Legacy Behavior Migration** - Migrate BDD, DDD, Clean-Code
8. **Increment 8: Final Cleanup** - Archive legacy, update docs

**BDD Approach:** Following Behavior-Driven Development, we will:
- Use the increments document as the source of truth for value delivery
- Build BDD test signatures for each increment's features
- Implement test-first (signature → unit → implementation → E2E)
- Ensure each increment delivers working end-to-end functionality

---

### Pre-Phase: Domain Model and BDD Setup

**Goal:** Update domain model using BDD and create test signatures

#### Pre-Phase 0.1: Domain Model Update Using DDD
- [ ] Execute: `python behaviors/ddd/ddd_runner.py generate-structure agents/spec-refactoring.md`
- [ ] Use DDD structure analysis to extract domain model from:
  - Existing spec-refactoring.md domain model
- [ ] Review generated domain map
- [ ] Execute: `python behaviors/ddd/ddd_runner.py validate-structure agents/spec-refactoring.md`
- [ ] Fix any DDD principle violations
- [ ] Execute: `python behaviors/ddd/ddd_runner.py generate-interaction agents/spec-refactoring.md`
- [ ] Analyze domain interactions and workflows
- [ ] Execute: `python behaviors/ddd/ddd_runner.py validate-interaction agents/spec-refactoring.md`
- [ ] Update domain model documentation based on DDD analysis
- [ ] Refine domain model with discovered entities, value objects, and interactions

**Deliverable:** Updated domain model based on DDD analysis (domain-map.txt and domain-interactions.txt)

#### Pre-Phase 0.2: BDD Test Signatures for Migration
- [ ] Create test file: `agents/base/test_base_agent_infrastructure_test.py`
- [ ] Execute: `python behaviors/bdd/bdd-runner.py workflow agents/base/test_base_agent_infrastructure_test.py describe`
- [ ] Build test signatures for Base Agent components using BDD workflow
- [ ] Create test file: `agents/story/test_story_agent_configuration_test.py`
- [ ] Execute: `python behaviors/bdd/bdd-runner.py workflow agents/story/test_story_agent_configuration_test.py describe`
- [ ] Build test signatures for Story Agent configuration using BDD workflow
- [ ] Review and refine test signatures
- [ ] Ensure test signatures align with domain model

**Deliverable:** BDD test signatures ready for implementation

**Note:** All commands reference existing behaviors in `behaviors/` folder. These will be migrated to `agents/` structure in later phases.

**Ongoing Pattern:** For each subsequent phase/increment (Phase 1, Phase 2, etc.):
- Update domain model if needed
- Build BDD test signatures for that phase's features

---

## Value Increment 1: Basic Agent Workflow

**Purpose:** Deliver end-to-end workflow from user request through basic content generation, demonstrating core agent infrastructure working together.

**Increment Details:** See `agents/docs/stories/increments/agent-architecture-story-map-increments.md` for full increment scope.

### Phase 0: Foundation Setup

**Goal:** Set up base infrastructure and testing framework (part of Increment 1)

#### 0.1: Update Domain Model and Testing Scaffold
- [ ] Update domain model documentation to reflect new architecture
- [ ] Create test scaffold for Base Agent infrastructure
- [ ] Create test scaffold for Story Agent infrastructure
- [ ] Define test data structures for JSON configs
- [ ] Set up test fixtures for base_agent_config.json and story_agent.json

**Deliverable:** Test scaffold ready, domain model updated

#### 0.2: Create Base Agent Infrastructure (Test-First)
- [ ] Write tests for Base Agent workflow engine
- [ ] Write tests for Base Agent prompt template loading/injection
- [ ] Write tests for Base Agent guidance methods
- [ ] Write tests for Base Agent rules validation
- [ ] Implement Base Agent infrastructure to pass tests
- [ ] Create `agents/common/base_agent_config.json` with prompt templates

**Deliverable:** Base Agent infrastructure with passing tests



---

### Phase 1: Story Agent Configuration Structure

**Goal:** Create JSON configuration structure and validation (part of Increment 1)

#### 1.1: Create Story Agent JSON Schema (Test-First)
- [ ] Write tests for story_agent.json schema validation
- [ ] Create JSON schema for story_agent.json
- [ ] Write tests for loading and parsing story_agent.json
- [ ] Implement JSON loader/validator
- [ ] Create `agents/stories/story_agent.json` with structure (no behavior details yet)

**Deliverable:** Valid story_agent.json structure that loads successfully

#### 1.2: Create Story Graph Schema (Test-First)
- [ ] Write tests for story_graph.json schema validation
- [ ] Create/update story_graph.json schema
- [ ] Write tests for structured content validation
- [ ] Implement schema validator

**Deliverable:** Valid story_graph.json schema with validation

**Checkpoint:** Can pause here for MCP worker setup if needed

---

## Value Increment 2: Context Clarification and Planning

**Purpose:** Add context validation and planning capabilities, enabling agents to validate requirements and get user confirmation before generation.

**Increment Details:** See `agents/docs/stories/increments/agent-architecture-story-map-increments.md` for full increment scope.

### Phase 2: Shape Behavior - Context Validation Action

**Goal:** Migrate context validation to new architecture (part of Increment 2)

#### 2.1: Context Validation - Signature Tests
- [ ] Write signature tests for context validation action
- [ ] Define expected inputs/outputs
- [ ] Define expected Base Agent method calls
- [ ] Define expected prompt template usage

#### 2.2: Context Validation - Unit Tests
- [ ] Write unit tests for context validation with base prompts
- [ ] Write unit tests for prompt injection (sufficient context)
- [ ] Write unit tests for prompt injection (insufficient context)
- [ ] Write unit tests for key questions/evidence extraction from config

#### 2.3: Context Validation - Implementation
- [ ] Implement context validation action using Base Agent
- [ ] Wire up base prompt templates
- [ ] Wire up story_agent.json key questions/evidence
- [ ] Ensure all tests pass

#### 2.4: Context Validation - End-to-End Test
- [ ] Create E2E test: user provides insufficient context → receives prompt
- [ ] Create E2E test: user provides sufficient context → proceeds to planning
- [ ] Test via MCP server (if available) or direct Python call
- [ ] Verify prompt output matches expected format

**Deliverable:** Context validation working with new architecture

**Test Harness:** At the end of implementing each behavior, build both unit and end-to-end tests for the MCP server, ensuring coverage for that behavior before proceeding.

---

### Phase 3: Shape Behavior - Planning Action

**Goal:** Migrate planning stage to new architecture (part of Increment 2)

#### 3.1: Planning - Signature Tests
- [ ] Write signature tests for planning action
- [ ] Define expected assumptions presentation
- [ ] Define expected decision criteria presentation
- [ ] Define expected high-level assessment

#### 3.2: Planning - Unit Tests
- [ ] Write unit tests for assumptions loading from config
- [ ] Write unit tests for decision criteria loading
- [ ] Write unit tests for assumptions_and_criteria prompt injection
- [ ] Write unit tests for high_level_assessment prompt injection
- [ ] Write unit tests for user assumption override handling

#### 3.3: Planning - Implementation
- [ ] Implement planning action using Base Agent
- [ ] Wire up assumptions_and_criteria prompt template
- [ ] Wire up high_level_assessment prompt template
- [ ] Wire up story_agent.json assumptions and decision criteria
- [ ] Ensure all tests pass

#### 3.4: Planning - End-to-End Test
- [ ] Create E2E test: planning presents assumptions/criteria → user selects
- [ ] Create E2E test: user overrides assumptions → agent updates
- [ ] Create E2E test: high-level assessment presented → user confirms
- [ ] Test via MCP server or direct Python call

**Deliverable:** Planning action working with new architecture

---

## Value Increment 3: Content Generation with Tools

**Purpose:** Enable agents to provide tools to AI Chat and orchestrate tool-based content building with schema validation and markdown generation.

**Increment Details:** See `agents/docs/stories/increments/agent-architecture-story-map-increments.md` for full increment scope.

### Phase 4: Shape Behavior - Generate Action

**Goal:** Migrate generation to new architecture (part of Increment 3)

#### 4.1: Generate - Signature Tests
- [ ] Write signature tests for generate action
- [ ] Define expected builder method calls
- [ ] Define expected prompt template usage
- [ ] Define expected structured content output

#### 4.2: Generate - Unit Tests
- [ ] Write unit tests for base generate prompt injection
- [ ] Write unit tests for story-specific builder method lookup
- [ ] Write unit tests for builder method execution
- [ ] Write unit tests for structured content creation
- [ ] Write unit tests for transformation (if included in generate)

#### 4.3: Generate - Implementation
- [ ] Implement generate action using Base Agent + Story Agent
- [ ] Wire up base generate prompt template
- [ ] Wire up story_agent.json builder method reference
- [ ] Implement story_agent_build_story_map method
- [ ] Ensure all tests pass

#### 4.4: Generate - End-to-End Test
- [ ] Create E2E test: generate creates structured content
- [ ] Create E2E test: generated content matches story_graph.json schema
- [ ] Create E2E test: output presented with decisions/assumptions
- [ ] Test via MCP server or direct Python call

**Deliverable:** Generate action working with new architecture

**Checkpoint:** Can pause here for MCP worker setup/testing

---

## Value Increment 4: Validation and Correction

**Purpose:** Enable agents to validate content against rules and correct rules/examples based on actual corrections made.

**Increment Details:** See `agents/docs/stories/increments/agent-architecture-story-map-increments.md` for full increment scope.

### Phase 5: Shape Behavior - Validate Action

**Goal:** Migrate validation to new architecture (part of Increment 4)

#### 5.1: Validate - Signature Tests
- [ ] Write signature tests for validate action
- [ ] Define expected diagnostic method calls
- [ ] Define expected rule validation
- [ ] Define expected validation results presentation

#### 5.2: Validate - Unit Tests
- [ ] Write unit tests for agent-level rule validation
- [ ] Write unit tests for behavior-level rule validation
- [ ] Write unit tests for diagnostic method lookup/execution
- [ ] Write unit tests for validation_results prompt injection
- [ ] Write unit tests for second pass handling

#### 5.3: Validate - Implementation
- [ ] Implement validate action using Base Agent + Story Agent
- [ ] Wire up validation_results prompt template
- [ ] Wire up story_agent.json diagnostic method references (agent + behavior level)
- [ ] Implement diagnostic methods (verb_noun_consistency, shape_story_granularity)
- [ ] Ensure all tests pass

#### 5.4: Validate - End-to-End Test
- [ ] Create E2E test: validation finds violations → presents results
- [ ] Create E2E test: user requests second pass → corrections applied
- [ ] Create E2E test: validation passes → proceeds to transform
- [ ] Test via MCP server or direct Python call

**Deliverable:** Validate action working with new architecture

---

### Phase 6: Shape Behavior - Transform Action (includes Markdown Generation)

**Goal:** Migrate transformation to new architecture, including markdown generation from JSON (part of Increment 3)

**Note:** Markdown generation is integrated into transformation - generate markdown command files and rule documentation from JSON configs as part of the normal content generation workflow.

#### 6.1: Transform - Signature Tests
- [ ] Write signature tests for transform action
- [ ] Define expected transformer method calls
- [ ] Define expected template usage
- [ ] Define expected output formats

#### 6.2: Transform - Unit Tests
- [ ] Write unit tests for transformer method lookup
- [ ] Write unit tests for transformer method execution
- [ ] Write unit tests for template rendering
- [ ] Write unit tests for multiple output formats

#### 6.3: Transform - Implementation
- [ ] Implement transform action using Base Agent + Story Agent
- [ ] Wire up story_agent.json transformer method references
- [ ] Wire up template files from content > outputs
- [ ] Implement transformer methods (story_map, epic, feature)
- [ ] Ensure all tests pass

#### 6.4: Transform - End-to-End Test
- [ ] Create E2E test: transform creates markdown from structured content
- [ ] Create E2E test: multiple output formats generated correctly
- [ ] Create E2E test: templates render with correct data
- [ ] Test via MCP server or direct Python call

**Deliverable:** Transform action working with new architecture

---

## Value Increment 5: Story Agent Configuration

**Purpose:** Enable Story Agent to configure workflow stages and behaviors with MCP integration.

**Increment Details:** See `agents/docs/stories/increments/agent-architecture-story-map-increments.md` for full increment scope.

### Phase 7: Shape Behavior - Complete Integration

**Goal:** Full shape behavior workflow end-to-end (part of Increment 5)

#### 7.1: Full Workflow - End-to-End Test
- [ ] Create E2E test: context-validation → planning → generate → validate → transform
- [ ] Test all user interaction points (assumption override, second validation pass, etc.)
- [ ] Test via MCP server
- [ ] Verify output matches existing behavior output (regression test)

#### 7.2: MCP Integration
- [ ] Set up MCP server with new architecture
- [ ] Test MCP endpoints for shape behavior
- [ ] Verify MCP responses match expected format
- [ ] Test error handling via MCP

**Deliverable:** Complete shape behavior working via MCP

**Checkpoint:** Major milestone - shape behavior fully migrated

---

### Phase 8: Remaining Story Behaviors

**Goal:** Migrate remaining behaviors (prioritization, discovery, exploration, specification) (part of Increment 5)

**Approach:** Repeat Phases 2-7 for each behavior:
- Prioritization (simpler, can be done quickly)
- Discovery
- Exploration  
- Specification

**For each behavior:**
- Signature tests
- Unit tests
- Implementation
- End-to-end tests
- MCP integration

**Deliverable:** All story behaviors migrated to `agents/stories/`

**Transition Point:** Once all story behaviors are migrated, switch from legacy `behaviors/stories/` to new `agents/stories/` for all story-related work (shaping, discovery, exploration, specification). From this point forward:
- Use `agents/stories/` for story work
- Use `agents/bdd/` for BDD work (once migrated)
- Use `agents/ddd/` for DDD work (once migrated)
- Only use legacy `behaviors/` for behaviors not yet migrated

---

## Value Increment 6: Agent Builder - Templatized Agent Creation

**Purpose:** Create automated agent builder that generates new agent structure from templates and questions, enabling rapid creation of new agents following the established architecture pattern.

**Increment Details:** See `agents/docs/stories/increments/agent-architecture-story-map-increments.md` for full increment scope.

### Phase 9: Agent Builder - Templatized Agent Creation

**Goal:** Create automated agent builder that generates new agent structure from templates and questions (part of Increment 6)

#### 9.1: Agent Builder - Domain Scaffolding (BDD/TDD)
- [ ] Use `agents/stories/` (new stories agent) for story shaping, discovery, exploration, specification
- [ ] Use BDD workflow to scaffold agent builder domain
- [ ] Define agent builder domain model
- [ ] Define agent builder interactions and workflows
- [ ] Create test signatures for agent builder

#### 9.2: Agent Builder - Signature Tests
- [ ] Write signature tests for agent folder creation
- [ ] Write signature tests for template file copying
- [ ] Write signature tests for configuration file generation
- [ ] Write signature tests for code generation
- [ ] Write signature tests for question/answer workflow

#### 9.3: Agent Builder - Unit Tests
- [ ] Write unit tests for folder structure creation (`agents/<agent-name>/`)
- [ ] Write unit tests for template discovery and copying
- [ ] Write unit tests for JSON config generation from answers
- [ ] Write unit tests for code generation from templates
- [ ] Write unit tests for question flow management

#### 9.4: Agent Builder - Implementation
- [ ] Implement agent folder structure creator
- [ ] Implement template file copier (from `agents/common/templates/` or agent-specific)
- [ ] Implement question/answer system for:
  - Agent name and description
  - Workflow stages (behaviors)
  - Required context (key questions, evidence)
  - Decision criteria
  - Typical assumptions
  - Rules (agent-level and behavior-level)
  - Content types and outputs
  - Builder/transformer methods needed
- [ ] Implement JSON config generator (creates `agents/<agent-name>/<agent-name>_agent.json`)
- [ ] Implement code generator for:
  - Agent-specific builder methods
  - Agent-specific transformer methods
  - Agent-specific diagnostic methods
- [ ] Ensure all tests pass

#### 9.5: Agent Builder - End-to-End Test
- [ ] Create E2E test: Run agent builder → answer questions → verify agent structure created
- [ ] Create E2E test: Verify generated JSON config is valid
- [ ] Create E2E test: Verify generated code compiles and basic structure works
- [ ] Test agent builder via CLI or interactive mode

**Deliverable:** Working agent builder that can create new agents from templates and questions

**Checkpoint:** Can pause here to test agent builder thoroughly

---

### Phase 10: Markdown Generation (Integrated into Phase 6)

**Note:** Markdown generation is now integrated into Phase 6 (Transform Action) as part of Increment 3. When content is generated, both structured JSON and markdown documentation are produced from templates, ensuring docs are always in sync with JSON source of truth.

**Implementation:** See Phase 6 above for markdown generation details.

---

## Value Increment 7: Legacy Behavior Migration

**Purpose:** Use agent builder to migrate existing behaviors (BDD, DDD, Clean-Code) from `behaviors/` to `agents/` structure, ensuring feature parity and improved architecture.

**Increment Details:** See `agents/docs/stories/increments/agent-architecture-story-map-increments.md` for full increment scope.

### Phase 11: Migrate Legacy Behaviors Using Agent Builder

**Goal:** Use agent builder to migrate BDD, DDD, and clean-code behaviors (part of Increment 7)

#### 11.1: Migrate BDD Behavior
- [ ] Run agent builder to create `agents/bdd/`
- [ ] Answer questions based on existing `behaviors/bdd/` structure
- [ ] Review and refine generated agent config
- [ ] Migrate BDD-specific templates and code
- [ ] Test BDD agent end-to-end
- [ ] Verify output matches existing BDD behavior (regression test)
- [ ] Archive `behaviors/bdd/` to `behaviors/archive/bdd/`

#### 11.2: Migrate DDD Behavior
- [ ] Run agent builder to create `agents/ddd/`
- [ ] Answer questions based on existing `behaviors/ddd/` structure
- [ ] Review and refine generated agent config
- [ ] Migrate DDD-specific templates and code
- [ ] Test DDD agent end-to-end
- [ ] Verify output matches existing DDD behavior (regression test)
- [ ] Archive `behaviors/ddd/` to `behaviors/archive/ddd/`

#### 11.3: Migrate Clean-Code Behavior
- [ ] Run agent builder to create `agents/clean-code/`
- [ ] Answer questions based on existing `behaviors/clean-code/` structure
- [ ] Review and refine generated agent config
- [ ] Migrate clean-code-specific templates and code
- [ ] Test clean-code agent end-to-end
- [ ] Verify output matches existing clean-code behavior (regression test)
- [ ] Archive `behaviors/clean-code/` to `behaviors/archive/clean-code/`

**Deliverable:** All legacy behaviors migrated to new architecture using agent builder

---

## Value Increment 8: Final Cleanup and Documentation

**Purpose:** Archive legacy code, update documentation, and ensure clean codebase with all references updated.

**Increment Details:** See `agents/docs/stories/increments/agent-architecture-story-map-increments.md` for full increment scope.

### Phase 12: Final Cleanup and Documentation

**Goal:** Archive legacy code, update documentation (part of Increment 8)

#### 12.1: Archive Legacy Behaviors
- [ ] Move `behaviors/stories/` to `behaviors/archive/stories/` (after verification)
- [ ] Document deprecation notices in archived behaviors
- [ ] Update any remaining references to point to new `agents/` structure

#### 12.2: Update Documentation
- [ ] Update architecture documentation with new folder structure
- [ ] Create agent builder usage guide
- [ ] Create migration guide for future behaviors
- [ ] Update developer onboarding docs
- [ ] Document agent builder question templates for customization

**Deliverable:** Clean codebase, all legacy code archived, updated documentation

---

## Testing Strategy Summary

**Test-First Approach:**
1. **Signature Tests** - Define expected behavior and interfaces
2. **Unit Tests** - Test individual components in isolation
3. **Implementation** - Write code to pass tests
4. **End-to-End Tests** - Test complete workflows

**Test Types:**
- **Signature Tests:** Define contracts and expected method calls
- **Unit Tests:** Test Base Agent methods, prompt injection, config loading
- **Integration Tests:** Test Base Agent + Story Agent interaction
- **End-to-End Tests:** Test complete user workflows via MCP or direct calls

**MCP Worker Checkpoints:**
- After Phase 0 (Foundation) - Set up MCP worker infrastructure
- After Phase 2 (Context Validation) - Test MCP with context validation
- After Phase 4 (Generate) - Test MCP with generation
- After Phase 7 (Shape Complete) - Full MCP integration test

---

## Success Criteria

- [ ] All tests passing (signature, unit, E2E)
- [ ] Shape behavior fully functional via MCP
- [ ] Output matches existing behavior (regression)
- [ ] Markdown docs generated from JSON
- [ ] Code is cleaner and more maintainable
- [ ] Ready to migrate other behaviors using same pattern

