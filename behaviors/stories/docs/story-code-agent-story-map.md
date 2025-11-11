# Story Code Agent - Story Map

## Product Vision
Build a complete story code agent feature following the code-agent pattern, with rules, commands, runners, templates, and heuristics based on Story Writing Training PowerPoint content.

## Target Users
- AI Agent (primary user - executes commands, generates/validates story artifacts)
- Development Teams (secondary - uses generated story artifacts for agile development)
- Product Owners (tertiary - reviews and validates story content)

## Main User Goals
- AI agent can guide teams through story writing stages (Shaping → Discovery → Exploration)
- Teams can generate well-structured story maps following agile best practices
- Teams can validate story artifacts against principles from training material
- Teams can create marketable increments with proper sizing and structure

## Scope Boundary
**In Scope:**
- Story writing commands for all 3 stages (Shaping, Discovery, Exploration)
- Rule files with principles from PowerPoint training
- Runner implementation with BDD TDD workflow
- Heuristics for validating story artifacts
- Templates for story maps, acceptance criteria, specifications
- Prompting questions integration for context gathering

**Out of Scope:**
- Actual story content generation for specific products (that's user's responsibility)
- Team collaboration tools integration
- Version control for story artifacts
- Story estimation calculations (deferred - calculation-heavy)

---

## Epic 1: Story Writing Foundation

### Feature 1.1: Story Writing Rules and Principles

#### Story 1.1.1: Create Story Rule File
**As an** AI agent  
**I want to** generate story rule file with principles from PowerPoint  
**So that** I can guide story writing with validated best practices

**Acceptance Criteria:**
- When AI generates rule file, then file contains frontmatter with description and globs
- When AI generates rule file, then file contains 5 principle sections (Section 0, 0.5, 1-3)
- When AI generates rule file, then each principle marked with command applicability (Universal, All Phases, Stage-specific, Command-specific)
- When AI generates rule file, then principles include DO/DON'T examples from PowerPoint
- When AI validates rule file, then structure matches required format (frontmatter, when/then, conventions, principles, commands)

**Size:** 5-7 days

#### Story 1.1.2: System Validates Rule File Structure
**As a** system  
**I want to** validate rule file against structure requirements  
**So that** rule file follows code-agent patterns

**Acceptance Criteria:**
- When system validates rule file, then checks for required sections (frontmatter, principles, commands)
- When system validates rule file, then verifies command applicability markers present
- When system validates rule file, then confirms DO/DON'T examples exist for each principle
- When system finds violations, then returns specific validation errors with line numbers

**Size:** 3-4 days

#### Story 1.1.3: Create Rule Command Files
**As an** AI agent  
**I want to** generate rule command files (main, generate, validate)  
**So that** users can execute rule commands via CLI

**Acceptance Criteria:**
- When AI generates rule commands, then creates 3 files (stories-rule-cmd.md, -generate-cmd.md, -validate-cmd.md)
- When AI generates rule commands, then each file follows command structure (Purpose, Rule, Runner, Actions)
- When AI generates rule commands, then files reference stories-rule.mdc as rule source
- When system validates rule commands, then verifies structure completeness

**Size:** 3-5 days

### Feature 1.2: Common Runner Enhancements

#### Story 1.2.1: Add Prompting Questions Concept
**As a** common runner  
**I want to** support prompting questions for commands  
**So that** commands can gather required context before execution

**Acceptance Criteria:**
- When developer adds prompting_questions to Command class, then attribute stores list of question strings
- When developer calls check_prompting_questions(), then method checks if questions answered in context
- When questions not answered, then AI generates prompts to ask user
- When questions answered, then command proceeds with normal flow
- When generate() or plan() called, then prompting questions checked FIRST

**Size:** 5-7 days

#### Story 1.2.2: System Integrates Prompting Questions into Workflow
**As a** system  
**I want to** automatically check prompting questions before generation  
**So that** commands have required context to execute properly

**Acceptance Criteria:**
- When system runs generate(), then checks prompting questions before proceeding
- When system runs plan(), then checks prompting questions before proceeding
- When prompting questions fail, then returns prompts to user and halts execution
- When prompting questions pass, then continues with normal command flow

**Size:** 3-4 days

---

## Epic 2: Story Shaping Stage

### Feature 2.1: Story Map Creation

#### Story 2.1.1: Generate Story Map Shell
**As an** AI agent  
**I want to** create initial story map with epic/feature/story hierarchy  
**So that** teams have structured starting point for story shaping

**Acceptance Criteria:**
- When AI generates story map, then creates epic/feature/story hierarchy structure
- When AI generates story map, then includes user AND system activities (not tasks)
- When AI generates story map, then uses business language (verb/noun patterns)
- When AI generates story map, then focuses on behavioral language (submits, validates, sends, displays)
- When AI generates story map, then avoids technical task language (implement, create, refactor)

**Size:** 7-10 days

#### Story 2.1.2: Elaborate Story Map Scope
**As an** AI agent  
**I want to** elaborate story map to understand full scope  
**So that** teams can see complete picture of work

**Acceptance Criteria:**
- When AI elaborates scope, then expands epics into features with story counts
- When AI elaborates scope, then extrapolates how many stories make up each feature
- When AI elaborates scope, then marks extrapolated counts (e.g., "~X stories")
- When AI elaborates scope, then ensures stories sized appropriately (3-12 day range)

**Size:** 5-7 days

#### Story 2.1.3: System Validates Story Map Structure
**As a** system  
**I want to** validate story map against shaping principles  
**So that** story map follows best practices

**Acceptance Criteria:**
- When system validates story map, then checks epic/feature/story hierarchy exists
- When system validates story map, then verifies user AND system activities present
- When system validates story map, then confirms business language usage (not generic functions)
- When system validates story map, then detects task-oriented language violations
- When system finds violations, then returns specific validation errors

**Size:** 5-7 days

### Feature 2.2: Marketable Increments Identification

#### Story 2.2.1: Identify Marketable Increments
**As an** AI agent  
**I want to** identify marketable increments in story map  
**So that** teams can plan value delivery

**Acceptance Criteria:**
- When AI identifies increments, then marks horizontal slices across features
- When AI identifies increments, then uses format "Increment 1: [Name]" or "MVI 1: [Name]"
- When AI identifies increments, then groups stories that deliver value together
- When AI identifies increments, then ensures increments span multiple features/stories

**Size:** 5-7 days

#### Story 2.2.2: Prioritize Marketable Increments
**As an** AI agent  
**I want to** prioritize increments based on value and dependencies  
**So that** teams can sequence delivery effectively

**Acceptance Criteria:**
- When AI prioritizes increments, then considers business priorities from context
- When AI prioritizes increments, then identifies dependencies between increments
- When AI prioritizes increments, then orders by value delivery potential
- When AI prioritizes increments, then documents prioritization rationale

**Size:** 3-5 days

#### Story 2.2.3: Apply Relative Sizing to Increments
**As an** AI agent  
**I want to** relatively size increments against previous work  
**So that** teams can estimate effort accurately

**Acceptance Criteria:**
- When AI sizes increments, then compares to previously completed work
- When AI sizes increments, then uses relative sizing (small/medium/large) at initiative/increment level
- When AI sizes increments, then considers platform and team skill similarity
- When AI sizes increments, then documents sizing comparisons

**Size:** 4-6 days

#### Story 2.2.4: System Validates Increment Identification
**As a** system  
**I want to** validate increment structure and completeness  
**So that** increments are well-defined

**Acceptance Criteria:**
- When system validates increments, then checks for clear boundaries (start/end stories)
- When system validates increments, then verifies increments deliver measurable value
- When system validates increments, then confirms stories appropriately sized
- When system validates increments, then ensures dependencies identified
- When system finds violations, then returns specific validation errors

**Size:** 4-6 days

---

## Epic 3: Discovery Stage

### Feature 3.1: Increment Refinement

#### Story 3.1.1: Refine Marketable Increments
**As an** AI agent  
**I want to** refine increments based on discovery insights  
**So that** increments are well-defined for delivery

**Acceptance Criteria:**
- When AI refines increments, then updates story map with discovery insights
- When AI refines increments, then adjusts boundaries based on new information
- When AI refines increments, then ensures increments remain well-defined
- When AI refines increments, then documents refinement changes

**Size:** 5-7 days

#### Story 3.1.2: Update Story Map During Discovery
**As an** AI agent  
**I want to** update story map based on discovery findings  
**So that** map reflects current understanding

**Acceptance Criteria:**
- When AI updates story map, then incorporates discovery insights into structure
- When AI updates story map, then adjusts story sizing based on new information
- When AI updates story map, then maintains consistency with shaping principles
- When AI updates story map, then tracks changes from original map

**Size:** 4-6 days

### Feature 3.2: Story Grooming

#### Story 3.2.1: Identify Ambiguous Stories
**As an** AI agent  
**I want to** detect stories that are too ambiguous  
**So that** teams can refine them before acceptance

**Acceptance Criteria:**
- When AI analyzes stories, then identifies stories lacking clear acceptance criteria
- When AI analyzes stories, then detects stories with vague titles or descriptions
- When AI analyzes stories, then flags stories with missing user/system activities
- When AI analyzes stories, then reports ambiguity violations with specifics

**Size:** 5-7 days

#### Story 3.2.2: Split Large Stories
**As an** AI agent  
**I want to** suggest splitting stories that are too large  
**So that** stories fit 3-12 day effort range

**Acceptance Criteria:**
- When AI analyzes story size, then identifies stories with 6+ acceptance criteria
- When AI analyzes story size, then detects multiple "and" statements in titles
- When AI analyzes story size, then suggests split points for large stories
- When AI suggests splits, then ensures each resulting story delivers value

**Size:** 5-7 days

#### Story 3.2.3: System Validates Discovery Activities
**As a** system  
**I want to** validate discovery artifacts against principles  
**So that** discovery follows best practices

**Acceptance Criteria:**
- When system validates discovery, then checks increment refinement completeness
- When system validates discovery, then verifies story map updates align with principles
- When system validates discovery, then confirms story grooming applied correctly
- When system finds violations, then returns specific validation errors

**Size:** 5-7 days

---

## Epic 4: Story Exploration Stage

### Feature 4.1: Acceptance Criteria Writing

#### Story 4.1.1: Generate Acceptance Criteria
**As an** AI agent  
**I want to** generate acceptance criteria in behavior form  
**So that** stories have testable conditions

**Acceptance Criteria:**
- When AI generates criteria, then uses "When...then..." or "Given...when...then..." format
- When AI generates criteria, then describes user/system interactions with behavioral language
- When AI generates criteria, then ensures observable outcomes
- When AI generates criteria, then avoids technical/task-oriented language
- When AI generates criteria, then avoids implementation details

**Size:** 7-10 days

#### Story 4.1.2: System Validates Acceptance Criteria
**As a** system  
**I want to** validate acceptance criteria quality  
**So that** criteria follow behavior form principles

**Acceptance Criteria:**
- When system validates criteria, then checks for "When...then..." pattern presence
- When system validates criteria, then verifies behavioral language usage
- When system validates criteria, then confirms observable outcomes described
- When system validates criteria, then detects technical language violations
- When system finds violations, then returns specific validation errors

**Size:** 5-7 days

### Feature 4.2: System Story Definition

#### Story 4.2.1: Define System-Level Stories
**As an** AI agent  
**I want to** identify and define system-level stories  
**So that** system behavior is captured alongside user stories

**Acceptance Criteria:**
- When AI defines system stories, then uses "System [behavioral verb] [noun]" pattern
- When AI defines system stories, then describes observable system behavior
- When AI defines system stories, then links system stories to user actions
- When AI defines system stories, then avoids technical implementation details
- When AI defines system stories, then distinguishes system stories from technical stories

**Size:** 6-8 days

#### Story 4.2.2: System Validates System Story Definitions
**As a** system  
**I want to** validate system stories against principles  
**So that** system stories describe behavior not implementation

**Acceptance Criteria:**
- When system validates system stories, then checks for behavioral verb patterns
- When system validates system stories, then verifies observable behavior described
- When system validates system stories, then detects technical task language violations
- When system validates system stories, then distinguishes system stories from technical stories
- When system finds violations, then returns specific validation errors

**Size:** 4-6 days

### Feature 4.3: Story Specification

#### Story 4.3.1: Create Specification Scenarios
**As an** AI agent  
**I want to** generate specification scenarios for stories  
**So that** detailed interactions between users and system are documented

**Acceptance Criteria:**
- When AI generates scenarios, then creates Given/When/Then narrative flow
- When AI generates scenarios, then covers happy path, edge cases, error cases
- When AI generates scenarios, then links scenarios to stories
- When AI generates scenarios, then uses behavioral language in scenario descriptions

**Size:** 7-10 days

#### Story 4.3.2: Create Specification Examples
**As an** AI agent  
**I want to** generate specification examples for scenarios  
**So that** concrete demonstrations of behavior are documented

**Acceptance Criteria:**
- When AI generates examples, then creates normal examples for specific use cases
- When AI generates examples, then creates parameterized examples for multiple similar cases
- When AI generates examples, then links examples to scenarios
- When AI generates examples, then uses concrete values for normal examples
- When AI generates examples, then includes Examples table for parameterized examples

**Size:** 7-10 days

#### Story 4.3.3: System Validates Story Specifications
**As a** system  
**I want to** validate specification completeness and structure  
**So that** specifications follow best practices

**Acceptance Criteria:**
- When system validates specifications, then checks scenario completeness (Given/When/Then)
- When system validates specifications, then verifies example completeness (values or tables)
- When system validates specifications, then confirms scenario-example linkage
- When system validates specifications, then validates parameterized example table format
- When system finds violations, then returns specific validation errors

**Size:** 6-8 days

---

## Epic 5: Command Implementation Infrastructure

### Feature 5.1: Command Classes and Runners

#### Story 5.1.1: Implement Story Shape Command
**As a** developer  
**I want to** implement StoryShapeCommand class  
**So that** AI can generate and validate story maps

**Acceptance Criteria:**
- When developer implements command, then creates inner command class extending Command
- When developer implements command, then defines prompting questions for context gathering
- When developer implements command, then implements generate() method using templates
- When developer implements command, then implements validate() method using heuristics
- When developer implements command, then creates CLI wrapper extending CodeAugmentedCommand

**Size:** 8-10 days

#### Story 5.1.2: Implement Market Increments Command
**As a** developer  
**I want to** implement StoryMarketIncrementsCommand class  
**So that** AI can identify and validate marketable increments

**Acceptance Criteria:**
- When developer implements command, then creates inner command class extending Command
- When developer implements command, then defines prompting questions for increment context
- When developer implements command, then implements generate() method for increment identification
- When developer implements command, then implements validate() method using increment heuristics
- When developer implements command, then creates CLI wrapper extending CodeAugmentedCommand

**Size:** 7-9 days

#### Story 5.1.3: Implement Discovery Command
**As a** developer  
**I want to** implement StoryDiscoveryCommand class  
**So that** AI can guide discovery activities

**Acceptance Criteria:**
- When developer implements command, then creates inner command class extending Command
- When developer implements command, then defines prompting questions for discovery context
- When developer implements command, then implements generate() method for increment refinement
- When developer implements command, then implements validate() method using discovery heuristics
- When developer implements command, then creates CLI wrapper extending CodeAugmentedCommand

**Size:** 8-10 days

#### Story 5.1.4: Implement Explore Command
**As a** developer  
**I want to** implement StoryExploreCommand class  
**So that** AI can guide exploration activities

**Acceptance Criteria:**
- When developer implements command, then creates inner command class extending Command
- When developer implements command, then defines prompting questions for exploration context
- When developer implements command, then implements generate() method for acceptance criteria
- When developer implements command, then implements validate() method using exploration heuristics
- When developer implements command, then creates CLI wrapper extending CodeAugmentedCommand

**Size:** 8-10 days

#### Story 5.1.5: Implement Specification Commands
**As a** developer  
**I want to** implement specification command classes (scenarios, examples)  
**So that** AI can generate and validate specifications

**Acceptance Criteria:**
- When developer implements scenario command, then creates inner command class extending Command
- When developer implements scenario command, then implements generate() and validate() methods
- When developer implements example command, then creates inner command class extending Command
- When developer implements example command, then implements generate() and validate() methods
- When developer implements both commands, then creates CLI wrappers extending CodeAugmentedCommand

**Size:** 10-12 days

### Feature 5.2: Heuristics Implementation

#### Story 5.2.1: Implement Story Shape Heuristics
**As a** developer  
**I want to** implement StoryShapeHeuristic class  
**So that** system can validate story map structure

**Acceptance Criteria:**
- When developer implements heuristic, then checks epic/feature/story hierarchy
- When developer implements heuristic, then validates user AND system activities present
- When developer implements heuristic, then checks business language usage
- When developer implements heuristic, then validates story sizing (3-12 day range)
- When developer implements heuristic, then detects task-oriented language violations

**Size:** 6-8 days

#### Story 5.2.2: Implement Market Increments Heuristics
**As a** developer  
**I want to** implement StoryMarketIncrementsHeuristic class  
**So that** system can validate increment structure

**Acceptance Criteria:**
- When developer implements heuristic, then validates increment boundaries clear
- When developer implements heuristic, then checks increments deliver measurable value
- When developer implements heuristic, then verifies relative sizing applied
- When developer implements heuristic, then confirms dependencies identified

**Size:** 5-7 days

#### Story 5.2.3: Implement Discovery Heuristics
**As a** developer  
**I want to** implement StoryDiscoveryHeuristic class  
**So that** system can validate discovery activities

**Acceptance Criteria:**
- When developer implements heuristic, then validates increment refinement completeness
- When developer implements heuristic, then checks story map updates align with principles
- When developer implements heuristic, then verifies story grooming applied
- When developer implements heuristic, then detects ambiguous stories

**Size:** 6-8 days

#### Story 5.2.4: Implement Exploration Heuristics
**As a** developer  
**I want to** implement exploration heuristic classes (explore, scenarios, examples)  
**So that** system can validate exploration artifacts

**Acceptance Criteria:**
- When developer implements explore heuristic, then validates acceptance criteria presence and format
- When developer implements explore heuristic, then checks behavioral language usage
- When developer implements scenario heuristic, then validates scenario completeness
- When developer implements example heuristic, then validates example structure and linkage

**Size:** 8-10 days

### Feature 5.3: Templates Creation

#### Story 5.3.1: Create Story Map Templates
**As a** developer  
**I want to** create story map template files  
**So that** AI can generate consistent story map structure

**Acceptance Criteria:**
- When developer creates template, then includes epic/feature/story hierarchy structure
- When developer creates template, then provides placeholders for user/system activities
- When developer creates template, then includes guidance comments for business language
- When developer creates template, then template follows shaping principles

**Size:** 3-5 days

#### Story 5.3.2: Create Increment Templates
**As a** developer  
**I want to** create increment template files  
**So that** AI can generate consistent increment structure

**Acceptance Criteria:**
- When developer creates template, then includes increment marker format
- When developer creates template, then provides placeholders for story groupings
- When developer creates template, then includes guidance for value delivery
- When developer creates template, then template follows increment principles

**Size:** 3-4 days

#### Story 5.3.3: Create Exploration Templates
**As a** developer  
**I want to** create exploration template files (story, acceptance criteria)  
**So that** AI can generate consistent exploration artifacts

**Acceptance Criteria:**
- When developer creates story template, then includes title, acceptance criteria, summary sections
- When developer creates acceptance criteria template, then uses When...then... format
- When developer creates templates, then includes guidance comments for behavioral language
- When developer creates templates, then templates follow exploration principles

**Size:** 4-6 days

---

## Epic 6: Integration and Configuration

### Feature 6.1: Configuration Files

#### Story 6.1.1: Update Behavior Configuration
**As a** developer  
**I want to** update behavior.json with deployment settings  
**So that** story behavior is discoverable and deployable

**Acceptance Criteria:**
- When developer updates config, then sets deployed: true
- When developer updates config, then adds description from rule file
- When developer updates config, then includes all command references
- When developer updates config, then validates JSON structure

**Size:** 2-3 days

#### Story 6.1.2: Create Code Agent Index
**As a** developer  
**I want to** create code-agent-index.json with all artifacts  
**So that** code agent can discover story commands and rules

**Acceptance Criteria:**
- When developer creates index, then lists all rule files
- When developer creates index, then lists all command files
- When developer creates index, then lists all runner files
- When developer creates index, then follows code-agent index pattern

**Size:** 3-4 days

#### Story 6.1.3: Update Feature Outline
**As a** developer  
**I want to** update feature-outline.md with command documentation  
**So that** developers understand story agent structure

**Acceptance Criteria:**
- When developer updates outline, then documents all 7 commands
- When developer updates outline, then describes command relationships to stages
- When developer updates outline, then documents workflow patterns
- When developer updates outline, then includes command-to-heuristic mapping

**Size:** 3-4 days

### Feature 6.2: CLI Integration

#### Story 6.2.1: Register CLI Entry Points
**As a** developer  
**I want to** register all command CLI handlers  
**So that** users can execute commands via CLI

**Acceptance Criteria:**
- When developer registers handlers, then adds execute-* handlers for all commands
- When developer registers handlers, then adds generate-* handlers for all commands
- When developer registers handlers, then adds validate-* handlers for all commands
- When developer registers handlers, then maps handlers to wrapper classes

**Size:** 4-5 days

#### Story 6.2.2: System Routes CLI Commands
**As a** system  
**I want to** route CLI commands to appropriate handlers  
**So that** commands execute correctly

**Acceptance Criteria:**
- When system receives CLI command, then parses command name and action
- When system receives CLI command, then routes to registered handler
- When system receives CLI command, then passes arguments to handler
- When handler not found, then returns error message

**Size:** 3-4 days

---

## Market Increment Breakdown

### Increment 1: Foundation (Stories: 1.1.1-1.1.3, 1.2.1-1.2.2)
**Value:** Establish rule infrastructure and prompting questions framework  
**Estimated Size:** ~20-25 days  
**Dependencies:** None

### Increment 2: Story Shaping Commands (Stories: 2.1.1-2.1.3, 2.2.1-2.2.4, 5.1.1-5.1.2, 5.2.1-5.2.2, 5.3.1-5.3.2)
**Value:** Enable story map creation and increment identification  
**Estimated Size:** ~60-75 days  
**Dependencies:** Increment 1

### Increment 3: Discovery Commands (Stories: 3.1.1-3.1.2, 3.2.1-3.2.3, 5.1.3, 5.2.3)
**Value:** Enable increment refinement and story grooming  
**Estimated Size:** ~35-45 days  
**Dependencies:** Increment 2

### Increment 4: Exploration Commands (Stories: 4.1.1-4.1.2, 4.2.1-4.2.2, 4.3.1-4.3.3, 5.1.4-5.1.5, 5.2.4, 5.3.3)
**Value:** Enable acceptance criteria and specification generation  
**Estimated Size:** ~65-80 days  
**Dependencies:** Increment 3

### Increment 5: Integration (Stories: 6.1.1-6.1.3, 6.2.1-6.2.2)
**Value:** Complete deployment and CLI integration  
**Estimated Size:** ~15-20 days  
**Dependencies:** Increments 2, 3, 4

---

## Story Count Summary

- **Epic 1 (Foundation):** 5 stories
- **Epic 2 (Story Shaping):** 7 stories
- **Epic 3 (Discovery):** 5 stories
- **Epic 4 (Story Exploration):** 7 stories
- **Epic 5 (Command Infrastructure):** 14 stories
- **Epic 6 (Integration):** 5 stories

**Total Stories:** 43 stories  
**Estimated Total Effort:** ~195-245 days (assuming single developer)

---

## Notes

**User Activities:**
- Users invoke CLI commands for story generation/validation
- Users review generated artifacts and provide feedback
- Users answer prompting questions for context gathering
- Users edit generated story maps and specifications

**System Activities:**
- System validates story artifacts against principles
- System generates story maps using templates
- System checks prompting questions before execution
- System routes CLI commands to handlers
- System applies heuristics for validation
- System returns validation errors with specifics

**Language:**
- All stories use verb/noun patterns (behavioral language)
- System stories describe observable behavior, not implementation
- Avoided task-oriented language (implement, create, refactor)
- Focused on user/system interactions

