from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import re
from agile_bot.bots.base_bot.src.bot.bot_paths import BotPaths

logger = logging.getLogger(__name__)


class ValidationReportWriter:
    """Writes validation reports to markdown files."""
    
    def __init__(self, behavior_name: str, bot_paths: BotPaths):
        """Initialize ValidationReportWriter.
        
        Args:
            behavior_name: Name of the behavior being validated
            bot_paths: BotPaths instance for accessing workspace and documentation paths
        """
        self.behavior_name = behavior_name
        self.bot_paths = bot_paths
        self.workspace_directory = bot_paths.workspace_directory
    
    def write(self, instructions: Dict[str, Any], validation_rules: List[Dict[str, Any]], files: Dict[str, List[Path]]) -> None:
        """Write validation report to file.
        
        Args:
            instructions: Instructions structure with base_instructions and validation_rules
            validation_rules: List of validation rules
            files: Dict mapping file type keys to lists of file paths (e.g., {'test': [...], 'src': [...]})
        """
        report_path = self._get_report_path()
        
        logger.info("=== _write_validation_report START ===")
        logger.info(f"Report path: {report_path}")
        logger.info(f"Number of validation rules: {len(validation_rules)}")
        
        try:
            report_file = Path(report_path)
            report_file.parent.mkdir(parents=True, exist_ok=True)
            
            lines = self._build_report_lines(instructions, validation_rules, files, report_path)
            
            logger.info("Step 4: Writing report to file...")
            logger.info(f"Report file path: {report_file}")
            logger.info(f"Number of lines to write: {len(lines)}")
            report_file.write_text('\n'.join(lines), encoding='utf-8')
            logger.info("Report file written successfully")
            logger.info("=== _write_validation_report COMPLETE ===")
        except Exception as e:
            import traceback
            logger.error("=== ERROR in _write_validation_report ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {e}")
            logger.error(f"Report path: {report_path}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            raise
    
    def get_report_path(self) -> Path:
        """Get report path from bot_paths.
        
        Returns:
            Path object for the validation report file
        """
        docs_path = self.bot_paths.documentation_path
        docs_dir = self.workspace_directory / docs_path
        report_file = docs_dir / 'validation-report.md'
        return report_file
    
    def _get_report_path(self) -> str:
        """Get report path as string (for internal use)."""
        return str(self.get_report_path())
    
    def get_report_hyperlink(self) -> str:
        """Create a VS Code-compatible hyperlink for the report path.
        
        Returns:
            Markdown-formatted hyperlink string
        """
        report_path = self.get_report_path()
        try:
            resolved_path = report_path.resolve() if report_path.exists() else report_path
            file_str = str(resolved_path).replace('\\', '/')
            if len(file_str) >= 2 and file_str[1] == ':':
                file_str = file_str[0].upper() + ':' + file_str[2:]
            vscode_uri = f"vscode://file/{file_str}"
            
            # Get relative path for display
            try:
                rel_path = str(report_path.relative_to(self.workspace_directory))
            except ValueError:
                rel_path = str(report_path)
            
            return f"[{rel_path}]({vscode_uri})"
        except Exception as e:
            logger.warning(f"Could not create report hyperlink: {e}")
            return str(report_path)
    
    def _build_report_lines(self, instructions: Dict[str, Any], validation_rules: List[Dict[str, Any]], files: Dict[str, List[Path]], report_path: str) -> List[str]:
        """Build all lines for the validation report.
        
        Args:
            instructions: Instructions structure
            validation_rules: List of validation rules
            files: Dict mapping file type keys to lists of file paths
            report_path: Path where report will be saved
            
        Returns:
            List of markdown lines
        """
        lines = []
        lines.extend(self._build_header())
        lines.extend(self._build_metadata())
        lines.extend(self._build_summary(validation_rules))
        lines.extend(self._build_content_validated(files))
        lines.extend(self._build_validation_rules(validation_rules))
        lines.extend(self._build_violations(validation_rules))
        lines.extend(self._build_instructions(instructions))
        lines.extend(self._build_report_location(report_path))
        return lines
    
    def _build_header(self) -> List[str]:
        """Build report header."""
        return [
            f"# Validation Report - {self.behavior_name.replace('_', ' ').title()}",
            ""
        ]
    
    def _build_metadata(self) -> List[str]:
        """Build metadata section."""
        return [
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Project:** {self.workspace_directory.name}",
            f"**Behavior:** {self.behavior_name}",
            f"**Action:** validate_rules",
            ""
        ]
    
    def _build_summary(self, validation_rules: List[Dict[str, Any]]) -> List[str]:
        """Build summary section."""
        total_rules = len(validation_rules)
        return [
            "## Summary",
            "",
            f"Validated story map and domain model against **{total_rules} validation rules**.",
            ""
        ]
    
    def _build_content_validated(self, files: Dict[str, List[Path]]) -> List[str]:
        """Build content validated section."""
        lines = [
            "## Content Validated",
            ""
        ]
        
        clarification_file, planning_file, rendered_outputs = self._find_content_files()
        
        if clarification_file:
            lines.append(f"- **Clarification:** `{clarification_file.name}`")
        if planning_file:
            lines.append(f"- **Planning:** `{planning_file.name}`")
        if rendered_outputs:
            lines.append("- **Rendered Outputs:**")
            for output in rendered_outputs:
                lines.append(f"  - `{output.name}`")
        
        test_files_scanned = [str(fp) for fp in files.get('test', [])]
        code_files_scanned = [str(fp) for fp in files.get('src', [])]
        
        lines.extend(self._build_scanned_files_section('test', test_files_scanned, 'Test Files Scanned'))
        lines.extend(self._build_scanned_files_section('src', code_files_scanned, 'Code Files Scanned'))
        
        lines.append("")
        return lines
    
    def _find_content_files(self) -> tuple:
        """Find clarification.json, planning.json, and rendered outputs.
        
        Returns:
            Tuple of (clarification_file, planning_file, rendered_outputs)
        """
        docs_path = self.bot_paths.documentation_path
        docs_dir = self.workspace_directory / docs_path
        
        clarification_file = docs_dir / 'clarification.json'
        planning_file = docs_dir / 'planning.json'
        
        clarification = clarification_file if clarification_file.exists() else None
        planning = planning_file if planning_file.exists() else None
        
        rendered_outputs = []
        if docs_dir.exists():
            rendered_patterns = [
                '*-story-map.md',
                '*-domain-model-description.md',
                '*-domain-model-diagram.md',
                'story-graph.json',
                '*-increments.md'
            ]
            for pattern in rendered_patterns:
                for file_path in docs_dir.glob(pattern):
                    rendered_outputs.append(file_path)
        
        return clarification, planning, rendered_outputs
    
    def _build_scanned_files_section(self, file_type: str, files_scanned: List[str], section_title: str) -> List[str]:
        """Build a scanned files section (test files or code files).
        
        Args:
            file_type: Type of files ('test' or 'src')
            files_scanned: List of file paths that were scanned
            section_title: Title for the section
            
        Returns:
            List of markdown lines
        """
        lines = []
        if files_scanned:
            logger.info(f"{section_title} from content_info: {len(files_scanned)} files")
            lines.append(f"- **{section_title}:**")
            for file_str in sorted(files_scanned):
                file_path = Path(file_str)
                rel_path = self._get_relative_path(file_path)
                lines.append(f"  - `{rel_path}`")
            lines.append(f"  - **Total:** {len(files_scanned)} {file_type} file(s)")
        return lines
    
    def _get_relative_path(self, file_path: Path) -> str:
        """Get relative path for display, falling back to filename if needed.
        
        Args:
            file_path: Path to convert
            
        Returns:
            Relative path string or filename
        """
        try:
            if file_path.is_absolute() and self.workspace_directory:
                return str(file_path.relative_to(self.workspace_directory))
            elif self.workspace_directory and not file_path.is_absolute():
                try:
                    resolved = (self.workspace_directory / file_path).resolve()
                    return str(resolved.relative_to(self.workspace_directory))
                except (ValueError, AttributeError):
                    return file_path.name
            else:
                return file_path.name
        except (ValueError, AttributeError) as e:
            logger.warning(f"Could not create relative path for {file_path}: {e}")
            return file_path.name
    
    def _build_validation_rules(self, validation_rules: List[Dict[str, Any]]) -> List[str]:
        """Build validation rules section."""
        lines = [
            "## Validation Rules Checked",
            ""
        ]
        
        total_rules = len(validation_rules)
        for rule_dict in validation_rules[:20]:
            rule_file = rule_dict.get('rule_file', 'unknown')
            rule_content = rule_dict.get('rule_content', rule_dict)
            description = rule_content.get('description', 'No description')
            rule_name = Path(rule_file).stem if rule_file else 'unknown'
            lines.append(f"### Rule: {rule_name.replace('_', ' ').title()}")
            lines.append(f"**Description:** {description}")
            lines.append("")
        
        if total_rules > 20:
            lines.append(f"*... and {total_rules - 20} more rules*")
            lines.append("")
        
        return lines
    
    def _build_violations(self, validation_rules: List[Dict[str, Any]]) -> List[str]:
        """Build violations section."""
        lines = [
            "## Violations Found",
            ""
        ]
        
        file_by_file_violations_by_rule, cross_file_violations_by_rule = self._organize_violations(validation_rules)
        total_file_by_file = sum(len(v) for v in file_by_file_violations_by_rule.values())
        total_cross_file = sum(len(v) for v in cross_file_violations_by_rule.values())
        total_violations = total_file_by_file + total_cross_file
        
        if total_violations == 0:
            lines.append("✅ **No violations found.** All rules passed validation.")
            lines.append("")
        else:
            lines.append(f"**Total Violations:** {total_violations}")
            lines.append(f"- **File-by-File Violations:** {total_file_by_file}")
            lines.append(f"- **Cross-File Violations:** {total_cross_file}")
            lines.append("")
            
            if file_by_file_violations_by_rule:
                lines.extend(self._build_violations_by_type(file_by_file_violations_by_rule, "File-by-File Violations (Pass 1)", 
                    "These violations were detected by scanning each file individually."))
            
            if cross_file_violations_by_rule:
                lines.extend(self._build_violations_by_type(cross_file_violations_by_rule, "Cross-File Violations (Pass 2)",
                    "These violations were detected by analyzing all files together to find patterns that span multiple files."))
        
        return lines
    
    def _organize_violations(self, validation_rules: List[Dict[str, Any]]) -> tuple:
        """Organize violations by rule and type.
        
        Returns:
            Tuple of (file_by_file_violations_by_rule, cross_file_violations_by_rule) dicts
        """
        file_by_file_violations_by_rule = {}
        cross_file_violations_by_rule = {}
        
        for rule_dict in validation_rules:
            rule_file = rule_dict.get('rule_file', 'unknown')
            scanner_results = rule_dict.get('scanner_results', {})
            rule_name = Path(rule_file).stem if rule_file else 'unknown'
            
            if 'file_by_file' in scanner_results or 'cross_file' in scanner_results:
                file_by_file_violations = scanner_results.get('file_by_file', {}).get('violations', [])
                cross_file_violations = scanner_results.get('cross_file', {}).get('violations', [])
                
                if file_by_file_violations:
                    file_by_file_violations_by_rule[rule_name] = file_by_file_violations
                if cross_file_violations:
                    cross_file_violations_by_rule[rule_name] = cross_file_violations
        
        return file_by_file_violations_by_rule, cross_file_violations_by_rule
    
    def _build_violations_by_type(self, violations_by_rule: Dict[str, List[Dict[str, Any]]], title: str, description: str) -> List[str]:
        """Build violations section for a specific type (file-by-file or cross-file).
        
        Args:
            violations_by_rule: Dict mapping rule names to lists of violations
            title: Section title
            description: Section description
            
        Returns:
            List of markdown lines
        """
        lines = [
            f"### {title}",
            "",
            description,
            ""
        ]
        
        for rule_name, violations in violations_by_rule.items():
            lines.append(f"#### {rule_name.replace('_', ' ').title()}: {len(violations)} violation(s)")
            lines.append("")
            
            for violation in violations:
                location = violation.get('location', 'unknown')
                message = violation.get('violation_message', 'No message')
                severity = violation.get('severity', 'error')
                line_number = violation.get('line_number')
                severity_icon = '🔴' if severity == 'error' else '🟡' if severity == 'warning' else '🔵'
                
                location_link = self._create_file_link(location, line_number)
                test_info = self._extract_test_info(message, location, line_number)
                
                if test_info:
                    lines.append(f"- {severity_icon} **{severity.upper()}** - {location_link}: {test_info}")
                else:
                    lines.append(f"- {severity_icon} **{severity.upper()}** - {location_link}: {message}")
            
            lines.append("")
        
        return lines
    
    def _build_instructions(self, instructions: Dict[str, Any]) -> List[str]:
        """Build validation instructions section."""
        lines = [
            "## Validation Instructions",
            ""
        ]
        
        base_instructions = instructions.get('base_instructions', [])
        if base_instructions:
            lines.append("The following validation steps were performed:")
            lines.append("")
            for i, instruction in enumerate(base_instructions[:10], 1):
                lines.append(f"{i}. {instruction}")
            if len(base_instructions) > 10:
                lines.append(f"*... and {len(base_instructions) - 10} more instructions*")
        lines.append("")
        
        return lines
    
    def _build_report_location(self, report_path: str) -> List[str]:
        """Build report location section."""
        return [
            "## Report Location",
            "",
            f"This report was automatically generated and saved to:",
            f"`{report_path}`",
            ""
        ]
    
    def _create_file_link(self, location: str, line_number: Optional[int] = None) -> str:
        """Create a clickable file link for the validation report using VS Code URIs.
        
        Args:
            location: File path (can be absolute or relative)
            line_number: Optional line number to link to
            
        Returns:
            Markdown link string with VS Code URI
        """
        if location == 'unknown' or not location:
            return f"`{location}`"
        
        try:
            file_path = Path(location)
            
            is_absolute = file_path.is_absolute() or (len(location) > 1 and location[1] == ':') or location.startswith('\\\\')
            
            if is_absolute:
                if self.workspace_directory:
                    try:
                        rel_path = file_path.relative_to(self.workspace_directory)
                        file_uri = self._get_file_uri(location, line_number)
                        return f"[`{rel_path}`]({file_uri})"
                    except ValueError:
                        file_uri = self._get_file_uri(location, line_number)
                        return f"[`{Path(location).name}`]({file_uri})"
                else:
                    file_uri = self._get_file_uri(location, line_number)
                    return f"[`{Path(location).name}`]({file_uri})"
            else:
                return f"[`{location}`]({self._get_file_uri(location, line_number)})"
        except Exception:
            try:
                file_uri = self._get_file_uri(location, line_number)
                return f"[`{Path(location).name if location else location}`]({file_uri})"
            except Exception:
                if line_number:
                    return f"`{location}:{line_number}`"
                return f"`{location}`"
    
    def _extract_test_info(self, message: str, location: str, line_number: Optional[int] = None) -> Optional[str]:
        """Extract test class and method information from violation message and create links.
        
        Args:
            message: Violation message that may contain test names
            location: File path
            line_number: Line number where violation occurs
            
        Returns:
            Formatted message with clickable links to test class/method, or None if no test info found
        """
        test_method_patterns = [
            r'Test\s+method\s+["\']([^"\']+)["\']',
            r'Test\s+["\']([^"\']+)["\']',
            r'test\s+method\s+["\']([^"\']+)["\']',
        ]
        
        test_class_patterns = [
            r'Test\s+class\s+["\']([^"\']+)["\']',
            r'class\s+["\']([^"\']+)["\']',
        ]
        
        test_method_match = None
        for pattern in test_method_patterns:
            test_method_match = re.search(pattern, message, re.IGNORECASE)
            if test_method_match:
                break
        
        test_class_match = None
        for pattern in test_class_patterns:
            test_class_match = re.search(pattern, message, re.IGNORECASE)
            if test_class_match:
                break
        
        if not test_method_match and not test_class_match:
            return None
        
        file_uri = self._get_file_uri(location, line_number)
        
        try:
            if test_method_match:
                test_method_name = test_method_match.group(1)
                replacement = f'Test method [{test_method_name}]({file_uri})'
                message = message.replace(f'Test method "{test_method_name}"', replacement)
                message = message.replace(f"Test method '{test_method_name}'", replacement)
                message = message.replace(f'Test "{test_method_name}"', replacement)
                message = message.replace(f"Test '{test_method_name}'", replacement)
                message = message.replace(f'test method "{test_method_name}"', replacement)
                message = message.replace(f"test method '{test_method_name}'", replacement)
            
            if test_class_match:
                test_class_name = test_class_match.group(1)
                replacement = f'Test class [{test_class_name}]({file_uri})'
                message = message.replace(f'Test class "{test_class_name}"', replacement)
                message = message.replace(f"Test class '{test_class_name}'", replacement)
                message = message.replace(f'class "{test_class_name}"', replacement)
                message = message.replace(f"class '{test_class_name}'", replacement)
        except Exception as e:
            logger.warning(f"Failed to create test info links: {e}, returning original message")
            return None
        
        return message
    
    def _get_file_uri(self, location: str, line_number: Optional[int] = None) -> str:
        """Get VS Code-compatible file URI for markdown links.
        
        Args:
            location: File path
            line_number: Optional line number
            
        Returns:
            VS Code URI format: vscode://file/C:/path/to/file.py:123
        """
        try:
            file_path = Path(location)
            if file_path.is_absolute():
                resolved_path = file_path.resolve() if file_path.exists() else file_path
            else:
                if self.workspace_directory:
                    resolved_path = (self.workspace_directory / file_path).resolve()
                else:
                    resolved_path = Path(location)
            
            file_str = str(resolved_path).replace('\\', '/')
            if len(file_str) >= 2 and file_str[1] == ':':
                file_str = file_str[0].upper() + ':' + file_str[2:]
            
            vscode_uri = f"vscode://file/{file_str}"
            
            if line_number:
                vscode_uri = f"{vscode_uri}:{line_number}"
            
            return vscode_uri
        except Exception:
            file_str = location.replace('\\', '/')
            if len(file_str) >= 2 and file_str[1] == ':':
                file_str = file_str[0].upper() + ':' + file_str[2:]
            vscode_uri = f"vscode://file/{file_str}"
            if line_number:
                vscode_uri = f"{vscode_uri}:{line_number}"
            return vscode_uri

