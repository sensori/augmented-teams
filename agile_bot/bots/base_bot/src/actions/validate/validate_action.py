from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import traceback
import json
from agile_bot.bots.base_bot.src.utils import read_json_file
from agile_bot.bots.base_bot.src.actions.action import Action
from agile_bot.bots.base_bot.src.scanners.violation import Violation
from agile_bot.bots.base_bot.src.actions.validate.rule import Rule
from agile_bot.bots.base_bot.src.actions.validate.rules import Rules
from agile_bot.bots.base_bot.src.actions.validate.scanners.scanner_loader import ScannerLoader
from agile_bot.bots.base_bot.src.actions.validate.story_graph import StoryGraph
from agile_bot.bots.base_bot.src.actions.validate.validation_scope import ValidationScope
from agile_bot.bots.base_bot.src.actions.validate.validation_report_writer import ValidationReportWriter

logger = logging.getLogger(__name__)


class ScannerExecutionError(Exception):
    def __init__(self, rule_file: str, scanner_path: str, original_error: Exception):
        self.rule_file = rule_file
        self.scanner_path = scanner_path
        self.original_error = original_error
        message = (
            f"Scanner execution failed for rule '{rule_file}' "
            f"(scanner: {scanner_path}): {original_error}"
        )
        super().__init__(message)


class ValidateRulesAction(Action):
    def __init__(self, base_action_config=None, behavior=None, activity_tracker=None,
                 bot_name: str = None, action_name: str = 'validate'):
        super().__init__(base_action_config=base_action_config, behavior=behavior,
                        activity_tracker=activity_tracker)
        if self.behavior:
            self._rules = Rules(behavior=self.behavior, bot_paths=self.behavior.bot_paths)
        else:
            self._rules = None
    
    @property
    def rules(self) -> Optional[Rules]:
        if self._rules is None and self.behavior:
            self._rules = Rules(behavior=self.behavior, bot_paths=self.behavior.bot_paths)
        return self._rules
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Story graph is required for validation
            # Tests that don't need knowledge graph validation should create an empty story graph
            story_graph = StoryGraph(self.behavior.bot_paths, self.working_dir)
            
            validation_scope = ValidationScope(parameters or {}, self.behavior.bot_paths)
            
            scope_config = validation_scope.scope
            # Only set scope if parameters actually provide scope configuration
            # Scope config keys that indicate actual scope: story_names, increment_priorities, epic_names, all
            # If parameters don't provide scope (empty dict or only path params), preserve file scope
            scope_keys = {'story_names', 'increment_priorities', 'epic_names', 'all'}
            has_scope_in_params = any(key in scope_config for key in scope_keys)
            
            if has_scope_in_params:
                # Parameters provide scope - use it (overwrites file scope)
                story_graph['_validation_scope'] = scope_config
            elif '_validation_scope' in story_graph.content:
                # Parameters don't provide scope, but file has scope - preserve it
                # This handles cases where scope is added to file before action execution
                pass  # Scope already in story_graph.content, no need to overwrite
            # If neither params nor file have scope, that's fine (validate all)
            
            files = validation_scope.all_files()
            
            # Pass story_graph.content directly - it should already have _validation_scope set above
            # The story_graph object uses __setitem__ which modifies _content directly
            result = self.injectValidationInstructions(story_graph.content, files=files)
            
            instructions = result.get('instructions', {})
            validation_rules = instructions.get('validation_rules', [])
            
            writer = ValidationReportWriter(self.behavior.name, self.behavior.bot_paths)
            writer.write(instructions, validation_rules, files)
            
            return result
        except FileNotFoundError as e:
            # Re-raise FileNotFoundError for story graph as-is (tests expect this)
            if "story graph" in str(e).lower() or "story-graph.json" in str(e):
                raise
            # Otherwise wrap in RuntimeError
            logger.error("=== ERROR in validate_rules action ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {e}")
            logger.error(f"Parameters: {parameters}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            error_msg = (
                f"Error in validate_rules action: {e}\n"
                f"Parameters: {parameters}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            raise RuntimeError(error_msg) from e
        except (json.JSONDecodeError, ValueError) as e:
            # Re-raise JSON/Value errors as-is (tests expect these for invalid JSON)
            raise
        except Exception as e:
            logger.error("=== ERROR in validate_rules action ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {e}")
            logger.error(f"Parameters: {parameters}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            error_msg = (
                f"Error in validate_rules action: {e}\n"
                f"Parameters: {parameters}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            raise RuntimeError(error_msg) from e
    
    def inject_common_bot_rules(self) -> Dict[str, Any]:
        base_bot_rules_dir = self.bot_dir.parent / 'base_bot' / 'rules'
        
        common_rules = []
        if base_bot_rules_dir.exists() and base_bot_rules_dir.is_dir():
            for rule_file in base_bot_rules_dir.glob('*.json'):
                rule_data = read_json_file(rule_file)
                common_rules.append({
                    'rule_file': f'agile_bot/bots/base_bot/rules/{rule_file.name}',
                    'rule_content': rule_data
                })
        
        return {
            'validation_rules': common_rules
        }
    
    def inject_behavior_specific_and_bot_rules(self) -> Dict[str, Any]:
        """Inject both behavior-specific rules and bot-level rules.
        
        Returns:
            Dict with 'validation_rules' key containing list of rule dicts
        """
        all_rules = []
        
        # Load bot-level rules
        if self.behavior and self.behavior.bot_paths:
            bot_dir = self.behavior.bot_paths.bot_directory
            if bot_dir:
                bot_rules_dir = bot_dir / 'rules'
                if bot_rules_dir.exists() and bot_rules_dir.is_dir():
                    for rule_file in bot_rules_dir.glob('*.json'):
                        rule_data = read_json_file(rule_file)
                        all_rules.append({
                            'rule_file': f'{bot_dir.name}/rules/{rule_file.name}',
                            'rule_content': rule_data
                        })
                
                # Load behavior-specific rules
                if self.behavior.name:
                    behavior_rules_dir = bot_dir / 'behaviors' / self.behavior.name / 'rules'
                    if behavior_rules_dir.exists() and behavior_rules_dir.is_dir():
                        for rule_file in behavior_rules_dir.glob('*.json'):
                            rule_data = read_json_file(rule_file)
                            all_rules.append({
                                'rule_file': f'{bot_dir.name}/behaviors/{self.behavior.name}/rules/{rule_file.name}',
                                'rule_content': rule_data
                            })
        
        # Also include common bot rules
        common_rules_data = self.inject_common_bot_rules()
        all_rules.extend(common_rules_data.get('validation_rules', []))
        
        return {
            'validation_rules': all_rules
        }
    
    def get_action_instructions(self) -> List[str]:
        action_instructions = []
        base_actions_path = self.base_actions_dir
        
        config_path = base_actions_path / 'validate' / 'action_config.json'
        
        if config_path.exists():
            config = read_json_file(config_path)
            action_instructions = config.get('instructions', [])
        
        return action_instructions
    
    def inject_next_action_instructions(self):
        return ""  # Empty string for terminal action
    
    def injectValidationInstructions(self, knowledge_graph: Dict[str, Any], files: Optional[Dict[str, List[Path]]] = None) -> Dict[str, Any]:
        action_instructions = self.get_action_instructions()
        
        # Get report path and create hyperlink from ValidationReportWriter
        writer = ValidationReportWriter(self.behavior.name, self.behavior.bot_paths)
        report_path = writer.get_report_path()
        report_link = writer.get_report_hyperlink()
        
        if not self.rules:
            # Add report link to instructions even if no rules
            action_instructions.append(f"\nValidation report: {report_link}")
            return {
                'instructions': {
                    'action': 'validate',
                    'behavior': self.behavior.name,
                    'base_instructions': action_instructions,
                    'validation_rules': [],
                    'content_to_validate': None,
                    'report_path': str(report_path),
                    'report_link': report_link
                }
            }
        
        files = files or {}
        processed_rules = self.rules.validate(knowledge_graph, files)
        
        violation_summary = self.rules.violation_summary
        if violation_summary:
            edit_instructions = [
                "Based on code scanner diagnostics, edit the knowledge graph to fix violations:",
                *violation_summary,
                "Review each violation and update the knowledge graph accordingly."
            ]
            action_instructions.extend(edit_instructions)
        
        # Add report link to instructions
        action_instructions.append(f"\nValidation report: {report_link}")
        
        instructions = {
            'action': 'validate_rules',
            'behavior': self.behavior.name,
            'base_instructions': action_instructions,
            'validation_rules': processed_rules,
            'content_to_validate': None,
            'report_path': str(report_path),
            'report_link': report_link
        }
        
        return {'instructions': instructions}
    
    def finalize_and_transition(self, next_action: str = None):
        """Finalize action and transition to next action.
        
        Args:
            next_action: Next action name (None for terminal action)
        
        Returns:
            ActionResult-like object with next_action property
        """
        class ActionResult:
            def __init__(self, next_action):
                self.next_action = next_action
        
        return ActionResult(next_action=next_action)

