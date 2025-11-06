#!/usr/bin/env python3
"""
Provisioner Classes

Contains all provisioner implementations for CODE, SERVICE, and CONTAINER modes
"""

import sys
import subprocess
import requests
import time
import re
from pathlib import Path
from abc import ABC, abstractmethod

# Windows-safe print function
def safe_print(message: str):
    """Print with automatic Unicode handling for Windows"""
    try:
        print(message, flush=True)
    except UnicodeEncodeError:
        # Remove emojis and try again
        clean_message = re.sub(r'[\U0001F300-\U0001F9FF]', '', message)
        try:
            print(clean_message, flush=True)
        except:
            # ASCII only fallback
            print(message.encode('ascii', errors='ignore').decode('ascii'), flush=True)

class Provisioner(ABC):
    """Abstract base class for provisioners"""
    
    def __init__(self, feature_path, containerization_path):
        self.feature_path = feature_path
        self.containerization_path = containerization_path
    
    @staticmethod
    def create(mode, feature_path, containerization_path):
        """Factory method to create appropriate provisioner"""
        if mode == 'CODE':
            return CodeProvisioner(feature_path, containerization_path)
        elif mode == 'SERVICE':
            return ServiceProvisioner(feature_path, containerization_path)
        elif mode == 'CONTAINER':
            return ContainerProvisioner(feature_path, containerization_path)
        elif mode == 'AZURE':
            return AzureContainerProvisioner(feature_path, containerization_path)
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    def is_provisioning_needed(self):
        """Check if provisioning is needed (check if up to date)"""
        # TODO: Implement checking logic (e.g., compare timestamps, check if deps installed, etc.)
        return True
    
    def is_service_running(self):
        """Check if service is already running"""
        test_url = self.get_test_url()
        if not test_url:
            return False
        try:
            response = requests.get(test_url, timeout=2)
            return response.status_code == 200
        except:
            return False
    
    @abstractmethod
    def provision(self, always=False):
        """Provision the service"""
        pass
    
    @abstractmethod
    def start(self, always=False):
        """Start the service"""
        pass
    
    @abstractmethod
    def get_test_url(self):
        """Get the URL for testing"""
        pass

class CodeProvisioner(Provisioner):
    """Provisioner for code-only tests (no service needed)"""
    
    def provision(self, always=False):
        """No provisioning needed for code tests"""
        return True
    
    def start(self, always=False):
        """No start needed for code tests"""
        return True
    
    def get_test_url(self):
        """No URL for code tests"""
        return None

class ServiceProvisioner(Provisioner):
    """Provisioner for in-memory service tests"""
    
    def _get_config(self):
        """Load config from feature-config.yaml"""
        import yaml
        config_file = self.feature_path / "config" / "feature-config.yaml"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def provision(self, always=False):
        """Provision the service"""
        # Check if provisioning is needed
        if not always and not self.is_provisioning_needed():
            safe_print("[SKIP] Service already provisioned and up to date")
            return True
        
        safe_print(f"[PROVISION] Provisioning {self.feature_path.name}...")
        print("=" * 60)
        
        # Install dependencies from build.requirements in config
        safe_print("[DEPS] Installing dependencies...")
        config = self._get_config()
        requirements = config.get('build', {}).get('requirements', [])
        
        if requirements:
            # Install each requirement
            for req in requirements:
                result = subprocess.run([sys.executable, "-m", "pip", "install", req])
                if result.returncode != 0:
                    safe_print(f"[FAILED] Failed to install {req}")
                    return False
            safe_print("[SUCCESS] Dependencies installed")
        else:
            safe_print("[WARN] No build.requirements in config")
        
        return True
    
    @staticmethod
    def _kill_port(port=8000):
        """Kill any process using the specified port"""
        import os
        import subprocess
        
        if os.name == 'nt':  # Windows
            try:
                # Find process using the port
                result = subprocess.run(
                    ["netstat", "-ano"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            if pid.isdigit():
                                safe_print(f"[WARN]  Killing process {pid} using port {port}")
                                subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
            except Exception as e:
                safe_print(f"[WARN]  Could not kill process on port {port}: {e}")
        else:  # Unix/Linux/Mac
            try:
                subprocess.run(["lsof", "-ti", f":{port}", "-s", "TCP:LISTEN", "|", "xargs", "-r", "kill", "-9"], shell=True)
            except Exception as e:
                safe_print(f"[WARN]  Could not kill process on port {port}: {e}")
    
    def start(self, always=False):
        """Start service in-memory"""
        # Check if already running
        if not always and self.is_service_running():
            print("✅ Service already running")
            return True
        
        # Kill any existing service on the port if forcing
        if always:
            self._kill_port(8000)
            time.sleep(1)  # Give time for port to be released
        
        # Start service by importing and running with uvicorn
        print("🚀 Starting service in-memory...")
        sys.path.insert(0, str(self.feature_path))
        import uvicorn
        import threading
        
        # Run in background thread
        # Try service.py first, fall back to main.py
        try:
            from service import app
            module = "service"
        except ImportError:
            from main import app
            module = "main"
        
        def run_server():
            uvicorn.run(f"{module}:app", host='0.0.0.0', port=8000, log_level='info', reload=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for service to be ready
        time.sleep(2)
        return True
    
    def get_test_url(self):
        """Get service test URL from config (dev)"""
        config = self._get_config()
        return config.get('environment', {}).get('development', {}).get('url', "http://localhost:8000")

class ContainerProvisioner(Provisioner):
    """Provisioner for container tests"""
    
    def _get_config(self):
        """Load config from feature-config.yaml"""
        import yaml
        config_file = self.feature_path / "config" / "feature-config.yaml"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def provision(self, always=False):
        """Provision the container"""
        # Check if provisioning is needed
        if not always and not self.is_provisioning_needed():
            safe_print("[SKIP] Service already provisioned and up to date")
            return True
        
        safe_print(f"[PROVISION] Provisioning {self.feature_path.name}...")
        print("=" * 60)
        
        # Install dependencies from build.requirements in config
        safe_print("[DEPS] Installing dependencies...")
        config = self._get_config()
        requirements = config.get('build', {}).get('requirements', [])
        
        if requirements:
            # Install each requirement
            for req in requirements:
                result = subprocess.run([sys.executable, "-m", "pip", "install", req])
                if result.returncode != 0:
                    safe_print(f"[FAILED] Failed to install {req}")
                    return False
            safe_print("[SUCCESS] Dependencies installed")
        else:
            safe_print("[WARN] No build.requirements in config")
        
        return True
    
    def start(self, always=False):
        """Start container by spawning service.py as background subprocess"""
        # Check if already running
        if not always and self.is_service_running():
            print("✅ Container already running")
            return True
        
        # Kill any existing service on the port if forcing
        if always:
            safe_print("[WARN]  Force mode: killing any existing services on port 8000...")
            ServiceProvisioner._kill_port(8000)
            time.sleep(1)  # Give time for port to be released
        
        # Start service by spawning service.py in background
        print("🚀 Starting container...")
        sys.path.insert(0, str(self.feature_path))
        import uvicorn
        import threading
        
        # Try service.py first, fall back to main.py
        try:
            from service import app
            module = "service"
        except ImportError:
            from main import app
            module = "main"
        
        def run_server():
            uvicorn.run(f"{module}:app", host='0.0.0.0', port=8000, log_level='info', reload=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for service to be ready
        time.sleep(2)
        return True
    
    def get_test_url(self):
        """Get container test URL from config (production)"""
        config = self._get_config()
        return config.get('environment', {}).get('production', {}).get('url', "http://localhost:8000")

def main():
    """
    Main provisioning CLI
    
    Examples:
        # Provision a feature in SERVICE mode
        python provisioner.py SERVICE behaviors/git-integration
        
        # Provision in CONTAINER mode
        python provisioner.py CONTAINER behaviors/git-integration
        
        # Provision with --always flag (skip checks)
        python provisioner.py SERVICE behaviors/git-integration --always
        
        # Code mode (no service needed)
        python provisioner.py CODE behaviors/git-integration
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Provision service')
    parser.add_argument('mode', choices=['CODE', 'SERVICE', 'CONTAINER'], help='Mode: CODE, SERVICE, or CONTAINER')
    parser.add_argument('feature_path', nargs='?', help='Feature path (default: parent)')
    parser.add_argument('--always', action='store_true', help='Always provision/start (skip checks)')
    
    args = parser.parse_args()
    
    # Get feature path
    if args.feature_path:
        feature_path = Path(args.feature_path)
    else:
        # Default to parent of containerization folder
        feature_path = Path(__file__).parent.parent
    
    # Get containerization path
    containerization_path = Path(__file__).parent
    
    # Create provisioner
    provisioner = Provisioner.create(args.mode, feature_path, containerization_path)
    
    # Run provisioning
    if not provisioner.provision(args.always):
        print("❌ Provisioning failed")
        sys.exit(1)
    
    # Start service (if not CODE mode)
    if args.mode != 'CODE':
        if not provisioner.start(args.always):
            print("❌ Failed to start service")
            sys.exit(1)
    
    print(f"✅ {feature_path.name} provisioned and started successfully!")
    sys.exit(0)

class AzureContainerProvisioner(Provisioner):
    """Provisioner for AZURE mode - deploys to Azure Container Apps"""
    
    def _get_config(self):
        """Load config from feature-config.yaml"""
        import yaml
        config_file = self.feature_path / "config" / "feature-config.yaml"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def provision(self, always=False):
        """Build and push Docker image to ACR"""
        print("🚀 Provisioning for AZURE deployment...")
        config = self._get_config()
        
        # Run inject-config to ensure Dockerfile is up to date
        print("📦 Generating Dockerfile...")
        inject_script = self.containerization_path / "inject-config.py"
        result = subprocess.run(
            [sys.executable, str(inject_script), str(self.feature_path)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode != 0:
            print(f"❌ Failed to generate Dockerfile: {result.stderr}")
            return False
        
        print("✅ Dockerfile generated")
        
        # Build and push Docker image
        import os
        acr_server = config.get('azure', {}).get('container_registry', '')
        feature_name = config.get('feature', {}).get('name', self.feature_path.name).lower()
        image_name = f"{acr_server}/{feature_name}:latest"
        
        # Login to ACR if password provided
        registry_password = os.environ.get('ACR_PASSWORD', '')
        if registry_password:
            print(f"🔐 Logging into {acr_server}...")
            registry_username = config.get('azure', {}).get('registry_username', '')
            docker_login = subprocess.run(
                ["docker", "login", acr_server, "--username", registry_username, "--password", registry_password],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            if docker_login.returncode != 0:
                safe_print(f"[WARN] Docker login failed (may already be logged in)")
        
        # Build the image
        # For containerization, build from repo root; for others, build from feature directory
        is_containerization = feature_name == 'containerization'
        if is_containerization:
            build_context = self.feature_path.parent.parent  # Repo root
        else:
            build_context = self.feature_path  # Feature directory
        
        print(f"🔨 Building Docker image {image_name} from {build_context}...")
        build_result = subprocess.run(
            ["docker", "build", "-t", image_name, "-f", str(self.feature_path / "config" / "Dockerfile"), str(build_context)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if build_result.returncode != 0:
            print(f"❌ Failed to build Docker image: {build_result.stderr}")
            return False
        
        print("✅ Docker image built")
        
        # Push the image
        print(f"📤 Pushing Docker image to {acr_server}...")
        push_result = subprocess.run(
            ["docker", "push", image_name],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if push_result.returncode != 0:
            print(f"❌ Failed to push Docker image: {push_result.stderr}")
            return False
        
        print("✅ Docker image pushed to ACR")
        return True
    
    def start(self, always=False):
        """Deploy to Azure Container Apps using Azure CLI"""
        print("🚀 Deploying to Azure Container Apps...")
        config = self._get_config()
        
        # Get Azure CLI path from PATH environment variable
        import os
        az_path = None
        # Try both PATH and Path (Windows)
        path_var = os.environ.get("PATH", "") or os.environ.get("Path", "")
        for path_dir in path_var.split(os.pathsep):
            az_test = os.path.join(path_dir, "az.cmd" if os.name == 'nt' else "az")
            if os.path.isfile(az_test):
                az_path = az_test
                break
        
        if not az_path:
            print("❌ Azure CLI not found in PATH. Install from https://aka.ms/installazurecliwindows")
            return False
        
        # Check if az CLI is working
        result = subprocess.run(
            [az_path, "--version"], 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        if result.returncode != 0:
            print("❌ Azure CLI not working properly")
            return False
        
        # Get Azure config from feature-config.yaml
        import os
        resource_group = config.get('azure', {}).get('resource_group', 'AugmentedTeams')
        acr_server = config.get('azure', {}).get('container_registry', '')
        registry_username = config.get('azure', {}).get('registry_username', '')
        registry_password = os.environ.get('ACR_PASSWORD', '')
        feature_name = config.get('feature', {}).get('name', self.feature_path.name).lower()
        environment = 'managedEnvironment-AugmentedTeams-aa2c'  # TODO: get from config
        
        image_name = f"{acr_server}/{feature_name}:latest"
        
        # Check if container app exists
        check_cmd = [az_path, "containerapp", "show", 
                    "--name", feature_name,
                    "--resource-group", resource_group]
        
        result = subprocess.run(check_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        app_exists = result.returncode == 0
        
        if app_exists:
            print(f"📦 Updating existing Container App '{feature_name}'...")
            # Update existing app with --force to ensure new revision
            update_cmd = [
                az_path, "containerapp", "update",
                "--name", feature_name,
                "--resource-group", resource_group,
                "--image", image_name,
                "--set-env-vars", f"DEPLOYMENT_TIMESTAMP={int(time.time())}"
            ]
            result = subprocess.run(update_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        else:
            print(f"🚀 Creating new Container App '{feature_name}'...")
            # Create new app
            create_cmd = [
                az_path, "containerapp", "create",
                "--name", feature_name,
                "--resource-group", resource_group,
                "--environment", environment,
                "--image", image_name,
                "--registry-server", acr_server,
                "--registry-username", registry_username,
                "--registry-password", registry_password,
                "--target-port", "8000",
                "--ingress", "external",
                "--cpu", "0.25",
                "--memory", "0.5Gi"
            ]
            result = subprocess.run(create_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode != 0:
            print(f"❌ Failed to deploy: {result.stderr}")
            return False
        
        # Set up GitHub token secret if the feature requires it
        github_token = os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN', '')
        if github_token and feature_name == 'mcp-proxy':
            print(f"🔐 Setting up GitHub token secret...")
            secret_cmd = [
                az_path, "containerapp", "secret", "set",
                "--name", feature_name,
                "--resource-group", resource_group,
                "--secrets", f"github-token={github_token}"
            ]
            secret_result = subprocess.run(secret_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if secret_result.returncode == 0:
                print("✅ GitHub token secret configured")
                # Set it as an environment variable in the container app
                set_env_cmd = [
                    az_path, "containerapp", "update",
                    "--name", feature_name,
                    "--resource-group", resource_group,
                    "--set-env-vars", "GITHUB_PERSONAL_ACCESS_TOKEN=secretref:github-token"
                ]
                env_result = subprocess.run(set_env_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                if env_result.returncode == 0:
                    print("✅ GitHub token environment variable configured")
                else:
                    print(f"⚠️ Failed to set environment variable: {env_result.stderr}")
            else:
                print(f"⚠️ Failed to set secret: {secret_result.stderr}")
        
        print(f"✅ Container App deployed successfully!")
        return True
    
    def get_test_url(self):
        """Get Azure Container App URL from config"""
        config = self._get_config()
        return config.get('environment', {}).get('production', {}).get('url', '')

if __name__ == "__main__":
    main()

