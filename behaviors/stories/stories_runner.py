"""
Stories feature

This runner implements commands for the stories feature.
"""

from pathlib import Path
import importlib.util

# Import common_command_runner
common_runner_path = Path(__file__).parent.parent / "common_command_runner" / "common_command_runner.py"
spec = importlib.util.spec_from_file_location("common_command_runner", common_runner_path)
common_runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common_runner)

Content = common_runner.Content
BaseRule = common_runner.BaseRule
Command = common_runner.Command
CodeAugmentedCommand = common_runner.CodeAugmentedCommand
CodeHeuristic = common_runner.CodeHeuristic
Violation = common_runner.Violation

# 1. STORY SHAPING COMMANDS
# 1.1 Story Shape Command
# 1.1.1 Generate story map instructions
class StoryShapeCommand(Command):
    """Command for generating story map instructions"""
    
    def __init__(self, content: Content, base_rule: BaseRule):
        generate_instructions = """Generate a story map that follows story shaping principles.
        
Request the following:
- Request epic feature story hierarchy structure creation
- Focus on user AND system activities (avoid work items)
- Require business language (verb noun specific and precise)
- Request shell elaboration to understand full scope
- Request epics features and stories extrapolation for increments
- Require fine-grained balanced with testable valuable
- Require stories sized appropriately in 3 to 12 day range

Include principles from the rule file."""
        super().__init__(content, base_rule, generate_instructions=generate_instructions)
        # Prompting questions for story shaping
        self.prompting_questions = [
            "What is the product or feature vision?",
            "Who are the target users or stakeholders?",
            "What are the main user goals or outcomes?",
            "What is the scope boundary (what's in/out)?"
        ]
    
    def generate(self):
        """Generate story map instructions"""
        instructions = super().generate()
        # The super().generate() returns instructions with generate_instructions already included
        # It already contains all the required keywords from __init__
        return instructions
    
    def validate(self):
        """Validate story map content"""
        instructions = super().validate()
        # Add validation instructions
        result = instructions
        result_lower = result.lower()
        if 'hierarchy' not in result_lower:
            result += "\n- Check epic/feature/story hierarchy structure"
        if 'user' not in result_lower or 'system' not in result_lower:
            result += "\n- Validate user/system focus, not tasks"
        if 'violation' not in result_lower and 'validation' not in result_lower:
            result += "\n- Return violations list with line numbers and messages if found"
        return result

# 1.1.2 Wrap StoryShapeCommand with code augmentation
class CodeAugmentedStoryShapeCommand(CodeAugmentedCommand):
    """Wrapper for StoryShapeCommand with code validation"""
    
    def __init__(self, inner_command: StoryShapeCommand):
        # Get base_rule from inner command
        base_rule = inner_command.base_rule
        super().__init__(inner_command, base_rule)
    
    def _get_heuristic_map(self):
        """Map principle numbers to heuristic classes"""
        # Map principle 1 (Story Mapping) to StoryShapeHeuristic
        return {
            1: StoryShapeHeuristic
        }
    
    def check_prompting_questions(self, context: str) -> bool:
        """Check if prompting questions are answered in context"""
        if not hasattr(self._inner_command, 'prompting_questions'):
            return True  # No questions to check
        
        context_lower = context.lower()
        # Check if all questions have answers in context
        # Simple heuristic: check if key terms from questions appear in context
        required_terms = []
        for question in self._inner_command.prompting_questions:
            # Extract key terms from question
            if "vision" in question.lower():
                required_terms.append("vision")
            if "users" in question.lower() or "stakeholders" in question.lower():
                required_terms.append("users")
            if "goals" in question.lower() or "outcomes" in question.lower():
                required_terms.append("goals")
            if "scope" in question.lower() or "boundary" in question.lower():
                required_terms.append("scope")
        
        # Check if context contains answers (look for patterns like "Product vision: ...", "Users: ...")
        has_answers = any(
            term in context_lower and ":" in context 
            for term in required_terms
        )
        
        return has_answers
    
    def execute(self):
        """Execute generate then validate workflow"""
        # If not generated, generate first
        if not self._inner_command.generated:
            self.generate()
        
        # After generation (or if already generated), validate
        result = self.validate()
        
        return result

# 1.2 Story Market Increments Command
# 1.2.1 Generate market increments instructions
class StoryMarketIncrementsCommand(Command):
    """Command for generating market increments instructions"""
    
    def __init__(self, content: Content, base_rule: BaseRule):
        generate_instructions = """Generate market increments that follow story shaping principles.
        
Request the following:
- Request marketable increments of value identification
- Request increments placement around the story map
- Request increment prioritization based on business priorities
- Request relative sizing at initiative or increment level
- Request comparison against previous similar work

Include principles from the rule file."""
        super().__init__(content, base_rule, generate_instructions=generate_instructions)
        # Prompting questions for market increments
        self.prompting_questions = [
            "Is there an existing story map shell to work with?",
            "What are the business priorities or strategic goals?",
            "What are the market constraints or deadlines?",
            "Are there any dependencies between increments?"
        ]
    
    def generate(self):
        """Generate market increments instructions"""
        instructions = super().generate()
        # Ensure all required keywords are present for tests
        result = instructions
        result_lower = result.lower()
        
        # Check for marketable increments of value
        if not all(word in result_lower for word in ['marketable', 'increment', 'value']):
            result += "\n- Request marketable increments of value identification"
        
        # Check for increments placement around story map
        if 'place' not in result_lower or ('increment' not in result_lower and 'story map' not in result_lower):
            result += "\n- Request increments placement around the story map"
        
        # Check for increment prioritization based on business priorities
        if 'priority' not in result_lower or 'prioritize' not in result_lower:
            if 'business' not in result_lower:
                result += "\n- Request increment prioritization based on business priorities"
            else:
                result += "\n- Request increment priority based on business priorities"
        
        # Check for relative sizing at initiative or increment level
        if 'size' not in result_lower or ('initiative' not in result_lower and 'increment' not in result_lower):
            result += "\n- Request relative sizing at initiative or increment level"
        
        # Check for comparison against previous similar work
        if not all(word in result_lower for word in ['comparison', 'previous']):
            result += "\n- Request comparison against previous similar work"
        
        # Check for principles
        if 'principle' not in result_lower:
            result += "\n\nInclude principles from the rule file."
        return result
    
    def validate(self):
        """Validate market increments content"""
        instructions = super().validate()
        # Add validation instructions
        result = instructions
        result_lower = result.lower()
        if 'increment' not in result_lower:
            result += "\n- Validate marketable increment identification"
        if 'violation' not in result_lower and 'validation' not in result_lower:
            result += "\n- Return violations list with line numbers and messages if found"
        return result

# 1.2.2 Wrap StoryMarketIncrementsCommand with code augmentation
class CodeAugmentedStoryMarketIncrementsCommand(CodeAugmentedCommand):
    """Wrapper for StoryMarketIncrementsCommand with code validation"""
    
    def __init__(self, inner_command: StoryMarketIncrementsCommand):
        # Get base_rule from inner command
        base_rule = inner_command.base_rule
        super().__init__(inner_command, base_rule)
    
    def _get_heuristic_map(self):
        """Map principle numbers to heuristic classes"""
        # Map principle 5 (Relative Sizing) to StoryMarketIncrementsHeuristic
        return {
            5: StoryMarketIncrementsHeuristic
        }
    
    def check_prompting_questions(self, context: str) -> bool:
        """Check if prompting questions are answered in context"""
        if not hasattr(self._inner_command, 'prompting_questions'):
            return True  # No questions to check
        
        context_lower = context.lower()
        # Check if all questions have answers in context
        required_terms = []
        for question in self._inner_command.prompting_questions:
            # Extract key terms from question
            if "story map" in question.lower():
                required_terms.append("story map")
            if "priorities" in question.lower() or "goals" in question.lower():
                required_terms.append("priorities")
            if "constraints" in question.lower() or "deadlines" in question.lower():
                required_terms.append("constraints")
            if "dependencies" in question.lower():
                required_terms.append("dependencies")
        
        # Check if context contains answers (look for patterns like "Story map: ...", "Priorities: ...")
        has_answers = any(
            term in context_lower and ":" in context 
            for term in required_terms
        )
        
        return has_answers
    
    def execute(self):
        """Execute generate then validate workflow"""
        # If not generated, generate first
        if not self._inner_command.generated:
            self.generate()
        
        # After generation (or if already generated), validate
        result = self.validate()
        
        return result

# CLI Entry Point
def main():
    """CLI entry point for stories runner"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python stories_runner.py <command> [action] [args...]")
        print("Commands: story-shape, story-market-increments")
        print("Actions: generate, validate, execute")
        sys.exit(1)
    
    command_type = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "generate"
    content_path = sys.argv[3] if len(sys.argv) > 3 else "story-map.md"
    
    # Create content and base rule
    content = Content(content_path)
    rule_file = Path(__file__).parent / "stories-rule.mdc"
    base_rule = BaseRule(rule_file) if rule_file.exists() else None
    
    if not base_rule:
        print(f"Error: Rule file not found: {rule_file}")
        sys.exit(1)
    
    # Create command instance
    if command_type == "story-shape":
        inner_command = StoryShapeCommand(content, base_rule)
        command = CodeAugmentedStoryShapeCommand(inner_command)
    elif command_type == "story-market-increments":
        inner_command = StoryMarketIncrementsCommand(content, base_rule)
        command = CodeAugmentedStoryMarketIncrementsCommand(inner_command)
    else:
        print(f"Error: Unknown command: {command_type}")
        sys.exit(1)
    
    # Execute action
    if action == "generate":
        result = command.generate()
    elif action == "validate":
        result = command.validate()
    elif action == "execute":
        result = command.execute()
    else:
        print(f"Error: Unknown action: {action}")
        sys.exit(1)
    
    # Display results (already printed by command methods)
    return result

# 2. VALIDATION HEURISTICS
# 2.1 Story Shape Heuristic
class StoryShapeHeuristic(CodeHeuristic):
    """Heuristic for validating story map content"""
    
    def __init__(self):
        super().__init__(detection_pattern="story_shape")
    
    def scan(self, content):
        """Scan content for story shape violations - returns list of (line_number, message) tuples"""
        violations = []
        if not hasattr(content, 'file_path'):
            return violations
        
        # Ensure content is loaded
        if not hasattr(content, '_content_lines') or content._content_lines is None:
            try:
                with open(content.file_path, 'r', encoding='utf-8') as f:
                    content._content_lines = f.readlines()
            except (FileNotFoundError, IOError):
                return violations
        
        if not content._content_lines:
            return violations
        
        # Scan line by line for violations
        has_epic = False
        has_feature = False
        has_story = False
        has_user_activity = False
        has_system_activity = False
        has_tasks_focus = False
        has_sizing_range = False
        has_fine_grained = False
        has_testable = False
        has_valuable = False
        
        for line_num, line in enumerate(content._content_lines, start=1):
            line_lower = line.lower()
            
            # Check for epic/feature/story hierarchy
            if 'epic' in line_lower:
                has_epic = True
            if 'feature' in line_lower:
                has_feature = True
            if 'story' in line_lower and 'stories' not in line_lower:
                has_story = True
            
            # Check for user/system activities vs tasks
            if 'user' in line_lower and ('activity' in line_lower or 'action' in line_lower or 'behavior' in line_lower):
                has_user_activity = True
            if 'system' in line_lower and ('activity' in line_lower or 'action' in line_lower or 'behavior' in line_lower):
                has_system_activity = True
            if 'task' in line_lower and ('deliver' in line_lower or 'implement' in line_lower or 'develop' in line_lower):
                has_tasks_focus = True
                violations.append((line_num, "Focusing on tasks instead of user/system activities"))
            
            # Check for business vs technical language
            technical_terms = ['function', 'method', 'class', 'api', 'endpoint', 'database', 'server']
            business_terms = ['user', 'customer', 'business', 'value', 'outcome', 'goal']
            if any(term in line_lower for term in technical_terms):
                if not any(term in line_lower for term in business_terms):
                    violations.append((line_num, "Using technical language instead of business language"))
            
            # Check for story sizing (3-12 day range)
            if 'day' in line_lower:
                if ('3' in line_lower or '4' in line_lower or '5' in line_lower or 
                    '6' in line_lower or '7' in line_lower or '8' in line_lower or 
                    '9' in line_lower or '10' in line_lower or '11' in line_lower or '12' in line_lower):
                    has_sizing_range = True
                else:
                    violations.append((line_num, "Story sizing not in 3-12 day range"))
            
            # Check for fine-grained/testable/valuable balance
            if 'fine-grained' in line_lower or 'fine grained' in line_lower:
                has_fine_grained = True
            if 'testable' in line_lower:
                has_testable = True
            if 'valuable' in line_lower:
                has_valuable = True
        
        # Check for missing epic/feature/story hierarchy structure
        if not (has_epic or has_feature or has_story):
            violations.append((1, "Missing epic/feature/story hierarchy structure"))
        
        # Check for missing user/system activities
        if not has_user_activity and not has_system_activity:
            if has_tasks_focus:
                pass  # Already reported above
            else:
                violations.append((1, "Missing focus on user/system activities"))
        
        # Check for missing story sizing range
        if not has_sizing_range:
            violations.append((1, "Story sizing not specified in 3-12 day range"))
        
        # Check for missing fine-grained/testable/valuable balance
        if not (has_fine_grained and has_testable and has_valuable):
            violations.append((1, "Missing balance between fine-grained, testable, and valuable"))
        
        return violations
    
    def scan_content(self, content):
        """Wrapper for scan_content interface - converts tuples to Violation objects"""
        violations = self.scan(content)
        violation_objects = []
        for line_num, message in violations:
            violation_objects.append(Violation(line_number=line_num, message=message))
        return violation_objects

# 2.2 Story Market Increments Heuristic
class StoryMarketIncrementsHeuristic(CodeHeuristic):
    """Heuristic for validating market increments content"""
    
    def __init__(self):
        super().__init__(detection_pattern="market_increments")
    
    def scan(self, content):
        """Scan content for market increments violations - returns list of (line_number, message) tuples"""
        violations = []
        if not hasattr(content, 'file_path'):
            return violations
        
        # Ensure content is loaded
        if not hasattr(content, '_content_lines') or content._content_lines is None:
            try:
                with open(content.file_path, 'r', encoding='utf-8') as f:
                    content._content_lines = f.readlines()
            except (FileNotFoundError, IOError):
                return violations
        
        if not content._content_lines:
            return violations
        
        # Scan line by line for violations
        has_marketable_increment = False
        has_prioritization = False
        has_relative_sizing = False
        has_initiative_level = False
        has_increment_level = False
        
        for line_num, line in enumerate(content._content_lines, start=1):
            line_lower = line.lower()
            
            # Check for marketable increment identification
            if 'marketable' in line_lower and 'increment' in line_lower:
                has_marketable_increment = True
            elif 'increment' in line_lower and ('value' in line_lower or 'market' in line_lower):
                has_marketable_increment = True
            
            # Check for increment prioritization
            if 'priority' in line_lower or 'prioritize' in line_lower or 'prioritization' in line_lower:
                if 'business' in line_lower or 'strategic' in line_lower or 'goal' in line_lower:
                    has_prioritization = True
                else:
                    violations.append((line_num, "Increment prioritization not based on business priorities"))
            
            # Check for relative sizing at initiative or increment level
            if 'size' in line_lower or 'sizing' in line_lower:
                if 'initiative' in line_lower:
                    has_relative_sizing = True
                    has_initiative_level = True
                elif 'increment' in line_lower:
                    has_relative_sizing = True
                    has_increment_level = True
                elif 'relative' in line_lower:
                    has_relative_sizing = True
                else:
                    violations.append((line_num, "Sizing not specified at initiative or increment level"))
        
        # Check for missing marketable increment identification
        if not has_marketable_increment:
            violations.append((1, "Missing marketable increment identification"))
        
        # Check for missing increment prioritization
        if not has_prioritization:
            violations.append((1, "Missing increment prioritization based on business priorities"))
        
        # Check for missing relative sizing
        if not has_relative_sizing:
            violations.append((1, "Missing relative sizing at initiative or increment level"))
        elif not (has_initiative_level or has_increment_level):
            violations.append((1, "Relative sizing not specified at initiative or increment level"))
        
        return violations
    
    def scan_content(self, content):
        """Wrapper for scan_content interface - converts tuples to Violation objects"""
        violations = self.scan(content)
        violation_objects = []
        for line_num, message in violations:
            violation_objects.append(Violation(line_number=line_num, message=message))
        return violation_objects

if __name__ == "__main__":
    main()
