# Story Graph Reverse Engineering: New Stories for Refactored Domain Classes

## Overview
This document maps new domain classes created during the refactor to stories in the story graph. Each story = one test class, each scenario = one test method.

**Test files are organized by epic/sub-epic where they are used, not by domain grouping.**

## Test File to Epic/Sub-Epic Mapping

**IMPORTANT:** Test files match sub-epic names. Stories are added to existing test files, not separate class-specific files.

### Epic: Invoke Bot

#### Sub-Epic: Invoke CLI
**File:** `test_invoke_cli.py` (existing)
- TriggerWords class stories (Stories 1-2) - **ADD TO THIS FILE**

#### Sub-Epic: Invoke MCP  
**File:** `test_invoke_mcp.py` (existing)
- Instructions class stories (Stories 3-5) - **ADD TO THIS FILE**

#### Sub-Epic: Perform Behavior Action
**File:** `test_perform_behavior_action.py` (existing)
- MergedInstructions class - base_instructions property (Story 6) - **ADD TO THIS FILE**
- BehaviorConfig class (Story 21) - **ADD TO THIS FILE**
- Behaviors collection class (Story 22) - **ADD TO THIS FILE**
- BotConfig class (Story 23) - **ADD TO THIS FILE**
- BotPaths class (Story 24) - **ADD TO THIS FILE**

### Epic: Execute Behavior Actions

#### Sub-Epic: Render Output
**File:** `test_render_output.py` (existing)
- MergedInstructions class - render_instructions and merge (Stories 7-8) - **ADD TO THIS FILE**

#### Sub-Epic: Validate Knowledge & Content Against Rules
**File:** `test_validate_knowledge_and_content_against_rules.py` (existing)
- Rules collection class (Stories 9-11) - **ADD TO THIS FILE**
- Rule class (Stories 12-14) - **ADD TO THIS FILE**
- ValidationScope class (Story 15) - **ADD TO THIS FILE**
- ScannerLoader class (Story 16) - **ADD TO THIS FILE**

#### Sub-Epic: Gather Context
**File:** `test_gather_context.py` (existing)
- BaseActionConfig class (Story 17) - **ADD TO THIS FILE**
- Actions collection class (Story 18) - **ADD TO THIS FILE**
- Action base class (Story 19) - **ADD TO THIS FILE**
- Guardrails class (Story 20) - **ADD TO THIS FILE**

---

## Epic: Invoke Bot

### Sub-Epic: Invoke CLI
**File:** `test_invoke_cli.py` (existing - ADD stories to this file)

#### Story 1: Get Trigger Priority
**Class:** TriggerWords  
**File:** `test_invoke_cli.py` (add to existing file)  
**Epic:** Invoke Bot → Invoke CLI  
**Test Class:** `TestGetTriggerPriority`

**Scenarios:**
1. "Priority property returns configured priority or zero"
   - Given: BehaviorConfig with different trigger configurations
   - When: priority property accessed
   - Then: Returns configured priority when available, otherwise returns 0
   
   **Examples:**
   | trigger_config | expected_priority |
   |----------------|-------------------|
   | priority: 5 | 5 |
   | no priority field | 0 |
   | list trigger format | 0 |

#### Story 2: Match Text Against Triggers
**Class:** TriggerWords  
**File:** `test_invoke_cli.py` (add to existing file)  
**Epic:** Invoke Bot → Invoke CLI  
**Test Class:** `TestMatchTextAgainstTriggers`

**Scenarios:**
1. "Matches returns true when text matches any pattern"
   - Given: BehaviorConfig with multiple patterns ['test', 'pattern', 'xyz']
   - When: matches() called with text 'This is a test'
   - Then: Returns True

2. "Matches returns false when no patterns match"
   - Given: BehaviorConfig with patterns ['xyz', 'abc']
   - When: matches() called with text 'This is a test'
   - Then: Returns False

3. "Matches returns false when no triggers configured"
   - Given: BehaviorConfig with no triggers
   - When: matches() called with text 'This is a test'
   - Then: Returns False

4. "Matches works with list trigger format"
   - Given: BehaviorConfig with list triggers ['test', 'pattern']
   - When: matches() called with text 'This is a test'
   - Then: Returns True

5. "Matches checks all patterns until match found"
   - Given: BehaviorConfig with patterns ['xyz', 'abc', 'test']
   - When: matches() called with text 'This is a test'
   - Then: Returns True (third pattern matches)

6. "Matches handles regex patterns"
   - Given: BehaviorConfig with regex pattern 'test.*pattern'
   - When: matches() called with text 'test this pattern'
   - Then: Returns True

7. "Matches is case insensitive"
   - Given: BehaviorConfig with pattern 'TEST'
   - When: matches() called with text 'this is a test'
   - Then: Returns True (case insensitive)

8. "Matches handles invalid regex patterns by falling back to literal"
   - Given: BehaviorConfig with invalid regex pattern '['
   - When: matches() called with text 'This contains [ bracket'
   - Then: Returns True (fallback to literal matching)

### Sub-Epic: Perform Behavior Action
**File:** `test_perform_behavior_action.py` (existing - ADD stories to this file)

#### Story 21: Load Behavior Config
**Class:** BehaviorConfig  
**File:** `test_perform_behavior_action.py` (add to existing file)  
**Epic:** Invoke Bot → Perform Behavior Action  
**Test Class:** `TestLoadBehaviorConfig`

**Scenarios:**
1. "Behavior config loads correct behavior from behavior.json file"
   - Given: behavior.json exists in behavior folder for 'shape' behavior
   - When: BehaviorConfig instantiated with behavior and bot_paths
   - Then: Config loaded from file and behavior_name property returns 'shape'

2. "Behavior config provides access to config objects"
   - Given: BehaviorConfig loaded with complete behavior.json
   - When: Config properties accessed (description, goal, inputs, outputs, instructions, trigger_words, actions_workflow)
   - Then: All config objects are accessible

3. "Behavior config raises error when behavior.json missing"
   - Given: Behavior folder without behavior.json
   - When: BehaviorConfig instantiated
   - Then: Raises FileNotFoundError

#### Story 22: Manage Behaviors Collection
**Class:** Behaviors  
**File:** `test_perform_behavior_action.py` (add to existing file)  
**Epic:** Invoke Bot → Perform Behavior Action  
**Test Class:** `TestManageBehaviorsCollection`

**Scenarios:**
1. "Behaviors collection loads behaviors from bot config"
   - Given: BotConfig with behaviors list
   - When: Behaviors instantiated with bot_config
   - Then: Behaviors collection contains all behaviors from config

2. "Behaviors find by name returns behavior when exists"
   - Given: Behaviors collection with 'shape' behavior
   - When: find_by_name('shape') called
   - Then: Returns Behavior object

3. "Behaviors find by name returns none when does not exist"
   - Given: Behaviors collection without 'nonexistent' behavior
   - When: find_by_name('nonexistent') called
   - Then: Returns None

4. "Behaviors check exists returns true when behavior exists"
   - Given: Behaviors collection with 'discovery' behavior
   - When: check_exists('discovery') called
   - Then: Returns True

5. "Behaviors check exists returns false when behavior does not exist"
   - Given: Behaviors collection without 'nonexistent' behavior
   - When: check_exists('nonexistent') called
   - Then: Returns False

6. "Behaviors current property returns current behavior"
   - Given: Behaviors collection with current behavior set
   - When: current property accessed
   - Then: Returns current Behavior object

7. "Behaviors next property returns next behavior"
   - Given: Behaviors collection with current behavior
   - When: next property accessed
   - Then: Returns next Behavior object

8. "Behaviors navigate to behavior updates current behavior"
   - Given: Behaviors collection
   - When: navigate_to('discovery') called
   - Then: Current behavior updated to 'discovery'

9. "Behaviors close current marks behavior and action complete"
   - Given: Behaviors collection with current behavior and current action
   - When: close_current() called
   - Then: Current behavior marked complete and current action closed

10. "Behaviors execute current executes current behavior"
    - Given: Behaviors collection with current behavior
    - When: execute_current() called
    - Then: Current behavior's execute() method called

#### Story 23: Load Bot Configuration
**Class:** BotConfig  
**File:** `test_perform_behavior_action.py` (add to existing file)  
**Epic:** Invoke Bot → Perform Behavior Action  
**Test Class:** `TestLoadBotConfiguration`

**Scenarios:**
1. "Bot config loads correct bot from bot_config.json file"
   - Given: bot_config.json exists in config directory with name 'story_bot'
   - When: BotConfig instantiated with bot_name and bot_paths
   - Then: Config loaded from file and name property returns 'story_bot'

2. "Bot config provides access to config properties"
   - Given: BotConfig loaded with complete bot_config.json
   - When: Config properties accessed (description, goal, instructions, mcp, trigger_words, base_actions_path, behaviors_list, working_area)
   - Then: All config properties are accessible

3. "Bot config behaviors list returns empty list when missing"
   - Given: bot_config.json without behaviors key
   - When: behaviors_list property accessed
   - Then: Returns []

4. "Bot config raises error when config file missing"
   - Given: Bot directory without config/bot_config.json
   - When: BotConfig instantiated
   - Then: Raises FileNotFoundError

#### Story 24: Resolve Bot Paths
**Class:** BotPaths  
**File:** `test_perform_behavior_action.py` (add to existing file)  
**Epic:** Invoke Bot → Perform Behavior Action  
**Test Class:** `TestResolveBotPaths`

**Scenarios:**
1. "Bot paths resolves bot directory from environment"
   - Given: BOT_DIRECTORY environment variable set
   - When: BotPaths instantiated
   - Then: bot_directory property returns path from environment

2. "Bot paths resolves workspace directory from environment"
   - Given: WORKING_AREA environment variable set
   - When: BotPaths instantiated
   - Then: workspace_directory property returns path from environment

3. "Bot paths properties return resolved paths"
   - Given: BotPaths with resolved paths
   - When: Properties accessed (bot_directory, workspace_directory)
   - Then: Returns bot directory Path and workspace directory Path

5. "Bot paths uses default paths when environment variables not set"
   - Given: No BOT_DIRECTORY or WORKING_AREA environment variables
   - When: BotPaths instantiated
   - Then: Uses default path resolution logic

#### Story 6: Get Base Instructions (MergedInstructions)
**Class:** MergedInstructions  
**File:** `test_perform_behavior_action.py` (add to existing file)  
**Epic:** Invoke Bot → Perform Behavior Action  
**Test Class:** `TestGetBaseInstructions`

**Scenarios:**
1. "Base instructions property returns instructions from config"
   - Given: BaseActionConfig with instructions (list, string, or None)
   - When: base_instructions property accessed
   - Then: Returns list format (converts string to list, returns empty list when None, returns copy not reference)
   
   **Examples:**
   | instructions | expected_result |
   |--------------|-----------------|
   | ['instruction1', 'instruction2'] | ['instruction1', 'instruction2'] |
   | 'single instruction' | ['single instruction'] |
   | None | [] |

---

## Epic: Execute Behavior Actions

### Sub-Epic: Render Output
**File:** `test_render_output.py` (existing - ADD stories to this file)

#### Story 7: Get Render Instructions
**Class:** MergedInstructions  
**File:** `test_render_output.py` (add to existing file)  
**Epic:** Execute Behavior Actions → Render Output  
**Test Class:** `TestGetRenderInstructions`

**Scenarios:**
1. "Render instructions property returns provided instructions or None"
   - Given: MergedInstructions with or without render instructions
   - When: render_instructions property accessed
   - Then: Returns render instructions dict when provided, None when not provided
   
   **Examples:**
   | render_instructions | expected_result |
   |---------------------|-----------------|
   | {'instructions': ['render1', 'render2']} | {'instructions': ['render1', 'render2']} |
   | None | None |

#### Story 8: Merge Base and Render Instructions
**Class:** MergedInstructions  
**File:** `test_render_output.py` (add to existing file)  
**Epic:** Execute Behavior Actions → Render Output  
**Test Class:** `TestMergeBaseAndRenderInstructions`

**Scenarios:**
1. "Merge combines base and render instructions"
   - Given: BaseActionConfig with ['base1', 'base2'] and render instructions {'instructions': ['render1', 'render2']}
   - When: merge() called
   - Then: Returns dict with base_instructions and render_instructions

2. "Merge handles missing render instructions"
   - Given: BaseActionConfig with ['base1', 'base2'] without render instructions
   - When: merge() called
   - Then: Returns dict with only base_instructions

3. "Merge handles empty render instructions"
   - Given: BaseActionConfig with ['base1'] and empty render instructions {}
   - When: merge() called
   - Then: Returns dict with base_instructions and empty render_instructions

### Sub-Epic: Validate Knowledge & Content Against Rules
**File:** `test_validate_knowledge_and_content_against_rules.py` (existing - ADD stories to this file)

#### Story 9: Load Rules Collection
**Class:** Rules  
**File:** `test_validate_knowledge_and_content_against_rules.py` (add to existing file)  
**Epic:** Execute Behavior Actions → Validate Knowledge & Content Against Rules  
**Test Class:** `TestLoadRulesCollection`

**Scenarios:**
1. "Rules loads both bot-level and behavior-specific rules when instantiated with behavior"
   - Given: Behavior with bot rules directory and behavior rules directory with rule files, and bot_paths
   - When: Rules instantiated with behavior and bot_paths
   - Then: Rules collection contains both bot-level and behavior-specific rules

2. "Rules raises error when behavior provided without bot_paths"
   - Given: Behavior without bot_paths
   - When: Rules instantiated with behavior but no bot_paths
   - Then: Raises ValueError

3. "Rules raises error when behavior not provided"
   - Given: No behavior
   - When: Rules instantiated without behavior
   - Then: Raises ValueError

#### Story 10: Find Rule By Name
**Class:** Rules  
**File:** `test_validate_knowledge_and_content_against_rules.py` (add to existing file)  
**Epic:** Execute Behavior Actions → Validate Knowledge & Content Against Rules  
**Test Class:** `TestFindRuleByName`

**Scenarios:**
1. "Find by name returns rule when rule exists"
   - Given: Rules collection with rule named 'test_rule'
   - When: find_by_name('test_rule') called
   - Then: Returns Rule object

2. "Find by name returns none when rule does not exist"
   - Given: Rules collection without 'nonexistent_rule'
   - When: find_by_name('nonexistent_rule') called
   - Then: Returns None

3. "Find by name searches both bot-level and behavior-specific rules"
   - Given: Rules collection with bot-level and behavior-specific rules
   - When: find_by_name() called
   - Then: Searches both rule sets

#### Story 11: Iterate Rules
**Class:** Rules  
**File:** `test_validate_knowledge_and_content_against_rules.py` (add to existing file)  
**Epic:** Execute Behavior Actions → Validate Knowledge & Content Against Rules  
**Test Class:** `TestIterateRules`

**Scenarios:**
1. "Iterate returns all rules in collection"
   - Given: Rules collection with multiple rules
   - When: iterate() called
   - Then: Returns iterator with all rules

2. "Iterate returns empty iterator when no rules loaded"
   - Given: Rules collection with no rules
   - When: iterate() called
   - Then: Returns empty iterator

3. "Iterate includes both bot-level and behavior-specific rules"
   - Given: Rules collection with bot-level and behavior-specific rules
   - When: iterate() called
   - Then: Iterator includes all rules from both sources

#### Story 12: Load Rule From File
**Class:** Rule  
**File:** `test_validate_knowledge_and_content_against_rules.py` (add to existing file)  
**Epic:** Execute Behavior Actions → Validate Knowledge & Content Against Rules  
**Test Class:** `TestLoadRuleFromFile`

**Scenarios:**
1. "Rule loads from JSON file path"
   - Given: Rule JSON file exists
   - When: Rule instantiated with file path
   - Then: Rule loads content from file

2. "Rule loads embedded rule from validation_rules.json"
   - Given: validation_rules.json with embedded rule data
   - When: Rule instantiated with rule_content parameter
   - Then: Rule loads from provided content

3. "Rule extracts name from file path"
   - Given: Rule file 'test_rule.json'
   - When: Rule instantiated
   - Then: Rule name property returns 'test_rule'

4. "Rule extracts name from embedded rule data"
   - Given: Embedded rule data with name 'embedded_rule'
   - When: Rule instantiated with rule_content
   - Then: Rule name property returns 'embedded_rule'

5. "Rule raises error when file does not exist"
   - Given: Non-existent rule file path
   - When: Rule instantiated without rule_content
   - Then: Raises FileNotFoundError

#### Story 13: Load Scanner For Rule
**Class:** Rule  
**File:** `test_validate_knowledge_and_content_against_rules.py` (add to existing file)  
**Epic:** Execute Behavior Actions → Validate Knowledge & Content Against Rules  
**Test Class:** `TestLoadScannerForRule`

**Scenarios:**
1. "Rule loads scanner class when scanner path provided"
   - Given: Rule with scanner path in config
   - When: Rule instantiated
   - Then: Scanner class loaded

2. "Rule scanner properties return scanner instance or None"
   - Given: Rule with different scanner configurations
   - When: scanner and scanner_class properties accessed
   - Then: Returns scanner instance and class type when loaded, None when not configured or not found
   
   **Examples:**
   | scanner_config | scanner_result | scanner_class_result |
   |----------------|----------------|----------------------|
   | valid scanner path | scanner instance | scanner class type |
   | no scanner path | None | None |
   | invalid scanner path | None | None |

#### Story 14: Get Rule Properties
**Class:** Rule  
**File:** `test_validate_knowledge_and_content_against_rules.py` (add to existing file)  
**Epic:** Execute Behavior Actions → Validate Knowledge & Content Against Rules  
**Test Class:** `TestGetRuleProperties`

**Scenarios:**
1. "Rule provides access to config properties"
   - Given: Rule loaded with complete rule config (description, examples, instruction, behavior_name)
   - When: Rule properties accessed (description, examples, instruction, behavior_name)
   - Then: All config properties are accessible

#### Story 15: Create Validation Scope
**Class:** ValidationScope  
**File:** `test_validate_knowledge_and_content_against_rules.py` (add to existing file)  
**Epic:** Execute Behavior Actions → Validate Knowledge & Content Against Rules  
**Test Class:** `TestCreateValidationScope`

**Scenarios:**
1. "Validation scope created with different parameter combinations"
   - Given: Parameters dict with scope configuration
   - When: ValidationScope instantiated with parameters
   - Then: ValidationScope scope property returns expected configuration
   
   **Examples:**
   | parameters | expected_scope_contains |
   |------------|------------------------|
   | {'test': ['test_file.py']} | test: ['test_file.py'] |
   | {'src': ['src_file.py']} | src: ['src_file.py'] |
   | {'test': ['test1.py'], 'src': ['src1.py']} | test: ['test1.py'], src: ['src1.py'] |
   | {'validate_all': True} | all: True |
   | {'story_names': ['Story1']} | story_names: ['Story1'] |

#### Story 16: Load Scanner Class
**Class:** ScannerLoader  
**File:** `test_validate_knowledge_and_content_against_rules.py` (add to existing file)  
**Epic:** Execute Behavior Actions → Validate Knowledge & Content Against Rules  
**Test Class:** `TestLoadScannerClass`

**Scenarios:**
1. "Scanner loader loads scanner from exact module path"
   - Given: Valid scanner module path
   - When: load_scanner() called with exact path
   - Then: Returns scanner class

2. "Scanner loader loads scanner from base_bot scanners directory"
   - Given: Scanner name 'story_scanner'
   - When: load_scanner() called
   - Then: Tries base_bot/src/scanners/story_scanner.py

3. "Scanner loader loads scanner from bot-specific scanners directory"
   - Given: Bot name 'story_bot' and scanner name
   - When: load_scanner() called
   - Then: Tries bot's src/scanners directory

4. "Scanner loader validates scanner inherits from Scanner base class"
   - Given: Scanner class that doesn't inherit from Scanner
   - When: load_scanner() called
   - Then: Returns None (validation fails)

5. "Scanner loader returns none when scanner class not found"
   - Given: Invalid scanner module path
   - When: load_scanner() called
   - Then: Returns None

6. "Scanner loader returns error message when load fails"
   - Given: Invalid scanner path
   - When: load_scanner_with_error() called
   - Then: Returns tuple (None, error_message)

7. "Scanner loader tries multiple paths when exact path fails"
   - Given: Scanner name without full module path
   - When: load_scanner() called
   - Then: Tries multiple possible paths

### Sub-Epic: Gather Context (or new sub-epic for Actions Domain)
**File Location:** `test_gather_context.py` (or separate files for Actions domain)

#### Story 18: Load Base Action Config
**Class:** BaseActionConfig  
**File:** `test_base_action_config.py` (new)  
**Epic:** Execute Behavior Actions → Gather Context (or new Actions Domain sub-epic)  
**Test Class:** `TestLoadBaseActionConfig`

**Scenarios:**
1. "Base action config loads correct action from action_config.json file"
   - Given: action_config.json exists in base_actions/{action_name}/ with complete config
   - When: BaseActionConfig instantiated with action_name
   - Then: Config loaded from file and properties accessible (order, next_action, custom_class, instructions, workflow)

2. "Base action config uses default config when action_config.json missing"
   - Given: Action name without action_config.json
   - When: BaseActionConfig instantiated
   - Then: Uses default config (doesn't raise error)

#### Story 18: Access Actions
**Class:** Actions  
**File:** `test_gather_context.py` (add to existing file)  
**Epic:** Execute Behavior Actions → Gather Context  
**Test Class:** `TestManageActionsCollection`

**Scenarios:**
1. "Actions collection loads actions from behavior config"
   - Given: BehaviorConfig with actions_workflow
   - When: Actions instantiated with behavior_config and behavior
   - Then: Actions collection contains all actions from config

2. "Actions find by name returns action when exists"
   - Given: Actions collection with 'gather_context' action
   - When: find_by_name('gather_context') called
   - Then: Returns Action object

3. "Actions find by name returns none when does not exist"
   - Given: Actions collection without 'nonexistent_action'
   - When: find_by_name('nonexistent_action') called
   - Then: Returns None

4. "Actions find by order returns action when exists"
   - Given: Actions collection with action at order 1
   - When: find_by_order(1) called
   - Then: Returns Action object

5. "Actions find by order returns none when does not exist"
   - Given: Actions collection without order 99
   - When: find_by_order(99) called
   - Then: Returns None

6. "Actions current and next properties return action objects"
   - Given: Actions collection with current action set
   - When: current and next properties accessed
   - Then: Returns current Action object and next Action object

8. "Actions navigate to action updates current action"
   - Given: Actions collection
   - When: navigate_to('build_knowledge') called
   - Then: Current action updated to 'build_knowledge'

9. "Actions close current marks action complete"
   - Given: Actions collection with current action
   - When: close_current() called
   - Then: Current action marked complete

10. "Actions execute current executes current action"
    - Given: Actions collection with current action
    - When: execute_current() called
    - Then: Current action's execute() method called

#### Story 20: Initialize Action
**Class:** Action  
**File:** `test_action.py` (new)  
**Epic:** Execute Behavior Actions → Gather Context (or new Actions Domain sub-epic)  
**Test Class:** `TestInitializeAction`

**Scenarios:**
1. "Action initializes with base action config and behavior"
   - Given: BaseActionConfig and Behavior
   - When: Action instantiated with both
   - Then: Action initialized successfully

2. "Action loads and merges instructions on initialization"
   - Given: BaseActionConfig with instructions and Behavior
   - When: Action instantiated
   - Then: Instructions loaded and merged

3. "Action properties return expected values"
   - Given: Action initialized with BaseActionConfig and Behavior
   - When: Properties accessed (order, action_class, instructions, tracker)
   - Then: All properties return expected values (order from config, action_class from config, merged instructions dict, ActivityTracker instance)

#### Story 25: Load Guardrails
**Class:** Guardrails  
**File:** `test_guardrails.py` (new)  
**Epic:** Execute Behavior Actions → Gather Context  
**Test Class:** `TestLoadGuardrails`

**Scenarios:**
1. "Guardrails loads required context guardrails"
   - Given: BehaviorConfig with guardrails directory
   - When: Guardrails instantiated with behavior_config
   - Then: Required context guardrails loaded

2. "Guardrails loads strategy guardrails"
   - Given: BehaviorConfig with strategy guardrails directory
   - When: Guardrails instantiated
   - Then: Strategy guardrails loaded

3. "Guardrails properties return guardrails objects"
   - Given: Guardrails with loaded guardrails
   - When: Properties accessed (required_context, strategy)
   - Then: Returns RequiredContext object and Strategy object

5. "Guardrails handles missing guardrails files gracefully"
   - Given: BehaviorConfig without guardrails files
   - When: Guardrails instantiated
   - Then: Creates empty/default guardrails objects

---

## Updated Existing Stories

### Update Story: "Load And Merge Behavior Action Instructions"
**Current Location:** `Invoke Bot` → `Invoke MCP` sub-epic  
**File:** `test_invoke_mcp.py`

**Add Scenarios:**
1. "Action uses Instructions class to merge base and behavior instructions"
   - Given: Action with BaseActionConfig and Behavior
   - When: Action initialized
   - Then: Action uses Instructions class to merge instructions

2. "Action uses MergedInstructions class when render instructions present"
   - Given: RenderOutputAction with render instructions
   - When: Action initialized
   - Then: Action uses MergedInstructions class for merging

### Update Story: "Inject Validation Rules for Validate Rules Action"
**Current Location:** `Execute Behavior Actions` → `Validate Knowledge & Content Against Rules` sub-epic  
**File:** `test_validate_knowledge_and_content_against_rules.py`

**Add Scenarios:**
1. "Action uses Rules collection to load rules"
   - Given: ValidateRulesAction with Behavior
   - When: Action executes
   - Then: Action uses Rules collection to load rules

2. "Action uses Rule class to access rule properties"
   - Given: ValidateRulesAction with loaded rules
   - When: Action accesses rule properties
   - Then: Uses Rule class properties

3. "Action uses ScannerLoader to load scanner classes"
   - Given: ValidateRulesAction with rules containing scanner paths
   - When: Action loads scanners
   - Then: Uses ScannerLoader service

4. "Action uses ValidationScope to define validation scope"
   - Given: ValidateRulesAction with file paths or story graph
   - When: Action creates validation scope
   - Then: Uses ValidationScope class

### Update Story: "Load Scanner Classes"
**Current Location:** `Execute Behavior Actions` → `Validate Knowledge & Content Against Rules` sub-epic  
**File:** `test_validate_knowledge_and_content_against_rules.py`

**Add Scenarios:**
1. "Action uses ScannerLoader service to load scanner classes"
   - Given: Rule with scanner path
   - When: Scanner needs to be loaded
   - Then: Uses ScannerLoader service

2. "ScannerLoader loads scanner from multiple possible paths"
   - Given: ScannerLoader with bot_name
   - When: load_scanner() called with scanner name
   - Then: Tries multiple path locations

3. "ScannerLoader validates scanner inherits from Scanner base class"
   - Given: ScannerLoader with scanner class
   - When: Scanner loaded
   - Then: Validates inheritance from Scanner

---

## Story Graph JSON Structure

### New Sub-Epic JSON Template

```json
{
  "name": "Domain Classes",
  "sequential_order": 6,
  "estimated_stories": 15,
  "sub_epics": [],
  "story_groups": [
    {
      "type": "and",
      "connector": null,
      "stories": [
        {
          "name": "Match Trigger Pattern",
          "sequential_order": 1,
          "connector": "or",
          "users": ["Bot Behavior"],
          "story_type": "user",
          "scenarios": [
            {
              "name": "Match pattern with regex pattern",
              "type": "happy_path",
              "test_method": "test_match_pattern_with_regex_pattern",
              "background": [],
              "steps": [
                "Given BehaviorConfig with regex pattern 'test.*pattern'",
                "When match_pattern() called with pattern and text 'test this pattern'",
                "Then Returns True"
              ]
            }
            // ... more scenarios
          ]
        }
        // ... more stories
      ]
    }
  ]
}
```

---

## Implementation Notes

1. **File Organization:**
   - Each sub-epic becomes one test file: `test_domain_classes.py`
   - Stories become test classes: `TestMatchTriggerPattern`, `TestGetTriggerPriority`, etc.
   - Scenarios become test methods: `test_match_pattern_with_regex_pattern`, etc.

2. **Helper Functions:**
   - Use `given_`, `when_`, `then_` prefixes per testing rules
   - Place helpers at appropriate scope (story-level, sub-epic level, epic level)

3. **Test Structure:**
   - Follow pytest orchestrator pattern
   - Tests under 20 lines, helpers under 20 lines
   - Use Given-When-Then structure with comments

4. **Integration:**
   - Some stories test classes in isolation
   - Some stories verify integration with actions (e.g., "Action uses Instructions class")

5. **Story Order:**
   - Follow sequential_order in story graph
   - Group related stories together (Instructions domain, Rules domain, etc.)

