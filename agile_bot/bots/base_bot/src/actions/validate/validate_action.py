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
    def __init__(self, behavior=None, action_config=None):
        super().__init__(behavior=behavior, action_config=action_config)
        self._rules = Rules(behavior=self.behavior, bot_paths=self.behavior.bot_paths)
    
    @property
    def action_name(self) -> str:
        """Action name is always 'validate' for ValidateRulesAction."""
        return 'validate'
    
    @action_name.setter
    def action_name(self, value: str):
        raise AttributeError("action_name is read-only for ValidateRulesAction")
    
    @property
    def rules(self) -> Rules:
        return self._rules
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            story_graph = StoryGraph(self.behavior.bot_paths, self.working_dir)
            validation_scope = ValidationScope(parameters or {}, self.behavior.bot_paths)
            scope_config = validation_scope.scope
            scope_keys = {'story_names', 'increment_priorities', 'epic_names', 'all'}
            has_scope_in_params = any(key in scope_config for key in scope_keys)
            
            if has_scope_in_params:
                story_graph['_validation_scope'] = scope_config
            
            files = validation_scope.all_files()
            result = self.injectValidationInstructions(story_graph.content, files=files)
            instructions = result.get('instructions', {})
            validation_rules = instructions.get('validation_rules', [])
            writer = ValidationReportWriter(self.behavior.name, self.behavior.bot_paths)
            writer.write(instructions, validation_rules, files)
            return result
        except FileNotFoundError as e:
            if "story graph" in str(e).lower() or "story-graph.json" in str(e):
                raise
            logger.error("=== ERROR in validate action ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {e}")
            logger.error(f"Parameters: {parameters}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            error_msg = (
                f"Error in validate action: {e}\n"
                f"Parameters: {parameters}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            raise RuntimeError(error_msg) from e
        except (json.JSONDecodeError, ValueError) as e:
            raise
        except Exception as e:
            logger.error("=== ERROR in validate action ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {e}")
            logger.error(f"Parameters: {parameters}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            error_msg = (
                f"Error in validate action: {e}\n"
                f"Parameters: {parameters}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            raise RuntimeError(error_msg) from e
    
    def inject_common_bot_rules(self) -> Dict[str, Any]:
        base_bot_rules_dir = self.bot_dir.parent / 'base_bot' / 'rules'
        common_rules = []
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
        all_rules = []
        bot_dir = self.behavior.bot_paths.bot_directory
        bot_rules_dir = bot_dir / 'rules'
        for rule_file in bot_rules_dir.glob('*.json'):
            rule_data = read_json_file(rule_file)
            all_rules.append({
                'rule_file': f'{bot_dir.name}/rules/{rule_file.name}',
                'rule_content': rule_data
            })
        behavior_rules_dir = bot_dir / 'behaviors' / self.behavior.name / 'rules'
        for rule_file in behavior_rules_dir.glob('*.json'):
            rule_data = read_json_file(rule_file)
            all_rules.append({
                'rule_file': f'{bot_dir.name}/behaviors/{self.behavior.name}/rules/{rule_file.name}',
                'rule_content': rule_data
            })
        common_rules_data = self.inject_common_bot_rules()
        all_rules.extend(common_rules_data.get('validation_rules', []))
        return {
            'validation_rules': all_rules
        }
    
    def get_action_instructions(self) -> List[str]:
        action_instructions = []
        base_actions_path = self.base_actions_dir
        config_path = base_actions_path / 'validate' / 'action_config.json'
        config = read_json_file(config_path)
        action_instructions = config.get('instructions', [])
        return action_instructions
    
    def inject_next_action_instructions(self):
        return ""
    
    def injectValidationInstructions(self, knowledge_graph: Dict[str, Any], files: Optional[Dict[str, List[Path]]] = None) -> Dict[str, Any]:
        action_instructions = self.get_action_instructions()
        writer = ValidationReportWriter(self.behavior.name, self.behavior.bot_paths)
        report_path = writer.get_report_path()
        report_link = writer.get_report_hyperlink()
        
        if not self.rules:
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
        action_instructions.append(f"\nValidation report: {report_link}")
        instructions = {
            'action': 'validate',
            'behavior': self.behavior.name,
            'base_instructions': action_instructions,
            'validation_rules': processed_rules,
            'content_to_validate': None,
            'report_path': str(report_path),
            'report_link': report_link
        }
        return {'instructions': instructions}
    
    def finalize_and_transition(self, next_action: str = None):
        class ActionResult:
            def __init__(self, next_action):
                self.next_action = next_action
        return ActionResult(next_action=next_action)
