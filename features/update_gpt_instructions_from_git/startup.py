#!/usr/bin/env python3
"""
GPT Builder Startup Script

This script reads bootstrap-config.json and pulls the latest instructions
from Git to set up the GPT runtime environment.

Usage:
    python startup.py [--config path/to/bootstrap-config.json]
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class GPTBuilderStartup:
    def __init__(self, config_path: str = "bootstrap-config.json"):
        self.repo_root = Path(__file__).resolve().parent  # Current feature directory
        self.config_path = self.repo_root / config_path
        self.config = None
        
    def load_bootstrap_config(self) -> Dict:
        """Load and validate bootstrap configuration."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            
            print(f"[OK] Loaded bootstrap config from {self.config_path}")
            return self.config
            
        except FileNotFoundError:
            print(f"[ERROR] Bootstrap config not found: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in bootstrap config: {e}")
            sys.exit(1)
    
    def check_auto_refresh_enabled(self) -> bool:
        """Check if auto-refresh is enabled in config."""
        if not self.config:
            return False
            
        auto_refresh = self.config.get('auto_refresh', {})
        return auto_refresh.get('enabled', False)
    
    def get_instruction_paths(self) -> List[str]:
        """Get instruction file paths from config."""
        if not self.config:
            return []
            
        auto_refresh = self.config.get('auto_refresh', {})
        return auto_refresh.get('instruction_paths', ['instructions/'])
    
    def ensure_latest_git(self) -> bool:
        """Pull latest changes from Git repository."""
        try:
            print("Pulling latest changes from Git...")
            
            # Get the actual repo root (3 levels up from feature directory)
            actual_repo_root = self.repo_root.parents[2]
            
            # Fetch latest
            subprocess.run(['git', 'fetch', 'origin'], 
                         cwd=actual_repo_root, check=True)
            
            # Checkout main branch
            subprocess.run(['git', 'checkout', 'main'], 
                         cwd=actual_repo_root, check=True)
            
            # Pull latest changes
            subprocess.run(['git', 'pull', 'origin', 'main'], 
                         cwd=actual_repo_root, check=True)
            
            print("[OK] Git repository is up to date")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Git operation failed: {e}")
            return False
    
    def validate_instruction_files(self) -> bool:
        """Validate that all required instruction files exist."""
        if not self.config:
            return False
            
        instruction_files = self.config.get('instruction_files', {})
        required_files = [
            instruction_files.get('primary', 'instructions/OPERATING_MODEL.md'),
            instruction_files.get('style_guide', 'instructions/STYLE_GUIDE.md'),
            instruction_files.get('tools', 'instructions/TOOLS.md'),
            instruction_files.get('examples', 'instructions/EXAMPLES.md'),
            instruction_files.get('purpose', 'instructions/PURPOSE.md')
        ]
        
        print("Validating instruction files...")
        all_exist = True
        
        # Get the actual repo root for instruction files
        actual_repo_root = self.repo_root.parents[2]
        
        for file_path in required_files:
            full_path = actual_repo_root / file_path
            if full_path.exists():
                print(f"  [OK] {file_path}")
            else:
                print(f"  [ERROR] {file_path} - MISSING")
                all_exist = False
        
        if all_exist:
            print("[OK] All required instruction files present")
        else:
            print("[ERROR] Some instruction files are missing")
            
        return all_exist
    
    def load_instructions_for_runtime(self) -> Dict[str, str]:
        """Load instruction files into memory for runtime use."""
        if not self.config:
            return {}
            
        instruction_files = self.config.get('instruction_files', {})
        loaded_instructions = {}
        
        print("Loading instruction files for runtime...")
        
        # Get the actual repo root for instruction files
        actual_repo_root = self.repo_root.parents[2]
        
        for key, file_path in instruction_files.items():
            full_path = actual_repo_root / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    loaded_instructions[key] = content
                    print(f"  [OK] Loaded {key}: {len(content)} characters")
            else:
                print(f"  [WARNING] Skipped {key}: {file_path} not found")
        
        return loaded_instructions
    
    def create_runtime_summary(self, instructions: Dict[str, str]) -> str:
        """Create a summary of loaded instructions for the GPT."""
        summary = "# GPT Runtime Instructions Summary\n\n"
        summary += f"Generated: {self._get_timestamp()}\n"
        summary += f"Repository: {self.repo_root.name}\n"
        summary += f"Config: {self.config_path.name}\n\n"
        
        summary += "## Loaded Instructions\n\n"
        for key, content in instructions.items():
            summary += f"### {key.replace('_', ' ').title()}\n"
            summary += f"Length: {len(content)} characters\n"
            summary += f"Lines: {content.count(chr(10)) + 1}\n\n"
        
        summary += "## Configuration\n\n"
        summary += f"- Auto-refresh: {self.check_auto_refresh_enabled()}\n"
        summary += f"- Instruction paths: {', '.join(self.get_instruction_paths())}\n"
        summary += f"- Git integration: {self.config.get('git_integration', {}).get('read_only', True)}\n"
        summary += f"- Write-back: {self.config.get('git_integration', {}).get('write_back', False)}\n"
        
        return summary
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def run_startup(self) -> bool:
        """Run the complete startup process."""
        print("Starting GPT Builder startup process...")
        
        # Load configuration
        self.load_bootstrap_config()
        
        # Check if auto-refresh is enabled
        if not self.check_auto_refresh_enabled():
            print("⚠️ Auto-refresh is disabled in config")
            return True
        
        # Pull latest changes from Git
        if not self.ensure_latest_git():
            print("❌ Failed to update Git repository")
            return False
        
        # Validate instruction files
        if not self.validate_instruction_files():
            print("❌ Instruction file validation failed")
            return False
        
        # Load instructions for runtime
        instructions = self.load_instructions_for_runtime()
        
        # Create runtime summary
        summary = self.create_runtime_summary(instructions)
        
        # Save runtime summary in repo root
        actual_repo_root = self.repo_root.parents[2]
        summary_path = actual_repo_root / "gpt-runtime-summary.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"[OK] Runtime summary saved to {summary_path}")
        print("SUCCESS: GPT Builder startup completed successfully!")
        
        return True

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Update GPT Instructions from Git')
    parser.add_argument('--config', default='bootstrap-config.json',
                       help='Path to bootstrap config file')
    
    args = parser.parse_args()
    
    startup = GPTBuilderStartup(args.config)
    success = startup.run_startup()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
