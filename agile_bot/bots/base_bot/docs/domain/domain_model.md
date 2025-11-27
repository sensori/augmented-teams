Agile Bot
	Loads Workflow: Workflow,Bot Config
	Loads Project: Project,Workflow
	Loads Behaviors: Behaviors,Bot Config
	Generates MCP Server: MCP Bot Server Generator

Project
	Manages Project State: Project Bot State,File System
	Manages Workflow State: Workflow,Project Bot State,File System
	Provides Project Scaffold: File System
	Tracks Bot State And Activity: Project Bot State,Bot Activity,File System

Workflow
	Orders Behavior Action Steps: Agile Bot,Bot Behavior

Bot Behavior
	Defines Action Steps: Bot Config

Project Bot State
	Stores Project Area: File System
	Stores Activities: Bot Activity,File System
	Stores Workflow State: Workflow State,File System

Workflow State
	Stores Current Behavior Name: Behavior
	Stores Current Action Name: Action

Bot Tool
	Runs Active Action On Active Behavior: Agile Bot,Project,Project Bot State,Workflow State,Bot Behavior,Bot Action
	Moves To Next Action If Done: Workflow,Agile Bot,Project,Workflow State
	Moves To Next Behavior If Done: Workflow,Agile Bot,Project,Workflow State

Behavior Tool
	Determines Active Or Next Behavior Action: Workflow State,Workflow,Bot Config
	Runs Active Action On Behavior: Agile Bot,Project,Project Bot State,Workflow State,Bot Behavior,Bot Action
	Moves To Next Action If Done: Workflow,Project Bot State,Workflow State
	Moves To Next Behavior If Done: Workflow,Project Bot State,Workflow State

Behavior Action Tool
	Runs Specific Behavior Action: Agile Bot,Bot Behavior,Bot Action

Project State Tool
	Reads Project State: Project Bot State,Workflow State,File System
	Returns Current State: AI Chat,MCP Bot Server

MCP Bot Server Generator
	Generates MCP Bot Server: Bot Config,MCP Bot Server
	Generates Bot Tools: Bot Config,MCP Bot Server,Bot Tool,Trigger Words
	Generates Behavior Tools: Bot Config,MCP Bot Server,Behavior Tool,Bot Behavior,Behavior Trigger Words
	Generates Behavior Action Tools: Bot Config,MCP Bot Server,Behavior Action Tool,Behavior,Action,Behavior Action Trigger Words

MCP Bot Server
	Created By Bot: Agile Bot
	Instantiates Bot For Project: Bot Config,Bot,Project
	Intercepts Tool Calls With Project Check: Project,Bot Tool,Behavior Tool,Behavior Action Tool
	Returns Project Location For Confirmation Or Display: Project,AI Chat
	Provides Bot Behavior Actions MCP Tools: Bot Behavior Action Tool
	Provides Bot Behavior Tools: Bot Behavior Tool
	Provides Bot Tools: Bot Tool
	Provides Project State Tool: Project State Tool
	Routes Tool Calls: AI Chat,Bot Tools
	Routes To Specific MCP Tool Based On Trigger Words: AI Chat,Bot Tool,Behavior Tool,Behavior Action Tool

AI Chat
	Detects Trigger Words And Routes To Tools: Human,Bot Server,MCP Bot Tools,Bot Tool,Project State Tool,Behavior Tool,Behavior Action Tool
	Presents Information To Human: Human,All tools
