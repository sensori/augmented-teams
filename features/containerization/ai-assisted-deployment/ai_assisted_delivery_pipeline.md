# AI-Assisted Feature Development Documentation

## Section 1: Overview

### Vision
Combine automated code execution (fast, deterministic operations) with AI-powered judgment (context-aware, adaptive decision-making) to create an intelligent deployment system that speeds up feature development while automatically recovering from errors.

### Goals
- Faster deployments: Skip unnecessary rebuilds by analyzing what actually changed
- Intelligent error recovery: Automatically diagnose and fix common deployment issues
- Reduced manual intervention: Minimize human involvement in routine deployment tasks
- Transparent AI decisions: Show reasoning behind AI choices

### Scope
This system covers the full feature lifecycle:
- Feature scaffolding and structure creation
- Code generation using AI with test-driven development approach
- Service layer generation and testing
- Git operations with semantic commits
- GitHub Actions deployment monitoring
- Health checking and verification
- Error diagnosis and automatic recovery
- Integration with existing provisioner infrastructure

## Section 2: Architecture

### Core Components

**Orchestration Engine**
- `AssistedDeploymentOrchestrator`: Main class that coordinates all deployment steps
- Manages workflow state and retry logic
- Coordinates between code execution and AI judgment
- Handles error recovery and reattempts

**AI Integration Layer**
- `AIAssistant`: Wrapper for OpenAI API with function calling
- Manages schemas for code generation, error analysis, commit messages
- Provides context-aware responses based on deployment state
- Caches responses where appropriate to reduce latency

**Deployment Steps**
- Each step represents a discrete operation in the deployment pipeline
- Steps can be code-only, AI-only, or hybrid
- Steps support retry logic with exponential backoff
- Steps track their own success/failure state

**State Management**
- `DeploymentState`: Tracks current progress through deployment pipeline
- Records completed steps, failed steps, and retry counts
- Used by AI to make context-aware decisions
- Enables resume from failure points

### Design Principles
- Clear separation: Code for execution, AI for judgment
- Test-driven development: Generate tests first, then code to pass tests
- Progressive enhancement: Start with minimal viable feature, iterate
- Error recovery: Automatic diagnosis and remediation when possible
- Parameterizable: Configuration controls which steps run and how

## Section 3: Static Component List

### Core Classes

**AssistedDeploymentOrchestrator**
- Coordinates full deployment workflow
- Manages step execution and retries
- Integrates with provisioner and AI assistant
- Handles error recovery logic

**AIAssistant**
- Wraps OpenAI API client
- Manages function calling schemas
- Generates code, commits, analyzes errors
- Provides structured responses

**DeploymentStep**
- Represents single deployment operation
- Defines executor function and retry behavior
- Tracks whether AI involvement is required

**DeploymentState**
- Tracks deployment progress
- Records completed and failed steps
- Provides context to AI decisions

**DeploymentConfig**
- YAML-based configuration
- Controls code generation, rebuilds, AI involvement
- Defines retry strategies and GitHub parameters

**ErrorAnalysis**
- Structured error information from AI
- Contains error type, suggested fix, confidence level

**RecoveryAction**
- AI-suggested fix to apply
- Includes action type, target, and parameters

**StepResult**
- Result of step execution
- Contains success status, output, error information

### Existing Components

**Provisioner (provisioner.py)**
- Handles CODE, SERVICE, CONTAINER, AZURE modes
- Manages service provisioning and startup
- To be extended with skip_base parameter

**inject-config.py**
- Generates Dockerfile from feature-config.yaml
- Creates Azure Container App configuration
- Injects dependencies and environment variables

**service_test_base.py**
- Common test infrastructure
- Provides URL resolution by mode
- Handles service starting for SERVICE/CONTAINER modes

**generate-service-test.py**
- Generates service-test.py from test.py
- Parses AST to infer HTTP endpoints
- Creates HTTP integration test stubs

### AI Function Calling Schemas

**generate_test_code**
- Input: Feature requirements, existing main.py code (if any)
- Output: test.py with test functions
- Follows test-driven development approach

**generate_main_code**
- Input: Test code, error messages (if iterating)
- Output: main.py business logic
- Generates code to pass failing tests

**generate_service_code**
- Input: main.py functions
- Output: service.py FastAPI routes
- Follows existing patterns in codebase

**generate_service_test_code**
- Input: test.py functions
- Output: service-test.py HTTP integration tests
- Leverages or extends generate-service-test.py

**analyze_deployment_error**
- Input: Logs, error summary, deployment context
- Output: Error classification and suggested fix
- Provides structured recovery action

**create_commit_message**
- Input: List of changes, feature name, change type
- Output: Semantic commit message with feature tags
- Follows conventional commit format

**determine_retry_strategy**
- Input: Error type, retry count, context
- Output: Retry decision with parameters
- Considers max retries and exponential backoff

## Section 4: Deployment Workflow Steps

The workflow combines user actions, code execution, and AI function calls in a structured sequence:

### Step 1: Create Feature Structure (code)
- **User**: Provides feature name and requirements
- **Code**: Copies template from `features/_template`
- **Code**: Generates config files from feature-config.yaml
- **Code**: Sets up directory structure (main.py, service.py, test.py placeholders)
- **Output**: Feature directory ready for code generation

### Step 2: Generate and Test Main Code (AI + code loop)
- **User**: Provides feature requirements and desired functionality
- **AI Function Call**: `generate_test_code` - Creates test.py following test-driven approach
- **Code**: Runs `python test.py` (CODE mode - plain Python unit tests)
- **If tests fail (expected on first run)**:
  - **AI Function Call**: `generate_main_code` - Creates/edits main.py to pass tests
  - **Code**: Runs `python test.py` again
  - **Repeat loop** until tests pass (max retries enforced)

### Step 3: Generate Service Layer (AI + code)
- **AI Function Call**: `generate_service_code` - Creates service.py with FastAPI routes
- **AI Function Call**: `generate_service_test_code` - Creates service-test.py (or uses existing generate-service-test.py)
- **Code**: Starts service in CONTAINER mode via provisioner
- **Code**: Runs `python service-test.py CONTAINER`
- **If tests fail**:
  - **AI**: Analyzes failure and identifies issue
  - **AI**: Patches service.py or service-test.py
  - **Code**: Reruns tests
  - **Repeat** until passing

### Step 4: Commit & Push (AI + code)
- **AI Function Call**: `create_commit_message` - Generates semantic commit with feature tags
- **Code**: Executes `git add`, `git commit`, `git push`
- **Push triggers**: GitHub Actions workflow (.github/workflows/feature-deploy.yml)

### Step 5: Wait for GitHub Action (code)
- **Code**: Polls GitHub API for workflow status
- **Code**: Streams logs in real-time
- **Code**: Detects completion or failure
- **Timeout**: Max wait time enforced

### Step 6: Check Service Health (code)
- **Code**: Pings production endpoint
- **Code**: Verifies health check passes
- **Code**: Attempts retry with backoff if needed
- **Failure triggers**: Error analysis workflow

### Step 7: Fetch Logs (code)
- **Code**: Fetches Azure Container App logs via `az containerapp logs`
- **Code**: Fetches GitHub Actions workflow logs via API
- **Code**: Parses and structures log data
- **Output**: Structured logs for AI analysis

### Step 8: Error Analysis (AI)
- **AI Function Call**: `analyze_deployment_error` - Analyzes logs and error context
- **AI**: Classifies error type (from error pattern database)
- **AI**: Suggests fix action from recovery patterns
- **Output**: RecoveryAction with specific steps to execute

### Step 9: Apply Fix (code + AI)
- **If CODE_FIX**: AI patches source, code commits changes
- **If INSTALL_DEPENDENCY**: Code installs package via pip
- **If REPROVISION**: Code re-provisions without rebuilding base environment
- **If TEST_FIX**: AI regenerates tests, code reruns
- **If FAIL**: Exceeded retries, return error to user
- **Recovery**: Iterate back to appropriate step

---

## Section 5: Error Recovery Patterns

| Error Type | Detection | AI Action | Code Action | Rebuild Base Env? |
|------------|-----------|-----------|-------------|-------------------|
| Missing Python dependency | Import error in logs | Identify package name and version | Run pip install package | No |
| Azure CLI not installed | "az command not found" in logs | Suggest install command for OS | Run Azure CLI install script | Only if first deployment |
| Provision failed | Deploy step exit code != 0 | Review config/code for issues | Fix config/code, redeploy container | No |
| Test failed | Test assertion error in logs | Debug test logic, identify root cause | Regenerate test.py or fix main.py | No |
| Service timeout | Health check fails after N retries | Analyze startup logs for bottlenecks | Extend timeout, retry health check | No |
| Docker build error | Dockerfile syntax error | Fix Dockerfile syntax/commands | Rebuild Docker image | Yes |
| Code syntax error | Python parsing error in logs | Fix syntax in main.py/service.py | Commit patch, redeploy | No |
| GitHub Action failed | Workflow status = "failed" | Parse workflow logs, classify error | Apply appropriate fix from above | Depends on error |
| Port already in use | "Address already in use" error | Suggest kill process command | Kill process on port, restart | No |
| Azure auth failed | "Authentication failed" in logs | Check credentials, suggest re-auth | Run az login or set credentials | No |

## Section 6: Deployment Configuration

```yaml
deployment:
  # Code Generation Control
  regenerate_main: true
  regenerate_service: true
  regenerate_test: true
  
  # Deployment Control
  rebuild_base_env: false
  rebuild_container: true
  rerun_tests: true
  skip_provision: false
  
  # AI Involvement
  ai_generate_code: true
  ai_analyze_errors: true
  ai_create_commits: true
  ai_suggest_fixes: true
  
  # Retry Strategy
  max_retries: 3
  retry_on_provision_fail: true
  retry_on_test_fail: true
  retry_delay_seconds: 10
  exponential_backoff: true
  
  # Provisioner Integration
  provision_mode: AZURE
  skip_steps: []
  
  # GitHub Action Parameters
  github:
    wait_for_completion: true
    poll_interval_seconds: 30
    max_wait_minutes: 15
    fetch_logs_on_failure: true
```

## Section 7: Implementation Classes

```python
class AssistedDeploymentOrchestrator:
    def __init__(self, feature_name: str, config: DeploymentConfig):
        self.feature_name = feature_name
        self.config = config
        self.ai_client = AIAssistant()
        self.provisioner = None
        self.state = DeploymentState()
        self.retry_count = 0
    
    async def deploy(self) -> DeploymentResult:
        try:
            self.execute_step(DeploymentStep.CREATE_STRUCTURE)
            await self.generate_and_test_main_code()
            await self.generate_and_test_service()
            await self.commit_and_push()
            self.wait_for_github_action()
            if not self.check_service_health():
                await self.recover_from_error()
            return DeploymentResult(success=True, url=self.get_production_url())
        except Exception as e:
            return await self.handle_fatal_error(e)
    
    async def generate_and_test_main_code(self):
        test_code = await self.ai_client.generate_code(
            prompt=f"Generate test.py for {self.feature_name}",
            schema=self.ai_client.schemas['generate_test_code']
        )
        self.write_file('test.py', test_code)
        for attempt in range(self.config.max_retries):
            result = self.run_command('python test.py')
            if result.returncode == 0:
                break
            main_code = await self.ai_client.generate_code(
                prompt=f"Generate main.py to pass tests. Error: {result.stderr}",
                schema=self.ai_client.schemas['generate_main_code'],
                context={'test_code': test_code, 'error': result.stderr}
            )
            self.write_file('main.py', main_code)

class AIAssistant:
    def __init__(self, api_key: str = None):
        import openai
        self.client = openai.OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.schemas = self._load_schemas()
    
    async def generate_code(self, prompt: str, schema: dict, context: dict = None) -> str:
        messages = [{"role": "user", "content": prompt}]
        if context:
            messages.insert(0, {"role": "system", "content": json.dumps(context)})
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            functions=[schema],
            function_call={"name": schema['name']}
        )
        result = json.loads(response.choices[0].message.function_call.arguments)
        return result['code']

class DeploymentStep:
    def __init__(self, name: str, executor: callable, requires_ai: bool = False, 
                 max_retries: int = 1, retry_delay: int = 5):
        self.name = name
        self.executor = executor
        self.requires_ai = requires_ai
        self.max_retries = max_retries
        self.retry_delay = retry_delay

class DeploymentState:
    def __init__(self):
        self.current_step = None
        self.completed_steps = []
        self.failed_steps = []
```

## Section 8: Integration with Existing Provisioner

```python
class AzureContainerProvisioner(Provisioner):
    def provision(self, always=False, skip_base=False):
        if skip_base:
            print("Skipping base environment rebuild - using cached layers")
            build_args = ["--cache-from", f"{image_name}:latest"]
        else:
            build_args = ["--no-cache"]
        # Rest of provisioning logic...

def create_provisioner_with_config(feature_path: Path, config: DeploymentConfig):
    provisioner = Provisioner.create(
        mode=config.provision_mode,
        feature_path=feature_path,
        containerization_path=get_containerization_path()
    )
    if hasattr(provisioner, 'set_skip_base'):
        provisioner.set_skip_base(not config.rebuild_base_env)
    return provisioner
```

## Section 9: Usage Examples

```bash
# Basic usage - full AI-assisted deployment
python features/containerization/ai-assisted-deployment/ai-assisted-deploy.py \
  --feature "payment-api" \
  --requirements "Create REST API for payment processing" \
  --mode AZURE

# Partial deployment - skip code generation
python features/containerization/ai-assisted-deployment/ai-assisted-deploy.py \
  --feature "existing-feature" \
  --no-regenerate \
  --skip-base-rebuild

# Error recovery mode
python features/containerization/ai-assisted-deployment/ai-assisted-deploy.py \
  --feature "failing-feature" \
  --recovery-mode \
  --analyze-logs

# Custom configuration
python features/containerization/ai-assisted-deployment/ai-assisted-deploy.py \
  --feature "ml-service" \
  --config configs/ml-deployment.yaml \
  --max-retries 5

# Dry run
python features/containerization/ai-assisted-deployment/ai-assisted-deploy.py \
  --feature "test-api" \
  --dry-run
```

## Section 10: Benefits & Trade-offs

Benefits: Faster iterations, self-healing, transparent decision-making, flexible workflows, robust error handling, learning system
Trade-offs: Complexity, AI dependency, cost, testing complexity, debugging challenges, latency, non-deterministic behavior, API rate limits

## Section 11: Future Enhancements

1. Memory Integration with In-Memoria MCP
2. Multi-Feature Orchestration
3. Intelligent Rollback
4. Cost Optimization
5. Enhanced Error Patterns
6. Integration with Byterover MCP
7. Preview and Approval Mode
8. Performance Monitoring
9. Multi-Cloud Support
10. Security Scanning

## Section 12: Implementation Phases

Phase 1: Core Orchestrator - Build basic orchestration framework
Phase 2: AI Integration - Connect OpenAI function calling
Phase 3: Error Recovery - Build robust error handling
Phase 4: Testing & Refinement - Validate and polish

