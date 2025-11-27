# Story Map: Behavior-First MCP Interface

**Navigation:** [📊 Increments](../increments/behavior-first-mcp-interface-story-map-increments.md)

**File Name**: `behavior-first-mcp-interface-story-map.md`
**Location**: `demo/cheap_wealth_online/docs/stories/map/behavior-first-mcp-interface-story-map.md`

> **CRITICAL MARKDOWN FORMATTING**: All tree structure lines MUST end with TWO SPACES (  ) for proper line breaks. Without two spaces, markdown will wrap lines together into one long line, breaking the visual tree structure.

## System Purpose

Refactor MCP interface to use behavior-first tools that return settled instructions, with workflow coordination tools and dynamic tool generation from agent.json. Remove chatty navigation tools and MCP-side file saving - AI handles all file operations.

---

## Legend
- 🎯 **Epic** - High-level capability
- ⚙️ **Feature** - Cohesive set of functionality
- 📝 **Story** - Small increment of behavior (3-12d)

---

## Story Map Structure

🎯 **Create Behavior-First Tools** (2 features, ~3 stories)  
│  
├─ ⚙️ **Generate Behavior-Action Tools Dynamically** (~2 stories)  
│  ├─ 📝 Story: Discover Behaviors from Agent Config  
│  │  *MCP server loads agent.json configuration, extracts behaviors dictionary from config, iterates through each behavior, extracts actions list from each behavior, generates tool name: {behavior_name}-{action_name}, registers tool with FastMCP*  
│  │  
│  └─ 📝 Story: Return Settled Instructions from Behavior-Action Tool  
│     *AI Chat calls shaping-clarify tool, MCP server moves agent workflow to shape behavior, moves agent workflow to clarification action, retrieves action.instructions from agent, formats response as settled instructions JSON, includes next_action_hint in response, returns JSON to AI Chat*  
│  
└─ ⚙️ **Remove Legacy Navigation Tools** (~1 story)  
   └─ 📝 Story: Remove Navigation Tool Registration  
      *MCP server removes _register_navigation_tools method, removes navigation tool implementations, removes navigation tool registration calls*  

🎯 **Add Workflow Coordination Tools** (2 features, ~2 stories)  
│  
├─ ⚙️ **Implement Story-Bot-Finish Tool** (~1 story)  
│  └─ 📝 Story: Finish Current Action and Advance  
│     *AI Chat calls story-bot-finish tool, MCP server gets current behavior and action from agent, calls agent.workflow.next_action(), checks if next action exists, if next action exists: returns status with next action name and hint, if no next action: calls agent.workflow.next_behavior(), returns status indicating behavior complete or all complete*  
│  
└─ ⚙️ **Implement Story-Bot-Status Tool** (~1 story)  
   └─ 📝 Story: Get Current Workflow Status  
      *AI Chat calls story-bot-status tool, MCP server gets agent instance, gets current_behavior.name from agent, gets current_action.name from agent.workflow, gets project_area from agent, gets available behaviors list from agent.behaviors, returns JSON with status information*  

🎯 **Remove MCP File Saving** (2 features, ~2 stories)  
│  
├─ ⚙️ **Remove Storage Tools** (~1 story)  
│  └─ 📝 Story: Remove Storage Tool Registration  
│     *MCP server removes _register_storage_tools method, removes agent_store_clarification implementation, removes agent_store_planning implementation, removes agent_store_action_output implementation, removes storage tool registration calls*  
│  
└─ ⚙️ **Update Instructions to Include File Saving** (~1 story)  
   └─ 📝 Story: Add File Saving Instructions to Settled Instructions  
      *MCP server formats settled instructions for clarification action, includes instruction: 'After gathering clarification, save to {project_area}/docs/activity/{agent_name}/clarification.json', formats settled instructions for planning action, includes instruction: 'After user confirms planning decisions, save to {project_area}/docs/activity/{agent_name}/planning.json', includes file paths in instructions*  

🎯 **Simplify Tool Response Format** (1 feature, ~1 story)  
│  
└─ ⚙️ **Standardize Settled Instructions Format** (~1 story)  
   └─ 📝 Story: Format Behavior-Action Tool Response  
      *MCP server retrieves action instructions from agent, determines next action in behavior workflow, builds next_action_hint string, formats JSON response with instructions, context, next_action_hint, returns formatted JSON to AI Chat*  

---

## Source Material

**Shape Phase:**
- **Primary Source**: User requirements for behavior-first MCP interface refactoring
- **Date Generated**: 2025-11-26
- **Context Note**: Story map created to refactor MCP interface from chatty navigation-based tools to behavior-first tools with settled instructions

