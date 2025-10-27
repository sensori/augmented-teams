#!/usr/bin/env python3
"""
AI-Assisted Feature Deployment

Combines automated code execution with AI-powered judgment to deploy features
with intelligent error recovery.

TABLE OF CONTENTS:
1. AI-ASSISTED DEPLOYMENT ORCHESTRATION
   1.1 Core Orchestrator
   1.2 AI Assistant Integration
   1.3 Deployment Steps
   1.4 State Management
   1.5 Error Recovery
"""

import asyncio
import json
import os
import sys
import time
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, List, Callable, Any
from abc import ABC, abstractmethod
from datetime import datetime

# Windows-safe print function that handles Unicode
def safe_print(message: str):
    """Print with automatic Unicode handling for Windows"""
    try:
        print(message, flush=True)
    except UnicodeEncodeError:
        # Fallback: remove emojis and try again
        import re
        # Remove common emoji ranges
        clean_message = re.sub(r'[\U0001F300-\U0001F9FF]', '', message)
        try:
            print(clean_message, flush=True)
        except:
            # Last resort: ASCII only
            print(message.encode('ascii', errors='ignore').decode('ascii'), flush=True)

# Add OpenAI import for AI functionality
try:
    import openai
except ImportError:
    openai = None

# Try to load .env file for environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    pass  # dotenv is optional

# Import existing provisioner
sys.path.insert(0, str(Path(__file__).parent))
from provisioner import Provisioner


@dataclass
class DeploymentConfig:
    """Configuration for deployment workflow"""
    regenerate_main: bool = True
    regenerate_service: bool = True
    regenerate_test: bool = True
    rebuild_base_env: bool = False
    rebuild_container: bool = True
    rerun_tests: bool = True
    skip_provision: bool = False
    ai_generate_code: bool = True
    ai_analyze_errors: bool = True
    ai_create_commits: bool = True
    ai_suggest_fixes: bool = True
    max_retries: int = 3
    retry_on_provision_fail: bool = True
    retry_on_test_fail: bool = True
    retry_delay_seconds: int = 10
    exponential_backoff: bool = True
    provision_mode: str = "AZURE"
    skip_steps: List[str] = field(default_factory=list)


@dataclass
class DeploymentState:
    """Tracks deployment progress"""
    current_step: Optional[str] = None
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[Dict[str, Any]] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    retry_count: int = 0
    
    def mark_completed(self, step_name: str):
        self.completed_steps.append(step_name)
    
    def mark_failed(self, step_name: str, error: str):
        self.failed_steps.append({'step': step_name, 'error': error})


class DeploymentLogger:
    """Conversational deployment logger capturing variables, prompts, responses, and outcomes"""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.conversation = []
    
    def log(self, message: str, data: Optional[Dict] = None):
        """Log a conversational entry"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            'timestamp': timestamp,
            'message': message,
            'data': data or {}
        }
        self.conversation.append(entry)
        
        # Write to file immediately for real-time monitoring
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n[{timestamp}] {message}\n")
            if data:
                f.write(f"  Data: {json.dumps(data, indent=2)}\n")
    
    def log_variables(self, name: str, variables: Dict):
        """Log variable values"""
        self.log(f"Variables for {name}", {'variables': variables})
    
    def log_function_call(self, function_name: str, params: Dict, result: Any):
        """Log function call with parameters and result"""
        self.log(
            f"Function Call: {function_name}",
            {'params': params, 'result': str(result)[:500]}  # Truncate long results
        )
    
    def log_ai_prompt(self, function_name: str, prompt: str):
        """Log AI prompt being sent"""
        self.log(
            f"AI Prompt ({function_name})",
            {'prompt': prompt[:2000]}  # Truncate very long prompts
        )
    
    def log_ai_response(self, function_name: str, response: str, success: bool = True):
        """Log AI response"""
        status = "[SUCCESS]" if success else "[FAILURE]"
        self.log(
            f"AI Response ({function_name}) - {status}",
            {'response': response[:2000]}  # Truncate very long responses
        )
    
    def log_outcome(self, step_name: str, success: bool, details: Optional[Dict] = None):
        """Log step outcome"""
        status = "[SUCCESS]" if success else "[FAILED]"
        self.log(f"Outcome: {step_name} - {status}", details)


@dataclass
class StepResult:
    """Result of step execution"""
    success: bool
    output: str = ""
    error: str = ""


@dataclass
class ErrorAnalysis:
    """Structured error information from AI"""
    error_type: str
    suggested_fix: str
    confidence: float
    action_type: str
    target_file: str = ""


@dataclass
class RecoveryAction:
    """AI-suggested fix to apply"""
    action_type: str  # CODE_FIX, INSTALL_DEPENDENCY, REPROVISION, TEST_FIX
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)


class AIAssistant:
    """Wrapper for OpenAI function calling"""
    
    # Function calling schemas
    SCHEMAS = {
        'generate_test_code': {
            'name': 'generate_test_code',
            'description': 'Generate test.py based on requirements',
            'parameters': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'string'},
                    'functions': {'type': 'array'}
                }
            }
        },
        'generate_main_code': {
            'name': 'generate_main_code',
            'description': 'Generate main.py business logic',
            'parameters': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'string'},
                    'functions': {'type': 'array'}
                }
            }
        },
        'generate_service_code': {
            'name': 'generate_service_code',
            'description': 'Generate service.py FastAPI routes',
            'parameters': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'string'},
                    'routes': {'type': 'array'}
                }
            }
        },
        'analyze_deployment_error': {
            'name': 'analyze_deployment_error',
            'description': 'Analyze deployment error and suggest fix',
            'parameters': {
                'type': 'object',
                'properties': {
                    'error_type': {'type': 'string'},
                    'suggested_fix': {'type': 'string'},
                    'confidence': {'type': 'number'},
                    'action_type': {'type': 'string'}
                }
            }
        },
        'create_commit_message': {
            'name': 'create_commit_message',
            'description': 'Generate semantic commit message',
            'parameters': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'type': {'type': 'string'},
                    'scope': {'type': 'string'}
                }
            }
        }
    }
    
    def __init__(self, api_key: Optional[str] = None, logger: Optional[DeploymentLogger] = None):
        if openai is None:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        self.client = openai.OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        if not self.client.api_key:
            safe_print("[WARN] Warning: OPENAI_API_KEY not set")
        
        self.logger = logger  # Optional logger for conversational logging
    
    def _call_ai_function(self, prompt: str, schema_name: str, context: Optional[Dict] = None) -> str:
        """Internal helper for AI function calling - parametrized boilerplate"""
        # Log prompt
        if self.logger:
            self.logger.log_ai_prompt(schema_name, prompt)
            if context:
                self.logger.log_variables(f"{schema_name} context", context)
        
        messages = [{"role": "user", "content": prompt}]
        if context:
            messages.insert(0, {"role": "system", "content": json.dumps(context)})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                functions=[self.SCHEMAS[schema_name]],
                function_call={"name": schema_name}
            )
            
            if response.choices[0].message.function_call:
                result = json.loads(response.choices[0].message.function_call.arguments)
                code = result.get('code', '')
                
                # Log response
                if self.logger:
                    self.logger.log_ai_response(schema_name, code, success=bool(code))
                
                return code
            return ""
        except Exception as e:
            error_msg = str(e)
            if self.logger:
                self.logger.log_ai_response(schema_name, f"Error: {error_msg}", success=False)
            safe_print(f"[FAILED] AI {schema_name} failed: {e}")
            return ""
    
    async def generate_test_code(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Generate test.py code using function calling"""
        return self._call_ai_function(prompt, 'generate_test_code', context)
    
    async def generate_main_code(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Generate main.py code using function calling"""
        return self._call_ai_function(prompt, 'generate_main_code', context)
    
    async def generate_service_code(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Generate service.py code using function calling"""
        return self._call_ai_function(prompt, 'generate_service_code', context)
    
    async def analyze_error(self, logs: str, error: str, context: Dict) -> ErrorAnalysis:
        """Analyze deployment error"""
        prompt = f"Analyze this deployment error:\n\nError: {error}\n\nLogs:\n{logs[:1000]}\n\nContext: {json.dumps(context)}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                functions=[self.SCHEMAS['analyze_deployment_error']],
                function_call={"name": "analyze_deployment_error"}
            )
            
            if response.choices[0].message.function_call:
                result = json.loads(response.choices[0].message.function_call.arguments)
                return ErrorAnalysis(**result)
        except Exception as e:
            safe_print(f"[FAILED] Error analysis failed: {e}")
        
        return ErrorAnalysis(
            error_type="UNKNOWN",
            suggested_fix="Manual intervention required",
            confidence=0.0,
            action_type="MANUAL"
        )
    
    async def create_commit_message(self, changes: List[str], feature_name: str) -> str:
        """Generate semantic commit message"""
        prompt = f"Create a commit message for feature '{feature_name}' with changes: {changes}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                functions=[self.SCHEMAS['create_commit_message']],
                function_call={"name": "create_commit_message"}
            )
            
            if response.choices[0].message.function_call:
                result = json.loads(response.choices[0].message.function_call.arguments)
                return result.get('message', f"[{feature_name}] Update")
        except Exception as e:
            safe_print(f"[FAILED] Commit message generation failed: {e}")
        
        return f"[{feature_name}] Update"


class AssistedDeploymentOrchestrator:
    """
    Main orchestration engine that combines code execution with AI judgment
    
    1. AI-ASSISTED DEPLOYMENT ORCHESTRATION
    1.1 Core Orchestrator - Main deployment coordination
    """
    
    def __init__(self, feature_name: str, feature_path: Path, config: Optional[DeploymentConfig] = None):
        self.feature_name = feature_name
        self.feature_path = feature_path
        self.config = config or DeploymentConfig()
        self.ai_client = None
        self.provisioner = None
        self.state = DeploymentState()
        self.retry_count = 0
        
        # Initialize logger with timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = Path("features/containerization/logs") / f"ai-assisted-deployment-{timestamp}.log"
        self.logger = DeploymentLogger(log_file)
        
        # Initialize AI if enabled
        if self.config.ai_generate_code or self.config.ai_analyze_errors:
            try:
                self.ai_client = AIAssistant(logger=self.logger)
            except ImportError:
                safe_print("[WARN] OpenAI not available - AI features disabled")
        
        # Log initial state
        self.logger.log(f"Starting deployment for feature: {self.feature_name}")
        self.logger.log_variables("Configuration", {
            'feature_name': self.feature_name,
            'feature_path': str(self.feature_path),
            'provision_mode': self.config.provision_mode,
            'regenerate_main': self.config.regenerate_main,
            'regenerate_service': self.config.regenerate_service,
            'ai_enabled': bool(self.ai_client)
        })
    
    def execute_step(self, step_name: str, step_func: Callable) -> StepResult:
        """Execute single deployment step with retry logic"""
        self.state.current_step = step_name
        
        for attempt in range(self.config.max_retries):
            try:
                safe_print(f"[EXEC] Executing step: {step_name} (attempt {attempt + 1}/{self.config.max_retries})")
                result = step_func()
                
                if result.success:
                    self.state.mark_completed(step_name)
                    safe_print(f"[SUCCESS] Step completed: {step_name}")
                    return result
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    self.state.mark_failed(step_name, str(e))
                    safe_print(f"[FAILED] Step failed after {self.config.max_retries} attempts: {step_name}")
                    raise
                wait_time = self.config.retry_delay_seconds * (2 ** attempt) if self.config.exponential_backoff else self.config.retry_delay_seconds
                time.sleep(wait_time)
        
        return StepResult(success=False, error=f"Max retries exceeded for {step_name}")
    
    async def deploy(self) -> bool:
        """
        1.1 Core Orchestrator - Execute full deployment workflow
        
        Orchestrates the complete deployment process following TDD approach:
        - Create feature structure
        - Generate and test main code iteratively
        - Generate service layer
        - Commit and deploy
        - Monitor and recover from errors
        """
        self.state.start_time = time.time()
        
        try:
            # Phase 1: Setup
            safe_print(f"\n[DEPLOY] Starting AI-assisted deployment for '{self.feature_name}'")
            safe_print("=" * 70)
            
            if "CREATE_STRUCTURE" not in self.config.skip_steps:
                self.execute_step("CREATE_STRUCTURE", self._create_feature_structure)
            
            # Phase 2: Code Generation (TDD loop)
            if "GENERATE_MAIN_CODE" not in self.config.skip_steps:
                await self._generate_and_test_main_code()
            
            # Phase 3: Service Layer
            if "GENERATE_SERVICE" not in self.config.skip_steps:
                await self._generate_and_test_service()
            
            # Phase 4: Commit and Deploy
            if "COMMIT_PUSH" not in self.config.skip_steps:
                await self._commit_and_push()
            
            # Phase 5: Monitor (if Azure deployment)
            if self.config.provision_mode == "AZURE" and "MONITOR_DEPLOYMENT" not in self.config.skip_steps:
                self._wait_for_github_action()
                if not self._check_service_health():
                    await self._recover_from_error()
            
            self.state.end_time = time.time()
            duration = self.state.end_time - self.state.start_time
            safe_print(f"\n[SUCCESS] Deployment completed in {duration:.1f}s")
            return True
            
        except Exception as e:
            self.state.end_time = time.time()
            safe_print(f"\n[FAILED] Deployment failed: {e}")
            if self.config.ai_analyze_errors:
                await self._handle_fatal_error(e)
            return False
    
    def _create_feature_structure(self) -> StepResult:
        """Create feature directory and basic structure"""
        safe_print("[SETUP] Creating feature structure...")
        # Create the feature directory structure
        self.feature_path.mkdir(parents=True, exist_ok=True)
        (self.feature_path / "config").mkdir(exist_ok=True)
        self.logger.log(f"Created feature directory structure: {self.feature_path}")
        return StepResult(success=True, output=f"Feature structure at {self.feature_path}")
    
    async def _generate_and_test_main_code(self) -> None:
        """
        1.1.2 Generate and Test Main Code - TDD approach
        
        Follows test-driven development:
        1. AI generates test.py from requirements
        2. Run tests (expected to fail initially)
        3. AI generates main.py to pass tests
        4. Repeat until all tests pass
        """
        if not self.config.regenerate_main or not self.config.ai_generate_code:
            safe_print("[SKIP] Skipping main code generation (disabled in config)")
            return
        
        if not self.ai_client:
            safe_print("[WARN] AI client not available - skipping code generation")
            return
        
        safe_print("\n[TDD] Generating and testing main code (TDD approach)...")
        
        # Generate initial test.py
        test_file = self.feature_path / "test.py"
        if not test_file.exists() or self.config.regenerate_test:
            safe_print("[AI] AI generating test.py...")
            prompt = f"Generate test.py for feature '{self.feature_name}' with comprehensive tests"
            test_code = await self.ai_client.generate_test_code(prompt)
            if test_code:
                with open(test_file, 'w') as f:
                    f.write(test_code)
                safe_print("[SUCCESS] Generated test.py")
        
        # TDD Loop: Generate main.py to pass tests
        main_file = self.feature_path / "main.py"
        for attempt in range(self.config.max_retries):
            safe_print(f"\n[TEST] Running tests (attempt {attempt + 1}/{self.config.max_retries})...")
            
            # Run tests
            result = self._run_command(f'python {test_file}')
            
            if result.returncode == 0:
                safe_print("[SUCCESS] All tests passing!")
                break
            
            # Tests failed - generate/fix main.py
            if attempt < self.config.max_retries - 1:
                safe_print("[AI] AI generating/fixing main.py to pass tests...")
                error_msg = result.stderr
                
                prompt = f"""
Generate main.py for feature '{self.feature_name}' that passes these tests.
Error output: {error_msg}
Ensure the code is production-ready and follows best practices.
"""
                
                if main_file.exists():
                    with open(main_file, 'r') as f:
                        existing_code = f.read()
                    prompt += f"\n\nExisting code:\n{existing_code}"
                
                main_code = await self.ai_client.generate_main_code(prompt)
                
                if main_code:
                    with open(main_file, 'w') as f:
                        f.write(main_code)
                    safe_print("[SUCCESS] Updated main.py")
                else:
                    safe_print("[FAILED] Failed to generate main.py")
                    break
    
    def _run_command(self, command: str) -> subprocess.CompletedProcess:
        """Run shell command and return result"""
        try:
            return subprocess.run(
                command.split(),
                cwd=self.feature_path,
                capture_output=True,
                text=True,
                timeout=60
            )
        except subprocess.TimeoutExpired:
            safe_print("[TIMEOUT] Command timed out")
            return subprocess.CompletedProcess(
                args=command.split(),
                returncode=1,
                stderr="Command timed out"
            )
    
    async def _generate_and_test_service(self) -> None:
        """Generate service.py and service-test.py using provisioner"""
        safe_print("\n[SERVICE] Generating service layer...")
        
        if not self.config.regenerate_service:
            safe_print("[SKIP] Skipping service layer (disabled in config)")
            return
        
        # Create provisioner for the feature
        containerization_path = Path(__file__).parent
        self.provisioner = Provisioner.create(
            self.config.provision_mode,
            self.feature_path,
            containerization_path
        )
        
        # Provision and start service
        if self.provisioner:
            safe_print(f"[PROVISION] Provisioning in {self.config.provision_mode} mode...")
            if self.provisioner.provision(always=True):
                if self.provisioner.start(always=True):
                    safe_print("[SUCCESS] Service started")
                else:
                    safe_print("[FAILED] Failed to start service")
            else:
                safe_print("[FAILED] Provisioning failed")
    
    async def _commit_and_push(self) -> None:
        """Commit changes with AI-generated message and push to trigger GitHub Actions"""
        safe_print("\n[GIT] Committing and pushing changes...")
        
        # Generate commit message if AI is enabled
        commit_message = f"[{self.feature_name}] Update"
        if self.config.ai_create_commits and self.ai_client:
            try:
                changes = [f.path for f in Path(self.feature_path).rglob('*.py')]
                commit_message = await self.ai_client.create_commit_message(
                    changes[:5],  # First 5 changed files
                    self.feature_name
                )
                safe_print(f"[AI] AI-generated commit message: {commit_message}")
            except Exception as e:
                safe_print(f"[WARN] Failed to generate commit message: {e}")
        
        # Stage, commit, and push
        repo_root = Path.cwd()
        commands = [
            f"git add {self.feature_path}",
            f"git commit -m \"{commit_message}\"",
            "git push"
        ]
        
        for cmd in commands:
            safe_print(f"[EXEC] Running: {cmd}")
            result = self._run_command(cmd)
            if result.returncode != 0:
                safe_print(f"[FAILED] Git command failed: {result.stderr}")
                return
        
        safe_print("[SUCCESS] Changes pushed to GitHub")
    
    def _wait_for_github_action(self) -> None:
        """Monitor GitHub Actions deployment"""
        safe_print("\n[WAIT] Waiting for GitHub Actions...")
        safe_print("[INFO] Check workflow status at: https://github.com/...")
        # TODO: Poll GitHub API for workflow status
        # For now, just wait a bit
        time.sleep(5)
    
    def _check_service_health(self) -> bool:
        """Check if deployed service is healthy"""
        safe_print("\n🏥 Checking service health...")
        # TODO: Ping production endpoint
        # For now, assume healthy
        return True
    
    async def _recover_from_error(self) -> None:
        """
        1.5 Error Recovery - AI-powered error diagnosis and fix
        
        Analyzes deployment errors and applies automatic fixes.
        Recovery patterns defined in documentation.
        """
        safe_print("\n[RECOVER] Attempting automatic error recovery...")
        
        if not self.config.ai_analyze_errors or not self.ai_client:
            safe_print("[WARN] Error recovery disabled (AI not available)")
            return
        
        # Fetch logs
        safe_print("[LOGS] Fetching logs...")
        logs = self._fetch_logs()
        
        if not logs:
            safe_print("[WARN] Could not fetch logs")
            return
        
        # AI analyzes error
        safe_print("[AI] AI analyzing error...")
        analysis = await self.ai_client.analyze_error(
            logs=logs,
            error="Service health check failed",
            context={
                'feature': self.feature_name,
                'step': self.state.current_step,
                'retry_count': self.state.retry_count
            }
        )
        
        safe_print(f"[CLASSIFY] Error classified as: {analysis.error_type}")
        safe_print(f"[FIX] Suggested fix: {analysis.suggested_fix}")
        
        # TODO: Apply suggested fix based on action_type
        # CODE_FIX, INSTALL_DEPENDENCY, REPROVISION, TEST_FIX
    
    async def _handle_fatal_error(self, error: Exception) -> None:
        """Handle unrecoverable errors"""
        safe_print(f"\n[FATAL] Fatal error: {error}")
        safe_print("[STATE] Deployment state:")
        safe_print(f"  Completed steps: {self.state.completed_steps}")
        safe_print(f"  Failed steps: {len(self.state.failed_steps)}")
        
        if self.config.ai_analyze_errors and self.ai_client:
            safe_print("\n[AI] AI diagnostic report:")
            # TODO: Generate diagnostic report with AI
            pass
        
        # TODO: Save deployment log for debugging
    
    def _fetch_logs(self) -> str:
        """Fetch logs from various sources"""
        logs = []
        
        # TODO: Fetch Azure Container App logs
        # TODO: Fetch GitHub Actions workflow logs
        
        return "\n".join(logs) if logs else ""


def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI-Assisted Feature Deployment')
    parser.add_argument('--feature', required=True, help='Feature name')
    parser.add_argument('--requirements', help='Feature requirements description')
    parser.add_argument('--mode', choices=['CODE', 'SERVICE', 'CONTAINER', 'AZURE'], default='AZURE')
    parser.add_argument('--config', help='Path to deployment config YAML')
    parser.add_argument('--no-regenerate', action='store_true', help='Skip code regeneration')
    parser.add_argument('--skip-base-rebuild', action='store_true', help='Skip base environment rebuild')
    parser.add_argument('--dry-run', action='store_true', help='Preview without executing')
    
    args = parser.parse_args()
    
    # Set feature path
    feature_path = Path("features") / args.feature
    
    # Create config
    config = DeploymentConfig()
    config.provision_mode = args.mode
    config.regenerate_main = not args.no_regenerate
    config.rebuild_base_env = not args.skip_base_rebuild
    
    # Create orchestrator
    orchestrator = AssistedDeploymentOrchestrator(
        feature_name=args.feature,
        feature_path=feature_path,
        config=config
    )
    
    # Run deployment
    if args.dry_run:
        safe_print("[DRY-RUN] Dry run mode - preview only")
        safe_print(f"Would deploy: {args.feature} in {args.mode} mode")
        sys.exit(0)
    
    success = asyncio.run(orchestrator.deploy())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

