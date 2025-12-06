### Command: `/ddd-interaction-generate`

**Purpose:** Document domain interactions following DDD principles. Generates scenario-based flows showing how domain concepts (Agent, Story Agent, Project) work together. Delegates to main command with explicit generate action.

**Usage:**
* `/ddd-interaction-generate [file-path]` — Generate interaction flows

**Context:**
* For agent architecture: Documents how Agent orchestrates workflow, applies guidance, validates with rules, generates content, and loads configuration
* Documents Story Agent extending Agent with story-specific behaviors
* Documents Project tracking activity and outputs
* Based on domain map: `agents/agent-architecture-domain-map.txt`

**Steps:**
1. **Code** Execute the generate action in `/ddd-interaction`
   - Discovers domain map file (`*-domain-map.txt`) in same directory as source file
   - Reads domain concepts from domain map (Agent, Story Agent, Project)
   - Identifies business scenarios and triggers from interaction flow documentation
   - Documents transformations at business level (e.g., Context Data → Validation Data → Content Data)
   - Documents lookups as business strategy (e.g., loading configuration, retrieving behavior data)
   - States business rules as domain logic (e.g., "Context must be validated before proceeding to planning")
   - Maintains domain-level abstraction (no implementation details like API calls, JSON parsing)
   - Generates scenario-based flows with TRIGGER, ACTORS, FLOW, RULES, RESULT structure
   - Outputs to `<name>-domain-interactions.txt` (e.g., `agent-architecture-domain-interactions.txt`)

2. **AI Agent** Presents generated interaction flows to user
   - Shows file path of generated interactions
   - Highlights key scenarios documented
   - Notes any concepts from domain map that need interaction documentation

**Key Scenarios for Agent Architecture:**
* User Requests Story Shaping (Agent workflow orchestration)
* Agent Loads Configuration (Configuration data loading)
* Content Generation with Validation (Content and Rule interaction)
* Content Transformation (Content pipeline)
* User Provides Feedback and Corrections (Guidance application)

**Next Steps:**
* Review generated interactions
* Run `/ddd-interaction-validate` to check against DDD principles
* Update domain model if interactions reveal missing concepts or relationships
