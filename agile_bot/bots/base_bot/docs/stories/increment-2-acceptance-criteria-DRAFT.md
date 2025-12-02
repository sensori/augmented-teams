# Increment 2: Simplest MCP - Acceptance Criteria (DRAFT)

## Planning Decisions Applied
- **Granularity:** Inner System (technical interactions, system-to-system, internal behavior)
- **Count:** Stop at full back-and-forth (user-system-user) - atomic and testable slices
- **Consolidation:** Same logic/different data = consolidate; Different formulas = separate; Different validation = separate

---

## Epic: Build Agile Bots
### Sub-Epic: Generate Bot Server And Tools

---

## Story 1: Generate MCP Bot Server

**User:** MCP Server Generator  
**Sequential Order:** 3  
**Story Type:** system

### Acceptance Criteria

- **WHEN** MCP Server Generator receives Bot Config
- **THEN** Generator generates unique MCP Server instance with **Unique server name** from bot name (e.g., "story_bot_server", "bdd_bot_server")
  - THAT leverages**Server initialization code** to start in separate thread
- **AND** Generated server includes Bot Config reference
- **AND** Generated server leverages Specific Bot instantiation code


## Story 2: Generate Behavior Action Tools

**User:** MCP Server Generator  
**Sequential Order:** 1  
**Story Type:** system

### Acceptance Criteria
- **WHEN** Generator processes Bot Config
- **THEN** Generator creates tool code for each (behavior, action) pair:
    - **AND** Enumerates all behaviors and actions from Bot Config (2_gather_context, 3_decide_planning_criteria, 4_build_knowledge, 5_render_output, 6_correct_bot, 7_validate_rules)
    - **AND** For each pair, generates tool code that:
      - **AND** Has unique name: `{bot_name}_{behavior}_{action}`
      - **AND** Loads trigger words from `{bot}/behaviors/{behavior}/{action}/trigger_words.json`
      - **Example:** story_bot with 4 behaviors × 6 base actions = 24 tool instances to generate
      - **AND** Annotates tool with trigger words for lookup
      - **AND** Forwards invocation to Bot + Behavior + Action
      - **AND** Loads instructions and injects into AI Chat
  - **Tool catalog** prepared with all generated tool instances


## Story 3: Deploy MCP BOT Server

**User:** System  
**Sequential Order:** 3  
**Story Type:** system

### Acceptance Criteria

#### AC 1: Deploy and Publish Tool Catalog
- **WHEN** MCP Server code generated and all tools generated
- **THEN** Generator deploys/starts generated MCP Server
- **AND** Server initializes in separate thread
- **AND** Server registers itself with MCP Protocol Handler using unique server name
- **AND** Server publishes tool catalog to AI Chat containing all generated BaseBehavioralActionTools
- **AND** Each tool entry in catalog includes:
  - Unique tool name: `{bot_name}_{behavior}_{action}`
  - Description from instructions.json
  - Trigger patterns from trigger_words.json (for AI Chat to match against user input)
  - Parameters (behavior name, action name, optional user input)
- **AND** AI Chat can discover tools by trigger word pattern matching
- **AND** Server endpoint accessible to AI Chat client

- **WHEN** Tool code generation and deploy completes for each (behavior, action) pair
- **THEN** Generator adds tool to server's tool catalog:
  - **AND** Adds generated tool with unique tool name
  - **AND** Includes trigger word patterns for lookup
  - **AND** Includes tool description and parameters
- **AND** All generated tools added to catalog during server generation

## Story 4: Invoke MCP BOT Tool

**User:** AI Chat  
**Sequential Order:** 4  
**Story Type:** system

#### AC 3: Generated Server Self-Initialization
- **WHEN** Generated MCP Server starts up
- **THEN** Server initializes itself in separate thread
- **AND** Server instantiates Specific Bot class from Bot Config
- **AND** Specific Bot loads Behavior configuration from Bot Config

- **WHEN** Generated MCP Server initializes
- **THEN** Server preloads Specific Bot class from Bot Config
- **AND** Bot class remains in memory for duration of server lifecycle
- **AND** All tool invocations use same preloaded bot instance
- **Technical Constraint:** Preload bot once, reuse across all tool invocations

- **WHEN** AI Chat invokes any generated tool
- **THEN** Tool uses inherited BaseTool logic to invoke correct behavior action on preloaded bot
- **AND** Invocation completes in < 50ms (lookup + forward to bot)
- **AND** Instructions loaded and injected into AI Chat context
- **AND** Total round-trip time < 200ms
- **Technical Constraint:** Cache instructions in memory, minimize I/O

- **WHEN** MCP tool is called for a (behavior, action) pair
  - **THEN** tool directly routes to behavior action method ofpreloaded Bot class
  - **AND** Calls Bot.Behavior.Action with correct parameters
  - **AND** Bot.Behavior compiles and returns instructions 
  - **AND**  MCP tool Injects instructions into AI Chat context


## Folder Structure

```
agile_bot/bots/
├── base_bot/
│   ├── src/
│   │   ├── generator.py          # MCP Server Generator code
│   │   ├── base_mcp_server.py    # Base MCP Server implementation
│   │   ├── base_tool.py          # BaseTool inheritance logic
│   │   └── base_bot.py           # Base Bot class
│   ├── config/
│   │   └── mcp_config.json       # General MCP configuration
│   ├── lib/
│   │   ├── fastmcp/              # FastMCP library
│   │   └── [other dependencies]
│   └── docs/
│
├── story_bot/                    # Example specific bot
│   ├── src/
│   │   ├── story_bot_server.py   # Generated specific MCP server
│   │   ├── story_bot.py          # Specific Bot class
│   │   └── tools/                # Generated tool code
│   │       ├── story_bot_shape_gather_context.py
│   │       ├── story_bot_shape_decide_planning_criteria.py
│   │       ├── [etc... N×6 tools]
│   ├── config/
│   │   └── tool_config.json      # Specific tool configuration
│   └── behaviors/
│       ├── 1_shape/
│       ├── 2_discovery/
│       ├── [etc...]
│
└── [other specific bots: bdd_bot, domain_bot, etc.]
```

## Tool Catalog Structure per Bot

For each bot, Generator creates tool catalog:

```
Generated MCP Server (e.g., "story_bot_server")
├── Unique Server Name: "story_bot_server"
├── Tool Catalog containing BaseBehavioralActionTools:
│   ├── story_bot_shape_gather_context
│   ├── story_bot_shape_decide_planning_criteria
│   ├── story_bot_shape_build_knowledge
│   ├── story_bot_shape_render_output
│   ├── story_bot_shape_validate_rules
│   ├── story_bot_shape_correct_bot
│   ├── (repeat for each behavior: discovery, exploration, specification)
│   └── Total: N behaviors × 6 base actions = N×6 tools
└── Each tool inherits from base_bot/src/base_tool.py
```

---

## File Locations

**Base Bot (agile_bot/bots/base_bot/):**
- Generator code: `src/generator.py`
- Base MCP Server: `src/base_mcp_server.py`
- Base Tool: `src/base_tool.py`
- Base Bot class: `src/base_bot.py`
- General MCP config: `config/mcp_config.json`
- Dependencies: `lib/fastmcp/` and other libs

**Specific Bot (e.g., agile_bot/bots/story_bot/):**
- Generated server: `src/story_bot_server.py`
- Specific bot class: `src/story_bot.py`
- Generated tools: `src/tools/story_bot_{behavior}_{action}.py`
- Tool config: `config/tool_config.json`
- Behaviors: `behaviors/{behavior}/` folders

---

## Out of Scope for Increment 2

The following are explicitly **OUT OF SCOPE** for this increment:
- **Project State Manager** - state persistence
- **Workflow State** - tracking current behavior/action
- **Workflow** - orchestrating behavior-action sequences
- **State management** - will be added in future increments

This increment focuses ONLY on:
- MCP Server generation and deployment (in base_bot/src/)
- Tool generation (in <specific_bot>/src/tools/)
- Basic invocation and instruction injection
- NO state persistence or workflow management

---

## Notes for Editing

- Add/remove/modify acceptance criteria as needed
- Adjust timing constraints if too aggressive/lenient
- Clarify domain responsibilities if ambiguous
- Add edge cases or error scenarios if missing
- Flag any consolidation opportunities I missed
- Verify tool hierarchy aligns with implementation plan
- Ensure no workflow/state management leaked into acceptance criteria


