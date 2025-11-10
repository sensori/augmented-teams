"""
Pytest plugin to discover and run Mamba BDD tests.
This allows VS Code to discover individual Mamba tests and show play buttons.

This plugin parses Mamba test files and creates pytest test items for each
'with it(...)' block, enabling VS Code's test explorer to show individual
test play buttons.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest


def pytest_collect_file(parent, file_path):
    """Collect Mamba test files (*_test.py)"""
    # Handle both pathlib.Path (new) and py.path.local (old) for compatibility
    if hasattr(file_path, 'name'):
        basename = file_path.name
        path_obj = file_path
    else:
        # Legacy py.path.local support
        basename = file_path.basename
        path_obj = Path(str(file_path))
    
    if basename.endswith('_test.py') or basename.startswith('test_'):
        return MambaFile.from_parent(parent, path=path_obj)


class MambaFile(pytest.File):
    """Represents a Mamba test file"""
    
    def collect(self):
        """Parse Mamba test file and create test items"""
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Use regex to find 'with it(...)' blocks (more reliable than AST for Mamba)
            # Pattern: 'with it('...'):' or 'with it("...")'
            it_pattern = r'with\s+it\s*\([\'"]([^\'"]+)[\'"]\)\s*:'
            
            for line_num, line in enumerate(lines, start=1):
                match = re.search(it_pattern, line)
                if match:
                    test_name = match.group(1)
                    # Create a sanitized test name for pytest
                    sanitized_name = re.sub(r'[^\w\s-]', '', test_name).strip().replace(' ', '_')
                    if sanitized_name:
                        yield MambaTestItem.from_parent(
                            self,
                            name=sanitized_name,
                            line_no=line_num,
                            test_name=test_name
                        )
        except Exception as e:
            # If parsing fails, create a single test item for the whole file
            yield MambaTestItem.from_parent(
                self,
                name=f"mamba_test_file_{self.path.stem}",
                line_no=1,
                test_name=None
            )
    


class MambaTestItem(pytest.Item):
    """Represents a single Mamba test"""
    
    def __init__(self, name, line_no, test_name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.line_no = line_no
        self.test_name = test_name
    
    def runtest(self):
        """Run the Mamba test using mamba CLI"""
        test_file = str(self.parent.path)
        test_file_path = Path(test_file).resolve()
        # Find workspace root (go up from test file directory until we find .vscode or .git)
        workspace_root = test_file_path.parent
        while workspace_root.parent != workspace_root:
            if (workspace_root / '.vscode').exists() or (workspace_root / '.git').exists():
                break
            workspace_root = workspace_root.parent
        
        # Run mamba with --line option to run specific test
        # Mamba uses --line to run tests at a specific line
        cmd = [sys.executable, '-m', 'mamba.cli', test_file, '--line', str(self.line_no)]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(workspace_root),
            timeout=60
        )
        
        if result.returncode != 0:
            error_msg = f"Mamba test failed at line {self.line_no}\n"
            error_msg += f"Command: {' '.join(cmd)}\n"
            error_msg += f"STDOUT:\n{result.stdout}\n"
            error_msg += f"STDERR:\n{result.stderr}\n"
            raise MambaTestError(error_msg)
    
    def repr_failure(self, excinfo):
        """Format test failure"""
        if isinstance(excinfo.value, MambaTestError):
            return str(excinfo.value)
        return super().repr_failure(excinfo)


class MambaTestError(Exception):
    """Custom exception for Mamba test failures"""
    pass

