"""
Validate Code Files Action

Extends ValidateRulesAction to validate generated code files
(test files for 7_tests behavior, source files for 8_code behavior).
Files must be passed as parameters - no auto-discovery.
"""
from pathlib import Path
from typing import Dict, Any, List
from agile_bot.bots.base_bot.src.bot.validate_rules_action import ValidateRulesAction


class ValidateCodeFilesAction(ValidateRulesAction):
    """Action that validates both knowledge graph and generated code files.
    
    Files must be passed as parameters (test_files or code_files).
    No auto-discovery - files must be explicitly provided.
    """
    
    def do_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation for both knowledge graph and code files.
        
        Overrides base method to:
        1. Call base do_execute() to validate knowledge graph (with test files if provided)
        2. Get code files from parameters (test_files or code_files) - no auto-discovery
        3. Validate each code file individually using ValidateRulesAction with test_file parameter
        4. Merge violations from both knowledge graph and code files
        """
        # Step 1: Validate knowledge graph (call base implementation)
        # This will handle test files if they're in parameters
        kg_result = super().do_execute(parameters)
        
        # Step 2: Get code files from parameters (not auto-discovery)
        code_files = []
        if parameters.get('test_files'):
            test_files_list = parameters['test_files']
            if isinstance(test_files_list, list):
                code_files.extend(test_files_list)
            else:
                code_files.append(test_files_list)
        if parameters.get('code_files'):
            code_files_list = parameters['code_files']
            if isinstance(code_files_list, list):
                code_files.extend(code_files_list)
            else:
                code_files.append(code_files_list)
        
        if not code_files:
            # No code files to validate, return knowledge graph results
            return kg_result
        
        # Step 3: Validate each code file and merge violations
        all_violations = []
        
        # Extract violations from knowledge graph validation
        kg_instructions = kg_result.get('instructions', {})
        kg_validation_rules = kg_instructions.get('validation_rules', [])
        
        # Collect violations from knowledge graph validation
        # Violations are stored in self._violations by injectValidationInstructions
        all_violations.extend(self._violations)
        
        # Track seen rules to avoid duplicates
        seen_rules = {r.get('rule_file', '') for r in kg_validation_rules}
        merged_rules = list(kg_validation_rules)
        
        # Validate each code file
        for code_file_path in code_files:
            file_path = Path(code_file_path)
            if not file_path.exists():
                continue
            
            # Create a new ValidateRulesAction instance to validate this file
            # Use test_file parameter to validate the file
            file_validator = ValidateRulesAction(
                bot_name=self.bot_name,
                behavior=self.behavior,
                bot_directory=self.bot_directory
            )
            
            # Validate the file
            file_result = file_validator.do_execute({
                'test_file': str(file_path)
            })
            
            # Extract violations from file validation
            all_violations.extend(file_validator._violations)
            
            # Merge validation rules (avoid duplicates)
            file_instructions = file_result.get('instructions', {})
            file_validation_rules = file_instructions.get('validation_rules', [])
            
            for rule in file_validation_rules:
                rule_file = rule.get('rule_file', '')
                if rule_file and rule_file not in seen_rules:
                    merged_rules.append(rule)
                    seen_rules.add(rule_file)
        
        # Step 4: Merge violations and rules into result
        kg_result['violations'] = all_violations
        
        # Update instructions with merged validation rules
        if kg_instructions:
            kg_instructions['validation_rules'] = merged_rules
            kg_result['instructions'] = kg_instructions
        
        # Update self._violations to include all violations
        self._violations = all_violations
        
        return kg_result

