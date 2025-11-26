# Story Map: Agent Architecture

**Navigation:** [📊 Increments](../increments/agent-architecture-story-map-increments.md)

**File Name**: `agent-architecture-story-map.md`
**Location**: `agents/docs/stories/map/agent-architecture-story-map.md`

> **CRITICAL MARKDOWN FORMATTING**: All tree structure lines MUST end with TWO SPACES (  ) for proper line breaks. Without two spaces, markdown will wrap lines together into one long line, breaking the visual tree structure.

## System Purpose

Migrate from markdown-first command architecture to JSON-first agent architecture. Enable structured JSON configuration as source of truth while maintaining human-readable markdown documentation. Provide common agent infrastructure (Base Agent) and specific agent implementations (Story Agent, etc.) with workflow orchestration, guidance application, rule validation, and content generation.

---

## Legend
- ⚙️ **Feature** - Cohesive set of functionality
- 📝 **Story** - Small increment of behavior (3-12d)

---

## Story Map Structure

⚙️ **Orchestrate Workflow**  

**Domain Acceptance Criteria**

**Workflow**
- Behavior-based execution engine with behaviors sorted by order property
- Behavior Data: behavior name, state (approved, next, skip, start), order
- Workflow derives behavior names from behaviors dictionary sorted by order property
- Each behavior contains: order, guardrails, rules, actions, content
- Each behavior has actions (clarification, planning, build_structure, render_output, validate, correct)
- Behavior transitions follow order unless skipped
- Behavior approval marks behavior as complete
- All behavior transitions tracked in Project.activity_log
- Instructions come from workflow.current_action.instructions

**Behavior Order Data**
- Behaviors configured with order property (e.g., shape: 1, prioritization: 2, discovery: 3, exploration: 4)
- Workflow automatically derives behavior order from behaviors sorted by order property
- No separate workflow.stages config needed

│  
├─ 📝 **Start Workflow**  
│  - and system loads Configuration and starts workflow at specified stage  
│  
│  **Acceptance Criteria**
│  - **When** user requests agent behavior execution, **then** AI Chat determines that an agent needs to be invoked
│  - **When** AI Chat determines agent needs to be invoked, **then** Agent receives request to execute behavior
│  - **When** Agent receives request to execute behavior, **then** Agent initializes with agent_name and loads Configuration from agent.json
│  - **When** Agent loads Configuration, **then** Agent creates Project with activity_area based on agent_name
│  - **When** Agent loads Configuration, **then** Agent initializes Workflow with behaviors dictionary
│  - **When** Agent initializes Workflow, **then** Workflow derives stages from behaviors sorted by order property
│  - **When** Agent initializes Workflow, **then** Agent starts workflow at initial stage
│  - **When** Agent starts workflow, **then** Agent provides instructions to AI Chat via properties (clarification_instructions, planning_instructions, generate_instructions)
│  
├─ 📝 **Manage Workflow Behaviors**  
│  - and system orchestrates Workflow using Behavior Data  
│  
│  **Acceptance Criteria**
│  - **When** Agent orchestrates Workflow, **then** Agent accesses current_behavior property which returns Behavior from behaviors dictionary based on workflow.current_behavior_name
│  - **When** Agent orchestrates Workflow, **then** Agent can start workflow at specified behavior via workflow.start(behavior_name)
│  - **When** Agent orchestrates Workflow, **then** Agent can move to next behavior via workflow.next_behavior()
│  - **When** Agent orchestrates Workflow, **then** Agent can approve current behavior via workflow.approve_current()
│  - **When** Agent orchestrates Workflow, **then** Agent can skip current behavior via workflow.skip_current()
│  - **When** Agent approves current behavior, **then** behavior is marked as complete
│  - **When** Workflow transitions behaviors, **then** Workflow tracks activity via Project.track_activity() for each behavior transition
│  
├─ 📝 **Manage Workflow Actions**  
│  - and system manages actions within behaviors  
│  
│  **Acceptance Criteria**
│  - **When** Agent orchestrates Workflow, **then** Agent can move to specific action within current behavior via workflow.move_to_action(action_name)
│  - **When** Agent accesses instructions, **then** Agent accesses instructions property which delegates to workflow.current_action.instructions
│  - **When** Agent accesses current_action, **then** Agent gets current Action from current behavior's actions
│  
├─ 📝 **Evaluate Workflow Behaviors**  
│  - and system determines which behavior should be initiated  
│  
│  **Acceptance Criteria**
│  - **When** Agent receives request to proceed, **then** Agent evaluates workflow behaviors to determine which behavior should be initiated
│  - **When** Agent evaluates workflow behaviors and context is being provided for the first time, **then** Agent determines context clarification behavior should be initiated
│  - **When** Agent evaluates workflow behaviors and context is complete, **then** Agent determines planning behavior should be initiated
│  - **When** Agent evaluates workflow behaviors and planning is complete, **then** Agent determines generation behavior should be initiated
│  
├─ 📝 **Transition Workflow Behaviors**  
│  - and system orchestrates Workflow to next behavior  
│  
│  **Acceptance Criteria**
│  - **When** Agent determines context clarification needed, **then** Agent orchestrates Workflow to context validation behavior
│  - **When** Agent determines planning needed, **then** Agent orchestrates Workflow to planning behavior
│  - **When** Agent determines generation needed, **then** Agent orchestrates Workflow to generation behavior
│  - **When** Agent determines validation needed, **then** Agent orchestrates Workflow to validation behavior
│  - **When** Agent determines correction needed, **then** Agent orchestrates Workflow to correct behavior
│  - **When** current behavior is complete, **then** Agent orchestrates Workflow to next behavior
│  
└─ 📝 **Configure Workflow Behaviors**  
   - and system configures Workflow Behaviors with Behavior Order Data  
   
   **Acceptance Criteria**
   - **When** Story Agent configures Workflow Behaviors, **then** Story Agent configures behaviors with order property (shape: 1, prioritization: 2, discovery: 3, exploration: 4)
   - **When** Story Agent configures behaviors, **then** Workflow automatically derives behavior order from behaviors sorted by order property
   - **When** Agent defines workflow behaviors, **then** workflow behaviors are derived from behaviors dictionary, not from separate workflow.stages config
   - **When** Agent enforces behavior transition order, **then** behavior transitions follow order property unless skipped
   - **When** Agent marks behavior as complete, **then** behavior approval is recorded in Behavior Data and tracked in Project.activity_log

⚙️ **Apply Guidance**  

**Domain Acceptance Criteria**

**Context Data**
- Key questions, evidence, assumptions, decision criteria, user feedback
- Required context (key questions, evidence) defined in GuardRails Data
- Key questions and evidence must be provided before proceeding

**GuardRails Data**
- Required context (key questions, evidence)
- Decision making criteria (questions, outcomes, options)
- Typical assumptions
- Agent evaluates Context against requirements using agent-specific guardrails methods (code-based check)

**Planning Data**
- Assumptions, decision criteria, high-level assessment
- User can override assumptions
- User must confirm decision criteria before proceeding
- Assumptions and decision criteria flow through all guidance interactions

│  
├─ 📝 **Clarify Context**  
│  - and system evaluates Context against requirements and prompts user for missing requirements  
│  
│  **Acceptance Criteria**
│  - **When** user provides initial context for content generation, **then** AI Chat determines that an agent can be used and some initial context has been provided
│  - **When** AI Chat determines agent can be used, **then** AI Chat sends request to generate content to Agent or to explicitly clarify context
│  - **When** Agent receives request, **then** Agent accesses current_behavior property to get Behavior for current workflow behavior
│  - **When** Agent accesses current_behavior, **then** Agent accesses clarification_instructions property which delegates to current_behavior.guardrails.requirements_clarification_instructions
│  - **When** GuardRails generates requirements_clarification_instructions, **then** GuardRails returns dict with content_data (key_questions, evidence) and instructions string
│  - **When** GuardRails generates instructions, **then** GuardRails uses RequiredClarification from guardrails config to get key_questions and evidence lists
│  - **When** GuardRails formats instructions, **then** GuardRails includes intro from BaseInstructions and lists required questions and evidence
│  - **When** AI Chat follows instructions, **then** AI Chat performs context→requirements analysis
│  - **When** key questions and evidence incomplete, **then** AI Chat prompts user to provide missing requirements
│  - **When** user provides missing key questions and evidence, **then** AI Chat calls Agent.store_clarification(key_questions_answered, evidence_provided)
│  - **When** Agent stores clarification, **then** Agent delegates to Project.store_clarification() which updates Project.clarification dict
│  - **When** key questions and evidence complete, **then** AI Chat instructs Agent to proceed
│  
├─ 📝 **Plan Approach**  
│  - and system presents assumptions and decision criteria for user review  
│  
│  **Acceptance Criteria**
│  - **When** user confirms context is complete OR AI Chat determines planning needed, **then** AI Chat determines that planning behavior should be initiated
│  - **When** AI Chat determines planning needed, **then** AI Chat sends request to proceed to planning to Agent
│  - **When** Agent receives request, **then** Agent accesses current_behavior property to get Behavior for current workflow behavior
│  - **When** Agent accesses current_behavior, **then** Agent accesses planning_instructions property which delegates to current_behavior.guardrails.get_planning_instructions
│  - **When** GuardRails generates get_planning_instructions, **then** GuardRails returns dict with content_data (assumptions, decision_criteria) and instructions string
│  - **When** GuardRails generates instructions, **then** GuardRails uses planning config from guardrails to get typical_assumptions and decision_making_criteria
│  - **When** GuardRails formats instructions, **then** GuardRails includes intro from BaseInstructions and lists assumptions and decision criteria with options
│  - **When** AI Chat follows instructions, **then** AI generates prompt text with assumptions list and decision criteria options
│  - **When** AI generates prompt text, **then** AI Chat presents prompt to user
│  - **When** user reviews prompt, **then** user can override assumptions, select from decision criteria options, make updates, OR confirm approach
│  - **When** user provides response, **then** AI Chat calls Agent.store_decisions_and_assumptions(decisions_made, assumptions_made)
│  - **When** Agent stores planning, **then** Agent delegates to Project.store_planning() which updates Project.planning dict
│  - **When** user requests changes, **then** Agent loops to provide planning instructions again
│  - **When** user confirms, **then** AI Chat instructs Agent to proceed

⚙️ **Generate Content**  

**Domain Acceptance Criteria**

**Content Data**
- JSON structures, templates, schemas, markdown, structured content schema, rendered documents
- Content Data must follow schema defined in Config Data
- Both structured JSON and rendered documents must be saved

**Builder Method**
- Performs initial structure building (code-based)
- Receives parameters from AI Chat
- Returns partial Content Data with completion instructions

**Transformer Methods**
- Render Content Data to markdown/other formats using templates
- Receive Content Data and template parameters
- Generate rendered documents

**Schema**
- Validates JSON structure against schema definitions
- Story Agent validates structured content against schema
- Schema reference defined in Content Data

│  
├─ 📝 **Provide Tools and Instructions**  
│  - and system provides MCP tool usage instructions to AI Chat  
│  
│  **Acceptance Criteria**
│  - **When** Agent initiates generation behavior, **then** Agent provides MCP tool names and appropriate usage instructions to AI Chat for initial structure building
│  - **When** Agent provides tool instructions, **then** Agent references MCP tools that are already registered via MCP server configuration
│  - **When** AI Chat receives tool names and instructions, **then** AI Chat calls appropriate MCP build tool passing in parameters using context
│  - **When** Agent needs to transform content, **then** Agent provides instructions to AI Chat with set of documents to be built, templates to be used, and important parameters
│  - **When** Agent provides transformation instructions, **then** Agent assembles transformation instructions for AI Chat
│  
├─ 📝 **Build Structured Content**  
│  - and system executes builder method and AI Chat completes structure building  
│  
│  **Acceptance Criteria**
│  - **When** Agent receives request to proceed to generation, **then** Agent accesses current_behavior property to get Behavior for current workflow behavior
│  - **When** Agent accesses current_behavior, **then** Agent moves to build_structure action via workflow.move_to_action("build_structure")
│  - **When** Agent accesses instructions, **then** Agent accesses instructions property which delegates to workflow.current_action.instructions
│  - **When** Content generates build_instructions, **then** Content includes agent-level rules, behavior-level rules, structured_content instructions
│  - **When** Content generates transform_instructions, **then** Content includes instructions from each output's instructions field
│  - **When** Agent builds structure, **then** Agent calls Content.build() to create initial structure
│  - **When** AI Chat follows build_instructions, **then** AI Chat uses tools to complete structure building
│  - **When** AI Chat generates structured content, **then** AI Chat calls Agent.store_content(structured=content_data) with generated structured content
│  - **When** Agent stores content, **then** Agent delegates to current_behavior.content.structured setter which stores data and calls Content.store()
│  - **When** Content stores, **then** Content stores via Project.store_output() and creates traceability link
│  - **When** Project stores output, **then** Project saves structured JSON to project_area/docs/content/structured.json
│  
├─ 📝 **Validate Content Schema**  
│  - and system validates Content Data against schema  
│  
│  **Acceptance Criteria**
│  - **When** Agent captures Content Data, **then** Agent calls Content.validate() to validate Content Data structure
│  - **When** Agent validates Content Data, **then** Content performs code-based schema validation
│  - **When** Story Agent validates structured content, **then** Story Agent validates against schema from Content Data
│  - **When** Agent validates Content Data, **then** Agent ensures Content Data follows schema defined in Config Data
│  
├─ 📝 **Transform Content to Documents**  
│  - and system transforms structure into required documents using templates  
│  
│  **Acceptance Criteria**
│  - **When** AI Chat follows transform_instructions, **then** AI Chat transforms structured content into rendered documents
│  - **When** AI Chat generates rendered documents, **then** AI Chat calls Agent.store_content(rendered=rendered_docs) with rendered documents
│  - **When** Agent stores rendered content, **then** Agent delegates to current_behavior.content.rendered setter which stores data and calls Content.store()
│  - **When** Content stores, **then** Content stores via Project.store_output() and creates traceability link
│  - **When** Project stores rendered output, **then** Project saves rendered documents to project_area/docs/content/{output_name}.md files (one file per output)
│  
├─ 📝 **Manage Content Data**  
│  - and system loads prompt templates and saves Content Data  
│  
│  **Acceptance Criteria**
│  - **When** Agent stores content, **then** Agent uses store_content() method which sets Content.structured or Content.rendered
│  - **When** Content.structured or Content.rendered is set, **then** Content.store() is automatically called
│  - **When** Content.store() is called, **then** Content stores via Project.store_output() and creates traceability link
│  - **When** Project stores output, **then** Project saves structured JSON to project_area/docs/content/structured.json
│  - **When** Project stores rendered output, **then** Project saves rendered markdown to project_area/docs/content/{output_name}.md files
│  - **When** Project creates traceability link, **then** Project links last activity entry to output data
│  
└─ 📝 **Configure Content Generation**  
   - and system configures Content Data with schema, builder, transformer, and templates  
   
   **Acceptance Criteria**
   - **When** Story Agent configures Behavior, **then** Story Agent configures Content Data (schema reference, builder, transformer, templates)
   - **When** Story Agent configures Content Data, **then** Story Agent defines structured content schema
   - **When** Story Agent configures Content Data, **then** Story Agent configures builder method for structured content
   - **When** Story Agent configures Content Data, **then** Story Agent configures transformer methods for output templates
   - **When** Story Agent configures Content Data, **then** Story Agent configures output templates for document generation

⚙️ **Validate with Rule**  

**Domain Acceptance Criteria**

**Validation Data**
- Examples (do/don't patterns), violations, corrections, diagnostic results, validation reports
- Agent-level rules apply to all behaviors
- Behavior-specific rules apply only to specific behavior
- Corrections in Validation Data must be incorporated into Content Data before proceeding

**Code Diagnostics**
- Code-based validation scanning
- Behavior-specific code diagnostics
- Agent performs code-based scanning for violations only

**AI Evaluation**
- AI does all evaluation, report generation, fix generation, and example update decisions
- Agent assembles prompts with examples, rules, violations, and content for AI evaluation

**Correction Data**
- Original Content Data, corrections made, current rules, instructions, examples
- Agent saves updates to Config Data (agent-level) or Behavior Data (behavior-specific)
- Updated rules, examples, and prompts improve future content generation and validation

│  
├─ 📝 **Scan for Violations**  
│  - and system scans Content Data with code and executes diagnostic methods  
│  
│  **Acceptance Criteria**
│  - **When** user triggers validation OR AI Chat determines validation needed, **then** AI Chat sends request to validate to Agent
│  - **When** Agent receives request to validate, **then** Agent scans for validations with code against Content Data
│  - **When** Agent scans for violations, **then** Story Agent executes diagnostic methods on Content Data
│  - **When** Agent scans for violations, **then** Agent identifies violations in Validation Data
│  - **When** Agent identifies violations, **then** Agent captures violations found by code
│  
├─ 📝 **Assemble Validation Prompts**  
│  - and system assembles validation prompt and AI evaluates Content Data against rules  
│  
│  **Acceptance Criteria**
│  - **When** Agent captures violations, **then** Agent assembles validation prompt (purpose: instruct AI to evaluate Content Data against rules and generate report) from Config Data templates with Content Data, examples, rules, and violations found by code
│  - **When** Agent assembles validation prompt, **then** Agent provides prompt to AI Chat
│  - **When** AI Chat follows prompt, **then** AI evaluates Content Data against rules and creates validation report
│  - **When** AI creates validation report, **then** AI Chat presents validation report to user
│  
├─ 📝 **Incorporate Fixes**  
│  - and system incorporates validated fixes into Content Data  
│  
│  **Acceptance Criteria**
│  - **When** user reads validation report, **then** user decides what to do (make fixes based on recommendations, adjust recommendations, or proceed if no violations)
│  - **When** user wants fixes, **then** user provides decision (what to fix based on recommendations or adjusted recommendations) to AI Chat
│  - **When** user provides decision, **then** AI Chat implements fixes
│  - **When** AI Chat implements fixes, **then** Agent incorporates validated fixes into Content Data
│  - **When** Agent incorporates fixes, **then** user again reviews and iterates and then agrees to proceed
│  
├─ 📝 **Correct Rules and Examples**  
│  - and system assembles correction prompt and updates rules, examples, and prompts  
│  
│  **Acceptance Criteria**
│  - **When** user requests correction OR AI Chat determines correction needed, **then** AI Chat sends request to correct to Agent
│  - **When** Agent receives request to correct, **then** Agent assembles correction prompt (purpose: instruct AI to go through original content that was created, the corrections that were made, evaluate against attached rules and instructions and examples, and provide a corrected set of rules, instructions, or prompts) with original Content Data, corrections made, rules, instructions, and examples
│  - **When** Agent assembles correction prompt, **then** Agent provides prompt to AI Chat
│  - **When** AI Chat follows prompt, **then** AI evaluates original content, corrections, rules, instructions, and examples
│  - **When** AI evaluates, **then** AI generates corrected set of rules, instructions, and prompts
│  - **When** AI generates corrections, **then** AI Chat provides corrected rules, instructions, and prompts to user
│  - **When** user reads corrected rules and decides on final form, **then** Agent updates rules, examples, and prompts in Config Data or Behavior Data
│  
└─ 📝 **Manage Validation Data**  
   - and system captures and saves Validation Data  
   
   **Acceptance Criteria**
   - **When** Agent performs validation, **then** Agent captures Validation Data (examples, violations, corrections, diagnostic results)
   - **When** AI generates example changes, **then** Agent saves example changes to Validation Data
   - **When** Agent applies rules, **then** Agent applies agent-level rules from Config Data
   - **When** Story Agent applies rules, **then** Story Agent applies behavior-specific rules from Behavior Data

⚙️ **Load Configuration**  

**Domain Acceptance Criteria**

**Config Data**
- Prompt templates, workflow definitions, rules, behaviors, content configs, examples
- Base Agent Config provides common prompt templates
- Agent Config provides behavior-specific configuration
- Config Data must be loaded before workflow execution

**Base Agent Config**
- Common prompt templates (context_validation, planning, generate, validate, correct)
- Loaded by all agents

**Agent Config**
- Workflow behaviors, agent-level rules, behaviors with guardrails/rules/actions/content
- Agent-specific configuration

**Behavior Data**
- MCP config, guardrails, rules, actions, content configs
- Story Agent configures Behavior using Behavior Data
- Method references in Config Data point to agent-specific implementations

│  
├─ 📝 **Load Base Agent Config**  
│  - and system loads common prompt templates from Base Agent Config  
│  
│  **Acceptance Criteria**
│  - **When** Agent receives request, **then** Agent loads Base Agent Config (common prompt templates)
│  - **When** Agent loads Base Agent Config, **then** Agent retrieves prompt templates from Config Data
│  - **When** Agent retrieves prompt templates, **then** Agent loads context_validation prompt templates
│  - **When** Agent retrieves prompt templates, **then** Agent loads planning prompt templates
│  - **When** Agent retrieves prompt templates, **then** Agent loads generate, validate, correct prompt templates
│  
├─ 📝 **Load Agent Config**  
│  - and system loads workflow stages, agent-level rules, and behaviors from Agent Config  
│  
│  **Acceptance Criteria**
│  - **When** Agent receives request, **then** Agent loads Agent Config from agent.json (agent-level rules, behaviors with order/guardrails/rules/actions/content)
│  - **When** Agent loads Agent Config, **then** Agent retrieves agent-level rules from Config Data
│  - **When** Agent loads Agent Config, **then** Agent retrieves behaviors dictionary from Config Data
│  - **When** Agent retrieves behaviors, **then** Agent initializes Behavior objects with behavior_config, agent_rules, and project
│  - **When** Agent initializes behaviors, **then** Agent creates behaviors dictionary keyed by behavior name
│  - **When** Agent initializes Workflow, **then** Workflow derives behavior names from behaviors sorted by order property (not from separate workflow.stages config)
│  
├─ 📝 **Load Behavior Configuration**  
│  - and system configures Behavior using Behavior Data  
│  
│  **Acceptance Criteria**
│  - **When** Story Agent configures Behavior, **then** Story Agent configures Behavior using Behavior Data
│  - **When** Story Agent configures Behavior, **then** Story Agent retrieves Guideline Data from Behavior Data
│  - **When** Story Agent configures Behavior, **then** Story Agent retrieves Rule Data from Behavior Data
│  - **When** Story Agent configures Behavior, **then** Story Agent retrieves Action Data and Content Data from Behavior Data
│  
└─ 📝 **Lookup Method References**  
   - and system looks up method references (builder, transformer, diagnostic) from Config Data  
   
   **Acceptance Criteria**
   - **When** Agent needs method references, **then** Agent looks up method references (builder, transformer, diagnostic) from Config Data
   - **When** Agent looks up builder method, **then** Agent looks up builder method for structured content
   - **When** Agent looks up transformer methods, **then** Agent looks up transformer methods for output templates
   - **When** Agent looks up diagnostic methods, **then** Agent looks up diagnostic method references for validation

⚙️ **Track Activity and Store Output**  

**Domain Acceptance Criteria**

**Activity Data**
- Status, inputs, reasoning (context provided, decisions made, human intervention)
- Activity Data must track all workflow behaviors
- Activity Data must record all assumptions, decisions, and human intervention used

**Output Data**
- Structured JSON, rendered markdown/other formats
- Output Data must include both structured and rendered formats
- Activity Data must link to Output Data for traceability

**Domain Area**
- Organizes work by domain
- Project organizes Domain Area for work tracking

│  
├─ 📝 **Organize Domain Area**  
│  - and system organizes Domain Area for work tracking  
│  
│  **Acceptance Criteria**
│  - **When** Project tracks activity, **then** Project organizes Domain Area for work tracking
│  - **When** Project organizes Domain Area, **then** Project creates domain area structure
│  - **When** Project creates domain area structure, **then** Project links activities to domain area
│  - **When** Project links activities, **then** Project manages domain area organization
│  
├─ 📝 **Track Activity**  
│  - and system tracks Activity using Activity Data  
│  
│  **Acceptance Criteria**
│  - **When** Agent completes workflow behavior, **then** Workflow calls Project.track_activity(status, behavior_name) for behavior transitions (start, next, approved, skip)
│  - **When** Project tracks activity, **then** Project creates activity entry with status and behavior name, appends to activity_log
│  - **When** Content is stored, **then** Content calls Project.store_output(structured, rendered) when Content.structured or Content.rendered is set
│  - **When** Content stores, **then** Content calls Project.create_traceability_link(structured, rendered) after storing
│  - **When** Project creates traceability link, **then** Project creates link between last activity entry and output data
│  
└─ 📝 **Store Output**  
   - and system stores Output using Output Data  
   
   **Acceptance Criteria**
   - **When** Project stores output, **then** Project saves structured JSON to output/{activity_area}/structured.json via _save_structured()
   - **When** Project stores rendered output, **then** Project saves rendered markdown files to output/{activity_area}/{output_name}.md via _save_rendered()
   - **When** Project creates traceability link, **then** Project creates link between last activity entry and output data
   - **When** Project initializes, **then** Project loads existing output data from filesystem if files exist
   - **When** Project organizes work, **then** Project organizes work by activity_area (derived from agent_name)

---

## Source Material

**Shape Phase:**
- **Primary Source**: `agents/agent-architecture-domain-map.txt` - Domain model defining Agent, Story Agent, and Project concepts with their behaviors and data structures
- **Primary Source**: `agents/agent-architecture-domain-interactions.txt` - Interaction flows showing how User, AI Chat, Agent (code), Story Agent (code), AI, and Project interact across scenarios
- **Date Generated**: 2025-11-18
- **Context Note**: Story map generated from domain model and interaction flows to support migration from markdown-first to JSON-first agent architecture

**Exploration Phase:**
- **Source**: Inherited from Shape phase
- **Acceptance Criteria**: Generated based on domain model and interaction flows
- **Date Generated**: 2025-11-18
- **Context Note**: All acceptance criteria added directly to story map document due to small scope
