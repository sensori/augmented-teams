# Domain Model Diagram: Agile Bot Framework

## Complete Domain Model Class Diagram

```mermaid
classDiagram
    class BaseBot {
        +Executes Actions()
        +Track activity()
        +Route to behaviors and actions()
        +Persist content()
        +Manage Project State()
        +Render()
    }
    
    class SpecificBot {
        +Provide Behavior config()
        +Provide MCP config()
        +Provide Renderers()
        +Provide Extractors()
        +Provide Synchronizer()
        +Provide Trigger Words()
    }
    
    class BehaviorWorkflow {
        +Determine next Action()
        +Track state()
    }
    
    class Project {
        +Move project to working area()
        +Save project in context()
        +Update project area()
    }
    
    class Behavior {
        +Perform Configured Actions()
        +Invoke On Trigger Words()
        +Inject Instructions()
        +Provide Guardrails()
        +Provide Rules()
        +Provide Content Specs()
    }
    
    class BaseAction {
        <<abstract>>
        +Inject Instructions()*
        +Load Relevant Content + Inject Into Instructions()*
        +Save content changes()*
    }
    
    class GatherContextAction {
        +Inject gather context instructions()
        +Inject questions and evidence()
    }
    
    class PlanningAction {
        +Inject planning instructions()
        +Inject decision criteria and assumptions()
    }
    
    class BuildKnowledgeAction {
        +Inject knowledge graph template()
        +Inject builder instructions()
        +Save Knowledge graph()
    }
    
    class RenderOutputAction {
        +Inject render output instructions()
        +Inject templates()
        +Inject transformers()
        +Load + inject structured content()
    }
    
    class ValidateRulesAction {
        +Inject common bot rules()
        +Inject behavior specific rules()
        +Load + inject content for validation()
    }
    
    class CorrectBotAction {
        +Inject correct bot instructions()
        +Load + inject diagnostics results()
    }
    
    class Guardrails {
        +Provide required context()
        +Guide planning decisions()
        +Define recommended human activity()
    }
    
    class Content {
        +Render outputs()
        +Synchronize formats()
        +Save knowledge graph()
        +Load rendered content()
        +Present rendered content()
    }
    
    class Router {
        +Match trigger patterns()
        +Route to MCP bot tool()
        +Route to behavior tool()
        +Route to action tool()
        +Forward to behavior()
        +Forward to action()
        +Forward to current behavior and action()
    }
    
    class Template {
        +Define output structure()
        +Transform content()
        +Load template()
    }
    
    class ExtractorSynchronizer {
        +Extract from source()
        +Load + inject rendered content()
    }
    
    class Renderer {
        +Render complex output()
        +Render outputs using components in context()
    }
    
    class Rule {
        +Validate content()
        +Find behavior specific rules from context()
        +Find common bot rules from context()
        +Load + inject diagnostics results()
        +Suggest corrections()
        +Provide examples Do()
        +Provide examples Dont()
        +Specialized examples()
    }
    
    class WorkflowState {
        +Track current action()
        +Track completed actions()
        +Determine next action()
        +Pause workflow()
        +Resume workflow()
    }
    
    %% Inheritance
    SpecificBot --|> BaseBot
    BaseAction <|-- GatherContextAction
    BaseAction <|-- PlanningAction
    BaseAction <|-- BuildKnowledgeAction
    BaseAction <|-- RenderOutputAction
    BaseAction <|-- ValidateRulesAction
    BaseAction <|-- CorrectBotAction
    
    %% Associations
    BaseBot --> BehaviorWorkflow : executes
    BaseBot --> Router : uses
    BaseBot --> Project : manages
    BaseBot --> Content : persists
    
    SpecificBot --> Behavior : provides
    SpecificBot --> Renderer : provides
    SpecificBot --> ExtractorSynchronizer : provides
    
    BehaviorWorkflow --> BaseAction : determines
    BehaviorWorkflow --> WorkflowState : tracks
    BehaviorWorkflow --> Behavior : uses
    
    Behavior --> Guardrails : provides
    Behavior --> Rule : provides
    Behavior --> Content : provides specs
    Behavior --> BaseAction : configures
    
    BaseAction --> Content : saves changes
    BaseAction --> Behavior : injects from
    
    GatherContextAction --> Guardrails : uses
    PlanningAction --> Guardrails : uses
    BuildKnowledgeAction --> Content : saves to
    RenderOutputAction --> Template : uses
    RenderOutputAction --> Renderer : uses
    ValidateRulesAction --> Rule : uses
    CorrectBotAction --> Rule : uses
    
    Content --> Template : rendered by
    Content --> Renderer : rendered by
    Content --> ExtractorSynchronizer : synced by
    
    Router --> Behavior : routes to
    Router --> BaseAction : routes to
    
    Template --> Content : transforms
    Rule --> Content : validates
```

---

## Source Material

**Primary Source**: agile_bot/bots/base_bot/docs/stories/story-graph.json  
**Domain Model**: agile_bot/bots/base_bot/docs/domain/base-bot-domain-model-outline.md  
**Phase**: Shape - Complete domain modeling  
**Date Generated**: 2025-12-02  
**Context**: Complete class diagram showing all domain concepts: Base Bot, Specific Bot, Behavior Workflow, Actions (1 abstract + 6 concrete), Behavior, Content, Guardrails, Rules, Router, Template, Renderer, Extractor/Synchronizer, Project, and Workflow State with all their relationships.
