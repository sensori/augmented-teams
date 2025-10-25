# Common Feature Template

This template provides the standard structure and scripts that ALL features should follow, based on the proven git integration pattern.

## 📁 Required File Structure

Every feature MUST contain these 9 core files:

```
src/features/[feature-name]/
├── main.py                      # Main application entry point
├── config/                       # Configuration and deployment files
│   ├── config.yaml               # Centralized configuration (single source of truth)
│   ├── Dockerfile                # Container definition (generated)
│   ├── .azure/containerapp.yaml  # Azure Container App config (generated)
│   ├── deploy-github-action.yml  # Versioned deployment workflow
│   ├── gpt-action.yml            # GPT Action schema (manual upload to ChatGPT)
│   └── env-template.txt          # Environment configuration template (generated)
├── test-service.py               # Comprehensive test suite
├── requirements.txt              # Python dependencies
└── README.md                     # Feature documentation
```

**Shared Scripts (in containerization feature):**
- `inject-config.py` - Located in `src/features/containerization/inject-config.py`
- `provision-service.py` - Located in `src/features/containerization/provision-service.py`

**Usage:**
```bash
# Inject configuration into any feature
python src/features/containerization/inject-config.py src/features/[feature-name]

# Provision any feature using shared script
python src/features/containerization/provision-service.py src/features/[feature-name]
```

## 📊 File Scope Analysis

| File | Scope | Location | Naming Convention | Conflict Risk |
|------|-------|----------|-------------------|---------------|
| `main.py` | **LOCAL** | Feature domain only | `main.py` | ✅ No conflict |
| `config/config.yaml` | **LOCAL** | Feature domain only | `config.yaml` | ✅ No conflict |
| `config/Dockerfile` | **LOCAL** | Feature domain only | `Dockerfile` | ✅ No conflict |
| `config/.azure/containerapp.yaml` | **LOCAL** | Feature domain only | `containerapp.yaml` | ✅ No conflict |
| `config/deploy-github-action.yml` | **GLOBAL** | Deployed to `.github/workflows/` | `[feature-name]-deploy.yml` | ⚠️ **MUST prefix** |
| `config/gpt-action.yml` | **GLOBAL** | Manual upload to ChatGPT | `[feature-name]-gpt-action.yml` | ⚠️ **MUST prefix** |
| `test-service.py` | **LOCAL** | Feature domain only | `test-service.py` | ✅ No conflict |
| `requirements.txt` | **LOCAL** | Feature domain only | `requirements.txt` | ✅ No conflict |
| `config/env-template.txt` | **LOCAL** | Feature domain only | `env-template.txt` | ✅ No conflict |
| `README.md` | **LOCAL** | Feature domain only | `README.md` | ✅ No conflict |

**Shared Scripts (in containerization feature):**
- `inject-config.py` - Configuration injection script
- `provision-service.py` - Complete provisioning script (parameterized)

**Configuration Files (in `config/` subfolder):**
- `config.yaml` - Centralized configuration (single source of truth)
- `Dockerfile` - Container definition (generated from config.yaml)
- `.azure/containerapp.yaml` - Azure Container App config (generated from config.yaml)
- `deploy-github-action.yml` - Versioned deployment workflow
- `gpt-action.yml` - GPT Action schema (manual upload to ChatGPT)
- `env-template.txt` - Environment configuration template (generated from config.yaml)

**Global Deployment Files (Require Feature Prefix):**
- `config/deploy-github-action.yml` → `.github/workflows/[feature-name]-deploy.yml`
- `config/gpt-action.yml` → Manual upload to ChatGPT as `[feature-name]-gpt-action.yml`
- Example: `vector-search-deploy.yml`, `vector-search-gpt-action.yml`

**Local Files (No Prefix Needed):**
- All other files stay within feature domain
- No global deployment conflicts

## ⚙️ Centralized Configuration Strategy

**Problem:** Having the same configuration values in multiple files creates maintenance overhead and inconsistencies.

**Solution:** Centralized configuration with build-time injection.

### Centralized Configuration File
**Location:** `src/features/[feature-name]/config.yaml`
**Purpose:** Single source of truth for all configuration values

```yaml
# [Feature Name] Configuration
# Single source of truth for all configuration values

feature:
  name: "[feature-name]"
  version: "1.0.0"
  description: "[Feature Description]"

service:
  port: 8000
  host: "0.0.0.0"
  url: "http://localhost:8000"
  timeout: 30

environment:
  development:
    log_level: "DEBUG"
    api_endpoint: "http://localhost:3000"
    debug: true
  production:
    log_level: "INFO"
    api_endpoint: "https://api.production.com"
    debug: false

azure:
  resource_group: "augmented-team-rg"
  container_registry: "augmentedteamacr.azurecr.io"
  namespace: "augmented-teams"
  replicas: 1
  memory_request: "256Mi"
  memory_limit: "512Mi"
  cpu_request: "100m"
  cpu_limit: "250m"

secrets:
  api_key: "${API_KEY}"
  github_token: "${GITHUB_TOKEN}"

health_check:
  interval: 30
  timeout: 10
  start_period: 5
  retries: 3
  path: "/health"
```

### Build-Time Configuration Injection

**Script:** `src/features/[feature-name]/inject-config.py`
**Purpose:** Inject configuration values into all files at build time

```python
#!/usr/bin/env python3
"""
Configuration Injection Script
Injects centralized configuration values into all configuration files
"""

import yaml
import os
import re
from pathlib import Path

def load_config():
    """Load centralized configuration"""
    config_file = Path(__file__).parent / "config.yaml"
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def inject_env_template(config):
    """Generate env-template.txt from config"""
    env_content = f"""# {config['feature']['name']} Service Environment Variables
# Copy this file to .env and fill in your values

# Service Configuration
SERVICE_PORT={config['service']['port']}
SERVICE_HOST={config['service']['host']}
SERVICE_URL={config['service']['url']}

# Environment
ENVIRONMENT=development
LOG_LEVEL={config['environment']['development']['log_level']}

# Feature-specific configuration
API_ENDPOINT={config['environment']['development']['api_endpoint']}
API_KEY=your_api_key_here

# Azure Configuration
AZURE_RESOURCE_GROUP={config['azure']['resource_group']}
AZURE_CONTAINER_REGISTRY={config['azure']['container_registry']}
"""
    
    env_file = Path(__file__).parent / "env-template.txt"
    with open(env_file, 'w') as f:
        f.write(env_content)

def inject_dockerfile(config):
    """Generate Dockerfile from config"""
    dockerfile_content = f"""FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set default environment variables
ENV SERVICE_PORT={config['service']['port']}
ENV SERVICE_HOST={config['service']['host']}
ENV ENVIRONMENT=production

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port (configurable via ENV)
EXPOSE ${{SERVICE_PORT}}

# Health check
HEALTHCHECK --interval={config['health_check']['interval']}s --timeout={config['health_check']['timeout']}s --start-period={config['health_check']['start_period']}s --retries={config['health_check']['retries']} \\
  CMD curl -f http://localhost:${{SERVICE_PORT}}{config['health_check']['path']} || exit 1

# Run the application
CMD ["python", "main.py"]
"""
    
    dockerfile = Path(__file__).parent / "Dockerfile"
    with open(dockerfile, 'w') as f:
        f.write(dockerfile_content)

def inject_azure_config(config):
    """Generate Azure Container App config from config.yaml"""
    azure_content = f"""apiVersion: apps/v1
kind: ContainerApp
metadata:
  name: {config['feature']['name']}
  namespace: {config['azure']['namespace']}
spec:
  replicas: {config['azure']['replicas']}
  template:
    metadata:
      labels:
        app: {config['feature']['name']}
        feature: {config['feature']['name']}
    spec:
      containers:
      - name: {config['feature']['name']}
        image: {config['azure']['container_registry']}/{config['feature']['name']}:latest
        ports:
        - containerPort: {config['service']['port']}
        env:
        # Service Configuration
        - name: SERVICE_PORT
          value: "{config['service']['port']}"
        - name: SERVICE_HOST
          value: "{config['service']['host']}"
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "{config['environment']['production']['log_level']}"
        # Feature-specific configuration
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: {config['feature']['name']}-secrets
              key: api-key
        - name: API_ENDPOINT
          value: "{config['environment']['production']['api_endpoint']}"
        resources:
          requests:
            memory: "{config['azure']['memory_request']}"
            cpu: "{config['azure']['cpu_request']}"
          limits:
            memory: "{config['azure']['memory_limit']}"
            cpu: "{config['azure']['cpu_limit']}"
        livenessProbe:
          httpGet:
            path: {config['health_check']['path']}
            port: {config['service']['port']}
          initialDelaySeconds: {config['health_check']['start_period']}
          periodSeconds: {config['health_check']['interval']}
        readinessProbe:
          httpGet:
            path: {config['health_check']['path']}
            port: {config['service']['port']}
          initialDelaySeconds: 5
          periodSeconds: 5
  service:
    type: ClusterIP
    ports:
    - port: 80
      targetPort: {config['service']['port']}
      protocol: TCP
"""
    
    azure_dir = Path(__file__).parent / ".azure"
    azure_dir.mkdir(exist_ok=True)
    azure_file = azure_dir / "containerapp.yaml"
    with open(azure_file, 'w') as f:
        f.write(azure_content)

def inject_provision_script(config):
    """Generate provision-service.py constants from config"""
    provision_file = Path(__file__).parent / "provision-service.py"
    
    # Read existing file
    with open(provision_file, 'r') as f:
        content = f.read()
    
    # Replace configuration constants
    constants = f"""# Configuration constants (injected from config.yaml)
DEFAULT_PORT = {config['service']['port']}
DEFAULT_HOST = "{config['service']['host']}"
DEFAULT_TIMEOUT = {config['service']['timeout']}
REQUIRED_FILES = [
    "requirements.txt",
    "main.py", 
    "test-service.py",
    "env-template.txt",
    "config.yaml"
]
HEALTH_CHECK_TIMEOUT = {config['health_check']['timeout']}
SERVICE_STARTUP_WAIT = 3
HEALTH_CHECK_PATH = "{config['health_check']['path']}"
"""
    
    # Replace the constants section
    content = re.sub(
        r'# Configuration constants.*?(?=\ndef |\nclass |\nif __name__)',
        constants,
        content,
        flags=re.DOTALL
    )
    
    with open(provision_file, 'w') as f:
        f.write(content)

def main():
    """Main injection function"""
    print("🔄 Injecting configuration values...")
    
    config = load_config()
    
    inject_env_template(config)
    print("✅ Generated env-template.txt")
    
    inject_dockerfile(config)
    print("✅ Generated Dockerfile")
    
    inject_azure_config(config)
    print("✅ Generated .azure/containerapp.yaml")
    
    inject_provision_script(config)
    print("✅ Updated provision-service.py constants")
    
    print("🎉 Configuration injection completed!")

if __name__ == "__main__":
    main()
```

### Build Process Integration

**Update provision-service.py to run configuration injection:**

```python
def inject_configuration():
    """Inject configuration values into all files using shared script"""
    print("Injecting configuration values...")
    
    # Use shared inject-config.py from containerization feature
    inject_script = Path(__file__).parent.parent / "containerization" / "inject-config.py"
    feature_path = Path(__file__).parent
    
    result = run_command([sys.executable, str(inject_script), str(feature_path)])
    
    if result.returncode == 0:
        print("Configuration injection completed successfully")
        return True
    else:
        print("Configuration injection failed")
        return False

def main():
    """Complete provisioning function"""
    print("[Feature Name] Service Complete Provisioning")
    print("=" * 60)
    
    # Step 0: Inject configuration
    if not inject_configuration():
        print("Configuration injection failed")
        return 1
    
    # Step 1: Validate environment
    if not validate_environment():
        print("Environment validation failed")
        return 1
    
    # ... rest of provisioning steps
```

## ⚙️ Configuration Hierarchy (Simplified)

### 1. Environment Configuration (env-template.txt)
**Purpose:** Runtime configuration parameters
**Location:** `src/features/[feature-name]/env-template.txt`
**Usage:** Copy to `.env` for local development

```txt
# [Feature Name] Service Environment Variables
# Copy this file to .env and fill in your values

# Service Configuration
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
SERVICE_URL=http://localhost:8000

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# Feature-specific configuration
[FEATURE_NAME]_API_KEY=your_api_key_here
[FEATURE_NAME]_ENDPOINT=https://api.example.com

# Azure Configuration (for production)
AZURE_RESOURCE_GROUP=augmented-team-rg
AZURE_CONTAINER_REGISTRY=augmentedteamacr.azurecr.io
```

### 2. Dockerfile Configuration
**Purpose:** Container-level configuration
**Location:** `src/features/[feature-name]/Dockerfile`

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set default environment variables
ENV SERVICE_PORT=8000
ENV SERVICE_HOST=0.0.0.0
ENV ENVIRONMENT=production

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port (configurable via ENV)
EXPOSE $SERVICE_PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$SERVICE_PORT/health || exit 1

# Run the application
CMD ["python", "main.py"]
```

### 3. Azure Container App Configuration
**Purpose:** Cloud deployment configuration
**Location:** `src/features/[feature-name]/.azure/containerapp.yaml`

```yaml
apiVersion: apps/v1
kind: ContainerApp
metadata:
  name: [feature-name]
  namespace: augmented-teams
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: [feature-name]
        feature: [feature-name]
    spec:
      containers:
      - name: [feature-name]
        image: augmentedteamacr.azurecr.io/[feature-name]:latest
        ports:
        - containerPort: 8000
        env:
        # Service Configuration
        - name: SERVICE_PORT
          value: "8000"
        - name: SERVICE_HOST
          value: "0.0.0.0"
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        # Feature-specific configuration
        - name: [FEATURE_NAME]_API_KEY
          valueFrom:
            secretKeyRef:
              name: [feature-name]-secrets
              key: api-key
        - name: [FEATURE_NAME]_ENDPOINT
          value: "https://api.example.com"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "250m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
  service:
    type: ClusterIP
    ports:
    - port: 80
      targetPort: 8000
      protocol: TCP
```

### 4. Provision Script Configuration
**Purpose:** Build-time and validation configuration
**Location:** `src/features/[feature-name]/provision-service.py`

```python
# Configuration constants
DEFAULT_PORT = 8000
DEFAULT_HOST = "0.0.0.0"
REQUIRED_FILES = [
    "requirements.txt",
    "main.py", 
    "test-service.py",
    "env-template.txt"
]
HEALTH_CHECK_TIMEOUT = 30
SERVICE_STARTUP_WAIT = 3

def validate_environment():
    """Validate system environment and prerequisites"""
    # Check Python version
    # Check required files exist
    # Check .env file exists (warn if not)
    # Validate configuration values
    pass

def check_configuration():
    """Validate configuration parameters"""
    # Check environment variables
    # Validate port availability
    # Check API keys/secrets
    pass
```

### 5. Test Configuration
**Purpose:** Test-specific configuration
**Location:** `src/features/[feature-name]/test-service.py`

```python
# Test Configuration
SERVICE_URL = os.getenv("SERVICE_URL", "http://localhost:8000")
SERVICE_TIMEOUT = 30
TEST_DATA_DIR = "test_data"
MOCK_API_RESPONSES = True

class [FeatureName]Tester:
    def __init__(self):
        self.service_url = SERVICE_URL
        self.timeout = SERVICE_TIMEOUT
        # Load test configuration
        pass
```

## 🔧 Common Scripts

### 1. provision-service.py - Complete Provisioning Script

**Purpose:** Performs full system setup for any feature
**Based on:** `src/integration/git/provision-service.py`

**Required Functions:**
- `validate_environment()` - Check Python version, dependencies, required files
- `install_dependencies()` - Install from requirements.txt
- `setup_service_configuration()` - Validate module imports
- `production_readiness_check()` - Test service startup and endpoints
- `run_tests()` - Execute comprehensive test suite
- `start_service()` - Start service in background for testing
- `cleanup()` - Clean up processes

**Template Structure:**
```python
#!/usr/bin/env python3
"""
[Feature Name] Service Complete Provisioning Script

Performs full system setup:
- Environment validation
- Dependencies installation  
- Service configuration
- Repository setup
- Full testing
- Production readiness validation
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def validate_environment():
    """Validate system environment and prerequisites"""
    # Check Python version (3.8+)
    # Check required files exist
    # Check environment configuration
    pass

def install_dependencies():
    """Install dependencies from requirements.txt"""
    # Check requirements.txt exists
    # Install dependencies with pip
    pass

def setup_service_configuration():
    """Setup service configuration and validate modules"""
    # Test module imports
    # Validate configuration
    pass

def production_readiness_check():
    """Perform production readiness validation"""
    # Start service
    # Test critical endpoints
    # Validate health checks
    pass

def run_tests():
    """Run the comprehensive test suite"""
    # Execute test-service.py
    # Validate all tests pass
    pass

def main():
    """Complete provisioning function"""
    # Execute all steps in order
    # Return 0 for success, 1 for failure
    pass

if __name__ == "__main__":
    sys.exit(main())
```

### 2. test-service.py - Comprehensive Test Suite

**Purpose:** Tests all endpoints and functionality of the feature
**Based on:** `src/integration/git/test-service.py`

**Required Test Categories:**
- Service health check
- Authentication (if applicable)
- Core functionality endpoints
- Error handling
- Integration tests

**Template Structure:**
```python
#!/usr/bin/env python3
"""
[Feature Name] Service Test Suite

Tests all endpoints and functionality of the [Feature Name] Service.
"""

import requests
import json
import time
import subprocess
import sys
from pathlib import Path
import tempfile
import os
from dotenv import load_dotenv

class [FeatureName]Tester:
    def __init__(self):
        self.service_url = os.getenv("SERVICE_URL", "http://localhost:8000")
        self.test_results = []
        self.session = requests.Session()
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        pass
    
    def check_service_running(self) -> bool:
        """Check if the service is running"""
        pass
    
    def test_health_endpoint(self):
        """Test the health/status endpoint"""
        pass
    
    def test_core_functionality(self):
        """Test core feature functionality"""
        pass
    
    def run_all_tests(self):
        """Run all tests"""
        pass

def main():
    tester = [FeatureName]Tester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

### 3. requirements.txt - Dependencies

**Purpose:** Define all Python dependencies
**Based on:** `src/integration/git/build-requirements.txt`

**Required Dependencies:**
```txt
# Core web framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.0

# Environment and configuration
python-dotenv==1.0.0

# HTTP requests
requests==2.31.0

# Add feature-specific dependencies below
# [feature-specific-package]==[version]
```

### 4. deploy-github-action.yml - Versioned Workflow

**Purpose:** Feature-specific deployment workflow (versioned in feature domain)
**Based on:** Standard GitHub Actions pattern
**⚠️ CRITICAL:** This file deploys to GLOBAL `.github/workflows/` and MUST use feature name prefix to prevent conflicts

**Naming Convention:**
- **Feature Domain:** `deploy-github-action.yml` (versioned)
- **Global Deployment:** `[feature-name]-deploy.yml` (prevents conflicts)
- **Examples:** `vector-search-deploy.yml`, `git-integration-deploy.yml`

### 5. gpt-action.yml - GPT Action Schema

**Purpose:** GPT Action schema for ChatGPT integration
**⚠️ CRITICAL:** This file is manually uploaded to ChatGPT and MUST use feature name prefix to prevent conflicts

**Naming Convention:**
- **Feature Domain:** `gpt-action.yml` (versioned)
- **ChatGPT Upload:** `[feature-name]-gpt-action.yml` (prevents conflicts)
- **Examples:** `vector-search-gpt-action.yml`, `git-integration-gpt-action.yml`

**Template Structure:**
```yaml
openapi: 3.0.0
info:
  title: [Feature Name] API
  description: [Feature Description]
  version: 1.0.0
servers:
  - url: https://[feature-name].azurecontainerapps.io
    description: Production server
paths:
  /health:
    get:
      summary: Health check
      operationId: healthCheck
      responses:
        '200':
          description: Service is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: "healthy"
  # Add feature-specific endpoints here
components:
  schemas:
    # Add feature-specific schemas here
```

**Template Structure:**
```yaml
name: Deploy [Feature Name] Feature

on:
  repository_dispatch:
    types: [deploy-[feature-name]]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Build & Deploy to Azure Container App
        uses: azure/container-apps-deploy-action@v2
        with:
          appSourcePath: src/features/[feature-name]
          acrName: ${{ secrets.ACR_NAME }}
          containerAppName: [feature-name]
          resourceGroup: ${{ secrets.AZURE_RESOURCE_GROUP }}

      - name: Deployment Status
        run: |
          echo "✅ [Feature Name] feature deployed successfully!"
          echo "🔗 Container App: [feature-name]"
          echo "📦 Source: src/features/[feature-name]"
```

### 5. Dockerfile - Container Definition

**Purpose:** Define the container for the feature
**Template:**
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "main.py"]
```

### 6. .azure/containerapp.yaml - Azure Configuration

**Purpose:** Define Azure Container App configuration
**Template:**
```yaml
apiVersion: apps/v1
kind: ContainerApp
metadata:
  name: [feature-name]
  namespace: augmented-teams
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: [feature-name]
        feature: [feature-name]
    spec:
      containers:
      - name: [feature-name]
        image: augmentedteamacr.azurecr.io/[feature-name]:latest
        ports:
        - containerPort: 8000
        env:
        - name: PORT
          value: "8000"
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "250m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
  service:
    type: ClusterIP
    ports:
    - port: 80
      targetPort: 8000
      protocol: TCP
```

## 🔧 Configuration Best Practices

### Configuration Priority (Highest to Lowest)
1. **Environment Variables** (`.env` file) - Runtime configuration
2. **Azure Container App** (`.azure/containerapp.yaml`) - Cloud deployment
3. **Dockerfile** (`Dockerfile`) - Container defaults
4. **Provision Script** (`provision-service.py`) - Build-time constants
5. **Test Script** (`test-service.py`) - Test-specific settings

### Configuration Types by File

| Configuration Type | File | Purpose | Example |
|-------------------|------|---------|---------|
| **Runtime Settings** | `env-template.txt` | Service behavior | `SERVICE_PORT=8000` |
| **Secrets/Keys** | `env-template.txt` | API keys, tokens | `API_KEY=your_key_here` |
| **Environment** | `env-template.txt` | Dev/staging/prod | `ENVIRONMENT=production` |
| **Container Defaults** | `Dockerfile` | Container behavior | `ENV SERVICE_PORT=8000` |
| **Cloud Settings** | `.azure/containerapp.yaml` | Azure deployment | `replicas: 2` |
| **Build Constants** | `provision-service.py` | Validation rules | `DEFAULT_PORT = 8000` |
| **Test Settings** | `test-service.py` | Test behavior | `SERVICE_TIMEOUT = 30` |

### Environment-Specific Configuration

**Development:**
```txt
# .env file
SERVICE_PORT=8000
ENVIRONMENT=development
LOG_LEVEL=DEBUG
API_ENDPOINT=http://localhost:3000
```

**Production:**
```yaml
# .azure/containerapp.yaml
env:
- name: ENVIRONMENT
  value: "production"
- name: LOG_LEVEL
  value: "INFO"
- name: API_ENDPOINT
  value: "https://api.production.com"
```

### Configuration Validation

The `provision-service.py` script should validate:
- Required environment variables are set
- Port availability
- API key format
- Endpoint reachability
- Configuration consistency

## 🚀 Usage Instructions

### Creating a New Feature

1. **Copy this template** to `src/features/[your-feature-name]/`
2. **Replace all placeholders** with your feature name
3. **Implement the core functionality** in `src/` directory
4. **Update dependencies** in `requirements.txt`
5. **Customize tests** in `test-service.py`
6. **Configure Azure settings** in `.azure/containerapp.yaml`
7. **Add deployment trigger** to containerization feature

### Running Provisioning

```bash
cd src/features/[feature-name]
python provision-service.py
```

### Running Tests

```bash
cd src/features/[feature-name]
python test-service.py
```

## ✅ Compliance Checklist

- [ ] All 7 required files present
- [ ] `provision-service.py` implements all required functions
- [ ] `test-service.py` covers all functionality
- [ ] `requirements.txt` includes all dependencies
- [ ] `deploy-github-action.yml` follows naming convention
- [ ] `Dockerfile` includes health checks
- [ ] `.azure/containerapp.yaml` configured correctly
- [ ] `README.md` documents the feature
- [ ] No cross-feature dependencies
- [ ] Self-contained configuration

## 🎯 Domain-Oriented Design Compliance

This template ensures compliance with:
- **Feature Localization**: Everything stays within the feature folder
- **Domain Boundaries**: Self-contained feature domain
- **5-7 File Rule**: Standard file structure
- **Clear Interfaces**: Clean APIs for cross-feature communication
- **Self-contained**: Independent configuration and deployment
