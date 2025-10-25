#!/usr/bin/env python3
"""
Shared Configuration Injection Script
Injects centralized configuration values into any feature's configuration files

Usage: python src/features/containerization/inject-config.py src/features/[feature-name]
"""

import yaml
import os
import re
import sys
from pathlib import Path

def load_config(feature_path):
    """Load centralized configuration from feature's config/config.yaml"""
    config_file = feature_path / "config" / "config.yaml"
    if not config_file.exists():
        print(f"❌ Error: config/config.yaml not found in {feature_path}")
        return None
    
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def inject_env_template(config, feature_path):
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
    
    env_file = feature_path / "config" / "env-template.txt"
    with open(env_file, 'w') as f:
        f.write(env_content)

def inject_dockerfile(config, feature_path):
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
    
    dockerfile = feature_path / "config" / "Dockerfile"
    with open(dockerfile, 'w') as f:
        f.write(dockerfile_content)

def inject_azure_config(config, feature_path):
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
    
    azure_dir = feature_path / "config" / ".azure"
    azure_dir.mkdir(parents=True, exist_ok=True)
    azure_file = azure_dir / "containerapp.yaml"
    with open(azure_file, 'w') as f:
        f.write(azure_content)

def inject_provision_script(config, feature_path):
    """Generate provision-service.py constants from config"""
    provision_file = feature_path / "provision-service.py"
    
    if not provision_file.exists():
        print(f"⚠️  Warning: provision-service.py not found in {feature_path}")
        return
    
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
    if len(sys.argv) != 2:
        print("Usage: python inject-config.py <feature-path>")
        print("Example: python inject-config.py src/features/vector-search")
        sys.exit(1)
    
    feature_path = Path(sys.argv[1])
    
    if not feature_path.exists():
        print(f"❌ Error: Feature path {feature_path} does not exist")
        sys.exit(1)
    
    print(f"🔄 Injecting configuration values for {feature_path.name}...")
    
    config = load_config(feature_path)
    if not config:
        sys.exit(1)
    
    inject_env_template(config, feature_path)
    print("✅ Generated env-template.txt")
    
    inject_dockerfile(config, feature_path)
    print("✅ Generated Dockerfile")
    
    inject_azure_config(config, feature_path)
    print("✅ Generated .azure/containerapp.yaml")
    
    inject_provision_script(config, feature_path)
    print("✅ Updated provision-service.py constants")
    
    print(f"🎉 Configuration injection completed for {feature_path.name}!")

if __name__ == "__main__":
    main()
