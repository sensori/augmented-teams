"""
Rules collection.

Wraps rule loading for a behavior.
"""
from typing import List, Any


class Rules:
    """Load and expose rules for a behavior."""

    def __init__(self, behavior):
        """Initialize Rules collection.
        
        Args:
            behavior: Behavior instance to load rules for
        """
        self.behavior = behavior
        self.bot_name = behavior.bot_name
        self.behavior_name = behavior.name

    def all(self) -> List[Any]:
        """Return Rule objects using existing ValidateRulesAction logic."""
        from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction, Rule

        if self.behavior.bot is None:
            raise RuntimeError("Cannot load rules: bot instance not set on behavior")
        
        action = ValidateRulesAction(
            bot_name=self.bot_name,
            behavior=self.behavior,
            action_name='validate_rules'
        )
        rules_data = action.inject_behavior_specific_and_bot_rules()
        validation_rules = rules_data.get('validation_rules', [])

        rule_objects = []
        for rule_dict in validation_rules:
            if isinstance(rule_dict, dict):
                rule_file = rule_dict.get('rule_file', 'unknown.json')
                rule_content = rule_dict.get('rule_content', rule_dict)

                behavior_name = 'common'
                if '/behaviors/' in rule_file:
                    parts = rule_file.split('/behaviors/')
                    if len(parts) > 1:
                        behavior_name = parts[1].split('/')[0]

                rule_obj = Rule(rule_file, rule_content, behavior_name)
                rule_objects.append(rule_obj)
        return rule_objects

    def scanners(self) -> List[type]:
        """Return scanner classes across all rules."""
        scanners = []
        for rule in self.all():
            scanner = getattr(rule, "scanner", None)
            if scanner is not None:
                scanners.append(scanner)
        return scanners

