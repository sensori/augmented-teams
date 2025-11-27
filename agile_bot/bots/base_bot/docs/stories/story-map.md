Epic
    Feature
        Story
            AC

Build Agile Bots
	Generate MCP Bot Server And Tools
    	Generate MCP Bot Server
            Human tells Bot to generate server
            Agile Bot triggers MCP Bot Server Generator
            MCP Bot Server Generator reads Bot Config from Bot Config file (agent.json)
            MCP Bot Server Generator creates Bot MCP Server Class from Bot Config
        Generate Bot Tools
            MCP Bot Server Generator reads Bot Config 
            MCP Bot Server Generator creates Bot Tool with trigger words in tool description docstring, and tool name
			MCP Bot Server Generates code that routes to active or next behavior and action of agent
        Generate Behavior Tools
            MCP Bot Server Generator reads Bot Config
            MCP Bot Server Generator creates Behavior Tool for each Bot Behavior with trigger words in tool description docstring, and tool name
			MCP Bot Server Generates code that routes to active or next action of Bot Behavior
        Generate Behavior Action Tools
            MCP Bot Server Generator reads Bot Config
            MCP Bot Server Generator creates Behavior Action Tool for each Bot Behavior-Action combination with aggregated trigger words in tool description docstring, and tool name
			MCP Bot Server Generates code that routes to specific Bot Behavior and Bot Action
		Deploy MCP BOT Server
			 Bot MCP Server exposes Bot Tool via FastMCP
			 Bot MCP Server exposes Behavior Tools via FastMCP
			 Bot MCP Server exposes Behavior Action Tools via FastMCP
			 Bot MCP Server exposes Project State Tool via FastMCP
Invoke MCP Bot Server
    New Project
        Human Triggers Agile Bot Tool for New
			MCP Bot Server Intercept with a Project Check
			Project Determines Project Location From Context
            Project checks project_area parameter if provided in context (ex: "C:\dev\augmented-teams\agents\base")
            Project stores project_area and bot_name
			MCP Bot Server returns Project Location to AI for confirmation Instructions
        Human Confirms Project Location
            AI Chat presents discovered Project Location to Human
            Human confirms or provides different Project Location
        Project Generates Project Scaffold
            Project creates project folder structure in project location
            Project creates Bot activity subfolder (docs/activity/{bot_name}/)
            Project Bot State stores Project Area and Bot Name to File System
			MCP Bot Server Routes to MCP Tool based on trigger words 
	Resume Existing Project
        Human Triggers Agile Bot Tool for Existing
			MCP Bot Server Intercept with a Project Check
			Project validates project exists in current directory  (looks for Project Bot State files in folder)
        Project Locates Existing Project Bot State
            Project checks project_area parameter if provided in context (ex: "C:\dev\augmented-teams\agents\base")
            Project checks current directory for Project Bot State files (docs/activity/{bot_name}/agent_state.json)
            MCP Bot Server returns existing Project Location to AI for display purposes
			MCP Bot Server Routes to MCP Tool based on trigger words 	
	Invoke Bot Tool
		Initialize Bot For Project
            MCP Bot Server instantiates Bot if not done before
            Agile Bot loads Workflow from Bot Config (ordered Behavior and Actions)
            Agile Bot loads Project and tells it to initialize
            Project now knows current Project and Workflow State
            Agile Bot loads Behaviors from Bot Config
            Agile Bot loads Action steps for each Behavior
		Invoke Bot Behavior Action Tool
            Human speaks to AI Chat with trigger words including Bot Behavior and Bot Action (ex: "start shaping for project xx"), including context
            AI Chat detects trigger words and routes to Behavior Action Tool via Bot MCP Server
            Behavior Action Tool receives invocation with context
		Invoke Bot Tool
            Human speaks to AI Chat with trigger words including Bot Behavior but no Bot Action (ex: "start stories for project xx"), including context
            AI Chat routes request to Behavior Tool via Bot MCP Server
            Behavior Tool determines active or next Behavior/Action
            Behavior Tool receives invocation with context
        Invoke Bot Tool
            Human speaks to AI Chat with trigger words for Bot but no Bot Behavior (ex: "start stories for project xx"), including context
            AI Chat detects trigger words and routes to Bot Tool via Bot MCP Server
            Bot Tool receives invocation with context and determines active Bot Behavior from Workflow State
		Bot Tool Determines Active Step To Invoke
            Bot Tool asks Bot Project if current action is done
            Bot Tool asks Bot Project to move to next Workflow step (Behavior or Action)
            Project determines next Behavior or Aciton form WOrkflow
			If no next action in current behavior, moves to next behavior
            If no next behavior, workflow is complete
            Project stores updated Workflow State to File System
			Bot sets current step to Behavior-Action

        Requests Project State
            Human asks for project state via AI Chat
            AI Chat detects request and routes to Project State Tool via Bot MCP Server
            Project State Tool routes to Bot Project which gets Bot Project State and Workflow State
            Project State Tool returns current state (project_area, bot_name, current_behavior, current_action) to AI Chat
            AI Chat presents project state information to Human

Execute Behavior Actions
    Initialize Project Action
        Human Provides Input for Initialize Project
        MCP Tool Invokes Initialize Project Action
        MCP Bot Server Intercepts Tool Call With Project Check
        Agile Bot Loads Behavior and Action from Workflow State
        Project Validates or Determines Project Location
        Action Accesses Initialize Project Instructions Template
        Action Generates Instructions with Project Area Confirmation
        AI Chat Receives Instructions and Presents Project Area to Human
        Human Confirms or Provides Project Location
        AI Chat Calls Agent Store Method with Project Area
        Project Updates Project Area and Creates Directory Structure
        Project Saves Project Area to Agent State File
        Project Tracks Activity for Initialize Project Action
    Gather Context Action
        Human Provides Input for Gather Context
        MCP Tool Invokes Gather Context Action
        MCP Bot Server Intercepts Tool Call With Project Check
        Agile Bot Loads Behavior and Action from Workflow State
        Behavior Accesses GuardRails Required Context Configuration
        Action Accesses Gather Context Instructions Template
        Action Loads Key Questions from GuardRails Configuration
        Action Loads Evidence Requirements from GuardRails Configuration
        Action Generates Instructions with Key Questions and Evidence
        AI Chat Receives Instructions and Reviews Available Context
        AI Chat Answers Key Questions Based on Context
        AI Chat Presents Questions and Answers to Human
        Human Reviews and Confirms or Corrects Answers
        AI Chat Calls Agent Store Clarification Method
        Project Stores Clarification Data to File System
        Project Tracks Activity for Gather Context Action
    Decide Planning Criteria Action
        Human Provides Input for Decide Planning Criteria
        MCP Tool Invokes Decide Planning Criteria Action
        MCP Bot Server Intercepts Tool Call With Project Check
        Agile Bot Loads Behavior and Action from Workflow State
        Behavior Accesses GuardRails Planning Configuration
        Action Loads Clarification Data from Project
        Action Loads Previous Planning Data from Project
        Action Accesses Decide Planning Criteria Instructions Template
        Action Loads Typical Assumptions from GuardRails Configuration
        Action Loads Decision Criteria from GuardRails Configuration
        Action Generates Instructions with Assumptions and Decision Criteria
        AI Chat Receives Instructions and Presents Assumptions to Human
        AI Chat Presents Decision Criteria Options to Human
        Human Reviews Assumptions and Selects Decision Criteria Options
        AI Chat Calls Agent Store Planning Method
        Project Stores Planning Data to File System
        Project Tracks Activity for Decide Planning Criteria Action
    Build Knowledge Action
        Human Provides Input for Build Knowledge
        MCP Tool Invokes Build Knowledge Action
        MCP Bot Server Intercepts Tool Call With Project Check
        Agile Bot Loads Behavior and Action from Workflow State
        Behavior Accesses Content Configuration
        Action Loads Clarification Data from Project
        Action Loads Planning Data from Project
        Action Loads Agent Rules from Bot Config
        Action Loads Behavior Rules from Behavior Configuration
        Action Accesses Build Knowledge Instructions Template
        Action Accesses Structured Content Schema from Content Configuration
        Action Accesses Builder Method Reference from Content Configuration
        Action Generates Instructions with Rules Schema and Builder
        AI Chat Receives Instructions and Generates Structured Content
        AI Chat Calls Agent Store Method with Structured Content
        Behavior Content Stores Structured Content
        Project Stores Structured Content to File System
        Project Creates Traceability Link
        Project Tracks Activity for Build Knowledge Action
    Render Output Action
        Human Provides Input for Render Output
        MCP Tool Invokes Render Output Action
        MCP Bot Server Intercepts Tool Call With Project Check
        Agile Bot Loads Behavior and Action from Workflow State
        Behavior Accesses Content Configuration
        Action Loads Clarification Data from Project
        Action Loads Planning Data from Project
        Action Loads Structured Content from Behavior Content
        Action Accesses Render Output Instructions Template
        Action Accesses Output Templates from Content Configuration
        Action Accesses Transformer Method References from Content Configuration
        Action Executes Output Builders if Configured
        Action Generates Instructions with Templates and Transformers
        AI Chat Receives Instructions and Transforms Structured Content
        AI Chat Calls Agent Store Method with Rendered Content
        Behavior Content Stores Rendered Content
        Project Stores Rendered Content to File System
        Project Creates Traceability Link
        Project Tracks Activity for Render Output Action
    Validate Rules Action
        Human Provides Input for Validate Rules
        MCP Tool Invokes Validate Rules Action
        MCP Bot Server Intercepts Tool Call With Project Check
        Agile Bot Loads Behavior and Action from Workflow State
        Behavior Accesses Rules Configuration
        Action Loads Clarification Data from Project
        Action Loads Planning Data from Project
        Action Loads Structured Content from Behavior Content
        Action Loads Rendered Content from Behavior Content
        Action Loads Agent Rules from Bot Config
        Action Loads Behavior Rules from Behavior Configuration
        Action Executes Code Diagnostics for Violations
        Action Accesses Validate Rules Instructions Template
        Action Generates Instructions with Rules Examples and Violations
        AI Chat Receives Instructions and Evaluates Content Against Rules
        AI Chat Generates Validation Report
        AI Chat Presents Validation Report to Human
        Project Tracks Activity for Validate Rules Action
    Correct Bot Action
        Human Provides Input for Correct Bot
        MCP Tool Invokes Correct Bot Action
        MCP Bot Server Intercepts Tool Call With Project Check
        Agile Bot Loads Behavior and Action from Workflow State
        Behavior Accesses Rules Configuration
        Action Loads Clarification Data from Project
        Action Loads Planning Data from Project
        Action Loads Validation Violations from Previous Action
        Action Loads User Feedback from Context
        Action Loads Original Content from Behavior Content
        Action Accesses Correct Bot Instructions Template
        Action Generates Instructions with Violations and Feedback
        AI Chat Receives Instructions and Applies Corrections
        AI Chat Calls Agent Store Method with Corrected Content
        Behavior Content Stores Corrected Content
        Project Stores Corrected Content to File System
        Project Creates Traceability Link
        Project Tracks Activity for Correct Bot Action

Manage Workflow State
    Determine Active Behavior and Action
        Bot Tool Determines Active Behavior from Workflow State
        Behavior Tool Determines Active or Next Action from Workflow State
        Behavior Action Tool Uses Specific Behavior and Action from Context
    Validate Workflow State
        Bot Tool Validates Current Action is Complete
        Project Checks if Action Can Advance
        Project Checks if Behavior Can Advance
    Transition Workflow State
        Bot Tool Moves to Next Action if Current Action Done
        Bot Tool Moves to Next Behavior if Current Behavior Done
        Project Updates Workflow State in File System
        Project Saves Workflow State to Agent State File

Manage Project State
    Store Project State
        Project Stores Project Area to Agent State File
        Project Stores Bot Name to Agent State File
        Project Stores Activity Area to Agent State File
    Store Workflow State
        Project Stores Current Behavior Name to Workflow State File
        Project Stores Current Action Name to Workflow State File
    Store Activity Data
        Project Tracks Activity with Status and Behavior Name
        Project Creates Activity Entry in Activity Log
        Project Saves Activity Log to File System
    Store Output Data
        Project Stores Structured Content to File System
        Project Stores Rendered Content to File System
        Project Creates Traceability Links Between Activity and Output

Load Configuration
    Load Bot Config
        Agile Bot Loads Bot Config from Agent JSON File
        Agile Bot Loads Behaviors from Bot Config
        Agile Bot Loads Agent Rules from Bot Config
        Agile Bot Loads Trigger Words from Bot Config
    Load Behavior Configuration
        Agile Bot Loads Behavior Order from Bot Config
        Agile Bot Loads GuardRails from Behavior Configuration
        Agile Bot Loads Rules from Behavior Configuration
        Agile Bot Loads Actions from Behavior Configuration
        Agile Bot Loads Content Configuration from Behavior Configuration
    Load Action Instructions
        Action Loads Instructions Template from Base Actions
        Action Loads Instructions Template from Behavior Actions
        Action Substitutes Template Variables with Project Data
    Load Templates and Rules
        Action Loads Output Templates from Content Configuration
        Action Loads Agent Rules from Bot Config
        Action Loads Behavior Rules from Behavior Configuration
        Action Loads Examples from Rules Configuration

Generate Instructions
    Generate Action Instructions
        Action Accesses Instructions Template
        Action Loads Required Data from Project
        Action Loads Required Data from Behavior
        Action Substitutes Template Variables
        Action Prepends Common Instructions
        Action Returns Instructions to MCP Tool
    Generate Build Instructions
        Action Loads Clarification Data
        Action Loads Planning Data
        Action Loads Agent Rules
        Action Loads Behavior Rules
        Action Loads Structured Content Schema
        Action Assembles Build Instructions
    Generate Transform Instructions
        Action Loads Clarification Data
        Action Loads Planning Data
        Action Loads Structured Content
        Action Loads Output Templates
        Action Loads Transformer Methods
        Action Assembles Transform Instructions
    Generate Validation Instructions
        Action Loads Clarification Data
        Action Loads Planning Data
        Action Loads Content Data
        Action Loads Rules and Examples
        Action Executes Code Diagnostics
        Action Assembles Validation Instructions

        
	