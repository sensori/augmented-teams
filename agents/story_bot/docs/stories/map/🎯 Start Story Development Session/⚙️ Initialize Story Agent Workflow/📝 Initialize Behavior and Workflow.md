# 📝 Initialize Behavior and Workflow

**Navigation:** [📋 Story Map](../../story-agent-story-map.md) | [⚙️ Feature Overview](../../initialize-workflow-exploration.md)

**Epic:** Start Story Development Session
**Feature:** Initialize Story Agent Workflow

## Story Description

After Project initialization, Agent loads base and Story Agent configurations (instruction templates, trigger words, Rules, Behaviors), connects Workflow to Project, Workflow sets up stages, and Agent starts workflow at first behavior and action

## Acceptance Criteria

### Behavioral Acceptance Criteria

- When Project is finished initializing, then Agent loads base configuration by reading agents/base/agent.json, extracts base instruction templates and base trigger words, stores them for use in future instruction generation
- When Agent has loaded base configuration, then Agent loads Story Agent configuration by reading agents/stories/agent.json, extracts agent-specific instruction templates and agent-specific trigger words, creates Rules objects from rules configuration, creates Behavior objects for each workflow behavior (shape, prioritization, discovery, exploration, specification) with their order, guardrails, rules, actions, and content configurations, stores behaviors in dictionary, and presents configuration summary to user for confirmation
- When Agent connects Workflow to Project, then Agent links Workflow instance (created during Project initialization) to Agent, and passes behaviors dictionary to Workflow
- When Workflow receives behaviors dictionary, then Workflow sorts behaviors by their order property (shape=1, prioritization=2, discovery=4, etc.), creates ordered list of stage names, and sets up workflow stages
- When Agent starts workflow for new project, then Agent calls Workflow to start, Workflow gets first behavior from sorted stages (shape behavior with order=1), initializes first action of that behavior (clarification action), sets workflow current_stage and current_action, and Agent presents workflow state to user for confirmation
- When AgentStateManager synchronizes workflow, then AgentStateManager verifies Project has workflow attribute, checks if Agent workflow and Project workflow reference the same object, and if different updates Project workflow to reference Agent workflow
- When MCP Server synchronizes project workflow, then MCP Server ensures Project workflow reference matches Agent workflow reference, and updates Project workflow if needed

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Agent is initialized with agent_name='stories'
  [🔗](../../../../../../src/stories_acceptance_tests.py#L404)
And Project is finished initializing
  [🔗](../../../../../../src/stories_acceptance_tests.py#L921)
```

## Scenarios

### Scenario Outline: Agent loads configurations and initializes workflow successfully

**Steps:**
```gherkin
Given test project area is set up at "<test_project_area>"
And test agent base area is set up at "<test_agent_base_area>"
And test agent stories area is set up at "<test_agent_stories_area>"
And valid base agent.json exists at "<test_agent_base_area>/agent.json>"
And valid stories agent.json exists at "<test_agent_stories_area>/agent.json>"
And Workflow instance exists in Project
  [🔗](../../../../../../src/stories_acceptance_tests.py#L914)
And Workflow in Project has state "<initial_workflow_state>"
Then Agent loads base configuration by reading "<test_agent_base_area>/agent.json"
And Agent extracts base instruction templates: "<expected_base_templates>"
And Agent extracts base trigger words: "<expected_base_trigger_words>"
And Agent stores them for use in future instruction generation
  [🔗](../../../../../../src/stories_acceptance_tests.py#L940)
When Agent has loaded base configuration
  [🔗](../../../../../../src/stories_acceptance_tests.py#L946)
Then Agent loads Story Agent configuration by reading "<test_agent_stories_area>/agent.json"
And Agent extracts agent-specific instruction templates: "<expected_agent_templates>"
And Agent extracts agent-specific trigger words: "<expected_agent_trigger_words>"
And Agent creates Rules objects from rules configuration with rules: "<expected_rules>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L964)
And Agent creates Behavior objects for each workflow behavior: "<expected_behaviors>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L970)
And Agent stores behaviors in dictionary with keys: "<expected_behavior_keys>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L977)
And Agent presents configuration summary to user for confirmation showing "<expected_summary_content>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L983)
When Agent connects Workflow to Project
  [🔗](../../../../../../src/stories_acceptance_tests.py#L992)
Then Agent verifies Project.workflow exists
And Agent verifies Workflow state matches "<initial_workflow_state>"
And Agent verifies Workflow current_stage is "<initial_current_stage>"
And Agent verifies Workflow current_action is "<initial_current_action>"
And Agent links Workflow instance to Agent
  [🔗](../../../../../../src/stories_acceptance_tests.py#L998)
And Agent verifies Agent.workflow references same object as Project.workflow: "<expected_object_reference_match>"
And Agent verifies Workflow state after linking is "<expected_workflow_state_after_link>"
And Agent passes behaviors dictionary to Workflow
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1240)
When Workflow receives behaviors dictionary
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1011)
Then Workflow sorts behaviors by their order property
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1017)
And Workflow creates ordered list of stage names "<expected_stage_names>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1023)
And Workflow sets up workflow stages: "<expected_stage_names>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1030)
When Agent starts workflow for new project
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1036)
Then Agent calls Workflow to start
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1308)
And Workflow gets first behavior "<first_behavior_name>" from sorted stages with order "<first_behavior_order>"
And Workflow initializes first action "<first_action_name>" of that behavior
And Workflow sets current_stage to "<expected_final_stage>"
And Workflow sets current_action to "<expected_final_action>"
And Workflow state is verified: current_behavior_name="<expected_final_stage>", current_action_name="<expected_final_action>"
And Agent presents workflow state to user for confirmation with stage "<expected_final_stage>" and action "<expected_final_action>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1072)
```

**Examples:**
| test_project_area | test_agent_base_area | test_agent_stories_area | initial_workflow_state | initial_current_stage | initial_current_action | expected_workflow_state_after_link | expected_base_templates | expected_base_trigger_words | expected_agent_templates | expected_agent_trigger_words | expected_rules | expected_behaviors | expected_behavior_keys | expected_summary_content | expected_stage_names | first_behavior_name | first_behavior_order | first_action_name | expected_final_stage | expected_final_action | expected_object_reference_match |
|-------------------|---------------------|------------------------|----------------------|---------------------|----------------------|----------------------------------|----------------------|--------------------------|----------------------|--------------------------|--------------|------------------|---------------------|----------------------|-------------------|-------------------|-------------------|-----------------|------------------|-------------------|---------------------------|
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories | uninitialized | None | None | uninitialized | context_clarification,planning,generate,render_output,validate,correct | correct,validate,build_structure | (same as base) | (same as base) | verb_noun_consistency | shape,prioritization,arrange,discovery,exploration,specification | shape,prioritization,arrange,discovery,exploration,specification | Loaded 6 behaviors: shape(1), prioritization(2), arrange(3), discovery(4), exploration(5), specification(6) | shape,prioritization,arrange,discovery,exploration,specification | shape | 1 | clarification | shape | clarification | true |
| test_data/projects/another-project | test_data/agents/base | test_data/agents/stories | uninitialized | None | None | uninitialized | context_clarification,planning,generate,render_output,validate,correct | correct,validate,build_structure | (same as base) | (same as base) | verb_noun_consistency | shape,prioritization,arrange,discovery,exploration,specification | shape,prioritization,arrange,discovery,exploration,specification | Loaded 6 behaviors: shape(1), prioritization(2), arrange(3), discovery(4), exploration(5), specification(6) | shape,prioritization,arrange,discovery,exploration,specification | shape | 1 | clarification | shape | clarification | true |
| test_data/projects/existing-project | test_data/agents/base | test_data/agents/stories | restored | shape | clarification | restored | context_clarification,planning,generate,render_output,validate,correct | correct,validate,build_structure | (same as base) | (same as base) | verb_noun_consistency | shape,prioritization,arrange,discovery,exploration,specification | shape,prioritization,arrange,discovery,exploration,specification | Loaded 6 behaviors: shape(1), prioritization(2), arrange(3), discovery(4), exploration(5), specification(6) | shape,prioritization,arrange,discovery,exploration,specification | shape | 1 | clarification | shape | clarification | true |

### Scenario Outline: Workflow synchronization ensures consistency

**Steps:**
```gherkin
Given Agent has loaded configurations
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1082)
And Workflow has been set up
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1088)
And Agent workflow has state "<agent_workflow_state>"
And Project workflow has state "<project_workflow_state>"
And Agent workflow and Project workflow may reference different objects
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1094)
When AgentStateManager synchronizes workflow
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1100)
Then AgentStateManager checks if Project has workflow attribute
And AgentStateManager verifies Agent workflow state is "<agent_workflow_state>"
And AgentStateManager verifies Project workflow state is "<project_workflow_state>"
When Project workflow attribute is missing or None
Then AgentStateManager sets Project.workflow to Agent.workflow
And AgentStateManager verifies Project workflow state matches Agent workflow state "<agent_workflow_state>"
When Project workflow exists but references different object than Agent workflow
Then AgentStateManager updates Project.workflow to reference Agent.workflow
And AgentStateManager verifies Project workflow state matches Agent workflow state "<agent_workflow_state>"
When MCP Server synchronizes project workflow
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1133)
Then MCP Server checks if Project.workflow attribute exists
And MCP Server checks if Project.workflow is None or references different object than Agent.workflow
When Project.workflow is None or references different object
Then MCP Server updates Project.workflow reference to point to same object as Agent.workflow
And MCP Server verifies Project.workflow references same object as Agent.workflow: "<expected_object_reference_match>"
And MCP Server verifies workflow state consistency: current_behavior_name="<expected_behavior>", current_action_name="<expected_action>"
And system does not crash from workflow reference mismatch
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1151)
```

**Examples:**
| agent_workflow_state | project_workflow_state | expected_behavior | expected_action | expected_object_reference_match |
|---------------------|----------------------|------------------|----------------|-------------------------------|
| shape:clarification | shape:clarification | shape | clarification | true |
| shape:clarification | None | shape | clarification | true |
| shape:planning | shape:clarification | shape | planning | true |

### Scenario Outline: Agent fails to load base configuration

**Steps:**
```gherkin
Given test project area is set up at "<test_project_area>"
And test agent base area is set up at "<test_agent_base_area>"
And base agent.json has error condition "<error_condition>"
And Agent attempts to load base configuration from "<test_agent_base_area>/agent.json"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1165)
Then Agent detects error condition "<error_condition>"
And Agent handles missing or corrupted base config error gracefully
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1180)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And error "<expected_error_message>" is presented to user in chat
But Agent does not call _load_agent_config()
But Agent does not create behaviors dictionary
But Agent does not create Rules objects
But Agent does not initialize Workflow
```

**Examples:**
| test_project_area | test_agent_base_area | error_condition | expected_error_message |
|-------------------|---------------------|-----------------|----------------------|
| test_data/projects/valid-project | test_data/agents/base-missing | file_not_found | "Error: Could not load base agent configuration from test_data/agents/base-missing/agent.json: File not found" |
| test_data/projects/valid-project | test_data/agents/base-invalid-json | invalid_json | "Error: Could not load base agent configuration from test_data/agents/base-invalid-json/agent.json: Invalid JSON syntax" |
| test_data/projects/valid-project | test_data/agents/base-missing-required | missing_required_field | "Error: Could not load base agent configuration from test_data/agents/base-missing-required/agent.json: Missing required field 'prompt_templates'" |
| test_data/projects/valid-project | test_data/agents/base-empty | empty_file | "Error: Could not load base agent configuration from test_data/agents/base-empty/agent.json: File is empty" |

### Scenario Outline: Agent fails to load agent-specific configuration

**Steps:**
```gherkin
Given test project area is set up at "<test_project_area>"
And test agent base area is set up at "<test_agent_base_area>"
And test agent stories area is set up at "<test_agent_stories_area>"
And valid base agent.json exists at "<test_agent_base_area>/agent.json>"
And stories agent.json has error condition "<error_condition>"
Then Agent loads base configuration from "<test_agent_base_area>/agent.json" successfully
When Agent attempts to load Story Agent configuration from "<test_agent_stories_area>/agent.json"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1213)
Then Agent detects error condition "<error_condition>"
And Agent handles missing or corrupted agent config error gracefully
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1219)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And error "<expected_error_message>" is presented to user in chat
But Agent does not create Behavior objects from behaviors configuration
But Agent does not create behaviors dictionary
But Agent does not call Agent.connect_workflow_to_project()
But Agent does not pass behaviors dictionary to Workflow
But Agent does not initialize Workflow stages
```

**Examples:**
| test_project_area | test_agent_base_area | test_agent_stories_area | error_condition | expected_error_message |
|-------------------|---------------------|-------------------------|-----------------|----------------------|
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories-missing | file_not_found | "Error: Could not load Story Agent configuration from test_data/agents/stories-missing/agent.json: File not found" |
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories-invalid-json | invalid_json | Stories agent.json contains invalid JSON syntax |
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories-missing-behaviors | missing_required_field | Stories agent.json missing required "behaviors" field |
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories-empty | empty_file | Stories agent.json is empty file |

### Scenario Outline: Workflow receives behaviors dictionary with missing order property

**Steps:**
```gherkin
Given test project area is set up at "<test_project_area>"
And test agent base area is set up at "<test_agent_base_area>"
And test agent stories area is set up at "<test_agent_stories_area>"
And valid base agent.json exists at "<test_agent_base_area>/agent.json>"
And agent.json with missing order properties exists at "<test_agent_stories_area>/agent.json>"
And Agent has loaded configurations
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1082)
And behaviors dictionary contains behaviors: "<behaviors_list>"
And behavior "<behavior_without_order>" in behaviors dictionary does not have "order" property
When Agent passes behaviors dictionary to Workflow
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1240)
And Workflow attempts to sort behaviors by order property
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1246)
Then Workflow detects missing order property in behavior "<behavior_without_order>"
And Workflow handles missing order property gracefully
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1252)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And Workflow uses insertion order for behaviors without order property
And order is presented to user for confirmation in chat
When user confirms order
Then Workflow proceeds with insertion order
And error is logged with message "<expected_error_message>"
And error type is "<expected_error_type>"
And behaviors are ordered as "<final_behavior_order>"
```

**Examples:**
| test_project_area | test_agent_base_area | test_agent_stories_area | behaviors_list | behavior_without_order | expected_error_message | expected_error_type | final_behavior_order |
|-------------------|---------------------|------------------------|--------------|----------------------|----------------------|-------------------|---------------------|
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories-missing-order | shape,prioritization,discovery,exploration,specification | shape | "Behavior 'shape' missing order property, using insertion order" | warning | shape,prioritization,discovery,exploration,specification |
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories-missing-order | shape,prioritization,discovery,exploration,specification | prioritization | "Behavior 'prioritization' missing order property, using insertion order" | warning | shape,prioritization,discovery,exploration,specification |

### Scenario Outline: Workflow receives behaviors dictionary with duplicate order values

**Steps:**
```gherkin
Given test project area is set up at "<test_project_area>"
And test agent base area is set up at "<test_agent_base_area>"
And test agent stories area is set up at "<test_agent_stories_area>"
And valid base agent.json exists at "<test_agent_base_area>/agent.json>"
And agent.json with duplicate order values exists at "<test_agent_stories_area>/agent.json>"
And Agent has loaded configurations
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1082)
And behaviors dictionary contains behaviors: "<behaviors_list>"
And behaviors "<behaviors_with_duplicate>" in behaviors dictionary have same order value "<duplicate_order_value>"
When Agent passes behaviors dictionary to Workflow
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1240)
And Workflow attempts to sort behaviors by order property
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1246)
Then Workflow detects duplicate order value "<duplicate_order_value>" in behaviors "<behaviors_with_duplicate>"
And Workflow handles duplicate order values gracefully
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1276)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And Workflow maintains insertion order "<maintained_order>" for behaviors with duplicate order values
And order is presented to user for confirmation in chat
When user confirms order
Then workflow stages are set up correctly with order "<final_stage_order>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1288)
```

**Examples:**
| test_project_area | test_agent_base_area | test_agent_stories_area | behaviors_list | duplicate_order_value | behaviors_with_duplicate | maintained_order | final_stage_order |
|-------------------|---------------------|------------------------|--------------|---------------------|-------------------------|-----------------|------------------|
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories-duplicate-order | shape,prioritization,discovery,exploration,specification | 1 | shape,prioritization | shape,prioritization,discovery,exploration,specification | shape,prioritization,discovery,exploration,specification |
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories-duplicate-order | shape,prioritization,discovery,exploration,specification | 2 | discovery,exploration | shape,prioritization,discovery,exploration,specification | shape,prioritization,discovery,exploration,specification |

### Scenario Outline: Workflow fails to get first behavior from sorted stages

**Steps:**
```gherkin
Given test project area is set up at "<test_project_area>"
And test agent base area is set up at "<test_agent_base_area>"
And test agent stories area is set up at "<test_agent_stories_area>"
And valid base agent.json exists at "<test_agent_base_area>/agent.json>"
And agent.json with empty behaviors exists at "<test_agent_stories_area>/agent.json>"
And Agent has loaded configurations
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1082)
And Workflow has set up stages
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1295)
And sorted stages list is empty due to "<empty_stages_reason>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1301)
When Agent calls Workflow to start
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1308)
And Workflow attempts to get first behavior from sorted stages
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1314)
Then Workflow detects empty stages list
And Workflow handles empty stages list gracefully
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1320)
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And error is returned to Agent with type "<expected_error_type>"
And error message contains "<expected_error_message>"
And Agent presents error "<expected_error_message>" to user in chat
And Agent does not present invalid workflow state to user
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1338)
```

**Examples:**
| test_project_area | test_agent_base_area | test_agent_stories_area | empty_stages_reason | expected_error_type | expected_error_message |
|-------------------|---------------------|------------------------|-------------------|-------------------|---------------------|
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories-empty-behaviors | empty_behaviors_dict | ValueError | "Cannot start workflow: no behaviors defined. Stages list is empty." |
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories-no-behaviors-field | missing_behaviors_field | ValueError | "Cannot start workflow: no behaviors defined. Stages list is empty." |

### Scenario Outline: Workflow initializes with default actions when behavior has no custom actions defined

**Steps:**
```gherkin
Given test project area is set up at "<test_project_area>"
And test agent base area is set up at "<test_agent_base_area>"
And test agent stories area is set up at "<test_agent_stories_area>"
And valid base agent.json exists at "<test_agent_base_area>/agent.json>"
And agent.json with behavior without actions array exists at "<test_agent_stories_area>/agent.json>"
And Agent has loaded configurations
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1082)
And Workflow has set up stages
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1295)
And first behavior "<behavior_name>" has no "actions" array defined in behavior configuration at "<config_path>"
When Agent calls Workflow to start
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1308)
And Workflow gets first behavior "<behavior_name>" from sorted stages
And Behavior initializes Actions from configuration at "<config_path>"
Then Behavior detects no custom actions array in configuration
And Behavior uses all default actions "<default_actions>"
And Workflow initializes first action "<first_action>" from default actions
And Workflow sets current_stage to "<expected_stage>"
And Workflow sets current_action to "<expected_action>"
And Agent presents workflow state to user for confirmation with stage "<expected_stage>" and action "<expected_action>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1072)
```

**Examples:**
| test_project_area | test_agent_base_area | test_agent_stories_area | behavior_name | config_path | default_actions | first_action | expected_stage | expected_action |
|-------------------|---------------------|------------------------|--------------|------------|----------------|-------------|----------------|----------------|
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories-no-actions | shape | test_data/agents/stories-no-actions/agent.json | clarification,planning,build_structure,render_output,validate,correct | clarification | shape | clarification |
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories-no-actions | prioritization | test_data/agents/stories-no-actions/agent.json | clarification,planning,build_structure,render_output,validate,correct | clarification | prioritization | clarification |

### Scenario Outline: Workflow initializes with custom actions when behavior defines custom actions array

**Steps:**
```gherkin
Given test project area is set up at "<test_project_area>"
And test agent base area is set up at "<test_agent_base_area>"
And test agent stories area is set up at "<test_agent_stories_area>"
And valid base agent.json exists at "<test_agent_base_area>/agent.json>"
And agent.json with custom actions array exists at "<test_agent_stories_area>/agent.json>"
And Agent has loaded configurations
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1082)
And Workflow has set up stages
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1295)
And first behavior "<behavior_name>" has "actions" array defined in behavior configuration at "<config_path>" with custom action names "<custom_actions>"
When Agent calls Workflow to start
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1308)
And Workflow gets first behavior "<behavior_name>" from sorted stages
And Behavior initializes Actions from configuration at "<config_path>"
Then Behavior detects custom actions array in configuration
And Behavior uses only custom actions "<custom_actions>" (replaces all default actions)
And Workflow initializes first action "<first_action>" from custom actions
And Workflow sets current_stage to "<expected_stage>"
And Workflow sets current_action to "<expected_action>"
And Agent presents workflow state to user for confirmation with stage "<expected_stage>" and action "<expected_action>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1072)
```

**Examples:**
| test_project_area | test_agent_base_area | test_agent_stories_area | behavior_name | config_path | custom_actions | first_action | expected_stage | expected_action |
|-------------------|---------------------|------------------------|--------------|------------|--------------|-------------|----------------|----------------|
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories-custom-actions | shape | test_data/agents/stories-custom-actions/agent.json | custom_action1,custom_action2 | custom_action1 | shape | custom_action1 |
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories-custom-actions | prioritization | test_data/agents/stories-custom-actions/agent.json | setup,execute,validate | setup | prioritization | setup |

### Scenario Outline: Project workflow attribute missing during synchronization

**Steps:**
```gherkin
Given test project area is set up at "<test_project_area>"
And test agent base area is set up at "<test_agent_base_area>"
And test agent stories area is set up at "<test_agent_stories_area>"
And valid base agent.json exists at "<test_agent_base_area>/agent.json>"
And valid stories agent.json exists at "<test_agent_stories_area>/agent.json>"
And Agent has loaded configurations
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1082)
And Workflow has been initialized
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1369)
And Project does not have workflow attribute due to "<missing_reason>"
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1375)
When AgentStateManager attempts to synchronize workflow
  [🔗](../../../../../../src/stories_acceptance_tests.py#L1382)
Then AgentStateManager checks if Project has workflow attribute
And AgentStateManager detects workflow attribute is missing due to "<missing_reason>"
When Project workflow attribute is missing
Then AgentStateManager sets Project.workflow to Agent.workflow
And system does not crash
  [🔗](../../../../../../src/stories_acceptance_tests.py#L301)
And Project workflow attribute is created and synchronized
And Workflow state after sync is "<expected_workflow_state>"
And verification confirms Project.workflow references same object as Agent.workflow: "<expected_object_reference_match>"
```

**Examples:**
| test_project_area | test_agent_base_area | test_agent_stories_area | missing_reason | expected_workflow_state | expected_object_reference_match |
|-------------------|---------------------|------------------------|--------------|----------------------|---------------------------|
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories | attribute_not_set | shape:clarification | true |
| test_data/projects/valid-project | test_data/agents/base | test_data/agents/stories | attribute_none | shape:clarification | true |

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase

