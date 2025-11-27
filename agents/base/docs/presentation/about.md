
# AI augmented product delivery is powerful, it requires precision to avoid frendly fire

Using AI to deliver enhancew product delivery of technology solutions sooner can be incredibly powerful—but without the right guardrails, that power quickly becomes unreliable.

It can generate fluent, convincing results that
- that crumble over time
- that it, and you don’t understand
- are unsafe and unsound
- are plain wrong

*What is the biggest bottleneck facing organizations that making heavy use of AI to augment their software delivery today?*
  
-  
-  
-  
-  
-  
-  
-  
-  
-  
-  
-  
-   
-  
-  
-  
-   
-  
-  
-  
-  
-  
-----------------------
# Even more than before Human Alignment and Human Collaboration remain the biggest bottlenecks in an AI Augmented World

*Humans Code Review* - senior developers and architects are struggling to ensure that AI gnerated code meets reasonable quality ad safety standards and supports business acceptance criteria.

When left to its own devices, using AI to enhance product delivery:

**Builds the Wrong Thing**
- Makes the wrong assumptions about goals, context, and priorities.
- Generates plausible nonsense — confident but contradictory even meaningless output.
- Acts with runaway behavior — it delivers too much, too quickly, without pausing to check, validate, or explain its reasoning.

**Builds the thing wrong**
- “Vibe-codes” and “vibe-delivers” — producing work that feels right but collapses under safety, scrutiny and scale
- Mimics bad habits of examples found on the Internet.
- Requires constant reminders — forgets what you tell it and reverts back to mediocre results.  
  
  
*What are some of the things we can doto guide AI human interaction in a way that dramatically accelerates product delivery*
  
-  
-  
-  
-  
-  
-  
-  
-  
-  
-  
-  
-   
-  
-  
-  
-   
-  
-  
-  
-  
-  
-----------------------
# Truly accelerated AI augmented product delivery is made possible through a setup that :

- **Requres Verification**
AI Proactively capture missing context, and align on human chosen strategy before continuing

- **Continuously Self-Correction**
AI behavior refines it's behavior in real time based on human feedback.

- **Gated Human Judgment**
AI pauses after each small increment of work to present outputr to for human feedbak.

- **Audits every Step**
AI Audits every step, tracing and recording every artifact, generation, and decision — making it easy to follow cause and effect throughout its workflow.

- **Incorperates Agile Best Practices**	
AI guide humans toward better delivery practices that keep AI on track. 
-- Small batches, iterative and incremental with frequent feedback
-- Hierarchical, story-driven requirements
-- Test Driven Development 
-- Domain Driven Modularization
-- Disciplined Service / Object Oriented design and programmming
-  
-  
-  
-   
-  
-  
-  
-   
-  
-  
-  
-   
-  
-  
-  
-   
-  
-  
-  
-  
-  
-----------------------

# Agile Bot
*Agile By Design has assembled a lightweight framework that implements these concepts. Agile bots have been designed to be easily installable on  development environments commonly found in scotiabank, such as Visual Studio Code.*

Agile bot is a colleciton of agents that provide an AI enabled delivery system that aligns analysts, developers, and testers to deliver usingagile principles -  accelerating best in class quality delivery through safe, human-in-the-loop, workflow.
- **Storybot** - Guided story mapping, discovery, and exploration workflows, transforming product vision into hierarchical user stories with acceptance criteria, executable specification and test code.
- **Domain Bot** - Produces domain models that apply Domain-Driven Design principles to identify core concepts, behaviors, and business rules.
- **Architecture Bot** -  aligns an architecture template to stories and domains to quickly generate production level codethat supports requirements while aligning to a specific technology choices and non functional requirements
- **BDD Bot** - Orchestrates Beavior Driven Developmment practices to develop micro tests that are business readable and ensure test-driven development discipline.
- **Clean Code Bot** - Genertes and Validates code quality against clean code principles and provides refactoring guidance, catching violations through automated heuristics and AI-powered semantic analysis.
-  
-  
-   
-  
-  
-  
-   
-  
-  
-  
-   
-  
-  
-  
-   
-  
-  
-  
-  
-  
-----------------------
# Agile Bot In A Nutshell

* Each agile bot guids team members through an *guided and iterative* workflow that generating product delivery artifacts using a particular set of agile practices (EG Story-Bot --> Story Shaping to Story Testting)
* Each bot work closely with a team member to *verify context upfront, and align on assumptions and strategy* before proceeding, and pause for human judgment at every step.
* Each bot generates a *semantically structured* JSON representation of all knowledge being captured (eg story-graph.json) — and then renders knowledge into multiple artifact formats using templates.
* Generation of all knowledge is guided by rules and examples taken from our *Agile By Design bootcamps / training material*, and is easily extended with working examples delivered as part of client usage.
* Each bot works with *comprehensive auditability* in mind step every decision and every relationshipis maintained
* All behavior, artifacts, knowledge , and workflows are *configurable* and can be customizedto suit the needs of the context of the team.



# Story Bot Demo
This is a demo of a solution that is *a work in progress* 
* some of the rough edges still need to be sanded down abd polish
* it should be a good demonstration of how this kind of approach can really accelerate upstream work

## Story Bot Behaviors

Storybot guides product owners and analysts through eight sequential behaviors that transform product vision into executable specifications and test code. Each behavior follows the same structured workflow, ensuring consistency and quality throughout the story development lifecycle.

**Shape**
* Creates the initial story map (epics, features, stories) from product vision and existing business cases, tech specs, waterfall specs, or from scratch
* identifies users, user - system interactions, and high-level workflows
* drills down on specific parts of the map based on user guidance

**Prioritization**
* Organizes stories into thin-slices value increments according to user guidance
* Prioritizes them based on value and risk assumptions

**Discovery**
* Expands stories for increment(s) in focus by enumerating all user-system interactions and component-level stories
* Performs decomposition to level of detail based on planning decisions

**Exploration**
* Adds acceptance criteria (Domain AC and Behavioral AC) to stories
* Defines "done" criteria in When/Then

**Specification Scenarios**
* Writes plain English Gherkin scenarios (Given/When/Then) for each story
* Defines step-by-step flows with Background sections for shared setup across multiple scenarios

**Specification Examples**
* Adds test data by converting scenarios to Scenario Outlines with Examples tables
* Provides concrete values for formulas, domain entities, and parameter variations

**Specification Tests**
* generates pytest BDD feature files
* Generates pytest-bdd test code from feature files
* Creates executable acceptance tests with step definitions that match feature files exactly
* Runs test as required once coding is done    

## Actions Within Behaviors

Each behavior uses the following gauardrails:
- **Clarification** - Verifies context by asking domain-specific questions, analyzing available information, and flagging missing details before proceeding.
- **Planning** - Presents assumptions and decision criteria for human selection, documenting choices that guide all subsequent generation and ensuring the AI follows your strategy.
- **Build Structure** - Generates semantic JSON structures following domain schemas, separating logic from presentation and enabling single-source generation of multiple artifact types.
- **Render Output** - Transforms structured JSON into rendered artifacts using configurable templates, creating markdown documents, diagrams, and other output formats.
- **Validate** - Checks content against rules using automated diagnostics and AI-powered semantic analysis, identifying violations and missing requirements.
- **Correct** - Applies fixes to the AI bot based on validation feedback and user corrections, updating it's behavior in real time.







