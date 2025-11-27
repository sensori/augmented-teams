# Story Map Increments: Behavior-First MCP Interface

**Navigation:** [📋 Story Map](../map/behavior-first-mcp-interface-story-map.md)

**File Name**: `behavior-first-mcp-interface-story-map-increments.md`
**Location**: `demo/cheap_wealth_online/docs/stories/increments/behavior-first-mcp-interface-story-map-increments.md`

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

## Value Increment 1: Foundation: Behavior-First Tools and Workflow Coordination - NOW

**Relative Size**: Large

**Purpose**: Implement dynamic behavior-action tool generation, add workflow coordination tools (story-bot-finish, story-bot-status), and remove legacy navigation tools. Establish foundation for new MCP interface.

**Approach**: Enable behavior-first tool calling with settled instructions and workflow coordination. Remove chatty navigation tools.

⚙️ **Create Behavior-First Tools** (PARTIAL - 2 of 2 features)  
│  
├─ ⚙️ **Generate Behavior-Action Tools Dynamically** (PARTIAL - 2 of 2 stories)  
│  ├─ 📝 **Discover Behaviors from Agent Config**  
│  │  - and system loads agent.json, discovers all behaviors and their actions, generates tool names in format {behavior}-{action}  
│  │  
│  └─ 📝 **Return Settled Instructions from Behavior-Action Tool**  
│     - and system moves agent to behavior and action, retrieves instructions, formats as settled instructions JSON with next_action_hint  
│  
└─ ⚙️ **Remove Legacy Navigation Tools** (PARTIAL - 1 of 1 story)  
   └─ 📝 **Remove Navigation Tool Registration**  
      - and system removes registration of agent_move_to_behavior, agent_move_to_action, agent_next_action, agent_next_behavior tools from ToolRegistry  

⚙️ **Add Workflow Coordination Tools** (PARTIAL - 2 of 2 features)  
│  
├─ ⚙️ **Implement Story-Bot-Finish Tool** (PARTIAL - 1 of 1 story)  
│  └─ 📝 **Finish Current Action and Advance**  
│     - and system marks current action complete, advances workflow to next action, returns status with next action hint  
│  
└─ ⚙️ **Implement Story-Bot-Status Tool** (PARTIAL - 1 of 1 story)  
   └─ 📝 **Get Current Workflow Status**  
      - and system returns current behavior name, current action name, project area, and available behaviors list  

**Domain Acceptance Criteria:**

**Concepts:**
- **Behavior-Action Tool**: MCP tool named {behavior}-{action} that moves agent to specific behavior and action, then returns settled instructions for AI execution.
- **Settled Instructions**: Ready-to-use instructions JSON returned by MCP tools containing instructions field (action instructions), context field (behavior/action metadata), and next_action_hint field (workflow guidance).
- **Workflow Coordination Tool**: Generalized MCP tool (story-bot-finish, story-bot-status) for managing workflow state and progression without behavior-specific knowledge.

**Behaviors:**
- **Behavior-Action Tool**: MCP server generates tool name from behavior and action, registers with FastMCP, returns settled instructions when called
- **Settled Instructions**: MCP server formats action instructions as JSON with context and workflow hints, returns to AI Chat
- **Workflow Coordination Tool**: MCP server provides finish and status tools that manage workflow progression and state queries

---

## Value Increment 2: Remove MCP File Operations - NEXT

**Relative Size**: Medium

**Purpose**: Remove all agent_store_* tools and update instructions to include file saving guidance for AI. Ensure AI handles all file operations directly.

**Approach**: Eliminate MCP-side file saving, make AI responsible for all file operations with clear instructions.

⚙️ **Remove MCP File Saving** (PARTIAL - 2 of 2 features)  
│  
├─ ⚙️ **Remove Storage Tools** (PARTIAL - 1 of 1 story)  
│  └─ 📝 **Remove Storage Tool Registration**  
│     - and system removes _register_storage_tools method and all agent_store_* tool implementations  
│  
└─ ⚙️ **Update Instructions to Include File Saving** (PARTIAL - 1 of 1 story)  
   └─ 📝 **Add File Saving Instructions to Settled Instructions**  
      - and system includes file saving instructions in settled instructions response, telling AI to save clarification.json, planning.json, or structured.json as appropriate  

**Domain Acceptance Criteria:**

**Concepts:**
- **AI File Operations**: AI Chat directly saves files (clarification.json, planning.json, structured.json) to project area based on instructions in settled instructions response.

**Behaviors:**
- **AI File Operations**: AI Chat reads file saving instructions from settled instructions, uses write tool to save files to specified paths

---

## Value Increment 3: Standardize Tool Responses - NEXT

**Relative Size**: Small

**Purpose**: Ensure all tools return consistent settled instructions format with instructions, context, and next_action_hint fields.

**Approach**: Standardize all tool responses to use settled instructions format for consistency.

⚙️ **Simplify Tool Response Format** (PARTIAL - 1 of 1 feature)  
│  
└─ ⚙️ **Standardize Settled Instructions Format** (PARTIAL - 1 of 1 story)  
   └─ 📝 **Format Behavior-Action Tool Response**  
      - and system formats behavior-action tool response as JSON with instructions (string), context (dict with behavior/action names), and next_action_hint (string with next tool to call)  

**Domain Acceptance Criteria:**

**Concepts:**
- **Standardized Tool Response**: All MCP tools return JSON with instructions (string), context (dict), and next_action_hint (string) fields for consistent AI consumption.

**Behaviors:**
- **Standardized Tool Response**: MCP server formats all tool responses using consistent JSON structure with required fields

---

## Source Material

**Shape Phase:**
- **Primary Source**: User requirements for behavior-first MCP interface refactoring
- **Date Generated**: 2025-11-26
- **Context Note**: Increments organized as vertical slices delivering end-to-end working flows across multiple features/stories

**Exploration Phase:**
- **Source**: Inherited from Shape phase
- **Acceptance Criteria**: Generated based on user requirements for MCP interface refactoring
- **Date Generated**: 2025-11-26
- **Context Note**: All acceptance criteria included in story map document

