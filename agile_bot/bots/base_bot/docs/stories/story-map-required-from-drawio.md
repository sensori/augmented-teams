Increment
    Epic (Purple)
        Feature (Green)
            Actor (Blue) - above Story
            Story (Yellow)

## Increment 1 : Increment 1

Build Agile Bots
	Generate MCP Bot Server And Tools
		AI Chat
			Deploy MCP BOT Server
		Project Bot State
			Generate Behavior Action Tools
		Project
			Generate Behavior Tools
		File System
			Generate Bot Tools
		Workflow State
			Generate MCP Bot Server
		Workflow
		Behavior Action Tool
		Behavior Tool
		Bot Tool
		Project State Tool

Invoke MCP Bot Server
	New Project
		MCP Tool
			Generates Project Scaffold
		Action
			Confirms Project Location
		Behavior Content
			Triggers Agile Bot Tool for New
		Behavior
	Resume Existing Project
		MCP Tool
			Locates Existing Project Bot State
		Action
			Triggers Agile Bot Tool for Existing
		Behavior Content
		Behavior
	Invoke Bot Tool
			Initialize Bot For Project
			Invoke Bot Behavior Action Tool
		MCP Tool
			Requests Project State
		Action
			Determines Active Step To Invoke
		Behavior Content
			Invoke Bot Tool
		Behavior
			Invoke Behavior Tool

Execute Behavior Actions
	Initialize Project Action
			Provides Input for Initialize Project
			Invokes Initialize Project Action
			Intercepts Tool Call With Project Check
			Loads Behavior and Action from Workflow State
			Validates or Determines Project Location
			Accesses Initialize Project Instructions Template
			Generates Instructions with Project Area Confirmation
			Receives Instructions and Presents Project Area to Human
			Confirms or Provides Project Location
			Calls Agent Store Method with Project Area
			Updates Project Area and Creates Directory Structure
			Saves Project Area to Agent State File
			Tracks Activity for Initialize Project Action
	Gather Context Action
			Provides Input for Gather Context
			Invokes Gather Context Action
			Intercepts Tool Call With Project Check
			Loads Behavior and Action from Workflow State
			Accesses GuardRails Required Context Configuration
			Accesses Gather Context Instructions Template
			Loads Key Questions from GuardRails Configuration
			Loads Evidence Requirements from GuardRails Configuration
			Generates Instructions with Key Questions and Evidence
			Receives Instructions and Reviews Available Context
			Answers Key Questions Based on Context
			Presents Questions and Answers to Human
			Reviews and Confirms or Corrects Answers
			Calls Agent Store Clarification Method
			Stores Clarification Data to File System
			Tracks Activity for Gather Context Action
	Decide Planning Criteria Action
			Provides Input for Decide Planning Criteria
			Invokes Decide Planning Criteria Action
			Intercepts Tool Call With Project Check
			Loads Behavior and Action from Workflow State
			Accesses GuardRails Planning Configuration
			Loads Clarification Data from Project
			Loads Previous Planning Data from Project
			Accesses Decide Planning Criteria Instructions Template
			Loads Typical Assumptions from GuardRails Configuration
			Loads Decision Criteria from GuardRails Configuration
			Generates Instructions with Assumptions and Decision Criteria
			Receives Instructions and Presents Assumptions to Human
			Presents Decision Criteria Options to Human
			Reviews Assumptions and Selects Decision Criteria Options
			Calls Agent Store Planning Method
			Stores Planning Data to File System
			Tracks Activity for Decide Planning Criteria Action
	Build Knowledge Action
			Provides Input for Build Knowledge
			Invokes Build Knowledge Action
			Intercepts Tool Call With Project Check
			Loads Behavior and Action from Workflow State
			Accesses Content Configuration
			Loads Clarification Data from Project
			Loads Planning Data from Project
			Loads Agent Rules from Bot Config
			Loads Behavior Rules from Behavior Configuration
			Accesses Build Knowledge Instructions Template
			Accesses Structured Content Schema from Content Configuration
			Accesses Builder Method Reference from Content Configuration
			Generates Instructions with Rules Schema and Builder
			Receives Instructions and Generates Structured Content
			Calls Agent Store Method with Structured Content
			Stores Structured Content
			Stores Structured Content to File System
			Creates Traceability Link
			Tracks Activity for Build Knowledge Action
	Render Output Action
			Provides Input for Render Output
			Invokes Render Output Action
			Intercepts Tool Call With Project Check
			Loads Behavior and Action from Workflow State
			Accesses Content Configuration
			Loads Clarification Data from Project
			Loads Planning Data from Project
			Loads Structured Content from Behavior Content
			Accesses Render Output Instructions Template
			Accesses Output Templates from Content Configuration
			Accesses Transformer Method References from Content Configuration
			Executes Output Builders if Configured
			Generates Instructions with Templates and Transformers
			Receives Instructions and Transforms Structured Content
			Calls Agent Store Method with Rendered Content
			Stores Rendered Content
			Stores Rendered Content to File System
			Creates Traceability Link
			Tracks Activity for Render Output Action
	Validate Rules Action
			Provides Input for Validate Rules
			Invokes Validate Rules Action
			Intercepts Tool Call With Project Check
			Loads Behavior and Action from Workflow State
			Accesses Rules Configuration
			Loads Clarification Data from Project
			Loads Planning Data from Project
			Loads Structured Content from Behavior Content
			Loads Rendered Content from Behavior Content
			Loads Agent Rules from Bot Config
			Loads Behavior Rules from Behavior Configuration
			Executes Code Diagnostics for Violations
			Accesses Validate Rules Instructions Template
			Generates Instructions with Rules Examples and Violations
			Receives Instructions and Evaluates Content Against Rules
			Generates Validation Report
			Presents Validation Report to Human
			Tracks Activity for Validate Rules Action
	Correct Bot Action
			Provides Input for Correct Bot
			Invokes Correct Bot Action
			Intercepts Tool Call With Project Check
			Loads Behavior and Action from Workflow State
			Accesses Rules Configuration
			Loads Clarification Data from Project
			Loads Planning Data from Project
			Loads Validation Violations from Previous Action
			Loads User Feedback from Context
			Loads Original Content from Behavior Content
			Accesses Correct Bot Instructions Template
			Generates Instructions with Violations and Feedback
			Receives Instructions and Applies Corrections
			Calls Agent Store Method with Corrected Content
			Stores Corrected Content
			Stores Corrected Content to File System
			Creates Traceability Link
			Tracks Activity for Correct Bot Action

Manage Workflow State
	Determine Active Behavior and Action
			Determines Active Behavior from Workflow State
			Determines Active or Next Action from Workflow State
			Uses Specific Behavior and Action from Context
	Validate Workflow State
			Validates Current Action is Complete
			Checks if Action Can Advance
			Checks if Behavior Can Advance
	Transition Workflow State
			Moves to Next Action if Current Action Done
			Moves to Next Behavior if Current Behavior Done
			Updates Workflow State in File System
			Saves Workflow State to Agent State File

Manage Project State
	Store Project State
			Stores Project Area to Agent State File
			Stores Bot Name to Agent State File
			Stores Activity Area to Agent State File
	Store Workflow State
			Stores Current Behavior Name to Workflow State File
			Stores Current Action Name to Workflow State File
	Store Activity Data
			Tracks Activity with Status and Behavior Name
			Creates Activity Entry in Activity Log
			Saves Activity Log to File System
	Store Output Data
			Stores Structured Content to File System
			Stores Rendered Content to File System
			Creates Traceability Links Between Activity and Output

Load Configuration
	Load Bot Config
			Loads Bot Config from Agent JSON File
			Loads Behaviors from Bot Config
			Loads Agent Rules from Bot Config
			Loads Trigger Words from Bot Config
	Load Behavior Configuration
			Loads Behavior Order from Bot Config
			Loads GuardRails from Behavior Configuration
			Loads Rules from Behavior Configuration
			Loads Actions from Behavior Configuration
			Loads Content Configuration from Behavior Configuration
	Load Action Instructions
			Loads Instructions Template from Base Actions
			Loads Instructions Template from Behavior Actions
			Substitutes Template Variables with Project Data
	Load Templates and Rules
			Loads Output Templates from Content Configuration
			Loads Agent Rules from Bot Config
			Loads Behavior Rules from Behavior Configuration
			Loads Examples from Rules Configuration

Generate Instructions
	Generate Action Instructions
			Accesses Instructions Template
			Loads Required Data from Project
			Loads Required Data from Behavior
			Substitutes Template Variables
			Prepends Common Instructions
			Returns Instructions to MCP Tool
	Generate Build Instructions
			Loads Clarification Data
			Loads Planning Data
			Loads Agent Rules
			Loads Behavior Rules
			Loads Structured Content Schema
			Assembles Build Instructions
	Generate Transform Instructions
			Loads Clarification Data
			Loads Planning Data
			Loads Structured Content
			Loads Output Templates
			Loads Transformer Methods
			Assembles Transform Instructions
	Generate Validation Instructions
			Loads Clarification Data
			Loads Planning Data
			Loads Content Data
			Loads Rules and Examples
			Executes Code Diagnostics
			Assembles Validation Instructions


## Increment 2 : Increment 2

Build Agile Bots
	Generate MCP Bot Server And Tools

Invoke MCP Bot Server
	New Project
	Resume Existing Project
	Invoke Bot Tool

Execute Behavior Actions
	Initialize Project Action
	Gather Context Action
	Decide Planning Criteria Action
	Build Knowledge Action
	Render Output Action
	Validate Rules Action
	Correct Bot Action

Manage Workflow State
	Determine Active Behavior and Action
	Validate Workflow State
	Transition Workflow State

Manage Project State
	Store Project State
	Store Workflow State
	Store Activity Data
	Store Output Data

Load Configuration
	Load Bot Config
	Load Behavior Configuration
	Load Action Instructions
	Load Templates and Rules

Generate Instructions
	Generate Action Instructions
	Generate Build Instructions
	Generate Transform Instructions
	Generate Validation Instructions


## Increment 3 : Increment 3

Build Agile Bots
	Generate MCP Bot Server And Tools

Invoke MCP Bot Server
	New Project
	Resume Existing Project
	Invoke Bot Tool

Execute Behavior Actions
	Initialize Project Action
	Gather Context Action
	Decide Planning Criteria Action
	Build Knowledge Action
	Render Output Action
	Validate Rules Action
	Correct Bot Action

Manage Workflow State
	Determine Active Behavior and Action
	Validate Workflow State
	Transition Workflow State

Manage Project State
	Store Project State
	Store Workflow State
	Store Activity Data
	Store Output Data

Load Configuration
	Load Bot Config
	Load Behavior Configuration
	Load Action Instructions
	Load Templates and Rules

Generate Instructions
	Generate Action Instructions
	Generate Build Instructions
	Generate Transform Instructions
	Generate Validation Instructions


## Increment 4 : Increment 4

Build Agile Bots
	Generate MCP Bot Server And Tools

Invoke MCP Bot Server
	New Project
	Resume Existing Project
	Invoke Bot Tool

Execute Behavior Actions
	Initialize Project Action
	Gather Context Action
	Decide Planning Criteria Action
	Build Knowledge Action
	Render Output Action
	Validate Rules Action
	Correct Bot Action

Manage Workflow State
	Determine Active Behavior and Action
	Validate Workflow State
	Transition Workflow State

Manage Project State
	Store Project State
	Store Workflow State
	Store Activity Data
	Store Output Data

Load Configuration
	Load Bot Config
	Load Behavior Configuration
	Load Action Instructions
	Load Templates and Rules

Generate Instructions
	Generate Action Instructions
	Generate Build Instructions
	Generate Transform Instructions
	Generate Validation Instructions


