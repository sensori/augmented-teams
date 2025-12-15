# Refactor Test Analysis: New Classes and Required Tests

## Overview
This document analyzes all new classes created in the last 3 commits with "code refactor" messages and identifies required test files following the story-epic/sub-epic pattern.

## Commits Analyzed
1. `7f0285b0` - code refactor: first pass
2. `f2c26ddc` - code refactor: first pass complete  
3. `d083232b` - code refactor 2 : actions part 1

---

## Phase 9 & 10: Instructions and TriggerWords Classes

### New Classes Created
1. **TriggerWords** (`src/bot/trigger_words.py`) - Already existed, parameter updated
2. **Instructions** (`src/bot/instructions.py`) - Already existed
3. **MergedInstructions** (`src/bot/merged_instructions.py`) - **NEWLY CREATED**

### Test Files Created
- ✅ `test_trigger_words.py` - Created
- ✅ `test_instructions.py` - Created
- ⚠️ `test_merged_instructions.py` - Needs to be recreated (was deleted)

---

## Phase 4: Rules and Validation Classes

### New Classes Created (from commit d083232b)
1. **Rules** (`src/actions/validate_rules/rules.py`) - Collection class
2. **Rule** (`src/actions/validate_rules/rule.py`) - Individual rule class
3. **ValidationScope** (`src/actions/validate_rules/validation_scope.py`) - **NEW**
4. **KnowledgeGraph** (`src/actions/validate_rules/knowledge_graph.py`) - **NEW**
5. **ScannerLoader** (`src/bot/scanner_loader.py`) - Service class

### Changes to Existing Classes
- **ValidateRulesAction** - Refactored to use Rules collection
- **Rule** - Extracted scanner loading to ScannerLoader
- **Violation** - Property renamed from `rule` to `validates_rule`

### Required Test Files
- ⚠️ `test_rules.py` - **MISSING** - Test Rules collection class
- ⚠️ `test_rule.py` - **MISSING** - Test Rule class
- ⚠️ `test_validation_scope.py` - **MISSING** - Test ValidationScope class
- ⚠️ `test_scanner_loader.py` - **MISSING** - Test ScannerLoader service
- ✅ `test_validate_knowledge_and_content_against_rules.py` - Exists, may need updates

---

## Phase 3: Actions Collection and Action Classes

### New Classes Created (from commit d083232b)
1. **Action** (`src/actions/action.py`) - Base action class
2. **Actions** (`src/actions/actions.py`) - Actions collection class
3. **BaseActionConfig** (`src/actions/base_action_config.py`) - Base action configuration

### Required Test Files
- ⚠️ `test_action.py` - **MISSING** - Test Action base class
- ⚠️ `test_actions.py` - **MISSING** - Test Actions collection class
- ⚠️ `test_base_action_config.py` - **MISSING** - Test BaseActionConfig class

---

## Phase 6: Content and Knowledge Classes

### New Classes Created (from commit d083232b)
1. **Content** (`src/actions/content.py`) - Content aggregator
2. **KnowledgeGraphSpec** (`src/actions/build_knowledge/knowledge_graph_spec.py`) - **NEW**
3. **KnowledgeGraphTemplate** (`src/actions/build_knowledge/knowledge_graph_template.py`) - **NEW**
4. **Knowledge** (`src/actions/build_knowledge/knowledge.py`) - **NEW**
5. **RenderSpec** (`src/actions/render_output/render_spec.py`) - **NEW**
6. **Template** (`src/actions/render_output/template.py`) - **NEW**
7. **Synchronizer** (`src/actions/render_output/synchronizer.py`) - **NEW**

### Required Test Files
- ⚠️ `test_content.py` - **MISSING** - Test Content class
- ⚠️ `test_knowledge_graph_spec.py` - **MISSING** - Test KnowledgeGraphSpec
- ⚠️ `test_knowledge_graph_template.py` - **MISSING** - Test KnowledgeGraphTemplate
- ⚠️ `test_knowledge.py` - **MISSING** - Test Knowledge class
- ⚠️ `test_render_spec.py` - **MISSING** - Test RenderSpec class
- ⚠️ `test_template.py` - **MISSING** - Test Template class
- ⚠️ `test_synchronizer.py` - **MISSING** - Test Synchronizer class
- ✅ `test_build_knowledge.py` - Exists, may need updates for new classes
- ✅ `test_render_output.py` - Exists, may need updates for new classes

---

## Phase 2: Behavior and Guardrails Classes

### New Classes Created (from commit d083232b)
1. **Behavior** (`src/bot/behavior.py`) - Refactored
2. **BehaviorConfig** (`src/bot/behavior_config.py`) - **NEW**
3. **Behaviors** (`src/bot/behaviors.py`) - Collection class
4. **BotConfig** (`src/bot/bot_config.py`) - **NEW**
5. **BotPaths** (`src/bot/bot_paths.py`) - **NEW**
6. **Guardrails** (`src/actions/guardrails.py`) - **NEW**

### Required Test Files
- ✅ `test_perform_behavior_action.py` - Exists, covers Behavior
- ⚠️ `test_behavior_config.py` - **MISSING** - Test BehaviorConfig class
- ⚠️ `test_behaviors.py` - **MISSING** - Test Behaviors collection
- ⚠️ `test_bot_config.py` - **MISSING** - Test BotConfig class
- ⚠️ `test_bot_paths.py` - **MISSING** - Test BotPaths class
- ⚠️ `test_guardrails.py` - **MISSING** - Test Guardrails class

---

## Gather Context Action Domain Objects

### New Classes Created (from commit d083232b)
1. **GatherContextAction** (`src/actions/gather_context/gather_context_action.py`)
2. **KeyQuestions** (`src/actions/gather_context/key_questions.py`) - **NEW**
3. **RequiredContext** (`src/actions/gather_context/required_context.py`) - **NEW**
4. **RecommendedActivities** (`src/actions/gather_context/recommended_activities.py`) - **NEW**
5. **RequirementsClarifications** (`src/actions/gather_context/requirements_clarifications.py`) - **NEW**

### Required Test Files
- ✅ `test_gather_context.py` - Exists
- ⚠️ `test_key_questions.py` - **MISSING** - Test KeyQuestions class
- ⚠️ `test_required_context.py` - **MISSING** - Test RequiredContext class
- ⚠️ `test_gather_recommended_activities.py` - **MISSING** - Test RecommendedActivities (gather_context)
- ⚠️ `test_requirements_clarifications.py` - **MISSING** - Test RequirementsClarifications

---

## Decide Strategy Action Domain Objects

### New Classes Created (from commit d083232b)
1. **DecideStrategyAction** (`src/actions/decide_strategy/decide_strategy_action.py`)
2. **Strategy** (`src/actions/decide_strategy/strategy.py`) - **NEW**
3. **StrategyCriterias** (`src/actions/decide_strategy/strategy_criterias.py`) - **NEW**
4. **StrategyCriteria** (`src/actions/decide_strategy/strategy_criteria.py`) - **NEW**
5. **Assumptions** (`src/actions/decide_strategy/assumptions.py`) - **NEW**
6. **Evidence** (`src/actions/decide_strategy/evidence.py`) - **NEW**
7. **RecommendedActivities** (`src/actions/decide_strategy/recommended_activities.py`) - **NEW**
8. **StrategyDecision** (`src/actions/decide_strategy/strategy_decision.py`) - **NEW**
9. **JsonPersistent** (`src/actions/decide_strategy/json_persistent.py`) - **NEW**

### Required Test Files
- ✅ `test_decide_strategy_criteria_action.py` - Exists
- ⚠️ `test_strategy.py` - **MISSING** - Test Strategy class
- ⚠️ `test_strategy_criterias.py` - **MISSING** - Test StrategyCriterias collection
- ⚠️ `test_strategy_criteria.py` - **MISSING** - Test StrategyCriteria class
- ⚠️ `test_assumptions.py` - **MISSING** - Test Assumptions class
- ⚠️ `test_evidence.py` - **MISSING** - Test Evidence class
- ⚠️ `test_strategy_recommended_activities.py` - **MISSING** - Test RecommendedActivities (decide_strategy)
- ⚠️ `test_strategy_decision.py` - **MISSING** - Test StrategyDecision class
- ⚠️ `test_json_persistent.py` - **MISSING** - Test JsonPersistent class

---

## Summary: Missing Test Files

### High Priority (Core Classes)
1. `test_merged_instructions.py` - MergedInstructions class
2. `test_rules.py` - Rules collection
3. `test_rule.py` - Rule class
4. `test_actions.py` - Actions collection
5. `test_action.py` - Action base class
6. `test_base_action_config.py` - BaseActionConfig
7. `test_behavior_config.py` - BehaviorConfig
8. `test_behaviors.py` - Behaviors collection
9. `test_bot_config.py` - BotConfig
10. `test_bot_paths.py` - BotPaths

### Medium Priority (Domain Objects)
11. `test_validation_scope.py` - ValidationScope
12. `test_scanner_loader.py` - ScannerLoader
13. `test_content.py` - Content
14. `test_guardrails.py` - Guardrails
15. `test_knowledge_graph_spec.py` - KnowledgeGraphSpec
16. `test_knowledge_graph_template.py` - KnowledgeGraphTemplate
17. `test_knowledge.py` - Knowledge
18. `test_render_spec.py` - RenderSpec
19. `test_template.py` - Template
20. `test_synchronizer.py` - Synchronizer

### Lower Priority (Action-Specific Domain Objects)
21. `test_key_questions.py` - KeyQuestions
22. `test_required_context.py` - RequiredContext
23. `test_gather_recommended_activities.py` - RecommendedActivities (gather_context)
24. `test_requirements_clarifications.py` - RequirementsClarifications
25. `test_strategy.py` - Strategy
26. `test_strategy_criterias.py` - StrategyCriterias
27. `test_strategy_criteria.py` - StrategyCriteria
28. `test_assumptions.py` - Assumptions
29. `test_evidence.py` - Evidence
30. `test_strategy_recommended_activities.py` - RecommendedActivities (decide_strategy)
31. `test_strategy_decision.py` - StrategyDecision
32. `test_json_persistent.py` - JsonPersistent

---

## Test Structure Requirements

All test files must follow the story-epic/sub-epic pattern:
- File header describing sub-epic
- Test classes named `Test<StoryName>`
- Test methods named `test_<scenario_description>`
- Helper functions with `given_`, `when_`, `then_` prefixes
- Follow pattern from `test_perform_behavior_action.py`

---

## Next Steps

1. Recreate `test_merged_instructions.py`
2. Create high-priority test files for core classes
3. Update existing test files to verify integration with new classes
4. Create medium-priority test files for domain objects
5. Create lower-priority test files for action-specific domain objects

