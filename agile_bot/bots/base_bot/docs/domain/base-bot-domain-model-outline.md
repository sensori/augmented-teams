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

Behavior Workflow
    Determine next Action:  Behavior, Action, State
    Track state:  Behavior, Action, State

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

BotTool
    Forward to behavior: Behavior, Specific Bot
    Forward to current behavior and action: Behavior, Action, Specific Bot
    

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

Workflow State
    Track current action: Action
    Track completed actions: Action, Activity Log
    Determine next action: Action, Behavior
    Pause workflow: Human, AI Chat
    Resume workflow: Human, AI Chat

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/story-graph.json
**Phase**: Shape - Initial domain modeling
**Date Generated**: 2025-12-02
**Context**: Explicit story-to-behavior mapping from story graph, including Human and AI Chat as primary actors in the bot workflow.
