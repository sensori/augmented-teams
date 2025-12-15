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
    Instantiated with: Bot Name, BotPath
    Instantiates: Behaviors, Rules
    bot directory: BotPath
    BotPath directory: BotPath
    behaviors: Behaviors
    rules: Rules
    Execute: Behaviors

BotConfig
    Instantiated with: Bot Name, BotPath
    name: BotPath
    behaviors list: BotPath
    base actions path: BotPath

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
    Inject next behavior reminder: Behavior
    Save state: BehaviorActionState, BotPath
    Load state: BehaviorActionState, BotPath

Behavior
    Instantiated with: Name, BotConfig
    Instantiates: Guardrails, Content, Rules, Actions, TriggerWords
    folder: BotPath
    guardrails: Guardrails
    content: Content
    rules: Rules
    Execute Current: Actions, Action
    actions: Actions
    Matches trigger: TriggerWords
    description: BehaviorConfig
    goal: BehaviorConfig
    inputs: BehaviorConfig
    outputs: BehaviorConfig

BehaviorConfig
    Instantiated with: Behavior, BotPath
    behavior name: BotPath
    description: BotPath
    goal: BotPath
    inputs: BotPath
    outputs: BotPath
    base actions path: BotPath
    instructions: BotPath
    trigger words: BotPath
    actions: BotPath
    Order: Number

TriggerWords
    Instantiated with: Behavior, BehaviorConfig
    Match pattern: BehaviorConfig
    priority: BehaviorConfig



---

## Actions
Actions
    Instantiated with: Behavior, BehaviorConfig
    Instantiates: Action
    current: Action (persisted)
    Find by name: Action
    Find by order: Action
    next: Action
    Iterate: Action
    Navigate to: Action
    Close current: Action
    Execute current: Action
     Inject next action reminder: Action
    Save state: BotPath, BehaviorActionState
    Load state: BotPath, BehaviorActionState
    BotPath directory: BotPath
    base actions directory: BotPath

Action
    Instantiated with: BaseActionConfig, Behavior, ActivityTracker
    Instructions: BaseActionConfig, Behavior
    action class: BaseActionConfig
    order: BaseActionConfig
    Execute: instructions, Instructions
    Track activity start: ActivityTracker
    Track activity completion: ActivityTracker
    

BaseActionConfig
    Instantiated with:  BotPath
    order: number
    next action: BaseActionConfig
    custom class: class
    instructions: 

---

## Guardrails

GatherContextAction (extends Action)
    Instantiated with: Behavior, BaseActionsConfig, BehaviorConfig
    Generates Instructions To Clarify Requirements: RequiredContext, KeyQuestions, Evidence
    required context: RequiredContext
    key questions: KeyQuestions
    evidence: Evidence
    Save clarification: RequirementsClarifications, BotPath

DecideStrategyAction (extends Action)
    Instantiated with: Behavior, BaseActionsConfig, BehaviorConfig
    Generates Instructions For Stratgegy Decisions: Strategy, StrategyCriteria, TypicalAssumptions, RecommendedHumanActivity, Behavior.Instructions
    strategy: Strategy
    strategy criteria: StrategyCriteria
    typical assumptions: TypicalAssumptions
    recommended activities: RecommendedHumanActivity
    Save strategy: StrategyDecision, BotPath

Guardrails
    RequiredContext
    Strategy
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
    

Strategy
    StrategyCriterias
    assumptions:List 
    RecommendedHumanActivity: list
    Instructions

StrategyCriteria
    question
    options
    outcome


StrategyDecision
    Decided on strategy : Strategy
    decisions : Strategy, StrategyCriteria,
    typical assumptions:Strategy,  Assumptions
    recommended activities: Strategy, RecommendedHumanActivity

---

## Content

BuildKnowledgeAction (extends BaseAction)
    Instantiated with: Behavior
    Generates Instructions To Build Knowledge Graph: Knowledge, KnowledgeGraphSpec, KnowledgeGraph, KnowledgeGraphTemplate, ValidateRulesAction
    knowledge graph spec: KnowledgeGraphSpec
    knowledge graph template: KnowledgeGraphTemplate
    rules: ValidateRulesAction
    Save knowledge graph: KnowledgeGraph, BotPath

RenderOutputAction (extends BaseAction)
    Instantiated with: Behavior
    Generates Instructions To Render Outputs: RenderSpec, Template, Synchronizer
    render specs: RenderSpec
    templates: Template
    synchronizers: Synchronizer
    Save rendered content: RenderedContent, BotPath

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


Story Node:
    Name 
    Description 
    Get children :Story Node
    Iterate Children: Story Node
    

StoryMap : Story Node
    Instantiated with: Story Graph JSON
    epics: Story Graph JSON
    domain concepts: DomainConcept

Epic: Story Node
    sub epics: SubEpics
    domain concepts: DomainConcept
    
SubEpic: Story Node
    sub epics: Sub Epic
    story groups: StoryGroup
    domain concepts:  DomainConcept 

StoryGroup: Story Node
    stories: Stories

Story: Story Node
    scenarios: Scenario
    test file: Test
    
Scenario : Story Node
    name
    steps
    test method

ScenarioOutline : Story Node
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
    Save validation report: ValidationReport, Violations, BotPath

Rules
    Find by name: Rule
    Iterate: Rule
    Instructions : Injected instructions

Rule
    description
    examples
    scanner: Scanner
    Injected Instruction:

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
    Scan Story Node: Story Node
    Scan: StoryGraph.

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
    current files: BotPath
    Remove obsolete: BotPath
    Write command file: BotPath

CliGenerator
    Instantiated with: BotPath
    Instantiates: GeneratedCLICode
    Generate CLI: GeneratedCLICode
    Update bot registry: BotRegistry

GeneratedCLICode
    Instantiated with: Bot, BotConfig
    Generate python CLI: Bot, BotPath
    Generate shell script: Bot, BotPath
    Generate PowerShell script: Bot, BotPath

BotRegistry
    Instantiated with: BotPath
    Update registry: BotPath
    Load trigger patterns: BotPath

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
    Instantiates: FastMCP, Tools, GeneratedMCPCode, BotPathRules
    Create server: FastMCP
    Register tools: Tools
    Generate code: GeneratedMCPCode
    Generate rules: BotPathRules

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
    Generate server entry point: Bot, BotPath
    Generate cursor MCP config: Bot, BotPath
    Generate bot config file: Behaviors, BotPath

BotPathRules
    Instantiated with: MCPServerGenerator, BotConfig
    Generate rules file: Bot, BotPath
    Load trigger words: Behaviors

---

## Utility Classes

BotPaths
    Instantiated with: BotPath Path (optional)
    BotPath directory: BotPath Path
    bot directory: BotPath Path
    base actions directory: BotPath Path
    python BotPath root: BotPath Path
    Find repo root: BotPath Path

ActivityTracker
    Instantiated with: Bot
    Track action start: Bot, BotPaths
    Track action completion: Bot, BotPaths

Docs
    Instantiated with: Behavior
    Instantiates: StoryMap
    clarification: BotPaths
    planning: BotPaths
    validation report: BotPaths

TestFiles
    Instantiated with: BotPaths
    Discover: BotPaths
    Resolve paths: FilePathResolver

CodeFiles
    Instantiated with: BotPaths
    Discover: BotPaths
    Resolve paths: FilePathResolver
    Filter by extension: BotPaths

FilePathResolver
    Instantiated with: BotPaths
    Resolve file paths: BotPaths
    Normalize paths: BotPaths

BotResult
    Instantiated with: Status, Behavior, Action, Data
    Return from action: Behavior, Action
