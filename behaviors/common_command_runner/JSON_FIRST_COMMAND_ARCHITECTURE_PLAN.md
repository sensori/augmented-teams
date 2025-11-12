# JSON-First Command Architecture Plan

## Executive Summary

**Architectural Shift:** Move to **structured JSON as the source of truth** that the code reads to generate prompts. JSON contains all command definitions, rules, principles, and workflow patterns. From JSON, we **generate BOTH**:
1. **Prompts for AI** - What the code uses to instruct AI during command execution
2. **Markdown documentation** - Following the template standards from PROMPT_BASED_COMMAND_REFACTORING_PLAN.md for human consumption

The markdown files (commands, rules, prompts) still exist and follow our template standards - they're just **generated from JSON** rather than being the source that code reads. This gives us structured data for code + readable documentation for humans.

---

## Core Principles

### 1. **JSON as Source of Truth (Not Replacement for Markdown)**
- **JSON defines everything**: Commands, rules, principles, examples, workflow steps
- **Code reads JSON**: Python infrastructure loads JSON, generates prompts for AI
- **Markdown is generated FROM JSON**: Human-readable docs created following PROMPT_BASED_COMMAND_REFACTORING_PLAN.md templates
- **Both outputs from one source**: 
  - Python code uses JSON to build AI prompts
  - Markdown generator creates documentation files following template standards
- **Version control friendly**: Structured diffs in JSON, readable docs in markdown

### 2. **Built-In Workflow Infrastructure**
Common patterns are first-class concepts in the base infrastructure:
- **Assumptions**: Track what AI assumes during execution
- **Questions**: Prompting questions (pre-action) and clarifying questions (post-action)
- **Decisions**: Document consolidate/separate choices and other judgment calls
- **Clarifications**: Request user input on uncertain items
- **Checklists**: Validation checklists applied consistently
- **Templates**: Reusable workflow patterns

### 3. **Thoughtful CLI Design**
- **Natural command structure**: `python runner.py <entity> <action> [params]`
- **Fewer complex commands**: CLI handles common patterns automatically
- **Interactive mode**: Prompt for missing parameters instead of failing
- **Help built-in**: `--help` on any command shows context-aware guidance

### 4. **Template-Oriented Architecture**
- **Command templates**: Define once, reuse across features
- **Workflow templates**: Standard patterns (generate, validate, correct)
- **Rule templates**: Principle structure standardized
- **Output templates**: Consistent formatting

---

## New Architecture Overview

```
behaviors/
  common_command_runner/
    infrastructure/
      ├── workflow_engine.py          # Executes workflow steps
      ├── assumption_tracker.py       # Tracks AI assumptions
      ├── question_manager.py         # Manages prompting/clarifying questions
      ├── decision_log.py             # Records decision rationale
      ├── checklist_engine.py         # Runs validation checklists
      ├── template_engine.py          # Loads and processes templates
      └── cli_builder.py              # Generates CLI from JSON definitions
    
    schemas/
      ├── command_schema.json         # JSON schema for commands
      ├── rule_schema.json            # JSON schema for rules/principles
      ├── workflow_schema.json        # JSON schema for workflows
      ├── checklist_schema.json       # JSON schema for checklists
      └── template_schema.json        # JSON schema for templates
    
    templates/
      ├── workflow_templates.json     # Standard workflow patterns
      ├── command_templates.json      # Command structure templates
      └── validation_templates.json   # Validation pattern templates
    
    json_command_runner.py            # New base runner that reads JSON
    markdown_generator.py             # Generates .md files from JSON
    
  stories/
    definitions/
      ├── story-shape-command.json      # Command definition in JSON
      ├── story-discovery-command.json  # Command definition in JSON
      ├── stories-rule.json             # Rules and principles in JSON
      └── checklists/
          ├── consolidation-checklist.json
          └── story-format-checklist.json
    
    generated/  # Generated markdown (not edited directly)
      ├── story-shape-cmd.md          # Generated from JSON
      ├── story-discovery-cmd.md      # Generated from JSON
      └── stories-rule.mdc            # Generated from JSON
    
    stories_runner.py                 # Loads JSON, uses infrastructure
```

---

## JSON Schema Definitions

### 1. Command Definition Schema

**File:** `behaviors/common_command_runner/schemas/command_schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Command Definition",
  "type": "object",
  "required": ["command_id", "name", "description", "entity_type", "actions"],
  "properties": {
    "command_id": {
      "type": "string",
      "description": "Unique identifier (e.g., 'story-discovery')"
    },
    "name": {
      "type": "string",
      "description": "Human-readable command name"
    },
    "description": {
      "type": "string",
      "description": "What this command does"
    },
    "entity_type": {
      "type": "string",
      "enum": ["story", "test", "code", "rule", "structure", "interaction"],
      "description": "Type of entity this command operates on"
    },
    "actions": {
      "type": "object",
      "description": "Available actions (generate, validate, correct, etc.)",
      "properties": {
        "generate": { "$ref": "#/definitions/action" },
        "validate": { "$ref": "#/definitions/action" },
        "correct": { "$ref": "#/definitions/action" },
        "plan": { "$ref": "#/definitions/action" }
      }
    },
    "cli": {
      "type": "object",
      "description": "CLI configuration",
      "properties": {
        "aliases": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Alternative command names"
        },
        "arguments": {
          "type": "array",
          "items": { "$ref": "#/definitions/cli_argument" }
        }
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "version": { "type": "string" },
        "author": { "type": "string" },
        "last_updated": { "type": "string", "format": "date-time" }
      }
    }
  },
  "definitions": {
    "action": {
      "type": "object",
      "required": ["workflow_template", "prompting_questions"],
      "properties": {
        "workflow_template": {
          "type": "string",
          "description": "Reference to workflow template (e.g., 'interactive_generate')"
        },
        "prompting_questions": {
          "type": "array",
          "items": { "$ref": "#/definitions/question" },
          "description": "Questions that MUST be answered before action proceeds"
        },
        "instructions": {
          "type": "object",
          "description": "Action-specific instructions",
          "properties": {
            "objective": { "type": "string" },
            "steps": {
              "type": "array",
              "items": { "type": "string" }
            },
            "rules_to_apply": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "rule_file": { "type": "string" },
                  "principle_ids": {
                    "type": "array",
                    "items": { "type": "string" }
                  }
                }
              }
            }
          }
        },
        "assumptions": {
          "type": "array",
          "items": { "$ref": "#/definitions/assumption_template" },
          "description": "Expected assumptions AI will make"
        },
        "clarifying_questions": {
          "type": "array",
          "items": { "$ref": "#/definitions/question_template" },
          "description": "Templates for questions to ask user"
        },
        "checklists": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "checklist_file": { "type": "string" },
              "when": { "type": "string", "enum": ["before", "after", "during"] }
            }
          }
        },
        "templates": {
          "type": "object",
          "properties": {
            "output_template": { "type": "string" },
            "report_template": { "type": "string" }
          }
        }
      }
    },
    "question": {
      "type": "object",
      "required": ["id", "text", "required"],
      "properties": {
        "id": { "type": "string" },
        "text": { "type": "string" },
        "required": { "type": "boolean" },
        "context_paths": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Where to look for answer in context (e.g., 'open_files', 'recent_edits')"
        },
        "inference_hints": {
          "type": "array",
          "items": { "type": "string" },
          "description": "How AI might infer the answer"
        }
      }
    },
    "assumption_template": {
      "type": "object",
      "properties": {
        "category": {
          "type": "string",
          "enum": ["data", "logic", "structure", "priority", "scope"]
        },
        "description": { "type": "string" },
        "examples": {
          "type": "array",
          "items": { "type": "string" }
        },
        "uncertainty_factors": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "question_template": {
      "type": "object",
      "properties": {
        "trigger": {
          "type": "string",
          "description": "When to ask this question (e.g., 'medium_or_high_uncertainty')"
        },
        "template": { "type": "string" },
        "options": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "label": { "type": "string" },
              "description": { "type": "string" }
            }
          }
        }
      }
    },
    "cli_argument": {
      "type": "object",
      "required": ["name", "type"],
      "properties": {
        "name": { "type": "string" },
        "type": { "type": "string", "enum": ["string", "int", "bool", "path", "list"] },
        "required": { "type": "boolean" },
        "default": {},
        "help": { "type": "string" },
        "aliases": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    }
  }
}
```

### Example Command Definition: Story Discovery

**File:** `behaviors/stories/definitions/story-discovery-command.json`

```json
{
  "command_id": "story-discovery",
  "name": "Story Discovery",
  "description": "Exhaustively decompose stories for market increment(s) in focus",
  "entity_type": "story",
  "version": "2.0.0",
  "actions": {
    "generate": {
      "workflow_template": "interactive_generate_with_decisions",
      "prompting_questions": [
        {
          "id": "increment_focus",
          "text": "Which market increment(s) are we focusing on for discovery?",
          "required": true,
          "context_paths": ["open_files", "recent_edits", "chat_history"],
          "inference_hints": [
            "Look for 'INCREMENT:' markers in open story map",
            "Check recent chat for increment mentions",
            "Default to 'NOW' increment if mentioned in context"
          ]
        },
        {
          "id": "story_map_location",
          "text": "Where is the existing story map file located?",
          "required": true,
          "context_paths": ["open_files", "workspace_files"],
          "inference_hints": [
            "Search for '*-story-map.md' in docs/stories/map/",
            "Use most recently modified story map",
            "Use file open in editor if it matches pattern"
          ]
        },
        {
          "id": "new_insights",
          "text": "What new information or insights have been discovered since shaping?",
          "required": false,
          "context_paths": ["chat_history", "attached_files"],
          "inference_hints": [
            "Review conversation for business context",
            "Check for attached documents or notes",
            "Can proceed without if not mentioned"
          ]
        }
      ],
      "instructions": {
        "objective": "Update story map with exhaustive decomposition for increment(s) in focus. For EACH story, decide: consolidate (same logic, different data) or separate (different logic/formulas).",
        "steps": [
          "1. Load existing story map and identify increment(s) marked as focus",
          "2. For each feature in focus increment, enumerate all stories (NO ~X notation)",
          "3. For each story, apply consolidation decision framework",
          "4. Document EVERY consolidate/separate decision with reasoning",
          "5. Update story map with final decomposition",
          "6. Ensure all stories follow '[Verb] [Noun]' format"
        ],
        "rules_to_apply": [
          {
            "rule_file": "stories-rule.json",
            "principle_ids": ["2.5", "2.6", "2.7"]
          }
        ]
      },
      "assumptions": [
        {
          "category": "logic",
          "description": "Determining if stories have 'same logic' vs 'different logic'",
          "examples": [
            "Stories with same UI but different data → CONSOLIDATE assumption",
            "Stories with different formulas → SEPARATE assumption",
            "Stories with similar descriptions but possibly different validation → UNCERTAIN"
          ],
          "uncertainty_factors": [
            "Cannot see actual code/validation rules",
            "Descriptions may be incomplete",
            "Business logic differences not always explicit"
          ]
        },
        {
          "category": "structure",
          "description": "Grouping related stories under features",
          "examples": [
            "Stories about 'character creation' grouped under Character feature",
            "Combat-related stories grouped under Combat feature"
          ],
          "uncertainty_factors": [
            "Feature boundaries may be subjective",
            "Some stories span multiple features"
          ]
        },
        {
          "category": "scope",
          "description": "What counts as 'in focus' for this increment",
          "examples": [
            "All NOW increment stories are in focus",
            "Only specific features marked with 'FOCUS' tag"
          ],
          "uncertainty_factors": [
            "Increment scope not always explicit",
            "May need to clarify with user"
          ]
        }
      ],
      "clarifying_questions": [
        {
          "trigger": "medium_or_high_uncertainty_on_consolidation",
          "template": "**Consolidation Decision Question:**\n\nStories being considered: {story_list}\nCurrent Decision: {decision}\nReasoning: {reasoning}\nUncertainty: {uncertainty_level}\n\nQuestion: Should these stories be:\n- Option A: {option_a}\n- Option B: {option_b}\n- Option C: Need more context\n\nCurrent choice: {current_choice}\nWhy uncertain: {uncertainty_explanation}\n\nYour decision: A, B, or C?"
        },
        {
          "trigger": "unclear_increment_scope",
          "template": "I found multiple possible interpretations of the increment scope:\n\n{interpretations}\n\nWhich interpretation is correct?"
        }
      ],
      "checklists": [
        {
          "checklist_file": "consolidation-checklist.json",
          "when": "during"
        },
        {
          "checklist_file": "story-format-checklist.json",
          "when": "after"
        }
      ],
      "templates": {
        "output_template": "story-map-update-template.json",
        "report_template": "decision-log-template.json"
      }
    },
    "validate": {
      "workflow_template": "interactive_validate_with_heuristics",
      "prompting_questions": [
        {
          "id": "story_map_to_validate",
          "text": "Which story map file should be validated?",
          "required": true,
          "context_paths": ["open_files", "recent_edits"],
          "inference_hints": [
            "Use currently open story map file",
            "Use file just generated in previous step"
          ]
        }
      ],
      "instructions": {
        "objective": "Validate story map follows discovery principles: exhaustive decomposition, correct consolidation, proper story format",
        "steps": [
          "1. Run automated heuristics first",
          "2. AI validates consolidation decisions (same logic → consolidated, different logic → separated)",
          "3. AI checks exhaustive decomposition (no ~X in focus increments)",
          "4. AI validates story format ('[Verb] [Noun]')",
          "5. List all violations with severity",
          "6. For each violation, propose fix with rationale"
        ],
        "rules_to_apply": [
          {
            "rule_file": "stories-rule.json",
            "principle_ids": ["2.5", "2.6", "2.7", "2.8"]
          }
        ]
      },
      "assumptions": [
        {
          "category": "logic",
          "description": "Judging if consolidation/separation is correct based on descriptions",
          "uncertainty_factors": [
            "Cannot see actual implementation",
            "Descriptions may not reveal all logic differences"
          ]
        }
      ],
      "clarifying_questions": [
        {
          "trigger": "consolidation_violation_found",
          "template": "**Consolidation Violation:**\n\nViolation: {violation_description}\nStories involved: {story_list}\nAnalysis: {analysis}\n\nQuestion: Should these stories:\n- Option A: {fix_option_a}\n- Option B: {fix_option_b}\n- Option C: Need more detail to determine\n\nRecommended: {recommended_option}\nUser Decision Needed: Which option?"
        }
      ],
      "checklists": [
        {
          "checklist_file": "discovery-validation-checklist.json",
          "when": "during"
        }
      ]
    }
  },
  "cli": {
    "aliases": ["discovery", "disc"],
    "arguments": [
      {
        "name": "story_map",
        "type": "path",
        "required": false,
        "help": "Path to story map file (inferred if not provided)"
      },
      {
        "name": "increment",
        "type": "string",
        "required": false,
        "aliases": ["-i", "--increment"],
        "help": "Increment to focus on (NOW/NEXT/LATER)"
      },
      {
        "name": "interactive",
        "type": "bool",
        "default": true,
        "aliases": ["-I", "--interactive"],
        "help": "Enable interactive mode (prompts for missing info)"
      }
    ]
  }
}
```

---

### 2. Rule Definition Schema

**File:** `behaviors/common_command_runner/schemas/rule_schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Rule Definition",
  "type": "object",
  "required": ["rule_id", "name", "description", "principles"],
  "properties": {
    "rule_id": { "type": "string" },
    "name": { "type": "string" },
    "description": { "type": "string" },
    "version": { "type": "string" },
    "principles": {
      "type": "array",
      "items": { "$ref": "#/definitions/principle" }
    }
  },
  "definitions": {
    "principle": {
      "type": "object",
      "required": ["principle_id", "principle_name", "content"],
      "properties": {
        "principle_id": {
          "type": "string",
          "description": "Hierarchical ID (e.g., '2.5' or '2.5.1')"
        },
        "principle_name": { "type": "string" },
        "content": { "type": "string" },
        "examples": {
          "type": "array",
          "items": { "$ref": "#/definitions/example" }
        },
        "heuristics": {
          "type": "array",
          "items": { "$ref": "#/definitions/heuristic" },
          "description": "Automated checks for this principle"
        }
      }
    },
    "example": {
      "type": "object",
      "properties": {
        "do": {
          "type": "object",
          "properties": {
            "text": { "type": "string" },
            "code": { "type": "string" }
          }
        },
        "dont": {
          "type": "object",
          "properties": {
            "text": { "type": "string" },
            "code": { "type": "string" }
          }
        }
      }
    },
    "heuristic": {
      "type": "object",
      "required": ["heuristic_id", "type", "pattern"],
      "properties": {
        "heuristic_id": { "type": "string" },
        "type": {
          "type": "string",
          "enum": ["regex", "ast", "count", "custom"]
        },
        "pattern": { "type": "string" },
        "severity": {
          "type": "string",
          "enum": ["ERROR", "WARNING", "INFO"]
        },
        "message_template": { "type": "string" }
      }
    }
  }
}
```

### Example Rule: Story Discovery Principles

**File:** `behaviors/stories/definitions/stories-rule.json` (excerpt)

```json
{
  "rule_id": "stories-rule",
  "name": "Story Writing and Mapping Principles",
  "description": "Guidelines for creating story maps, decomposing stories, and maintaining story quality",
  "version": "3.0.0",
  "principles": [
    {
      "principle_id": "2.5",
      "principle_name": "Exhaustive Logic Decomposition for Discovery",
      "content": "When a market increment is in Discovery phase, ALL stories must be explicitly listed (NO ~X stories notation). Stories should be decomposed exhaustively, enumerating all logic permutations. Apply consolidation framework: SAME logic + different data → CONSOLIDATE into one story; DIFFERENT logic/formula/rule/algorithm → SEPARATE into different stories.",
      "examples": [
        {
          "dont": {
            "text": "Using ~X stories notation in Discovery phase (incomplete)",
            "code": "⚙️ Character Creation\n   📝 User creates character\n   📝 ~5 stories (abilities selection)\n   📝 ~3 stories (equipment selection)"
          },
          "do": {
            "text": "Exhaustive enumeration with consolidation applied",
            "code": "⚙️ Character Creation\n   📝 User creates character and system validates prerequisites\n   📝 User selects character option from catalog (advantages/powers/equipment)\n   📝 User assigns ability scores and system calculates derived stats\n   📝 User selects skills and system validates skill point allocation"
          }
        },
        {
          "dont": {
            "text": "Over-separating stories with same logic but different data",
            "code": "📝 User selects advantage from advantage list\n📝 User selects power from power list\n📝 User selects equipment from equipment list"
          },
          "do": {
            "text": "Consolidating stories with same logic, different data",
            "code": "📝 User selects character option from catalog (advantages/powers/equipment)"
          }
        }
      ],
      "heuristics": [
        {
          "heuristic_id": "no_estimation_in_discovery",
          "type": "regex",
          "pattern": "~\\d+\\s+stories",
          "severity": "ERROR",
          "message_template": "Found ~X stories notation at line {line}. Discovery phase requires exhaustive story enumeration."
        }
      ]
    },
    {
      "principle_id": "2.6",
      "principle_name": "Story Format - Action-Oriented Business Language",
      "content": "Stories must use '[Verb] [Noun]' format from user or system perspective. Format: 'User [verb] [noun]' or 'System [verb] [noun] when [trigger]'. Single 'and system [response]' clause allowed. NO examples or extra notes in story titles.",
      "examples": [
        {
          "do": {
            "text": "Proper story format with single action and system response",
            "code": "📝 User selects advantage and system validates prerequisites"
          },
          "dont": {
            "text": "Multiple system clauses or embedded examples",
            "code": "📝 User selects advantage (e.g., Combat Reflexes, Wealth) and system validates prerequisites and system updates point total"
          }
        }
      ],
      "heuristics": [
        {
          "heuristic_id": "no_examples_in_story_title",
          "type": "regex",
          "pattern": "\\(e\\.g\\.,",
          "severity": "ERROR",
          "message_template": "Found examples in story title at line {line}. Remove examples - they belong in story details."
        }
      ]
    }
  ]
}
```

---

### 3. Workflow Template Schema

**File:** `behaviors/common_command_runner/schemas/workflow_schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Workflow Template",
  "type": "object",
  "required": ["workflow_id", "name", "steps"],
  "properties": {
    "workflow_id": { "type": "string" },
    "name": { "type": "string" },
    "description": { "type": "string" },
    "steps": {
      "type": "array",
      "items": { "$ref": "#/definitions/workflow_step" }
    }
  },
  "definitions": {
    "workflow_step": {
      "type": "object",
      "required": ["step_id", "name", "type"],
      "properties": {
        "step_id": { "type": "string" },
        "name": { "type": "string" },
        "type": {
          "type": "string",
          "enum": [
            "check_context",
            "ask_user",
            "execute_action",
            "track_assumptions",
            "generate_questions",
            "wait_user_feedback",
            "run_heuristics",
            "ai_validate",
            "apply_fixes"
          ]
        },
        "instructions": { "type": "string" },
        "infrastructure_calls": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "module": { "type": "string" },
              "function": { "type": "string" },
              "params": { "type": "object" }
            }
          }
        },
        "next_step_conditions": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "condition": { "type": "string" },
              "next_step": { "type": "string" }
            }
          }
        }
      }
    }
  }
}
```

### Example Workflow: Interactive Generate with Decisions

**File:** `behaviors/common_command_runner/templates/workflow_templates.json`

```json
{
  "workflows": [
    {
      "workflow_id": "interactive_generate_with_decisions",
      "name": "Interactive Generate with Decision Tracking",
      "description": "Standard generate workflow with explicit decision logging and assumption tracking",
      "steps": [
        {
          "step_id": "check_context",
          "name": "Check Context Against Prompting Questions",
          "type": "check_context",
          "instructions": "Review prompting questions from command definition. Check if all required questions are answered in context (open files, chat history, attached docs). If any required question unanswered, proceed to ask_user step. If all answered, proceed to execute_action.",
          "infrastructure_calls": [
            {
              "module": "question_manager",
              "function": "check_prompting_questions",
              "params": {
                "questions": "{command.actions.generate.prompting_questions}",
                "context_sources": ["open_files", "chat_history", "workspace"]
              }
            }
          ],
          "next_step_conditions": [
            {
              "condition": "all_questions_answered",
              "next_step": "execute_action"
            },
            {
              "condition": "missing_required_answers",
              "next_step": "ask_user"
            }
          ]
        },
        {
          "step_id": "ask_user",
          "name": "Ask User for Missing Context",
          "type": "ask_user",
          "instructions": "Present unanswered questions to user. STOP and WAIT for user response. Do NOT proceed without answers to required questions.",
          "infrastructure_calls": [
            {
              "module": "question_manager",
              "function": "present_missing_questions",
              "params": {
                "format": "interactive"
              }
            }
          ],
          "next_step_conditions": [
            {
              "condition": "user_provided_answers",
              "next_step": "check_context"
            }
          ]
        },
        {
          "step_id": "execute_action",
          "name": "Execute Generation",
          "type": "execute_action",
          "instructions": "Generate content following command instructions. Apply specified rules and principles. For actions requiring decisions (e.g., consolidate/separate), document EACH decision in decision log.",
          "infrastructure_calls": [
            {
              "module": "template_engine",
              "function": "load_template",
              "params": {
                "template_file": "{command.actions.generate.templates.output_template}"
              }
            },
            {
              "module": "decision_log",
              "function": "start_logging",
              "params": {
                "log_file": "decision_log_{timestamp}.json"
              }
            }
          ],
          "next_step_conditions": [
            {
              "condition": "generation_complete",
              "next_step": "track_assumptions"
            }
          ]
        },
        {
          "step_id": "track_assumptions",
          "name": "Document Assumptions Made",
          "type": "track_assumptions",
          "instructions": "List EVERY assumption made during generation. For each assumption: category (data/logic/structure/priority/scope), description, impact, uncertainty level (High/Medium/Low). Use assumption templates from command definition as guidance.",
          "infrastructure_calls": [
            {
              "module": "assumption_tracker",
              "function": "capture_assumptions",
              "params": {
                "templates": "{command.actions.generate.assumptions}",
                "format": "structured"
              }
            }
          ],
          "next_step_conditions": [
            {
              "condition": "assumptions_documented",
              "next_step": "generate_questions"
            }
          ]
        },
        {
          "step_id": "generate_questions",
          "name": "Create Clarifying Questions",
          "type": "generate_questions",
          "instructions": "For each Medium/High uncertainty assumption, create clarifying question using question templates from command definition. For decisions logged, create questions about uncertain decisions. Questions should offer specific options, not open-ended.",
          "infrastructure_calls": [
            {
              "module": "question_manager",
              "function": "generate_clarifying_questions",
              "params": {
                "assumptions": "{assumption_tracker.get_high_uncertainty()}",
                "decisions": "{decision_log.get_uncertain_decisions()}",
                "templates": "{command.actions.generate.clarifying_questions}"
              }
            }
          ],
          "next_step_conditions": [
            {
              "condition": "questions_generated",
              "next_step": "wait_user_feedback"
            }
          ]
        },
        {
          "step_id": "wait_user_feedback",
          "name": "Present Results and Wait for User",
          "type": "wait_user_feedback",
          "instructions": "Present to user: (1) Generated content, (2) Assumptions made, (3) Decisions logged, (4) Clarifying questions. STOP and WAIT for user feedback. DO NOT recommend proceeding to next action yet. Only after user responds, acknowledge feedback and suggest next step.",
          "infrastructure_calls": [
            {
              "module": "template_engine",
              "function": "render_output",
              "params": {
                "template": "generate_results_template",
                "data": {
                  "content": "{generated_content}",
                  "assumptions": "{assumption_tracker.get_all()}",
                  "decisions": "{decision_log.get_all()}",
                  "questions": "{question_manager.get_clarifying_questions()}"
                }
              }
            }
          ],
          "next_step_conditions": [
            {
              "condition": "user_provided_feedback",
              "next_step": "end"
            }
          ]
        }
      ]
    }
  ]
}
```

---

### 4. Checklist Schema

**File:** `behaviors/common_command_runner/schemas/checklist_schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Validation Checklist",
  "type": "object",
  "required": ["checklist_id", "name", "items"],
  "properties": {
    "checklist_id": { "type": "string" },
    "name": { "type": "string" },
    "description": { "type": "string" },
    "items": {
      "type": "array",
      "items": { "$ref": "#/definitions/checklist_item" }
    }
  },
  "definitions": {
    "checklist_item": {
      "type": "object",
      "required": ["item_id", "check", "severity"],
      "properties": {
        "item_id": { "type": "string" },
        "check": { "type": "string" },
        "severity": {
          "type": "string",
          "enum": ["ERROR", "WARNING", "INFO"]
        },
        "principle_ref": {
          "type": "string",
          "description": "Reference to principle (e.g., '2.5')"
        },
        "how_to_check": { "type": "string" },
        "pass_criteria": { "type": "string" },
        "fail_criteria": { "type": "string" },
        "fix_suggestion": { "type": "string" }
      }
    }
  }
}
```

### Example Checklist: Story Consolidation

**File:** `behaviors/stories/definitions/checklists/consolidation-checklist.json`

```json
{
  "checklist_id": "consolidation-checklist",
  "name": "Story Consolidation Validation",
  "description": "Validates that stories are correctly consolidated or separated based on logic similarity",
  "items": [
    {
      "item_id": "same_logic_consolidated",
      "check": "Stories with SAME logic and DIFFERENT data should be CONSOLIDATED",
      "severity": "ERROR",
      "principle_ref": "2.5",
      "how_to_check": "For each group of similar stories, examine if they use identical UI/validation/calculation logic with only data values differing",
      "pass_criteria": "Similar stories are consolidated into single story when logic is identical",
      "fail_criteria": "Multiple separate stories exist that have same logic, just different data values",
      "fix_suggestion": "Consolidate stories with same logic into single story. Example: 'User selects [category] item from catalog' instead of separate stories for each category"
    },
    {
      "item_id": "different_logic_separated",
      "check": "Stories with DIFFERENT logic/formulas/rules should be SEPARATED",
      "severity": "ERROR",
      "principle_ref": "2.5",
      "how_to_check": "For consolidated stories, examine if they actually involve different formulas, validation rules, or business logic",
      "pass_criteria": "Stories with different logic are kept as separate stories",
      "fail_criteria": "Consolidated story combines stories with fundamentally different logic/formulas",
      "fix_suggestion": "Split consolidated story into separate stories based on logic differences. Example: Separate 'calculate defense from armor' from 'calculate defense from powers' if formulas differ"
    },
    {
      "item_id": "consolidation_reasoning_documented",
      "check": "Each consolidation decision should be documented with reasoning",
      "severity": "WARNING",
      "principle_ref": "2.5",
      "how_to_check": "Check if decision log contains entry for each consolidation with reasoning and uncertainty level",
      "pass_criteria": "Decision log has entry with reasoning for each consolidated group",
      "fail_criteria": "Consolidation decisions lack documented reasoning",
      "fix_suggestion": "Add decision log entries explaining why stories were consolidated or kept separate"
    },
    {
      "item_id": "uncertainty_acknowledged",
      "check": "High/Medium uncertainty consolidations should have clarifying questions",
      "severity": "WARNING",
      "principle_ref": "2.5",
      "how_to_check": "For consolidations marked Medium/High uncertainty in decision log, verify clarifying question was generated",
      "pass_criteria": "Each uncertain consolidation has associated clarifying question for user",
      "fail_criteria": "Uncertain consolidations exist without clarifying questions",
      "fix_suggestion": "Generate clarifying questions for uncertain consolidation decisions asking user to validate the decision"
    }
  ]
}
```

---

## Common Component Library

**CRITICAL PRINCIPLE:** Add new features/commands/rules/principles by **editing JSON files only**. Zero Python code changes required for standard additions. The common component library handles all JSON operations.

### Component Library Architecture

```
behaviors/
  common_command_runner/
    json_components/
      ├── __init__.py
      ├── json_loader.py          # Universal JSON reader with schema validation
      ├── json_writer.py          # Universal JSON writer with formatting
      ├── entity_builder.py       # Build features, commands, rules, behaviors
      ├── principle_builder.py    # Add/modify principles and examples
      ├── action_builder.py       # Add/remove actions from commands
      ├── heuristic_builder.py    # Add heuristics to principles
      ├── question_builder.py     # Create prompting/clarifying questions
      ├── assumption_builder.py   # Define assumption templates
      ├── decision_builder.py     # Define decision types
      ├── checklist_builder.py    # Create validation checklists
      ├── template_builder.py     # Build templates from JSON sections
      └── correction_builder.py   # Create correction patterns
```

### 1. Universal JSON Loader/Writer

**File:** `behaviors/common_command_runner/json_components/json_loader.py`

```python
from typing import Dict, Any, Optional, Type
from pathlib import Path
import json
from jsonschema import validate, ValidationError
from dataclasses import dataclass, asdict

@dataclass
class LoadResult:
    """Result of loading JSON with validation"""
    data: Dict[str, Any]
    file_path: Path
    schema_validated: bool
    validation_errors: list
    warnings: list


class JSONLoader:
    """Universal JSON loader with schema validation and caching"""
    
    def __init__(self, schema_dir: str = "schemas"):
        self.schema_dir = Path(__file__).parent.parent / schema_dir
        self.schemas = {}  # Cache loaded schemas
        self.loaded_files = {}  # Cache loaded JSON files
    
    def load(
        self, 
        file_path: str, 
        schema_name: Optional[str] = None,
        validate_schema: bool = True,
        use_cache: bool = True
    ) -> LoadResult:
        """Universal JSON loader
        
        Args:
            file_path: Path to JSON file (relative or absolute)
            schema_name: Schema to validate against (e.g., 'command_schema.json')
            validate_schema: Whether to validate against schema
            use_cache: Whether to use cached version if available
            
        Returns:
            LoadResult with data and validation info
        """
        file_path = Path(file_path)
        
        # Check cache
        if use_cache and str(file_path) in self.loaded_files:
            return self.loaded_files[str(file_path)]
        
        # Load JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate against schema if requested
        validation_errors = []
        schema_validated = False
        
        if validate_schema and schema_name:
            schema = self._load_schema(schema_name)
            try:
                validate(instance=data, schema=schema)
                schema_validated = True
            except ValidationError as e:
                validation_errors.append(str(e))
        
        # Create result
        result = LoadResult(
            data=data,
            file_path=file_path,
            schema_validated=schema_validated,
            validation_errors=validation_errors,
            warnings=[]
        )
        
        # Cache result
        if use_cache:
            self.loaded_files[str(file_path)] = result
        
        return result
    
    def _load_schema(self, schema_name: str) -> Dict:
        """Load and cache JSON schema"""
        if schema_name not in self.schemas:
            schema_path = self.schema_dir / schema_name
            with open(schema_path, 'r') as f:
                self.schemas[schema_name] = json.load(f)
        return self.schemas[schema_name]
    
    def find_and_load(
        self, 
        pattern: str, 
        search_dirs: list = None,
        schema_name: Optional[str] = None
    ) -> list:
        """Find all JSON files matching pattern and load them
        
        Args:
            pattern: Glob pattern (e.g., '*-command.json')
            search_dirs: Directories to search (default: all behaviors)
            schema_name: Schema to validate against
            
        Returns:
            List of LoadResult objects
        """
        if search_dirs is None:
            search_dirs = [Path('behaviors')]
        
        results = []
        for search_dir in search_dirs:
            for json_file in Path(search_dir).rglob(pattern):
                result = self.load(str(json_file), schema_name)
                results.append(result)
        
        return results
    
    def invalidate_cache(self, file_path: Optional[str] = None):
        """Invalidate cache for specific file or all files"""
        if file_path:
            self.loaded_files.pop(str(file_path), None)
        else:
            self.loaded_files.clear()


class JSONWriter:
    """Universal JSON writer with formatting and backup"""
    
    def __init__(self, backup_enabled: bool = True):
        self.backup_enabled = backup_enabled
    
    def write(
        self, 
        file_path: str, 
        data: Dict[str, Any],
        schema_name: Optional[str] = None,
        create_backup: bool = None,
        indent: int = 2
    ) -> bool:
        """Universal JSON writer
        
        Args:
            file_path: Where to write JSON
            data: Data to write
            schema_name: Schema to validate before writing
            create_backup: Whether to backup existing file
            indent: JSON indentation
            
        Returns:
            Success boolean
        """
        file_path = Path(file_path)
        create_backup = create_backup if create_backup is not None else self.backup_enabled
        
        # Validate before writing
        if schema_name:
            loader = JSONLoader()
            schema = loader._load_schema(schema_name)
            try:
                validate(instance=data, schema=schema)
            except ValidationError as e:
                print(f"Validation error: {e}")
                return False
        
        # Backup existing file
        if create_backup and file_path.exists():
            backup_path = file_path.with_suffix('.json.bak')
            file_path.rename(backup_path)
        
        # Write JSON with formatting
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        return True
    
    def update(
        self,
        file_path: str,
        updates: Dict[str, Any],
        merge_strategy: str = "deep"
    ) -> bool:
        """Update existing JSON file with new values
        
        Args:
            file_path: JSON file to update
            updates: Dictionary of updates to apply
            merge_strategy: 'shallow' (top-level only) or 'deep' (recursive)
            
        Returns:
            Success boolean
        """
        loader = JSONLoader()
        result = loader.load(file_path)
        
        if merge_strategy == "deep":
            merged = self._deep_merge(result.data, updates)
        else:
            merged = {**result.data, **updates}
        
        return self.write(file_path, merged)
    
    def _deep_merge(self, base: Dict, updates: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
```

### 2. Entity Builder (Create Features, Commands, Rules, Behaviors)

**File:** `behaviors/common_command_runner/json_components/entity_builder.py`

```python
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from datetime import datetime
from .json_writer import JSONWriter

class EntityBuilder:
    """Build complete entities (features, commands, rules, behaviors) from JSON
    
    Usage:
        builder = EntityBuilder()
        
        # Create new command
        command = builder.create_command(
            command_id="story-discovery",
            name="Story Discovery",
            description="...",
            entity_type="story"
        )
        
        # Add action to command
        builder.add_action_to_command(
            command,
            action_name="generate",
            workflow_template="interactive_generate_with_decisions"
        )
        
        # Save command
        builder.save_command(command, "behaviors/stories/definitions/story-discovery-command.json")
    """
    
    def __init__(self):
        self.writer = JSONWriter()
    
    def create_command(
        self,
        command_id: str,
        name: str,
        description: str,
        entity_type: str,
        version: str = "1.0.0"
    ) -> Dict[str, Any]:
        """Create new command structure"""
        return {
            "command_id": command_id,
            "name": name,
            "description": description,
            "entity_type": entity_type,
            "version": version,
            "actions": {},
            "cli": {
                "aliases": [],
                "arguments": []
            },
            "metadata": {
                "version": version,
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def create_rule(
        self,
        rule_id: str,
        name: str,
        description: str,
        version: str = "1.0.0"
    ) -> Dict[str, Any]:
        """Create new rule structure"""
        return {
            "rule_id": rule_id,
            "name": name,
            "description": description,
            "version": version,
            "principles": []
        }
    
    def create_feature(
        self,
        feature_id: str,
        name: str,
        description: str,
        commands: List[str] = None
    ) -> Dict[str, Any]:
        """Create new feature structure"""
        return {
            "feature_id": feature_id,
            "name": name,
            "description": description,
            "commands": commands or [],
            "rules": [],
            "dependencies": []
        }
    
    def create_behavior(
        self,
        behavior_id: str,
        name: str,
        description: str,
        features: List[str] = None
    ) -> Dict[str, Any]:
        """Create new behavior structure"""
        return {
            "behavior_id": behavior_id,
            "name": name,
            "description": description,
            "features": features or [],
            "deployed": False
        }
    
    def save_command(self, command: Dict, file_path: str) -> bool:
        """Save command to JSON file"""
        return self.writer.write(file_path, command, schema_name="command_schema.json")
    
    def save_rule(self, rule: Dict, file_path: str) -> bool:
        """Save rule to JSON file"""
        return self.writer.write(file_path, rule, schema_name="rule_schema.json")
    
    def save_feature(self, feature: Dict, file_path: str) -> bool:
        """Save feature to JSON file"""
        return self.writer.write(file_path, feature)
    
    def save_behavior(self, behavior: Dict, file_path: str) -> bool:
        """Save behavior to JSON file"""
        return self.writer.write(file_path, behavior)
```

### 3. Action Builder (Add/Remove Actions from Commands)

**File:** `behaviors/common_command_runner/json_components/action_builder.py`

```python
from typing import Dict, Any, List, Optional
from .json_loader import JSONLoader
from .json_writer import JSONWriter

class ActionBuilder:
    """Add/remove/modify actions in commands
    
    Usage:
        builder = ActionBuilder()
        
        # Add generate action
        builder.add_action(
            "story-discovery-command.json",
            action_name="generate",
            workflow_template="interactive_generate_with_decisions",
            prompting_questions=[...],
            instructions={...}
        )
        
        # Remove action
        builder.remove_action("story-discovery-command.json", "plan")
        
        # Update action
        builder.update_action(
            "story-discovery-command.json",
            "generate",
            prompting_questions=[...]  # Only update questions
        )
    """
    
    def __init__(self):
        self.loader = JSONLoader()
        self.writer = JSONWriter()
    
    def add_action(
        self,
        command_file: str,
        action_name: str,
        workflow_template: str,
        prompting_questions: List[Dict] = None,
        instructions: Dict = None,
        assumptions: List[Dict] = None,
        clarifying_questions: List[Dict] = None,
        checklists: List[Dict] = None,
        templates: Dict = None
    ) -> bool:
        """Add action to command"""
        result = self.loader.load(command_file, schema_name="command_schema.json")
        command = result.data
        
        action_def = {
            "workflow_template": workflow_template,
            "prompting_questions": prompting_questions or []
        }
        
        if instructions:
            action_def["instructions"] = instructions
        if assumptions:
            action_def["assumptions"] = assumptions
        if clarifying_questions:
            action_def["clarifying_questions"] = clarifying_questions
        if checklists:
            action_def["checklists"] = checklists
        if templates:
            action_def["templates"] = templates
        
        command["actions"][action_name] = action_def
        
        return self.writer.write(command_file, command, schema_name="command_schema.json")
    
    def remove_action(self, command_file: str, action_name: str) -> bool:
        """Remove action from command"""
        result = self.loader.load(command_file)
        command = result.data
        
        if action_name in command["actions"]:
            del command["actions"][action_name]
        
        return self.writer.write(command_file, command, schema_name="command_schema.json")
    
    def update_action(
        self,
        command_file: str,
        action_name: str,
        **updates
    ) -> bool:
        """Update specific fields in action"""
        result = self.loader.load(command_file)
        command = result.data
        
        if action_name not in command["actions"]:
            return False
        
        command["actions"][action_name].update(updates)
        
        return self.writer.write(command_file, command, schema_name="command_schema.json")
```

### 4. Principle Builder (Add Principles and Examples to Rules)

**File:** `behaviors/common_command_runner/json_components/principle_builder.py`

```python
from typing import Dict, Any, List, Optional
from .json_loader import JSONLoader
from .json_writer import JSONWriter

class PrincipleBuilder:
    """Add/modify principles and examples in rules
    
    Usage:
        builder = PrincipleBuilder()
        
        # Add new principle
        builder.add_principle(
            "stories-rule.json",
            principle_id="2.9",
            principle_name="Story Estimation",
            content="Stories should be sized consistently...",
            examples=[...]
        )
        
        # Add example to existing principle
        builder.add_example(
            "stories-rule.json",
            principle_id="2.5",
            do_text="Correct approach",
            do_code="...",
            dont_text="Wrong approach",
            dont_code="..."
        )
        
        # Update principle content
        builder.update_principle(
            "stories-rule.json",
            principle_id="2.5",
            content="Updated content..."
        )
    """
    
    def __init__(self):
        self.loader = JSONLoader()
        self.writer = JSONWriter()
    
    def add_principle(
        self,
        rule_file: str,
        principle_id: str,
        principle_name: str,
        content: str,
        examples: List[Dict] = None,
        heuristics: List[Dict] = None
    ) -> bool:
        """Add new principle to rule"""
        result = self.loader.load(rule_file, schema_name="rule_schema.json")
        rule = result.data
        
        principle = {
            "principle_id": principle_id,
            "principle_name": principle_name,
            "content": content,
            "examples": examples or [],
            "heuristics": heuristics or []
        }
        
        rule["principles"].append(principle)
        
        return self.writer.write(rule_file, rule, schema_name="rule_schema.json")
    
    def add_example(
        self,
        rule_file: str,
        principle_id: str,
        do_text: str = "",
        do_code: str = "",
        dont_text: str = "",
        dont_code: str = ""
    ) -> bool:
        """Add example to existing principle"""
        result = self.loader.load(rule_file)
        rule = result.data
        
        # Find principle
        principle = self._find_principle(rule, principle_id)
        if not principle:
            return False
        
        example = {}
        if do_text or do_code:
            example["do"] = {"text": do_text, "code": do_code}
        if dont_text or dont_code:
            example["dont"] = {"text": dont_text, "code": dont_code}
        
        principle["examples"].append(example)
        
        return self.writer.write(rule_file, rule, schema_name="rule_schema.json")
    
    def update_principle(
        self,
        rule_file: str,
        principle_id: str,
        **updates
    ) -> bool:
        """Update principle fields"""
        result = self.loader.load(rule_file)
        rule = result.data
        
        principle = self._find_principle(rule, principle_id)
        if not principle:
            return False
        
        principle.update(updates)
        
        return self.writer.write(rule_file, rule, schema_name="rule_schema.json")
    
    def _find_principle(self, rule: Dict, principle_id: str) -> Optional[Dict]:
        """Find principle by ID in rule"""
        for principle in rule["principles"]:
            if principle["principle_id"] == principle_id:
                return principle
        return None
```

### 5. Question Builder, Assumption Builder, Decision Builder

**File:** `behaviors/common_command_runner/json_components/question_builder.py`

```python
class QuestionBuilder:
    """Build prompting and clarifying questions
    
    Usage:
        builder = QuestionBuilder()
        
        # Add prompting question
        question = builder.create_prompting_question(
            id="increment_focus",
            text="Which market increment(s) are we focusing on?",
            required=True,
            context_paths=["open_files", "chat_history"],
            inference_hints=["Look for 'INCREMENT:' markers"]
        )
        
        # Add to command
        builder.add_to_command(
            "story-discovery-command.json",
            action="generate",
            question=question
        )
    """
    
    def create_prompting_question(
        self,
        id: str,
        text: str,
        required: bool = True,
        context_paths: List[str] = None,
        inference_hints: List[str] = None
    ) -> Dict:
        """Create prompting question structure"""
        return {
            "id": id,
            "text": text,
            "required": required,
            "context_paths": context_paths or [],
            "inference_hints": inference_hints or []
        }
    
    def create_clarifying_question_template(
        self,
        trigger: str,
        template: str,
        options: List[Dict] = None
    ) -> Dict:
        """Create clarifying question template"""
        return {
            "trigger": trigger,
            "template": template,
            "options": options or []
        }
```

**File:** `behaviors/common_command_runner/json_components/assumption_builder.py`

```python
class AssumptionBuilder:
    """Build assumption templates for commands
    
    Usage:
        builder = AssumptionBuilder()
        
        assumption_template = builder.create_assumption_template(
            category="logic",
            description="Determining if stories have same logic vs different logic",
            examples=["Stories with same UI but different data → CONSOLIDATE"],
            uncertainty_factors=["Cannot see actual code/validation rules"]
        )
    """
    
    def create_assumption_template(
        self,
        category: str,  # data, logic, structure, priority, scope
        description: str,
        examples: List[str] = None,
        uncertainty_factors: List[str] = None
    ) -> Dict:
        """Create assumption template"""
        return {
            "category": category,
            "description": description,
            "examples": examples or [],
            "uncertainty_factors": uncertainty_factors or []
        }
```

**File:** `behaviors/common_command_runner/json_components/decision_builder.py`

```python
class DecisionBuilder:
    """Build decision type definitions
    
    Usage:
        builder = DecisionBuilder()
        
        decision_type = builder.create_decision_type(
            type_id="consolidate_vs_separate",
            name="Consolidation Decision",
            description="Decide whether to consolidate or separate stories",
            criteria=[
                "Same logic + different data → CONSOLIDATE",
                "Different logic/formula → SEPARATE"
            ],
            uncertainty_levels={
                "high": "Cannot determine logic similarity from descriptions",
                "medium": "Descriptions suggest similarity but unclear",
                "low": "Logic difference is explicit"
            }
        )
    """
    
    def create_decision_type(
        self,
        type_id: str,
        name: str,
        description: str,
        criteria: List[str],
        uncertainty_levels: Dict[str, str] = None
    ) -> Dict:
        """Create decision type definition"""
        return {
            "type_id": type_id,
            "name": name,
            "description": description,
            "criteria": criteria,
            "uncertainty_levels": uncertainty_levels or {}
        }
```

### 6. Template Builder (Templates as JSON Sections)

**File:** `behaviors/common_command_runner/json_components/template_builder.py`

```python
class TemplateBuilder:
    """Build templates from JSON sections
    
    Templates are structured as JSON with sections as entries:
    {
      "template_id": "decision_log_template",
      "name": "Decision Log Output",
      "sections": [
        {
          "section_id": "header",
          "content": "=== DECISIONS MADE ===",
          "format": "text"
        },
        {
          "section_id": "decision_list",
          "content": "{{#decisions}}...",
          "format": "mustache",
          "repeatable": true
        }
      ]
    }
    
    Usage:
        builder = TemplateBuilder()
        
        template = builder.create_template(
            template_id="decision_log_template",
            name="Decision Log Output"
        )
        
        builder.add_section(
            template,
            section_id="header",
            content="=== DECISIONS MADE ==="
        )
        
        builder.add_section(
            template,
            section_id="decision_list",
            content="{{#decisions}}...",
            format="mustache",
            repeatable=True
        )
    """
    
    def create_template(
        self,
        template_id: str,
        name: str,
        description: str = ""
    ) -> Dict:
        """Create template structure"""
        return {
            "template_id": template_id,
            "name": name,
            "description": description,
            "sections": []
        }
    
    def add_section(
        self,
        template: Dict,
        section_id: str,
        content: str,
        format: str = "text",  # text, mustache, jinja2, markdown
        repeatable: bool = False,
        optional: bool = False
    ) -> Dict:
        """Add section to template"""
        section = {
            "section_id": section_id,
            "content": content,
            "format": format,
            "repeatable": repeatable,
            "optional": optional
        }
        
        template["sections"].append(section)
        return template
```

### 7. Component Usage Examples

**Example 1: Create New Command with Zero Python Code**

```bash
# 1. Create command JSON (or use builder script)
cat > behaviors/my-feature/definitions/my-command.json << 'EOF'
{
  "command_id": "my-command",
  "name": "My Command",
  "description": "Does something useful",
  "entity_type": "story",
  "actions": {
    "generate": {
      "workflow_template": "interactive_generate",
      "prompting_questions": [
        {
          "id": "target_file",
          "text": "What file should be processed?",
          "required": true,
          "context_paths": ["open_files"],
          "inference_hints": ["Use currently open file"]
        }
      ],
      "instructions": {
        "objective": "Generate something useful",
        "steps": [
          "1. Load file",
          "2. Process it",
          "3. Output result"
        ]
      }
    }
  }
}
EOF

# 2. Generate markdown from JSON
python -m json_components.markdown_generator behaviors/my-feature/definitions/

# 3. Command is now available in CLI automatically
python augmented_teams_cli.py my-command generate
```

**Example 2: Add Principle to Rule**

```python
# Python script or interactive session
from json_components.principle_builder import PrincipleBuilder

builder = PrincipleBuilder()

# Add new principle
builder.add_principle(
    "behaviors/stories/definitions/stories-rule.json",
    principle_id="2.10",
    principle_name="Story Dependencies",
    content="Stories should document dependencies on other stories or technical prerequisites.",
    examples=[
        {
            "do": {
                "text": "Document dependencies clearly",
                "code": "📝 User selects advanced power\n   Prerequisites: Basic power selection completed"
            },
            "dont": {
                "text": "Implicit dependencies",
                "code": "📝 User selects advanced power\n   (no mention of prerequisites)"
            }
        }
    ]
)

# Regenerate markdown
# (happens automatically via file watcher or manual trigger)
```

**Example 3: Add Action to Existing Command**

```python
from json_components.action_builder import ActionBuilder

builder = ActionBuilder()

# Add 'plan' action to story-discovery command
builder.add_action(
    "behaviors/stories/definitions/story-discovery-command.json",
    action_name="plan",
    workflow_template="simple_plan",
    prompting_questions=[
        {
            "id": "planning_scope",
            "text": "What aspect of discovery should be planned?",
            "required": True,
            "context_paths": ["chat_history"],
            "inference_hints": ["Check recent conversation for scope"]
        }
    ],
    instructions={
        "objective": "Create plan for story discovery execution",
        "steps": [
            "1. Identify features in focus increment",
            "2. Estimate story count per feature",
            "3. Identify consolidation opportunities",
            "4. Create execution plan"
        ]
    }
)

# CLI now has this action available automatically
# python augmented_teams_cli.py story-discovery plan
```

---

## Built-In Infrastructure Modules

### 1. Workflow Engine

**File:** `behaviors/common_command_runner/infrastructure/workflow_engine.py`

```python
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class WorkflowContext:
    """Context passed between workflow steps"""
    command_def: Dict[str, Any]
    action: str  # "generate", "validate", etc.
    user_inputs: Dict[str, Any]
    generated_content: Optional[Any] = None
    assumptions: List[Any] = None
    decisions: List[Any] = None
    violations: List[Any] = None
    
    def __post_init__(self):
        if self.assumptions is None:
            self.assumptions = []
        if self.decisions is None:
            self.decisions = []
        if self.violations is None:
            self.violations = []


class WorkflowEngine:
    """Executes workflow steps based on JSON workflow templates"""
    
    def __init__(self, workflow_templates_file: str = "workflow_templates.json"):
        self.templates = self._load_templates(workflow_templates_file)
        self.infrastructure = self._initialize_infrastructure()
    
    def _load_templates(self, file_path: str) -> Dict[str, Any]:
        """Load workflow templates from JSON"""
        templates_path = Path(__file__).parent.parent / "templates" / file_path
        with open(templates_path, 'r') as f:
            data = json.load(f)
        return {wf['workflow_id']: wf for wf in data['workflows']}
    
    def _initialize_infrastructure(self):
        """Initialize infrastructure modules"""
        from .assumption_tracker import AssumptionTracker
        from .question_manager import QuestionManager
        from .decision_log import DecisionLog
        from .checklist_engine import ChecklistEngine
        from .template_engine import TemplateEngine
        
        return {
            'assumption_tracker': AssumptionTracker(),
            'question_manager': QuestionManager(),
            'decision_log': DecisionLog(),
            'checklist_engine': ChecklistEngine(),
            'template_engine': TemplateEngine()
        }
    
    def execute_workflow(self, workflow_id: str, context: WorkflowContext) -> WorkflowContext:
        """Execute workflow steps in sequence"""
        workflow = self.templates[workflow_id]
        current_step_id = workflow['steps'][0]['step_id']
        
        while current_step_id != 'end':
            step = self._find_step(workflow, current_step_id)
            print(f"\n=== {step['name']} ===\n")
            
            # Execute step
            context = self._execute_step(step, context)
            
            # Determine next step
            current_step_id = self._evaluate_next_step(step, context)
        
        return context
    
    def _find_step(self, workflow: Dict, step_id: str) -> Dict:
        """Find step by ID in workflow"""
        for step in workflow['steps']:
            if step['step_id'] == step_id:
                return step
        raise ValueError(f"Step {step_id} not found in workflow")
    
    def _execute_step(self, step: Dict, context: WorkflowContext) -> WorkflowContext:
        """Execute single workflow step"""
        step_type = step['type']
        
        if step_type == 'check_context':
            return self._step_check_context(step, context)
        elif step_type == 'ask_user':
            return self._step_ask_user(step, context)
        elif step_type == 'execute_action':
            return self._step_execute_action(step, context)
        elif step_type == 'track_assumptions':
            return self._step_track_assumptions(step, context)
        elif step_type == 'generate_questions':
            return self._step_generate_questions(step, context)
        elif step_type == 'wait_user_feedback':
            return self._step_wait_user_feedback(step, context)
        elif step_type == 'run_heuristics':
            return self._step_run_heuristics(step, context)
        elif step_type == 'ai_validate':
            return self._step_ai_validate(step, context)
        else:
            raise ValueError(f"Unknown step type: {step_type}")
    
    def _step_check_context(self, step: Dict, context: WorkflowContext) -> WorkflowContext:
        """Check if prompting questions are answered"""
        print(step['instructions'])
        print()
        
        # Call question manager infrastructure
        questions = context.command_def['actions'][context.action]['prompting_questions']
        result = self.infrastructure['question_manager'].check_prompting_questions(
            questions, 
            context.user_inputs
        )
        
        context.user_inputs['_questions_answered'] = result['all_answered']
        context.user_inputs['_missing_questions'] = result['missing']
        
        return context
    
    def _step_ask_user(self, step: Dict, context: WorkflowContext) -> WorkflowContext:
        """Present missing questions to user"""
        print(step['instructions'])
        print()
        
        missing = context.user_inputs['_missing_questions']
        answers = self.infrastructure['question_manager'].present_missing_questions(
            missing, 
            interactive=True
        )
        
        # Update context with answers
        context.user_inputs.update(answers)
        
        return context
    
    def _step_execute_action(self, step: Dict, context: WorkflowContext) -> WorkflowContext:
        """Execute the main generation/validation action"""
        print(step['instructions'])
        print()
        
        # Load template if specified
        templates = context.command_def['actions'][context.action].get('templates', {})
        if 'output_template' in templates:
            template = self.infrastructure['template_engine'].load_template(
                templates['output_template']
            )
            context.user_inputs['_output_template'] = template
        
        # Start decision logging if needed
        self.infrastructure['decision_log'].start_logging()
        
        # This is where AI actually generates content
        # Instructions from command definition guide the generation
        print("AI INSTRUCTION: Generate content following command instructions")
        print(f"Objective: {context.command_def['actions'][context.action]['instructions']['objective']}")
        print()
        
        # Simulated generation result
        # In real implementation, AI would generate here based on instructions
        context.generated_content = {"status": "content_generated"}
        
        return context
    
    def _step_track_assumptions(self, step: Dict, context: WorkflowContext) -> WorkflowContext:
        """Document assumptions made during generation"""
        print(step['instructions'])
        print()
        
        assumption_templates = context.command_def['actions'][context.action].get('assumptions', [])
        
        # AI lists assumptions using templates as guidance
        print("AI INSTRUCTION: List assumptions you made during generation")
        print("Use these categories as guidance:")
        for template in assumption_templates:
            print(f"  - {template['category']}: {template['description']}")
        print()
        
        # Capture assumptions in infrastructure
        # In real implementation, AI would provide assumptions
        assumptions = self.infrastructure['assumption_tracker'].capture_assumptions(
            templates=assumption_templates,
            format="structured"
        )
        
        context.assumptions = assumptions
        
        return context
    
    def _step_generate_questions(self, step: Dict, context: WorkflowContext) -> WorkflowContext:
        """Generate clarifying questions based on assumptions"""
        print(step['instructions'])
        print()
        
        question_templates = context.command_def['actions'][context.action].get('clarifying_questions', [])
        
        # Generate questions for high-uncertainty assumptions
        questions = self.infrastructure['question_manager'].generate_clarifying_questions(
            assumptions=context.assumptions,
            decisions=context.decisions,
            templates=question_templates
        )
        
        context.user_inputs['_clarifying_questions'] = questions
        
        return context
    
    def _step_wait_user_feedback(self, step: Dict, context: WorkflowContext) -> WorkflowContext:
        """Present results and wait for user"""
        print(step['instructions'])
        print()
        
        # Render output using template
        output = self.infrastructure['template_engine'].render_output(
            template="generate_results_template",
            data={
                'content': context.generated_content,
                'assumptions': context.assumptions,
                'decisions': context.decisions,
                'questions': context.user_inputs.get('_clarifying_questions', [])
            }
        )
        
        print(output)
        print("\n🛑 WAITING FOR YOUR FEEDBACK\n")
        
        # In real implementation, this would wait for actual user input
        # For now, simulate user providing feedback
        feedback = input("Enter feedback (or press Enter to continue): ")
        context.user_inputs['_user_feedback'] = feedback
        
        return context
    
    def _step_run_heuristics(self, step: Dict, context: WorkflowContext) -> WorkflowContext:
        """Run automated heuristics"""
        print(step['instructions'])
        print()
        
        # Load checklists from command definition
        checklists = context.command_def['actions'][context.action].get('checklists', [])
        
        for checklist_ref in checklists:
            if checklist_ref['when'] == 'during':
                violations = self.infrastructure['checklist_engine'].run_checklist(
                    checklist_ref['checklist_file'],
                    context.generated_content
                )
                context.violations.extend(violations)
        
        print(f"Found {len(context.violations)} violations from automated checks")
        print()
        
        return context
    
    def _step_ai_validate(self, step: Dict, context: WorkflowContext) -> WorkflowContext:
        """AI validates against principles"""
        print(step['instructions'])
        print()
        
        # AI performs comprehensive validation
        print("AI INSTRUCTION: Validate content against ALL principles")
        print("Check not just syntax, but meaning, flow, and context")
        print()
        
        # In real implementation, AI would validate here
        
        return context
    
    def _evaluate_next_step(self, step: Dict, context: WorkflowContext) -> str:
        """Determine next step based on conditions"""
        conditions = step.get('next_step_conditions', [])
        
        for condition in conditions:
            if self._evaluate_condition(condition['condition'], context):
                return condition['next_step']
        
        # Default: move to next step in sequence
        return 'end'
    
    def _evaluate_condition(self, condition: str, context: WorkflowContext) -> bool:
        """Evaluate step transition condition"""
        if condition == 'all_questions_answered':
            return context.user_inputs.get('_questions_answered', False)
        elif condition == 'missing_required_answers':
            return not context.user_inputs.get('_questions_answered', False)
        elif condition == 'user_provided_answers':
            return '_missing_questions' not in context.user_inputs
        elif condition == 'generation_complete':
            return context.generated_content is not None
        elif condition == 'assumptions_documented':
            return len(context.assumptions) > 0
        elif condition == 'questions_generated':
            return '_clarifying_questions' in context.user_inputs
        elif condition == 'user_provided_feedback':
            return '_user_feedback' in context.user_inputs
        else:
            return True
```

### 2. Question Manager

**File:** `behaviors/common_command_runner/infrastructure/question_manager.py`

```python
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class Question:
    id: str
    text: str
    required: bool
    context_paths: List[str]
    inference_hints: List[str]
    answer: Any = None


class QuestionManager:
    """Manages prompting questions and clarifying questions"""
    
    def __init__(self):
        self.prompting_questions: List[Question] = []
        self.clarifying_questions: List[Dict] = []
    
    def check_prompting_questions(self, questions: List[Dict], user_inputs: Dict) -> Dict:
        """Check if prompting questions are answered in context"""
        self.prompting_questions = [
            Question(**q) for q in questions
        ]
        
        missing = []
        for q in self.prompting_questions:
            if q.required and q.id not in user_inputs:
                # Try to infer from context
                inferred = self._try_infer_answer(q, user_inputs)
                if inferred is None:
                    missing.append(q)
                else:
                    user_inputs[q.id] = inferred
        
        return {
            'all_answered': len(missing) == 0,
            'missing': [{'id': q.id, 'text': q.text} for q in missing]
        }
    
    def _try_infer_answer(self, question: Question, context: Dict) -> Any:
        """Attempt to infer answer from context using hints"""
        # In real implementation, would examine context sources
        # (open files, chat history, workspace) using inference hints
        # For now, just return None (cannot infer)
        return None
    
    def present_missing_questions(self, missing: List[Dict], interactive: bool = True) -> Dict:
        """Present missing questions to user and collect answers"""
        print("MISSING REQUIRED CONTEXT:\n")
        
        answers = {}
        for q in missing:
            print(f"❓ {q['text']}")
            if interactive:
                answer = input("  Answer: ")
                answers[q['id']] = answer
            print()
        
        return answers
    
    def generate_clarifying_questions(
        self, 
        assumptions: List[Dict], 
        decisions: List[Dict],
        templates: List[Dict]
    ) -> List[Dict]:
        """Generate clarifying questions based on assumptions and templates"""
        questions = []
        
        for assumption in assumptions:
            if assumption.get('uncertainty', 'LOW') in ['MEDIUM', 'HIGH']:
                # Find matching template
                template = self._find_template(assumption, templates)
                if template:
                    question = self._instantiate_template(template, assumption)
                    questions.append(question)
        
        self.clarifying_questions = questions
        return questions
    
    def _find_template(self, assumption: Dict, templates: List[Dict]) -> Dict:
        """Find appropriate question template for assumption"""
        # Match based on category, uncertainty, etc.
        for template in templates:
            # Simple matching - in real implementation, would be more sophisticated
            return template
        return None
    
    def _instantiate_template(self, template: Dict, data: Dict) -> Dict:
        """Fill in template with actual data"""
        return {
            'template': template['template'],
            'data': data,
            'options': template.get('options', [])
        }
```

### 3. Assumption Tracker

**File:** `behaviors/common_command_runner/infrastructure/assumption_tracker.py`

```python
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class UncertaintyLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class AssumptionCategory(Enum):
    DATA = "data"
    LOGIC = "logic"
    STRUCTURE = "structure"
    PRIORITY = "priority"
    SCOPE = "scope"

@dataclass
class Assumption:
    category: AssumptionCategory
    description: str
    impact: str
    uncertainty: UncertaintyLevel
    reasoning: str = ""
    could_be_wrong_if: str = ""


class AssumptionTracker:
    """Tracks assumptions made during command execution"""
    
    def __init__(self):
        self.assumptions: List[Assumption] = []
    
    def capture_assumptions(self, templates: List[Dict], format: str = "structured") -> List[Dict]:
        """Capture assumptions using templates as guidance"""
        print("DOCUMENT YOUR ASSUMPTIONS:\n")
        print("For each assumption you made during generation:")
        print("  - Category (data/logic/structure/priority/scope)")
        print("  - Description")
        print("  - Impact on output")
        print("  - Uncertainty level (LOW/MEDIUM/HIGH)")
        print("  - Why you might be wrong")
        print()
        
        print("Templates to guide you:")
        for template in templates:
            print(f"\n{template['category'].upper()}:")
            print(f"  Description: {template['description']}")
            print(f"  Examples:")
            for example in template.get('examples', []):
                print(f"    - {example}")
            print(f"  Uncertainty factors:")
            for factor in template.get('uncertainty_factors', []):
                print(f"    - {factor}")
        print()
        
        # In real implementation, AI would provide structured assumptions
        # For now, simulate
        self.assumptions = []
        
        return [
            {
                'category': a.category.value,
                'description': a.description,
                'impact': a.impact,
                'uncertainty': a.uncertainty.value
            }
            for a in self.assumptions
        ]
    
    def add_assumption(
        self, 
        category: AssumptionCategory, 
        description: str, 
        impact: str,
        uncertainty: UncertaintyLevel
    ):
        """Add single assumption"""
        assumption = Assumption(
            category=category,
            description=description,
            impact=impact,
            uncertainty=uncertainty
        )
        self.assumptions.append(assumption)
    
    def get_high_uncertainty(self) -> List[Assumption]:
        """Get assumptions with HIGH or MEDIUM uncertainty"""
        return [
            a for a in self.assumptions 
            if a.uncertainty in [UncertaintyLevel.HIGH, UncertaintyLevel.MEDIUM]
        ]
    
    def get_all(self) -> List[Dict]:
        """Get all assumptions as dictionaries"""
        return [
            {
                'category': a.category.value,
                'description': a.description,
                'impact': a.impact,
                'uncertainty': a.uncertainty.value,
                'reasoning': a.reasoning,
                'could_be_wrong_if': a.could_be_wrong_if
            }
            for a in self.assumptions
        ]
```

### 4. Decision Log

**File:** `behaviors/common_command_runner/infrastructure/decision_log.py`

```python
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class DecisionType(Enum):
    CONSOLIDATE = "consolidate"
    SEPARATE = "separate"
    STRUCTURE = "structure"
    PRIORITY = "priority"
    SCOPE = "scope"

class UncertaintyLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

@dataclass
class Decision:
    decision_type: DecisionType
    items_involved: List[str]
    decision_made: str
    reasoning: str
    uncertainty: UncertaintyLevel
    alternatives_considered: List[str]
    timestamp: datetime
    context: Dict[str, Any]


class DecisionLog:
    """Logs decisions made during command execution with reasoning"""
    
    def __init__(self):
        self.decisions: List[Decision] = []
        self.logging_active = False
    
    def start_logging(self):
        """Start decision logging"""
        self.logging_active = True
        self.decisions = []
    
    def log_decision(
        self,
        decision_type: DecisionType,
        items_involved: List[str],
        decision_made: str,
        reasoning: str,
        uncertainty: UncertaintyLevel,
        alternatives: List[str] = None,
        context: Dict = None
    ):
        """Log a single decision"""
        if not self.logging_active:
            return
        
        decision = Decision(
            decision_type=decision_type,
            items_involved=items_involved,
            decision_made=decision_made,
            reasoning=reasoning,
            uncertainty=uncertainty,
            alternatives_considered=alternatives or [],
            timestamp=datetime.now(),
            context=context or {}
        )
        self.decisions.append(decision)
    
    def get_uncertain_decisions(self) -> List[Decision]:
        """Get decisions with MEDIUM or HIGH uncertainty"""
        return [
            d for d in self.decisions
            if d.uncertainty in [UncertaintyLevel.MEDIUM, UncertaintyLevel.HIGH]
        ]
    
    def get_all(self) -> List[Dict]:
        """Get all decisions as dictionaries"""
        return [
            {
                'type': d.decision_type.value,
                'items': d.items_involved,
                'decision': d.decision_made,
                'reasoning': d.reasoning,
                'uncertainty': d.uncertainty.value,
                'alternatives': d.alternatives_considered,
                'timestamp': d.timestamp.isoformat()
            }
            for d in self.decisions
        ]
    
    def export_to_file(self, file_path: str):
        """Export decision log to JSON file"""
        import json
        with open(file_path, 'w') as f:
            json.dump(self.get_all(), f, indent=2)
```

### 5. Checklist Engine

**File:** `behaviors/common_command_runner/infrastructure/checklist_engine.py`

```python
from typing import List, Dict, Any
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class ChecklistViolation:
    item_id: str
    check: str
    severity: str
    principle_ref: str
    location: str
    fix_suggestion: str


class ChecklistEngine:
    """Runs validation checklists"""
    
    def __init__(self):
        self.checklists: Dict[str, Dict] = {}
    
    def load_checklist(self, checklist_file: str) -> Dict:
        """Load checklist from JSON file"""
        if checklist_file not in self.checklists:
            # Search in behavior definitions/checklists/
            checklist_path = Path(checklist_file)
            if not checklist_path.is_absolute():
                # Try to find in standard locations
                for behavior_dir in Path('behaviors').iterdir():
                    potential_path = behavior_dir / 'definitions' / 'checklists' / checklist_file
                    if potential_path.exists():
                        checklist_path = potential_path
                        break
            
            with open(checklist_path, 'r') as f:
                self.checklists[checklist_file] = json.load(f)
        
        return self.checklists[checklist_file]
    
    def run_checklist(self, checklist_file: str, content: Any) -> List[ChecklistViolation]:
        """Run checklist validation"""
        checklist = self.load_checklist(checklist_file)
        violations = []
        
        print(f"Running checklist: {checklist['name']}\n")
        
        for item in checklist['items']:
            print(f"Checking: {item['check']}")
            
            # In real implementation, would run actual validation
            # For now, simulate
            passed = self._check_item(item, content)
            
            if not passed:
                violation = ChecklistViolation(
                    item_id=item['item_id'],
                    check=item['check'],
                    severity=item['severity'],
                    principle_ref=item.get('principle_ref', ''),
                    location='line X',  # Would be actual location
                    fix_suggestion=item.get('fix_suggestion', '')
                )
                violations.append(violation)
                print(f"  ❌ FAILED ({item['severity']})")
            else:
                print(f"  ✅ PASSED")
            print()
        
        return violations
    
    def _check_item(self, item: Dict, content: Any) -> bool:
        """Check single checklist item"""
        # In real implementation, would perform actual validation
        # based on item['how_to_check'] and item['pass_criteria']
        return True  # Simulate pass for now
```

### 6. Template Engine

**File:** `behaviors/common_command_runner/infrastructure/template_engine.py`

```python
from typing import Dict, Any
import json
from pathlib import Path

class TemplateEngine:
    """Loads and processes templates"""
    
    def __init__(self):
        self.templates: Dict[str, Any] = {}
    
    def load_template(self, template_file: str) -> Dict:
        """Load template from JSON file"""
        if template_file not in self.templates:
            template_path = Path(template_file)
            if not template_path.is_absolute():
                # Search in standard locations
                template_path = Path('behaviors/common_command_runner/templates') / template_file
            
            with open(template_path, 'r') as f:
                self.templates[template_file] = json.load(f)
        
        return self.templates[template_file]
    
    def render_output(self, template: str, data: Dict[str, Any]) -> str:
        """Render output using template"""
        if template == "generate_results_template":
            return self._render_generate_results(data)
        elif template == "validation_results_template":
            return self._render_validation_results(data)
        else:
            return json.dumps(data, indent=2)
    
    def _render_generate_results(self, data: Dict) -> str:
        """Render generation results"""
        output = []
        output.append("=" * 60)
        output.append("GENERATED CONTENT")
        output.append("=" * 60)
        output.append("")
        output.append(json.dumps(data.get('content', {}), indent=2))
        output.append("")
        
        output.append("=" * 60)
        output.append("ASSUMPTIONS MADE")
        output.append("=" * 60)
        output.append("")
        for assumption in data.get('assumptions', []):
            output.append(f"• {assumption['category'].upper()}: {assumption['description']}")
            output.append(f"  Impact: {assumption['impact']}")
            output.append(f"  Uncertainty: {assumption['uncertainty']}")
            output.append("")
        
        output.append("=" * 60)
        output.append("DECISIONS LOGGED")
        output.append("=" * 60)
        output.append("")
        for decision in data.get('decisions', []):
            output.append(f"• {decision['type'].upper()}: {decision['decision']}")
            output.append(f"  Items: {', '.join(decision['items'])}")
            output.append(f"  Reasoning: {decision['reasoning']}")
            output.append(f"  Uncertainty: {decision['uncertainty']}")
            output.append("")
        
        output.append("=" * 60)
        output.append("CLARIFYING QUESTIONS FOR YOU")
        output.append("=" * 60)
        output.append("")
        for i, question in enumerate(data.get('questions', []), 1):
            output.append(f"{i}. {question.get('template', 'Question template')}")
            output.append("")
        
        return "\n".join(output)
    
    def _render_validation_results(self, data: Dict) -> str:
        """Render validation results"""
        output = []
        output.append("=" * 60)
        output.append("VALIDATION RESULTS")
        output.append("=" * 60)
        output.append("")
        
        violations = data.get('violations', [])
        if not violations:
            output.append("✅ NO VIOLATIONS FOUND")
        else:
            output.append(f"❌ FOUND {len(violations)} VIOLATIONS")
            output.append("")
            for v in violations:
                output.append(f"• [{v['severity']}] {v['check']}")
                output.append(f"  Location: {v['location']}")
                output.append(f"  Fix: {v['fix_suggestion']}")
                output.append("")
        
        return "\n".join(output)
```

---

## Improved CLI Architecture

### CLI Builder (Auto-generates CLI from JSON)

**File:** `behaviors/common_command_runner/infrastructure/cli_builder.py`

```python
import argparse
from typing import Dict, List, Any
import json
from pathlib import Path

class CLIBuilder:
    """Builds CLI interface from command JSON definitions"""
    
    def __init__(self, command_definitions_dir: str):
        self.commands = self._load_all_commands(command_definitions_dir)
        self.parser = self._build_parser()
    
    def _load_all_commands(self, definitions_dir: str) -> Dict[str, Dict]:
        """Load all command definitions from directory"""
        commands = {}
        definitions_path = Path(definitions_dir)
        
        for json_file in definitions_path.glob('**/*-command.json'):
            with open(json_file, 'r') as f:
                cmd_def = json.load(f)
                commands[cmd_def['command_id']] = cmd_def
                
                # Also register aliases
                for alias in cmd_def.get('cli', {}).get('aliases', []):
                    commands[alias] = cmd_def
        
        return commands
    
    def _build_parser(self) -> argparse.ArgumentParser:
        """Build argument parser from command definitions"""
        parser = argparse.ArgumentParser(
            description="Augmented Teams Code Agent",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Command to execute')
        
        for cmd_id, cmd_def in self.commands.items():
            if cmd_id in cmd_def.get('cli', {}).get('aliases', []):
                continue  # Skip aliases, handled by main command
            
            cmd_parser = subparsers.add_parser(
                cmd_id,
                help=cmd_def['description'],
                aliases=cmd_def.get('cli', {}).get('aliases', [])
            )
            
            # Add action subparsers
            action_subparsers = cmd_parser.add_subparsers(dest='action', help='Action to perform')
            
            for action_name in cmd_def['actions'].keys():
                action_parser = action_subparsers.add_parser(action_name)
                
                # Add arguments from command definition
                for arg in cmd_def.get('cli', {}).get('arguments', []):
                    self._add_argument(action_parser, arg)
        
        return parser
    
    def _add_argument(self, parser: argparse.ArgumentParser, arg_def: Dict):
        """Add argument to parser based on definition"""
        arg_names = [f"--{arg_def['name']}"]
        if 'aliases' in arg_def:
            arg_names.extend(arg_def['aliases'])
        
        arg_type = {
            'string': str,
            'int': int,
            'bool': bool,
            'path': Path,
            'list': list
        }.get(arg_def['type'], str)
        
        kwargs = {
            'type': arg_type,
            'help': arg_def.get('help', ''),
            'required': arg_def.get('required', False)
        }
        
        if 'default' in arg_def:
            kwargs['default'] = arg_def['default']
        
        if arg_type == bool:
            kwargs['action'] = 'store_true'
            del kwargs['type']
        
        parser.add_argument(*arg_names, **kwargs)
    
    def parse_args(self, args: List[str] = None) -> Dict[str, Any]:
        """Parse command-line arguments"""
        parsed = self.parser.parse_args(args)
        return vars(parsed)
    
    def execute(self, args: List[str] = None):
        """Parse arguments and execute command"""
        parsed = self.parse_args(args)
        
        command_id = parsed.get('command')
        action = parsed.get('action')
        
        if not command_id or not action:
            self.parser.print_help()
            return
        
        cmd_def = self.commands[command_id]
        
        # Execute workflow
        from .workflow_engine import WorkflowEngine, WorkflowContext
        
        workflow_id = cmd_def['actions'][action]['workflow_template']
        context = WorkflowContext(
            command_def=cmd_def,
            action=action,
            user_inputs=parsed
        )
        
        engine = WorkflowEngine()
        result_context = engine.execute_workflow(workflow_id, context)
        
        print("\n" + "=" * 60)
        print("WORKFLOW COMPLETE")
        print("=" * 60)
```

### Example CLI Usage

With the JSON-first architecture, the CLI becomes much simpler and more intuitive:

```bash
# Old way (complex, requires memorizing command structure)
python behaviors/stories/stories_runner.py story-discovery generate /path/to/story-map.md

# New way (natural, entity-action pattern)
python augmented_teams_cli.py story-discovery generate

# With interactive mode (prompts for missing info)
python augmented_teams_cli.py discovery generate --interactive

# With explicit parameters
python augmented_teams_cli.py discovery generate --story_map="docs/stories/map/mm3e-story-map.md" --increment=NOW

# Help is context-aware
python augmented_teams_cli.py story-discovery --help
# Shows: prompting questions, available actions, expected inputs

python augmented_teams_cli.py story-discovery generate --help
# Shows: what will be generated, what questions need answers, assumptions that will be made

# Short aliases work
python augmented_teams_cli.py disc gen  # Same as story-discovery generate
```

---

## Markdown Generation from JSON → Template-Compliant Files

**CRITICAL:** The markdown generator creates files that **follow the exact template structure** from PROMPT_BASED_COMMAND_REFACTORING_PLAN.md. JSON is the source, markdown follows the template standards.

### Generated Files Follow Original Plan Templates

The markdown generator produces files matching these templates from the original plan:

**From JSON → Generated Markdown:**
- `story-discovery-command.json` → `story-discovery-prompts.md` (follows command_prompt_template.md structure)
- `stories-rule.json` → `stories-rule.mdc` (follows base_rule_template.mdc structure)
- Command definitions → Command plan files (follows command_plan_template.md)

### Markdown Generator Implementation

**File:** `behaviors/common_command_runner/markdown_generator.py`

```python
from typing import Dict, Any, List
import json
from pathlib import Path

class MarkdownGenerator:
    """Generates markdown documentation from JSON definitions
    
    IMPORTANT: Generated markdown follows template structures from 
    PROMPT_BASED_COMMAND_REFACTORING_PLAN.md:
    - Command prompts follow command_prompt_template.md
    - Rules follow base_rule_template.mdc
    - Commands follow command_template.md
    """
    
    def generate_command_prompts_md(self, command_def: Dict) -> str:
        """Generate command prompts markdown following command_prompt_template.md structure
        
        Template structure from PROMPT_BASED_COMMAND_REFACTORING_PLAN.md:
        - # {Command Name} Prompts
        - ## Prompting Questions
        - ## Generate Action Prompts
        -   ### Specific Instructions
        -   ### Principles to Apply
        -   ### Where AI Will Make Assumptions
        -   ### Clarifying Questions You Should Ask
        - ## Validate Action Prompts
        -   ### Specific Validation Checks
        -   ### Where You'll Make Validation Assumptions
        -   ### Clarifying Questions for Fixes
        """
        lines = []
        
        # Header (follows template)
        lines.append(f"# {command_def['name']} Prompts")
        lines.append("")
        lines.append(f"**Generated from:** `{command_def['command_id']}-command.json`")
        lines.append(f"**DO NOT EDIT THIS FILE DIRECTLY** - Edit the JSON source instead")
        lines.append("")
        
        # For each action (generate, validate, etc.)
        for action_name, action_def in command_def['actions'].items():
            lines.append(f"## {action_name.title()} Action Prompts")
            lines.append("")
            
            # === PROMPTING QUESTIONS (follows template section) ===
            lines.append("### Prompting Questions")
            lines.append("")
            lines.append("**CRITICAL:** Check if these are answered in context before proceeding. If not, ASK USER:")
            lines.append("")
            for q in action_def['prompting_questions']:
                lines.append(f"- {q['text']}")
                if q.get('inference_hints'):
                    lines.append(f"  - *Inference hints:* {', '.join(q['inference_hints'])}")
            lines.append("")
            lines.append("---")
            lines.append("")
            
            # === SPECIFIC INSTRUCTIONS (follows template section) ===
            if 'instructions' in action_def:
                lines.append("### Specific Instructions")
                lines.append("")
                lines.append(action_def['instructions']['objective'])
                lines.append("")
                lines.append("**Steps:**")
                for step in action_def['instructions']['steps']:
                    lines.append(f"{step}")
                lines.append("")
            
            # === PRINCIPLES TO APPLY (follows template section) ===
            if 'instructions' in action_def and 'rules_to_apply' in action_def['instructions']:
                lines.append("### Principles to Apply")
                lines.append("")
                for rule_ref in action_def['instructions']['rules_to_apply']:
                    lines.append(f"Apply these principles from {rule_ref['rule_file']}:")
                    for principle_id in rule_ref['principle_ids']:
                        lines.append(f"- **§{principle_id}**")
                lines.append("")
            
            # === WHERE AI WILL MAKE ASSUMPTIONS (follows template section) ===
            if 'assumptions' in action_def:
                lines.append("### Where AI Will Make Assumptions (Document These)")
                lines.append("")
                for assumption in action_def['assumptions']:
                    lines.append(f"**{assumption['category'].upper()} assumptions:**")
                    lines.append("")
                    lines.append(assumption['description'])
                    lines.append("")
                    lines.append("Examples of assumptions you'll make:")
                    for example in assumption.get('examples', []):
                        lines.append(f"- {example}")
                    lines.append("")
                    lines.append("Why these are uncertain:")
                    for factor in assumption.get('uncertainty_factors', []):
                        lines.append(f"- {factor}")
                    lines.append("")
            
            # === CLARIFYING QUESTIONS YOU SHOULD ASK (follows template section) ===
            if 'clarifying_questions' in action_def:
                lines.append("### Clarifying Questions You Should Ask")
                lines.append("")
                lines.append("For each decision/assumption with Medium/High uncertainty:")
                lines.append("")
                for q_template in action_def['clarifying_questions']:
                    lines.append(f"**When:** {q_template['trigger']}")
                    lines.append("")
                    lines.append("**Question format:**")
                    lines.append("```")
                    lines.append(q_template['template'])
                    lines.append("```")
                    lines.append("")
            
            # === CHECKLISTS (additional section) ===
            if 'checklists' in action_def:
                lines.append("### Checklists to Run")
                lines.append("")
                for checklist_ref in action_def['checklists']:
                    lines.append(f"- **{checklist_ref['when'].upper()}:** `{checklist_ref['checklist_file']}`")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_rule_md(self, rule_def: Dict) -> str:
        """Generate rule markdown (MDC format) from JSON"""
        lines = []
        
        # Header
        lines.append(f"# {rule_def['name']}")
        lines.append("")
        lines.append(rule_def['description'])
        lines.append("")
        
        # Principles
        for principle in rule_def['principles']:
            lines.append(f"## {principle['principle_id']}. {principle['principle_name']}")
            lines.append("")
            lines.append(principle['content'])
            lines.append("")
            
            # Examples
            for example in principle.get('examples', []):
                if 'do' in example:
                    lines.append("**[DO]:**")
                    if 'text' in example['do']:
                        lines.append(example['do']['text'])
                    lines.append("```")
                    lines.append(example['do']['code'])
                    lines.append("```")
                    lines.append("")
                
                if 'dont' in example:
                    lines.append("**[DON'T]:**")
                    if 'text' in example['dont']:
                        lines.append(example['dont']['text'])
                    lines.append("```")
                    lines.append(example['dont']['code'])
                    lines.append("```")
                    lines.append("")
        
        return "\n".join(lines)
    
    def generate_all_markdown(self, definitions_dir: str, output_dir: str):
        """Generate markdown for all definitions in directory"""
        definitions_path = Path(definitions_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate command markdown
        for json_file in definitions_path.glob('**/*-command.json'):
            with open(json_file, 'r') as f:
                cmd_def = json.load(f)
            
            md_content = self.generate_command_md(cmd_def)
            md_file = output_path / f"{cmd_def['command_id']}-cmd.md"
            
            with open(md_file, 'w') as f:
                f.write(md_content)
            
            print(f"Generated: {md_file}")
        
        # Generate rule markdown
        for json_file in definitions_path.glob('**/*-rule.json'):
            with open(json_file, 'r') as f:
                rule_def = json.load(f)
            
            md_content = self.generate_rule_md(rule_def)
            md_file = output_path / f"{rule_def['rule_id']}.mdc"
            
            with open(md_file, 'w') as f:
                f.write(md_content)
            
            print(f"Generated: {md_file}")
```

---

## Migration Path

### Phase 1: Infrastructure (Week 1-2)

1. **Create infrastructure modules**
   - WorkflowEngine
   - AssumptionTracker
   - QuestionManager
   - DecisionLog
   - ChecklistEngine
   - TemplateEngine
   - CLIBuilder

2. **Create JSON schemas**
   - command_schema.json
   - rule_schema.json
   - workflow_schema.json
   - checklist_schema.json

3. **Create base workflow templates**
   - interactive_generate_with_decisions
   - interactive_validate_with_heuristics
   - simple_generate
   - simple_validate

### Phase 2: Convert Stories Commands (Week 3-4)

1. **Convert story-discovery to JSON**
   - Create story-discovery-command.json
   - Create consolidation-checklist.json
   - Create story-format-checklist.json
   - Test with WorkflowEngine

2. **Convert story-shape to JSON**
   - Create story-shape-command.json
   - Test workflow execution

3. **Convert stories-rule to JSON**
   - Create stories-rule.json with all principles
   - Generate markdown from JSON
   - Verify markdown matches current .mdc

4. **Update stories_runner.py**
   - Use CLIBuilder instead of hardcoded CLI
   - Load command definitions from JSON
   - Execute workflows via WorkflowEngine

### Phase 3: Convert Other Behaviors (Week 5-6)

1. **Convert DDD commands**
   - ddd-structure-command.json
   - ddd-interaction-command.json
   - ddd-rule.json

2. **Convert BDD commands**
   - Keep complex workflow logic in Python
   - Extract prompt content to JSON
   - bdd-workflow-command.json
   - bdd-rule.json

3. **Convert Code Agent commands**
   - code-agent-command-command.json
   - code-agent-feature-command.json
   - code-agent-rule.json

### Phase 4: Enhanced CLI (Week 7)

1. **Unified CLI entry point**
   - Create augmented_teams_cli.py
   - Uses CLIBuilder to load all commands
   - Single entry point for all behaviors

2. **Interactive mode**
   - Prompt for missing parameters
   - Context-aware help
   - Command completion

3. **Documentation generation**
   - Auto-generate CLI help from JSON
   - Generate markdown docs from JSON
   - Keep markdown synced with JSON

### Phase 5: Validation & Refinement (Week 8)

1. **Meta-validation**
   - Code-agent validates JSON schema compliance
   - Validates workflow completeness
   - Checks for missing infrastructure calls

2. **Testing**
   - Integration tests for each command
   - Workflow execution tests
   - CLI interaction tests

3. **Documentation**
   - Architecture guide
   - JSON schema documentation
   - Migration guide for future commands

---

## Benefits

### For AI Agents

1. **Easier to Parse**: JSON is structured, no ambiguous markdown interpretation
2. **Direct Access**: Infrastructure modules called directly with typed parameters
3. **Clear Workflow**: Step-by-step workflow execution with explicit transitions
4. **Built-in Patterns**: Assumptions, questions, decisions are first-class concepts
5. **Less Guessing**: Templates and schemas guide what to do at each step

### For Humans

1. **Generated Markdown**: Human-readable docs auto-generated from JSON
2. **Single Source of Truth**: JSON is authoritative, markdown is for reading
3. **Easier Maintenance**: Change JSON, regenerate markdown automatically
4. **Better CLI**: Natural command structure, context-aware help
5. **Interactive Mode**: CLI prompts for missing info instead of failing

### For System

1. **Consistency**: All commands follow same patterns via infrastructure
2. **Reusability**: Workflow templates reused across commands
3. **Extensibility**: New commands just need JSON definition
4. **Validation**: Schema validation ensures correctness
5. **Tracking**: Assumptions, decisions, questions logged automatically

---

## Comparison: Old vs New

### Old Approach (Markdown-First)

```
Command defined in: story-discovery-generate-cmd.md (prose)
↓
Hardcoded in: StoryDiscoveryCommand.generate() (Python strings)
↓
AI reads: Long instruction string
↓
AI executes: No structure, freestyle execution
↓
Output: Generated content (assumptions not tracked)
```

**Problems:**
- Instructions in prose (AI interprets differently)
- Workflow implicit (AI might skip steps)
- No assumption tracking
- No decision logging
- Inconsistent across commands

### New Approach (JSON-First)

```
Command defined in: story-discovery-command.json (structured)
↓
Loaded by: WorkflowEngine (reads JSON, loads workflow template)
↓
Executed via: Workflow steps (explicit, sequential)
  Step 1: Check prompting questions → QuestionManager
  Step 2: Generate content → Use instructions from JSON
  Step 3: Track assumptions → AssumptionTracker
  Step 4: Log decisions → DecisionLog
  Step 5: Generate questions → QuestionManager
  Step 6: Wait for user → TemplateEngine renders output
↓
Output: Content + Assumptions + Decisions + Questions
↓
Markdown: Auto-generated for human consumption
```

**Benefits:**
- Instructions structured (no ambiguity)
- Workflow explicit (can't skip steps)
- Assumptions tracked automatically
- Decisions logged automatically
- Consistent across all commands

---

## Next Steps

1. **Review this plan** with team
2. **Create prototype** with story-discovery command
3. **Test workflow execution** end-to-end
4. **Refine infrastructure** based on prototype learnings
5. **Convert remaining commands** systematically
6. **Document architecture** for future commands

---

## Open Questions

1. **JSON complexity**: Will JSON definitions become too verbose? (Use template inheritance?)
2. **Markdown sync**: How to keep generated markdown in sync? (Pre-commit hook?)
3. **Custom logic**: Where to draw line between JSON-driven and custom Python code?
4. **Performance**: Does JSON parsing + workflow execution add significant overhead?
5. **Backward compatibility**: How to support existing commands during migration?

---

## Conclusion

**JSON-first architecture** with **built-in workflow infrastructure** provides:
- **Structure** (no ambiguity in commands)
- **Consistency** (all commands follow same patterns)
- **Traceability** (assumptions, decisions logged automatically)
- **Extensibility** (new commands via JSON, minimal Python)
- **Usability** (better CLI, interactive mode, auto-generated docs)

This is the foundation for scalable, maintainable code agent behaviors.

