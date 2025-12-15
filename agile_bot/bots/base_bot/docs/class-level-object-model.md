# Class-Level Object Model (CRC Format)

## Design Philosophy

- **Configuration-Driven**: Classes mirror the folder/JSON structure
- **Property-Oriented**: Objects expose data via properties
- **Ask-Don't-Tell**: Objects expose capabilities; callers ask for what they need
- **Constructor Injection**: Collaborators injected at instantiation, not per method call
- **Config Abstraction**: Configuration files fronted by classes for future flexibility
- **State on Collections**: Behaviors and Actions own their state (current, next, close)

---

## Bot (Top Level)

Bot
    Instantiated with: Bot Name, Workspace
    Instantiates: Behaviors, Rules
    bot directory: Workspace
    workspace directory: Workspace
    behaviors: Behaviors
    rules: Rules
    Execute: Behaviors

BotConfig
    Instantiated with: Bot Name, Workspace
    name: Workspace
    behaviors list: Workspace
    base actions path: Workspace

---

## Behaviors and Behavior

Behaviors
    Instantiated with: BotConfig
    Instantiates: Behavior
    current: Behavior (persisted)
    Find by name: Behavior
    next: Behavior
    Iterate: Behavior
    Check exists: Behavior
    Navigate to: Behavior
    Close current: Behavior
    Execute current: Behavior
    Save state: Workspace
    Load state: Workspace

Behavior
    Instantiated with: Name, BotConfig
    Instantiates: Guardrails, Content, Rules, Actions, TriggerWords
    folder: Workspace
    guardrails: Guardrails
    content: Content
    rules: Rules
    actions: Actions
    Matches trigger: TriggerWords
    description: BehaviorConfig
    goal: BehaviorConfig
    inputs: BehaviorConfig
    outputs: BehaviorConfig

BehaviorConfig
    Instantiated with: Behavior, Workspace
    behavior name: Workspace
    description: Workspace
    goal: Workspace
    inputs: Workspace
    outputs: Workspace
    base actions path: Workspace
    instructions: Workspace
    trigger words: Workspace
    actions: Workspace

TriggerWords
    Instantiated with: Behavior, BehaviorConfig
    Match pattern: BehaviorConfig
    priority: BehaviorConfig

Actions
    Instantiated with: Behavior, BaseActionsConfig, BehaviorConfig
    Instantiates: Action
    current: Action (persisted)
    Find by name: Action
    Find by order: Action
    next: Action
    Iterate: Action
    Navigate to: Action
    Close current: Action
    Execute current: Action
    Save state: Workspace
    Load state: Workspace

Action
    Instantiated with: Actions, BaseActionConfig, BehaviorConfig
    instructions: BaseActionConfig, BehaviorConfig
    action class: BaseActionConfig
    order: BaseActionConfig
    Execute: Behavior

BaseActionConfig
    Instantiated with: Actions, Workspace
    order: Workspace
    next action: Workspace
    custom class: Workspace
    instructions: Workspace

---

## Base Actions

BaseActions
    Instantiated with: Bot, BotConfig
    Instantiates: BaseActionConfig, BaseInstructions
    Find folder: BotConfig
    instructions for: BaseInstructions

BaseInstructions
    Instantiated with: BaseActions
    instructions: Workspace

BaseAction
    Instantiated with: Behavior, ActivityTracker
    Execute: Behavior, ActivityTracker
    Do execute: Behavior (abstract)
    Track activity start: ActivityTracker
    Track activity completion: ActivityTracker
    Inject next behavior reminder: Behaviors
    workspace directory: Workspace
    base actions directory: Workspace

---

## Guardrails

GatherContextAction (extends BaseAction)
    Instantiated with: Behavior, BaseActionsConfig, BehaviorConfig
    Generates Instructions To Clarify Requirements: RequiredContext, KeyQuestions, Evidence
    required context: RequiredContext
    key questions: KeyQuestions
    evidence: Evidence
    Save clarification: RequirementsClarifications, Workspace

PlanningAction (extends BaseAction)
    Instantiated with: Behavior, BaseActionsConfig, BehaviorConfig
    Generates Instructions For Planning Decisions: PlanningCriteria, DecisionCriteria, TypicalAssumptions, RecommendedHumanActivity, Behavior.Instructions
    planning crriteria: PlanningCriteria
    decision criteria: DecisionCriteria
    typical assumptions: TypicalAssumptions
    recommended activities: RecommendedHumanActivity
    Save planning: PlanningDecision, Workspace

Guardrails
    RequiredContext
    Planning
    Instructions:

RequiredContext
    KeyQuestions, 
    Evidence
    Instructions

KeyQuestions
    Questions: 

Evidence
    evidence list: 

RequirementsClarifications
    Answered For RequiredContext
    Answers: RequiredContext, Key Questions
    Evidence provided: RequiredContext, Evidence   
    

PlanningCriteria
    DecisionCriterias
    assumptions:List 
    RecommendedHumanActivity: list
    Instructions

DecisionCriteria
    question
    options
    outcome


PlanningDecision
    Decided on planning criteria : PlanningCriteria
    decisions : PlanningCriteria, DecisionCriteria,
    typical assumptions:PlanningCriteria,  Assumptions
    recommended activities: PlanningCriteria, RecommendedHumanActivity

---

## Content

BuildKnowledgeAction (extends BaseAction)
    Instantiated with: Behavior
    Generates Instructions To Build Knowledge Graph: Knowledge, KnowledgeGraphSpec, KnowledgeGraph, KnowledgeGraphTemplate, ValidateRulesAction
    knowledge graph spec: KnowledgeGraphSpec
    knowledge graph template: KnowledgeGraphTemplate
    rules: ValidateRulesAction
    Save knowledge graph: KnowledgeGraph, Workspace

RenderOutputAction (extends BaseAction)
    Instantiated with: Behavior
    Generates Instructions To Render Outputs: RenderSpec, Template, Synchronizer
    render specs: RenderSpec
    templates: Template
    synchronizers: Synchronizer
    Save rendered content: RenderedContent, Workspace

Content
    Knowledge: Knowledge
    render specs: RenderSpec
    synchronizers: Synchronizer
    instructions:
Knowledge.
    KnowledgeGraphSpec
    instruction
    KnowledgeGraphTemplate

KnowledgeGraphSpec
    output path
    output filename
    template filename

KnowledgeGraphTemplate
    schema

StoryGraphTemplate: KnowledgeGraphTemplate
    Epics, 
    sub-epics, 
    stories, 
    scenarios, 
    increments, 
    domain concepts.

KnowledgeGraph

StoryGraph: KnowledgeGraph
    Story Map

StoryMap
    Instantiated with: Story Graph JSON
    epics: Story Graph JSON
    domain concepts: DomainConcept

Epic
    sub epics: SubEpics
    domain concepts: DomainConcept
    
SubEpic
    sub epics: Sub Epic
    story groups: StoryGroup
    domain concepts:  DomainConcept 

StoryGroup
    stories: Stories

Story
    scenarios: Scenario
    test file: Test
    



Scenario
    name
    steps
    test method

ScenarioOutline
    name
    background
    examples
    steps
    test method
   

DomainConcept
    May Inherit From: DomainConcept
    name
    description
    responsibility DomainResponsibility
    Collaborators DomainConcept

DomainResponsibility
    Name
    Descriptions
    CollabotatesWith: DomainConcept



    

RenderSpec
    input: KnowledgeGraph
    output: Document Name
    template: Template
    Synchronizer: Synchronizer
    instructions

Template
    content

Synchronizer
    (leave blank for now)


MergedInstructions
    base instructions: BaseActions
    render instructions: RenderSpec

Instructions
    base instructions: BaseActions
    behavior instructions: Behavior

---

## Validation

ValidateRulesAction (extends BaseAction)
    Instantiated with: Behavior
    Generates Instructions To Validate Against Rules: Rules, ValidationContext, ValidationScope
    rules: Rules
    validation context: ValidationContext
    validation scope: ValidationScope
    Collect violations: Violations
    violation: Violation
    Save validation report: ValidationReport, Violations, Workspace

Rules
    Find by name: Rule
    Iterate: Rule
    Instructions : Rule

Rule
    description
    examples
    scanner: Scanner
    Instruction

ValidationContext
    rendered outputs
    clarification file
    planning file
    report path

ValidationScope
    file paths scope
    story graph scope

Scanner (Abstract)
    rule: Rule
    Scan: ValidationScope -> Violation

StoryScanner (extends Scanner)
    rule: Rule

TestScanner (extends Scanner)
    rule: Rule

CodeScanner (extends Scanner)
    rule: Rule


Violation
    Validates Rule: Rule
    message
    line number
    location
    severity

ValidationReport
    violations: Violations
    validation context: ValidationContext

---

## Knowledge Graph Classes



---

## CLI Classes

BaseBotCli
    Instantiated with: Bot
    Instantiates: HelpContent, CursorCommands
    Route to actions: Bot
    Parse arguments: Bot


CLIParameters
    Instantiated with: Argument List
    behavior name: Argument List
    action name: Argument List
    file paths: Argument List

HelpContent
    Instantiated with: BaseBotCli
    Generate behaviors help: Behaviors
    Generate cursor commands help: CursorCommands
    action description: BaseActions
    behavior description: Behaviors

ParsedArguments
    Instantiated with: Argument List
    Parse: Argument List
    Parse action parameters: Argument List
    Detect file paths: Argument List

CursorCommands
    Instantiated with: BaseBotCli
    Generate all: Behaviors
    current files: Workspace
    Remove obsolete: Workspace
    Write command file: Workspace

CliGenerator
    Instantiated with: Workspace
    Instantiates: GeneratedCLICode
    Generate CLI: GeneratedCLICode
    Update bot registry: BotRegistry

GeneratedCLICode
    Instantiated with: Bot, BotConfig
    Generate python CLI: Bot, Workspace
    Generate shell script: Bot, Workspace
    Generate PowerShell script: Bot, Workspace

BotRegistry
    Instantiated with: Workspace
    Update registry: Workspace
    Load trigger patterns: Workspace

TriggerRouter
    Instantiated with: Bot, BotConfig
    Match trigger patterns: TriggerWords
    Route to bot: BotRegistry
    Route to behavior: TriggerWords
    Route to action: TriggerWords

---

## MCP Classes

MCPServerGenerator
    Instantiated with: Bot, BotConfig
    Instantiates: FastMCP, Tools, GeneratedMCPCode, WorkspaceRules
    Create server: FastMCP
    Register tools: Tools
    Generate code: GeneratedMCPCode
    Generate rules: WorkspaceRules

Tools
    Instantiated with: MCPServerGenerator, MCP Server
    Register all: Bot, Behaviors
    Register bot tool: Bot
    Register behavior tools: Behaviors
    Register close action tool: Actions
    Register confirm out-of-order tool: Actions
    Register restart server tool: MCP Server

GeneratedMCPCode
    Instantiated with: MCPServerGenerator, BotConfig
    Generate server entry point: Bot, Workspace
    Generate cursor MCP config: Bot, Workspace
    Generate bot config file: Behaviors, Workspace

WorkspaceRules
    Instantiated with: MCPServerGenerator, BotConfig
    Generate rules file: Bot, Workspace
    Load trigger words: Behaviors

---

## Utility Classes

Workspace
    Instantiated with: Workspace Path
    workspace directory: Workspace Path
    bot directory: Workspace Path
    base actions directory: Workspace Path
    python workspace root: Workspace Path
    Find repo root: Workspace Path

ActivityTracker
    Instantiated with: Bot
    Track action start: Bot, Workspace
    Track action completion: Bot, Workspace

Docs
    Instantiated with: Behavior
    Instantiates: StoryMap
    clarification: Workspace
    planning: Workspace
    validation report: Workspace

TestFiles
    Instantiated with: Workspace
    Discover: Workspace
    Resolve paths: FilePathResolver

CodeFiles
    Instantiated with: Workspace
    Discover: Workspace
    Resolve paths: FilePathResolver
    Filter by extension: Workspace

FilePathResolver
    Instantiated with: Workspace
    Resolve file paths: Workspace
    Normalize paths: Workspace

BotResult
    Instantiated with: Status, Behavior, Action, Data
    Return from action: Behavior, Action
