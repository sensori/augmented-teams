# Story Map Increments: Agent Architecture

**Navigation:** [📋 Story Map](../map/agent-architecture-story-map.md)

**File Name**: `agent-architecture-story-map-increments.md`
**Location**: `agents/docs/stories/increments/agent-architecture-story-map-increments.md`

> **CRITICAL MARKDOWN FORMATTING**: All tree structure lines MUST end with TWO SPACES (  ) for proper line breaks. Without two spaces, markdown will wrap lines together into one long line, breaking the visual tree structure.

## Increment Planning Philosophy

**🎯 VERTICAL SLICES - NOT Horizontal Layers**

Each increment should deliver a **thin end-to-end working flow** across multiple features/epics, NOT complete one feature/epic at a time.

- ✅ **DO**: Include PARTIAL stories from MULTIPLE features in each increment
- ✅ **DO**: Ensure each increment demonstrates complete flow: input → process → validate → persist → display
- ✅ **DO**: Layer complexity across increments (simple first, then add users/scenarios/edge cases)
- ❌ **DON'T**: Complete entire Feature A, then Feature B, then Feature C
- ❌ **DON'T**: Build increments that can't demonstrate working end-to-end flow

**Layering Strategy:**
- **Increment 1**: Simplest user + simplest scenario + happy path → Full end-to-end
- **Increment 2**: Add complexity (more options, validations) + Additional users → Full end-to-end  
- **Increment 3**: Add edge cases + Error handling + Advanced features → Full end-to-end

## Legend
- ⚙️ **Feature** - Cohesive set of functionality
- 📝 **Story** - Small increment of behavior (3-12d)

---

## Value Increment 1: Basic Agent Workflow - NOW

**Relative Size**: Compared to existing command runner architecture (behaviors/stories/stories_runner.py)

**Purpose**: Deliver end-to-end workflow from user request through basic content generation, demonstrating core agent infrastructure working together.

**Implementation Phases** (from `agents/spec-refactoring.md`):
- **Phase 0**: Foundation Setup (Base Agent infrastructure, test scaffold)
- **Phase 1**: Story Agent Configuration Structure (JSON schema, story_graph.json schema)
- **Phase 4** (Partial): Generate Action (basic builder method execution, content saving)

⚙️ **Orchestrate Workflow** (PARTIAL - 2 of 5 stories)  
│  
├─ 📝 **Start Workflow**  
│  - and system loads Configuration from agent.json, initializes Workflow with behaviors, and starts workflow at initial behavior  
│  
└─ 📝 **Manage Workflow Behaviors**  
   - and system orchestrates Workflow with behaviors sorted by order property  

⚙️ **Load Configuration** (PARTIAL - 2 of 4 stories)  
│  
├─ 📝 **Load Base Agent Config**  
│  - and system loads common prompt templates from Base Agent Config (no longer needed - all config from agent.json)  
│  
└─ 📝 **Load Agent Config**  
   - and system loads agent-level rules and behaviors (with order, guardrails, rules, actions, content) from Agent Config  

⚙️ **Generate Content** (PARTIAL - 2 of 6 stories)  
│  
├─ 📝 **Build Structured Content**  
│  - and system executes builder method and AI Chat completes structure building  
│  
└─ 📝 **Manage Content Data**  
   - and system loads prompt templates and saves Content Data  

⚙️ **Track Activity and Store Output** (PARTIAL - 2 of 3 stories)  
│  
├─ 📝 **Track Activity**  
│  - and system tracks Activity using Activity Data  
│  
└─ 📝 **Store Output**  
   - and system stores Output using Output Data  

---

## Value Increment 2: Context Clarification and Planning - NEXT

**Relative Size**: Builds on Increment 1, adds guidance layer

**Purpose**: Add context validation and planning capabilities, enabling agents to validate requirements and get user confirmation before generation.

**Implementation Phases** (from `agents/spec-refactoring.md`):
- **Phase 2**: Shape Behavior - Context Validation Action (context validation, key questions/evidence)
- **Phase 3**: Shape Behavior - Planning Action (assumptions, decision criteria, high-level assessment)

⚙️ **Apply Guidance** (PARTIAL - 2 of 2 stories)  
│  
├─ 📝 **Clarify Context**  
│  - and system evaluates Context against requirements and prompts user for missing requirements  
│  
└─ 📝 **Plan Approach**  
   - and system presents assumptions and decision criteria for user review  

⚙️ **Orchestrate Workflow** (PARTIAL - 1 of 5 stories)  
│  
└─ 📝 **Evaluate Workflow Behaviors**  
   - and system determines which behavior should be initiated  

⚙️ **Load Configuration** (PARTIAL - 1 of 4 stories)  
│  
└─ 📝 **Load Base Agent Config**  
   - and system loads common prompt templates from Base Agent Config  

---

## Value Increment 3: Content Generation  - NEXT

**Relative Size**: Builds on Increments 1-2, adds tool-based content generation

**Purpose**: Enable agents to provide tools to AI Chat and orchestrate tool-based content building with schema validation and markdown generation.

**Implementation Phases** (from `agents/spec-refactoring.md`):
- **Phase 4**: Shape Behavior - Generate Action (builder methods, structured content creation, tool-based building)
- **Phase 6**: Shape Behavior - Transform Action (transformer methods, template rendering, document generation, **markdown generation from JSON**)
- **Phase 10**: Markdown Generation (integrated into transformation - generate markdown command files and rule documentation from JSON configs)

⚙️ **Generate Content** (PARTIAL - 4 of 6 stories)  
│  
├─ 📝 **Build Structured Content**  
│  - and system executes builder method and AI Chat completes structure building  
│  
├─ 📝 **Validate Content Schema**  
│  - and system validates Content Data against schema  
│  
└─ 📝 **Transform Content to Documents**  
   - and system transforms structure into required documents using templates
   - and system generates markdown documentation from JSON configuration (command files, rule documentation)
   - and system ensures markdown docs are always in sync with structured JSON source of truth  

⚙️ **Orchestrate Workflow** (PARTIAL - 1 of 5 stories)  
│  
└─ 📝 **Transition Workflow Behaviors**  
   - and system orchestrates Workflow to next behavior  

---

## Value Increment 4: Validation and Correction - LATER

**Relative Size**: Builds on Increments 1-3, adds validation and rule correction

**Purpose**: Enable agents to validate content against rules and correct rules/examples based on actual corrections made.

**Implementation Phases** (from `agents/spec-refactoring.md`):
- **Phase 5**: Shape Behavior - Validate Action (code diagnostics, AI evaluation, validation reports, second pass)
- **Correction**: Agent Corrects Rules and Examples (update rules, examples, prompts based on corrections)

⚙️ **Validate with Rule** (PARTIAL - 3 of 5 stories)  
│  
├─ 📝 **Scan for Violations**  
│  - and system scans Content Data with code and executes diagnostic methods  
│  
├─ 📝 **Assemble Validation Prompts**  
│  - and system assembles validation prompt and AI evaluates Content Data against rules  
│  
└─ 📝 **Correct Rules and Examples**  
   - and system assembles correction prompt and updates rules, examples, and prompts  

⚙️ **Orchestrate Workflow** (PARTIAL - 1 of 5 stories)  
│  
└─ 📝 **Transition Workflow Behaviors**  
   - and system orchestrates Workflow to next behavior  
├─ 📝 **Provide Tools and Instructions**  
│  - and system provides MCP tool usage instructions to AI Chat  
│  
---

## Value Increment 5: Story Agent Configuration - LATER

**Relative Size**: Builds on Increments 1-4, adds Story Agent specific behaviors

**Purpose**: Enable Story Agent to configure workflow behaviors with MCP integration.

**Implementation Phases** (from `agents/spec-refactoring.md`):
- **Phase 7**: Shape Behavior - Complete Integration (full workflow end-to-end, MCP integration)
- **Phase 8**: Remaining Story Behaviors (prioritization, discovery, exploration, specification)

⚙️ **Orchestrate Workflow** (PARTIAL - 1 of 5 stories)  
│  
└─ 📝 **Configure Workflow Behaviors**  
   - and system configures Workflow Behaviors with Behavior Order Data  

⚙️ **Load Configuration** (PARTIAL - 2 of 4 stories)  
│  
├─ 📝 **Load Behavior Configuration**  
│  - and system configures Behavior using Behavior Data  
│  
└─ 📝 **Lookup Method References**  
   - and system looks up method references (builder, transformer, diagnostic) from Config Data  

⚙️ **Generate Content** (PARTIAL - 1 of 6 stories)  
│  
└─ 📝 **Configure Content Generation**  
   - and system configures Content Data with schema, builder, transformer, and templates  

---

## Value Increment 6: Agent Builder - Templatized Agent Creation - LATER

**Relative Size**: Builds on Increments 1-5, adds automated agent creation capability

**Purpose**: Create automated agent builder that generates new agent structure from templates and questions, enabling rapid creation of new agents following the established architecture pattern.

**Implementation Phases** (from `agents/spec-refactoring.md`):
- **Phase 9**: Agent Builder - Templatized Agent Creation (domain scaffolding, signature tests, unit tests, implementation, E2E tests)

**Key Capabilities:**
- Agent folder structure creation (`agents/<agent-name>/`)
- Template file copying from common templates
- Configuration file generation (JSON configs)
- Code generation (builder, transformer, diagnostic methods)
- Question/answer workflow for agent configuration
- Validation of generated agent structure

**Deliverable:** Working agent builder that can create new agents from templates and questions

---

## Value Increment 7: Legacy Behavior Migration - LATER

**Relative Size**: Builds on Increments 1-6, migrates existing behaviors to new architecture

**Purpose**: Use agent builder to migrate existing behaviors (BDD, DDD, Clean-Code) from `behaviors/` to `agents/` structure, ensuring feature parity and improved architecture.

**Implementation Phases** (from `agents/spec-refactoring.md`):
- **Phase 11**: Migrate Legacy Behaviors Using Agent Builder
  - **11.1**: Migrate BDD Behavior (`behaviors/bdd/` → `agents/bdd/`)
  - **11.2**: Migrate DDD Behavior (`behaviors/ddd/` → `agents/ddd/`)
  - **11.3**: Migrate Clean-Code Behavior (`behaviors/clean-code/` → `agents/clean-code/`)

**For Each Behavior Migration:**
- Run agent builder to create new agent structure
- Answer questions based on existing behavior structure
- Review and refine generated agent config
- Migrate behavior-specific templates and code
- Test agent end-to-end
- Verify output matches existing behavior (regression test)
- Archive legacy behavior to `behaviors/archive/<behavior-name>/`

**Deliverable:** All legacy behaviors migrated to new architecture using agent builder, with feature parity verified

---

## Value Increment 8: Final Cleanup and Documentation - LATER

**Relative Size**: Builds on Increments 1-7, finalizes migration

**Purpose**: Archive legacy code, update documentation, and ensure clean codebase with all references updated.

**Implementation Phases** (from `agents/spec-refactoring.md`):
- **Phase 12**: Final Cleanup and Documentation
  - **12.1**: Archive Legacy Behaviors (move `behaviors/stories/` to archive, deprecation notices)
  - **12.2**: Update Documentation (architecture docs, agent builder guide, migration guide, onboarding docs)

**Key Activities:**
- Archive `behaviors/stories/` to `behaviors/archive/stories/` (after verification)
- Document deprecation notices in archived behaviors
- Update all references to point to new `agents/` structure
- Update architecture documentation with new folder structure
- Create agent builder usage guide
- Create migration guide for future behaviors
- Update developer onboarding docs
- Document agent builder question templates for customization

**Deliverable:** Clean codebase, all legacy code archived, updated documentation

---

## Source Material

**Shape Phase:**
- **Primary Source**: `agents/agent-architecture-domain-map.txt` - Domain model defining Agent, Story Agent, and Project concepts
- **Primary Source**: `agents/agent-architecture-domain-interactions.txt` - Interaction flows showing User, AI Chat, Agent (code), Story Agent (code), AI, and Project interactions
- **Date Generated**: 2025-11-18
- **Context Note**: Increments organized as vertical slices delivering end-to-end working flows across multiple features/stories

**Exploration Phase:**
- **Source**: Inherited from Shape phase
- **Acceptance Criteria**: Generated based on domain model and interaction flows, included in story map document
- **Date Generated**: 2025-11-18
- **Context Note**: All acceptance criteria added directly to story map document due to small scope
- **Plan Reference**: See `agents/spec-refactoring.md` for detailed implementation phases (Phase 0-12) that map to these value increments

