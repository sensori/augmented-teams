# Domain Outline: Agile Bot Framework

## Actors


Base Bot
    Executes Actions:  Workflow,  Behavior, Action
    (one of Initialize ProjectAction, GatherContextAction, PlanningAction, BuildKnowledgeAction, RenderOutputAction, ValidateRulesAction, CorrectBotAction )
    
    Track activity: Behavior, Action
    Route to behaviors and actions: Router, Trigger Words
    Persist content: Content
    Manage Project State: Project

    Render

Specific Bot
    Provide Behavior config: Bot Config,  Behavior
    Provide MCP config:  MCP Config
    Provide Renderers
    Provide Extractors
    Provide Synchronizer 
    Provide Trigger Words   

Workflow
    Orders Behavior Action Steps: Agile Bot, Bot Behavior
    Determines Next Action From Current Action: Current Action, Completed Actions (Fallback), Action Configuration, Transitions
    Checks If Action Is Completed: Completed Actions, Workflow State
    Saves Completed Action To Workflow State: Workflow State, Completed Actions, File System
    Transitions To Next Action In Behavior: State Machine, Action Configuration, Transitions
    Detects Final Action In Behavior: Action Configuration, State Machine
    Transitions To Next Behavior When Final Action Complete: Bot Config, Behavior, Workflow State
    Initializes Next Behavior At First Action: Behavior, Action Configuration, State Machine
    Loads State From workflow_state.json: Workflow State, File System
    Persists State To workflow_state.json: Workflow State, File System

Project
    Move project to working area: Working Directory
    Save project in context: Working Directory, Workflow State
    Update project area: Working Directory, Content

Behavior
    Perform Configured Actions: Actions
    Invoke On Trigger Words: List
    Inject Instructions: Text
    Provide Guardrails: GuardRails
    Provide Rules: Rule, Validation
    Provide Content Specs: Content

Base Action
    Inject Instructions: Behavior  #must be overridden
    Load Relevant Content + Inject Into Instructions: Content  #must be overridden
    Save content changes: Content #must be overriden
    Loads Action Configuration: Action Configuration, File System
    Injects Next Action Instructions (if workflow: true and next_action exists): Action Configuration, AI Chat

GatherContextAction (Action 2)
    Inject gather context instructions: Behavior, Guardrails, Required Clarifications
    Inject questions and evidence:  Behavior, Guardrails,  Key Questions, Evidence

PlanningAction (Action 3)
    Inject planning instructions:  Behavior, Guardrails, Planning
    Inject decision criteria and assumptions:Behavior, Guardrails, Decision Criteria, Assumptions, Recommended Human Activity
   

BuildKnowledgeAction (Action 4)
    Inject knowledge graph template: Behavior, Content, Knowledge Graph Spec, Knowledge Graph 
    Inject builder instructions: Behavior, Content, Build Instructions
    Save Knowledge graph: Behavior, Content,  Knowledge Graph
    

RenderOutputAction (Action 5)
    Inject render output instructions: Behavior, Content, Render Spec, Renderer
    Inject templates: Behavior, Content, Render Spec, Template
    Inject transformers: Behavior, Content, Transformer
    Load + inject structured content: Behavioe, Content, Knowledge Graph



ValidateRulesAction (Action 6)
    Inject common bot rules: Base Bot, Rules, Common Rules
    Inject behavior specific and Bot rules: Behavior, Rules, Behavior Rules
    Load + inject content for validation: Behavior, Content, Knowledge Graph, Rendered Outputs
    Load + inject diagnostics results: Behavior, Rules, Violations,

CorrectBotAction (Action 7)
    Inject correct bot instructions: Behavior, Correct Bot Instructions
    Load + inject diagnostics results: Content, Diagnostic Report, Violations, Suggestions


Guardrails
    Provide required context: Key Questions, Evidence
    Guide planning decisions: Decision Criteria, Assumptions
    Define recommended human activity: Human, Instructions

Content
    Render outputs: Template, Renderer, Render Spec
    Synchronize formats: Synchronizer, Extractor, Sunchronizer Spec
    Save knowledge graph: Knowledge Graph
    Load rendered content: na
    Present rendered content: na


SpecificMCPServer
   managesSpecificTools

SpecificBotTool
  providesBehaviorActionConfig : Behavior, Action
  providesBehaviorCOnfig: Config
  providesTriggerWordConfi
  provideSpecificBotCOnfig

BaseMCPServer
    hasehaviorTools
    hasBehaviorActionsTools
    hasBotTool

Bot Tool (examples: story_bot, story_bot_close_current_action)
    Runs Active Action On Active Behavior: Agile Bot, Project, Project Bot State, Workflow State, Bot Behavior, Bot Action
    Closes Current Action Explicitly: Workflow, Workflow State, Completed Actions
    Checks If Action Is In Completed Actions Before Closing: Workflow, Completed Actions, Workflow State
    Returns Error If Action Requires Confirmation: Completed Actions, AI Chat
    Transitions To Next Action When Action Complete: Workflow, Action Configuration, Workflow State
    Transitions To Next Behavior When Final Action Complete: Workflow, Bot Config, Behavior, Workflow State
    Initializes Next Behavior At First Action: Workflow, Behavior, Action Configuration
    Handles Idempotent Completion: Completed Actions, Workflow State
    

BotBehaviorTool
     Forward to action: Behavior, Action, Specific Bot

BehavioralActionTool
    invokeAction, Behavior, Action, SPecificBot

Template
    Define output structure: Placeholder
    Transform content: Transformer, Content
    Load template: Behavior, Content

Extractor / Synchronizer
    Extract from source: Template, Knowledge Graph
    Load + inject rendered content: AI Chat, Content

Renderer
    Render complex output: Template, Knowledge Graph, Transformer
    Render outputs using components in context: AI Chat, Template, Content

Rule
    Description: Test
    Provide examples:
        Do: Example, Description
        Dont: Example, Description
    Specialized examples: Language, Framework, Pattern

Action Configuration
    Specifies Action Name
    Specifies Workflow Flag: true/false
    Specifies Order In Workflow Sequence: Workflow
    Specifies Next Action In Sequence: Workflow, Base Action
    Stored In action_config.json Per Action Folder: File System

Router
    Checks Workflow State For Current Behavior: Workflow State
    Loads workflow_state.json From Project Area: Workflow State, File System
    Extracts current_behavior And current_action From State: Workflow State
    Routes To Current Behavior's MCP Tool: MCP Bot Server, Behavior Tool
    Forwards To Bot.Behavior[current_behavior].Action[current_action]: Bot Behavior, Base Action
    Defaults To First Behavior/Action If No State Exists: Bot Behavior, Base Action

Activity Log
    Records Action Execution With Timestamp: Base Action, File System
    Stores Behavior And Action Names: Bot Behavior, Base Action
    Stores Violations Count For Validation: ValidateRulesAction
    Links Action To Generated Content File Path: Base Action, File System
    Provides Audit Trail: Project
    Persists To activity_log.json: File System, Project

Workflow State
    Stores Current Behavior Name: Behavior
    Stores Current Action Name: Action
    Stores Action State (started/completed)
    Stores Completed Actions List
    Stores Timestamp
    Enables Workflow Resumption

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/story-graph.json
**Phase**: Shape - Initial domain modeling
**Date Generated**: 2025-12-02
**Context**: Explicit story-to-behavior mapping from story graph, including Human and AI Chat as primary actors in the bot workflow.
